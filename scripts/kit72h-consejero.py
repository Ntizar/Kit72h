#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — Consejero de crecimiento (Vía B).

El «cerebro» determinista del cron `kit72h-consejero`. Hace tres cosas:

  --briefing            Lee el estado real de la web y escupe un informe
                        RANKEADO de movimientos de crecimiento (0 tokens LLM).
                        Lo consume el cron LLM, que decide y redacta.
  --log ...             Apunta una decisión en el log para no repetirla en
                        días seguidos.
  --publicar <entrada>  Publica una entrada de blog/comparativa: upsert en
                        blog.json, materializa el directorio, regenera
                        home+SEO, hornea (prerender) y pasa el gate.

El juicio y la redacción van en el cron LLM; aquí solo va lo verificable.
Este script NUNCA hace commit ni push (eso lo decide el cron tras el gate).
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PLAN_DIR = RAIZ / "notes" / "plan-crecimiento"
LOG = PLAN_DIR / "log-decisiones.md"
MAPA = RAIZ / "notes" / "mapa-keywords.md"
HOY = date.today().isoformat()
TAG = "ntizar-21"

MESES_ESTACION = {
    # mes → lista de tokens de escenario estacional
    1: ["nieve", "frio", "frío", "nevada"],
    2: ["nieve", "frio", "frío", "nevada"],
    3: [],
    4: [],
    5: ["calor", "incendio"],
    6: ["calor", "incendio"],
    7: ["calor", "incendio"],
    8: ["calor", "incendio", "dana"],
    9: ["dana", "inundacion", "inundación"],
    10: ["dana", "inundacion", "inundación"],
    11: ["nieve", "frio", "frío", "nevada"],
    12: ["nieve", "frio", "frío", "nevada"],
}


# --------------------------------------------------------------------------- #
# utilidades
# --------------------------------------------------------------------------- #
def leer_json(ruta, por_defecto):
    try:
        return json.loads(Path(ruta).read_text(encoding="utf-8"))
    except Exception:
        return por_defecto


def run(*args, timeout=600):
    return subprocess.run(args, cwd=RAIZ, capture_output=True, text=True, timeout=timeout)


def log_reciente(dias=14):
    """Devuelve la lista de (slug, tipo, estado, nota) del log de decisiones."""
    if not LOG.exists():
        return []
    filas = []
    corte = date.today() - timedelta(days=dias)
    for linea in LOG.read_text(encoding="utf-8").splitlines():
        if not linea.strip().startswith("|"):
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) < 4 or not re.match(r"^\d{4}-\d{2}-\d{2}$", celdas[0]):
            continue
        try:
            f = datetime.strptime(celdas[0], "%Y-%m-%d").date()
        except ValueError:
            continue
        if f >= corte:
            filas.append((celdas[1], celdas[2], celdas[3], celdas[4] if len(celdas) > 4 else ""))
    return filas


# --------------------------------------------------------------------------- #
# lectura del estado
# --------------------------------------------------------------------------- #
def filas_mapa():
    """Extrae las filas de las tablas del mapa de keywords con estado pendiente."""
    if not MAPA.exists():
        return []
    pendientes = []
    for linea in MAPA.read_text(encoding="utf-8").splitlines():
        s = linea.strip()
        if not s.startswith("|"):
            continue
        celdas = [c.strip() for c in s.strip("|").split("|")]
        if len(celdas) < 6 or celdas[0].lower() == "keyword" or set(celdas[0]) <= set("-: "):
            continue
        keyword, volumen, intencion, destino, estado, prioridad = celdas[:6]
        e = estado.lower()
        if e.startswith("✅") and ("cubierto" in e or "hecha" in e):
            continue
        if not (e.startswith("pendiente") or e.startswith("parcial") or e == ""):
            continue
        pendientes.append({
            "keyword": keyword, "volumen": volumen, "intencion": intencion,
            "destino": destino, "estado": estado, "prioridad": prioridad,
        })
    return pendientes


