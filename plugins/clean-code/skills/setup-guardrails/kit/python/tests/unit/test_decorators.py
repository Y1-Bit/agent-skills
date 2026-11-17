from dataclasses import dataclass

import pytest
from structlog.testing import capture_logs

from app.books.domain.book import Book
from app.books.domain.errors import BookNotFoundError
from app.books.domain.value_objects import BookId, UserId
from app.books.infrastructure.in_memory import InMemoryUnitOfWork
from app.shared.application.decorators import logged, transactional
from tests.fakes import FIXED_NOW, make_profile


def _book() -> Book:
    return Book.catalog(
        book_id=BookId("bk_00000001"),
        profile=make_profile(),
        librarian_user_id=UserId(1),
        now=FIXED_NOW,
    )


class BoomError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class AddThenFail:
    uow: InMemoryUnitOfWork

    @logged
    @transactional
    async def __call__(self, command: Book) -> None:
        await self.uow.books.add(command)
        raise BookNotFoundError(command.id)


@dataclass(frozen=True, slots=True)
class Crash:
    uow: InMemoryUnitOfWork

    @logged
    async def __call__(self, command: str) -> None:
        raise BoomError(command)


async def test_transactional_rolls_back_on_error() -> None:
    uow = InMemoryUnitOfWork()

    with pytest.raises(BookNotFoundError):
        await AddThenFail(uow)(_book())

    assert uow.books.items == {}
    assert uow.commits == 0


async def test_logged_records_domain_error_code() -> None:
    with capture_logs() as logs, pytest.raises(BookNotFoundError):
        await AddThenFail(InMemoryUnitOfWork())(_book())

    assert logs[0]["name"] == "AddThenFail"
    assert logs[0]["outcome"] == "not_found"


async def test_logged_marks_unexpected_errors_as_crash() -> None:
    with capture_logs() as logs, pytest.raises(BoomError):
        await Crash(InMemoryUnitOfWork())("x")

    assert logs[0]["outcome"] == "crash"
