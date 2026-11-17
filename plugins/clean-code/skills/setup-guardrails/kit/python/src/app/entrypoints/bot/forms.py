"""Bot input → domain values. Kept out of handlers.py so handlers stay branch-free."""

from collections.abc import Mapping

from aiogram.types import Message

from app.books.application.catalog_book import CatalogBook
from app.books.domain.value_objects import (
    BookProfile,
    BookTitle,
    CountryCode,
    Genre,
    Isbn,
    ShortTitle,
    UserId,
)
from app.shared.domain.errors import InvalidValueError


def message_text(message: Message) -> str:
    if message.text is None:
        raise InvalidValueError(field="message", reason="send text")
    return message.text


def sender_id(message: Message) -> UserId:
    if message.from_user is None:
        raise InvalidValueError(field="user", reason="unknown sender")
    return UserId(message.from_user.id)


def to_command(data: Mapping[str, object], user_id: UserId) -> CatalogBook:
    raw = {key: str(value) for key, value in data.items()}
    profile = BookProfile(
        title=BookTitle.parse(raw["title"]),
        short_title=ShortTitle.parse(raw["title"]),
        isbn=Isbn.parse(raw["isbn"]),
        country=CountryCode.parse(raw["country"]),
        genre=Genre.parse(raw["genre"]),
    )
    return CatalogBook(profile=profile, librarian_user_id=user_id)
