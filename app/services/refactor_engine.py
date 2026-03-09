from __future__ import annotations

import logging

from app.llm.llm_service import LLMService
from app.models.schema import RefactorResponse
from app.services.search import SearchService
from app.llm.prompts import refactor_prompt, join_context_blocks


class RefactorEngineService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.search = SearchService()
        self.llm = LLMService()

    def suggest(
        self,
        project_id: int,
        target: str,
        max_chunks: int = 10,
        style: str = "safe",
    ) -> RefactorResponse:
        hits = self.search.search(project_id=project_id, query=target, limit=max_chunks)
        context_blocks = []

        for hit in hits:
            context_blocks.append(
                f"Fichier: {hit['rel_path']} (lignes {hit['start_line']}-{hit['end_line']})\n"
                f"{hit['content']}"
            )

        context_text = join_context_blocks(context_blocks)
        prompt = refactor_prompt(target, style, context_text)

        refactor_text = self.llm.generate(task="refactor_code", prompt=prompt)
        return RefactorResponse(refactor=refactor_text)
