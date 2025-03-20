import aiohttp
from aiogram import types
from aiogram.types import InlineKeyboardButton

from app.config import FASTAPI_URL
from app.core.utils import edit_message_with_keyboard, create_keyboard


async def show_main_menu(message: types.Message):
    keyboard = create_keyboard([
        [InlineKeyboardButton(text='💰 Операции с расходами', callback_data='show_expense_actions')],
        [InlineKeyboardButton(text='📁 Операции с категориями', callback_data='show_category_actions')],
        [InlineKeyboardButton(text='ℹ️ Инструкция', callback_data='show_instructions')],
        [InlineKeyboardButton(text='🧹 Очистить чат', callback_data='clear_chat')]
    ])
    await message.answer("Выберите действие:", reply_markup=keyboard)


async def show_instructions(callback_query: types.CallbackQuery):
    instructions = (
        'Привет! Я бот для отслеживания расходов. Вот как вы можете использовать меня:\n'
        '1. Добавить расходы: Нажмите на кнопку "Операции с расходами" и выберите "➕ Добавить расходы".\n'
        '2. Просмотреть расходы: Нажмите на кнопку "Операции с расходами" и выберите "📋 Показать расходы".\n'
        '3. Удалить расход: Нажмите на кнопку "Операции с расходами" и выберите "📋 Показать расходы", '
        'в выбранном меню вы можете удалить какой-либо расход нажав на него.\n'
        '4. Считать расходы за период: Нажмите на кнопку "Операции с расходами" и выберите "📅 Расходы за период".\n'
        '5. Считать расходы по категории за период: Нажмите на кнопку "Операции с расходами" и выберите '
        '"📅 Расходы по категории за период".\n'
        '6. Просмотреть общие расходы: Нажмите на кнопку "Операции с расходами" и выберите "📊 Общие расходы".\n'
        '7. Создать категории: Нажмите на кнопку "Операции с категориями" и выберите "➕ Создать категорию".\n'
        '8. Просмотреть категории: Нажмите на кнопку "Операции с категориями" и выберите "📋 Показать мои категории".\n'
        '9. Удалить категорию: Нажмите на кнопку "Операции с категориями" и выберите "📋 Показать мои категории", '
        'в выбранном меню вы можете удалить категорию нажав на неё. При удалении категории все её расходы удаляются.\n'
        '10. Очистить чат: Нажмите на кнопку "🧹 Очистить чат".\n'
    )
    keyboard = create_keyboard([
        [InlineKeyboardButton(text='🔙 Главное меню', callback_data='main_menu')]
    ])
    await callback_query.message.edit_text(instructions, reply_markup=keyboard)
    await callback_query.answer()


async def show_main_menu_callback(callback_query: types.CallbackQuery):
    keyboard = create_keyboard([
        [InlineKeyboardButton(text='💰 Операции с расходами', callback_data='show_expense_actions')],
        [InlineKeyboardButton(text="📁 Операции с категориями", callback_data='show_category_actions')],
        [InlineKeyboardButton(text='ℹ️ Инструкция', callback_data='show_instructions')],
        [InlineKeyboardButton(text='🧹 Очистить чат', callback_data='clear_chat')]
    ])
    await edit_message_with_keyboard(callback_query.message, 'Выберите действие:', keyboard)
    await callback_query.answer()


async def show_expense_actions(callback_query: types.CallbackQuery):
    keyboard = create_keyboard([
        [InlineKeyboardButton(text='➕ Добавить расходы', callback_data='add_expense')],
        [InlineKeyboardButton(text='📋 Показать расходы', callback_data='show_expenses')],
        [InlineKeyboardButton(text='📅 Расходы по категории за период',
                              callback_data='count_expenses_by_category_and_date')],
        [InlineKeyboardButton(text='📅 Расходы за период', callback_data='count_expenses_in_date_range')],
        [InlineKeyboardButton(text='📊 Общие расходы', callback_data='total_expenses')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data='main_menu')]
    ])
    await edit_message_with_keyboard(callback_query.message, 'Выберите действие с расходами:', keyboard)
    await callback_query.answer()


async def show_category_actions(callback_query: types.CallbackQuery):
    keyboard = create_keyboard([
        [InlineKeyboardButton(text='➕ Создать категорию', callback_data='create_category')],
        [InlineKeyboardButton(text='📋 Показать мои категории', callback_data='show_categories')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data='main_menu')]
    ])
    await edit_message_with_keyboard(callback_query.message, 'Выберите действие с категориями:', keyboard)
    await callback_query.answer()


async def start_command(message: types.Message):
    user = {
        'id': message.from_user.id,
        'name': message.from_user.username or message.from_user.first_name
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{FASTAPI_URL}/users/{user['id']}') as response:
            if response.status == 404:
                async with session.post(f'{FASTAPI_URL}/users/', json=user) as post_response:
                    if post_response.status != 200:
                        await message.answer('❌ Ошибка при создании пользователя')
                        return
    description = (
        '🎉 Добро пожаловать в ExpenseTrackerBot! 🎉\n\n'
        '💰 Я ваш персональный помощник по учёту финансов:\n\n'
        '✨ Что я умею:\n'
        '📝 Записывать ваши расходы\n'
        '📊 Считать траты за любой период\n'
        '📁 Организовывать расходы по категориям\n'
        '🚀 Начните прямо сейчас - выберите действие в меню ниже!'
    )
    await message.answer(description)
    await show_main_menu(message)


async def clear_chat(message: types.Message):
    try:
        current_message_id = message.message_id
        deleted_count = 0
        for message_id in range(current_message_id, 0, -1):
            try:
                await message.bot.delete_message(message.chat.id, message_id)
                deleted_count += 1
                if deleted_count >= 100:
                    break
            except Exception:
                break
        keyboard = create_keyboard([
            [InlineKeyboardButton(text='🔙 Главное меню', callback_data='main_menu')]
        ])
        await message.answer(f'✨ Удалено {deleted_count} сообщений', reply_markup=keyboard)
    except Exception:
        await message.answer('❌ Произошла ошибка при очистке чата')


async def clear_chat_callback(callback_query: types.CallbackQuery):
    await clear_chat(callback_query.message)
    await callback_query.answer()
