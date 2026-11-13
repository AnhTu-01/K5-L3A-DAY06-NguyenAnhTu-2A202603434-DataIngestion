"""PostgreSQL + pgvector: luu chunk, tim top-k theo cosine (exact, khong ANN), loc metadata trong SQL."""
import json
from typing import Any

import psycopg

from .models import Chunk

# cot duoc phep loc (whitelist, tranh chen SQL tu ten truong)
FILTER_COLUMNS = {"chapter": "chapter", "section": "section", "page": "page", "document_id": "document_id"}


def _vec(v: list[float]) -> str:
    return "[" + ",".join(repr(float(x)) for x in v) + "]"


class PgVectorStore:
    def __init__(self, database_url: str, dimensions: int) -> None:
        if not database_url:
            raise RuntimeError("Thieu DATABASE_URL trong .env")
        self.url, self.dimensions = database_url, dimensions

    def _conn(self) -> psycopg.Connection:
        return psycopg.connect(self.url)

    def create_schema(self) -> None:
        with self._conn() as c:
            c.execute("CREATE EXTENSION IF NOT EXISTS vector")
            c.execute(f"""
                CREATE TABLE IF NOT EXISTS chunks (
                    strategy text NOT NULL, chunk_id text NOT NULL,
                    document_id text NOT NULL, source text NOT NULL, page int NOT NULL,
                    chapter int, section text, text text NOT NULL, metadata jsonb NOT NULL,
                    embedding vector({self.dimensions}) NOT NULL,
                    PRIMARY KEY (strategy, chunk_id))""")
            c.execute("CREATE INDEX IF NOT EXISTS chunks_filter_idx ON chunks (strategy, chapter, section)")

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("So chunk khac so vector")
        if any(len(v) != self.dimensions for v in vectors):
            raise ValueError(f"Vector sai so chieu, can {self.dimensions}")
        ids = [c.chunk_id for c in chunks]
        with self._conn() as c:
            # xoa chunk cu khong con trong lan nap nay -> nap lai khong nhan doi
            c.execute("DELETE FROM chunks WHERE strategy = %s AND chunk_id <> ALL(%s)", (strategy, ids))
            with c.cursor() as cur:
                cur.executemany(
                    """INSERT INTO chunks (strategy, chunk_id, document_id, source, page, chapter, section,
                                           text, metadata, embedding)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::vector)
                       ON CONFLICT (strategy, chunk_id) DO UPDATE SET
                         text = EXCLUDED.text, metadata = EXCLUDED.metadata, embedding = EXCLUDED.embedding,
                         chapter = EXCLUDED.chapter, section = EXCLUDED.section, page = EXCLUDED.page""",
                    [(strategy, ch.chunk_id, ch.document_id, ch.source, ch.page, ch.metadata.get("chapter"),
                      ch.metadata.get("section"), ch.text, json.dumps(ch.metadata, ensure_ascii=False), _vec(v))
                     for ch, v in zip(chunks, vectors)])

    def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        where, params = ["strategy = %s"], [strategy]
        for k, v in (filters or {}).items():
            if k not in FILTER_COLUMNS:
                raise ValueError(f"Truong loc khong duoc phep: {k}")
            where.append(f"{FILTER_COLUMNS[k]} = %s")
            params.append(v)
        qv = _vec(query_vector)
        sql = (f"SELECT chunk_id, document_id, source, page, text, metadata, "
               f"1 - (embedding <=> %s::vector) AS score FROM chunks WHERE {' AND '.join(where)} "
               f"ORDER BY embedding <=> %s::vector LIMIT %s")
        with self._conn() as c:
            rows = c.execute(sql, [qv, *params, qv, top_k]).fetchall()
        return [{"chunk_id": r[0], "document_id": r[1], "source": r[2], "page": r[3], "text": r[4],
                 "metadata": r[5], "score": float(r[6])} for r in rows]

    def count(self, strategy: str) -> int:
        with self._conn() as c:
            return c.execute("SELECT count(*) FROM chunks WHERE strategy = %s", (strategy,)).fetchone()[0]

    def delete_strategy(self, strategy: str) -> None:
        with self._conn() as c:
            c.execute("DELETE FROM chunks WHERE strategy = %s", (strategy,))
