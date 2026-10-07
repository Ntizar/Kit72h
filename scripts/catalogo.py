#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — catalogo: un producto = un sitio, reutilizable en N kits.

Por qué existe (2026-09-28): 17 de los 154 productos del catálogo aparecen en
2-4 kits distintos copiados a mano. Un solo ASIN muerto (la manta térmica)
rompió la cesta de 3 kits a la vez y hubo que sustituirlo 3 veces. Este script
mantiene el ÍNDICE de productos y permite arreglar algo UNA vez.

data/catalogo.json es un índice DERIVADO de data/kits.json (kits.json sigue
siendo la fuente que lee la web). Aquí está la vista de productos: nombre
canónico, ASIN, categorías, y en qué kits se usa cada uno.

Uso:
  python scripts/catalogo.py build                  # regenerar el índice desde kits.json
  python scripts/catalogo.py donde B0GWNDVR7S       # en qué kits se usa un ASIN
  python scripts/catalogo.py compartidos            # productos usados en 2+ kits
  python scripts/catalogo.py huecos                 # items sin ficha (búsquedas / sin enlace)
  python scripts/catalogo.py sustituir VIEJO NUEVO  # cambia el ASIN en TODOS los kits + índice
  python scripts/catalogo.py verificar              # valida las fichas del índice (HTTP)

`sustituir` es la razón de ser de este script: escribe en kits.json, catalogo.json
y avisa cuántos kits/cestas se han arreglado de una sola pasada.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
KITS = RAIZ / "data" / "kits.json"
CATALOGO = RAIZ / "data" / "catalogo.json"
TAG = "ntizar-21"
RX_ASIN = re.compile(r"(?:/dp/|/gp/product/)([A-Z0-9]{10})")
NO_COMPRABLE = re.compile(
    r"efectivo|paracetamol|ibuprofeno|renueva el agua|recarga gratis|fotocopias|"
    r"plan familiar|punto de encuentro|acuerdo de vecindad|hoja de contactos|"
    r"imán o bolsa|reunión", re.I)


def cargar_kits():
    return json.loads(KITS.read_text(encoding="utf-8"))


def construir_indice(datos):
    """Recorre kits.json y agrupa por ASIN."""
    prod = {}
    for k in datos["kits"]:
        for s in k["secciones"]:
            for i in s.get("items", []):
                m = RX_ASIN.search(i.get("afiliado") or "")
                if not m:
                    continue
                asin = m.group(1)
                e = prod.setdefault(asin, {
                    "nombre_canonico": i.get("producto", ""),
                    "url": i["afiliado"], "categorias": [], "apariciones": [],
                })
                # el nombre canónico es el más corto (suele ser el genérico)
                if len(i.get("producto", "")) < len(e["nombre_canonico"]):
                    e["nombre_canonico"] = i["producto"]
                if s["titulo"] not in e["categorias"]:
                    e["categorias"].append(s["titulo"])
                e["apariciones"].append({
                    "kit": k["slug"], "producto": i.get("producto"),
                    "prioridad": i.get("prioridad"), "precio_aprox": i.get("precio_aprox"),
                })
    for a, e in prod.items():
        e["kits"] = sorted({ap["kit"] for ap in e["apariciones"]})
        e["n_kits"] = len(e["kits"])
        e["precio_ref"] = min((ap["precio_aprox"] for ap in e["apariciones"] if ap.get("precio_aprox")),
                              key=len, default=None)
    return prod


