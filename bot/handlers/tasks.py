import asyncio
from datetime import date
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot import db
from bot.states import TaskCreation
from bot.keyboards.main import tasks_menu, task_actions, priority_keyboard, cancel_keyboard

router = Router()

STATUS_LABELS = {'all': None, 'todo': 'todo', 'in_progress': 'in_progress', 'done': 'done'}


def format_task(task) -> str:
    lines = [f'{task.status_emoji} {task.priority_emoji} <b>{task.title}</b>']
    if task.description:
        lines.append(f'<i>{task.description}</i>')
    if task.due_date:
        lines.append(f'📅 До: {task.due_date.strftime("%d.%m.%Y")}')
    if task.category:
        lines.append(f'🏷 {task.category.name}')
    return '\n'.join(lines)


def format_tasks_list(tasks: list) -> str:
    if not tasks:
        return '📭 Задач нет.'
    return '\n\n'.join(
        f'{i}. {task.status_emoji} {task.priority_emoji} <b>{task.title}</b>'
        + (f'\n   📅 {task.due_date.strftime("%d.%m.%Y")}' if task.due_date else '')
        for i, task in enumerate(tasks, 1)
    )


@router.message(F.text == '📋 Мои задачи')
@router.message(Command('tasks'))
async def show_tasks(message: Message):
    await message.answer('📋 <b>Мои задачи</b>', parse_mode='HTML', reply_markup=tasks_menu())


@router.callback_query(F.data.startswith('tasks:'))
async def cb_tasks(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split(':')[1]

    if action == 'add':
        await state.set_state(TaskCreation.title)
        await callback.message.edit_text(
            '✏️ Введи название задачи:', reply_markup=cancel_keyboard()
        )
        await callback.answer()
        return

    status = STATUS_LABELS.get(action)
    tasks = await asyncio.to_thread(db.get_tasks, callback.from_user.id, status)
    text = format_tasks_list(tasks)

    labels = {'all': 'Все задачи', 'todo': 'К выполнению', 'in_progress': 'В процессе', 'done': 'Выполнено'}
    header = f'📋 <b>{labels.get(action, "Задачи")}</b>\n\n'

    await callback.message.edit_text(header + text, parse_mode='HTML', reply_markup=tasks_menu())
    await callback.answer()


@router.callback_query(F.data.startswith('task:'))
async def cb_task_action(callback: CallbackQuery):
    parts = callback.data.split(':')
    action, task_id = parts[1], int(parts[2])

    if action == 'start':
        task = await asyncio.to_thread(db.update_task_status, task_id, 'in_progress')
        await callback.answer('▶️ Задача начата!')
    elif action == 'done':
        task = await asyncio.to_thread(db.update_task_status, task_id, 'done')
        await callback.answer('✅ Задача выполнена!')
    elif action == 'delete':
        await asyncio.to_thread(db.delete_task, task_id)
        await callback.message.edit_text('🗑 Задача удалена.', reply_markup=tasks_menu())
        await callback.answer()
        return
    else:
        task = await asyncio.to_thread(db.get_task, task_id)

    await callback.message.edit_text(
        format_task(task),
        parse_mode='HTML',
        reply_markup=task_actions(task.id, task.status),
    )
    await callback.answer()


# ── FSM: Создание задачи ──────────────────────────────────────────────────────

@router.message(TaskCreation.title)
async def fsm_task_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(TaskCreation.description)
    await message.answer(
        '📝 Описание задачи (или /skip чтобы пропустить):',
        reply_markup=cancel_keyboard(),
    )


@router.message(TaskCreation.description)
async def fsm_task_description(message: Message, state: FSMContext):
    desc = '' if message.text == '/skip' else message.text
    await state.update_data(description=desc)
    await state.set_state(TaskCreation.priority)
    await message.answer('🎯 Выбери приоритет:', reply_markup=priority_keyboard())


@router.callback_query(TaskCreation.priority, F.data.startswith('priority:'))
async def fsm_task_priority(callback: CallbackQuery, state: FSMContext):
    priority = callback.data.split(':')[1]
    await state.update_data(priority=priority)
    await state.set_state(TaskCreation.due_date)
    await callback.message.edit_text(
        '📅 Укажи дедлайн в формате ДД.ММ.ГГГГ (или /skip):',
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(TaskCreation.due_date)
async def fsm_task_due_date(message: Message, state: FSMContext):
    due_date = None
    if message.text != '/skip':
        try:
            due_date = date(*reversed([int(x) for x in message.text.split('.')]))
        except (ValueError, TypeError):
            await message.answer('❌ Неверный формат. Попробуй ДД.ММ.ГГГГ или /skip:')
            return

    data = await state.get_data()
    await state.clear()

    task = await asyncio.to_thread(
        db.create_task,
        message.from_user.id,
        data['title'],
        data.get('description', ''),
        data.get('priority', 'medium'),
        due_date,
    )
    await message.answer(
        f'✅ Задача создана!\n\n{format_task(task)}',
        parse_mode='HTML',
        reply_markup=task_actions(task.id, task.status),
    )


@router.message(F.text == '➕ Новая задача')
async def quick_add_task(message: Message, state: FSMContext):
    await state.set_state(TaskCreation.title)
    await message.answer('✏️ Введи название задачи:', reply_markup=cancel_keyboard())


@router.message(F.text == '📊 Статистика')
@router.message(Command('stats'))
async def show_stats(message: Message):
    stats = await asyncio.to_thread(db.get_task_stats, message.from_user.id)
    await message.answer(
        '<b>📊 Статистика задач</b>\n\n'
        f'📋 Всего: {stats["total"]}\n'
        f'🟡 К выполнению: {stats["todo"]}\n'
        f'⚙️ В процессе: {stats["in_progress"]}\n'
        f'✅ Выполнено: {stats["done"]}',
        parse_mode='HTML',
    )
