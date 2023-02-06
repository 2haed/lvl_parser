import asyncio
import logging
import warnings

import asyncpg
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Text, Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from config import settings

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = Bot(token=settings.telegram.bot_token)
dp = Dispatcher()
router = Router()


@dp.message(Command("get_team_info"))
async def get_team_info(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Получить расписание игр команды"),
            types.KeyboardButton(text="Получить информацию о команде"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Введите название команды"
    )
    await message.answer("Введите действие", reply_markup=keyboard)


@dp.message(Text(text="Получить расписание игр команды", ignore_case=True))
async def get_team_schedule(message: types.Message, conn: asyncpg.Connection):
    row = await conn.fetch('select * from public.teams where team = $1', 'ОСНОВА')
    await message.answer(f'Ваш запрос про команду: {row[0]}')


@dp.message(Text(text="Получить информацию о команде", ignore_case=True))
async def get_team_stat(message: types.Message, conn: asyncpg.Connection):
    row = await conn.fetch('select * from public.schedule where host = "ОСНОВА" or guest = "ОСНОВА"')
    await message.answer(f'Ваш запрос про команду: {row[0]}')


@router.message(Command(commands=["info"]))
async def msg(message: types.Message, conn: asyncpg.Connection):
    row = await conn.fetch('select * from public.teams where team = $1', 'ОСНОВА')
    await message.answer(f'Ваш запрос про команду: {row[0]}')


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
