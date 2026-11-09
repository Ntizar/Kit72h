#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — precios reales de Amazon y oferta del día (0 tokens LLM).

Lee los ASIN de `data/kits.json` (fuente de verdad de los kits), los consulta por
lotes de 10 contra la Creators API y escribe `data/precios.json`, que es lo que
pinta la web:

    productos[asin] = {precio, precio_texto, precio_antes, ahorro_pct, disponible…}
    oferta_dia      = el producto del kit con mejor rebaja real del día
    ofertas[]       = los 10 mejores del día (para bloques por kit)

La web lee `data/precios.json` en cada visita (js/ui.js), así que refrescar
precios NO exige rehornear: el horneado diario solo fija la foto para SEO/sin-JS.

Reglas de honestidad:
- Sin precio de Amazon (listings vacío, solo terceros, descatalogado) el ASIN
  simplemente NO entra: la web cae al `precio_aprox` de siempre. Nunca se inventa.
- «Oferta» = Amazon publica un precio recomendado (`savingBasis`) por encima del
  actual. Sin ese dato no hay porcentaje ni insignia.

Uso:
    python3 scripts/precios-amazon.py              # refresco completo + oferta del día
    python3 scripts/precios-amazon.py --max 20     # prueba con 20 ASIN
    python3 scripts/precios-amazon.py --estado     # qué hay ahora mismo en el JSON
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import amazon_api as ama  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
KITS = RAIZ / "data" / "kits.json"
SALIDA = RAIZ / "data" / "precios.json"
HIST = RAIZ / "data" / "precios-historico.json"   # solo servidor: la web no lo descarga
UMBRAL_OFERTA = 10.0        # % mínimo de rebaja real publicada por Amazon para llamarlo oferta
DIAS_HISTORICO = 30


def _leer_json(ruta: Path, defecto):
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return defecto


def asins_de_kits() -> dict:
    """{asin: {producto, kit, kit_titulo, prioridad, precio_aprox, seccion}}"""
    datos = _leer_json(KITS, {})
    salida = {}
    for kit in datos.get("kits", []):
        for seccion in kit.get("secciones", []):
            for item in seccion.get("items", []):
                if item.get("es_busqueda") or not item.get("afiliado"):
                    continue
                import re
                m = re.search(r"/dp/([A-Z0-9]{10})", item["afiliado"])
                if not m:
                    continue
                asin = m.group(1)
                previo = salida.get(asin)
                # un ASIN puede repetirse: gana la prioridad más alta y el primer kit
                rango = {"esencial": 3, "recomendado": 2, "extra": 1, "opcional": 0}
                if previo and rango.get(previo["prioridad"], 0) >= rango.get(item.get("prioridad"), 0):
                    continue
                salida[asin] = {
                    "producto": item.get("producto", ""),
                    "kit": kit.get("slug", ""),
                    "kit_titulo": kit.get("titulo", ""),
                    "prioridad": item.get("prioridad", "extra"),
                    "precio_aprox": item.get("precio_aprox", ""),
                    "seccion": seccion.get("titulo", ""),
                }
    return salida


def _titulo_corto(texto: str, limite: int = 78) -> str:
    texto = (texto or "").strip()
    if len(texto) <= limite:
        return texto
    corte = texto[:limite].rsplit(" ", 1)[0]
    return corte.rstrip(",.;:|-– ") + "…"


def _elegir_oferta(candidatos: list[dict], ahora: datetime) -> dict | None:
    """Mejor rebaja real del día. Empata/rota entre los 3 primeros para que el
    bloque no se quede clavado semanas con el mismo producto."""
    if not candidatos:
        return None
    orden = sorted(candidatos, key=lambda c: c["punt"], reverse=True)
    cabeza = [c for c in orden if c["punt"] >= orden[0]["punt"] * 0.85][:3]
    elegido = cabeza[ahora.timetuple().tm_yday % len(cabeza)]
    return {k: elegido[k] for k in ("asin", "producto", "titulo_amazon", "precio", "precio_texto",
                                   "precio_antes", "ahorro_pct", "kit", "kit_titulo", "url", "fecha")}


