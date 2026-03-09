from app.indexers.chunker import chunk_text


def test_chunk_text_basic():
    text = "\n".join([f"line {i}" for i in range(1, 51)])
    chunks = chunk_text(text, max_chars=120, overlap=20)
    assert len(chunks) > 1
    assert chunks[0].start_line == 1
    assert chunks[-1].end_line == 50
