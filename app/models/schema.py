from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


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
    project_id: int = Field(ge=1)
    query: str = Field(min_length=1, max_length=4000)
    max_chunks: int = Field(default=8, ge=1, le=24)

    @field_validator("query")
    @classmethod
    def _strip_query(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("query cannot be empty")
        return cleaned


class ChatResponse(BaseModel):
    answer: str
    used_chunks: list[ChunkHit]


class DocRequest(BaseModel):
    project_id: int = Field(ge=1)
    focus: str | None = Field(default=None, max_length=2000)
    max_chunks: int = Field(default=12, ge=1, le=24)


class DocResponse(BaseModel):
    markdown: str


class TestRequest(BaseModel):
    __test__ = False
    project_id: int = Field(ge=1)
    target: str = Field(min_length=1, max_length=4000)
    max_chunks: int = Field(default=10, ge=1, le=24)
    framework: Literal["pytest"] = "pytest"

    @field_validator("target")
    @classmethod
    def _strip_target(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("target cannot be empty")
        return cleaned


class TestResponse(BaseModel):
    __test__ = False
    test_code: str


class RefactorRequest(BaseModel):
    project_id: int = Field(ge=1)
    target: str = Field(min_length=1, max_length=4000)
    max_chunks: int = Field(default=10, ge=1, le=24)
    style: Literal["safe", "moderate", "aggressive"] = "safe"

    @field_validator("target")
    @classmethod
    def _strip_refactor_target(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("target cannot be empty")
        return cleaned


class RefactorResponse(BaseModel):
    refactor: str


class ProjectIndexRequest(BaseModel):
    root_path: str = Field(min_length=1, max_length=500)

    @field_validator("root_path")
    @classmethod
    def _strip_root_path(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("root_path cannot be empty")
        if "\x00" in cleaned:
            raise ValueError("root_path contains null byte")
        return cleaned


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
