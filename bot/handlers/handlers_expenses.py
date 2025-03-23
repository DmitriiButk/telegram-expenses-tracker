from datetime import datetime
import aiohttp
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton

from app.config import FASTAPI_URL
from app.core.utils import get_categories, validate_date_with_pydantic, \
    edit_message_with_keyboard, create_keyboard
from ..states import ExpenseForm


async def add_expense_command(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    categories = await get_categories(user_id)
    keyboard = create_keyboard(
        [[InlineKeyboardButton(text=category['name'], callback_data=f'category_{category['id']}')]
         for category in categories] +
        [[InlineKeyboardButton(text='🔙 Назад', callback_data='show_expense_actions')]]
    )
    await state.set_state(ExpenseForm.category)
    await edit_message_with_keyboard(callback_query.message, 'Выберите категорию:', keyboard)
    await callback_query.answer()


async def process_category(callback_query: types.CallbackQuery, state: FSMContext):
    category_id = int(callback_query.data.split('_')[1])
    await state.update_data(category_id=category_id)
    await state.set_state(ExpenseForm.description)
    await callback_query.message.edit_text('Введите название расходов:')
    await callback_query.answer()


async def process_description(message: types.Message, state: FSMContext):
    menu_message = await message.answer('Введите стоимость расходов:')
    await state.update_data(description=message.text, menu_message_id=menu_message.message_id)
    await state.set_state(ExpenseForm.amount)


async def process_amount(message: types.Message, state: FSMContext):
    keyboard = create_keyboard([[InlineKeyboardButton(text='🔙 Назад', callback_data='show_expense_actions')]])
    try:
        amount = float(message.text.strip())
        if amount <= 0:
            await message.answer('Сумма расхода должна быть больше нуля', reply_markup=keyboard)
            return
        user_data = await state.get_data()
        description = user_data.get('description')
        category_id = user_data.get('category_id')
        user_id = message.from_user.id
        date = user_data.get('date', datetime.now().strftime('%Y-%m-%d'))

        async with aiohttp.ClientSession() as session:
            expense_data = {
                'amount': amount,
                'description': description,
                'date': date,
                'category_id': category_id,
                'user_id': user_id
            }
            async with session.post(f'{FASTAPI_URL}/expenses/{user_id}', json=expense_data) as response:
                if response.status == 200:
                    await message.answer('✅ Расход успешно добавлен!', reply_markup=keyboard)
                else:
                    await message.answer('❌ Ошибка при добавлении расхода', reply_markup=keyboard)
    except ValueError:
        await message.answer('Введите корректное числовое значение для суммы расхода', reply_markup=keyboard)
        return

    await state.clear()


async def count_user_expenses(callback_query: types.CallbackQuery):
    user_id = int(callback_query.from_user.id)
    keyboard = create_keyboard([[InlineKeyboardButton(text='🔙 Назад', callback_data='show_expense_actions')]])
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{FASTAPI_URL}/expenses/user/{user_id}/count') as response:
            if response.status == 200:
                response_data = await response.json()
                total_expenses = response_data.get('total_expenses', 0)
                await callback_query.message.edit_text(f'Ваши общие расходы: {total_expenses}', reply_markup=keyboard)
            else:
                await callback_query.message.edit_text('Ошибка в запросе общих расходов', reply_markup=keyboard)
        await callback_query.answer()


async def start_date_input(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(ExpenseForm.start_date)
    await callback_query.message.edit_text('Введите начальную дату в формате ГГГГ-ММ-ДД:')
    await callback_query.answer()


async def process_start_date(message: types.Message, state: FSMContext):
    date_text = message.text.strip()
    await state.update_data(start_date=date_text)
    await state.set_state(ExpenseForm.end_date)
    await message.answer('Введите конечную дату в формате ГГГГ-ММ-ДД:')


async def process_end_date(message: types.Message, state: FSMContext):
    date_text = message.text.strip()
    valid, error_msg = validate_date_with_pydantic(date_text)
    keyboard = create_keyboard([[InlineKeyboardButton(text='🔙 Назад', callback_data='show_expense_actions')]])

    if not valid:
        await message.answer('Неверный формат даты. Используйте формат ГГГГ-ММ-ДД', reply_markup=keyboard)
        return

    user_data = await state.get_data()
    start_date = user_data.get('start_date')
    end_date = message.text.strip()
    user_id = message.from_user.id

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{FASTAPI_URL}/expenses/user/{user_id}/count_in_date_range',
                               params={'start_date': start_date, 'end_date': end_date}) as response:
            if response.status == 200:
                response_data = await response.json()
                total_expenses = response_data.get('total_expenses', 0)
                await message.answer(f'Ваши расходы с {start_date} по {end_date}: {total_expenses}',
                                     reply_markup=keyboard)
            else:
                await message.answer('Ошибка при подсчёте расходов, введите корректные даты', reply_markup=keyboard)

    await state.clear()


async def start_count_expenses_by_category_and_date(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    categories = await get_categories(user_id)
    keyboard = create_keyboard(
        [[InlineKeyboardButton(text=category['name'], callback_data=f'select_category_{category['id']}')]
         for category in categories] +
        [[InlineKeyboardButton(text='🔙 Назад', callback_data='show_expense_actions')]]
    )
    await state.set_state(ExpenseForm.category)
    await edit_message_with_keyboard(callback_query.message, 'Выберите категорию:', keyboard)
    await callback_query.answer()


async def process_selected_category(callback_query: types.CallbackQuery, state: FSMContext):
    category_id = int(callback_query.data.split('_')[2])
    await state.update_data(category_id=category_id)
    await state.set_state(ExpenseForm.start_category_date)
    await callback_query.message.edit_text('Введите начальную дату в формате ГГГГ-ММ-ДД:')
    await callback_query.answer()


async def process_start_date_for_category(message: types.Message, state: FSMContext):
    keyboard = create_keyboard([[InlineKeyboardButton(text='🔙 Назад', callback_data='show_expense_actions')]])
    start_date = message.text.strip()
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        await message.answer('Ошибка: неверный формат даты. Введите в формате ГГГГ-ММ-ДД', reply_markup=keyboard)
        return

    await state.update_data(start_date=start_date, previous_message_id=message.message_id)
    await state.set_state(ExpenseForm.end_category_date)
    await message.answer('Введите конечную дату в формате ГГГГ-ММ-ДД:')


async def process_end_date_for_category(message: types.Message, state: FSMContext):
    end_date = message.text.strip()
    keyboard = create_keyboard([[InlineKeyboardButton(text='🔙 Назад', callback_data='show_expense_actions')]])
    try:
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        await message.answer('Ошибка: неверный формат даты. Введите в формате ГГГГ-ММ-ДД', reply_markup=keyboard)
        return

    data = await state.get_data()
    start_date = data.get('start_date')
    category_id = data.get('category_id')

    if not start_date or not category_id:
        await message.answer('Ошибка: не найдены начальная дата или категория. Начните заново', reply_markup=keyboard)
        await state.clear()
        return

    user_id = message.from_user.id

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{FASTAPI_URL}/expenses/user/{user_id}/count_in_date_range_by_category',
                               params={'start_date': start_date, 'end_date': end_date,
                                       'category_id': category_id}) as response:
            if response.status == 200:
                response_data = await response.json()
                total_expenses = response_data.get('total_expenses', 0)
                await message.answer(f'Ваши расходы по категории с {start_date} по {end_date}: {total_expenses}',
                                     reply_markup=keyboard)
            else:
                await message.answer('Ошибка при подсчёте расходов, введите корректные даты', reply_markup=keyboard)

    await state.clear()


async def show_expenses(callback_query: types.CallbackQuery):
    data_parts = callback_query.data.split('_')
    page = 1
    if len(data_parts) >= 3:
        try:
            page = int(data_parts[-1])
        except ValueError:
            await callback_query.answer("Ошибка: неверный номер страницы.")
            return

    user_id = callback_query.from_user.id
    expenses_per_page = 10
    offset = (page - 1) * expenses_per_page

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{FASTAPI_URL}/expenses/user/{user_id}/expenses',
                               params={'skip': offset, 'limit': expenses_per_page, 'order_by': 'desc'}) as response:
            if response.status == 200:
                expenses = await response.json()
                if expenses:
                    keyboard_buttons = [
                        [InlineKeyboardButton(
                            text=f'{expense["description"][:20]} - {expense["amount"]}',
                            callback_data=f'delete_expense_{expense["id"]}'
                        ) for expense in expenses[i:i + 2]]
                        for i in range(0, len(expenses), 2)
                    ]

                    if len(expenses) == expenses_per_page:
                        keyboard_buttons.append([InlineKeyboardButton(text='➡️ Следующая страница',
                                                                      callback_data=f'show_expenses_{page + 1}')])
                    if page > 1:
                        keyboard_buttons.append([InlineKeyboardButton(text='⬅️ Предыдущая страница',
                                                                      callback_data=f'show_expenses_{page - 1}')])
                    keyboard_buttons.append(
                        [InlineKeyboardButton(text='🔙 Назад к меню', callback_data='show_expense_actions')])
                    keyboard = create_keyboard(keyboard_buttons)
                    await callback_query.message.edit_text('Ваши расходы (Нажмите на расход для удаления):',
                                                           reply_markup=keyboard)
                else:
                    await callback_query.message.edit_text('У вас пока нет расходов', reply_markup=create_keyboard(
                        [[InlineKeyboardButton(text='🔙 Назад', callback_data='show_expense_actions')]]))
            else:
                await callback_query.message.edit_text('Ошибка при получении расходов', reply_markup=create_keyboard(
                    [[InlineKeyboardButton(text='🔙 Назад', callback_data='show_expense_actions')]]))

    await callback_query.answer()


async def process_delete_expense(callback_query: types.CallbackQuery):
    expense_id = int(callback_query.data.split('_')[2])
    user_id = callback_query.from_user.id
    keyboard = create_keyboard([[InlineKeyboardButton(text='🔙 Назад', callback_data='show_expense_actions')]])
    async with aiohttp.ClientSession() as session:
        async with session.delete(f'{FASTAPI_URL}/expenses/{expense_id}', params={'user_id': user_id}) as response:
            if response.status == 200:
                await callback_query.message.edit_text('✅ Расход успешно удален!', reply_markup=keyboard)
            else:
                await callback_query.message.edit_text('❌ Ошибка при удалении расхода',
                                                       reply_markup=keyboard)

    await callback_query.answer()
