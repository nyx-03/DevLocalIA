import sqlite3

from app.services.search import SearchService


def test_search_returns_empty_on_blank_query():
    service = SearchService()
    assert service.search(1, "   ") == []


def test_search_handles_fts_error(monkeypatch):
    service = SearchService()

    def raise_fts(*args, **kwargs):
        raise sqlite3.OperationalError("fts5 error")

    monkeypatch.setattr(service.repo, "find_file_by_suffix", lambda *args, **kwargs: None)
    monkeypatch.setattr(service.repo, "search_chunks", raise_fts)

    assert service.search(1, "app/main.py") == []
