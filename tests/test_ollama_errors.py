import requests

from app.llm.ollama_client import OllamaClient, OllamaError


def test_ollama_timeout(monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise requests.Timeout()

    monkeypatch.setattr(requests, "post", raise_timeout)
    client = OllamaClient()

    try:
        client.generate("hi", "model")
    except OllamaError as exc:
        assert "timeout" in str(exc).lower()
        assert exc.status_code == 504
    else:
        raise AssertionError("OllamaError was not raised")


def test_ollama_connection_error(monkeypatch):
    def raise_conn(*args, **kwargs):
        raise requests.ConnectionError()

    monkeypatch.setattr(requests, "post", raise_conn)
    client = OllamaClient()

    try:
        client.generate("hi", "model")
    except OllamaError as exc:
        assert exc.status_code == 503
    else:
        raise AssertionError("OllamaError was not raised")
