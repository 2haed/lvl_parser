from app.bot.bot import dp
from aiogram import Router, types
from aiogram.filters import Text

router = Router()


@dp.message(Text(text="Получить расписание игр команды", ignore_case=True))
async def get_team_schedule(message: types.Message):
    await message.answer("TEST TEAM SCHEDULE")


@dp.message(Text(text="Получить информацию о команде", ignore_case=True))
async def get_team_stat(message: types.Message):
    await message.answer("TEST TEAM INFO")
