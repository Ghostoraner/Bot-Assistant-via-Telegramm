from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from cachetools import TTLCache
from app.locales import TEXTS


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, time_limit: float = 1.5):
        # Кэш хранит ID пользователей в течение time_limit секунд
        self.cache = TTLCache(maxsize=10000, ttl=time_limit)

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id:
            if user_id in self.cache:
                # Спам обнаружен — блокируем обработку
                if isinstance(event, Message):
                    await event.answer(TEXTS["ru"]["rate_limit_error"])
                elif isinstance(event, CallbackQuery):
                    await event.answer(TEXTS["ru"]["rate_limit_error"], show_alert=True)
                return

            self.cache[user_id] = True

        return await handler(event, data)