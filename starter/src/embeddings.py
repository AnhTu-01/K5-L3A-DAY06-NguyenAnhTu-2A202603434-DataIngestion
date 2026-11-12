"""Choose a real embedding provider (API or local) and implement this contract."""
from typing import Protocol


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text, in the same order."""
        ...

    def embed_query(self, question: str) -> list[float]:
        """Return a query vector compatible with the stored document vectors."""
        ...


class MyEmbedder:
    """TODO: implement a provider adapter; do not silently fall back to mock vectors."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        raise NotImplementedError("TODO: initialize real embedder and dimensions")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError("TODO: embed_documents")

    def embed_query(self, question: str) -> list[float]:
        raise NotImplementedError("TODO: embed_query")
