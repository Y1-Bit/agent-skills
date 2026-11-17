from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.books.domain.value_objects import (
    BookId,
    BookProfile,
    BookTitle,
    CountryCode,
    Genre,
    Isbn,
    ShortTitle,
)

FIXED_NOW = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


@dataclass(slots=True)
class FixedClock:
    current: datetime = FIXED_NOW

    def now(self) -> datetime:
        return self.current


@dataclass(slots=True)
class SequentialIds:
    counter: int = field(default=0)

    def next_id(self) -> BookId:
        self.counter += 1
        return BookId(f"bk_{self.counter:08d}")


def make_profile(*, country: str = "DE", isbn: str = "9780441013593") -> BookProfile:
    return BookProfile(
        title=BookTitle("Dune"),
        short_title=ShortTitle("Dune"),
        isbn=Isbn(isbn),
        country=CountryCode.parse(country),
        genre=Genre.SCIENCE,
    )
