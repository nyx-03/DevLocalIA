from __future__ import annotations

import hashlib


def sha256_file(path: str, chunk_size: int = 8192) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(chunk_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
