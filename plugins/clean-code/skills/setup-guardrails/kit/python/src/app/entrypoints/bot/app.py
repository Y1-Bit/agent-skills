from aiogram import Dispatcher
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage

from app.entrypoints.bot.handlers import build_router
from app.entrypoints.bot.middleware import DomainErrorMiddleware, LogContextMiddleware
from app.entrypoints.container import Container


def create_dispatcher(
    container: Container | None = None, storage: BaseStorage | None = None
) -> Dispatcher:
    dispatcher = Dispatcher(storage=storage or MemoryStorage())
    dispatcher["container"] = container or Container()
    dispatcher.update.outer_middleware(LogContextMiddleware())
    dispatcher.message.middleware(DomainErrorMiddleware())
    dispatcher.callback_query.middleware(DomainErrorMiddleware())
    dispatcher.include_router(build_router())
    return dispatcher
