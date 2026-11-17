import pytest

from app.books.domain.value_objects import BookId, BookTitle, CountryCode, Isbn
from app.shared.domain.errors import InvalidValueError


@pytest.mark.parametrize("raw", ["", "   ", "x" * 201])
def test_title_rejects_blank_or_too_long(raw: str) -> None:
    with pytest.raises(InvalidValueError, match="BookTitle"):
        BookTitle(raw)


def test_parse_strips_whitespace() -> None:
    assert BookTitle.parse("  Dune  ").value == "Dune"


def test_country_code_is_normalised_on_parse() -> None:
    assert CountryCode.parse(" de ").value == "DE"


@pytest.mark.parametrize("raw", ["DEU", "D1", "de"])
def test_country_code_rejects_non_iso(raw: str) -> None:
    with pytest.raises(InvalidValueError, match="ISO 3166"):
        CountryCode(raw)


@pytest.mark.parametrize("raw", ["0441013597", "9770441013593", "978044101359X", "97804410135930"])
def test_isbn_requires_thirteen_digits_with_a_book_prefix(raw: str) -> None:
    with pytest.raises(InvalidValueError, match="Isbn"):
        Isbn(raw)


def test_book_id_requires_prefix() -> None:
    with pytest.raises(InvalidValueError, match="bk_"):
        BookId("usr_12345678")


def test_value_objects_compare_by_value() -> None:
    assert BookTitle("Dune") == BookTitle("Dune")
