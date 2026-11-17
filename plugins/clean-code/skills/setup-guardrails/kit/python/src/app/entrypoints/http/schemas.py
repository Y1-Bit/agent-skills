"""Transport DTOs. Pydantic lives only at the edge; the domain never sees it.

`to_command` is where raw input becomes domain types. Invalid values raise
InvalidValueError, which the central handler turns into a 422.
"""

from pydantic import BaseModel

from app.books.application.catalog_book import CatalogBook
from app.books.domain.book import Book
from app.books.domain.value_objects import (
    BookProfile,
    BookTitle,
    CountryCode,
    Genre,
    Isbn,
    ShortTitle,
    UserId,
)


class CatalogBookRequest(BaseModel):
    title: str
    short_title: str
    isbn: str
    country_code: str
    genre: Genre
    librarian_user_id: int

    def to_command(self) -> CatalogBook:
        profile = BookProfile(
            title=BookTitle.parse(self.title),
            short_title=ShortTitle.parse(self.short_title),
            isbn=Isbn.parse(self.isbn),
            country=CountryCode.parse(self.country_code),
            genre=self.genre,
        )
        return CatalogBook(profile=profile, librarian_user_id=UserId(self.librarian_user_id))


class BookResponse(BaseModel):
    id: str
    short_title: str
    country_code: str
    status: str

    @classmethod
    def from_domain(cls, book: Book) -> "BookResponse":
        return cls(
            id=str(book.id),
            short_title=str(book.profile.short_title),
            country_code=str(book.profile.country),
            status=book.status.value,
        )
