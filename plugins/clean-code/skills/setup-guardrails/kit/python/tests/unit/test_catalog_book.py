import pytest

from app.books.application.catalog_book import CatalogBook, CatalogBookHandler
from app.books.domain.errors import DuplicateBookError
from app.books.domain.value_objects import BookId, UserId
from app.books.infrastructure.in_memory import InMemoryUnitOfWork
from tests.fakes import FIXED_NOW, FixedClock, SequentialIds, make_profile


@pytest.fixture
def uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork()


@pytest.fixture
def handler(uow: InMemoryUnitOfWork) -> CatalogBookHandler:
    return CatalogBookHandler(uow=uow, ids=SequentialIds(), clock=FixedClock())


async def test_catalogs_persists_and_commits_once(
    handler: CatalogBookHandler, uow: InMemoryUnitOfWork
) -> None:
    book_id = await handler(CatalogBook(make_profile(), UserId(1)))

    stored = await uow.books.get(book_id)
    assert book_id == BookId("bk_00000001")
    assert stored.created_at == FIXED_NOW
    assert uow.commits == 1


async def test_rejects_duplicate_book_without_committing(
    handler: CatalogBookHandler, uow: InMemoryUnitOfWork
) -> None:
    await handler(CatalogBook(make_profile(), UserId(1)))

    with pytest.raises(DuplicateBookError):
        await handler(CatalogBook(make_profile(), UserId(2)))
    assert uow.commits == 1
    assert len(uow.books.items) == 1
