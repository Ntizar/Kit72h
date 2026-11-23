#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — auditar-enlaces: ¿el ASIN de cada item es EL producto que se anuncia?

POR QUÉ EXISTE
--------------
El 2026-11-17 la ficha de Starlink anunciaba dos productos y enlazaba otros dos:
la tarjeta de la «Terminal Starlink Gen 3» llevaba a un soporte de techo de
XXSSTUDIO (49,99 €) y la del «Garmin inReach Mini 3» a un inReach Messenger.
Ningún gate lo veía: el enlace tenía `tag=kit72h-21` y respondía 200, así que
era «válido». Un enlace válido al producto equivocado es peor que un 404.

QUÉ HACE
--------
Lee `data/kits.json`, coge el ASIN de cada item con ficha `/dp/`, pide el título
real a la Creators API (10 ASIN por llamada) y compara el nombre editorial con
lo que Amazon vende de verdad. Solo acusa cuando el nombre pide algo que el
título NO tiene:

  mismatch   el nombre promete algo ausente del título: la palabra que define el
             producto (terminal, cable, soporte…), el modelo (mini 3, gen 3,
             20.000 mAh) o casi todo el resto
  dudoso     coincidencia parcial: lo revisa un humano
  ok         el título sostiene el nombre editorial
  sin_datos  Amazon no devuelve el ASIN (descatalogado / solo terceros)
  duplicado  el mismo ASIN con dos nombres editoriales incompatibles

Señales, de más a menos fiable:
  1. CABEZA: primer sustantivo de producto del nombre (sin paréntesis, sin
     cualificadores tipo mini/pro). Si no aparece en el título ni por sinónimo,
     el título vende otra cosa.
  2. MODELO: «gen 3», «mini 3», «v2», «20.000 mAh». Declarado en el nombre y
     ausente del título ⇒ otra versión (Mini 3 ≠ Messenger, Gen 3 ≠ Gen 2).
  3. COBERTURA del resto de palabras del nombre, con stems y sinónimos.

Uso:
  python3 scripts/auditar-enlaces.py                 # todo el catálogo
  python3 scripts/auditar-enlaces.py --solo-kit kit-starlink
  python3 scripts/auditar-enlaces.py --informe       # no falla, solo informa
  python3 scripts/auditar-enlaces.py --desde-cache   # sin red (usa el JSON)

Salidas:
  data/auditoria-enlaces.json  {generado, resumen, total, items[...]}
  exit 2 si hay mismatch/duplicado/sin_datos (salvo --informe)
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import amazon_api  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
KITS = RAIZ / "data" / "kits.json"
SALIDA = RAIZ / "data" / "auditoria-enlaces.json"

# Palabras que no distinguen un producto de otro.
STOP = {
    "de", "del", "la", "el", "los", "las", "un", "una", "y", "o", "con", "sin",
    "para", "por", "en", "al", "a", "tipo", "mas", "muy", "tu", "su", "que",
    "pack", "set", "unidad", "unidades", "color", "nuevo", "nueva", "original",
    "compatible", "universal", "profesional", "alta", "alto", "gran", "mejor",
    "incluye", "aprox", "solo", "como", "cada", "entre", "hasta", "desde",
}

# Unidades y medidas: aparecen en cualquier título y no identifican el producto.
UNIDADES = {
    "cm", "mm", "m", "km", "ml", "l", "cl", "kg", "g", "mg", "w", "kw", "wh",
    "mah", "ah", "v", "a", "hz", "ghz", "mhz", "lumenes", "lm", "dbi", "bar",
    "psi", "grados", "ø", "x", "h", "hora", "horas", "dias", "años",
}

# Cualificadores: van delante del producto, no son el producto.
CUALIFICADORES = {"mini", "maxi", "pro", "plus", "lite", "ultra", "premium", "smart"}

# Sinónimos: mismo producto, otra palabra (se comparan por stem).
SINONIMOS = {
    "terminal": {"antena", "parabolica", "dish", "plato", "receptor"},
    "antena": {"terminal", "parabolica", "dish"},
    "parabolica": {"antena", "terminal", "dish"},
    "powerbank": {"power", "bank", "bateria", "cargador", "powerbank"},
    "bateria": {"powerbank", "pila", "acumulador"},
    "pila": {"bateria", "pilas"},
    "nevera": {"frigorifico", "refrigerador", "cooler", "conservadora"},
    "frigorifico": {"nevera", "refrigerador"},
    "linterna": {"frontal", "lampara", "luz", "foco"},
    "frontal": {"linterna", "lampara"},
    "radio": {"walkie", "transmisor", "emisora"},
    "walkie": {"radio", "transmisor"},
    "messenger": {"comunicador", "mensajeria", "inreach", "localizador", "baliza"},
    "satelital": {"satelite", "satelit"},
    "comunicador": {"messenger", "mensajeria", "inreach", "baliza"},
    "soporte": {"montaje", "mount", "base", "abrazadera", "adaptador"},
    "montaje": {"soporte", "mount"},
    "cable": {"ethernet", "cableado", "extension"},
    "extension": {"cable", "prolongador"},
    "filtro": {"purificador", "depuradora"},
    "purificador": {"filtro"},
    "estufa": {"calefactor", "calefaccion", "insercion"},
    "generador": {"grupo", "electrogeno"},
    "placa": {"panel", "solar"},
    "panel": {"placa", "solar"},
    "saco": {"sleeping", "dormir"},
    "botiquin": {"primeros", "auxilios", "curas"},
    "pastilla": {"potabilizadora", "potabilizar", "comprimido"},
}

