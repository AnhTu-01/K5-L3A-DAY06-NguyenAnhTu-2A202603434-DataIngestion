"""In top-3 cua 5 cau test audit (q04,q09,q13,q16,q20) cho A, B, C kem kiem tra metadata tu dong."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "starter"))
from src.ingestion import load_corpus  # noqa: E402

AUDIT = ["q04", "q09", "q13", "q16", "q20"]
pages = {p.page: p for p in load_corpus(ROOT / "data" / "pages.jsonl")}
tr = {s: {t["id"]: t for t in map(json.loads, open(ROOT / "results" / f"traces_{s}.jsonl", encoding="utf-8"))} for s in "ABC"}

def meta_check(h):
    p = pages.get(h["page"])
    on_page = bool(p) and h["text"] in p.text
    same_md = bool(p) and all(h["metadata"].get(k) == p.metadata[k] for k in ("chapter", "section"))
    return f"text_tren_trang={on_page} chapter/section_khop={same_md}"

for qid in AUDIT:
    q = tr["B"][qid]
    print(f"\n######## {qid} ({q['type']}) {q['question']} | filter={q['filter']} | gold trang {q['gold_page']}")
    print(f"   evidence gold: {q['evidence_quote'][:200]}")
    for s in "ABC":
        t = tr[s][qid]
        if s == "C" and [h["chunk_id"] for h in t["top3"]] == [h["chunk_id"] for h in tr["B"][qid]["top3"]]:
            print("  -- C: top-3 giong het B (khong filter hoac filter khong doi ket qua)")
            continue
        print(f"  -- {s} | hit1={t['hit1']} hit3={t['hit3']} | filter_applied={t['filter_applied']} | tuan_thu_filter={t['filter_compliant']}")
        for h in t["top3"]:
            md = h["metadata"]
            print(f"     #{h['rank']} {h['score']:.3f} p{h['page']} ch{md['chapter']} [{md['section']}] evidence={h['evidence_hit']} | {meta_check(h)}")
            print(f"        {h['text'][:380]}")
