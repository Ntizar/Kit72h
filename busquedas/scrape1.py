import re, subprocess, time, sys, html

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'

def fetch_search(query):
    url = f'https://www.amazon.es/s?k={query}'
    for attempt in range(3):
        cookiejar = f'ck_{query[:12]}_{attempt}.txt'
        cmd = ['curl', '-s', '-L', '-o', f's_{query[:12]}_{attempt}.html',
               '-w', '%{http_code}', '-c', cookiejar, '-b', cookiejar, '-A', UA,
               '--compressed', '--max-time', '60', url]
        code = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
        try:
            txt = open(f's_{query[:12]}_{attempt}.html', encoding='utf-8', errors='ignore').read()
        except: txt=''
        if code=='200' and 'captcha' not in txt[:3000].lower() and 's-result' in txt:
            return txt
        time.sleep(2)
    return txt if 'txt' in dir() else ''

def parse(txt):
    results = []
    # split by result blocks
    blocks = re.split(r'data-asin="([A-Z0-9]{10})"', txt)
    for i in range(1, len(blocks)-1, 2):
        asin = blocks[i]; b = blocks[i+1][:8000]
        if not re.search(r's-result-item|s-inclusion-container', b) and 'a-price' not in b: continue
        m = re.search(r'<h2[^>]*>.*?<span[^>]*>(.*?)</span>', b, re.S)
        title = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else ''
        mp = re.search(r'a-price[^>]*><span class="a-price-whole">([\d\.,]+)', b)
        pf = re.search(r'a-price-fraction">(\d+)', b)
        price = None
        if mp:
            whole = mp.group(1).replace('.','').replace(',','.')
            price = float(whole) + (int(pf.group(1))/100 if pf else 0)
        r = re.search(r'([\d,]+) de 5 estrellas', b)
        rating = float(r.group(1).replace(',', '.')) if r else None
        rv = re.search(r'>([\d\.]+)<', re.search(r'a-size-base s-underline-text(.*?)</span>', b, re.S).group(1)) if re.search(r'a-size-base s-underline-text', b) else None
        reviews = int(rv.group(1).replace('.','')) if rv else 0
        if title and price:
            results.append((asin, title, price, rating, reviews))
    return results

PRODUCTS = [
 ("1", "botella agua 3 litros", (5,15)),
 ("2", "pastillas potabilizadoras agua", (8,15)),
 ("3", "comida deshidratada militar racion", (8,12)),
 ("4", "lata legumbres cocidas conserva", (1,3)),
 ("5", "barritas energeticas pack", (10,15)),
 ("6", "linterna LED pilas", (10,20)),
 ("7", "powerbank 20000 mAh", (25,50)),
 ("8", "pilas alcalinas AA AAA surtidas", (10,20)),
 ("9", "radio a pilas dinamo", (15,35)),
 ("10", "mapa fisico papel", (5,15)),
 ("11", "bolsa estanca documentos", (5,12)),
 ("12", "riñonera oculta portadocumentos", (8,15)),
 ("13", "botiquin primeros auxilios", (15,30)),
 ("14", "gel hidroalcoholico toallitas", (5,10)),
 ("15", "manta termica emergencia", (3,8)),
 ("16", "poncho impermeable chubasquero", (15,30)),
]

out = []
for num, q, (lo, hi) in PRODUCTS:
    txt = fetch_search(q.replace(' ', '+'))
    res = parse(txt)
    # prefer products matching price range, rating>=4, reviews>=100
    cands = [r for r in res if lo <= r[2] <= hi and r[3] and r[3] >= 4.0 and r[4] >= 50]
    if not cands:
        cands = [r for r in res if lo*0.8 <= r[2] <= hi*1.3 and r[3] and r[3] >= 4.0]
    cands.sort(key=lambda r: -(r[4] or 0))
    out.append((num, q, cands[:3], len(res)))
    print(f'{num} {q}: {len(res)} items, top: {cands[:2] if cands else res[:2]}')
    sys.stdout.flush()

import json
json.dump([(n,q,c) for n,q,c,_ in out], open('cands.json','w'))
print('DONE')
