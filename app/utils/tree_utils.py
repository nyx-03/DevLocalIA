from __future__ import annotations

from typing import Iterable, Set
from fnmatch import fnmatch


def _insert_path(tree: dict, parts: list[str]) -> None:
    node = tree
    for i, part in enumerate(parts):
        is_last = i == len(parts) - 1
        if is_last:
            node.setdefault(part, None)
        else:
            current = node.get(part)
            if current is None:
                current = {}
                node[part] = current
            node = current


def _is_env_file(name: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch(name, pattern) for pattern in patterns)


def build_tree(
    paths: Iterable[str],
    max_depth: int = 6,
    max_entries: int = 500,
    root_label: str = ".",
    ignore_dirs: Set[str] | None = None,
    ignore_file_patterns: Iterable[str] | None = None,
) -> str:
    tree: dict = {}
    ignore_dirs = ignore_dirs or set()
    ignore_file_patterns = ignore_file_patterns or []
    for path in paths:
        parts = [p for p in path.split("/") if p]
        if not parts:
            continue
        if any(part in ignore_dirs for part in parts):
            continue
        if _is_env_file(parts[-1], ignore_file_patterns):
            continue
        _insert_path(tree, parts)

    lines: list[str] = [root_label]
    entry_count = 0
    truncated = False

    def render(node: dict, prefix: str, depth: int) -> None:
        nonlocal entry_count, truncated
        if depth > max_depth:
            return
        items = sorted(node.items(), key=lambda item: (item[1] is None, item[0].lower()))
        for idx, (name, child) in enumerate(items):
            if entry_count >= max_entries:
                truncated = True
                return
            is_last = idx == len(items) - 1
            branch = "└── " if is_last else "├── "
            if child is None:
                lines.append(f"{prefix}{branch}{name}")
                entry_count += 1
            else:
                lines.append(f"{prefix}{branch}{name}/")
                entry_count += 1
                next_prefix = f"{prefix}{'    ' if is_last else '│   '}"
                render(child, next_prefix, depth + 1)

    render(tree, "", 1)

    if truncated:
        lines.append("… (troncature, trop d'éléments)")

    return "\n".join(lines)
