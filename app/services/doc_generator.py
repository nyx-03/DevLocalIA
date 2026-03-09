from __future__ import annotations

import json
import logging

from app.core.config import get_settings
from app.llm.llm_service import LLMService
from app.models.schema import DocResponse
from app.repositories.project_repository import ProjectRepository
from app.services.search import SearchService


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

        context_text = "\n\n---\n\n".join(context_blocks) if context_blocks else "(aucun contexte trouvé)"

        stats_text = json.dumps(stats, indent=2, ensure_ascii=False) if stats else "{}"

        prompt = (
            "Tu es un assistant IA local pour développeurs. Produis une documentation technique complète en Markdown.\n"
            "La documentation doit inclure :\n"
            "1) Un README technique (installation, lancement, structure, conventions).\n"
            "2) Une section d'architecture (modules principaux, flux).\n"
            "3) Une section par module/fichier important (responsabilité, points clés).\n"
            "4) Points d'amélioration et limites connues.\n\n"
            "Contexte projet (stats JSON) :\n"
            f"{stats_text}\n\n"
            "Liste des fichiers :\n"
            f"{file_list}\n\n"
            "Extraits de code :\n"
            f"{context_text}\n\n"
            "Réponds uniquement en Markdown, sans bloc de code pour le markdown complet."
        )

        markdown = self.llm.generate(task="generate_docs", prompt=prompt)
        return DocResponse(markdown=markdown)
