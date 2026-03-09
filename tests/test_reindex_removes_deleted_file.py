import os

from app.core.config import get_settings
from app.repositories.project_repository import ProjectRepository
from app.services.indexer import IndexerService
from app.services.scanner import ScannerService


def test_reindex_removes_deleted_file(tmp_path, monkeypatch):
    db_path = tmp_path / "index.db"
    monkeypatch.setenv("DB_PATH", str(db_path))
    get_settings.cache_clear()

    project_dir = tmp_path / "project"
    project_dir.mkdir()

    file_a = project_dir / "a.py"
    file_b = project_dir / "b.py"
    file_a.write_text("print('a')\n")
    file_b.write_text("print('b')\n")

    scanner = ScannerService()
    indexer = IndexerService()

    scan = scanner.scan(str(project_dir))
    result = indexer.index_scan(scan)

    repo = ProjectRepository(str(db_path))
    paths = set(repo.list_file_paths(result.project_id))
    assert "a.py" in paths
    assert "b.py" in paths

    os.remove(file_b)

    scan2 = scanner.scan(str(project_dir))
    result2 = indexer.index_scan(scan2)
    paths2 = set(repo.list_file_paths(result2.project_id))

    assert "a.py" in paths2
    assert "b.py" not in paths2
