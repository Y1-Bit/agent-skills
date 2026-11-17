from dataclasses import dataclass

from app.books.application.ports import BookIdGenerator, BooksUnitOfWork, Clock
from app.books.domain.book import Book
from app.books.domain.errors import DuplicateBookError
from app.books.domain.value_objects import BookId, BookProfile, UserId
from app.shared.application.decorators import logged, transactional


@dataclass(frozen=True, slots=True)
class CatalogBook:
    profile: BookProfile
    librarian_user_id: UserId


@dataclass(frozen=True, slots=True)
class CatalogBookHandler:
    """One use case = one class with one public method.

    Only business steps live here: transactions and logging come from decorators,
    error responses from the edge handler.
    """

    uow: BooksUnitOfWork
    ids: BookIdGenerator
    clock: Clock

    @logged
    @transactional
    async def __call__(self, command: CatalogBook) -> BookId:
        profile = command.profile
        books = self.uow.books
        if await books.book_exists(profile.isbn):
            raise DuplicateBookError(profile.isbn)

        book = Book.catalog(
            book_id=self.ids.next_id(),
            profile=profile,
            librarian_user_id=command.librarian_user_id,
            now=self.clock.now(),
        )
        await books.add(book)
        return book.id
