"""The ONLY place where domain errors become HTTP responses.

Routes and use cases never catch domain errors. They propagate here, and the
error *category* (by MRO) decides the status code. A new error type needs no
new handler, only the right base class.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.shared.domain.errors import (
    ConflictError,
    DomainError,
    InvalidValueError,
    NotFoundError,
    RuleViolationError,
)

_STATUS_BY_CATEGORY: dict[type[DomainError], int] = {
    InvalidValueError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    RuleViolationError: status.HTTP_409_CONFLICT,
}


def _status_for(error: DomainError) -> int:
    for category in type(error).__mro__:
        if category in _STATUS_BY_CATEGORY:
            return _STATUS_BY_CATEGORY[category]
    return status.HTTP_400_BAD_REQUEST


async def _handle_domain_error(_: Request, error: Exception) -> JSONResponse:
    if not isinstance(error, DomainError):
        raise error
    return JSONResponse(
        status_code=_status_for(error),
        content={"error": {"code": error.code, "message": error.message}},
    )


def install_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _handle_domain_error)
