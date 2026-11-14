#!/usr/bin/env python3
"""Kit72h — traducciones: pone al día los idiomas y publica.

Pensado para el cron nocturno. Hace, en este orden y con presupuesto de tiempo:

  1. Traduce las entradas de blog pendientes de cada idioma (por lotes, con caché:
     cada noche avanza lo que puede y lo deja a medias sin romper nada).
  2. Regenera SEO (sitemap con hreflang) y hornea el HTML de todos los mercados.
  3. Pasa el gate de calidad. Si falla, NO commitea.
  4. Commit + push solo si hay cambios (el push publica en GitHub Pages).

Uso:
  python scripts/kit72h-traducciones.py                  # todo, 3 h de presupuesto
  python scripts/kit72h-traducciones.py --solo-traducir  # sin publicar
  python scripts/kit72h-traducciones.py --entradas 4     # solo 4 por idioma (prueba)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
IDIOMAS = ["en", "de", "fr", "it", "nl"]


def corre(cmd, timeout=None):
    print(f"\n$ {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True,
                       timeout=timeout, encoding="utf-8", errors="ignore")
    salida = (r.stdout or "") + (r.stderr or "")
    print("\n".join(salida.strip().splitlines()[-25:]), flush=True)
    return r.returncode


def pendientes(lang):
    ruta = RAIZ / f"data/i18n/contenido/{lang}.json"
    if not ruta.exists():
        return None
    try:
        d = json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    base = json.loads((RAIZ / "data/blog.json").read_text(encoding="utf-8"))
    hechas = set((d.get("blog") or {}).keys())
    return [e["slug"] for e in base["entradas"] if e["slug"] not in hechas]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--presupuesto", type=int, default=10800,
                    help="segundos máximos de traducción (por defecto 3 h)")
    ap.add_argument("--entradas", type=int, default=0,
                    help="máximo de entradas por idioma y pasada (0 = todas las que quepan)")
    ap.add_argument("--solo-traducir", action="store_true")
    ap.add_argument("--sin-push", action="store_true")
    a = ap.parse_args()

    t0 = time.time()
    total_antes = {}

    for lang in IDIOMAS:
        p = pendientes(lang)
        if p is None:
            print(f"  {lang}: sin overlay todavía, se salta", flush=True)
            continue
        total_antes[lang] = len(p)
    print(f"pendientes: {total_antes}", flush=True)

    for lang in IDIOMAS:
        if lang not in total_antes or not total_antes[lang]:
            continue
        restante = a.presupuesto - (time.time() - t0)
        if restante < 180:
            print(f"  {lang}: sin tiempo (quedan {restante:.0f}s), se deja para la próxima",
                  flush=True)
            continue
        cmd = [sys.executable, "scripts/traducir.py", "blog", "--langs", lang,
               "--pendientes", "--hilos", "4"]
        if a.entradas:
            cmd += ["--limite", str(a.entradas)]
        corre(cmd, timeout=int(restante) + 60)

    if a.solo_traducir:
        print("\nsolo-traducir: no se regenera ni se publica")
        return 0

    if corre([sys.executable, "scripts/generar-seo.py"]) != 0:
        print("SEO falló: no se publica")
        return 1
    if corre([sys.executable, "scripts/prerender.py"], timeout=7200) != 0:
        print("prerender falló: no se publica")
        return 1
    if corre([sys.executable, "scripts/verificar-sitio.py"]) != 0:
        print("gate de calidad en rojo: NO se publica")
        return 1
    if a.sin_push:
        print("sin-push: cambios en disco, sin commitear")
        return 0

    # Commit + push solo si hay algo que contar.
    if subprocess.run(["git", "status", "--porcelain"], cwd=RAIZ,
                      capture_output=True, text=True).stdout.strip():
        subprocess.run(["git", "add", "-A"], cwd=RAIZ, check=True)
        msg = "chore(i18n): traducciones del blog + prerender multi-mercado"
        subprocess.run(["git", "commit", "-m", msg], cwd=RAIZ, check=False)
        r = subprocess.run(["git", "push"], cwd=RAIZ, capture_output=True, text=True)
        if r.returncode != 0:
            # Otro cron (la VM) puede haber pusheado mientras traducíamos: rebase y reintento.
            print("push rechazado → pull --rebase y reintento", flush=True)
            subprocess.run(["git", "pull", "--rebase", "--autostash"], cwd=RAIZ,
                           capture_output=True, text=True)
            r = subprocess.run(["git", "push"], cwd=RAIZ, capture_output=True, text=True)
        print(r.stdout + r.stderr)
        return 0 if r.returncode == 0 else 1
    print("sin cambios: nada que publicar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