def huecos_catalogo():
    """Cuenta items de kit sin ficha /dp/ (es_busqueda) y blogs sin cuerpo."""
    kits = leer_json(RAIZ / "data" / "kits.json", {"kits": []})
    sin_asin = 0
    for k in kits.get("kits", []):
        for sec in k.get("secciones", []):
            for it in sec.get("items", []):
                if it.get("es_busqueda") or "/dp/" not in (it.get("afiliado") or ""):
                    sin_asin += 1
    blog = leer_json(RAIZ / "data" / "blog.json", {"entradas": []})
    sin_cuerpo = [x["slug"] for x in blog.get("entradas", [])
                  if not isinstance(x.get("cuerpo"), str)]
    return sin_asin, sin_cuerpo


def ultimos_commits(n=12):
    r = run("git", "log", "--oneline", "-n", str(n))
    return r.stdout.strip().splitlines() if r.returncode == 0 else []


# --------------------------------------------------------------------------- #
# scoring
# --------------------------------------------------------------------------- #
def _factor_volumen(vol):
    v = vol.lower()
    if v.startswith("alto"):
        return 1.4
    if v.startswith("media"):
        return 1.0
    if v.startswith("baja"):
        return 0.7
    return 0.9


def _factor_intencion(intencion):
    i = intencion.lower()
    if i == "compra":
        return 1.5
    if "compra" in i:          # info→compra
        return 1.35
    if i == "info":
        return 1.0
    return 1.1


def _factor_prioridad(p):
    p = p.upper()
    if p.startswith("P1"):
        return 100.0
    if p.startswith("P2"):
        return 60.0
    if p.startswith("P3"):
        return 30.0
    return 40.0


def _factor_estacional(volumen, keyword):
    tokens = MESES_ESTACION.get(date.today().month, [])
    k = keyword.lower()
    toca = any(t in k for t in tokens)
    if "estacional" in volumen.lower():
        return 1.35 if toca else 0.75
    return 1.15 if toca else 1.0


def _factor_novedad(texto, recientes):
    t = texto.lower()
    for slug, tipo, estado, nota in recientes:
        if slug and slug.lower() in t:
            return 0.15 if estado == "ejecutado" else 0.45
    return 1.0


def tipo_de_destino(destino, keyword):
    d = destino.lower()
    k = keyword.lower()
    if "banner" in d:
        return ("banner", "solo borrador", False)
    if "/kit/" in d:
        return ("ficha-kit", "mejorar ficha de kit", False)
    if "/blog/" in d or "blog pendiente" in d or "post" in d:
        if k.startswith("mejor") or "comparativa" in k or " vs " in k or "top " in k:
            return ("comparativa", "blog comparativa «mejor X»", True)
        return ("guia", "blog guía informativa", True)
    if d.startswith("/"):
        return ("mejora-pagina", "mejorar página existente", False)
    return ("otro", "revisar", False)


def construir_candidatos():
    recientes = log_reciente()
    cands = []
    for fila in filas_mapa():
        tipo, desc_tipo, ejecutable = tipo_de_destino(fila["destino"], fila["keyword"])
        score = (_factor_prioridad(fila["prioridad"])
                 * _factor_intencion(fila["intencion"])
                 * _factor_volumen(fila["volumen"])
                 * _factor_estacional(fila["volumen"], fila["keyword"])
                 * _factor_novedad(fila["keyword"], recientes))
        cands.append({
            "titulo": fila["keyword"], "tipo": tipo, "desc_tipo": desc_tipo,
            "ejecutable": ejecutable, "score": round(score, 1),
            "fuente": "mapa-keywords", "destino": fila["destino"],
            "prioridad": fila["prioridad"], "intencion": fila["intencion"],
            "volumen": fila["volumen"], "estado": fila["estado"],
        })
    # señales derivadas (siempre solo-borrador: las cubren otros crons)
    sin_asin, sin_cuerpo = huecos_catalogo()
    if sin_cuerpo:
        cands.append({"titulo": f"Reparar {len(sin_cuerpo)} entradas de blog sin cuerpo",
                      "tipo": "fix-contenido", "desc_tipo": "blog.json con cuerpo None",
                      "ejecutable": False, "score": 45.0, "fuente": "derivado",
                      "destino": ",".join(sin_cuerpo[:5]), "prioridad": "P2",
                      "intencion": "compra", "volumen": "media",
                      "estado": "pendiente"})
    if sin_asin:
        cands.append({"titulo": f"Terminar fichas de producto pendientes ({sin_asin} items sin /dp/)",
                      "tipo": "asins", "desc_tipo": "los cubre el cron buscador (05:15)",
                      "ejecutable": False, "score": 40.0, "fuente": "derivado",
                      "destino": "data/kits.json", "prioridad": "P2",
                      "intencion": "compra", "volumen": "media",
                      "estado": "pendiente"})
    cands.sort(key=lambda c: c["score"], reverse=True)
    return cands, recientes


