import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage. memory import MemoryStorage

from app.core.config import config
from app.core.logger import logger
from app.database.connection import init_db

from app.tg_admin.middlewares import AdminMiddleware
from app.tg_admin.handlers import base, settings, accounts

async def main():
    logger.info("Запуск бота")

    await init_db()

    bot = Bot(token=config.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(AdminMiddleware())
    dp.callback_query.middleware(AdminMiddleware())

    dp.include_router(base.router)
    dp.include_router(settings.router)
    dp.include_router(accounts.router)
    try:
        logger.info("Бот успешно запущен и слушает")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}")
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Остановка по Ctrl+C")
