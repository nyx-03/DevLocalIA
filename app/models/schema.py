from __future__ import annotations

from pydantic import BaseModel


class FileMeta(BaseModel):
    path: str
    rel_path: str
    size: int
    sha256: str
    language: str | None


class SkippedFile(BaseModel):
    path: str
    reason: str


class ProjectScanResult(BaseModel):
    root_path: str
    project_name: str
    files: list[FileMeta]
    skipped: list[SkippedFile]


class Chunk(BaseModel):
    index: int
    content: str
    start_line: int
    end_line: int


class IndexResult(BaseModel):
    project_id: int
    file_count: int
    chunk_count: int


class ChunkHit(BaseModel):
    rel_path: str
    start_line: int
    end_line: int
    content: str


class ChatRequest(BaseModel):
    project_id: int
    query: str
    max_chunks: int = 8


class ChatResponse(BaseModel):
    answer: str
    used_chunks: list[ChunkHit]


class DocRequest(BaseModel):
    project_id: int
    focus: str | None = None
    max_chunks: int = 12


class DocResponse(BaseModel):
    markdown: str


class TestRequest(BaseModel):
    project_id: int
    target: str
    max_chunks: int = 10
    framework: str = "pytest"


class TestResponse(BaseModel):
    test_code: str


class RefactorRequest(BaseModel):
    project_id: int
    target: str
    max_chunks: int = 10
    style: str = "safe"


class RefactorResponse(BaseModel):
    refactor: str


class ProjectIndexRequest(BaseModel):
    root_path: str


class ProjectIndexResponse(BaseModel):
    project_id: int
    project_name: str
    root_path: str
    file_count: int
    chunk_count: int
    skipped_count: int


class ProjectStatsResponse(BaseModel):
    project_id: int
    project_name: str
    root_path: str
    file_count: int
    chunk_count: int
    total_size: int
    languages: dict[str, int]


class ProjectTreeResponse(BaseModel):
    project_id: int
    tree: str
