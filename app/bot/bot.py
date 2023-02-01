import asyncio
import logging
import warnings

import asyncpg
from aiogram import Bot, Dispatcher, types
from config import settings

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
bot = Bot(token=settings.telegram.bot_token)
dp = Dispatcher(bot)

HELP_COMMAND = """
/start - start bot
/get_team_info - get team info
"""


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    await message.answer(text=HELP_COMMAND)


@dp.message_handler(commands=["get_team_info"])
async def get_team_info(message: types.Message, conn: asyncpg.Connection):
    row = await conn.fetch('select * from public.teams where team = $1', 'ОСНОВА')
    await message.answer(row[0])


async def main():
    await dp.start_polling(bot)
    conn = await asyncpg.connect(
        host=settings.database.host,
        database=settings.database.database,
        user=settings.database.user,
        password=settings.database.password
    )
    conn.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
