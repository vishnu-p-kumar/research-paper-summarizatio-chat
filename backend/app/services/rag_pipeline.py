from __future__ import annotations

import math
import re
import threading
import uuid
from typing import List, Tuple
from hashlib import sha256

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.config import CHUNK_OVERLAP, CHUNK_SIZE, DATABASE_URL


def _chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    if not text:
        return []
    chunk_size = max(200, int(chunk_size))
    chunk_overlap = max(0, min(int(chunk_overlap), chunk_size - 1))

    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + chunk_size)
        chunks.append(text[start:end].strip())
        if end == n:
            break
        start = max(0, end - chunk_overlap)
    return [c for c in chunks if c]


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for x, y in zip(a, b):
        dot += x * y
        norm_a += x * x
        norm_b += y * y
    denom = math.sqrt(norm_a) * math.sqrt(norm_b)
    return dot / denom if denom else 0.0


class HashingEmbedder:
    def __init__(self, dimensions: int = 768):
        self.dimensions = dimensions

    def encode_one(self, text: str) -> List[float]:
        vec = [0.0] * self.dimensions
        tokens = re.findall(r"[a-zA-Z0-9][a-zA-Z0-9_\-]{1,}", text.lower())
        for token in tokens:
            idx = int(sha256(token.encode("utf-8")).hexdigest()[:12], 16) % self.dimensions
            vec[idx] += 1.0
        norm = math.sqrt(sum(x * x for x in vec))
        if not norm:
            return vec
        return [x / norm for x in vec]

    def encode_many(self, texts: List[str]) -> List[List[float]]:
        return [self.encode_one(text) for text in texts]


class RagStore:
    """
    PostgreSQL-backed RAG store for deployment.

    Tables are created automatically. Embeddings are stored as JSONB so the app
    works on regular managed Postgres without requiring pgvector setup.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._embedder = HashingEmbedder()
        self._schema_ready = False

    def _connect(self):
        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL is required for the deployment database.")
        return psycopg.connect(DATABASE_URL, row_factory=dict_row)

    def _ensure_schema(self) -> None:
        if self._schema_ready:
            return
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id UUID PRIMARY KEY,
                    user_id UUID NOT NULL,
                    text TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS document_chunks (
                    doc_id UUID NOT NULL REFERENCES documents(doc_id) ON DELETE CASCADE,
                    chunk_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding JSONB NOT NULL,
                    PRIMARY KEY (doc_id, chunk_id)
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_document_chunks_doc_id
                ON document_chunks(doc_id)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_documents_user_id
                ON documents(user_id)
                """
            )
        self._schema_ready = True

    def create_doc(self, text: str, user_id: str) -> str:
        doc_id = str(uuid.uuid4())
        chunks = _chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        if not chunks:
            raise ValueError("No text content found to index.")

        vecs = self._embedder.encode_many(chunks)
        rows = [
            (doc_id, idx, chunk, Jsonb(vecs[idx]))
            for idx, chunk in enumerate(chunks)
        ]

        with self._lock:
            self._ensure_schema()
            with self._connect() as conn:
                with conn.transaction():
                    conn.execute(
                        "INSERT INTO documents (doc_id, user_id, text) VALUES (%s, %s, %s)",
                        (doc_id, user_id, text),
                    )
                    with conn.cursor() as cur:
                        cur.executemany(
                            """
                            INSERT INTO document_chunks (doc_id, chunk_id, content, embedding)
                            VALUES (%s, %s, %s, %s)
                            """,
                            rows,
                        )
        return doc_id

    def get_text(self, doc_id: str, user_id: str | None = None) -> str:
        self._ensure_schema()
        params = [doc_id]
        where = "doc_id = %s"
        if user_id:
            where += " AND user_id = %s"
            params.append(user_id)
        with self._connect() as conn:
            row = conn.execute(
                f"SELECT text FROM documents WHERE {where}",
                tuple(params),
            ).fetchone()
        if not row:
            raise KeyError("Unknown doc_id")
        return row["text"]

    def retrieve(
        self,
        doc_id: str,
        query: str,
        k: int = 5,
        user_id: str | None = None,
    ) -> List[Tuple[int, float, str]]:
        self._ensure_schema()
        q = self._embedder.encode_one(query)

        params = [doc_id]
        user_join = ""
        user_where = ""
        if user_id:
            user_join = "JOIN documents d ON d.doc_id = c.doc_id"
            user_where = "AND d.user_id = %s"
            params.append(user_id)

        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT c.chunk_id, c.content, c.embedding
                FROM document_chunks c
                {user_join}
                WHERE c.doc_id = %s
                {user_where}
                ORDER BY c.chunk_id
                """,
                tuple(params),
            ).fetchall()

        if not rows:
            raise KeyError("Unknown doc_id")

        ranked = [
            (int(row["chunk_id"]), _cosine_similarity(q, row["embedding"]), row["content"])
            for row in rows
        ]
        ranked.sort(key=lambda item: item[1], reverse=True)
        return ranked[: max(1, min(int(k), len(ranked)))]


rag_store = RagStore()
