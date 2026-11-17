"""Request-scoped logging context. Every log line inside a request — including the
`use_case` lines from `@logged` — carries the same request_id, with zero code in
handlers. Agents otherwise thread ids and loggers through every function.
"""

import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import FastAPI, Request, Response

logger = structlog.get_logger("http")

REQUEST_ID_HEADER = "X-Request-ID"


async def _bind_request_context(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)

    response.headers[REQUEST_ID_HEADER] = request_id
    logger.info(
        "request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        elapsed_ms=elapsed_ms,
    )
    return response


def install_middleware(app: FastAPI) -> None:
    app.middleware("http")(_bind_request_context)
