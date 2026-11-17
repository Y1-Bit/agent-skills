"""Cross-cutting concerns as decorators, so use cases contain only business steps.

Without these, agents repeat the same boilerplate in every handler:
`try: ... session.commit() except: session.rollback(); logger.exception(...)`.
"""

import functools
import time
from collections.abc import Awaitable, Callable
from typing import Protocol

import structlog

from app.shared.application.unit_of_work import UnitOfWork
from app.shared.domain.errors import DomainError

logger = structlog.get_logger("use_case")


class HasUnitOfWork(Protocol):
    @property
    def uow(self) -> UnitOfWork: ...


type UseCase[H, C, R] = Callable[[H, C], Awaitable[R]]


def transactional[H: HasUnitOfWork, C, R](method: UseCase[H, C, R]) -> UseCase[H, C, R]:
    """Run the use case inside `self.uow`; commit on success, roll back on any error."""

    @functools.wraps(method)
    async def wrapper(self: H, command: C) -> R:
        async with self.uow:
            result = await method(self, command)
            await self.uow.commit()
        return result

    return wrapper


def logged[H, C, R](method: UseCase[H, C, R]) -> UseCase[H, C, R]:
    """Log name, duration and outcome of a use case. Re-raises; never swallows."""

    @functools.wraps(method)
    async def wrapper(self: H, command: C) -> R:
        name = type(self).__name__
        started = time.perf_counter()
        outcome = "ok"
        try:
            return await method(self, command)
        except DomainError as error:
            outcome = error.code
            raise
        except Exception:
            outcome = "crash"
            raise
        finally:
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            logger.info("use_case", name=name, outcome=outcome, elapsed_ms=elapsed_ms)

    return wrapper
