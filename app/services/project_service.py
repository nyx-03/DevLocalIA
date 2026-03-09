from __future__ import annotations

import logging

from app.models.schema import ProjectIndexResponse, ProjectStatsResponse
from app.repositories.project_repository import ProjectRepository
from app.services.indexer import IndexerService
from app.services.scanner import ScannerService
from app.utils.tree_utils import build_tree
from app.core.config import get_settings


class ProjectService:
    def __init__(self, db_path: str) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.scanner = ScannerService()
        self.indexer = IndexerService()
        self.repo = ProjectRepository(db_path)

    def scan_and_index(self, root_path: str) -> ProjectIndexResponse:
        scan = self.scanner.scan(root_path)
        index_result = self.indexer.index_scan(scan)
        return ProjectIndexResponse(
            project_id=index_result.project_id,
            project_name=scan.project_name,
            root_path=scan.root_path,
            file_count=index_result.file_count,
            chunk_count=index_result.chunk_count,
            skipped_count=len(scan.skipped),
        )

    def get_stats(self, project_id: int) -> ProjectStatsResponse | None:
        project = self.repo.get_project(project_id)
        stats = self.repo.get_stats(project_id)
        if not project or not stats:
            return None

        languages = stats.get("languages_json")
        try:
            import json

            languages = json.loads(languages) if languages else {}
        except Exception:
            languages = {}

        return ProjectStatsResponse(
            project_id=project["id"],
            project_name=project["name"],
            root_path=project["root_path"],
            file_count=stats["file_count"],
            chunk_count=stats["chunk_count"],
            total_size=stats["total_size"],
            languages=languages,
        )

    def get_tree(self, project_id: int, max_depth: int = 6, max_entries: int = 500) -> str | None:
        project = self.repo.get_project(project_id)
        if not project:
            return None
        paths = self.repo.list_file_paths(project_id)
        settings = get_settings()
        ignore_dirs = set(settings.ignore_dir_set)
        ignore_dirs.update({".venv", ".direnv"})
        ignore_patterns = [".env", ".env.*", "*.env"]
        return build_tree(
            paths,
            max_depth=max_depth,
            max_entries=max_entries,
            root_label=project["name"],
            ignore_dirs=ignore_dirs,
            ignore_file_patterns=ignore_patterns,
        )
