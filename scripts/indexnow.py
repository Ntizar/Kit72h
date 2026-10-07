#!/usr/bin/env python3
"""IndexNow: notifica a Bing/Yandex/Seznam (y Google vía API si hay clave) las URLs
nuevas o modificadas de kit72h.com. Gratis, sin registro (la clave se valida sirviendo
un fichero <clave>.txt en la raíz del sitio).

Uso:
  python3 scripts/indexnow.py                    # envía TODO el sitemap (1ª vez / mass ping)
  python3 scripts/indexnow.py --desde-git HEAD~1 # solo URLs de ficheros tocados en un commit
  python3 scripts/indexnow.py /kit/kit-apagon/ /blog/mejor-linterna-emergencia-72h/
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.request

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://kit72h.com"
# Clave IndexNow: identificador arbitrario; su fichero <clave>.txt sirve en la raíz.
KEY_FILE = os.path.join(R, "indexnow-key.txt")


def clave_actual():
    if os.path.exists(KEY_FILE):
        return open(KEY_FILE).read().strip()
    import secrets
    k = secrets.token_hex(16)
    with open(KEY_FILE, "w") as f:
        f.write(k)
    return k


def urls_sitemap():
    import xml.etree.ElementTree as ET
    arbol = ET.parse(os.path.join(R, "sitemap.xml"))
    return [e.text for e in arbol.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]


def urls_de_commit(rango):
    """URLs del sitemap cuyas rutas aparecen tocadas en el rango de commits."""
    r = subprocess.run(["git", "-C", R, "diff", "--name-only", rango],
                       capture_output=True, text=True)
    tocados = set(r.stdout.strip().split("\n"))
    urls = []
    for u in urls_sitemap():
        ruta = u.replace(BASE, "").strip("/")
        if not ruta or (ruta + "/index.html") in tocados or ruta in tocados \
           or any(ruta.startswith("blog/") and t.startswith("data/") for t in tocados):
            urls.append(u)
    return urls


def enviar(urls, key):
    if not urls:
        print("IndexNow: sin URLs que notificar")
        return 0
    payload = json.dumps({
        "host": "kit72h.com",
        "key": key,
        "keyLocation": BASE + "/" + key + ".txt",
        "urlList": urls[:10000],
    }).encode()
    ok_total = 0
    # api.indexnow.org reparte a Bing, Yandex y Seznam (no hace falta más)
    for endpoint in ("https://api.indexnow.org/indexnow",):
        req = urllib.request.Request(endpoint, data=payload,
                                     headers={"Content-Type": "application/json; charset=utf-8",
                                              "User-Agent": "kit72h-indexnow/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                ok_total += 1
                print("IndexNow %s -> HTTP %s (%d urls)" % (endpoint.split("/")[2], r.status, len(urls)))
        except Exception as e:
            print("IndexNow %s -> ERROR %s" % (endpoint.split("/")[2], str(e)[:120]))
    return 0 if ok_total else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde-git", help="rango de commits, ej HEAD~1")
    ap.add_argument("rutas", nargs="*", help="rutas sueltas tipo /kit/kit-apagon/")
    args = ap.parse_args()

    key = clave_actual()
    # El fichero de verificación debe estar en el repo (se sirve en la raíz por Pages)
    kf = os.path.join(R, key + ".txt")
    if not os.path.exists(kf):
        with open(kf, "w") as f:
            f.write(key)
        print("creado fichero de verificación %s.txt (conmítalo)" % key)

    if args.rutas:
        urls = [BASE + r if r.startswith("/") else BASE + "/" + r for r in args.rutas]
    elif args.desde_git:
        urls = urls_de_commit(args.desde_git)
    else:
        urls = urls_sitemap()

    sys.exit(enviar(urls, key))


if __name__ == "__main__":
    main()
