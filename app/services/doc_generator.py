from __future__ import annotations

import json
import logging

from app.core.config import get_settings
from app.llm.llm_service import LLMService
from app.models.schema import DocResponse
from app.repositories.project_repository import ProjectRepository
from app.services.search import SearchService
from app.llm.prompts import doc_prompt, join_context_blocks


class DocGeneratorService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.settings = get_settings()
        self.repo = ProjectRepository(self.settings.db_path)
        self.search = SearchService()
        self.llm = LLMService()

    def generate(self, project_id: int, focus: str | None = None, max_chunks: int = 12) -> DocResponse:
        stats = self.repo.get_stats(project_id)
        file_rows = self.repo.list_files(project_id)

        file_list = "\n".join(
            f"- {row['rel_path']} ({row.get('language') or 'unknown'}, {row['size']} bytes)"
            for row in file_rows
        )

        base_query = focus or "architecture overview entrypoint module"
        hits = self.search.search(project_id=project_id, query=base_query, limit=max_chunks)
        context_blocks = []
        for hit in hits:
            context_blocks.append(
                f"Fichier: {hit['rel_path']} (lignes {hit['start_line']}-{hit['end_line']})\n"
                f"{hit['content']}"
            )

        context_text = join_context_blocks(context_blocks)

        stats_text = json.dumps(stats, indent=2, ensure_ascii=False) if stats else "{}"

        prompt = doc_prompt(stats_text, file_list, context_text)

        markdown = self.llm.generate(task="generate_docs", prompt=prompt)
        return DocResponse(markdown=markdown)
