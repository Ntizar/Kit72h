
import subprocess, re, html, json, time, sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
CK = "C:/Users/d_ant/Projects/kit72h/busquedas/c3.txt"

def fetch(url):
    r = subprocess.run(["curl","-s","--compressed","-L","--max-time","40","-c",CK,"-b",CK,"-A",UA,url], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout

def clean(s):
    return html.unescape(re.sub(r"\s+"," ",s or "")).strip()

def ficha(asin):
    h = fetch("https://www.amazon.es/dp/" + asin)
    if len(h) < 30000 or "captcha" in h[:5000].lower():
        return {"asin":asin, "ok":False, "code":"short/captcha", "len":len(h)}
    t = re.search(r'id="productTitle"[^>]*>\s*([^<]+)', h)
    p = None
    pm = re.search(r'id="corePrice_feature_div".{0,3000}?a-offscreen">([^<]+)', h, re.S) or re.search(r'a-offscreen">([\d.,]+\s*&nbsp;?€)', h)
    if pm: p = clean(pm.group(1)).replace("&nbsp;"," ")
    r = re.search(r'([\d,]+) de 5 estrellas|([\d,]+) out of 5 stars', h)
    rating = (r.group(1) or r.group(2)) if r else None
    rc = re.search(r'([\d.]+) valoraciones|([\d.,]+) ratings', h)
    return {"asin":asin, "ok":True, "title":clean(t.group(1))[:140] if t else None,
            "price":p, "rating":rating, "nratings": rc.group(1) or rc.group(2) if rc else None}

if __name__=="__main__":
    asins = sys.argv[1:]
    for a in asins:
        f = ficha(a)
        print(json.dumps(f, ensure_ascii=False), flush=True)
        time.sleep(1.2)
