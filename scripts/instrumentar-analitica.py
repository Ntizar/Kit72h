#!/usr/bin/env python3
"""Kit72h — instrumentar la analítica en todas las páginas HTML.

Inserta en el <head> de cada página el cargador de analítica:
    <script src="/js/analiticas.js?v=<VER>" defer></script>

Idempotente: si la página ya lo tiene, solo actualiza la versión. Los ficheros
de pintout/ (renders de Pinterest, no son páginas web navegables) y sketches/
(maquetas) se quedan fuera a propósito.

Uso:
    python3 scripts/instrumentar-analitica.py            # aplica
    python3 scripts/instrumentar-analitica.py --dry-run  # solo cuenta
    python3 scripts/instrumentar-analitica.py --ver 20261012b
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VER = "20261012a"
MARCA = "/js/analiticas.js"
EXCLUIDOS = {".git", "node_modules", "pintout", "sketches", "__pycache__",
             "analiticas"}  # analiticas/ es nuestro panel: no se mide a sí mismo

PATRON_EXISTENTE = re.compile(
    r'<script[^>]*src="/js/analiticas\.js(\?v=[^"]*)?"[^>]*></script>', re.I)


def version_actual(html):
    m = re.search(r'/js/analiticas\.js\?v=([^"]*)', html)
    return m.group(1) if m else None


def instrumentar(ruta, ver, aplicar):
    html = ruta.read_text(encoding="utf-8", errors="replace")
    if "</head>" not in html:
        return "sin-head"
    etiqueta = f'<script src="{MARCA}?v={ver}" defer></script>'
    if PATRON_EXISTENTE.search(html):
        if version_actual(html) == ver:
            return "ya-ok"
        if aplicar:
            nuevo = PATRON_EXISTENTE.sub(etiqueta, html, count=1)
            ruta.write_text(nuevo, encoding="utf-8")
        return "version-actualizada"
    nuevo = html.replace("</head>", etiqueta + "</head>", 1)
    if aplicar:
        ruta.write_text(nuevo, encoding="utf-8")
    return "insertado"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="no escribe nada")
    ap.add_argument("--ver", default=VER, help="versión de caché (query ?v=)")
    args = ap.parse_args()
    aplicar = not args.dry_run

    resumen = {}
    tocados = []
    for ruta in sorted(REPO.rglob("*.html")):
        rel = ruta.relative_to(REPO)
        if any(parte in EXCLUIDOS for parte in rel.parts):
            continue
        estado = instrumentar(ruta, args.ver, aplicar)
        resumen[estado] = resumen.get(estado, 0) + 1
        if estado in ("insertado", "version-actualizada"):
            tocados.append(str(rel))

    modo = "DRY-RUN (nada escrito)" if not aplicar else "APLICADO"
    print(f"[{modo}] versión {args.ver} — {sum(resumen.values())} páginas HTML vistas")
    for estado in ("insertado", "version-actualizada", "ya-ok", "sin-head"):
        if resumen.get(estado):
            print(f"  {estado}: {resumen[estado]}")
    if resumen.get("sin-head"):
        print("  AVISO: páginas sin </head> (revisar a mano)")
    if tocados:
        print("  primeras tocadas: " + ", ".join(tocados[:5]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
