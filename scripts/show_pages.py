"""In noi dung trang da chuan hoa: python scripts/show_pages.py 258 268 [--n 1800]"""
import json, sys
args = sys.argv[1:]
n = 1800
if '--n' in args:
    i = args.index('--n'); n = int(args[i + 1]); del args[i:i + 2]
want = {int(a) for a in args}
for line in open('data/pages.jsonl', encoding='utf-8'):
    d = json.loads(line)
    if d['page'] in want:
        m = d['metadata']
        print(f"\n===== TRANG {d['page']} | ch{m['chapter']} | {m['section']} | {len(d['text'])} ky tu =====")
        print(d['text'][:n])
