"""Small in-memory RAG pipeline using OpenAI embeddings."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import numpy as np
from openai import OpenAI


@dataclass
class Chunk:
    text: str
    source: str
    embedding: list[float]


def chunk_text(text: str, source: str, chunk_size: int = 900, overlap: int = 150) -> list[tuple[str, str]]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append((text[start:end], source))
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def embed_texts(client: OpenAI, texts: list[str], model: str) -> list[list[float]]:
    response = client.embeddings.create(model=model, input=texts)
    return [item.embedding for item in response.data]


class InMemoryVectorStore:
    def __init__(self):
        self.chunks: list[Chunk] = []

    def add_documents(self, client: OpenAI, documents: Iterable[tuple[str, str]], model: str) -> int:
        docs = list(documents)
        if not docs:
            return 0
        vectors = embed_texts(client, [text for text, _ in docs], model)
        self.chunks.extend(
            Chunk(text=text, source=source, embedding=vector)
            for (text, source), vector in zip(docs, vectors)
        )
        return len(docs)

    def search(self, client: OpenAI, query: str, model: str, top_k: int = 4) -> list[dict]:
        if not self.chunks:
            return []
        query_vector = np.array(embed_texts(client, [query], model)[0], dtype=float)
        matrix = np.array([c.embedding for c in self.chunks], dtype=float)
        denom = np.linalg.norm(matrix, axis=1) * np.linalg.norm(query_vector)
        scores = np.divide(matrix @ query_vector, denom, out=np.zeros(len(matrix)), where=denom != 0)
        indices = np.argsort(scores)[::-1][:top_k]
        return [
            {"text": self.chunks[i].text, "source": self.chunks[i].source, "score": float(scores[i])}
            for i in indices
        ]
