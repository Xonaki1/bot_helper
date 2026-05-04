import asyncio
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot import db
from bot.keyboards.main import main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await asyncio.to_thread(
        db.get_or_create_user,
        message.from_user.id,
        message.from_user.username or '',
        message.from_user.first_name or '',
        message.from_user.last_name or '',
    )
    await message.answer(
        f'Привет, {message.from_user.first_name}! 👋\n\n'
        'Я твой персональный ассистент.\n\n'
        '📋 <b>Задачи</b> — планируй и отслеживай дела\n'
        '🛒 <b>Список покупок</b> — не забудь ничего в магазине\n\n'
        'Выбери раздел в меню:',
        parse_mode='HTML',
        reply_markup=main_menu(),
    )


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(
        '<b>Доступные команды:</b>\n\n'
        '/start — главное меню\n'
        '/tasks — мои задачи\n'
        '/shopping — список покупок\n'
        '/stats — статистика\n'
        '/help — справка',
        parse_mode='HTML',
    )


@router.callback_query(F.data == 'cancel')
async def cb_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('❌ Действие отменено.')
    await callback.answer()
