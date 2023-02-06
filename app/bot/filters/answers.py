import asyncpg
from aiogram import Router, types
from aiogram.filters import Text

from app.bot.handlers.base import router


@router.message(Text(text="Получить расписание игр команды", ignore_case=True))
async def get_team_schedule(message: types.Message):
    await message.answer("TEST TEAM SCHEDULE")


@router.message(Text(text="Получить информацию о команде", ignore_case=True))
async def get_team_stat(message: types.Message):
    await message.answer("TEST TEAM INFO")

#
# @router.message(Text(text="Получить расписание игр команды", ignore_case=True))
# async def get_team_schedule(message: types.Message, conn: asyncpg.Connection):
#     row = await conn.fetch('select * from public.teams where team = $1', 'ОСНОВА')
#     await message.answer(f'Ваш запрос про команду: {row[0]}')
#
#
# @router.message(Text(text="Получить информацию о команде", ignore_case=True))
# async def get_team_stat(message: types.Message, conn: asyncpg.Connection):
#     row = await conn.fetch('select * from public.schedule where host = "ОСНОВА" or guest = "ОСНОВА"')
#     await message.answer(f'Ваш запрос про команду: {row[0]}')
