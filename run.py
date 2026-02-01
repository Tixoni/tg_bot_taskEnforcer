import asyncio
import logging
import os  # ЭТОГО ИМПОРТА НЕ ХВАТАЛО!
import uvicorn
from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router
from app.database import init_db
from app.myapi import app  


async def start_bot(bot, dp):
    dp.include_router(router)
    # drop_pending_updates=True удалит сообщения, пришедшие пока бот был выключен
    await bot.delete_webhook(drop_pending_updates=True) 
    await dp.start_polling(bot)

async def main():
    init_db()
    
    # Инициализируем бота внутри асинхронной функции
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    # Получаем порт от Railway (автоматически)
    port = int(os.environ.get("PORT", 8000))
    
    bot_task = asyncio.create_task(start_bot(bot, dp))
    
    # Используем переменную port
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    
    logging.info(f"Server starting on port {port}")
    await server.serve()
    await bot_task

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")