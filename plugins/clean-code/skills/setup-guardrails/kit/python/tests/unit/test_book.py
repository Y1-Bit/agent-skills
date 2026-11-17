from datetime import datetime

import pytest

from app.books.domain.book import Book
from app.books.domain.errors import BookWithdrawnError, NaiveDatetimeError
from app.books.domain.value_objects import BookId, BookStatus, ShortTitle, UserId
from tests.fakes import FIXED_NOW, make_profile


def _book() -> Book:
    return Book.catalog(
        book_id=BookId("bk_00000001"),
        profile=make_profile(),
        librarian_user_id=UserId(7),
        now=FIXED_NOW,
    )


def test_catalog_starts_active_at_version_one() -> None:
    book = _book()
    assert book.status is BookStatus.ACTIVE
    assert book.version == 1


def test_catalog_rejects_naive_datetime() -> None:
    with pytest.raises(NaiveDatetimeError):
        Book.catalog(
            book_id=BookId("bk_00000001"),
            profile=make_profile(),
            librarian_user_id=UserId(7),
            now=datetime(2026, 1, 1),  # noqa: DTZ001 — the naive value is the point of the test
        )


def test_rename_bumps_version() -> None:
    book = _book()
    book.rename(ShortTitle("Dune Saga"))
    assert book.profile.short_title == ShortTitle("Dune Saga")
    assert book.version == 2


def test_withdrawn_book_cannot_be_renamed() -> None:
    book = _book()
    book.withdraw()
    with pytest.raises(BookWithdrawnError):
        book.rename(ShortTitle("Nope"))
