from __future__ import annotations

import logging
import re

from app.core.config import get_settings
from app.repositories.search_repository import SearchRepository


_FILE_SUFFIX_PATTERN = re.compile(r"([\w\-/\\.]+\.[a-zA-Z0-9]+)")


class SearchService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.repo = SearchRepository(self.settings.db_path)

    def _detect_file_suffix(self, query: str) -> str | None:
        match = _FILE_SUFFIX_PATTERN.search(query)
        if not match:
            return None
        candidate = match.group(1)
        return candidate.replace("\\", "/")

    def _sanitize_fts_query(self, query: str) -> str:
        cleaned = re.sub(r"[^\w]+", " ", query, flags=re.UNICODE).strip()
        if not cleaned:
            return ""
        tokens = cleaned.split()
        return " ".join(f"\"{token}\"" for token in tokens)

    def search(self, project_id: int, query: str, limit: int = 8) -> list[dict]:
        raw_query = query.strip()
        if not raw_query:
            return []

        file_suffix = self._detect_file_suffix(raw_query)
        if file_suffix:
            file_row = self.repo.find_file_by_suffix(project_id, file_suffix)
            if file_row:
                chunks = self.repo.get_file_chunks(file_row["id"])
                return [
                    {
                        "rel_path": file_row["rel_path"],
                        "start_line": chunk["start_line"],
                        "end_line": chunk["end_line"],
                        "content": chunk["content"],
                    }
                    for chunk in chunks
                ]

        sanitized = self._sanitize_fts_query(raw_query)
        if not sanitized:
            return []

        try:
            rows = self.repo.search_chunks(project_id, sanitized, limit)
        except Exception:
            return []
        return [
            {
                "rel_path": row["rel_path"],
                "start_line": row["start_line"],
                "end_line": row["end_line"],
                "content": row["content"],
            }
            for row in rows
        ]
