from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from asyncpg import Pool


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, pool: Pool):
        super().__init__()
        self.pool: Pool = pool

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        async with self.pool.acquire() as conn: # type: asyncpg.Connection
            data['conn'] = conn
            return await handler(event, data)
