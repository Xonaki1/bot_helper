import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot import db
from bot.states import ShoppingStates
from bot.keyboards.main import shopping_list_keyboard, shopping_item_keyboard, cancel_keyboard

router = Router()


def format_shopping_list(shopping_list) -> str:
    items = list(shopping_list.items.all())
    if not items:
        return f'🛒 <b>{shopping_list.name}</b>\n\n📭 Список пуст. Добавь позиции!'

    lines = [f'🛒 <b>{shopping_list.name}</b>', '']
    for item in items:
        check = '✅' if item.is_purchased else '⬜️'
        qty = f' — {item.quantity}' if item.quantity else ''
        lines.append(f'{check} {item.name}{qty}  /item_{item.id}')

    purchased = sum(1 for i in items if i.is_purchased)
    lines.append(f'\n<i>Куплено: {purchased}/{len(items)}</i>')
    return '\n'.join(lines)


@router.message(F.text == '🛒 Список покупок')
@router.message(Command('shopping'))
async def show_shopping(message: Message):
    shopping_list = await asyncio.to_thread(db.get_active_shopping_list, message.from_user.id)

    if not shopping_list:
        await message.answer(
            '🛒 У тебя нет активного списка покупок.\n\nСоздать новый?',
            reply_markup=shopping_list_keyboard(0),
        )
        return

    has_purchased = any(i.is_purchased for i in shopping_list.items.all())
    await message.answer(
        format_shopping_list(shopping_list),
        parse_mode='HTML',
        reply_markup=shopping_list_keyboard(shopping_list.id, show_clear=has_purchased),
    )


@router.callback_query(F.data.startswith('shop:'))
async def cb_shopping(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(':')
    action = parts[1]

    if action == 'new_list':
        await state.set_state(ShoppingStates.new_list_name)
        await callback.message.edit_text(
            '📝 Введи название нового списка покупок:',
            reply_markup=cancel_keyboard(),
        )
        await callback.answer()
        return

    if action == 'add_item':
        list_id = int(parts[2])
        await state.set_state(ShoppingStates.add_item)
        await state.update_data(list_id=list_id)
        await callback.message.edit_text(
            '➕ Введи название позиции (можно с количеством, например: <i>Молоко 2л</i>):',
            parse_mode='HTML',
            reply_markup=cancel_keyboard(),
        )
        await callback.answer()
        return

    if action == 'view':
        list_id = int(parts[2])
        shopping_list = await asyncio.to_thread(db.get_shopping_list, list_id)
        has_purchased = any(i.is_purchased for i in shopping_list.items.all())
        await callback.message.edit_text(
            format_shopping_list(shopping_list),
            parse_mode='HTML',
            reply_markup=shopping_list_keyboard(list_id, show_clear=has_purchased),
        )
        await callback.answer()
        return

    if action == 'clear':
        list_id = int(parts[2])
        deleted = await asyncio.to_thread(db.clear_purchased_items, list_id)
        shopping_list = await asyncio.to_thread(db.get_shopping_list, list_id)
        await callback.message.edit_text(
            format_shopping_list(shopping_list),
            parse_mode='HTML',
            reply_markup=shopping_list_keyboard(list_id),
        )
        await callback.answer(f'🧹 Удалено {deleted} позиций')
        return

    if action in ('check', 'uncheck'):
        list_id, item_id = int(parts[2]), int(parts[3])
        purchased = action == 'check'
        item = await asyncio.to_thread(db.toggle_shopping_item, item_id, purchased)
        shopping_list = await asyncio.to_thread(db.get_shopping_list, list_id)
        has_purchased = any(i.is_purchased for i in shopping_list.items.all())
        await callback.message.edit_text(
            format_shopping_list(shopping_list),
            parse_mode='HTML',
            reply_markup=shopping_list_keyboard(list_id, show_clear=has_purchased),
        )
        await callback.answer('✅ Куплено!' if purchased else '↩️ Отмечено как не купленное')
        return

    if action == 'delete_item':
        list_id, item_id = int(parts[2]), int(parts[3])
        await asyncio.to_thread(db.delete_shopping_item, item_id)
        shopping_list = await asyncio.to_thread(db.get_shopping_list, list_id)
        has_purchased = any(i.is_purchased for i in shopping_list.items.all())
        await callback.message.edit_text(
            format_shopping_list(shopping_list),
            parse_mode='HTML',
            reply_markup=shopping_list_keyboard(list_id, show_clear=has_purchased),
        )
        await callback.answer('🗑 Удалено')
        return

    await callback.answer()


@router.message(F.text.startswith('/item_'))
async def show_item_actions(message: Message):
    try:
        item_id = int(message.text.split('_')[1])
    except (IndexError, ValueError):
        return

    from apps.shopping.models import ShoppingItem
    item = await asyncio.to_thread(
        lambda: ShoppingItem.objects.select_related('shopping_list').get(pk=item_id)
    )
    await message.answer(
        f'<b>{item.name}</b>' + (f' — {item.quantity}' if item.quantity else ''),
        parse_mode='HTML',
        reply_markup=shopping_item_keyboard(item.shopping_list_id, item.id, item.is_purchased),
    )


# ── FSM: Shopping ─────────────────────────────────────────────────────────────

@router.message(ShoppingStates.new_list_name)
async def fsm_new_list_name(message: Message, state: FSMContext):
    shopping_list = await asyncio.to_thread(
        db.create_shopping_list, message.from_user.id, message.text
    )
    await state.clear()
    await message.answer(
        f'✅ Список <b>{shopping_list.name}</b> создан!\n\n'
        'Добавь первые позиции:',
        parse_mode='HTML',
        reply_markup=shopping_list_keyboard(shopping_list.id),
    )


@router.message(ShoppingStates.add_item)
async def fsm_add_item(message: Message, state: FSMContext):
    data = await state.get_data()
    list_id = data['list_id']

    text = message.text.strip()
    parts = text.rsplit(None, 1)
    name = parts[0] if len(parts) > 1 else text
    quantity = parts[1] if len(parts) > 1 else ''

    await asyncio.to_thread(db.add_shopping_item, list_id, name, quantity)
    shopping_list = await asyncio.to_thread(db.get_shopping_list, list_id)
    await state.clear()

    await message.answer(
        format_shopping_list(shopping_list),
        parse_mode='HTML',
        reply_markup=shopping_list_keyboard(list_id),
    )
