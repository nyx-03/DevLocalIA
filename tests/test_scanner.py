from app.services.scanner import ScannerService


def test_scanner_skips_binary(tmp_path):
    text_file = tmp_path / "hello.py"
    text_file.write_text("print('hello')\n")

    binary_file = tmp_path / "image.bin"
    binary_file.write_bytes(b"\x00\x01\x02\x03")

    scanner = ScannerService()
    result = scanner.scan(str(tmp_path))

    rel_paths = {meta.rel_path for meta in result.files}
    skipped = {item.path: item.reason for item in result.skipped}

    assert "hello.py" in rel_paths
    assert "image.bin" in skipped
    assert skipped["image.bin"] == "binary"