# --------------------------------------------------------------------------- #
# briefing
# --------------------------------------------------------------------------- #
def briefing():
    cands, recientes = construir_candidatos()
    mes = date.today().month
    est = MESES_ESTACION.get(mes, [])
    print("# Briefing del consejero — %s" % HOY)
    print()
    print("- Mes %d · escenario estacional que toca: %s" % (mes, ", ".join(est) or "ninguno"))
    print("- Candidatos: %d (ejecutables por el consejero: %d)"
          % (len(cands), sum(1 for c in cands if c["ejecutable"])))
    print()
    print("## Candidatos rankeados")
    print()
    print("| # | Score | Tipo | Ejecutable | Título / keyword | Destino | Prioridad |")
    print("|---|---|---|---|---|---|---|")
    for i, c in enumerate(cands[:15], 1):
        print("| %d | %.1f | %s | %s | %s | %s | %s |" % (
            i, c["score"], c["tipo"], "sí" if c["ejecutable"] else "no",
            c["titulo"], c["destino"], c["prioridad"]))
    print()
    print("## Decisiones recientes (últimos 14 días, para NO repetir)")
    print()
    if recientes:
        for slug, tipo, estado, nota in recientes[-12:]:
            print("- %s · %s · %s · %s" % (slug, tipo, estado, nota[:90]))
    else:
        print("- (log vacío: primera decisión)")
    print()
    print("## Estado de la web")
    sin_asin, sin_cuerpo = huecos_catalogo()
    print("- Items de kit sin ficha /dp/: %d" % sin_asin)
    print("- Entradas de blog sin cuerpo: %d %s"
          % (len(sin_cuerpo), ("→ " + ", ".join(sin_cuerpo[:6])) if sin_cuerpo else ""))
    print("- Últimos commits:")
    for l in ultimos_commits(8):
        print("  - " + l)


# --------------------------------------------------------------------------- #
# log
# --------------------------------------------------------------------------- #
def apuntar_log(slug, tipo, estado, nota):
    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG.exists():
        LOG.write_text(
            "# Log de decisiones del consejero (kit72h)\n\n"
            "> Una fila por movimiento propuesto/ejecutado. El briefing lee los\n"
            "> últimos 14 días para no repetir el mismo play en días seguidos.\n\n"
            "| Fecha | Slug/Keyword | Tipo | Estado | Nota |\n"
            "|---|---|---|---|---|\n",
            encoding="utf-8")
    linea = "| %s | %s | %s | %s | %s |\n" % (HOY, slug, tipo, estado, nota.replace("|", "/")[:160])
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(linea)
    print("log: %s" % linea.strip())


# --------------------------------------------------------------------------- #
# publicar
# --------------------------------------------------------------------------- #
def _marcar_keyword_hecha(keyword):
    """Marca la fila del mapa como hecha (best-effort)."""
    if not MAPA.exists() or not keyword:
        return
    txt = MAPA.read_text(encoding="utf-8")
    lineas = txt.splitlines()
    for i, l in enumerate(lineas):
        if l.strip().startswith("|") and keyword.lower() in l.lower():
            celdas = l.split("|")
            if len(celdas) >= 6:
                celdas[5] = " ✅ hecha (%s) " % HOY
                lineas[i] = "|".join(celdas)
                break
    else:
        return
    MAPA.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("mapa: fila «%s» marcada hecha" % keyword)


def _cmd_prerender():
    """Horneado: en el VM el CLI de Chrome cuelga, así que preferimos Playwright
    (venv ~/.mastermind/venv). Si no hay venv/playwright, caemos al CLI."""
    venv = Path.home() / ".mastermind" / "venv" / "bin" / "python"
    if venv.exists():
        return [str(venv), "scripts/prerender_playwright.py"]
    return ["python3", "scripts/prerender.py"]


