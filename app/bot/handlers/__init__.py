from aiogram import Router
from app.bot.handlers.base import router as base_router
from app.bot.handlers.question import router as question_router
from app.bot.handlers.answers import router as answers_router

router = Router()

router.include_router(base_router)
router.include_router(question_router)
router.include_router(answers_router)
