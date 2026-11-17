"""Unit of Work: one transaction per use case, opened and committed in ONE place.

Handlers never call `commit()` themselves (ast-grep rule `commit-only-in-uow`).
They are decorated with `@transactional`, which commits on success; leaving the
`async with` block without a commit rolls back.
"""

from typing import Protocol, Self


class UnitOfWork(Protocol):
    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, *exc_info: object) -> None:
        """Roll back anything not committed."""
        ...

    async def commit(self) -> None: ...
