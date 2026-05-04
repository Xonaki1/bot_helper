from aiogram.fsm.state import State, StatesGroup


class TaskCreation(StatesGroup):
    title = State()
    description = State()
    priority = State()
    due_date = State()


class ShoppingStates(StatesGroup):
    new_list_name = State()
    add_item = State()
