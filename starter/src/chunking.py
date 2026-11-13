"""Hai kieu chia chunk: A = kich thuoc co dinh co overlap; B = gom theo cau, co gioi han kich thuoc."""
import re

from .models import Chunk, DocumentPage

_SENT = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9"“(\[])')


def _make(page: DocumentPage, idx: int, tag: str, start: int, end: int) -> Chunk:
    md = dict(page.metadata)
    md.update({"char_start": start, "char_end": end})
    return Chunk(chunk_id=f"{page.document_id}:p{page.page}:{tag}:{idx:03d}",
                 document_id=page.document_id, source=page.source, page=page.page,
                 text=page.text[start:end].strip(), metadata=md)


def fixed_size(page: DocumentPage, size: int, overlap: int) -> list[Chunk]:
    """Cua so truot theo ky tu, khong vuot qua ranh gioi trang."""
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("can size > 0 va 0 <= overlap < size")
    n, step, start, idx, out = len(page.text), size - overlap, 0, 0, []
    while start < n:
        end = min(start + size, n)
        ch = _make(page, idx, "fixed", start, end)
        if ch.text:
            out.append(ch)
            idx += 1
        if end >= n:
            break
        start += step
    return out


def _sentence_spans(text: str) -> list[tuple[int, int]]:
    spans, pos = [], 0
    for m in _SENT.finditer(text):
        spans.append((pos, m.start()))
        pos = m.end()
    spans.append((pos, len(text)))
    return [(s, e) for s, e in spans if e > s]


def _split_long(text: str, s: int, e: int, max_size: int) -> list[tuple[int, int]]:
    spans, a = [], s
    while e - a > max_size:
        cut = text.rfind(" ", a, a + max_size)
        if cut <= a:
            cut = a + max_size
        spans.append((a, cut))
        a = cut + 1 if text[cut:cut + 1] == " " else cut
    spans.append((a, e))
    return spans


def by_paragraph(page: DocumentPage, max_size: int, min_size: int = 80) -> list[Chunk]:
    """Gom cac cau lien tiep toi da max_size ky tu; cau dai hon max_size duoc cat theo tu.

    Manh nho (< min_size) duoc gop vao chunk ke can neu tong khong qua 1.2 * max_size.
    Ten ham giu theo khung bai, nhung PDF da trich khong con ranh gioi doan/heading
    nen day la chia theo CAU (khong overlap)."""
    if max_size <= 0:
        raise ValueError("max_size phai > 0")
    t, spans, cur = page.text, [], None
    for s, e in _sentence_spans(t):
        if e - s > max_size:
            if cur:
                spans.append(cur)
                cur = None
            spans.extend(_split_long(t, s, e, max_size))
            continue
        if cur and e - cur[0] > max_size:
            spans.append(cur)
            cur = None
        cur = (cur[0], e) if cur else (s, e)
    if cur:
        spans.append(cur)
    merged: list[tuple[int, int]] = []
    for sp in spans:
        if (merged and (sp[1] - sp[0] < min_size or merged[-1][1] - merged[-1][0] < min_size)
                and sp[1] - merged[-1][0] <= int(max_size * 1.2)):
            merged[-1] = (merged[-1][0], sp[1])
        else:
            merged.append(sp)
    out: list[Chunk] = []
    for a, b in merged:
        ch = _make(page, len(out), "para", a, b)
        if ch.text:
            out.append(ch)
    return out
