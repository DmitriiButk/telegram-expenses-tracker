from typing import Tuple
import aiohttp

from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from app.schemas import DateValidation
from app.config import FASTAPI_URL


async def get_expenses(user_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{FASTAPI_URL}/expenses/', params={'user_id': user_id}) as response:
            if response.status == 200:
                return await response.json()
            else:
                return []


async def get_categories(user_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{FASTAPI_URL}/categories/', params={'user_id': user_id}) as response:
            if response.status == 200:
                return await response.json()
            else:
                return []


async def edit_message_with_keyboard(message: types.Message, text: str, keyboard: InlineKeyboardMarkup):
    if message.photo:
        await message.edit_caption(caption=text, reply_markup=keyboard)
    else:
        await message.edit_text(text, reply_markup=keyboard)


def validate_date_with_pydantic(date_string: str) -> Tuple[bool, str]:
    try:
        DateValidation(date=date_string)
        return True, ''
    except ValueError as e:
        return False, str(e)


def create_keyboard(buttons):
    return InlineKeyboardMarkup(inline_keyboard=buttons)
