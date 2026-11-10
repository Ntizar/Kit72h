#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bump único del token `styles.css?v=...` en las páginas publicadas.

Uso:
    python3 scripts/bump-version-css.py --nueva 20261110a
    python3 scripts/bump-version-css.py --nueva 20261110a --seco

No toca pintout, sketches, busquedas ni videos. Verifica que en cada HTML queda
una sola referencia y que el atributo cierra bien (`...">`).
"""
from __future__ import annotations

import argparse
import re
from html.parser import HTMLParser
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CARPETAS = ("blog", "kit", "fuentes", "zona", "privacidad", "noticias", "analiticas")
EXCLUIR = {"pintout", "sketches", "busquedas", "videos", ".git"}


def paginas() -> list[Path]:
    salida = [p for p in RAIZ.glob("*.html")]
    for carpeta in CARPETAS:
        base = RAIZ / carpeta
        if base.is_dir():
            salida.extend(base.rglob("*.html"))
    return sorted(p for p in salida if not (set(p.parts) & EXCLUIR))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nueva", required=True, help="token nuevo, p. ej. 20261110a")
    ap.add_argument("--seco", action="store_true", help="no escribir, solo contar")
    args = ap.parse_args()
    if not re.fullmatch(r"[\w-]+", args.nueva):
        ap.error("token inválido")

    patron = re.compile(r"styles\.css\?v=[\w-]+")
    tocados = 0
    for ruta in paginas():
        html = ruta.read_text(encoding="utf-8")
        nuevo, n = patron.subn(f"styles.css?v={args.nueva}", html)
        if not n:
            continue
        assert nuevo.count("styles.css?v=") == 1, ruta
        assert f'styles.css?v={args.nueva}">' in nuevo, ruta
        HTMLParser().feed(nuevo)
        tocados += 1
        if not args.seco:
            ruta.write_text(nuevo, encoding="utf-8")
    print(f"páginas actualizadas: {tocados} · token: {args.nueva}"
          + (" · seco" if args.seco else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
