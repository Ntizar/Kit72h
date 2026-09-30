#!/usr/bin/env python3
"""Kit72h — auditor SEO diario (cron kit72h-seo-audit, script puro sin LLM).
Determinístico: imprime UNA línea si todo está bien (o silencio), o bullets
con cada problema detectado para que el agente lo repare."""
import json
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

R = Path.home() / "Projects" / "kit72h"   # sin ruta personal en el repo
BASE = "https://kit72h.com"
problemas = []


def existe(rel):
    return (R / rel).exists()


# 1) sitemap: URLs reales y ficheros generados correspondientes
try:
    arbol = ET.parse(R / "sitemap.xml")
    locs = [e.text for e in arbol.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    if any("#" in l for l in locs):
        problemas.append("sitemap con #hash (rutas viejas)")
    if len(locs) < 40:
        problemas.append(f"sitemap solo tiene {len(locs)} urls")
    for l in locs:
        ruta = l.replace(BASE, "").strip("/")
        destino = (R / ruta / "index.html") if ruta else (R / "index.html")
        if not destino.exists():
            problemas.append(f"sitemap apunta a {l} pero no existe {destino.name}")
except Exception as e:
    problemas.append(f"sitemap.xml ilegible: {e}")

# 2) cada pagina generada: canonical + JSON-LD valido
paginas = list((R / "kit").rglob("index.html")) + list((R / "blog").rglob("index.html")) + [R / "fuentes" / "index.html", R / "zona" / "index.html", R / "index.html"]
for f in paginas:
    h = f.read_text(encoding="utf-8")
    if 'rel="canonical"' not in h:
        problemas.append(f"sin canonical: {f.relative_to(R)}")
    for m in re.finditer(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', h, re.S):
        try:
            json.loads(m.group(1).replace("<\\/", "</"))
        except Exception:
            problemas.append(f"JSON-LD roto: {f.relative_to(R)}")

# 3) robots abierto a IA
robots = (R / "robots.txt").read_text(encoding="utf-8")
for bot in ("GPTBot", "ClaudeBot", "PerplexityBot"):
    if f"User-agent: {bot}" not in robots or "Disallow" in robots:
        problemas.append(f"robots.txt no deja claro el acceso de {bot}")

# 4) feed + llms
try:
    ET.parse(R / "feed.xml")
except Exception as e:
    problemas.append(f"feed.xml ilegible: {e}")
if not (R / "llms.txt").exists() or not (R / "llms-full.txt").exists():
    problemas.append("faltan llms.txt o llms-full.txt")
llms = (R / "llms.txt").read_text(encoding="utf-8") if (R / "llms.txt").exists() else ""
if "kit72h.com/blog/" not in llms:
    problemas.append("llms.txt sin URLs /blog/ completas")

# 5) sin datos de autor personal en contenido publicable
veto = R / ".veto-privacidad"
# El veto es un fichero local (gitignored). Cada línea es un patrón regex;
# si no existe, se comprueba al menos el nombre propio con detección literal.
if veto.exists():
    terminos = [t for t in veto.read_text(encoding="utf-8").splitlines() if t.strip()]
else:
    terminos = [re.escape("David Antizar")]
problemas_veto = []
for f in list((R / "data").glob("*.json")) + [R / "index.html"] + list((R / "js").glob("*.js")):
    texto = f.read_text(encoding="utf-8")
    for t in terminos:
        try:
            if re.search(t, texto, re.I):
                problemas_veto.append(f"rastro de dato personal en {f.relative_to(R)}")
                break
        except re.error:
            # patrón inválido en el veto local: no tumba la auditoría entera
            continue
problemas.extend(problemas_veto)

def git(*args, timeout=300):
    return subprocess.run(("git",) + args, cwd=R, capture_output=True, text=True, timeout=timeout)


def desfasadas():
    """Paginas mas antiguas que los datos: el prerender debe salir del mismo run."""
    dm = max((R / "data" / n).stat().st_mtime for n in ("kits.json", "blog.json"))
    dm = min(dm, time.time())  # un fichero con fecha futura no debe envenenar la comparacion
    return [str(f.relative_to(R)) for f in paginas if f.stat().st_mtime < dm - 60]


def autorreparar():
    """Regenera SEO+prerender, los commitea y pushea. True si la web queda al dia.

    Por que AUTORREPARA y no solo avisa: este job detecta un desfase que ya es
    deterministico de arreglar (mismo run de scripts) y el aviso suelto se queda
    en 'hay que arreglarlo' hasta que alguien lo mira. Caso real 2026-09-29: el
    buscador commiteo data/kits.json a las 05:17 sin regenerar el HTML.
    """
    for script in ("scripts/generar-seo.py", "scripts/prerender.py"):
        r = subprocess.run([sys.executable, script], cwd=R, capture_output=True,
                           text=True, timeout=1200)
        if r.returncode != 0:
            print(f"[auto-fix] {script} falló (exit {r.returncode}): "
                  + " | ".join(l for l in (r.stdout or "").splitlines() if l.strip())[-300:])
            return False
    if desfasadas():
        return False
    git("add", "index.html", "sitemap.xml", "feed.xml", "llms.txt", "llms-full.txt",
        "kit", "blog", "fuentes", "zona")
    if git("diff", "--cached", "--quiet").returncode == 0:
        return True  # nada que commitear: el desfase era solo de mtime
    c = git("-c", "user.name=Mastermind", "-c", "user.email=bot@kit72h.local",
            "commit", "-q", "-m", "chore(seo): prerender regenerado por la auditoria diaria")
    if c.returncode != 0:
        print(f"[auto-fix] commit falló: {(c.stderr or '').strip()[:200]}")
        return False
    git("pull", "--rebase", "-q", "origin", "main")
    p = git("push", "-q", "origin", "main")
    if p.returncode != 0:
        print(f"[auto-fix] push falló: {(p.stderr or '').strip()[:200]}")
        return False
    return True


# 6) prerender fresco: los ficheros no deben ser mas antiguos que los datos
viejos = desfasadas()
if len(viejos) > 5:
    if autorreparar():
        print(f"[auto-fix] prerender puesto al dia: {len(viejos)} paginas desfasadas "
              "(ej. " + viejos[0] + ") regeneradas y pusheadas")
    else:
        problemas.append(f"prerender desactualizado: {len(viejos)} paginas mas antiguas que data/ (ej. {viejos[0]}) — el auto-arreglo falló")

if problemas:
    print(f"SEO AUDIT — {len(problemas)} problemas:")
    for p in problemas:
        print(f"- {p}")
    sys.exit(1)
print(f"SEO OK — {len(paginas)} paginas, sitemap {len(locs)} urls, feed+llms+robots correctos")
