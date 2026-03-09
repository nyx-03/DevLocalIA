from __future__ import annotations

import os
import re
from typing import Iterable, Tuple


_SIZE_PATTERN = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([kKmMgG]?[bB])?\s*$")


def parse_size_to_bytes(value: str) -> int:
    match = _SIZE_PATTERN.match(value)
    if not match:
        raise ValueError(f"Invalid size format: {value}")

    number = float(match.group(1))
    unit = (match.group(2) or "b").lower()

    multiplier = 1
    if unit in {"kb", "k"}:
        multiplier = 1024
    elif unit in {"mb", "m"}:
        multiplier = 1024 ** 2
    elif unit in {"gb", "g"}:
        multiplier = 1024 ** 3

    return int(number * multiplier)


def is_binary_file(path: str, sample_size: int = 4096) -> bool:
    try:
        with open(path, "rb") as file_obj:
            chunk = file_obj.read(sample_size)
    except OSError:
        return True

    if b"\x00" in chunk:
        return True

    if not chunk:
        return False

    text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)))
    non_text = chunk.translate(None, text_chars)
    return float(len(non_text)) / float(len(chunk)) > 0.30


def iter_project_files(root_path: str, ignore_dirs: set[str]) -> Iterable[Tuple[str, str]]:
    for current_root, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        for filename in filenames:
            full_path = os.path.join(current_root, filename)
            rel_path = os.path.relpath(full_path, root_path)
            yield full_path, rel_path
