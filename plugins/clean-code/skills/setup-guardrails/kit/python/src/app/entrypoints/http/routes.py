"""Routes are thin: parse → call use case → serialize. No try/except, no logic."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.books.application.get_book import GetBook
from app.books.application.withdraw_book import WithdrawBook
from app.books.domain.value_objects import BookId
from app.entrypoints.container import Container
from app.entrypoints.http.schemas import BookResponse, CatalogBookRequest

router = APIRouter(prefix="/books", tags=["books"])


def get_container(request: Request) -> Container:
    container: Container = request.app.state.container
    return container


ContainerDep = Annotated[Container, Depends(get_container)]


@router.post("", status_code=status.HTTP_201_CREATED)
async def catalog_book(body: CatalogBookRequest, container: ContainerDep) -> dict[str, str]:
    book_id = await container.catalog_book()(body.to_command())
    return {"id": str(book_id)}


@router.get("/{book_id}")
async def get_book(book_id: str, container: ContainerDep) -> BookResponse:
    book = await container.get_book()(GetBook(BookId.parse(book_id)))
    return BookResponse.from_domain(book)


@router.post("/{book_id}/withdraw", status_code=status.HTTP_204_NO_CONTENT)
async def withdraw_book(book_id: str, container: ContainerDep) -> None:
    command = WithdrawBook(book_id=BookId.parse(book_id))
    await container.withdraw_book()(command)
