"""Chay thu end-to-end tren 2 trang: embed that, ghi pgvector, tim co/khong filter, nap lai khong nhan doi."""
import os
from pathlib import Path

from dotenv import load_dotenv

from src.chunking import by_paragraph
from src.embeddings import MyEmbedder
from src.ingestion import load_corpus
from src.store import PgVectorStore

load_dotenv(Path(".env"))
pages = [p for p in load_corpus(Path("../data/pages.jsonl")) if p.page in (258, 385)]
chunks = [c for p in pages for c in by_paragraph(p, 500)]
emb = MyEmbedder(os.getenv("EMBEDDING_MODEL"))
store = PgVectorStore(os.getenv("DATABASE_URL"), emb.dimensions)
store.create_schema()
store.upsert("smoke", chunks, emb.embed_documents([c.text for c in chunks]))
store.upsert("smoke", chunks, emb.embed_documents([c.text for c in chunks]))  # nap lai
print("model:", emb.model_name, "| chieu:", emb.dimensions, "| chunk:", len(chunks), "| trong DB:", store.count("smoke"))
qv = emb.embed_query("What does the Select operator return?")
for label, f in (("khong filter", None), ("filter chapter=6", {"chapter": 6})):
    print("\n--", label)
    for h in store.search("smoke", qv, 3, f):
        print(f"  {h['score']:.3f} | p{h['page']} ch{h['metadata']['chapter']} | {h['text'][:80]}")
print("\nchi phi:", emb.cost, "| tokens:", emb.tokens, "| goi API:", emb.calls)
store.delete_strategy("smoke")