def _oferta_publica(c: dict) -> dict:
    return {k: c[k] for k in ("asin", "producto", "titulo_amazon", "precio", "precio_texto",
                              "precio_antes", "ahorro_pct", "kit", "kit_titulo", "url", "fecha")}


def refrescar(max_asins: int | None = None) -> int:
    cfg = ama.cargar_env()
    if not cfg.get("AMAZON_CREDENTIAL_ID"):
        print("precios: sin credenciales de la Creators API en .env — no se toca el JSON")
        return 0

    mapa = asins_de_kits()
    asins = list(mapa)
    if max_asins:
        asins = asins[:max_asins]
    print(f"precios: {len(asins)} ASIN de {len(mapa)} en los kits · lotes de {ama.MAX_IDS}")

    previo = _leer_json(SALIDA, {})
    productos = dict(previo.get("productos") or {})
    historico = dict(_leer_json(HIST, {}).get("historico") or previo.get("historico") or {})
    ahora = datetime.now(timezone.utc)
    hoy = ahora.date().isoformat()

    con_precio = sin_datos = sin_oferta = 0
    for i in range(0, len(asins), ama.MAX_IDS):
        lote = asins[i:i + ama.MAX_IDS]
        res = ama.items_por_asin(cfg, lote, pausa=0.0)
        for asin, datos in res["ok"].items():
            meta = mapa.get(asin, {})
            if not datos.get("precio"):
                sin_oferta += 1
                continue
            con_precio += 1
            productos[asin] = {
                **datos,
                "producto": meta.get("producto", datos.get("titulo")),
                "kit": meta.get("kit", ""),
                "kit_titulo": meta.get("kit_titulo", ""),
                "prioridad": meta.get("prioridad", ""),
                "precio_aprox": meta.get("precio_aprox", ""),
                "actualizado": hoy,
            }
            serie = historico.setdefault(asin, [])
            if not serie or serie[-1].get("fecha") != hoy:
                serie.append({"fecha": hoy, "precio": datos["precio"]})
                del serie[:-DIAS_HISTORICO]
        sin_datos += len(res["sin_datos"])
        _volcar(productos, historico, previo, con_precio, sin_datos, sin_oferta, ahora, asins)
        print(f"  · {min(i + ama.MAX_IDS, len(asins))}/{len(asins)}  "
              f"precio={con_precio}  sin_listado={sin_oferta}  sin_datos={sin_datos}", flush=True)

    salida = _volcar(productos, historico, previo, con_precio, sin_datos, sin_oferta, ahora, asins)
    od = salida.get("oferta_dia")
    if od:
        print(f"oferta del día: {od['producto']} — {od['precio_texto']} "
              f"(-{od['ahorro_pct']}% sobre {od['precio_antes']:.2f} €) · kit {od['kit']}")
    else:
        print("oferta del día: ninguna rebaja real hoy (el bloque no se pinta)")
    return 0


