"""TYPICAL AGENT OUTPUT — fat route with local error handling. Negative example."""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/books/{book_id}/withdraw")
async def withdraw(book_id: str, repo, notify: bool = True):
    try:
        book = await repo.get(book_id)
        if book is None:
            raise HTTPException(404, "not found")
        if not book.is_active:
            raise HTTPException(409, "already withdrawn")
        book.withdraw()
        await repo.save(book)
        if notify:
            print(f"book {book_id} withdrawn")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"ok": True}
