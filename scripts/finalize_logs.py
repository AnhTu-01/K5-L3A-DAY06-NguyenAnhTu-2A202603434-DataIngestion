"""Ghi audit grounding + metadata (5 cau test) va artifacts/experiment_log.csv tu ket qua that."""
import csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "starter"))
from src.ingestion import load_corpus  # noqa: E402

AUDIT = ["q04", "q09", "q13", "q16", "q20"]
RATER = "Claude Sonnet 5.5 (nhan khoi tao); tac gia xem xet va xac nhan: CHUA"
pages = {p.page: p for p in load_corpus(ROOT / "data" / "pages.jsonl")}
tr = {s: {t["id"]: t for t in map(json.loads, open(ROOT / "results" / f"traces_{s}.jsonl", encoding="utf-8"))} for s in "ABC"}

G = {  # (chien luoc, cau): (diem, ly do). C dung chung ket qua voi B.
    ("A", "q04"): (2, "chunk hang 1 chua tron cau ve stack pointer, truy duoc p268"),
    ("A", "q09"): (2, "chunk hang 1 chua tron dong 'Copy: ...', truy duoc p286"),
    ("A", "q13"): (0, "top-3 khong co cau khuyen nghi 'initialize'; cau bi cat sang cua so ke tiep; hang 2 la 'best practice' khac (dat ten bien)"),
    ("A", "q16"): (2, "chunk hang 1 chua tron cau 'code generation', truy duoc p352"),
    ("A", "q20"): (2, "chunk hang 1 chua tron dinh nghia Select, truy duoc p385 muc 8.3"),
    ("B", "q04"): (2, "chunk hang 1 chua tron cau ve stack pointer, truy duoc p268"),
    ("B", "q09"): (2, "chunk hang 1 chua tron dong 'Copy: ...', truy duoc p286"),
    ("B", "q13"): (2, "chunk hang 1 chua day du cau khuyen nghi khoi tao bien"),
    ("B", "q16"): (2, "chunk hang 1 chua tron cau 'code generation', truy duoc p352"),
    ("B", "q20"): (2, "chunk hang 1 chua tron dinh nghia Select, truy duoc p385 muc 8.3"),
}
with open(ROOT / "results" / "audit_grounding.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["strategy", "question", "score_0_2", "reason", "rater"])
    for s in "ABC":
        for q in AUDIT:
            sc, why = G[("B" if s == "C" else s, q)]
            w.writerow([s, q, sc, why + (" | C dung chung top-3 voi B" if s == "C" else ""), RATER])
for s in "ABC":
    v = [G[("B" if s == "C" else s, q)][0] for q in AUDIT]
    print(f"Grounding {s}: {sum(v)/len(v):.2f}/2 | muc: {[v.count(i) for i in (0, 1, 2)]} (so cau o muc 0,1,2)")

rows, ok = [], {"A": 0, "B": 0, "C": 0}
for s in "ABC":
    for q in AUDIT:
        for h in tr[s][q]["top3"]:
            p = pages[h["page"]]
            src_ok = p.source == "openstax_intro_cs.pdf" and h["chunk_id"].startswith(p.document_id + ":")
            page_ok = h["text"] in p.text
            sec_ok = all(h["metadata"].get(k) == p.metadata[k] for k in ("chapter", "section"))
            good = src_ok and page_ok and sec_ok
            ok[s] += good
            rows.append([s, q, h["rank"], h["chunk_id"], h["page"], src_ok, page_ok, sec_ok, good])
with open(ROOT / "results" / "audit_metadata.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["strategy", "question", "rank", "chunk_id", "page", "source_ok", "text_on_cited_page", "chapter_section_ok", "record_ok"])
    w.writerows(rows)
for s in "ABC":
    print(f"Metadata {s}: {ok[s]}/15 ban ghi du va dung (kiem tra tu dong) | filter q20 tuan thu: {tr[s]['q20']['filter_compliant']}")

summ = json.loads((ROOT / "results" / "summary.json").read_text(encoding="utf-8"))
st = json.loads((ROOT / "results" / "ingest_stats.json").read_text(encoding="utf-8"))
f_ = lambda s, sp, k: f"{summ[s][sp][k]}/{summ[s][sp]['n']}"
cfg = {
    "A": ("fixed_size", 500, 50, "chapter,section,page (khong loc)", "khong", "Baseline: cua so co dinh se cat ngang y, nen Evidence Hit@3 thap hon B"),
    "B": ("sentence_pack<=500, gop manh<80", 500, 0, "chapter,section,page (khong loc)", "khong", "Chia theo cau giu tron y hon A (thay 1 yeu to: chunking) nen Hit@3 va coherence cao hon"),
    "C": ("nhu B (dung chung chunk)", 500, 0, "chapter,section,page", "chapter/section khi cau hoi co filter", "Loc metadata khi co pham vi giup tranh trang lech chuong (thay 1 yeu to so voi B)"),
}
with open(ROOT / "artifacts" / "experiment_log.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["strategy", "chunking", "chunk_size", "overlap", "metadata", "filter", "vectorizer", "hypothesis",
                "dev_hit1", "dev_hit3", "test_hit1", "test_hit3", "notes"])
    for s, (ch, size, ov, md, flt, hyp) in cfg.items():
        base = st["A" if s == "A" else "B"]
        note = (f"{base['chunks']} chunk; nap+embed {base['embed_store_seconds']}s; chi phi ${base['embed_cost_usd']:.6f}; "
                "gia thuyet ghi vao log sau khi chay, dua tren thiet ke ban dau; mau nho (17 dev/6 test)")
        w.writerow([s, ch, size, ov, md, flt, "openai/text-embedding-3-small (OpenRouter, 1536 chieu)", hyp,
                    f_(s, "dev", "hit1"), f_(s, "dev", "hit3"), f_(s, "test", "hit1"), f_(s, "test", "hit3"), note])
print("Da ghi artifacts/experiment_log.csv")