def _volcar(productos, historico, previo, con_precio, sin_datos, sin_oferta, ahora, asins) -> dict:
    hoy = ahora.date().isoformat()
    candidatos = []
    for asin, d in productos.items():
        if not d.get("precio") or not d.get("precio_antes"):
            continue
        pct = d.get("ahorro_pct") or 0
        if pct < UMBRAL_OFERTA:
            continue
        # El ticket manda: 3 % de comisión sobre 315 € deja 9,45 €; sobre 6,95 €, 0,21 €.
        # Se pondera el % de rebaja por el precio (tope 500 €, más allá no añade).
        factor = max(d["precio"], 1) / 100.0
        if d["precio"] > 500:
            factor = 5.0 + (min(d["precio"], 1200) - 500) / 1000.0
        if d.get("prioridad") == "esencial":
            factor *= 1.1
        candidatos.append({
            "asin": asin,
            "producto": d.get("producto", ""),
            "titulo_amazon": _titulo_corto(d.get("titulo")),
            "precio": d["precio"],
            "precio_texto": d.get("precio_texto") or f"{d['precio']:.2f} €",
            "precio_antes": d["precio_antes"],
            "ahorro_pct": pct,
            "kit": d.get("kit", ""),
            "kit_titulo": d.get("kit_titulo", ""),
            "url": d.get("url") or f"https://www.amazon.es/dp/{asin}?tag=ntizar-21",
            "fecha": hoy,
            "punt": pct * factor,
        })
    candidatos.sort(key=lambda c: c["punt"], reverse=True)
    oferta = _elegir_oferta(candidatos, ahora)

    datos = {
        "meta": {
            "actualizado": ahora.isoformat(timespec="seconds"),
            "fuente": "Amazon Creators API",
            "marketplace": "www.amazon.es",
            "tag": "ntizar-21",
            "aviso": ("Precios consultados hoy en Amazon.es. Pueden cambiar en cualquier momento: "
                      "el precio válido es el de la ficha en el momento de la compra."),
            "total_asins": len(asins),
            "con_precio": con_precio,
            "sin_listado": sin_oferta,
            "sin_datos": sin_datos,
            "umbral_oferta_pct": UMBRAL_OFERTA,
        },
        # Payload de la web: sólo los 5 campos que pinta js/ui.js. Todo lo demás
        # (titulo, imagen, histórico) se queda en servidor — este JSON se descarga
        # en CADA visita, así que cada byte de más se paga en móvil.
        "productos": {a: {k: d.get(k) for k in ("precio", "precio_texto", "precio_antes",
                                                "ahorro_pct", "disponible") if d.get(k) is not None}
                      for a, d in productos.items()},
        "oferta_dia": _oferta_publica(oferta) if oferta else None,
        "ofertas": [_oferta_publica(c) for c in candidatos[:10]],
    }
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, separators=(",", ":")) + "\n",
                      encoding="utf-8")
    HIST.write_text(json.dumps({"meta": {"actualizado": datos["meta"]["actualizado"]},
                                "historico": {a: s[-DIAS_HISTORICO:] for a, s in historico.items() if s}},
                               ensure_ascii=False) + "\n", encoding="utf-8")
    return datos


def estado() -> int:
    datos = _leer_json(SALIDA, None)
    if not datos:
        print("precios: todavía no hay data/precios.json (nunca se ha refrescado)")
        return 1
    m = datos.get("meta", {})
    print(f"actualizado: {m.get('actualizado')}  ·  con precio: {m.get('con_precio')}/{m.get('total_asins')}  "
          f"· sin listado: {m.get('sin_listado')}  · sin datos: {m.get('sin_datos')}")
    od = datos.get("oferta_dia")
    print("oferta del día: " + (f"{od['producto']} — {od['precio_texto']} (-{od['ahorro_pct']}%)"
                                if od else "ninguna"))
    con_pct = [(a, d) for a, d in (datos.get("productos") or {}).items() if d.get("ahorro_pct")]
    con_pct.sort(key=lambda x: x[1]["ahorro_pct"], reverse=True)
    nombres = asins_de_kits()
    for a, d in con_pct[:8]:
        nombre = (nombres.get(a) or {}).get("producto") or a
        print(f"  {a}  {d['precio_texto']:>9}  -{d['ahorro_pct']}%  {nombre[:60]}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Precios reales de Amazon para kit72h")
    ap.add_argument("--max", type=int, default=None, help="limitar a N ASIN (pruebas)")
    ap.add_argument("--estado", action="store_true", help="resumen del JSON actual")
    args = ap.parse_args()
    if args.estado:
        return estado()
    return refrescar(args.max)


if __name__ == "__main__":
    sys.exit(main())
