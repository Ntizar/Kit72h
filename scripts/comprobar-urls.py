#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
comprobar-urls.py — Comprueba que las fichas de Amazon del kit siguen activas.
Genera data/estado.json con:
  ok → ficha responde 200
  posible_rotura → 404/503/bloqueo repetido
Lanzar periódicamente (cron mensual). Puedes limitar con --solo N (prueba).
"""
import json, re, subprocess, sys, time, argparse
from pathlib import Path
from datetime import date

RAIZ = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
CK = RAIZ / "busquedas" / "ck_estado.txt"
ESTADO = RAIZ / "data" / "estado.json"

def cargar_items():
    d = json.loads((RAIZ / "data" / "kits.json").read_text(encoding="utf-8"))
    items = []
    for k in d["kits"]:
        for s in k["secciones"]:
            for it in s.get("items", []):
                if it.get("afiliado", "").startswith("http"):
                    items.append({
                        "url": it["afiliado"],
                        "producto": it["producto"],
                        "kit": k["titulo"],
                    })
    return items

def curl(url):
    r = subprocess.run(
        ["curl", "-s", "-L", "--compressed", "-w", "%{http_code}",
         "-c", str(CK), "-b", str(CK), "-A", UA, url],
        capture_output=True, text=True, timeout=60)
    body = r.stdout[:-3]
    code = r.stdout[-3:]
    return code, body

def comprobar(url, intentos=2):
    """Devuelve 'ok' | 'posible_rotura'. Con cookie jar y reintentos anti-503."""
    for i in range(intentos):
        code, body = curl(url)
        if code == "200" and "productTitle" in body:
            return "ok"
        if code == "404":
            return "posible_rotura"
        time.sleep(3 + i * 3)  # 503 suele ser rate-limit: esperar y reintentar
    return "posible_rotura"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", type=int, default=0, help="comprobar solo N productos (prueba)")
    args = ap.parse_args()

    previo = {}
    if ESTADO.exists():
        try:
            previo = json.loads(ESTADO.read_text(encoding="utf-8")).get("productos", {})
        except Exception:
            pass

    items = cargar_items()
    if args.solo:
        items = items[:args.solo]

    productos = {}
    n_ok = 0
    for it in items:
        e = comprobar(it["url"])
        productos[it["url"]] = {
            "estado": e,
            "producto": it["producto"],
            "kit": it["kit"],
            "busqueda": it["producto"],
            "fecha": date.today().isoformat(),
        }
        n_ok += e == "ok"
        print(f"[{e}] {it['producto'][:70]}")
        time.sleep(1.5)  # cortesía anti rate-limit

    ESTADO.write_text(json.dumps({
        "generado": date.today().isoformat(),
        "total": len(productos),
        "ok": n_ok,
        "productos": productos,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n→ {ESTADO.name}: {n_ok}/{len(productos)} activos")

if __name__ == "__main__":
    main()
