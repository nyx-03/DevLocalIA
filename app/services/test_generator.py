from __future__ import annotations

import logging

from app.llm.llm_service import LLMService
from app.models.schema import TestResponse
from app.services.search import SearchService
from app.llm.prompts import test_prompt, join_context_blocks


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

        context_text = join_context_blocks(context_blocks)
        prompt = test_prompt(target, framework, context_text)

        test_code = self.llm.generate(task="generate_tests", prompt=prompt)
        return TestResponse(test_code=test_code)
