"""Embedding that qua OpenRouter (POST /api/v1/embeddings). Khong co fallback mock: loi la dung."""
import json
import os
import time
import urllib.error
import urllib.request
from typing import Protocol

URL = "https://openrouter.ai/api/v1/embeddings"


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, question: str) -> list[float]: ...


class MyEmbedder:
    """Cung model cho document va query, khong them prefix (model doi xung)."""

    def __init__(self, model_name: str, batch_size: int = 64) -> None:
        key = os.getenv("OPENROUTER_API_KEY")
        if not key:
            raise RuntimeError("Thieu OPENROUTER_API_KEY trong .env")
        self._key, self.model_name, self.batch_size = key, model_name, batch_size
        self.calls = 0
        self.tokens = 0
        self.cost = 0.0
        self.seconds = 0.0
        self.dimensions = len(self._embed(["dimension probe"])[0])

    def _embed(self, texts: list[str]) -> list[list[float]]:
        body = json.dumps({"model": self.model_name, "input": texts}).encode()
        req = urllib.request.Request(URL, data=body, headers={
            "Authorization": "Bearer " + self._key, "Content-Type": "application/json"})
        for attempt in range(4):
            t0 = time.time()
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    r = json.load(resp)
                break
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f"Embedding API loi HTTP {e.code}: {e.read()[:300]!r}") from e
            except urllib.error.URLError as e:
                if attempt < 3:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f"Khong goi duoc Embedding API: {e}") from e
        self.seconds += time.time() - t0
        self.calls += 1
        u = r.get("usage") or {}
        self.tokens += u.get("total_tokens") or u.get("prompt_tokens") or 0
        self.cost += float(u.get("cost") or 0.0)
        data = sorted(r["data"], key=lambda d: d["index"])
        if len(data) != len(texts):
            raise RuntimeError("So vector tra ve khong khop so van ban")
        return [d["embedding"] for d in data]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for i in range(0, len(texts), self.batch_size):
            out.extend(self._embed(texts[i:i + self.batch_size]))
        return out

    def embed_query(self, question: str) -> list[float]:
        return self._embed([question])[0]
