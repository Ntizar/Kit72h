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
VER = "20261023a"
MARCA = "/js/analiticas.js"
CSS_VER = "20261015b"          # versión de caché de /css/styles.css
RUTA_PANEL = "/analiticas/"    # enlace discreto del pie al panel privado
EXCLUIDOS = {".git", "node_modules", "pintout", "sketches", "__pycache__",
             "analiticas"}  # analiticas/ es nuestro panel: no se mide a sí mismo

PATRON_EXISTENTE = re.compile(
    r'<script[^>]*src="/js/analiticas\.js(\?v=[^"]*)?"[^>]*></script>', re.I)
PATRON_CSS_VER = re.compile(r'styles\.css\?v=[0-9a-zA-Z]+')
ENLACE_PANEL = (' · <a class="pie-panel" href="' + RUTA_PANEL + '" rel="nofollow"'
                ' title="Panel privado de analítica">Panel</a>')


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


def pie_panel(html, aplicar, dry):
    """Mete el enlace discreto al panel justo antes del último </footer>.
    Idempotente: si la página ya enlaza /analiticas/, no hace nada."""
    if RUTA_PANEL in html:
        return "ya-ok"
    corte = html.rfind("</footer>")
    if corte == -1:
        return "sin-footer"
    nuevo = html[:corte] + ENLACE_PANEL + "\n" + html[corte:]
    if aplicar:
        dry.write_text(nuevo, encoding="utf-8")
    return "pie-insertado"


def normalizar_css(html, aplicar, dry):
    """Alinea styles.css?v= a CSS_VER. Reemplazo quirúrgico SOLO del número de
    versión (este repo ya se quedó sin CSS una vez por un regex demasiado
    goloso: nunca tocar el resto de la etiqueta <link>)."""
    if f"styles.css?v={CSS_VER}" in html:
        return "css-ok"
    nuevo, n = PATRON_CSS_VER.subn(f"styles.css?v={CSS_VER}", html)
    if n == 0:
        return "css-sin-ref"
    if aplicar:
        dry.write_text(nuevo, encoding="utf-8")
    return "css-actualizado"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="no escribe nada")
    ap.add_argument("--ver", default=VER, help="versión de caché (query ?v=)")
    ap.add_argument("--css-ver", default=CSS_VER, help="versión de /css/styles.css")
    ap.add_argument("--solo-pie", action="store_true",
                    help="solo enlace del pie + css (no toca el tag de analítica)")
    args = ap.parse_args()
    aplicar = not args.dry_run

    resumen = {}
    tocados = []
    for ruta in sorted(REPO.rglob("*.html")):
        rel = ruta.relative_to(REPO)
        if any(parte in EXCLUIDOS for parte in rel.parts):
            continue
        html = ruta.read_text(encoding="utf-8", errors="replace")
        marcas = []
        if not args.solo_pie:
            marcas.append(("tag:" + instrumentar(ruta, args.ver, aplicar)))
            html = ruta.read_text(encoding="utf-8", errors="replace")
        marcas.append(("pie:" + pie_panel(html, aplicar, ruta)))
        html = ruta.read_text(encoding="utf-8", errors="replace")
        marcas.append(("css:" + normalizar_css(html, aplicar, ruta)))

        cambio = False
        for m in marcas:
            resumen[m] = resumen.get(m, 0) + 1
            if m.split(":")[1] in ("insertado", "version-actualizada",
                                   "pie-insertado", "css-actualizado"):
                cambio = True
        if cambio:
            tocados.append(str(rel))

    modo = "DRY-RUN (nada escrito)" if not aplicar else "APLICADO"
    print(f"[{modo}] {sum(v for k, v in resumen.items() if k.startswith('tag:'))} "
          f"páginas HTML · tag v{args.ver} · css v{args.css_ver}")
    for clave in sorted(resumen):
        print(f"  {clave}: {resumen[clave]}")
    if tocados:
        print(f"  {len(tocados)} páginas tocadas · p.ej. " + ", ".join(tocados[:4]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
