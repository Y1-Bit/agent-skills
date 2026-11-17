from dataclasses import dataclass

from app.books.application.ports import BooksUnitOfWork
from app.books.domain.book import Book
from app.books.domain.value_objects import BookId


@dataclass(frozen=True, slots=True)
class GetBook:
    book_id: BookId


@dataclass(frozen=True, slots=True)
class GetBookHandler:
    """Read-only query: opens the UoW for a consistent read, never commits."""

    uow: BooksUnitOfWork

    async def __call__(self, query: GetBook) -> Book:
        async with self.uow:
            return await self.uow.books.get(query.book_id)
