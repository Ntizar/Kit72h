
import subprocess, re, html, sys, json

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
CK = "C:/Users/d_ant/Projects/kit72h/busquedas/c3.txt"

def fetch(url):
    r = subprocess.run(["curl","-s","--compressed","-L","--max-time","40","-c",CK,"-b",CK,"-A",UA,url], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout

def clean(s):
    return html.unescape(re.sub(r"\s+"," ",s or "")).strip()

def search(k):
    h = fetch("https://www.amazon.es/s?k=" + k.replace(" ","+"))
    if len(h) < 50000 or "captcha" in h[:5000].lower():
        return None
    items, seen = [], set()
    for m in re.finditer(r'data-asin="([A-Z0-9]{10})"', h):
        asin = m.group(1)
        if asin in seen: continue
        seg = h[m.start(): m.start()+25000]
        t = None
        for pat in [r'<h2[^>]*aria-label="([^"]{10,300})"', r'<img[^>]+alt="([^"]{15,300})"']:
            tm = re.search(pat, seg)
            if tm: t = tm.group(1); break
        if not t: continue
        pm = re.search(r'a-offscreen">([\d.,]+\s*&nbsp;?€)', seg)
        price = clean(pm.group(1)).replace("&nbsp;"," ") if pm else "?"
        rm = re.search(r'([\d,]+) de 5 estrellas|([\d,]+) out of 5 stars', seg)
        rating = rm.group(1) or rm.group(2) if rm else "?"
        seen.add(asin)
        items.append({"asin":asin,"title":clean(t)[:130],"price":price,"rating":rating})
        if len(items)>=10: break
    return items

if __name__=="__main__":
    print(json.dumps(search(sys.argv[1]), ensure_ascii=False, indent=0))
