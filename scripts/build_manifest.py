"""Sinh data/manifest.json va data/pages.jsonl tu PDF OpenStax (chuong 6-8)."""
import json, re, unicodedata, datetime
from pathlib import Path
from pypdf import PdfReader

PDF = Path('data/raw/openstax_intro_cs.pdf')
CHAPTERS = {  # chapter -> (title, first_pdf_page, last_pdf_page) cua phan noi dung
    6: ('Infrastructure Abstraction Layer: Operating Systems', 250, 294),
    7: ('High-Level Programming Languages', 308, 356),
    8: ('Data Management', 370, 423),
}

EXCLUDE = {356}  # chi con 1 cau ket thuc muc 7.4 + dau/chan trang

def normalize(t):
    t = unicodedata.normalize('NFC', t or '')
    return re.sub(r'\s+', ' ', t).strip()

r = PdfReader(PDF)

# Muc (6.1, 7.2, ...) lay tu outline cua PDF
sections = []
def walk(items, depth=0):
    for it in items:
        if isinstance(it, list):
            walk(it, depth + 1)
        elif depth == 1 and re.match(r'^\d+\.\d+ ', it.title):
            sections.append((r.get_destination_page_number(it) + 1, it.title.replace('andBusiness', 'and Business')))
walk(r.outline)
sections.sort()

def section_of(p):
    cur = None
    for start, title in sections:
        if start <= p:
            cur = title
    return cur

pages, total = [], 0
with open('data/pages.jsonl', 'w', encoding='utf-8') as f:
    for ch, (ctitle, a, b) in CHAPTERS.items():
        for p in range(a, b + 1):
            if p in EXCLUDE:
                continue
            text = normalize(r.pages[p - 1].extract_text())
            rec = {'document_id': 'openstax-intro-cs', 'source': 'openstax_intro_cs.pdf',
                   'page': p, 'text': text,
                   'metadata': {'chapter': ch, 'chapter_title': ctitle, 'section': section_of(p)}}
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            pages.append({'page': p, 'chapter': ch, 'section': section_of(p), 'chars': len(text)})
            total += len(text)

manifest = {
    'sources': [{
        'source_id': 'openstax-intro-cs',
        'title': 'Introduction to Computer Science (OpenStax), chapters 6-8',
        'source_path_or_url': 'https://openstax.org/details/books/introduction-computer-science (file: data/raw/openstax_intro_cs.pdf, khong commit)',
        'license_or_permission': 'CC BY 4.0 (OpenStax). Attribution: Access for free at openstax.org',
        'accessed_at': datetime.date.today().isoformat(),
        'physical_pdf_pages_total': len(r.pages),
        'counting_rule': 'Trang vat ly PDF (1-based). Tinh: ch6 p250-294, ch7 p308-355, ch8 p370-423 (tu muc x.1 den het muc cuoi). Loai: p356 (chi con 1 cau ket thuc muc), bia, muc luc, Preface, Chapter Outline/Introduction, Chapter Review, Index, Appendix.',
        'counted_pages': len(pages),
        'total_chars_normalized': total,
        'pages': pages,
    }],
}
Path('data/manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding='utf-8')
print('trang tinh:', len(pages), '| tong ky tu:', total, '| so muc:', len({x['section'] for x in pages}))
for ch in CHAPTERS:
    secs = sorted({x['section'] for x in pages if x['chapter'] == ch})
    print(f'ch{ch}:', secs)
