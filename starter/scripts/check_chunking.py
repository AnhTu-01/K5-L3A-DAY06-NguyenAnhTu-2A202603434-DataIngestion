"""Chay thu chunking A/B tren corpus; do so chunk, do dai va 'tran' Hit: evidence co nam tron trong 1 chunk khong."""
import json
import statistics
from pathlib import Path

from src.chunking import by_paragraph, fixed_size
from src.ingestion import load_corpus, normalize_text

pages = load_corpus(Path("../data/pages.jsonl"))
qs = json.load(open("../benchmark/questions.json", encoding="utf-8"))
print("so trang:", len(pages), "| tong ky tu:", sum(len(p.text) for p in pages))

strategies = {
    "A fixed 500/50": lambda p: fixed_size(p, 500, 50),
    "B sentence<=500": lambda p: by_paragraph(p, 500),
}
for name, fn in strategies.items():
    chunks = [c for p in pages for c in fn(p)]
    lens = [len(c.text) for c in chunks]
    by_page = {}
    for c in chunks:
        by_page.setdefault(c.page, []).append(c)
    whole = [q["id"] for q in qs
             if any(normalize_text(q["evidence_quote"]) in c.text for c in by_page.get(q["gold_page"], []))]
    split = [q["id"] for q in qs if q["id"] not in whole]
    print(f"\n[{name}] chunk: {len(chunks)} | dai TB {statistics.mean(lens):.0f} | trung vi {statistics.median(lens):.0f} | min {min(lens)} | max {max(lens)}")
    print(f"  evidence nam tron trong 1 chunk: {len(whole)}/{len(qs)} | bi cat: {split}")
p258 = next(p for p in pages if p.page == 258)
print("\nVi du trang 258, 2 chunk dau cua B:")
for c in by_paragraph(p258, 500)[:2]:
    print(" -", c.chunk_id, "|", c.metadata["section"], "|", c.text[:120], "...")
