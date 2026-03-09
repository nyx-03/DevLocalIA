from __future__ import annotations

import json
import sqlite3
from typing import Iterable

from app.models.schema import Chunk, FileMeta
from app.repositories.db import get_connection


_SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    root_path TEXT NOT NULL UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    rel_path TEXT NOT NULL,
    size INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    language TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, rel_path),
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    file_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    content,
    rel_path UNINDEXED,
    file_id UNINDEXED,
    project_id UNINDEXED,
    chunk_id UNINDEXED
);

CREATE TABLE IF NOT EXISTS stats (
    project_id INTEGER PRIMARY KEY,
    file_count INTEGER NOT NULL,
    chunk_count INTEGER NOT NULL,
    total_size INTEGER NOT NULL,
    languages_json TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
"""


class IndexRepository:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with get_connection(self.db_path) as conn:
            conn.executescript(_SCHEMA)

    def upsert_project(
        self,
        name: str,
        root_path: str,
        conn: sqlite3.Connection | None = None,
    ) -> int:
        if conn is None:
            with get_connection(self.db_path) as conn:
                return self.upsert_project(name, root_path, conn)

        conn.execute(
            "INSERT INTO projects(name, root_path) VALUES(?, ?) "
            "ON CONFLICT(root_path) DO UPDATE SET updated_at = CURRENT_TIMESTAMP",
            (name, root_path),
        )
        row = conn.execute(
            "SELECT id FROM projects WHERE root_path = ?",
            (root_path,),
        ).fetchone()
        return int(row["id"])

    def upsert_file(
        self,
        project_id: int,
        file_meta: FileMeta,
        conn: sqlite3.Connection | None = None,
    ) -> int:
        if conn is None:
            with get_connection(self.db_path) as conn:
                return self.upsert_file(project_id, file_meta, conn)

        conn.execute(
            "INSERT INTO files(project_id, rel_path, size, sha256, language) "
            "VALUES(?, ?, ?, ?, ?) "
            "ON CONFLICT(project_id, rel_path) DO UPDATE SET "
            "size = excluded.size, sha256 = excluded.sha256, language = excluded.language, "
            "updated_at = CURRENT_TIMESTAMP",
            (
                project_id,
                file_meta.rel_path,
                file_meta.size,
                file_meta.sha256,
                file_meta.language,
            ),
        )
        row = conn.execute(
            "SELECT id FROM files WHERE project_id = ? AND rel_path = ?",
            (project_id, file_meta.rel_path),
        ).fetchone()
        return int(row["id"])

    def replace_chunks(
        self,
        project_id: int,
        file_id: int,
        rel_path: str,
        chunks: Iterable[Chunk],
        conn: sqlite3.Connection | None = None,
    ) -> int:
        if conn is None:
            with get_connection(self.db_path) as conn:
                return self.replace_chunks(project_id, file_id, rel_path, chunks, conn)

        existing = conn.execute(
            "SELECT id FROM chunks WHERE file_id = ?",
            (file_id,),
        ).fetchall()
        for row in existing:
            conn.execute("DELETE FROM chunks_fts WHERE chunk_id = ?", (row["id"],))

        conn.execute("DELETE FROM chunks WHERE file_id = ?", (file_id,))

        chunk_count = 0
        for chunk in chunks:
            cursor = conn.execute(
                "INSERT INTO chunks(project_id, file_id, chunk_index, start_line, end_line, content) "
                "VALUES(?, ?, ?, ?, ?, ?)",
                (
                    project_id,
                    file_id,
                    chunk.index,
                    chunk.start_line,
                    chunk.end_line,
                    chunk.content,
                ),
            )
            chunk_id = cursor.lastrowid
            conn.execute(
                "INSERT INTO chunks_fts(content, rel_path, file_id, project_id, chunk_id) "
                "VALUES(?, ?, ?, ?, ?)",
                (
                    chunk.content,
                    rel_path,
                    file_id,
                    project_id,
                    chunk_id,
                ),
            )
            chunk_count += 1

        return chunk_count

    def delete_missing_files(
        self,
        project_id: int,
        keep_rel_paths: set[str],
        conn: sqlite3.Connection | None = None,
    ) -> int:
        if conn is None:
            with get_connection(self.db_path) as conn:
                return self.delete_missing_files(project_id, keep_rel_paths, conn)

        rows = conn.execute(
            "SELECT id, rel_path FROM files WHERE project_id = ?",
            (project_id,),
        ).fetchall()
        to_delete = [row["id"] for row in rows if row["rel_path"] not in keep_rel_paths]
        if not to_delete:
            return 0

        def chunks(items: list[int], size: int = 900) -> list[list[int]]:
            return [items[i : i + size] for i in range(0, len(items), size)]

        for batch in chunks(to_delete):
            placeholders = ",".join("?" for _ in batch)
            chunk_rows = conn.execute(
                f"SELECT id FROM chunks WHERE file_id IN ({placeholders})",
                batch,
            ).fetchall()
            chunk_ids = [row["id"] for row in chunk_rows]
            if chunk_ids:
                chunk_placeholders = ",".join("?" for _ in chunk_ids)
                conn.execute(
                    f"DELETE FROM chunks_fts WHERE chunk_id IN ({chunk_placeholders})",
                    chunk_ids,
                )
            conn.execute(
                f"DELETE FROM files WHERE id IN ({placeholders})",
                batch,
            )

        return len(to_delete)

    def upsert_stats(
        self,
        project_id: int,
        file_count: int,
        chunk_count: int,
        total_size: int,
        language_counts: dict[str, int],
        conn: sqlite3.Connection | None = None,
    ) -> None:
        languages_json = json.dumps(language_counts)
        if conn is None:
            with get_connection(self.db_path) as conn:
                return self.upsert_stats(
                    project_id,
                    file_count,
                    chunk_count,
                    total_size,
                    language_counts,
                    conn,
                )

        conn.execute(
            "INSERT INTO stats(project_id, file_count, chunk_count, total_size, languages_json) "
            "VALUES(?, ?, ?, ?, ?) "
            "ON CONFLICT(project_id) DO UPDATE SET "
            "file_count = excluded.file_count, "
            "chunk_count = excluded.chunk_count, "
            "total_size = excluded.total_size, "
            "languages_json = excluded.languages_json, "
            "updated_at = CURRENT_TIMESTAMP",
            (project_id, file_count, chunk_count, total_size, languages_json),
        )
