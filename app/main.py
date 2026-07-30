import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.config import BOT_TOKEN

# Імпортуємо всі наші роутери
from app.handlers.menu import menu_router
from app.handlers.ai_chat import ai_router
from app.handlers.job_search import job_router
from app.handlers.tasks_planner import tasks_planner_router  #

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()


    dp.include_router(ai_router)
    dp.include_router(tasks_planner_router)
    dp.include_router(job_router)
    dp.include_router(menu_router)

    logging.info("Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())