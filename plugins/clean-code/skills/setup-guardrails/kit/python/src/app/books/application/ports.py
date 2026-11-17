"""Ports: what the application needs from the outside world, as Protocols.

Infrastructure implements them; tests pass fakes. Nothing here knows about
databases, HTTP or the system clock.
"""

from datetime import datetime
from typing import Protocol

from app.books.domain.book import Book
from app.books.domain.value_objects import BookId, Isbn
from app.shared.application.unit_of_work import UnitOfWork


class BookRepository(Protocol):
    async def get(self, book_id: BookId) -> Book:
        """Return the book or raise BookNotFoundError."""
        ...

    async def add(self, book: Book) -> None: ...

    async def save(self, book: Book) -> None: ...

    async def book_exists(self, isbn: Isbn) -> bool: ...


class BooksUnitOfWork(UnitOfWork, Protocol):
    """Repositories are reached through the UoW, so every write is transactional."""

    @property
    def books(self) -> BookRepository: ...


class Clock(Protocol):
    def now(self) -> datetime: ...


class BookIdGenerator(Protocol):
    def next_id(self) -> BookId: ...
