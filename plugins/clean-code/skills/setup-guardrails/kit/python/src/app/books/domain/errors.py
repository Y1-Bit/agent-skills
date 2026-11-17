from app.books.domain.value_objects import BookId, Isbn
from app.shared.domain.errors import ConflictError, NotFoundError, RuleViolationError


class BookNotFoundError(NotFoundError):
    def __init__(self, book_id: BookId) -> None:
        super().__init__(f"book {book_id} not found")


class DuplicateBookError(ConflictError):
    def __init__(self, isbn: Isbn) -> None:
        super().__init__(f"ISBN {isbn} is already in the catalog")


class BookWithdrawnError(RuleViolationError):
    def __init__(self, book_id: BookId) -> None:
        super().__init__(f"book {book_id} is withdrawn")


class NaiveDatetimeError(RuleViolationError):
    def __init__(self) -> None:
        super().__init__("timestamps must be timezone-aware")
