import asyncio
import logging
import os 
import uvicorn
from aiogram import Bot, Dispatcher
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Важно: используем zoneinfo вместо pytz

# Импортируем обновленный метод для привычек и метод для очистки задач
from app.database import init_db, reset_daily_habits, delete_completed_tasks
from config import TOKEN
from app.handlers import router
from app.myapi import app  

# Определяем часовые пояса
SERVER_TZ = ZoneInfo("America/Los_Angeles")  # Пояс сервера (Калифорния)
USER_TZ = ZoneInfo("Europe/Moscow")          # Пояс пользователей (Москва)

async def start_bot(bot, dp):
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True) 
    await dp.start_polling(bot)

async def schedule_daily_reset():
    """Запуск процесса в 23:58 по московскому времени."""
    while True:
        # Получаем текущее время в UTC
        utc_now = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
        
        # Конвертируем в московское время
        moscow_now = utc_now.astimezone(USER_TZ)
        
        # Устанавливаем целевое время на сегодня 23:58 по Москве
        target_time = moscow_now.replace(hour=23, minute=58, second=0, microsecond=0)
        
        # Если 23:58 уже прошло, планируем на завтра
        if moscow_now >= target_time:
            target_time += timedelta(days=1)
        
        # Конвертируем целевое время обратно в UTC для расчета sleep
        target_time_utc = target_time.astimezone(ZoneInfo("UTC"))
        
        # Вычисляем разницу в секундах
        wait_seconds = (target_time_utc - utc_now).total_seconds()
        
        logging.info(f"Текущее время по Москве: {moscow_now.strftime('%H:%M:%S')}")
        logging.info(f"Следующее обновление запланировано на {target_time.strftime('%Y-%m-%d %H:%M:%S')} по Москве (через {wait_seconds:.0f} сек.)")
        
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

async def get_moscow_time():
    """Вспомогательная функция для получения текущего московского времени"""
    utc_now = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
    return utc_now.astimezone(USER_TZ)

async def get_server_time():
    """Вспомогательная функция для получения текущего времени сервера"""
    utc_now = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
    return utc_now.astimezone(SERVER_TZ)

async def main():
    # Инициализация структуры БД при запуске
    init_db()
    
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    # Получаем порт от Railway
    port = int(os.environ.get("PORT", 8000))
    
    # Логируем информацию о времени
    server_time = await get_server_time()
    moscow_time = await get_moscow_time()
    logging.info(f"Время на сервере (Калифорния): {server_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    logging.info(f"Время для пользователей (Москва): {moscow_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    logging.info(f"Разница во времени: {(moscow_time - server_time).total_seconds()/3600:.1f} часов")
    
    # Запускаем бота и планировщик как фоновые задачи
    bot_task = asyncio.create_task(start_bot(bot, dp))
    asyncio.create_task(schedule_daily_reset())

    # Настройка и запуск API сервера
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