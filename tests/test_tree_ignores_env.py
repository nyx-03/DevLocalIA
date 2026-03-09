from app.core.config import get_settings
from app.services.indexer import IndexerService
from app.services.project_service import ProjectService
from app.services.scanner import ScannerService


def test_tree_ignores_env_files(tmp_path, monkeypatch):
    db_path = tmp_path / "index.db"
    monkeypatch.setenv("DB_PATH", str(db_path))
    get_settings.cache_clear()

    project_dir = tmp_path / "project"
    project_dir.mkdir()

    (project_dir / "app.py").write_text("print('ok')\n")
    (project_dir / ".env").write_text("SECRET=1\n")
    (project_dir / ".env.local").write_text("SECRET=2\n")

    scanner = ScannerService()
    indexer = IndexerService()
    scan = scanner.scan(str(project_dir))
    result = indexer.index_scan(scan)

    service = ProjectService(str(db_path))
    tree = service.get_tree(result.project_id)

    assert tree is not None
    assert "app.py" in tree
    assert ".env" not in tree
    assert ".env.local" not in tree
