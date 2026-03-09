from fastapi.testclient import TestClient

from app.main import app


def test_ui_assets_available():
    client = TestClient(app)
    assert client.get("/ui/styles.css").status_code == 200
    assert client.get("/ui/app.js").status_code == 200
