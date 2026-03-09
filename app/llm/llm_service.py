from __future__ import annotations

import logging

from app.core.config import get_settings
from app.llm.ollama_client import OllamaClient, OllamaError


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = OllamaClient()
        self.logger = logging.getLogger(self.__class__.__name__)

    def _model_for_task(self, task: str) -> str:
        task = task.lower()
        if task in {"generate_tests", "refactor_code", "technical_analysis", "generate_docs"}:
            return self.settings.model_code
        if task in {"explain_code", "architecture_summary", "qa", "chat"}:
            return self.settings.model_reasoning
        return self.settings.model_reasoning

    def generate(self, task: str, prompt: str) -> str:
        model = self._model_for_task(task)
        response = self.client.generate(prompt=prompt, model=model, stream=False)
        if not isinstance(response, dict):
            raise OllamaError("Réponse Ollama invalide.", status_code=502)
        if "response" not in response:
            raise OllamaError("Réponse Ollama incomplète.", status_code=502)
        return response.get("response", "").strip()
