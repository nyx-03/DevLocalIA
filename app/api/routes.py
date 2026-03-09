from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path

from app.models.schema import (
    ChatRequest,
    ChatResponse,
    DocRequest,
    DocResponse,
    TestRequest,
    TestResponse,
    RefactorRequest,
    RefactorResponse,
    ProjectIndexRequest,
    ProjectIndexResponse,
    ProjectStatsResponse,
    ProjectTreeResponse,
)
from app.services.chat import ChatService
from app.services.doc_generator import DocGeneratorService
from app.services.test_generator import TestGeneratorService
from app.services.refactor_engine import RefactorEngineService
from app.services.project_service import ProjectService
from app.core.config import get_settings

router = APIRouter()
chat_service = ChatService()
doc_service = DocGeneratorService()
test_service = TestGeneratorService()
refactor_service = RefactorEngineService()
project_service = ProjectService(get_settings().db_path)


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/", response_class=HTMLResponse)
def ui() -> str:
    ui_path = Path(__file__).resolve().parents[1] / "ui" / "index.html"
    return ui_path.read_text(encoding="utf-8")


@router.post("/projects/index", response_model=ProjectIndexResponse)
def index_project(request: ProjectIndexRequest) -> ProjectIndexResponse:
    return project_service.scan_and_index(request.root_path)


@router.get("/projects/{project_id}/stats", response_model=ProjectStatsResponse)
def project_stats(project_id: int) -> ProjectStatsResponse:
    stats = project_service.get_stats(project_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Project not found or not indexed")
    return stats


@router.get("/projects/{project_id}/tree", response_model=ProjectTreeResponse)
def project_tree(project_id: int, max_depth: int = 6, max_entries: int = 500) -> ProjectTreeResponse:
    tree = project_service.get_tree(project_id, max_depth=max_depth, max_entries=max_entries)
    if not tree:
        raise HTTPException(status_code=404, detail="Project not found or not indexed")
    return ProjectTreeResponse(project_id=project_id, tree=tree)


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return chat_service.chat(
        project_id=request.project_id,
        query=request.query,
        max_chunks=request.max_chunks,
    )


@router.post("/docs/generate", response_model=DocResponse)
def generate_docs(request: DocRequest) -> DocResponse:
    return doc_service.generate(
        project_id=request.project_id,
        focus=request.focus,
        max_chunks=request.max_chunks,
    )


@router.post("/tests/generate", response_model=TestResponse)
def generate_tests(request: TestRequest) -> TestResponse:
    return test_service.generate(
        project_id=request.project_id,
        target=request.target,
        max_chunks=request.max_chunks,
        framework=request.framework,
    )


@router.post("/refactor/suggest", response_model=RefactorResponse)
def suggest_refactor(request: RefactorRequest) -> RefactorResponse:
    return refactor_service.suggest(
        project_id=request.project_id,
        target=request.target,
        max_chunks=request.max_chunks,
        style=request.style,
    )
