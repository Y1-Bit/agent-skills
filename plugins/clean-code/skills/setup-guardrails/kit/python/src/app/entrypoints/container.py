"""Composition root: the one place that knows which adapter backs which port."""

from dataclasses import dataclass, field

from app.books.application.catalog_book import CatalogBookHandler
from app.books.application.get_book import GetBookHandler
from app.books.application.ports import BookIdGenerator, BooksUnitOfWork, Clock
from app.books.application.withdraw_book import WithdrawBookHandler
from app.books.infrastructure.in_memory import (
    InMemoryUnitOfWork,
    RandomBookIdGenerator,
    SystemClock,
)


@dataclass(slots=True)
class Container:
    uow: BooksUnitOfWork = field(default_factory=InMemoryUnitOfWork)
    ids: BookIdGenerator = field(default_factory=RandomBookIdGenerator)
    clock: Clock = field(default_factory=SystemClock)

    def catalog_book(self) -> CatalogBookHandler:
        return CatalogBookHandler(uow=self.uow, ids=self.ids, clock=self.clock)

    def withdraw_book(self) -> WithdrawBookHandler:
        return WithdrawBookHandler(uow=self.uow)

    def get_book(self) -> GetBookHandler:
        return GetBookHandler(uow=self.uow)
