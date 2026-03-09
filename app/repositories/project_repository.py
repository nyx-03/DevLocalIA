from __future__ import annotations

from app.repositories.db import get_connection


class ProjectRepository:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def list_files(self, project_id: int) -> list[dict]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                "SELECT rel_path, language, size FROM files WHERE project_id = ? ORDER BY rel_path ASC",
                (project_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def list_file_paths(self, project_id: int) -> list[str]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                "SELECT rel_path FROM files WHERE project_id = ? ORDER BY rel_path ASC",
                (project_id,),
            ).fetchall()
            return [row["rel_path"] for row in rows]

    def get_stats(self, project_id: int) -> dict | None:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT file_count, chunk_count, total_size, languages_json "
                "FROM stats WHERE project_id = ?",
                (project_id,),
            ).fetchone()
            return dict(row) if row else None

    def get_project(self, project_id: int) -> dict | None:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT id, name, root_path FROM projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            return dict(row) if row else None
