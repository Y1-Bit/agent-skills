from dataclasses import dataclass

from app.books.application.ports import BooksUnitOfWork
from app.books.domain.value_objects import BookId
from app.shared.application.decorators import logged, transactional


@dataclass(frozen=True, slots=True)
class WithdrawBook:
    book_id: BookId


@dataclass(frozen=True, slots=True)
class WithdrawBookHandler:
    uow: BooksUnitOfWork

    @logged
    @transactional
    async def __call__(self, command: WithdrawBook) -> None:
        book = await self.uow.books.get(command.book_id)
        book.withdraw()
        await self.uow.books.save(book)
