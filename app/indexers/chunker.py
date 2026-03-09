from __future__ import annotations

from app.models.schema import Chunk


def chunk_text(text: str, max_chars: int, overlap: int) -> list[Chunk]:
    lines = text.splitlines()
    if not lines:
        return []

    chunks: list[Chunk] = []
    i = 0
    chunk_index = 0

    while i < len(lines):
        start_line = i + 1
        current_lines: list[str] = []
        current_len = 0

        while i < len(lines):
            line = lines[i]
            line_len = len(line) + 1
            if current_lines and current_len + line_len > max_chars:
                break
            current_lines.append(line)
            current_len += line_len
            i += 1

        end_line = start_line + len(current_lines) - 1
        content = "\n".join(current_lines)
        chunks.append(
            Chunk(
                index=chunk_index,
                content=content,
                start_line=start_line,
                end_line=end_line,
            )
        )
        chunk_index += 1

        if i >= len(lines):
            break

        if overlap > 0:
            overlap_len = 0
            overlap_lines = 0
            for line in reversed(current_lines):
                overlap_len += len(line) + 1
                overlap_lines += 1
                if overlap_len >= overlap:
                    break

            next_index = i - overlap_lines
            if next_index <= start_line - 1:
                next_index = start_line
            i = max(next_index, 0)

    return chunks
