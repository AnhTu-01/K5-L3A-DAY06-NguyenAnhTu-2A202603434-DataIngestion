"""Chon 10 vi tri audit coherence theo quy tac co dinh va in chunk A va B tai cung vi tri."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "starter"))
from src.chunking import by_paragraph, fixed_size  # noqa: E402
from src.ingestion import load_corpus  # noqa: E402

pages = sorted(load_corpus(ROOT / "data" / "pages.jsonl"), key=lambda p: p.page)
picked = [pages[i] for i in range(0, len(pages), 15)][:10]   # thu tu 1,16,31,...,136
sample = []
for n, p in enumerate(picked, 1):
    pos = len(p.text) // 2
    row = {"pos_id": n, "page": p.page, "char_pos": pos, "section": p.metadata["section"]}
    for s, chunks in (("A", fixed_size(p, 500, 50)), ("B", by_paragraph(p, 500))):
        c = next(c for c in chunks if c.metadata["char_start"] <= pos < c.metadata["char_end"])
        row[s] = {"chunk_id": c.chunk_id, "text": c.text}
    sample.append(row)
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "audit_coherence_sample.json").write_text(json.dumps(sample, ensure_ascii=False, indent=1), encoding="utf-8")
print("Thang: 0 = bi cat giua y/thieu chu the lam khong hieu; 1 = hieu mot phan, thieu ngu canh; 2 = tu hieu duoc, tron y\n")
for r in sample:
    print(f"##### VI TRI {r['pos_id']} | trang {r['page']} | {r['section']}")
    for s in "AB":
        print(f"--- {s} [{r[s]['chunk_id']}] ({len(r[s]['text'])} ky tu)\n{r[s]['text']}\n")
