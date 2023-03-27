import asyncio
import logging
import warnings

import asyncpg
from aiogram import Dispatcher, Bot
from loguru import logger

from app.bot.handlers import router
from app.bot.middleware.database import DatabaseMiddleware
from app.config import settings

warnings.filterwarnings("ignore", category=DeprecationWarning)


async def register_middlewares(dp: Dispatcher) -> None:
    pool = await asyncpg.create_pool(
        user=settings.database.user,
        password=settings.database.password,
        database=settings.database.database,
        host=settings.database.host,
        port=settings.database.port
    )
    dp.update.middleware(DatabaseMiddleware(pool))


def register_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("Starting bot")

    bot = Bot(token=settings.telegram.bot_token, parse_mode="HTML")
    dp = Dispatcher()
    await register_middlewares(dp)
    register_handlers(dp)

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        await dp.storage.close()
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        logger.error("Bot stopper")
