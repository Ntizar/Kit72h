#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — resolución nocturna de fichas reales de Amazon.

Los productos cuyo enlace es una búsqueda genérica (`es_busqueda: true`) se
resuelven contra la Creators API (SearchItems), no raspando la web. Se filtran
por rango de precio, stock y **compatibilidad del título con el producto**
(modelo, capacidad y unidad incluidas), y solo entonces se proponen.

Reglas de la auditoría 2026-11-10:
- Nada de scraping: una ficha se acepta si la API la devuelve con `IN_STOCK`.
- El título debe contener las unidades/capacidad del producto y no puede ser
  un accesorio (funda, repuesto, compatible con…).
- Un fallo de la API NO se cuenta como «producto agotado»: el lote se corta,
  se conserva lo ya resuelto y se reintenta la próxima noche.
- Nunca escribe enlaces a ciegas: genera propuestas en
  `data/propuestas-fichas.json`; las que pasan el filtro se aplican a
  `data/kits.json` dejando traza de la URL anterior.

Uso:
  python scripts/buscar-amazon.py                 # lote de esta noche (12)
  python scripts/buscar-amazon.py --cupo 5        # lote pequeño
  python scripts/buscar-amazon.py --producto "sirena"   # probar uno
"""
import argparse
import json
import re
import sys
import time
import unicodedata
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
import amazon_api as ama  # noqa: E402

D_KITS = RAIZ / "data" / "kits.json"
D_PROP = RAIZ / "data" / "propuestas-fichas.json"
D_XLSX = RAIZ / "data" / "productos-pendientes.xlsx"
D_LOG = RAIZ / "data" / "buscador-log.json"
# Cola de lo que NO se puede ofrecer aún: el catálogo visible (kits.json) solo
# muestra productos con ficha real verificada. Lo pendiente vive aquí.
D_PEND = RAIZ / "data" / "pendientes-catalogo.json"
D_DESCART = RAIZ / "data" / "propuestas-descartadas.json"
TAG = "ntizar-21"

# Productos que no son de compra online: nunca se buscan
EXCLUIR = re.compile(r"efectivo|paracetamol|ibuprofeno|renueva|recarga gratis|"
                     r"fotocopias|plan familiar|reunión|punto de encuentro", re.I)
STOP = {"de", "del", "la", "el", "los", "las", "para", "con", "sin", "por", "un",
        "una", "unos", "unas", "y", "o", "en", "al", "tipo", "color", "pack"}
ACCESORIOS = {"funda", "carcasa", "repuesto", "compatible", "adaptador",
              "soporte", "protector", "cable", "recambio"}
UNIDAD = (r"(?:mah|wh|kw|ml|cl|kg|cm|mm|km|lm|ghz|hz|bar|atm|grados|db|"
          r"w|v|l|g|a|ah)")


def _normalizar(texto: str) -> str:
    s = unicodedata.normalize("NFKD", (texto or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def _tokens(texto: str) -> set[str]:
    salida = set()
    for t in _normalizar(texto).split():
        if len(t) < 3 or t in STOP:
            continue
        salida.add(t)
        # "silbatos" y "silbato" deben casar sin exigir un stemmer completo.
        if len(t) > 4 and t.endswith("s"):
            salida.add(t[:-1])
    return salida


def _unidades(texto: str) -> set[str]:
    plano = _normalizar(texto)
    compacto = plano.replace(" ", "")
    return {m for m in re.findall(rf"\d+(?:[.,]\d+)?{UNIDAD}", compacto)}


def titulo_compatible(producto: str, titulo: str) -> bool:
    """Evita cambiar un producto por su funda o por otro modelo."""
    pn, tn = _normalizar(producto), _normalizar(titulo)
    if not pn or not tn:
        return False
    if any(a in tn.split() and a not in pn.split() for a in ACCESORIOS):
        return False
    if pn and pn in tn:
        return True
    unidades = _unidades(producto)
    if unidades and not unidades.issubset(_unidades(titulo)):
        return False
    pt = _tokens(producto)
    if not pt:
        return False
    coinciden = len(pt & _tokens(titulo))
    return coinciden >= 2 and coinciden / len(pt) >= 0.60


def rango_de(precio_aprox):
    """'5-15 €' -> (4, 17) con márgenes."""
    nums = [float(x.replace(",", ".")) for x in re.findall(r"\d+(?:[.,]\d+)?", precio_aprox or "")]
    if not nums:
        return (2, 200)
    lo = min(nums) * 0.6
    hi = max(nums) * 1.6 + 3
    return (max(1, lo), hi)


def coletilla_no_compra(producto):
    return EXCLUIR.search(producto)


def n_agotado(clave, intentos, n_max):
    """¿Este item lleva ya demasiadas noches sin candidato verificado?"""
    if not n_max:
        return False
    return (intentos.get(clave) or {}).get("n", 0) >= n_max


def insertar_en_kit(kits: dict, slug: str, seccion: str, item: dict) -> bool:
    """Devuelve al catálogo visible un producto ya verificado.

    Busca el kit por slug (`kit-bebe`, `huerto-autosuficiencia`…) y la sección por
    título; si alguno no existe no inventa nada y devuelve False.
    """
    for kit in kits.get("kits", []):
        if kit.get("slug") != slug:
            continue
        for s in kit.get("secciones", []):
            if s.get("titulo") != seccion:
                continue
            if any(x.get("producto") == item.get("producto") for x in s.get("items", [])):
                return False
            s.setdefault("items", []).append(item)
            return True
        # La sección pudo retirarse por quedarse sin productos reales: se recrea.
        kit.setdefault("secciones", []).append(
            {"titulo": seccion, "items": [item], "intro": ""})
        return True
    return False


def registrar_intento(clave, intentos, hoy):
    """Suma una noche sin candidato y conserva primera y última fecha."""
    v = intentos.get(clave)
    if not isinstance(v, dict):
        v = {"n": 0, "primera": hoy.isoformat()}
    v["n"] = int(v.get("n", 0)) + 1
    v.setdefault("primera", hoy.isoformat())
    v["ultima"] = hoy.isoformat()
    intentos[clave] = v
    return v["n"]


def elegir_candidato(producto: str, resultados: list[dict], lo: float, hi: float) -> dict | None:
    """Filtra por stock, precio y título; elige el más cercano al centro del rango."""
    validos = []
    centro = (lo + hi) / 2
    for d in resultados:
        precio = d.get("precio")
        if not d.get("asin") or not precio or d.get("disponible") is not True:
            continue
        if not (lo <= precio <= hi):
            continue
        if not titulo_compatible(producto, d.get("titulo") or ""):
            continue
        validos.append((abs(precio - centro), d))
    if not validos:
        return None
    return min(validos, key=lambda x: x[0])[1]


def _atomico(ruta: Path, texto: str) -> None:
    tmp = ruta.with_name(ruta.name + ".tmp")
    tmp.write_text(texto, encoding="utf-8")
    tmp.replace(ruta)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cupo", type=int, default=12)
    ap.add_argument("--max-segundos", type=int, default=0,
                    help="presupuesto de tiempo para el lote (0 = sin límite)")
    ap.add_argument("--producto", default=None, help="filtrar por substring (pruebas)")
    ap.add_argument("--limpieza", action="store_true", help="marcar N/A los no-compra y reescribir log")
    ap.add_argument("--agotado-n", type=int, default=3,
                    help="noches sin candidato tras las que un item sale de la rotación (0 = nunca)")
    ap.add_argument("--reabrir", default=None,
                    help="devolver a la rotación los agotados cuyo nombre contenga este texto")
    ap.add_argument("--simular", action="store_true",
                    help="ensayo sin red: dice qué items tocarían y cuántos hay agotados")
    args = ap.parse_args()

    kits = json.loads(D_KITS.read_text(encoding="utf-8"))
    propuestas = json.loads(D_PROP.read_text(encoding="utf-8")) if D_PROP.exists() else {}
    log = json.loads(D_LOG.read_text(encoding="utf-8")) if D_LOG.exists() else {
        "resueltos": [], "na": [], "intentos": {}}
    intentos = log.get("intentos")
    if not isinstance(intentos, dict):
        intentos = {}
        log["intentos"] = intentos

    # Lo que no se puede ofrecer aún (sin ficha real) vive fuera del catálogo.
    pend_doc = (json.loads(D_PEND.read_text(encoding="utf-8"))
                if D_PEND.exists() else {"meta": {}, "items": []})
    pend_items = pend_doc.setdefault("items", [])
    pend_changed = False

    pendientes = []
    for kit in kits["kits"]:
        for s in kit["secciones"]:
            for i in s["items"]:
                prod = i.get("producto", "")
                url = i.get("afiliado") or ""
                if i.get("sin_enlace"):
                    continue
                sin_ficha = ("amazon.es/s?" in url) or not url or i.get("es_busqueda")
                if not sin_ficha:
                    continue
                if coletilla_no_compra(prod):
                    if prod not in log["na"]:
                        log["na"].append(prod)
                    continue
                clave = f"{kit['slug']}|{prod}"
                if (propuestas.get(clave) or {}).get("url"):
                    continue
                if n_agotado(clave, intentos, args.agotado_n):
                    continue
                if prod in log["resueltos"]:
                    continue
                pendientes.append((kit, s, i, clave, "kits"))

    for rec in list(pend_items):
        prod = rec.get("producto", "")
        clave = f"{rec.get('kit', '')}|{prod}"
        if n_agotado(clave, intentos, args.agotado_n):
            continue
        if (propuestas.get(clave) or {}).get("url"):
            continue
        pendientes.append(({"slug": rec.get("kit", "")},
                           {"titulo": rec.get("seccion", "")}, rec, clave, "pend"))

    if args.reabrir:
        tocados = [c for c in list(intentos) if args.reabrir.lower() in c.lower()]
        for c in tocados:
            intentos.pop(c, None)
        log["intentos"] = intentos
        _atomico(D_LOG, json.dumps(log, ensure_ascii=False, indent=2))
        print(f"reabiertos {len(tocados)}: {tocados or '(ninguno coincidió)'}")
        return 0

    if args.limpieza:
        _atomico(D_LOG, json.dumps(log, ensure_ascii=False, indent=2))
        print(f"log de limpieza: {len(log['na'])} marcados N/A")
        return 0

    hoy = date.today()
    dia = int(hoy.strftime("%Y%m%d"))
    rot = dia % max(1, len(pendientes)) if pendientes else 0
    lote = pendientes[rot:rot + args.cupo] or pendientes[:args.cupo]
    if args.producto:
        lote = [p for p in pendientes if args.producto.lower() in p[2]["producto"].lower()][:5]

    agotados = sorted(c for c, v in intentos.items()
                      if (v or {}).get("n", 0) >= args.agotado_n > 0)
    print(f"Pendientes: {len(pendientes)} | lote de esta noche: {len(lote)} | "
          f"agotados: {len(agotados)} (de {len(intentos)} con intentos) | N/A: {len(log['na'])}")
    if args.simular:
        print(f"[simulación] tocaría {len(lote)} de {len(pendientes)} pendientes:")
        for kit, s, i, clave, origen in lote:
            v = intentos.get(clave) or {}
            print(f"  · {i['producto'][:58]:60s} intentos={v.get('n', 0)}")
        print(f"[simulación] {len(agotados)} fuera de rotación (agotado-n={args.agotado_n})")
        return 0

    cfg = ama.cargar_env()
    if not cfg.get("AMAZON_CREDENTIAL_ID") or not cfg.get("AMAZON_PARTNER_TAG"):
        print("buscador: faltan credenciales de Creators API en .env — no se toca nada",
              file=sys.stderr)
        return 2

    nuevos = aplicadas = 0
    t0 = time.monotonic()

    def guardar():
        """Guardado incremental y atómico de cada item terminado."""
        _atomico(D_PROP, json.dumps(propuestas, ensure_ascii=False, indent=2) + "\n")
        _atomico(D_LOG, json.dumps(log, ensure_ascii=False, indent=2))
        if aplicadas:
            _atomico(D_KITS, json.dumps(kits, ensure_ascii=False, indent=2) + "\n")
        if pend_changed:
            _atomico(D_PEND, json.dumps(pend_doc, ensure_ascii=False, indent=2) + "\n")

    for kit, s, i, clave, origen in lote:
        if args.max_segundos and (time.monotonic() - t0) > args.max_segundos:
            print(f"⏱️  presupuesto de {args.max_segundos}s agotado: {nuevos}/{len(lote)} del lote "
                  f"({aplicadas} aplicadas, guardadas). El resto, la próxima noche.")
            break
        prod = i["producto"]
        q = i.get("busqueda") or re.sub(r"\(.*?\)|[—–:/]", " ", prod).strip().lower()
        lo, hi = rango_de(i.get("precio_aprox"))
        try:
            resultados = ama.buscar(cfg, q, n=10)
        except (RuntimeError, SystemExit) as e:
            guardar()
            print(f"❌ buscador: SearchItems falló en «{prod}»: {str(e)[:200]}. "
                  "Lote cortado; NO se marca agotado.", file=sys.stderr)
            return 2

        ficha = elegir_candidato(prod, resultados, lo, hi)
        entry = {"kit": kit["slug"], "seccion": s["titulo"], "busqueda": q,
                 "rango_esperado": i.get("precio_aprox"), "fecha": hoy.isoformat()}
        if ficha:
            url = f"https://www.amazon.es/dp/{ficha['asin']}?tag={TAG}"
            entry.update({
                "asin": ficha["asin"],
                "titulo": (ficha.get("titulo") or "")[:120],
                "precio": ficha.get("precio"),
                "url": url,
                "verificacion": "creators-api-search+stock",
                "aplicada": True,
                "anterior": i.get("afiliado"),
            })
            log["resueltos"].append(prod)
            intentos.pop(clave, None)
            if origen == "kits":
                i["afiliado"] = url
                i["es_busqueda"] = False
                i["verificado_ficha"] = hoy.isoformat()
                aplicadas += 1
            elif insertar_en_kit(kits, i.get("kit"), i.get("seccion"), {
                    "producto": prod,
                    "afiliado": url,
                    "descripcion": i.get("descripcion", ""),
                    "precio_aprox": i.get("precio_aprox", "—"),
                    "prioridad": i.get("prioridad", "esencial"),
                    "es_busqueda": False,
                    "verificado_ficha": hoy.isoformat()}):
                pend_items.remove(i)
                pend_changed = True
                aplicadas += 1
                print(f"     ↳ vuelve al catálogo: {i.get('kit')} · {i.get('seccion')}")
            print(f"  ✅ {prod[:55]:57s} -> {url}")
        else:
            entry["intentos"] = registrar_intento(clave, intentos, hoy)
            entry["estado"] = (f"agotado ({entry['intentos']} noches sin candidato)"
                               if n_agotado(clave, intentos, args.agotado_n)
                               else f"sin candidato compatible (intento {entry['intentos']})")
            print(f"  ·  {prod[:55]:57s} -> {entry['estado']}")
        propuestas[clave] = entry
        nuevos += 1
        guardar()

    guardar()
    if aplicadas:
        print(f"kits.json actualizado con {aplicadas} fichas verificadas por API")

    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font
        from openpyxl.utils import get_column_letter
        wb = Workbook()
        ws = wb.active
        ws.title = "Pendientes"
        ws.append(["Nº", "Kit", "Sección", "Producto", "Búsqueda", "URL verificada (con tu tag)",
                   "Precio", "Rating", "Reseñas", "Verificación", "Estado", "Validado (sí/no)"])
        for c in ws[1]:
            c.font = Font(bold=True)
        n = 0
        for kit in kits["kits"]:
            for s in kit["secciones"]:
                for i in s["items"]:
                    prod = i["producto"]
                    clave = f"{kit['slug']}|{prod}"
                    es_na = coletilla_no_compra(prod)
                    if not (es_busqueda(i) or es_na):
                        continue
                    p = propuestas.get(clave)
                    n += 1
                    ws.append([n, kit["slug"], s["titulo"], prod, i.get("busqueda", ""),
                               (p or {}).get("url", ""), (p or {}).get("precio", ""),
                               (p or {}).get("rating", ""), (p or {}).get("resenas", ""),
                               (p or {}).get("verificacion", ""),
                               "N/A — no es compra online" if es_na else
                               ((p or {}).get("estado") or "propuesta"), ""])
        anchos = [4, 16, 18, 42, 30, 52, 8, 7, 8, 26, 34, 14]
        for j, w in enumerate(anchos, 1):
            ws.column_dimensions[get_column_letter(j)].width = w
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        wb.save(D_XLSX)
        print(f"Excel: {D_XLSX.name} con {n} filas")
    except ImportError:
        print("openpyxl no disponible: solo JSON de propuestas")

    print(f"DONE propuestas totales: {len(propuestas)} | resueltos: {len(log['resueltos'])} | "
          f"pendientes restantes: {max(0, len(pendientes) - nuevos)} | agotados: {len(agotados)}")
    if agotados:
        print(f"Fuera de la rotación ({len(agotados)}; ya no cuentan como pendientes):")
        for c in agotados:
            v = intentos.get(c) or {}
            print(f"  · {c[:76]:78s} {v.get('n', 0)} noches · última {v.get('ultima')}")
        print('  reintentar uno tras arreglar su búsqueda:  --reabrir "<trozo del producto>"')
    return 0


def es_busqueda(i):
    u = i.get("afiliado") or ""
    return i.get("es_busqueda") or "amazon.es/s?" in u


if __name__ == "__main__":
    sys.exit(main())
