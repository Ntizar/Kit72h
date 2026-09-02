#!/usr/bin/env python3
"""Kit72h — fusionar mejoras de contenido y kits nuevos en data/kits.json.

Fuentes de entrada (todas en data/, todas opcionales):
  - mejora-kits.json : paraQuien / paraQuien_no / coste_total / errores /
                       secciones_intro para los kits ya existentes
  - kits-nuevos.json : array de kits completos a añadir (no pisa ids existentes)

Reglas: solo AÑADE o ENRIQUECE, nunca borra ni reordena. Idempotente.
Al final refresca meta.ultima_revision y escribe un resumen por stdout.
"""
import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
D_KITS = RAIZ / "data" / "kits.json"
D_MEJORA = RAIZ / "data" / "mejora-kits.json"
D_NUEVOS = RAIZ / "data" / "kits-nuevos.json"

kits = json.loads(D_KITS.read_text(encoding="utf-8"))
cambios = []

# --- 1. enriquecer kits existentes -------------------------------------------
if D_MEJORA.exists():
    mejs = json.loads(D_MEJORA.read_text(encoding="utf-8")).get("mejoras", {})
    for kit in kits["kits"]:
        m = mejs.get(kit["id"])
        if not m:
            continue
        for campo in ("paraQuien", "paraQuien_no", "coste_total", "errores"):
            if m.get(campo) and not kit.get(campo):
                kit[campo] = m[campo]
                cambios.append(f"{kit['id']}.{campo}")
        intros = m.get("secciones_intro", {})
        for s in kit.get("secciones", []):
            if not s.get("intro") and intros.get(s["titulo"]):
                s["intro"] = intros[s["titulo"]]
                cambios.append(f"{kit['id']}:{s['titulo']}.intro")

# --- 2. añadir kits nuevos ----------------------------------------------------
if D_NUEVOS.exists():
    nuevos = json.loads(D_NUEVOS.read_text(encoding="utf-8")).get("kits", [])
    existentes = {k["id"] for k in kits["kits"]}
    slugs = {k["slug"] for k in kits["kits"]}
    for nk in nuevos:
        if nk.get("id") in existentes:
            print(f"  omitido (ya existe id): {nk.get('id')}")
            continue
        if nk.get("slug") in slugs:
            print(f"  omitido (slug duplicado): {nk.get('slug')}")
            continue
        kits["kits"].append(nk)
        cambios.append(f"kit nuevo {nk['id']}")

# --- 3. enlaces de búsqueda para items sin ficha resuelta ---------------------
# Un item con afiliado=null se beneficia ya de un enlace de búsqueda con el tag
# de afiliado: dirige a resultados reales de amazon.es y el cron buscador lo
# sustituirá por la ficha concreta cuando esté verificada.
TAG = "nti0c8-21"
from urllib.parse import quote_plus
import re as _re

def busqueda_de(nombre):
    """Término de búsqueda a partir del nombre: sin paréntesis ni guiones, minúsculas."""
    t = _re.sub(r"\(.*?\)", "", nombre)
    t = _re.sub(r"[—–:/]", " ", t)
    t = _re.sub(r"\s+", " ", t).strip().lower()
    return t[:60]

sin_enlace = 0
for kit in kits["kits"]:
    for s in kit.get("secciones", []):
        for i in s.get("items", []):
            if not i.get("afiliado"):
                q = i.get("busqueda") or busqueda_de(i.get("producto", ""))
                i["busqueda"] = q
                i["afiliado"] = f"https://www.amazon.es/s?k={quote_plus(q)}&tag={TAG}"
                i["es_busqueda"] = True
                sin_enlace += 1

# --- 4. meta -----------------------------------------------------------------
n_items = sum(len(s["items"]) for k in kits["kits"] for s in k["secciones"])
con_enlace = sum(1 for k in kits["kits"] for s in k["secciones"]
                 for i in s["items"] if i.get("afiliado"))
kits["meta"]["ultima_revision"] = date.today().isoformat()
kits["meta"]["nota_revision"] = (
    f"{date.today().isoformat()}: enriquecimiento editorial — los 12 kits llevan "
    "para quién es (y para quién no), coste orientativo, errores típicos e intro "
    f"por sección. Nuevos kits bebé y persona mayor. {n_items} productos, "
    f"{con_enlace} con enlace."
)

D_KITS.write_text(json.dumps(kits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"kits: {len(kits['kits'])} | productos: {n_items} | con enlace: {con_enlace}")
print(f"cambios aplicados: {len(cambios)}")
for c in cambios:
    print("  ·", c)
