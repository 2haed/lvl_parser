import logging
import warnings
from aiogram import types, Router
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import hlink, hbold
from loguru import logger

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    logger.info("User {user} start conversation with bot", user=message.from_user.id)
    await message.answer(
        (
            "Привет, {user}.\n"
            "Жми /help если хочешь ознакомиться со списком команд.\n"
            "Это open source проект, вот ссылка: {source_url}"
        ).format(
            user=hbold(message.from_user.full_name),
            source_url=hlink("GitHub", "https://github.com/2haed/lvl_parser"),
        )
    )


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        (
            "Список команд:\n"
            "/help - Показывает этот список\n"
            "/start - Начать диалог с ботом\n"
            "/leagues - Показать лиги из лвл\n"
            "/teams - Показать команды из лвл\n"
        )
    )