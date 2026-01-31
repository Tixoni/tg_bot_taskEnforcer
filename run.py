import asyncio
import logging
import uvicorn
from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router
from app.database import init_db
from app.myapi import app  

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def start_bot():
    dp.include_router(router)
    await dp.start_polling(bot)

async def main():
    init_db()
    
    # Запускаем бота как отдельную задачу
    bot_task = asyncio.create_task(start_bot())
    
    # Настраиваем и запускаем сервер
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    
    # Ждем выполнения обоих процессов
    await server.serve()
    await bot_task

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")