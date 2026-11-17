"""TYPICAL AGENT OUTPUT — kept as a negative example. `make demo-violations` shows what catches it.

Compare with src/app/books/domain/book.py + value_objects.py.
"""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class Book:
    id: int | None
    version: int
    public_id: str
    title: str
    country_code: str
    isbn: str
    short_title: str
    created_at: datetime
    librarian_user_id: int
    is_active: bool
    is_deleted: bool

    def __post_init__(self) -> None:
        if not self.public_id:
            msg = "public_id must be provided"
            raise ValueError(msg)
        if len(self.title) < 1 or len(self.title) > 200:
            msg = "title must be 1..200 characters"
            raise ValueError(msg)
        if len(self.country_code) != 2 or not self.country_code.isalpha():
            msg = "country_code must be ISO alpha-2"
            raise ValueError(msg)
        if len(self.short_title) < 1 or len(self.short_title) > 80:
            msg = "short_title must be 1..80 characters"
            raise ValueError(msg)

    @classmethod
    def create(
        cls,
        public_id: str,
        title: str,
        country_code: str,
        isbn: str,
        short_title: str,
    ) -> "Book":
        return cls(
            id=None,
            version=1,
            public_id=public_id,
            title=title,
            country_code=country_code.upper(),
            isbn=isbn,
            short_title=short_title,
            created_at=datetime.now(timezone.utc),
            librarian_user_id=1,
            is_active=True,
            is_deleted=False,
        )

    def withdraw(self) -> None:
        try:
            if not self.is_active:
                raise RuntimeError("already withdrawn")
            self.is_active = False
        except RuntimeError:
            pass  # type: ignore
