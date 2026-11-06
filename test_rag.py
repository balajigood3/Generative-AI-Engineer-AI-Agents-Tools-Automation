from app.rag import chunk_text


def test_chunk_text_returns_source_and_chunks():
    chunks = chunk_text("alpha " * 400, "sample.txt", chunk_size=100, overlap=10)
    assert len(chunks) > 1
    assert all(source == "sample.txt" for _, source in chunks)
    assert all(text for text, _ in chunks)
