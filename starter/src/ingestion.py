"""Doc corpus da trich san (data/pages.jsonl, tao boi scripts/build_manifest.py) va chuan hoa."""
import json
import re
import unicodedata
from pathlib import Path

from .models import DocumentPage

ATTRIBUTION = "Access for free at openstax.org"
# Chan trang OpenStax dang "346 7 • High-Level Programming Languages Access for free at openstax.org"
FOOTER = re.compile(r"\b\d{1,3} \d{1,2} • [^•]{3,80}? Access for free at openstax\.org")


def normalize_text(text: str) -> str:
    """NFC, bo chan trang lap lai, gop khoang trang. Dong ghi nguon van nam o README/manifest."""
    t = unicodedata.normalize("NFC", text or "")
    t = FOOTER.sub(" ", t)
    t = t.replace(ATTRIBUTION, " ")
    return re.sub(r"\s+", " ", t).strip()


def load_corpus(path: Path) -> list[DocumentPage]:
    """Doc tung trang tu JSONL; trang rong duoc bo qua va bao loi ro rang."""
    pages: list[DocumentPage] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        d = json.loads(line)
        text = normalize_text(d["text"])
        if not text:
            print(f"[canh bao] trang {d['page']} khong co text, bo qua")
            continue
        pages.append(DocumentPage(document_id=d["document_id"], source=d["source"],
                                  page=d["page"], text=text, metadata=d["metadata"]))
    return pages
