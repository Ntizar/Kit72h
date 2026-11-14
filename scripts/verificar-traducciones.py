#!/usr/bin/env python3
"""Kit72h — verificación de traducciones.

Comprueba que cada overlay de idioma encaja con el castellano y que no hay
castellano disfrazado de traducción:

  1. Estructura: mismo número de kits, secciones e items que data/kits.json.
     Si no cuadra, el merge por índice pintaría textos de otra sección.
  2. Cadenas sin traducir: una frase larga idéntica al original es un fallo del
     traductor (o un lote perdido), no una traducción.
  3. Marcadores y etiquetas: {n}, {pais}, {num}, <a>, <b>... siguen ahí.
  4. Cobertura: % de entradas de blog traducidas por idioma.

Uso: python scripts/verificar-traducciones.py [--estricto]
  --estricto  devuelve 1 si queda cualquier cadena sin traducir (para el cron).
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
IDIOMAS = ["en", "de", "fr", "it", "nl"]
ETIQUETA = re.compile(r"</?(a|b|i|br|strong|em|p|ul|ol|li|span|small)\b", re.I)
MARCADOR = re.compile(r"\{[a-z]+\}")
LETRAS = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]")

errores: list[str] = []
avisos: list[str] = []


def leer(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def igual_estructura(src, dst) -> bool:
    return (Counter(x.lower() for x in ETIQUETA.findall(src)) ==
            Counter(x.lower() for x in ETIQUETA.findall(dst)) and
            sorted(MARCADOR.findall(src)) == sorted(MARCADOR.findall(dst)))


def sin_traducir(src, dst) -> bool:
    """Frase larga idéntica al castellano = no se tradujo."""
    return bool(src and dst and len(src) > 25 and LETRAS.search(src) and src.strip() == dst.strip())


def main() -> int:
    kits = leer(RAIZ / "data/kits.json")
    blog = leer(RAIZ / "data/blog.json")
    estricto = "--estricto" in sys.argv

    print("═" * 62)
    print("  TRADUCCIONES — kit72h")
    print("═" * 62)

    for lang in IDIOMAS:
        ruta = RAIZ / f"data/i18n/contenido/{lang}.json"
        if not ruta.exists():
            avisos.append(f"{lang}: sin overlay de contenido")
            continue
        ov = leer(ruta)
        sin = 0
        rotas = 0

        for k in kits["kits"]:
            t = (ov.get("kits") or {}).get(k["slug"])
            if not t:
                avisos.append(f"{lang}: falta el kit '{k['slug']}'")
                continue
            for c in ("titulo", "resumen"):
                if sin_traducir(k.get(c, ""), t.get(c, "")):
                    sin += 1
            secs_ov = t.get("secciones") or []
            if len(secs_ov) != len(k.get("secciones") or []):
                errores.append(f"{lang}/{k['slug']}: {len(secs_ov)} secciones traducidas "
                               f"frente a {len(k.get('secciones') or [])} reales")
                rotas += 1
                continue
            for si, s in enumerate(k.get("secciones") or []):
                so = secs_ov[si]
                if len(so.get("items") or []) != len(s.get("items") or []):
                    errores.append(f"{lang}/{k['slug']} secc.{si+1}: items descuadrados "
                                   f"({len(so.get('items') or [])} vs {len(s.get('items') or [])})")
                    rotas += 1
                    continue
                for ii, it in enumerate(s.get("items") or []):
                    io = (so.get("items") or [])[ii]
                    for c in ("producto", "descripcion"):
                        if sin_traducir(it.get(c, ""), io.get(c, "")):
                            sin += 1
                        if it.get(c) and io.get(c) and not igual_estructura(it[c], io[c]):
                            avisos.append(f"{lang}/{k['slug']}: '{c}' de "
                                          f"'{it.get('producto','')[:30]}' perdió etiquetas/marcadores")

        hechas = len((ov.get("blog") or {}))
        total = len(blog["entradas"])
        pct = 100 * hechas / total if total else 0
        print(f"\n{lang}: {sin} cadenas sin traducir · {rotas} secciones descuadradas · "
              f"blog {hechas}/{total} ({pct:.0f}%)")
        if pct < 100:
            avisos.append(f"{lang}: blog al {pct:.0f}% ({total - hechas} entradas pendientes)")

    if avisos:
        print(f"\n⚠  AVISOS ({len(avisos)}):")
        for a in avisos[:25]:
            print(f"   · {a}")
        if len(avisos) > 25:
            print(f"   … y {len(avisos) - 25} más")

    if errores:
        print(f"\n❌ ERRORES ({len(errores)}):")
        for e in errores:
            print(f"   ✗ {e}")

    if errores:
        return 1
    if estricto and any("sin traducir" in a for a in avisos):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
