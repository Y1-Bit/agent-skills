from dataclasses import dataclass, replace
from datetime import datetime
from typing import Self

from app.books.domain.errors import BookWithdrawnError, NaiveDatetimeError
from app.books.domain.value_objects import (
    BookId,
    BookProfile,
    BookStatus,
    ShortTitle,
    UserId,
)


@dataclass(slots=True)
class Book:
    """Aggregate root. Invariants live in methods, not in callers."""

    id: BookId
    profile: BookProfile
    librarian_user_id: UserId
    created_at: datetime
    status: BookStatus = BookStatus.ACTIVE
    version: int = 1

    @classmethod
    def catalog(
        cls,
        *,
        book_id: BookId,
        profile: BookProfile,
        librarian_user_id: UserId,
        now: datetime,
    ) -> Self:
        if now.tzinfo is None:
            raise NaiveDatetimeError
        return cls(
            id=book_id,
            profile=profile,
            librarian_user_id=librarian_user_id,
            created_at=now,
        )

    @property
    def is_active(self) -> bool:
        return self.status is BookStatus.ACTIVE

    def rename(self, short_title: ShortTitle) -> None:
        self._ensure_active()
        self.profile = replace(self.profile, short_title=short_title)
        self._touch()

    def withdraw(self) -> None:
        self._ensure_active()
        self.status = BookStatus.WITHDRAWN
        self._touch()

    def _ensure_active(self) -> None:
        if not self.is_active:
            raise BookWithdrawnError(self.id)

    def _touch(self) -> None:
        self.version += 1
