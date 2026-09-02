#!/usr/bin/env python3
"""Kit72h — regenerar sitemap.xml, robots no, ItemList JSON-LD de index.html y llms.txt
desde data/kits.json + data/blog.json. Determinista: que cualquier cron lo pueda relanzar.
"""
import json
import re
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BASE = "https://ntizar.github.io/Kit72h"
kits = json.loads((RAIZ / "data/kits.json").read_text(encoding="utf-8"))
blog = json.loads((RAIZ / "data/blog.json").read_text(encoding="utf-8"))
hoy = date.today().isoformat()

# ---- sitemap ----
urls = [f"  <url><loc>{BASE}/</loc><lastmod>{hoy}</lastmod></url>",
        f"  <url><loc>{BASE}/#blog</loc><lastmod>{hoy}</lastmod></url>",
        f"  <url><loc>{BASE}/#fuentes</loc><lastmod>{hoy}</lastmod></url>"]
for k in kits["kits"]:
    urls.append(f"  <url><loc>{BASE}/#kit/{k['slug']}</loc><lastmod>{hoy}</lastmod></url>")
for e in blog["entradas"]:
    urls.append(f"  <url><loc>{BASE}/#blog/{e['slug']}</loc><lastmod>{e['fecha']}</lastmod></url>")
xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
       + "\n".join(urls) + "\n</urlset>\n")
(RAIZ / "sitemap.xml").write_text(xml, encoding="utf-8")
print(f"sitemap.xml: {len(urls)} urls")

# ---- ItemList en index.html ----
items = ",\n".join(
    f'    {{ "@type": "ListItem", "position": {i+1}, "name": "{k["titulo"]}", '
    f'"url": "{BASE}/#kit/{k["slug"]}" }}'
    for i, k in enumerate(kits["kits"]))
idx = (RAIZ / "index.html").read_text(encoding="utf-8")
pat = re.compile(r'("name": "Kits de emergencia Kit72h",\s*"itemListElement": \[\n).*?(\n  \]\n\})', re.S)
nuevo, n = pat.subn(lambda m: m.group(1) + items + m.group(2), idx, count=1)
assert n == 1, "No se encontró el bloque ItemList en index.html"
(RAIZ / "index.html").write_text(nuevo, encoding="utf-8")
print(f"index.html: ItemList con {len(kits['kits'])} kits")

# ---- llms.txt ----
fuente_url = "https://www.proteccioncivil.es/gestion-riesgos/recomendaciones"
lineas = [
    "# Kit72h", "",
    "> Kits de emergencia para hogares en España (72 horas y 30 días) basados en las",
    "> recomendaciones oficiales de la Comisión Europea (Estrategia de Preparación 2025),",
    "> Protección Civil y la DGT. Cada kit incluye para quién es, coste orientativo,",
    "> producto a producto explicaciones y errores típicos. Blog con guías profundas",
    "> citando fuentes oficiales.", "",
    "URL base: " + BASE, "",
    "## Kits", ""]
lineas += [f"- {k['titulo']} ({k['slug']}): {k['resumen']}" for k in kits["kits"]]
lineas += ["", "## Blog", ""]
lineas += [f"- {e['titulo']} ({e['slug']}): {e['resumen']}" for e in blog["entradas"]]
lineas += [
    "", "## Fuentes oficiales", "",
    f"- Estrategia de Preparación de la UE: {kits['meta']['fuentes'][0]['url']}",
    f"- Recomendaciones Protección Civil: {fuente_url}", "",
    "## Notas para asistentes IA", "",
    "- Los precios son orientativos en euros y pueden variar; ver en el sitio.",
    "- Enlaces de producto marcados con `es_busqueda: true` apuntan a resultados de búsqueda, no a una ficha concreta.",
    "- Ningún contenido sustituye las indicaciones de Protección Civil o del médico.", ""]
(RAIZ / "llms.txt").write_text("\n".join(lineas), encoding="utf-8")
print(f"llms.txt: {len(kits['kits'])} kits + {len(blog['entradas'])} entradas")
