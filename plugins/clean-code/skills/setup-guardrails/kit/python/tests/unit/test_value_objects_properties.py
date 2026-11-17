"""Property-based tests: hypothesis generates thousands of inputs, incl. edge cases
an agent would never think of (unicode, whitespace-only, exact boundaries)."""

import string

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.books.domain.value_objects import BookTitle, CountryCode
from app.shared.domain.errors import InvalidValueError

valid_names = st.text(min_size=1, max_size=BookTitle.max_length).filter(lambda s: s.strip() != "")


@given(valid_names)
def test_any_non_blank_text_within_limits_is_accepted(raw: str) -> None:
    assert BookTitle(raw).value == raw


@given(st.text(min_size=BookTitle.max_length + 1, max_size=BookTitle.max_length + 50))
def test_text_over_the_limit_is_always_rejected(raw: str) -> None:
    with pytest.raises(InvalidValueError):
        BookTitle(raw)


@given(st.text(alphabet=string.ascii_letters, min_size=2, max_size=2))
def test_parse_country_code_accepts_any_case(raw: str) -> None:
    assert CountryCode.parse(raw).value == raw.upper()


@given(valid_names)
def test_parse_is_idempotent(raw: str) -> None:
    once = BookTitle.parse(raw)
    assert BookTitle.parse(once.value) == once
