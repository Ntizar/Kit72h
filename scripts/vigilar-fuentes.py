#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vigilar-fuentes.py — Vigilancia nocturna Kit72h de fuentes oficiales.

Descarga las fuentes (UE + Protección Civil), las normaliza a texto sin
chrome y las compara línea a línea contra data/snapshots/*.txt.
Imprime un informe JSON en stdout: http, líneas añadidas/borradas
sustantivas y hash nuevo por fuente. Actualiza snapshots solo con
--aplicar (tras decidir que el cambio es legítimo).

Uso:
  python scripts/vigilar-fuentes.py            # informe
  python scripts/vigilar-fuentes.py --aplicar  # regenera snapshots + hashes
"""
import json, re, sys, hashlib, subprocess
from pathlib import Path
from html.parser import HTMLParser

RAIZ = Path(__file__).resolve().parent.parent
SNAP = RAIZ / "data" / "snapshots"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")

URLS = {
    "eu-resilience-and-security_es": "https://commission.europa.eu/topics/eu-resilience-and-security_es",
    "preparedness_es": "https://commission.europa.eu/topics/preparedness_es",
    "recomendaciones": "https://www.proteccioncivil.es/gestion-riesgos/recomendaciones",
    "lluvias-intensas": "https://www.proteccioncivil.es/coordinacion/gestion-de-riesgos/meterologicos/lluvias-intensas",
    "altas-temperaturas": "https://www.proteccioncivil.es/coordinacion/gestion-de-riesgos/meterologicos/altas-temperaturas",
}


class TX(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "head"}

    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, t, a):
        if t in self.SKIP:
            self.skip += 1
        if t in ("p", "br", "div", "li", "h1", "h2", "h3", "h4", "tr", "section", "article"):
            self.parts.append("\n")

    def handle_endtag(self, t):
        if t in self.SKIP and self.skip > 0:
            self.skip -= 1

    def handle_data(self, d):
        if not self.skip:
            self.parts.append(d)


def norm(html):
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    title = re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
    p = TX()
    try:
        p.feed(html)
    except Exception:
        pass
    txt = "".join(p.parts)
    lines = [re.sub(r"\s+", " ", l).strip() for l in txt.splitlines()]
    lines = [l for l in lines if l and not re.fullmatch(r"[\W_]+", l)]
    return [title] + lines


def fetch(url):
    r = subprocess.run(
        ["curl", "-s", "-L", "--compressed", "-A", UA, "--max-time", "50",
         "-w", "\n@@HTTP:%{http_code}@@", url],
        capture_output=True, text=True, timeout=70,
        encoding="utf-8", errors="replace")
    body, _, code = r.stdout.rpartition("\n@@HTTP:")
    return code.replace("@@", "").strip(), body


def substantive(ls):
    out = []
    for l in ls:
        if len(l) < 25:
            continue
        out.append(l)
    return out[:30]


def main():
    aplicar = "--aplicar" in sys.argv
    import difflib
    hashes_old = {}
    hp = SNAP / "hashes.json"
    if hp.exists():
        hashes_old = json.loads(hp.read_text(encoding="utf-8"))
    informe = {}
    for key, url in URLS.items():
        try:
            code, body = fetch(url)
        except Exception as e:
            informe[key] = {"http": "ERROR", "error": str(e)}
            continue
        if code != "200":
            informe[key] = {"http": code, "url": url}
            continue
        lines = norm(body)
        h = hashlib.sha256("\n".join(lines).encode()).hexdigest()[:16]
        entry = {"http": code, "hash": h, "hash_prev": hashes_old.get(key), "nlineas": len(lines)}
        old_path = SNAP / f"{key}.txt"
        if old_path.exists():
            old = [l.strip() for l in old_path.read_text(encoding="utf-8").splitlines() if l.strip()]
            sm = difflib.SequenceMatcher(None, old, lines)
            added, removed = [], []
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag in ("insert", "replace"):
                    added += lines[j1:j2]
                if tag in ("delete", "replace"):
                    removed += old[i1:i2]
            entry["anadidas_sustantivas"] = substantive(added)
            entry["borradas_sustantivas"] = substantive(removed)
            entry["cambio_hash"] = h != hashes_old.get(key)
            if aplicar:
                old_path.write_text("\n".join(lines), encoding="utf-8")
        else:
            entry["nueva"] = True
            if aplicar:
                old_path.write_text("\n".join(lines), encoding="utf-8")
        informe[key] = entry
    if aplicar:
        nuevos = dict(hashes_old)
        for k, v in informe.items():
            if v.get("http") == "200" and "hash" in v:
                nuevos[k] = v["hash"]
        (SNAP / "hashes.json").write_text(json.dumps(nuevos, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(informe, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
