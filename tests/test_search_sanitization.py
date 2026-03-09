from app.services.search import SearchService


def test_sanitize_fts_query_strips_punctuation():
    service = SearchService()
    assert service._sanitize_fts_query("app/main.py") == '"app" "main" "py"'


def test_sanitize_fts_query_handles_operators_as_tokens():
    service = SearchService()
    assert service._sanitize_fts_query("foo OR bar") == '"foo" "OR" "bar"'


def test_sanitize_fts_query_returns_empty_on_symbols_only():
    service = SearchService()
    assert service._sanitize_fts_query("...///---") == ""