# Nombres de producto reconocibles: si el editorial empieza por uno de estos y
# el título no lo menciona (ni por sinónimo), es que vende otra cosa.
CABEZAS = {
    "soporte", "montaje", "cable", "adaptador", "funda", "carcasa", "cargador",
    "carpeta", "antena", "terminal", "powerbank", "bateria",
    "linterna", "nevera", "generador", "placa", "panel", "radio", "walkie",
    "messenger", "comunicador", "botiquin", "estufa", "filtro", "purificador",
    "saco", "mochila", "herramienta", "extintor", "pastilla", "lampara",
}


def sin_acentos(t: str) -> str:
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return t.lower()


def sin_parentesis(t: str) -> str:
    return re.sub(r"\([^)]*\)|\[[^\]]*\]", " ", t or "")


def tokens(t: str) -> list[str]:
    return [x for x in re.split(r"[^a-z0-9]+", sin_acentos(t)) if x]


def stem(t: str) -> str:
    if len(t) > 5 and t.endswith("es"):
        return t[:-2]
    if len(t) > 4 and t.endswith("s"):
        return t[:-1]
    return t


def significativos(texto: str) -> list[str]:
    out = []
    for t in tokens(sin_parentesis(texto)):
        s = stem(t)
        if not s or s in STOP or s in UNIDADES:
            continue
        if re.fullmatch(r"\d+(x\d+)*", s):      # 59x39x127, 20000
            continue
        out.append(s)
    return out


def modelos(texto: str) -> dict[str, set[str]]:
    """Modelos y capacidades declaradas, por dimensión.

    Cada dimensión es un conjunto de ALTERNATIVAS válidas: «10.000-20.000 mAh»
    produce {"mah": {"10000mah", "20000mah"}}, y basta con que el título traiga
    una. Así un rango editorial no se convierte en falso positivo.
    """
    s = sin_acentos(texto)
    dims: dict[str, set[str]] = {}

    def add(dim: str, val: str) -> None:
        dims.setdefault(dim, set()).add(val)

    for m in re.finditer(r"\b(gen|generacion)\s*(\d+)\b", s):
        add("gen", f"gen{m.group(2)}")
    for m in re.finditer(r"\b(mini|plus|pro|max|lite|ultra|v)\s*(\d+)\b", s):
        add("version", f"{m.group(1)}{m.group(2)}")
    # capacidades: 20.000 mAh, 22,5 W, 300-500 Wh. Los separadores se ignoran
    # (20000mAh == 20.000 mAh == 20,000mAh) y un rango cuenta como alternativas.
    for m in re.finditer(r"\b(\d[\d.,]*?)(?:\s*-\s*(\d[\d.,]*?))?\s?(mah|wh|kw|w|ah)\b", s):
        for grupo in (m.group(1), m.group(2)):
            if grupo:
                limpio = re.sub(r"[.,]", "", grupo)
                if limpio.isdigit():
                    add(m.group(3), f"{limpio}{m.group(3)}")
    return dims


def familia(t: str) -> set[str]:
    return {t} | set(SINONIMOS.get(t, ()))


def aparece(token: str, titulo_tokens: set[str], titulo_norm: str) -> bool:
    fam = familia(token)
    for f in fam:
        if f in titulo_tokens or f in titulo_norm:
            return True
        if any(f in x or (len(x) > 3 and x in f) for x in titulo_tokens):
            return True
    return False


def cabeza(texto: str) -> str | None:
    """Primer sustantivo de producto del nombre editorial (no cualificadores)."""
    for t in significativos(texto):
        if t in CUALIFICADORES:
            continue
        if t in CABEZAS:
            return t
        for g in SINONIMOS.get(t, ()):
            if g in CABEZAS:
                return g
    return None



