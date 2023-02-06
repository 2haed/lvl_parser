import asyncio
import logging
import warnings

from aiogram import Dispatcher, Bot
from loguru import logger

from app.bot.filters.answers import router
from config import settings

warnings.filterwarnings("ignore", category=DeprecationWarning)


# @router.message(Command(commands=["info"]))
# async def msg(message: types.Message, conn: asyncpg.Connection):
#     row = await conn.fetch('select * from public.teams where team = $1', 'ОСНОВА')
#     await message.answer(f'Ваш запрос про команду: {row[0]}')


# conn = await asyncpg.connect(
#     host=settings.database.host,
#     database=settings.database.database,
#     user=settings.database.user,
#     password=settings.database.password
# )
# conn.close()

def register_middlewares(dp: Dispatcher) -> None:
    # Add middlewares if needed
    pass


def register_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("Starting bot")

    bot = Bot(token=settings.telegram.token, parse_mode="HTML")
    dp = Dispatcher()

    register_middlewares(dp)
    register_handlers(dp)

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        await dp.storage.close()
        await bot.session.close()
        logger.info("Bot stopped")


if "__name__" == "__main__":
    try:
        asyncio.run(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        logger.error("Bot stopper")
