import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from app.locales import TEXTS


class ErrorHandlingMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logging.exception(f"Неперехваченное исключение: {e}")

            error_msg = TEXTS["ru"]["system_error"]
            if isinstance(event, Message):
                await event.answer(error_msg)
            elif isinstance(event, CallbackQuery):
                await event.answer(error_msg, show_alert=True)