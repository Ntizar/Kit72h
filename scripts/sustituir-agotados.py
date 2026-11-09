#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — sustituir productos agotados por uno equivalente que SÍ se venda.

Lee los ASIN que la Creators API marca como sin stock (`data/precios.json →
sin_precio`), busca un equivalente con `searchItems` y propone el cambio. Con
`--aplicar` reescribe el enlace en `data/kits.json` (la fuente de verdad).

Reglas (no negociables):
- Nunca se inventa un ASIN: el sustituto sale de la API y se comprueba con
  `disponible is True` y con precio en el orden del `precio_aprox` del item.
- El nombre editorial del producto NO se toca: sólo el enlace.
- Sin candidato que pase el filtro, el item se queda como está (y se lista).

Uso:
    python3 scripts/sustituir-agotados.py              # sólo propone y escribe el JSON
    python3 scripts/sustituir-agotados.py --aplicar    # además reescribe kits.json
    python3 scripts/sustituir-agotados.py --tabla      # resumen legible
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import amazon_api as ama  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
KITS = RAIZ / "data" / "kits.json"
PRECIOS = RAIZ / "data" / "precios.json"
SALIDA = RAIZ / "data" / "sustituciones.json"
TAG = "ntizar-21"

STOP = {"de", "del", "la", "el", "los", "las", "un", "una", "unos", "unas", "para", "por",
        "con", "sin", "y", "o", "e", "a", "en", "al", "mas", "pack", "dos", "tres", "cuatro",
        "persona", "personas", "unidad", "unidades", "aproximado", "aprox", "tipo", "kit"}


def _norm(texto: str) -> str:
    texto = unicodedata.normalize("NFD", (texto or "").lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]+", " ", texto)


def _tokens(texto: str) -> set[str]:
    return {t for t in _norm(texto).split() if len(t) > 2 and t not in STOP}


def _raiz(token: str) -> str:
    """Plural/singular grosero: 'botellas' ~ 'botella'."""
    return token[:-1] if len(token) > 4 and token.endswith("s") else token


def _cobertura(producto: str, titulo: str) -> tuple[float, int]:
    quiero = {_raiz(t) for t in _tokens(producto)}
    if not quiero:
        return 0.0, 0
    hay = {_raiz(t) for t in _tokens(titulo)}
    comunes = quiero & hay
    return len(comunes) / len(quiero), len(comunes)


def _rango_aprox(precio_aprox: str) -> tuple[float, float] | None:
    nums = [float(n) for n in re.findall(r"\d+(?:[.,]\d+)?", str(precio_aprox).replace(".", ""))]
    if not nums:
        return None
    return min(nums), max(nums)


def _aceptable(precio: float | None, precio_aprox: str) -> bool:
    rango = _rango_aprox(precio_aprox)
    if not precio:
        return False
    if not rango:
        return True
    lo, hi = rango
    return lo * 0.35 <= precio <= hi * 2.8


def buscar_candidatos(cfg: dict, producto: str, precio_aprox: str) -> list[dict]:
    palabras = [t for t in _tokens(producto)]
    consulta = " ".join(sorted(palabras, key=len, reverse=True)[:6])
    if not consulta:
        return []
    resultados = ama.buscar(cfg, consulta, 10)
    buenos = []
    for d in resultados:
        if not d.get("disponible") or not d.get("precio") or not d.get("asin"):
            continue
        if not _aceptable(d["precio"], precio_aprox):
            continue
        cob, comunes = _cobertura(producto, d.get("titulo") or "")
        if comunes < 2:
            continue
        buenos.append({**d, "cobertura": round(cob, 2), "comunes": comunes})
    buenos.sort(key=lambda d: (d["cobertura"], d["comunes"]), reverse=True)
    return buenos


def items_por_asin(kits: dict) -> dict:
    mapa: dict[str, list] = {}
    for kit in kits["kits"]:
        for seccion in kit.get("secciones", []):
            for item in seccion.get("items", []):
                m = re.search(r"/dp/([A-Z0-9]{10})", item.get("afiliado") or "")
                if m:
                    mapa.setdefault(m.group(1), []).append((kit, seccion, item))
    return mapa