def cmd_build(args):
    datos = cargar_kits()
    prod = construir_indice(datos)
    previo = json.loads(CATALOGO.read_text(encoding="utf-8")) if CATALOGO.exists() else {}
    for a, e in prod.items():                       # conservar estado de verificación
        if a in previo.get("productos", {}):
            for campo in ("estado", "verificado"):
                if campo in previo["productos"][a]:
                    e[campo] = previo["productos"][a][campo]
    CATALOGO.write_text(json.dumps({
        "_nota": ("Índice de productos DERIVADO de data/kits.json (la web lee kits.json). "
                  "Un producto = un ASIN = un sitio donde arreglarlo. Regenerar con "
                  "`python scripts/catalogo.py build` tras tocar los kits."),
        "generado": date.today().isoformat(),
        "total_productos": len(prod),
        "compartidos": sum(1 for e in prod.values() if e["n_kits"] > 1),
        "productos": dict(sorted(prod.items())),
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    comp = [a for a, e in prod.items() if e["n_kits"] > 1]
    print(f"catálogo: {len(prod)} productos | compartidos en 2+ kits: {len(comp)}")
    for a in sorted(comp, key=lambda x: -prod[x]["n_kits"])[:5]:
        print(f"  {a} x{prod[a]['n_kits']} {prod[a]['nombre_canonico'][:50]}")


def cmd_donde(args):
    prod = json.loads(CATALOGO.read_text(encoding="utf-8"))["productos"]
    e = prod.get(args.asin)
    if not e:
        return print(f"{args.asin} no está en el catálogo")
    print(f"{args.asin} — {e['nombre_canonico']}")
    print(f"  url: {e['url']}")
    print(f"  en {e['n_kits']} kit(s):")
    for ap in e["apariciones"]:
        print(f"    - {ap['kit']:24} [{ap['prioridad']}] {ap['producto'][:55]}")


def cmd_compartidos(args):
    prod = json.loads(CATALOGO.read_text(encoding="utf-8"))["productos"]
    comp = sorted(((len(e["kits"]), a, e) for a, e in prod.items()), reverse=True)
    print(f"productos usados en 2+ kits: {sum(1 for c, _, _ in comp if c > 1)} de {len(prod)}")
    for c, a, e in comp:
        if c < 2:
            continue
        print(f"  {a} x{c} {e['nombre_canonico'][:44]:46} {', '.join(e['kits'])}")


def cmd_huecos(args):
    datos = cargar_kits()
    comp, noc = [], []
    for k in datos["kits"]:
        for s in k["secciones"]:
            for i in s.get("items", []):
                u = i.get("afiliado") or ""
                if RX_ASIN.search(u):
                    continue
                (noc if NO_COMPRABLE.search(i.get("producto", "")) else comp).append(
                    f"[{k['slug']}] {i.get('producto')} ~ {i.get('precio_aprox')}")
    print(f"huecos: {len(comp) + len(noc)}  (comprables: {len(comp)} | consejos sin enlace: {len(noc)})")
    print("\nCOMPRABLES — se les puede buscar ficha:")
    for x in comp:
        print("  " + x)
    print("\nCONSEJOS — no son producto comprable:")
    for x in noc:
        print("  " + x)


def cmd_sustituir(args):
    viejo, nuevo = args.viejo.upper(), args.nuevo.upper()
    if not re.fullmatch(r"[A-Z0-9]{10}", nuevo):
        return print(f"'{nuevo}' no tiene pinta de ASIN (10 caracteres A-Z0-9)")
    datos = cargar_kits()
    txt = KITS.read_text(encoding="utf-8")
    tocados, kits_tocados = 0, set()
    for k in datos["kits"]:
        for s in k["secciones"]:
            for i in s.get("items", []):
                u = i.get("afiliado") or ""
                if viejo in u:
                    txt = txt.replace(u, f"https://www.amazon.es/dp/{nuevo}?tag={TAG}")
                    tocados += 1
                    kits_tocados.add(k["slug"])
    if not tocados:
        return print(f"{viejo} no aparece en ningún kit")
    if args.solo_ver:
        return print(f"[simulación] {viejo} -> {nuevo} afectaría a {tocados} item(s) en {len(kits_tocados)} kit(s): {sorted(kits_tocados)}")
    KITS.write_text(txt, encoding="utf-8", newline="")
    json.loads(KITS.read_text(encoding="utf-8"))            # valida el JSON
    print(f"{viejo} -> {nuevo}: {tocados} item(s) en {len(kits_tocados)} kit(s) {sorted(kits_tocados)}")
    cmd_build(args)


def cmd_verificar(args):
    sys.path.insert(0, str(RAIZ / "scripts"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("va", RAIZ / "scripts" / "verificar-asins.py")
    va = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(va)
    prod = json.loads(CATALOGO.read_text(encoding="utf-8"))["productos"]
    from concurrent.futures import ThreadPoolExecutor
    asins = sorted(prod)
    with ThreadPoolExecutor(max_workers=4) as ex:
        res = list(ex.map(va.comprobar, asins))
    hoy, caidos = date.today().isoformat(), []
    for a, (est, tit) in zip(asins, res):
        prod[a]["estado"], prod[a]["verificado"] = est, hoy
        if est != "vivo":
            caidos.append((a, est, prod[a]["nombre_canonico"], prod[a]["kits"]))
    datos = json.loads(CATALOGO.read_text(encoding="utf-8"))
    datos["productos"] = prod
    datos["verificacion"] = {"fecha": hoy, "caidos": len(caidos)}
    CATALOGO.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    if caidos:
        print(f"FICHAS CAIDAS ({len(caidos)} de {len(asins)}):")
        for a, est, nom, ks in caidos:
            print(f"  {a} [{est}] {nom[:50]} -> rompe la cesta de: {', '.join(ks)}")
    else:
        print(f"todas vivas: {len(asins)}/{len(asins)} ✅")
    return 1 if caidos else 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    p = sub.add_parser("donde"); p.add_argument("asin")
    sub.add_parser("compartidos")
    sub.add_parser("huecos")
    p = sub.add_parser("sustituir")
    p.add_argument("viejo"); p.add_argument("nuevo")
    p.add_argument("--solo-ver", action="store_true", dest="solo_ver")
    sub.add_parser("verificar")
    args = ap.parse_args()
    return {"build": cmd_build, "donde": cmd_donde, "compartidos": cmd_compartidos,
            "huecos": cmd_huecos, "sustituir": cmd_sustituir, "verificar": cmd_verificar}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
