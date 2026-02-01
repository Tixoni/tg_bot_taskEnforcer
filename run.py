import asyncio
import logging
import os 
import uvicorn
from aiogram import Bot, Dispatcher
from datetime import datetime, timedelta

# Импортируем обновленный метод для привычек и метод для очистки задач
from app.database import init_db, reset_daily_habits, delete_completed_tasks
from config import TOKEN
from app.handlers import router
from app.myapi import app  

async def start_bot(bot, dp):
    dp.include_router(router)
    # drop_pending_updates=True удалит сообщения, пришедшие пока бот был выключен
    await bot.delete_webhook(drop_pending_updates=True) 
    await dp.start_polling(bot)

async def schedule_daily_reset():
    """Запуск процесса в 23:58 для учета выполненных привычек и очистки задач."""
    while True:
        now = datetime.now()
        # Устанавливаем целевое время на сегодня 23:58
        target_time = now.replace(hour=23, minute=58, second=0, microsecond=0)
        
        # Если 23:58 сегодня уже прошло, планируем на завтра
        if now >= target_time:
            target_time += timedelta(days=1)
        
        wait_seconds = (target_time - now).total_seconds()
        logging.info(f"Следующее обновление запланировано на {target_time} (через {wait_seconds:.0f} сек.)")
        
        await asyncio.sleep(wait_seconds)
        
        # Выполнение операций
        logging.info("Запуск ежедневного обновления данных...")
        
        # 1. Сброс привычек с обновлением счетчика count_complete
        try:
            reset_daily_habits()
            logging.info("Статус привычек обновлен: count_complete увеличен для выполненных.")
        except Exception as e:
            logging.error(f"Ошибка при обновлении привычек: {e}")

        # 2. Удаление выполненных задач
        try:
            deleted_count = delete_completed_tasks()
            logging.info(f"Удалено выполненных задач: {deleted_count}")
        except Exception as e:
            logging.error(f"Ошибка при удалении задач: {e}")

async def main():
    # Инициализация структуры БД при запуске [cite: 53, 54]
    init_db()
    
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    # Получаем порт от Railway [cite: 54]
    port = int(os.environ.get("PORT", 8000))
    
    # Запускаем бота и планировщик как фоновые задачи
    bot_task = asyncio.create_task(start_bot(bot, dp))
    asyncio.create_task(schedule_daily_reset())

    # Настройка и запуск API сервера [cite: 54]
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    
    logging.info(f"Сервер запущен на порту {port}")
    await server.serve()
    await bot_task

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Выход")