def publicar(ruta_json):
    entrada = json.loads(Path(ruta_json).read_text(encoding="utf-8"))
    slug = entrada.get("slug", "").strip()
    if not re.match(r"^[a-z0-9][a-z0-9-]{2,80}$", slug):
        print("FALLIDO: slug inválido «%s»" % slug)
        return 1
    cuerpo = entrada.get("cuerpo") or ""
    if len(cuerpo) < 800 or "<p>" not in cuerpo or "<h2>" not in cuerpo:
        print("FALLIDO: cuerpo demasiado corto o sin estructura (<p>/<h2>)")
        return 1
    if ("amazon.es" in cuerpo) and ("tag=%s" % TAG) not in cuerpo:
        print("FALLIDO: hay enlaces de Amazon sin tag=%s" % TAG)
        return 1

    palabras = len(re.sub(r"<[^>]+>", " ", cuerpo).split())
    entrada["fecha"] = entrada.get("fecha") or HOY
    entrada["lectura"] = "%d min" % max(3, round(palabras / 200))
    entrada["autor"] = "Redacción Kit72h"
    entrada.setdefault("kits_relacionados", [])
    entrada.setdefault("etiquetas", [])

    ruta_blog = RAIZ / "data" / "blog.json"
    blog = json.loads(ruta_blog.read_text(encoding="utf-8"))
    entradas = [e for e in blog["entradas"] if e.get("slug") != slug]
    entradas.append(entrada)
    entradas.sort(key=lambda e: (e.get("fecha", ""), e.get("slug", "")), reverse=True)
    blog["entradas"] = entradas
    blog.setdefault("meta", {})
    blog["meta"]["total"] = len(entradas)
    blog["meta"]["ultima_revision"] = HOY
    with open(ruta_blog, "w", encoding="utf-8", newline="\r\n") as f:
        json.dump(blog, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("blog.json: entrada «%s» insertada (%d palabras, %d entradas)"
          % (slug, palabras, len(entradas)))

    # materializar el directorio (prerender lo sobrescribe entero)
    destino = RAIZ / "blog" / slug
    destino.mkdir(parents=True, exist_ok=True)
    if not (destino / "index.html").exists():
        plantilla = next((d / "index.html" for d in (RAIZ / "blog").iterdir()
                          if d.is_dir() and d.name != slug and (d / "index.html").exists()), None)
        if plantilla:
            (destino / "index.html").write_text(plantilla.read_text(encoding="utf-8"),
                                                encoding="utf-8")
            print("materializado blog/%s/index.html (copia de plantilla)" % slug)

    pasos = [
        ("generar-blog-home", ["python3", "scripts/generar-blog-home.py"]),
        ("generar-seo", ["python3", "scripts/generar-seo.py"]),
        ("prerender", _cmd_prerender()),
    ]
    for nombre, cmd in pasos:
        r = run(*cmd, timeout=900)
        if r.returncode != 0:
            cola = (r.stdout or r.stderr or "").strip().splitlines()[-3:]
            print("FALLIDO en %s (rc=%d): %s" % (nombre, r.returncode, " | ".join(cola)))
            return 1
        print("ok: %s" % nombre)

    _marcar_keyword_hecha(entrada.get("_keyword") or "")

    gate = run("python3", "scripts/verificar-sitio.py", timeout=300)
    if gate.returncode != 0:
        cola = (gate.stdout or gate.stderr or "").strip().splitlines()[-6:]
        print("FALLIDO en gate (rc=%d):\n%s" % (gate.returncode, "\n".join(cola)))
        return 1
    print("ok: gate verificar-sitio.py ✅")
    print("PUBLICADO: /blog/%s/ (listo para commit+push)" % slug)
    return 0


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description="Consejero de crecimiento kit72h")
    ap.add_argument("--briefing", action="store_true", help="informe rankeado (por defecto)")
    ap.add_argument("--log", action="store_true", help="apuntar decisión en el log")
    ap.add_argument("--publicar", metavar="ENTRADA.json", help="publicar una entrada de blog")
    ap.add_argument("--slug", default="", help="slug/keyword para --log")
    ap.add_argument("--tipo", default="", help="tipo para --log")
    ap.add_argument("--estado", default="propuesto", help="estado para --log")
    ap.add_argument("--nota", default="", help="nota para --log")
    args = ap.parse_args()

    if args.publicar:
        return publicar(args.publicar)
    if args.log:
        apuntar_log(args.slug, args.tipo, args.estado, args.nota)
        return 0
    briefing()
    return 0


if __name__ == "__main__":
    sys.exit(main())
