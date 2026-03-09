from __future__ import annotations

import logging
from collections import Counter

from app.core.config import get_settings
from app.indexers.chunker import chunk_text
from app.models.schema import IndexResult, ProjectScanResult
from app.repositories.index_repository import IndexRepository
from app.utils.text_utils import read_text_file


class IndexerService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.repo = IndexRepository(self.settings.db_path)

    def index_scan(self, scan_result: ProjectScanResult) -> IndexResult:
        project_id = self.repo.upsert_project(
            name=scan_result.project_name,
            root_path=scan_result.root_path,
        )

        total_chunks = 0
        language_counts: Counter[str] = Counter()
        total_size = 0

        for file_meta in scan_result.files:
            total_size += file_meta.size
            if file_meta.language:
                language_counts[file_meta.language] += 1

            file_id = self.repo.upsert_file(project_id, file_meta)
            content = read_text_file(file_meta.path)
            chunks = chunk_text(
                content,
                max_chars=self.settings.chunk_size,
                overlap=self.settings.chunk_overlap,
            )
            total_chunks += self.repo.replace_chunks(
                project_id=project_id,
                file_id=file_id,
                rel_path=file_meta.rel_path,
                chunks=chunks,
            )

        self.repo.upsert_stats(
            project_id=project_id,
            file_count=len(scan_result.files),
            chunk_count=total_chunks,
            total_size=total_size,
            language_counts=dict(language_counts),
        )

        self.logger.info(
            "Index complete: %s files, %s chunks", len(scan_result.files), total_chunks
        )
        return IndexResult(
            project_id=project_id,
            file_count=len(scan_result.files),
            chunk_count=total_chunks,
        )
