import asyncio
from fastapi import FastAPI
from app.routers import expenses, users, categories
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from bot.handlers.handlers_init import register_handlers


load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

register_handlers(dp)

app = FastAPI()

app.include_router(expenses.router)
app.include_router(users.router)
app.include_router(categories.router)


@app.get('/')
def check_api_work():
    return {'message': 'API for telegram bot is working'}


async def start_fastapi():
    import uvicorn
    config = uvicorn.Config("main:app", host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(
        start_fastapi(),
        dp.start_polling(bot, skip_updates=True)
    )


if __name__ == "__main__":
    asyncio.run(main())
