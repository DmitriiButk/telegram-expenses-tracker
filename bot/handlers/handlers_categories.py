import aiohttp
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.config import FASTAPI_URL
from app.core.utils import get_categories
from bot.states import ExpenseForm


async def show_categories(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    categories = await get_categories(user_id)

    keyboard_buttons = [
        [InlineKeyboardButton(text=categories[i]['name'], callback_data=f'delete_category_{categories[i]["id"]}'),
         InlineKeyboardButton(text=categories[i + 1]['name'],
                              callback_data=f'delete_category_{categories[i + 1]["id"]}')]
        if i + 1 < len(categories) else
        [InlineKeyboardButton(text=categories[i]['name'], callback_data=f'delete_category_{categories[i]["id"]}')]
        for i in range(0, len(categories), 2)
    ]

    keyboard_buttons.append([InlineKeyboardButton(text='🔙 Назад', callback_data='show_category_actions')])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    message_text = 'Список категорий (Нажмите на категорию для удаления):' if categories else 'Категории не найдены'
    await callback_query.message.edit_text(message_text, reply_markup=keyboard)
    await callback_query.answer()


async def start_create_category(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(ExpenseForm.waiting_for_category_name)
    await callback_query.message.edit_text('Введите название новой категории:')
    await callback_query.answer()


async def process_category_name(message: types.Message, state: FSMContext):
    if await state.get_state() != ExpenseForm.waiting_for_category_name.state:
        return

    category_name = message.text.strip()
    if not category_name:
        await message.answer('❌Ошибка: название категории не может быть пустым. Введите заново:')
        return

    user_id = message.from_user.id
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{FASTAPI_URL}/categories/', params={'user_id': user_id},
                                json={"name": category_name}) as response:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text='🔙 Назад', callback_data='show_category_actions')]])
            if response.status == 200:
                await message.answer(f'✅ Категория "{category_name}" успешно создана!', reply_markup=keyboard)
            else:
                await message.answer('❌ Ошибка при создании категории', reply_markup=keyboard)
            await state.clear()


async def start_delete_category(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    categories = await get_categories(user_id)
    keyboard_buttons = [
        [InlineKeyboardButton(text=category['name'], callback_data=f'delete_category_{category['id']}')]
        for category in categories
    ]
    keyboard_buttons.append([InlineKeyboardButton(text='🔙 Назад', callback_data='show_category_actions')])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await state.set_state('delete_category')
    await callback_query.message.edit_text('Выберите категорию для удаления:', reply_markup=keyboard)
    await callback_query.answer()


async def process_delete_category(callback_query: types.CallbackQuery, state: FSMContext):
    category_id = int(callback_query.data.split('_')[2])
    user_id = callback_query.from_user.id
    async with aiohttp.ClientSession() as session:
        async with session.delete(f'{FASTAPI_URL}/categories/{category_id}', params={'user_id': user_id}) as response:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text='🔙 Назад', callback_data='show_category_actions')]])
            if response.status == 200:
                await callback_query.message.edit_text('✅ Категория успешно удалена!', reply_markup=keyboard)
            else:
                await callback_query.message.edit_text('❌ Ошибка при удалении категории', reply_markup=keyboard)
            await state.clear()
    await callback_query.answer()
