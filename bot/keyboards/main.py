from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text='📋 Мои задачи'),
        KeyboardButton(text='🛒 Список покупок'),
    )
    builder.row(
        KeyboardButton(text='➕ Новая задача'),
        KeyboardButton(text='📊 Статистика'),
    )
    return builder.as_markup(resize_keyboard=True)


def tasks_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='📋 Все', callback_data='tasks:all'),
        InlineKeyboardButton(text='⚙️ В процессе', callback_data='tasks:in_progress'),
        InlineKeyboardButton(text='✅ Готово', callback_data='tasks:done'),
    )
    builder.row(
        InlineKeyboardButton(text='➕ Добавить задачу', callback_data='tasks:add'),
    )
    return builder.as_markup()


def task_actions(task_id: int, status: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if status == 'todo':
        builder.row(InlineKeyboardButton(text='▶️ Начать', callback_data=f'task:start:{task_id}'))
    if status == 'in_progress':
        builder.row(InlineKeyboardButton(text='✅ Завершить', callback_data=f'task:done:{task_id}'))
    if status != 'done':
        builder.row(InlineKeyboardButton(text='🗑 Удалить', callback_data=f'task:delete:{task_id}'))
    builder.row(InlineKeyboardButton(text='◀️ Назад', callback_data='tasks:all'))
    return builder.as_markup()


def priority_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='🟢 Низкий', callback_data='priority:low'),
        InlineKeyboardButton(text='🟡 Средний', callback_data='priority:medium'),
        InlineKeyboardButton(text='🔴 Высокий', callback_data='priority:high'),
    )
    builder.row(InlineKeyboardButton(text='❌ Отмена', callback_data='cancel'))
    return builder.as_markup()


def shopping_list_keyboard(list_id: int, show_clear: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='➕ Добавить позицию', callback_data=f'shop:add_item:{list_id}'))
    builder.row(InlineKeyboardButton(text='🔄 Обновить', callback_data=f'shop:view:{list_id}'))
    if show_clear:
        builder.row(InlineKeyboardButton(text='🧹 Очистить купленные', callback_data=f'shop:clear:{list_id}'))
    builder.row(InlineKeyboardButton(text='📋 Новый список', callback_data='shop:new_list'))
    return builder.as_markup()


def shopping_item_keyboard(list_id: int, item_id: int, is_purchased: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_purchased:
        builder.row(InlineKeyboardButton(text='↩️ Не куплено', callback_data=f'shop:uncheck:{list_id}:{item_id}'))
    else:
        builder.row(InlineKeyboardButton(text='✅ Куплено', callback_data=f'shop:check:{list_id}:{item_id}'))
    builder.row(InlineKeyboardButton(text='🗑 Удалить', callback_data=f'shop:delete_item:{list_id}:{item_id}'))
    builder.row(InlineKeyboardButton(text='◀️ Назад к списку', callback_data=f'shop:view:{list_id}'))
    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='❌ Отмена', callback_data='cancel'))
    return builder.as_markup()
