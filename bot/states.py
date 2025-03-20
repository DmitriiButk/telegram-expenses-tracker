from aiogram.fsm.state import State, StatesGroup


class ExpenseForm(StatesGroup):
    waiting_for_category_name = State()
    category = State()
    description = State()
    amount = State()
    start_date = State()
    end_date = State()
    start_category_date = State()
    end_category_date = State()
