from __future__ import annotations


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as file_obj:
        return file_obj.read()
