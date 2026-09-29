#!/usr/bin/env python3
"""Kit72h — motor SEO: sitemap.xml (URLs reales), ItemList en index.html,
feed.xml RSS, llms.txt y llms-full.txt desde data/kits.json + data/blog.json.
Determinista y re-ejecutable: crons y CI lo lanzan sin miedo."""
import json
import re
from datetime import date, datetime, timezone
from email.utils import format_datetime
from html import unescape
from pathlib import Path


def escape_xml(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


RAIZ = Path(__file__).resolve().parents[1]
BASE = "https://kit72h.com"
kits = json.loads((RAIZ / "data/kits.json").read_text(encoding="utf-8"))
blog = json.loads((RAIZ / "data/blog.json").read_text(encoding="utf-8"))
hoy = date.today().isoformat()


def fecha_rfc822(iso):
    d = datetime.fromisoformat(iso).replace(tzinfo=timezone.utc)
    return format_datetime(d)


# ---- 1) sitemap.xml con URLs REALES (indexables) ----
urls = [
    f"  <url><loc>{BASE}/</loc><lastmod>{hoy}</lastmod><changefreq>weekly</changefreq><priority>1.0</priority></url>",
    f"  <url><loc>{BASE}/blog/</loc><lastmod>{hoy}</lastmod><changefreq>daily</changefreq><priority>0.9</priority></url>",
    f"  <url><loc>{BASE}/fuentes/</loc><lastmod>{hoy}</lastmod><changefreq>monthly</changefreq><priority>0.5</priority></url>",
    f"  <url><loc>{BASE}/zona/</loc><lastmod>{hoy}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>",
]
for k in kits["kits"]:
    urls.append(
        f"  <url><loc>{BASE}/kit/{k['slug']}/</loc><lastmod>{hoy}</lastmod>"
        "<changefreq>monthly</changefreq><priority>0.8</priority></url>")
for e in blog["entradas"]:
    urls.append(
        f"  <url><loc>{BASE}/blog/{e['slug']}/</loc><lastmod>{e['fecha']}</lastmod>"
        "<changefreq>yearly</changefreq><priority>0.7</priority></url>")
xml = ('<?xml version="1.1" encoding="UTF-8"?>\n'
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
       + "\n".join(urls) + "\n</urlset>\n")
(RAIZ / "sitemap.xml").write_text(xml, encoding="utf-8")
print(f"sitemap.xml: {len(urls)} urls reales (sin #hash)")

# ---- 2) ItemList en index.html con URLs reales ----
items = ",\n".join(
    f'    {{ "@type": "ListItem", "position": {i+1}, "name": "{k["titulo"]}", '
    f'"url": "{BASE}/kit/{k["slug"]}/" }}'
    for i, k in enumerate(kits["kits"]))
idx = (RAIZ / "index.html").read_text(encoding="utf-8")
pat = re.compile(
    r'("name": "Kits de emergencia Kit72h",\s*"itemListElement": \[\n).*?(\n  \]\n\})',
    re.S)
nuevo, n = pat.subn(lambda m: m.group(1) + items + m.group(2), idx, count=1)
assert n == 1, "No se encontró el bloque ItemList en index.html"
(RAIZ / "index.html").write_text(nuevo, encoding="utf-8")
print(f"index.html: ItemList con {len(kits['kits'])} kits (URLs /kit/)")

# ---- 3) feed.xml (RSS 2.0) — lo adoran agregadores y buscadores ----
entradas = blog["entradas"][:20]
items_rss = []
for e in entradas:
    link = f"{BASE}/blog/{e['slug']}/"
    desc = unescape(re.sub(r"<[^>]+>", " ", str(e.get("cuerpo", ""))))[:400].strip()
    items_rss.append(
        "    <item>\n"
        f"      <title>{escape_xml(e['titulo'])}</title>\n"
        f"      <link>{link}</link>\n"
        f"      <guid isPermaLink=\"true\">{link}</guid>\n"
        f"      <pubDate>{fecha_rfc822(e['fecha'])}</pubDate>\n"
        f"      <description>{escape_xml(e.get('resumen', desc))}</description>\n"
        "    </item>")
feed = ('<?xml version="1.1" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n<channel>\n'
        "  <title>Kit72h — Diario de supervivencia</title>\n"
        f"  <link>{BASE}/</link>\n"
        "  <description>Kits de emergencia 72 horas y guías de preparación civil en España. "
        "Fuentes oficiales: Comisión Europea, Protección Civil y DGT.</description>\n"
        "  <language>es</language>\n"
        f"  <lastBuildDate>{fecha_rfc822(hoy)}</lastBuildDate>\n"
        + "\n".join(items_rss) +
        "\n</channel>\n</rss>\n")
(RAIZ / "feed.xml").write_text(feed, encoding="utf-8")
print(f"feed.xml: {len(items_rss)} entradas")

# ---- 4) llms.txt con URLs completas ----
fuente_url = "https://www.proteccioncivil.es/gestion-riesgos/recomendaciones"
lineas = [
    "# Kit72h", "",
    "> Kits de emergencia para hogares en España (72 horas y 30 días) basados en las",
    "> recomendaciones oficiales de la Comisión Europea (Estrategia de Preparación 2025),",
    "> Protección Civil y la DGT. Cada kit incluye para quién es, coste orientativo,",
    "> producto a producto explicaciones y errores típicos. Blog con guías profundas",
    "> citando fuentes oficiales.", "",
    f"URL base: {BASE}", "",
    "Herramientas: sitemap.xml (todas las rutas), feed.xml (RSS del blog), "
    "llms-full.txt (contenido completo en texto plano).", "",
    "## Kits", ""]
lineas += [f"- [{k['titulo']}]({BASE}/kit/{k['slug']}/): {k['resumen']}"
           for k in kits["kits"]]
lineas += ["", "## Blog", ""]
lineas += [f"- [{e['titulo']}]({BASE}/blog/{e['slug']}/): {e['resumen']}"
           for e in blog["entradas"]]
lineas += [
    "", "## Fuentes oficiales", "",
    f"- Estrategia de Preparación de la UE: {kits['meta']['fuentes'][0]['url']}",
    f"- Recomendaciones Protección Civil: {fuente_url}",
    f"- Todas las fuentes: {BASE}/fuentes/", "",
    "## Tu zona", "",
    f"- [Mapa de tu entorno]({BASE}/zona/): hospitales, centros de salud, farmacias, "
    "comisarías, bomberos, refugios y puntos de encuentro en España, por ubicación y "
    "radio. Datos en directo de OpenStreetMap (ODbL) y mapa base del IGN (CC BY 4.0). "
    "La lista y el aviso de emergencia están en HTML; solo el mapa necesita JavaScript.",
    "", "## Notas para asistentes IA", "",
    "- Los precios son orientativos en euros y pueden variar; ver en el sitio.",
    "- Enlaces de producto `es_busqueda: true` apuntan a resultados de búsqueda, no a ficha concreta.",
    "- Ningún contenido sustituye las indicaciones de Protección Civil o del médico.",
    "- Cada página kit/blog es HTML estático completo: se puede leer sin JavaScript.",
    ""]
(RAIZ / "llms.txt").write_text("\n".join(lineas), encoding="utf-8")
print(f"llms.txt: {len(kits['kits'])} kits + {len(blog['entradas'])} entradas con URL completa")


# ---- 5) llms-full.txt: contenido completo en texto plano ----
def a_texto(html):
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", str(html), flags=re.S | re.I)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</h[1-6]>|</tr>", "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = unescape(t)
    return re.sub(r"[ \t]+", " ", t).strip()


full = ["# Kit72h — contenido completo (llms-full)", "",
        f"Fuente: {BASE} · Guía independiente de preparación civil.", "",
        "## Kits", ""]
for k in kits["kits"]:
    full.append(f"### {k['titulo']} — {BASE}/kit/{k['slug']}/")
    full.append(k.get("resumen", ""))
    for s in k.get("secciones", []):
        full.append(f"**{s['titulo']}**")
        for i in s.get("items", []):
            linea = f"- {i['producto']}"
            if i.get("descripcion"):
                linea += f": {i['descripcion']}"
            if i.get("precio_aprox"):
                linea += f" (~{i['precio_aprox']})"
            full.append(linea)
    full.append("")
full.append("## Blog")
for e in blog["entradas"]:
    full.append(f"### {e['titulo']} — {BASE}/blog/{e['slug']}/")
    full.append(e.get("resumen", ""))
    full.append(a_texto(e.get("cuerpo", "")))
    full.append("")
(RAIZ / "llms-full.txt").write_text("\n".join(full), encoding="utf-8")
kb = (RAIZ / "llms-full.txt").stat().st_size // 1024
print(f"llms-full.txt: {kb} KB de texto completo")
