"""Tests written because `make mutate` showed surviving mutants despite 99% coverage.

Each test names the mutant class it kills. This is the workflow: coverage says the
line ran, mutation testing says whether any assertion would notice it breaking.
"""

from collections.abc import Callable

import pytest

from app.books.domain.book import Book
from app.books.domain.errors import BookWithdrawnError
from app.books.domain.value_objects import (
    BookId,
    BookStatus,
    BookTitle,
    CountryCode,
    UserId,
)
from app.shared.domain.errors import InvalidValueError
from tests.fakes import FIXED_NOW, make_profile


def _book() -> Book:
    return Book.catalog(
        book_id=BookId("bk_00000001"),
        profile=make_profile(),
        librarian_user_id=UserId(7),
        now=FIXED_NOW,
    )


def test_exact_max_length_is_accepted() -> None:
    """Kills `<=` → `<` (off-by-one at the upper bound)."""
    assert BookTitle("x" * BookTitle.max_length).value == "x" * BookTitle.max_length


def test_catalog_keeps_the_librarian() -> None:
    assert _book().librarian_user_id == UserId(7)


def test_withdraw_sets_withdrawn_status() -> None:
    book = _book()
    book.withdraw()
    assert book.status is BookStatus.WITHDRAWN


def test_withdrawn_error_names_the_book() -> None:
    book = _book()
    book.withdraw()
    with pytest.raises(BookWithdrawnError, match="bk_00000001"):
        book.withdraw()


@pytest.mark.parametrize(
    ("build", "expected"),
    [
        (lambda: BookTitle("  "), "BookTitle: must not be blank"),
        (lambda: BookTitle("x" * 201), "BookTitle: length must be within 1..200"),
        (lambda: CountryCode("D1"), "CountryCode: must be an ISO 3166-1 alpha-2 code, e.g. 'DE'"),
    ],
)
def test_invalid_value_messages_are_exact(build: Callable[[], object], expected: str) -> None:
    with pytest.raises(InvalidValueError) as caught:
        build()
    assert caught.value.message == expected
    assert caught.value.field == expected.split(":", maxsplit=1)[0]
