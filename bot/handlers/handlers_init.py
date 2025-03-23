from aiogram import Dispatcher
from aiogram.filters import Command

from .handlers_categories import *
from .handlers_common import *
from .handlers_expenses import *


def register_handlers(dp: Dispatcher):
    dp.message.register(start_command, Command(commands=["start"]))
    dp.callback_query.register(show_expense_actions, lambda c: c.data == "show_expense_actions")
    dp.callback_query.register(show_category_actions, lambda c: c.data == "show_category_actions")
    dp.callback_query.register(show_main_menu_callback, lambda c: c.data == "main_menu")
    dp.callback_query.register(add_expense_command, lambda c: c.data == "add_expense")
    dp.callback_query.register(process_category, lambda c: c.data.startswith("category_"))
    dp.callback_query.register(count_user_expenses, lambda c: c.data == "total_expenses")
    dp.callback_query.register(start_date_input, lambda c: c.data == "count_expenses_in_date_range")
    dp.message.register(process_start_date, ExpenseForm.start_date)
    dp.message.register(process_end_date, ExpenseForm.end_date)
    dp.callback_query.register(start_count_expenses_by_category_and_date,
                               lambda c: c.data == "count_expenses_by_category_and_date")
    dp.callback_query.register(process_selected_category, lambda c: c.data.startswith("select_category_"))
    dp.message.register(process_start_date_for_category, ExpenseForm.start_category_date)
    dp.message.register(process_end_date_for_category, ExpenseForm.end_category_date)
    dp.message.register(process_description, ExpenseForm.description)
    dp.message.register(process_amount, ExpenseForm.amount)
    dp.callback_query.register(start_create_category, lambda c: c.data == "create_category")
    dp.message.register(process_category_name, ExpenseForm.waiting_for_category_name)
    dp.callback_query.register(start_delete_category, lambda c: c.data == "delete_category")
    dp.callback_query.register(process_delete_category, lambda c: c.data.startswith("delete_category_"))
    dp.callback_query.register(show_categories, lambda c: c.data == "show_categories")
    dp.callback_query.register(show_expenses, lambda c: c.data == "show_expenses")
    dp.callback_query.register(show_expenses, lambda c: c.data and c.data.startswith('show_expenses_'))
    dp.callback_query.register(process_delete_expense, lambda c: c.data.startswith("delete_expense_"))
    dp.callback_query.register(show_main_menu, lambda c: c.data == "main_menu")
    dp.callback_query.register(show_instructions, lambda c: c.data == "show_instructions")
    dp.message.register(clear_chat, Command(commands=["clear"]))
    dp.callback_query.register(clear_chat_callback, lambda c: c.data == "clear_chat")
