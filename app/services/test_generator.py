from __future__ import annotations

import logging

from app.llm.llm_service import LLMService
from app.models.schema import TestResponse
from app.services.search import SearchService


class TestGeneratorService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.search = SearchService()
        self.llm = LLMService()

    def generate(
        self,
        project_id: int,
        target: str,
        max_chunks: int = 10,
        framework: str = "pytest",
    ) -> TestResponse:
        hits = self.search.search(project_id=project_id, query=target, limit=max_chunks)
        context_blocks = []

        for hit in hits:
            context_blocks.append(
                f"Fichier: {hit['rel_path']} (lignes {hit['start_line']}-{hit['end_line']})\n"
                f"{hit['content']}"
            )

        context_text = "\n\n---\n\n".join(context_blocks) if context_blocks else "(aucun contexte trouvé)"

        prompt = (
            "Tu es un assistant IA local pour développeurs. Génère des tests unitaires en Python.\n"
            "Contraintes :\n"
            "- Utiliser pytest.\n"
            "- Écrire du vrai code, pas de pseudocode.\n"
            "- Ajouter des mocks si nécessaire (pytest-mock ou unittest.mock).\n"
            "- Couvrir les cas normaux et au moins un cas d'erreur.\n"
            "- Répondre uniquement avec le fichier de tests en code Python.\n\n"
            f"Cible: {target}\n"
            f"Framework: {framework}\n\n"
            "Contexte code (extraits):\n"
            f"{context_text}\n"
        )

        test_code = self.llm.generate(task="generate_tests", prompt=prompt)
        return TestResponse(test_code=test_code)
