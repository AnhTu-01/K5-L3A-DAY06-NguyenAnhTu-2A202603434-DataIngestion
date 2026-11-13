"""Tao results/audit_coherence.csv tu mau da chon + nhan (sua dict LABELS neu ban doi diem, roi chay lai)."""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sample = json.loads((ROOT / "results" / "audit_coherence_sample.json").read_text(encoding="utf-8"))
LABELS = {  # pos_id: ((diem_A, ly_do_A), (diem_B, ly_do_B))
    1: ((1, "mo dau giua cau thieu chu the (macOS), cuoi cut 'ne'"), (2, "cau tron ven, co chu the")),
    2: ((1, "cat giua tu, chua neu chu the (microkernel), cuoi cut 'mo'"), (1, "bat dau bang 'Also,' tiep noi y truoc, thieu chu the")),
    3: ((1, "dau la man cau cu, cuoi cut giua cau"), (2, "hai cach cap phat bo nho, du y")),
    4: ((1, "bat dau 'h-level', cuoi cut chu 'J'"), (1, "'It' chua ro chi gi")),
    5: ((1, "dau va cuoi cut"), (2, "dinh nghia array tu hieu duoc")),
    6: ((1, "dau va cuoi cut, lan chu thich hinh"), (1, "chu thich hinh lan vao, y 'In this implementation' bo do")),
    7: ((1, "dau va cuoi cut, tron hai chu de (interpreter va linking)"), (1, "'It also isolates...' chua ro 'It' la gi")),
    8: ((1, "danh sach muc tieu tron voi dinh nghia RDBMS, cuoi cut"), (1, "mo dau bang man bullet 'components of...' roi moi den dinh nghia")),
    9: ((1, "tron hai chu de (transaction va concurrency), cuoi cut"), (2, "mot cau tron y ve transaction management")),
    10: ((1, "lan cuoi muc truoc voi danh sach muc tieu, cuoi cut"), (2, "danh sach muc tieu nguyen ven (tron nhung it noi dung)")),
}
RATER = "Claude Sonnet 5.5 (nhan khoi tao); tac gia xem xet va xac nhan: CHUA"
rows, tot = [], {"A": 0, "B": 0}
for r in sample:
    (sa, ra), (sb, rb) = LABELS[r["pos_id"]]
    for s, sc, why in (("A", sa, ra), ("B", sb, rb)):
        tot[s] += sc
        rows.append([r["pos_id"], r["page"], r["char_pos"], s, r[s]["chunk_id"], sc, why, RATER])
    rows.append([r["pos_id"], r["page"], r["char_pos"], "C", r["B"]["chunk_id"], sb, "dung chung chunk voi B", RATER])
with open(ROOT / "results" / "audit_coherence.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["pos_id", "page", "char_pos", "strategy", "chunk_id", "score_0_2", "reason", "rater"])
    w.writerows(rows)
n = len(sample)
print(f"Coherence TB /2: A={tot['A']/n:.2f} | B={tot['B']/n:.2f} | C={tot['B']/n:.2f} (n={n})")
