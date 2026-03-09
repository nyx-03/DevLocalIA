from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router
from app.core.logging import setup_logging
from app.core.config import get_settings
from app.repositories.index_repository import IndexRepository


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="DevLocal AI", version="0.1.0")
    app.include_router(router)

    @app.on_event("startup")
    def init_db() -> None:
        settings = get_settings()
        IndexRepository(settings.db_path)

    return app


app = create_app()
