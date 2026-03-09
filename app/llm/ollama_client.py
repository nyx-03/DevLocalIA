from __future__ import annotations

import logging
from typing import Any

import requests
from requests import Response
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout

from app.core.config import get_settings


class OllamaError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


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
        try:
            response: Response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()
        except Timeout as exc:
            raise OllamaError("Ollama ne répond pas (timeout).", status_code=504) from exc
        except ConnectionError as exc:
            raise OllamaError("Impossible de joindre Ollama.", status_code=503) from exc
        except HTTPError as exc:
            status = getattr(exc.response, "status_code", None)
            raise OllamaError("Erreur HTTP depuis Ollama.", status_code=status or 502) from exc
        except ValueError as exc:
            raise OllamaError("Réponse Ollama invalide.", status_code=502) from exc
        except RequestException as exc:
            raise OllamaError("Erreur réseau avec Ollama.", status_code=502) from exc
