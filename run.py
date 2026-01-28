import asyncio
import sqlite3
import logging
from aiogram import Bot, Dispatcher, types

from config import TOKEN
from app.handlers import router

API_KEY = TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt: #чтобы отключать бота комбинацией cntr + c 
        print("Exit")