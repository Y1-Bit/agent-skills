import copy
import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Self

from app.books.domain.book import Book
from app.books.domain.errors import BookNotFoundError
from app.books.domain.value_objects import BookId, Isbn


@dataclass(slots=True)
class InMemoryBookRepository:
    items: dict[BookId, Book] = field(default_factory=dict)

    async def get(self, book_id: BookId) -> Book:
        book = self.items.get(book_id)
        if book is None:
            raise BookNotFoundError(book_id)
        return book

    async def add(self, book: Book) -> None:
        self.items[book.id] = book

    async def save(self, book: Book) -> None:
        self.items[book.id] = book

    async def book_exists(self, isbn: Isbn) -> bool:
        return any(book.profile.isbn == isbn for book in self.items.values())


@dataclass(slots=True)
class InMemoryUnitOfWork:
    """Snapshot on enter, restore on exit unless committed — same contract as a DB UoW."""

    books: InMemoryBookRepository = field(default_factory=InMemoryBookRepository)
    commits: int = 0
    _snapshot: dict[BookId, Book] | None = None
    _committed: bool = False

    async def __aenter__(self) -> Self:
        self._snapshot = copy.deepcopy(self.books.items)
        self._committed = False
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        if not self._committed and self._snapshot is not None:
            self.books.items = self._snapshot
        self._snapshot = None

    async def commit(self) -> None:
        self._committed = True
        self.commits += 1


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class RandomBookIdGenerator:
    def next_id(self) -> BookId:
        return BookId(f"bk_{secrets.token_hex(8)}")
