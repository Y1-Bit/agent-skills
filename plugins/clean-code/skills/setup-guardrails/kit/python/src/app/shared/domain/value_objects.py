"""Reusable value-object bases.

Instead of N copy-pasted `_validate_x` methods on an aggregate, each concept
gets its own tiny type that validates itself once, at construction. After that,
holding a `BookTitle` *is* the proof that it is valid.
"""

import re
from dataclasses import dataclass
from typing import ClassVar, Self

from app.shared.domain.errors import InvalidValueError


@dataclass(frozen=True, slots=True)
class BoundedText:
    """Non-blank text with a length range. Subclass and override the limits."""

    value: str

    min_length: ClassVar[int] = 1
    max_length: ClassVar[int] = 255

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise InvalidValueError(field=self._field(), reason="must not be blank")
        if not self.min_length <= len(self.value) <= self.max_length:
            reason = f"length must be within {self.min_length}..{self.max_length}"
            raise InvalidValueError(field=self._field(), reason=reason)

    @classmethod
    def parse(cls, raw: str) -> Self:
        return cls(raw.strip())

    def _field(self) -> str:
        return type(self).__name__

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class PatternText(BoundedText):
    """BoundedText that must also fully match `pattern`."""

    pattern: ClassVar[re.Pattern[str]] = re.compile(r".+")
    pattern_hint: ClassVar[str] = "invalid format"

    def __post_init__(self) -> None:
        BoundedText.__post_init__(self)  # zero-arg super() breaks on slots=True dataclasses
        if not self.pattern.fullmatch(self.value):
            raise InvalidValueError(field=self._field(), reason=self.pattern_hint)
