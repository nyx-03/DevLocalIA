import sqlite3

import pytest

from app.core.config import get_settings
from app.repositories.db import get_connection
from app.services.indexer import IndexerService
from app.services.scanner import ScannerService


def test_indexer_transaction_rollback(tmp_path, monkeypatch):
    db_path = tmp_path / "index.db"
    monkeypatch.setenv("DB_PATH", str(db_path))
    get_settings.cache_clear()

    project_dir = tmp_path / "project"
    project_dir.mkdir()

    file_a = project_dir / "a.py"
    file_b = project_dir / "b.py"
    file_a.write_text("print('a')\n")
    file_b.write_text("print('b')\n")

    call_count = {"n": 0}

    def faulty_read(path: str) -> str:
        call_count["n"] += 1
        if call_count["n"] == 2:
            raise RuntimeError("boom")
        return "print('ok')"

    monkeypatch.setattr("app.services.indexer.read_text_file", faulty_read)

    scanner = ScannerService()
    indexer = IndexerService()
    scan = scanner.scan(str(project_dir))

    with pytest.raises(RuntimeError):
        indexer.index_scan(scan)

    with get_connection(str(db_path)) as conn:
        project_count = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        files_count = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        chunks_count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]

    assert project_count == 0
    assert files_count == 0
    assert chunks_count == 0
