"""TODO: store and search vectors using PostgreSQL + pgvector."""
from typing import Any
from .models import Chunk


class PgVectorStore:
    def __init__(self, database_url: str, dimensions: int) -> None:
        """TODO: retain connection settings; validate model dimensions."""
        raise NotImplementedError("TODO: initialize store")

    def create_schema(self) -> None:
        """TODO: create table with vector column and source/page/filter metadata."""
        raise NotImplementedError("TODO: create_schema")

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """TODO: validate lengths/dimensions and write stable IDs without duplicates.

        When re-ingesting changed source documents, remove obsolete chunks too.
        """
        raise NotImplementedError("TODO: upsert")

    def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """TODO: filter permitted metadata in SQL, rank by cosine distance, return top-k.

        Return chunk ID, text, score and metadata. Parameterize user-supplied values.
        """
        raise NotImplementedError("TODO: search")