# Clases de producto que NO pueden colarse en una tarjeta: si el título de
# Amazon es de otra familia y la tarjeta no la menciona, es otro producto.
# Así se detectó el carburador de desbrozadora en el cambiador de bebé y el
# salino hipertónico de nebulizador en el suero de rehidratación oral.
TIPOS_INCOMPATIBLES = [
    # Familias que jamás pertenecen a un kit de emergencia. Lista CORTA a
    # propósito: los títulos las mencionan de pasada («apto lavavajillas»,
    # «para frigorífico») y una lista larga llena el gate de falsos positivos.
    "carburador", "desbrozadora", "motosierra", "cortacesped", "nebulizador",
    "calentador de agua", "caldera de gas", "ambientador", "semillas de cesped",
    "videojuego", "consola de juegos",
]


def tipo_incompatible(nombre: str, titulo: str) -> str | None:
    """Un tipo de producto que el título declara y la tarjeta no pide."""
    n = sin_acentos(nombre).lower()
    t = sin_acentos(titulo).lower()
    for tipo in TIPOS_INCOMPATIBLES:
        if tipo in t and tipo not in n:
            return tipo
    return None

def comparar(nombre: str, titulo: str) -> tuple[str, str, float]:
    """Devuelve (estado, motivo, cobertura). Solo acusa ausencias."""
    if not titulo:
        return "dudoso", "la API no devolvió título", 0.0

    tt = {stem(t) for t in tokens(titulo)}
    tnorm = sin_acentos(titulo)
    sig = significativos(nombre)
    if not sig:
        return "dudoso", "nombre editorial sin palabras comparables", 0.0

    # 1. La cabeza del producto debe estar en el título.
    cab = cabeza(nombre)
    if cab and not aparece(cab, tt, tnorm):
        return ("mismatch",
                f"el título no menciona «{cab}»: se anuncia otra cosa", 0.0)

    # 1b. El título vende otra FAMILIA de producto (carburador, nebulizador…).
    tipo = tipo_incompatible(nombre, titulo)
    if tipo:
        return ("mismatch", f"el título es de otra familia de producto («{tipo}»)", 0.0)

    # 2. Modelo declarado y ausente ⇒ otra versión del mismo producto.
    mod_n, mod_t = modelos(nombre), modelos(titulo)
    for dim, opciones in mod_n.items():
        en_titulo = mod_t.get(dim)
        if en_titulo and (opciones & en_titulo):
            continue
        if dim in ("gen", "version") or not en_titulo:
            return ("mismatch",
                    f"modelo declarado y ausente del título: {'/'.join(sorted(opciones))}"
                    + (f" (el título trae {'/'.join(sorted(en_titulo))})" if en_titulo else ""), 0.0)
        # capacidad distinta (2.000 mAh vs 10.000 mAh): lo mira un humano
        return ("dudoso",
                f"capacidad distinta: nombre {'/'.join(sorted(opciones))} · "
                f"título {'/'.join(sorted(en_titulo))}", 0.4)

    # 3. Cobertura del resto de palabras (con sinónimos).
    cubiertos = sum(1 for t in sig if aparece(t, tt, tnorm))
    cob = cubiertos / len(sig)
    faltan_pal = [t for t in sig if not aparece(t, tt, tnorm)]
    if cob >= 0.6:
        return "ok", "", round(cob, 2)
    estado = "dudoso"
    motivo = f"coincidencia {cubiertos}/{len(sig)} (falta: {', '.join(faltan_pal[:4])})"
    return estado, motivo, round(cob, 2)


