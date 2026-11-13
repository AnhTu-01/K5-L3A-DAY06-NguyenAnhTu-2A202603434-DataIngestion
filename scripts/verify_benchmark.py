"""Kiem tra benchmark: evidence co trong trang gold, filter khop metadata, dem split."""
import json, re, unicodedata, collections
norm = lambda t: re.sub(r'\s+', ' ', unicodedata.normalize('NFC', t or '')).strip()
pages = {}
for l in open('data/pages.jsonl', encoding='utf-8'):
    d = json.loads(l); pages[d['page']] = d
qs = json.load(open('benchmark/questions.json', encoding='utf-8'))
bad = 0
for q in qs:
    p = pages.get(q['gold_page'])
    ok_ev = bool(p) and norm(q['evidence_quote']) in p['text']
    ok_f = True
    if q['filter']:
        ok_f = all(p['metadata'].get(k) == v for k, v in q['filter'].items())
    if not (ok_ev and ok_f):
        bad += 1
        print('LOI', q['id'], '| evidence:', ok_ev, '| filter:', ok_f)
c = collections.Counter(q['split'] for q in qs)
nf = [q['id'] for q in qs if q['filter']]
print(f"tong {len(qs)} cau | dev {c['dev']} | test {c['test']} | filter: {nf} | loi: {bad}")
print('filter trong test:', [q['id'] for q in qs if q['filter'] and q['split'] == 'test'])
