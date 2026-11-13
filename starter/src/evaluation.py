"""Cham truy xuat tu dong (Hit@1, Evidence Hit@3) va giu trace day du. Khong thay cham thu cong."""
from collections import defaultdict
from typing import Any

from .ingestion import normalize_text


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    """Hit = chunk thuoc dung nguon/trang gold va chua DU evidence_quote (hoac nguon thay the alt_gold)."""
    golds = [{"page": question["gold_page"], "evidence_quote": question["evidence_quote"]}]
    golds += list(question.get("alt_gold", []))
    top = []
    for rank, h in enumerate(hits, 1):
        evidence_hit = h["document_id"] == question["gold_source_id"] and any(
            h["page"] == g["page"] and normalize_text(g["evidence_quote"]) in h["text"] for g in golds)
        page_hit = h["document_id"] == question["gold_source_id"] and any(h["page"] == g["page"] for g in golds)
        top.append({"rank": rank, "chunk_id": h["chunk_id"], "page": h["page"], "score": round(h["score"], 4),
                    "metadata": h["metadata"], "text": h["text"],
                    "evidence_hit": evidence_hit, "page_hit": page_hit})
    flt = question.get("filter")
    compliant = None
    if flt:
        compliant = bool(top) and all(all(t["metadata"].get(k) == v for k, v in flt.items()) for t in top)
    return {"id": question["id"], "split": question["split"], "type": question.get("type"),
            "question": question["question"], "filter": flt, "gold_page": question["gold_page"],
            "evidence_quote": question["evidence_quote"],
            "hit1": bool(top and top[0]["evidence_hit"]), "hit3": any(t["evidence_hit"] for t in top),
            "page_hit1": bool(top and top[0]["page_hit"]), "page_hit3": any(t["page_hit"] for t in top),
            "filter_compliant": compliant, "top3": top}


def summarize(traces: list[dict[str, Any]]) -> dict[str, Any]:
    """Tong hop theo chien luoc va split; bao so tu/mau."""
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for t in traces:
        groups[(t["strategy"], t["split"])].append(t)
    out: dict[str, Any] = {}
    for (strategy, split), ts in sorted(groups.items()):
        fq = [t for t in ts if t["filter"]]
        out.setdefault(strategy, {})[split] = {
            "n": len(ts), "hit1": sum(t["hit1"] for t in ts), "hit3": sum(t["hit3"] for t in ts),
            "page_hit1": sum(t["page_hit1"] for t in ts), "page_hit3": sum(t["page_hit3"] for t in ts),
            "filter_questions": len(fq), "filter_compliant": sum(bool(t["filter_compliant"]) for t in fq)}
    return out