def items_del_catalogo(solo_kit: str | None) -> list[dict]:
    d = json.loads(KITS.read_text(encoding="utf-8"))
    filas = []
    for kit in d["kits"]:
        if solo_kit and kit["slug"] != solo_kit:
            continue
        for sec in kit.get("secciones", []):
            for it in sec.get("items", []):
                m = re.search(r"/dp/([A-Z0-9]{10})", it.get("afiliado") or "")
                if not m:
                    continue
                filas.append({
                    "asin": m.group(1),
                    "kit": kit["slug"],
                    "seccion": sec.get("titulo"),
                    "producto": it.get("producto"),
                })
    return filas


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Audita que cada ASIN sea el producto anunciado")
    ap.add_argument("--solo-kit", help="limita la auditoría a un kit")
    ap.add_argument("--informe", action="store_true", help="no devuelve exit 2 con hallazgos")
    ap.add_argument("--desde-cache", action="store_true", help="no llama a Amazon; usa el JSON anterior")
    ap.add_argument("--json", action="store_true", help="imprime el JSON en vez de la tabla")
    args = ap.parse_args(argv)

    filas = items_del_catalogo(args.solo_kit)
    if not filas:
        print("sin items con ficha /dp/ que auditar")
        return 1

    cache = {}
    if SALIDA.exists():
        try:
            cache = {i["asin"]: i for i in json.loads(SALIDA.read_text(encoding="utf-8")).get("items", [])}
        except Exception:
            cache = {}

    if args.desde_cache:
        if not cache:
            print("no hay auditoría previa en data/auditoria-enlaces.json")
            return 1
        titulos, sin_datos = {}, set()
        filas = [f for f in filas if f["asin"] in cache]
        if not filas:
            print("la auditoría previa no cubre ningún item de este filtro")
            return 1
    else:
        cfg = amazon_api.cargar_env()
        asins = sorted({f["asin"] for f in filas})
        print(f"consultando {len(asins)} ASIN en Amazon ({(len(asins) + 9) // 10} llamadas)…")
        r = amazon_api.items_por_asin(cfg, asins)
        titulos = {a: (v.get("titulo") or None) for a, v in r["ok"].items()}
        sin_datos = set(r["sin_datos"]) - set(r["ok"])
        if r["lotes_fallidos"]:
            print(f"  ! {len(r['lotes_fallidos'])} lote(s) fallaron por red; esos ASIN no se auditan")

    nombres_por_asin: dict[str, list[dict]] = {}
    for f in filas:
        nombres_por_asin.setdefault(f["asin"], []).append(f)

    items: list[dict] = []
    resumen = {k: 0 for k in ("ok", "dudoso", "mismatch", "sin_datos", "duplicado")}
    for asin, filas_asin in nombres_por_asin.items():
        f = filas_asin[0]
        nombre = f["producto"]

        if args.desde_cache:
            item = dict(cache[asin])
            item["kit"] = f["kit"]
        else:
            if asin in sin_datos:
                estado = "sin_datos"
                motivo = "Amazon no devuelve el ASIN: descatalogado o solo terceros"
                titulo, cob = None, 0.0
            else:
                titulo = titulos.get(asin)
                estado, motivo, cob = comparar(nombre, titulo)

            incompatibles = [
                n["producto"] for n in filas_asin
                if difflib.SequenceMatcher(None, sin_acentos(n["producto"]),
                                           sin_acentos(nombre)).ratio() < 0.55
            ]
            conflictos = [
                n["producto"] for n in filas_asin
                if n["producto"] != nombre and comparar(n["producto"], titulo or "")[0] == "mismatch"
            ]
            if estado == "ok" and conflictos:
                estado = "duplicado"
                motivo = f"mismo ASIN anunciado como «{nombre}» y «{conflictos[0]}» (solo uno puede ser cierto)"

            item = {
                "asin": asin,
                "kit": f["kit"],
                "seccion": f["seccion"],
                "producto": nombre,
                "titulo_amazon": titulo,
                "estado": estado,
                "motivo": motivo,
                "cobertura": cob,
                "kits_con_el_asin": sorted({n["kit"] for n in filas_asin}),
            }

        items.append(item)
        resumen[item["estado"]] = resumen.get(item["estado"], 0) + 1

    orden = {"mismatch": 0, "duplicado": 1, "sin_datos": 2, "dudoso": 3, "ok": 4}
    items.sort(key=lambda i: (orden.get(i["estado"], 9), i["kit"], i["producto"] or ""))

    # Una pasada parcial (--solo-kit) NO puede borrar el resto del catálogo:
    # el gate lee este fichero entero y marcaría 228 ASIN «sin auditar».
    previos = []
    if args.solo_kit and SALIDA.exists():
        try:
            previos = [i for i in json.loads(SALIDA.read_text(encoding="utf-8")).get("items", [])
                       if i.get("kit") != args.solo_kit]
        except json.JSONDecodeError:
            previos = []
    if previos:
        items = sorted(previos + items,
                       key=lambda i: (orden.get(i["estado"], 9), i["kit"], i["producto"] or ""))
        resumen = {}
        for i in items:
            resumen[i["estado"]] = resumen.get(i["estado"], 0) + 1

    doc = {
        "generado": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "resumen": resumen,
        "total": len(items),
        "items": items,
    }
    SALIDA.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")

    if args.json:
        print(json.dumps(doc, ensure_ascii=False, indent=1))
    else:
        print(f"\n{len(items)} ASIN auditados · " + " · ".join(f"{k}: {v}" for k, v in resumen.items()))
        for it in items:
            if it["estado"] == "ok":
                continue
            print(f"\n[{it['estado'].upper()}] {it['asin']} · {it['kit']}")
            print(f"  anunciado: {it['producto']}")
            print(f"  amazon:    {(it['titulo_amazon'] or '—')[:110]}")
            print(f"  motivo:    {it['motivo']}")
        print(f"\nescrito {SALIDA.relative_to(RAIZ)}")

    fallos = resumen["mismatch"] + resumen["duplicado"] + resumen["sin_datos"]
    if fallos and not args.informe:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
