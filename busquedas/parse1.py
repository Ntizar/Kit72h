import re, html

def parse(txt):
    results = []
    blocks = re.split(r'data-asin="([A-Z0-9]{10})"', txt)
    for i in range(1, len(blocks)-1, 2):
        asin = blocks[i]; b = blocks[i+1][:12000]
        m = re.search(r'<h2[^>]*>.*?<span[^>]*>(.*?)</span>', b, re.S)
        title = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else ''
        mp = re.search(r'a-price-whole">([\d\.]+)<span class="a-price-decimal">,</span><span class="a-price-fraction">(\d+)', b)
        if not mp:
            off = re.search(r'a-offscreen">([\d\.]+),(\d\d)\s*€', b)
            if off: mp = off
        price = None
        if mp:
            price = float(mp.group(1).replace('.','')) + int(mp.group(2))/100
        r = re.search(r'([\d,]+) de 5 estrellas', b)
        rating = float(r.group(1).replace(',', '.')) if r else None
        rv = re.search(r'([\d\.]+)\s*</span>\s*<span class="a-size-base s-underline-text', b) or re.search(r's-underline-text">([\d\.]+)<', b)
        reviews = int(rv.group(1).replace('.','')) if rv else 0
        if title and price:
            results.append((asin, title, price, rating, reviews))
    return results

import glob, json
all_c = {}
for f in glob.glob('s_*.html'):
    txt = open(f, encoding='utf-8', errors='ignore').read()
    all_c[f] = parse(txt)
json.dump(all_c, open('cands.json','w'))
for f, r in all_c.items():
    print(f, len(r), r[:2])
