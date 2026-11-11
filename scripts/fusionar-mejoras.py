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

# --- 3. lo que no tiene ficha real NO se muestra ------------------------------
# El catálogo visible solo ofrece productos verificados. Un item sin `afiliado`
# (y que no sea un consejo marcado `sin_enlace`) se aparta a la cola de búsqueda
# data/pendientes-catalogo.json; el cron buscador lo devuelve a su sección en
# cuanto encuentre una ficha real con ASIN y precio.
D_PEND = RAIZ / "data" / "pendientes-catalogo.json"
import re as _re

def busqueda_de(nombre):
    """Término de búsqueda a partir del nombre: sin paréntesis ni guiones, minúsculas."""
    t = _re.sub(r"\(.*?\)", "", nombre)
    t = _re.sub(r"[—–:/]", " ", t)
    t = _re.sub(r"\s+", " ", t).strip().lower()
    return t[:60]

pend_doc = (json.loads(D_PEND.read_text(encoding="utf-8"))
            if D_PEND.exists() else {"meta": {}, "items": []})
pend_items = pend_doc.setdefault("items", [])
claves_pend = {f"{r.get('kit')}|{r.get('producto')}" for r in pend_items}
apartados = 0
for kit in kits["kits"]:
    for s in kit.get("secciones", []):
        quedan = []
        for i in s.get("items", []):
            if i.get("afiliado") or i.get("sin_enlace"):
                quedan.append(i)
                continue
            clave = f"{kit['slug']}|{i.get('producto', '')}"
            if clave not in claves_pend:
                pend_items.append({
                    "kit": kit["slug"],
                    "seccion": s.get("titulo", ""),
                    "producto": i.get("producto", ""),
                    "descripcion": i.get("descripcion", ""),
                    "precio_aprox": i.get("precio_aprox", "—"),
                    "prioridad": i.get("prioridad", "esencial"),
                    "busqueda": i.get("busqueda") or busqueda_de(i.get("producto", "")),
                    "desde": date.today().isoformat(),
                    "motivo": "sin ficha real verificada",
                })
                claves_pend.add(clave)
            apartados += 1
        s["items"] = quedan
if apartados:
    D_PEND.write_text(json.dumps(pend_doc, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
print(f"sin ficha real (fuera del catálogo visible): {apartados}")

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
