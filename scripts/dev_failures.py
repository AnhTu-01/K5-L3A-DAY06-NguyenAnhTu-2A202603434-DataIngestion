"""In cac cau DEV bi truot cua B (va danh sach id truot cua A, C) de phan tich loi. Khong in test."""
import json
from pathlib import Path

def load(s):
    return [json.loads(l) for l in open(f"../results/traces_{s}.jsonl", encoding="utf-8")]

tr = {s: {t["id"]: t for t in load(s) if t["split"] == "dev"} for s in "ABC"}
for s in "ABC":
    print(s, "truot Hit@1:", [i for i, t in tr[s].items() if not t["hit1"]], "| truot Hit@3:", [i for i, t in tr[s].items() if not t["hit3"]])
print()
for i, t in tr["B"].items():
    if t["hit1"]:
        continue
    print(f"== {i} ({t['type']}) {t['question']}  | gold trang {t['gold_page']} | hit3={t['hit3']}")
    for h in t["top3"]:
        print(f"   #{h['rank']} {h['score']:.3f} p{h['page']} evidence={h['evidence_hit']} | {h['text'][:140]}")
