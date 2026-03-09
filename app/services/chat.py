from __future__ import annotations

import logging

from app.llm.llm_service import LLMService
from app.models.schema import ChatResponse, ChunkHit
from app.services.search import SearchService
from app.services.project_service import ProjectService
from app.core.config import get_settings
from app.llm.prompts import chat_prompt, join_context_blocks


class ChatService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.search = SearchService()
        self.llm = LLMService()
        self.project_service = ProjectService(get_settings().db_path)

    def chat(self, project_id: int, query: str, max_chunks: int = 8) -> ChatResponse:
        lowered = query.lower()
        if any(
            keyword in lowered
            for keyword in (
                "arborescence",
                "structure",
                "dossiers",
                "folders",
                "tree",
            )
        ):
            tree = self.project_service.get_tree(project_id)
            if tree:
                answer = f"Voici l'arborescence du projet :\n\n{tree}"
                return ChatResponse(answer=answer, used_chunks=[])
        hits = self.search.search(project_id=project_id, query=query, limit=max_chunks)
        context_blocks = []
        used_chunks: list[ChunkHit] = []

        for hit in hits:
            context_blocks.append(
                f"Fichier: {hit['rel_path']} (lignes {hit['start_line']}-{hit['end_line']})\n"
                f"{hit['content']}"
            )
            used_chunks.append(
                ChunkHit(
                    rel_path=hit["rel_path"],
                    start_line=hit["start_line"],
                    end_line=hit["end_line"],
                    content=hit["content"],
                )
            )

        context_text = join_context_blocks(context_blocks)
        prompt = chat_prompt(query, context_text)

        answer = self.llm.generate(task="chat", prompt=prompt)
        return ChatResponse(answer=answer, used_chunks=used_chunks)
