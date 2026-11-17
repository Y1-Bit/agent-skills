"""Bot edge: the ONLY place where domain errors become chat replies.

Same idea as entrypoints/http/error_handlers.py: handlers never catch; the error
*category* decides the reply. Unexpected exceptions propagate to aiogram's error
handling and logs — they are bugs, not user mistakes.
"""

from collections.abc import Awaitable, Callable
from typing import override

import structlog
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update

from app.shared.domain.errors import (
    ConflictError,
    DomainError,
    InvalidValueError,
    NotFoundError,
    RuleViolationError,
)

type Handler = Callable[[TelegramObject, dict[str, object]], Awaitable[object]]

_REPLY_BY_CATEGORY: dict[type[DomainError], str] = {
    InvalidValueError: "⚠️ {message}. Please try again.",
    NotFoundError: "🔍 {message}",
    ConflictError: "⛔ {message}",
    RuleViolationError: "⛔ {message}",
}
_FALLBACK = "Something went wrong. Please try again later."


def reply_for(error: DomainError) -> str:
    for category in type(error).__mro__:
        template = _REPLY_BY_CATEGORY.get(category)
        if template is not None:
            return template.format(message=error.message)
    return _FALLBACK


class DomainErrorMiddleware(BaseMiddleware):
    @override
    async def __call__(
        self, handler: Handler, event: TelegramObject, data: dict[str, object]
    ) -> object:
        try:
            return await handler(event, data)
        except DomainError as error:
            if isinstance(event, Message | CallbackQuery):
                await event.answer(reply_for(error))
            return None


class LogContextMiddleware(BaseMiddleware):
    """Bind update/chat/user ids once, so every log line in the update carries them."""

    @override
    async def __call__(
        self, handler: Handler, event: TelegramObject, data: dict[str, object]
    ) -> object:
        structlog.contextvars.clear_contextvars()
        if isinstance(event, Update):
            structlog.contextvars.bind_contextvars(update_id=event.update_id)
        return await handler(event, data)
