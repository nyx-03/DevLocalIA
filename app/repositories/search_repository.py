from __future__ import annotations

from typing import Iterable

from app.repositories.db import get_connection


class SearchRepository:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def search_chunks(self, project_id: int, query: str, limit: int) -> list[dict]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                "SELECT chunks.id AS chunk_id, chunks.content, chunks.start_line, chunks.end_line, "
                "files.rel_path "
                "FROM chunks_fts "
                "JOIN chunks ON chunks.id = chunks_fts.chunk_id "
                "JOIN files ON files.id = chunks.file_id "
                "WHERE chunks_fts MATCH ? AND chunks_fts.project_id = ? "
                "ORDER BY bm25(chunks_fts) "
                "LIMIT ?",
                (query, project_id, limit),
            ).fetchall()
            return [dict(row) for row in rows]

    def find_file_by_suffix(self, project_id: int, suffix: str) -> dict | None:
        pattern = f"%{suffix}"
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT id, rel_path FROM files WHERE project_id = ? AND rel_path LIKE ? "
                "ORDER BY length(rel_path) ASC LIMIT 1",
                (project_id, pattern),
            ).fetchone()
            return dict(row) if row else None

    def get_file_chunks(self, file_id: int) -> list[dict]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                "SELECT chunk_index, content, start_line, end_line "
                "FROM chunks WHERE file_id = ? ORDER BY chunk_index ASC",
                (file_id,),
            ).fetchall()
            return [dict(row) for row in rows]
