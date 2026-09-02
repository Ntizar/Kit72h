#!/usr/bin/env python3
"""Kit72h — migrar las entradas del blog de js/blog.js a data/blog.json.

El blog deja de estar hardcodeado en JS para vivir en data/blog.json:
así el cron nocturno puede añadir entradas sin tocar código.
Preserva cuerpo HTML, fecha, lectura y resumen; añade campos nuevos:
  - autor, fuente (procedencia del contenido), kits_relacionados (derivado
    de los enlaces #kit/... del propio cuerpo), etiquetas.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "js" / "blog.js"
DST = RAIZ / "data" / "blog.json"

src = SRC.read_text(encoding="utf-8")

# Cada entrada: bloque entre "    {" y "    }," dentro de entradas: [ ... ]
trozo = src[src.index("entradas: ["):]
bloques = re.findall(r"\{\s*(slug:.*?)\n    \}", trozo, re.S)
print(f"Bloques encontrados: {len(bloques)}")

entradas = []
for b in bloques:
    def campo(nombre):
        m = re.search(rf"{nombre}:\s*'((?:[^'\\]|\\.)*)'", b, re.S)
        return m.group(1) if m else None

    cuerpo = campo("cuerpo")
    if cuerpo is None:
        # el cuerpo va en template literal `...`
        m = re.search(r"cuerpo:\s*`(.*?)`\s*$", b, re.S)
        if not m:
            m = re.search(r"cuerpo:\s*`(.*?)`", b, re.S)
        cuerpo = m.group(1) if m else ""
    cuerpo = cuerpo.strip()

    e = {
        "slug": campo("slug"),
        "titulo": campo("titulo"),
        "fecha": campo("fecha"),
        "lectura": campo("lectura"),
        "resumen": campo("resumen"),
        "autor": "David Antizar",
        "cuerpo": cuerpo,
        "kits_relacionados": sorted(set(re.findall(r'#kit/([a-z0-9\-]+)', cuerpo))),
        "etiquetas": [],
    }
    entradas.append(e)

# Etiquetas derivadas del tema (reglas simples, sin IA: determinista y gratuito)
REGLAS = {
    "agua": ["agua", "potabiliz", "hidrat"],
    "comida": ["comida", "despensa", "conserva", "aliment", "semilla", "germinad", "huerto"],
    "salud": ["botiquín", "medic", "temperatura", "hipoterm", "golpe de calor", "salud"],
    "documentos": ["documento", "carpeta", "papeles", "dinero", "efectivo"],
    "familia": ["mascota", "familia", "niños", "hogar"],
    "escenarios": ["dana", "apagón", "montaña", "coche", "evacu", "calor", "inundación"],
    "comunicación": ["comunicar", "radio", "red móvil", "recursos oficiales"],
    "comparativas": ["kit 72h", "30 días", "cuál necesitas"],
}
for e in entradas:
    txt = (e["titulo"] + " " + e["resumen"] + " " + e["cuerpo"]).lower()
    e["etiquetas"] = [t for t, kws in REGLAS.items() if any(k in txt for k in kws)] or ["preparación"]

salida = {
    "meta": {
        "sitio": "Kit72h — Blog de preparación",
        "descripcion": "Guías prácticas de preparación ante emergencias basadas en fuentes oficiales (UE, Protección Civil, DGT, OMS).",
        "reglas_editoriales": (
            "Toda entrada se basa en fuentes oficiales citadas con enlace y fecha. "
            "No se inventan datos ni se recomienda medicación concreta: se remite a "
            "Protección Civil, AEMPS o al médico. Se añade o corrige, nunca se borra "
            "contenido existente sin dejar nota. Cada entrada enlaza con los kits que la "
            "completan y con al menos dos fuentes oficiales."
        ),
        "actualizado": max(e["fecha"] for e in entradas),
    },
    "entradas": sorted(entradas, key=lambda x: x["fecha"], reverse=True),
}

DST.write_text(json.dumps(salida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Escrito {DST} con {len(entradas)} entradas")
for e in salida["entradas"]:
    print(f"  {e['fecha']} {e['slug']:42s} kits={e['kits_relacionados']} tags={e['etiquetas']}")
if len(entradas) < 16:
    sys.exit("ATENCION: menos de 16 entradas migradas, revisar el parseo")
