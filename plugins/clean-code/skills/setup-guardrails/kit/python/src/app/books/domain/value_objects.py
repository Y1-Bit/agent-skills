import re
from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar, NewType, Self

from app.shared.domain.errors import InvalidValueError
from app.shared.domain.value_objects import BoundedText, PatternText

UserId = NewType("UserId", int)


@dataclass(frozen=True, slots=True)
class BookId(PatternText):
    max_length: ClassVar[int] = 64
    pattern: ClassVar[re.Pattern[str]] = re.compile(r"bk_[a-z0-9]{8,}")
    pattern_hint: ClassVar[str] = "must look like 'bk_<lowercase alphanumerics>'"


@dataclass(frozen=True, slots=True)
class BookTitle(BoundedText):
    max_length: ClassVar[int] = 200


@dataclass(frozen=True, slots=True)
class ShortTitle(BoundedText):
    max_length: ClassVar[int] = 80


@dataclass(frozen=True, slots=True)
class Isbn(PatternText):
    max_length: ClassVar[int] = 13
    pattern: ClassVar[re.Pattern[str]] = re.compile(r"97[89]\d{10}")
    pattern_hint: ClassVar[str] = "must be a 13-digit ISBN"


@dataclass(frozen=True, slots=True)
class CountryCode(PatternText):
    pattern: ClassVar[re.Pattern[str]] = re.compile(r"[A-Z]{2}")
    pattern_hint: ClassVar[str] = "must be an ISO 3166-1 alpha-2 code, e.g. 'DE'"

    @classmethod
    def parse(cls, raw: str) -> Self:
        return cls(raw.strip().upper())


class Genre(StrEnum):
    FICTION = "fiction"
    SCIENCE = "science"
    HISTORY = "history"

    @classmethod
    def parse(cls, raw: str) -> "Genre":
        """`Genre("x")` would raise a bare ValueError (→ 500). Parse raises a domain error."""
        normalized = raw.strip().lower()
        if normalized not in cls._value2member_map_:
            choices = ", ".join(cls)
            raise InvalidValueError(field="Genre", reason=f"must be one of: {choices}")
        return cls(normalized)


class BookStatus(StrEnum):
    ACTIVE = "active"
    WITHDRAWN = "withdrawn"


@dataclass(frozen=True, slots=True)
class BookProfile:
    """Everything that describes the book, grouped as one value."""

    title: BookTitle
    short_title: ShortTitle
    isbn: Isbn
    country: CountryCode
    genre: Genre
