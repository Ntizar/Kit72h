#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — verificar-asins: comprueba en lote que cada ficha de Amazon sigue viva.

Motivo (2026-09-28): la "cesta llena en 1 clic" llevaba a la página de error de
Amazon porque un ASIN del kit básico (B09VH3MZG7, manta térmica) devolvía 404.
Amazon rechaza la cesta ENTERA si uno solo de los ASINs no existe.

Uso:
  python scripts/verificar-asins.py                 # todos los ASINs de data/kits.json
  python scripts/verificar-asins.py --json          # solo el resumen en JSON
  python scripts/verificar-asins.py --mutos         # solo los muertos

Salida: lista legible + data/asins-estado.json (asin -> vivo|404|http_XXX|error).
Codigo de salida 1 si encuentra algun ASIN muerto (util para CI/cron).
Hilos: 4 en paralelo (Amazon no se queja; con mas empieza a dar 503).
"""
import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
KITS = RAIZ / "data" / "kits.json"
SALIDA = RAIZ / "data" / "asins-estado.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
RX_ASIN = re.compile(r"/dp/([A-Z0-9]{10})")


def asins_del_catalogo():
    d = json.loads(KITS.read_text(encoding="utf-8"))
    out = {}
    for k in d["kits"]:
        for s in k["secciones"]:
            for i in s.get("items", []):
                m = RX_ASIN.search(i.get("afiliado") or "")
                if m:
                    out.setdefault(m.group(1), []).append(f"{k['slug']}: {i.get('producto','')}")
    return out


def comprobar(asin, intentos=2):
    for n in range(intentos):
        req = urllib.request.Request(f"https://www.amazon.es/dp/{asin}", headers={
            "User-Agent": UA, "Accept-Language": "es-ES,es;q=0.9",
            "Accept": "text/html,application/xhtml+xml"})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                body = r.read().decode("utf-8", "ignore")
            t = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
            titulo = html.unescape(re.sub(r"\s+", " ", t.group(1)).strip()) if t else ""
            if re.search(r"no encontrad|no se ha encontrado|page not found", titulo, re.I):
                return "404", titulo[:100]
            return "vivo", titulo[:100]
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return "404", ""
            if e.code in (429, 503) and n == 0:
                continue
            return f"http_{e.code}", ""
        except Exception:
            if n == 0:
                continue
            return "error", ""
    return "error", ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="solo el resumen JSON")
    ap.add_argument("--muertos", action="store_true", help="listar solo los ASINs caidos")
    ap.add_argument("--hilos", type=int, default=4)
    args = ap.parse_args()

    catalogo = asins_del_catalogo()
    asins = sorted(catalogo)
    with ThreadPoolExecutor(max_workers=max(1, args.hilos)) as ex:
        res = list(ex.map(comprobar, asins))

    muertos = []
    estado = {}
    for a, (est, tit) in zip(asins, res):
        estado[a] = {"estado": est, "titulo": tit, "usado_en": catalogo[a][:3]}
        if est != "vivo":
            muertos.append({"asin": a, "estado": est, "titulo": tit, "usado_en": catalogo[a]})

    SALIDA.write_text(json.dumps({
        "generado": date.today().isoformat(), "total": len(asins),
        "vivos": len(asins) - len(muertos), "muertos": len(muertos), "asins": estado,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    if args.json:
        print(json.dumps({"total": len(asins), "vivos": len(asins) - len(muertos),
                          "muertos": len(muertos), "detalle": muertos}, ensure_ascii=False, indent=1))
    else:
        if muertos:
            print(f"ASINs CAIDOS ({len(muertos)} de {len(asins)}) — cada uno rompe la cesta de su kit:")
            for m in muertos:
                print(f"  {m['asin']} [{m['estado']}] {m['titulo'][:60]}")
                for u in m["usado_en"]:
                    print(f"      en {u}")
        elif not args.muertos:
            print(f"todos vivos: {len(asins)} ASINs ✅")

    print(f"\n-> {SALIDA.name}: {len(asins) - len(muertos)}/{len(asins)} vivos", file=sys.stderr)
    return 1 if muertos else 0


if __name__ == "__main__":
    sys.exit(main())
