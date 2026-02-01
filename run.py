import asyncio
import logging
import os 
import uvicorn
from aiogram import Bot, Dispatcher
from datetime import datetime, timedelta
from app.database import reset_habits_db, delete_completed_tasks


from config import TOKEN
from app.handlers import router
from app.database import init_db
from app.myapi import app  


async def start_bot(bot, dp):
    dp.include_router(router)
    # drop_pending_updates=True удалит сообщения, пришедшие пока бот был выключен
    await bot.delete_webhook(drop_pending_updates=True) 
    await dp.start_polling(bot)


async def schedule_daily_reset():
    """Каждый день в 00:00 (локальное время сервера): сброс привычек и удаление выполненных задач."""
    while True:
        now = datetime.now()
        tomorrow = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        seconds_until_midnight = (tomorrow - now).total_seconds()

        await asyncio.sleep(seconds_until_midnight)
        try:
            reset_habits_db()
            logging.info("Habits status reset for all users.")
        except Exception as e:
            logging.exception("Habits reset failed: %s", e)
        try:
            deleted = delete_completed_tasks()
            logging.info("Deleted %d completed tasks (daily cleanup).", deleted)
        except Exception as e:
            logging.exception("Delete completed tasks failed: %s", e)


async def main():
    init_db()
    
    # Инициализируем бота внутри асинхронной функции
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    # Получаем порт от Railway (автоматически)
    port = int(os.environ.get("PORT", 8000))
    
    bot_task = asyncio.create_task(start_bot(bot, dp))
    asyncio.create_task(schedule_daily_reset())

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