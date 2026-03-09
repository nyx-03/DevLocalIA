from __future__ import annotations

import logging
import os

from app.core.config import get_settings
from app.models.schema import FileMeta, ProjectScanResult, SkippedFile
from app.utils.file_utils import is_binary_file, iter_project_files
from app.utils.hash_utils import sha256_file
from app.utils.language import detect_language


class ScannerService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.logger = logging.getLogger(self.__class__.__name__)

    def scan(self, root_path: str) -> ProjectScanResult:
        root_path = os.path.abspath(root_path)
        project_name = os.path.basename(root_path.rstrip(os.sep)) or root_path
        ignore_dirs = self.settings.ignore_dir_set
        max_size = self.settings.max_file_size_bytes

        files: list[FileMeta] = []
        skipped: list[SkippedFile] = []

        for full_path, rel_path in iter_project_files(root_path, ignore_dirs):
            try:
                size = os.path.getsize(full_path)
            except OSError as exc:
                skipped.append(SkippedFile(path=rel_path, reason=f"stat_error:{exc}"))
                continue

            if size > max_size:
                skipped.append(SkippedFile(path=rel_path, reason="too_large"))
                continue

            if is_binary_file(full_path):
                skipped.append(SkippedFile(path=rel_path, reason="binary"))
                continue

            try:
                file_hash = sha256_file(full_path)
            except OSError as exc:
                skipped.append(SkippedFile(path=rel_path, reason=f"hash_error:{exc}"))
                continue

            files.append(
                FileMeta(
                    path=full_path,
                    rel_path=rel_path,
                    size=size,
                    sha256=file_hash,
                    language=detect_language(full_path),
                )
            )

        self.logger.info("Scan complete: %s files, %s skipped", len(files), len(skipped))
        return ProjectScanResult(
            root_path=root_path,
            project_name=project_name,
            files=files,
            skipped=skipped,
        )