def aplicar_mapa(ruta_mapa: Path) -> int:
    """Aplica un mapa {asin_viejo: asin_nuevo} revisado a mano. No consulta la API:
    los pares ya se verificaron al aprobarlos. Falla en silencio controlado si un
    ASIN viejo no aparece en los kits (dato desfasado)."""
    mapa = {k: v for k, v in json.loads(ruta_mapa.read_text(encoding="utf-8")).items()
            if not k.startswith("_")}
    kits = json.loads(KITS.read_text(encoding="utf-8"))
    indice = items_por_asin(kits)
    cambios, faltan = 0, []
    for viejo, nuevo in mapa.items():
        if viejo not in indice:
            faltan.append(viejo)
            continue
        for _kit, _seccion, item in indice[viejo]:
            item["afiliado"] = f"https://www.amazon.es/dp/{nuevo}?tag={TAG}"
            item["es_busqueda"] = False
            item["sustituye_a"] = viejo
            cambios += 1
    KITS.write_text(json.dumps(kits, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"✅ {cambios} enlaces sustituidos ({len(mapa)} pares) en data/kits.json")
    if faltan:
        print(f"⚠️ {len(faltan)} ASIN del mapa ya no están en los kits: {', '.join(faltan)}")
    print("   siguiente: catalogo.py build + precios-amazon.py + generar-seo + prerender + gate")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true", help="reescribe data/kits.json")
    ap.add_argument("--tabla", action="store_true", help="sólo imprime lo ya propuesto")
    ap.add_argument("--umbral", type=float, default=0.7, help="cobertura mínima para aplicar")
    ap.add_argument("--mapa", help="JSON {asin_viejo: asin_nuevo} aprobado a mano")
    args = ap.parse_args()

    if args.mapa:
        return aplicar_mapa(Path(args.mapa))

    if args.tabla:
        propuestas = json.loads(SALIDA.read_text(encoding="utf-8"))["propuestas"]
        imprimir(propuestas)
        return 0

    cfg = ama.cargar_env()
    if not cfg.get("AMAZON_CREDENTIAL_ID"):
        print("Faltan credenciales de la Creators API en .env")
        return 2

    kits = json.loads(KITS.read_text(encoding="utf-8"))
    precios = json.loads(PRECIOS.read_text(encoding="utf-8"))
    agotados = [a for a, v in (precios.get("sin_precio") or {}).items() if v == 1]
    indice = items_por_asin(kits)

    propuestas = []
    for i, asin in enumerate(agotados, 1):
        usos = indice.get(asin) or []
        if not usos:
            continue
        kit, seccion, item = usos[0]
        producto, aprox = item.get("producto", ""), item.get("precio_aprox", "")
        candidatos = buscar_candidatos(cfg, producto, aprox)
        elegido = candidatos[0] if candidatos else None
        propuestas.append({
            "asin_viejo": asin,
            "producto": producto,
            "kit": kit["slug"],
            "kits_afectados": sorted({k["slug"] for k, _, _ in usos}),
            "precio_aprox": aprox,
            "motivo": "agotado en Amazon",
            "candidatos": [{k: c.get(k) for k in ("asin", "titulo", "precio", "precio_texto",
                                                  "cobertura", "comunes")} for c in candidatos[:3]],
            "elegido": {k: elegido.get(k) for k in ("asin", "titulo", "precio", "precio_texto",
                                                    "cobertura", "comunes")} if elegido else None,
        })
        estado = (f"→ {elegido['asin']} {elegido['precio_texto']} (cob {elegido['cobertura']})"
                  if elegido else "→ sin candidato válido")
        print(f"[{i}/{len(agotados)}] {producto[:44]:<44} {estado}", flush=True)

    aplicables = [p for p in propuestas if p["elegido"] and p["elegido"]["cobertura"] >= args.umbral]
    datos = {
        "meta": {
            "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "fuente": "Amazon Creators API · searchItems",
            "agotados": len(agotados),
            "con_sustituto": len([p for p in propuestas if p["elegido"]]),
            "aplicables": len(aplicables),
            "umbral_cobertura": args.umbral,
            "aplicado": bool(args.aplicar),
        },
        "propuestas": propuestas,
    }
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\n{len(propuestas)} agotados con ficha · {len(aplicables)} con sustituto claro "
          f"(cobertura ≥ {args.umbral}) → {SALIDA.relative_to(RAIZ)}")
    imprimir(propuestas)

    if not args.aplicar:
        return 0

    cambios = 0
    for p in aplicables:
        nuevo = p["elegido"]["asin"]
        for kit, _seccion, item in indice.get(p["asin_viejo"], []):
            item["afiliado"] = f"https://www.amazon.es/dp/{nuevo}?tag={TAG}"
            item["es_busqueda"] = False
            item["sustituye_a"] = p["asin_viejo"]
            cambios += 1
    if cambios:
        KITS.write_text(json.dumps(kits, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\n✅ {cambios} enlaces sustituidos en data/kits.json")
    print("   recuerda: catalogo.py build + generar-seo + prerender + gate")
    return 0


def imprimir(propuestas: list[dict]) -> None:
    print("\nPRODUCTO / KIT                          → SUSTITUTO")
    for p in propuestas:
        e = p.get("elegido")
        if e:
            print(f"· {p['producto'][:38]:<38} [{p['kit'][:18]:<18}] → {e['asin']} "
                  f"{str(e['precio_texto']):>9} cob={e['cobertura']} {(e['titulo'] or '')[:52]}")
        else:
            print(f"· {p['producto'][:38]:<38} [{p['kit'][:18]:<18}] → (revisar a mano)")


if __name__ == "__main__":
    sys.exit(main())
