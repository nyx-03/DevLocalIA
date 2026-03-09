from app.utils.file_utils import parse_size_to_bytes
from app.utils.language import detect_language


def test_parse_size_to_bytes():
    assert parse_size_to_bytes("1kb") == 1024
    assert parse_size_to_bytes("2mb") == 2 * 1024 * 1024
    assert parse_size_to_bytes("512") == 512


def test_detect_language():
    assert detect_language("main.py") == "python"
    assert detect_language("README.md") == "markdown"
    assert detect_language("unknown.xyz") is None
