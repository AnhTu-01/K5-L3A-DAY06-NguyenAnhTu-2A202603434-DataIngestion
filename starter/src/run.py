"""Pipeline: nap A va B vao pgvector, chay top-3 cho A/B/C tren benchmark, luu trace va thong ke.

Chay tu thu muc starter/:  python -m src.run            (in ket qua dev)
                           python -m src.run --show-test (in ket qua test da luu)
"""
import argparse
import json
import os
import platform
import statistics
import time
from datetime import datetime
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from .chunking import by_paragraph, fixed_size
from .embeddings import MyEmbedder
from .evaluation import evaluate_query, summarize
from .ingestion import load_corpus
from .store import PgVectorStore

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"
# ten cau hinh -> (chien luoc luu trong DB, co ap dung filter khong)
RUNS = {"A": ("A", False), "B": ("B", False), "C": ("B", True)}


def ingest(name, chunk_fn, pages, emb, store):
    t0 = time.time()
    chunks = [c for p in pages for c in chunk_fn(p)]
    chunk_secs = time.time() - t0
    cost0, tok0, t1 = emb.cost, emb.tokens, time.time()
    vectors = emb.embed_documents([c.text for c in chunks])
    store.upsert(name, chunks, vectors)
    lens = [len(c.text) for c in chunks]
    return {"chunks": len(chunks), "chars_total": sum(lens), "len_mean": round(statistics.mean(lens), 1),
            "len_median": statistics.median(lens), "len_min": min(lens), "len_max": max(lens),
            "chunk_seconds": round(chunk_secs, 3), "embed_store_seconds": round(time.time() - t1, 2),
            "embed_tokens": emb.tokens - tok0, "embed_cost_usd": emb.cost - cost0,
            "rows_in_db": store.count(name)}


def print_table(summary, split):
    for s in ("A", "B", "C"):
        r = summary.get(s, {}).get(split)
        if r:
            extra = (f" | filter dung {r['filter_compliant']}/{r['filter_questions']}" if r["filter_questions"] else "")
            print(f"  {s} {split}: Hit@1 {r['hit1']}/{r['n']} | Evidence Hit@3 {r['hit3']}/{r['n']} | "
                  f"dung trang@1 {r['page_hit1']}/{r['n']}, @3 {r['page_hit3']}/{r['n']}{extra}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--show-test", action="store_true", help="in ket qua test da luu")
    args = ap.parse_args()
    if args.show_test:
        print_table(json.loads((RESULTS / "summary.json").read_text(encoding="utf-8")), "test")
        return

    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    pages = load_corpus(ROOT / "data" / "pages.jsonl")
    questions = json.loads((ROOT / "benchmark" / "questions.json").read_text(encoding="utf-8"))
    n_dev = sum(q["split"] == "dev" for q in questions)
    n_test = sum(q["split"] == "test" for q in questions)
    n_flt = [q for q in questions if q.get("filter")]
    assert len(pages) >= 30, "Can >= 30 trang noi dung"
    assert len(questions) >= 20 and n_dev >= 15 and n_test >= 5, "Can >= 20 cau, 15 dev, 5 test"
    assert len(n_flt) >= 3 and any(q["split"] == "test" for q in n_flt), "Can >= 3 cau filter, >= 1 o test"
    print(f"Corpus {len(pages)} trang | benchmark {len(questions)} cau (dev {n_dev}, test {n_test}, filter {len(n_flt)})")

    emb = MyEmbedder(os.getenv("EMBEDDING_MODEL"))
    store = PgVectorStore(os.getenv("DATABASE_URL"), emb.dimensions)
    store.create_schema()
    stats = {"A": ingest("A", lambda p: fixed_size(p, 500, 50), pages, emb, store),
             "B": ingest("B", lambda p: by_paragraph(p, 500), pages, emb, store)}
    for k, v in stats.items():
        print(f"Nap {k}: {v['chunks']} chunk | {v['embed_store_seconds']}s | ${v['embed_cost_usd']:.6f}")

    qvec = {q["id"]: emb.embed_query(q["question"]) for q in questions}
    traces = []
    for name, (db_strategy, use_filter) in RUNS.items():
        for q in questions:
            hits = store.search(db_strategy, qvec[q["id"]], 3, q["filter"] if use_filter and q.get("filter") else None)
            tr = evaluate_query(q, hits)
            tr.update({"strategy": name, "filter_applied": bool(use_filter and q.get("filter"))})
            traces.append(tr)

    RESULTS.mkdir(exist_ok=True)
    for name in RUNS:
        with open(RESULTS / f"traces_{name}.jsonl", "w", encoding="utf-8") as f:
            for t in traces:
                if t["strategy"] == name:
                    f.write(json.dumps(t, ensure_ascii=False) + "\n")
    summary = summarize(traces)
    (RESULTS / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    (RESULTS / "ingest_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
    with psycopg.connect(os.getenv("DATABASE_URL")) as c:
        pg = c.execute("SELECT version()").fetchone()[0]
        vec = c.execute("SELECT extversion FROM pg_extension WHERE extname='vector'").fetchone()[0]
    meta = {"run_at": datetime.now().astimezone().isoformat(), "python": platform.python_version(),
            "psycopg": psycopg.__version__, "postgres": pg, "pgvector": vec,
            "embedding_provider": "OpenRouter", "embedding_model": emb.model_name, "dimensions": emb.dimensions,
            "query_vs_document": "cung model, khong prefix", "search": "exact cosine (<=>), khong ANN index",
            "embedding_api_calls": emb.calls, "embedding_tokens_total": emb.tokens,
            "embedding_cost_usd_total": emb.cost,
            "configs": {"A": "fixed 500/overlap 50, khong filter", "B": "gom theo cau <=500 (gop manh <80), khong filter",
                        "C": "chunk cua B + loc metadata khi cau hoi co filter"}}
    (RESULTS / "run_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nKET QUA DEV (test da luu vao results/, xem bang --show-test sau khi chot tieu chi):")
    print_table(summary, "dev")
    print(f"\nTong chi phi embedding: ${emb.cost:.6f} | tokens: {emb.tokens}")


if __name__ == "__main__":
    main()
