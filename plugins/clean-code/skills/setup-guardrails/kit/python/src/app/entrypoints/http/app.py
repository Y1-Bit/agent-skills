from fastapi import FastAPI

from app.entrypoints.container import Container
from app.entrypoints.http.error_handlers import install_error_handlers
from app.entrypoints.http.middleware import install_middleware
from app.entrypoints.http.routes import router


def create_app(container: Container | None = None) -> FastAPI:
    app = FastAPI(title="app")
    app.state.container = container or Container()
    install_error_handlers(app)
    install_middleware(app)
    app.include_router(router)
    return app
