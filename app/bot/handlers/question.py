from aiogram import Router, types
from aiogram.filters import Text, Command

from app.bot.handlers.base import router


@router.message(Command("get_team_info"))
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
