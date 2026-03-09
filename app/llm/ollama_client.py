from __future__ import annotations

import logging
from typing import Any

import requests

from app.core.config import get_settings


class OllamaClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate(self, prompt: str, model: str, stream: bool = False) -> dict[str, Any]:
        url = f"{self.settings.ollama_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
        }
        self.logger.debug("Sending request to Ollama model=%s", model)
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()
