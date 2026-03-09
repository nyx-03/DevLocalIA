from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.logging import setup_logging
from app.core.config import get_settings
from app.repositories.index_repository import IndexRepository
from app.llm.ollama_client import OllamaError


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="DevLocal AI", version="0.1.0")
    app.include_router(router)

    @app.on_event("startup")
    def init_db() -> None:
        settings = get_settings()
        IndexRepository(settings.db_path)

    @app.exception_handler(OllamaError)
    async def handle_ollama_error(request: Request, exc: OllamaError) -> JSONResponse:
        status = exc.status_code or 502
        return JSONResponse(status_code=status, content={"detail": str(exc)})

    return app


app = create_app()
