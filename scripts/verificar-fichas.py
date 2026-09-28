#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — verificar-fichas: ¿esta ficha se puede comprar DE VERDAD?

Por qué existe (2026-09-28): pedir la página por HTTP simple NO sirve — Amazon
devuelve a las peticiones automáticas una página de 3.789 bytes sin título ni
botón de compra, idéntica para un producto vivo y uno muerto. Y Chrome headless
desde esta máquina recibe captcha. El MÉTODO QUE SÍ FUNCIONA es el que ya usa
buscar-amazon.py: curl con `--compressed`, User-Agent de navegador y cookie jar
persistente (2,4 MB de página real, con título y botón de compra).

Estados (uno por ASIN, con fecha):
  ok          página + botón de compra  → se puede añadir a la cesta
  sin_buybox  página viva, sin compra directa (solo terceros)
  agotado     dice expresamente que no está disponible
  caido       ASIN muerto (404 / sin producto)
  bloqueado   captcha/429/503 → NO es una caída (evita falsos positivos)
  error       fallo de red

Reglas del sistema:
  - CADUCIDAD 7 días (decisión de David): pasados 7 días sin comprobar, la web
    deja de afirmar «disponible» y pasa a «sin comprobar».
  - Presupuesto por tanda con prioridad: sin verificar → peor estado → más días
    sin mirar → más kits donde aparece. Nunca se barre todo cada noche.
  - Sustitución automática de caídos (--sustituir): busca ficha verificada nueva
    y la cambia en TODOS los kits con catalogo.py.

Uso:
  python scripts/verificar-fichas.py --cupo 150      # tanda de hoy
  python scripts/verificar-fichas.py --asin B0XXX    # una ficha
  python scripts/verificar-fichas.py --resumen       # lee el registro
  python scripts/verificar-fichas.py --sustituir     # sustituye lo caído/agotado
  python scripts/verificar-fichas.py --exportar      # regenera data/estado.json
"""
import argparse
import json
import re
import sqlite3
import subprocess
import sys
import time
from datetime import date, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
KITS = RAIZ / "data" / "kits.json"
DB = RAIZ / "data" / "fichas.db"
ESTADO_WEB = RAIZ / "data" / "estado.json"
JAR = RAIZ / "data" / "_cookies_amz.txt"
TMP = RAIZ / "data" / "_tmp_ficha.html"
TAG = "nti0c8-21"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
RX_ASIN = re.compile(r"/dp/([A-Z0-9]{10})")
CADUCIDAD_DIAS = 7                      # decisión de David (2026-09-28)

S_BOTON = re.compile(r'id="add-to-cart-button"|id="buybox"|name="submit\.add-to-cart"', re.I)
S_AGOTADO = re.compile(r"No disponible actualmente|Currently unavailable|"
                       r"Temporalmente sin stock|no está disponible", re.I)
S_CAPTCHA = re.compile(r"captcha|Introduce los caracteres|api-services-support@amazon", re.I)
S_TERCEROS = re.compile(r"solo hay vendedores terceros|only available from other sellers", re.I)


def curl_ficha(url, timeout=60):
    """Método probado del proyecto: curl --compressed + cookie jar persistente."""
    cmd = ["curl", "-s", "-L", "--compressed", "-A", UA, "-c", str(JAR), "-b", str(JAR),
           "--max-time", str(timeout), "-o", str(TMP), "-w", "%{http_code}", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 20)
        code = (r.stdout or "").strip()
    except subprocess.TimeoutExpired:
        return "000", ""
    txt = TMP.read_text(encoding="utf-8", errors="ignore") if TMP.exists() else ""
    return code, txt


def clasificar(code, txt):
    if code == "404":
        return "caido"
    if code in ("429", "503", "000"):
        return "bloqueado"
    if S_CAPTCHA.search(txt[:6000]):
        return "bloqueado"
    m = re.search(r'id="productTitle"[^>]*>(.*?)<', txt, re.S)
    titulo = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""
    if not titulo:
        return "caido"
    if S_AGOTADO.search(txt):
        return "agotado"
    if S_BOTON.search(txt):
        return "ok"
    return "sin_buybox"


def comprobar_con_confirmacion(asin, pausa=2.5):
    """Regla anti-falso-positivo: un estado MALO necesita dos lecturas que coincidan.

    Amazon devuelve a veces páginas degradadas (y eso fabrica 'agotado' donde el
    producto está perfecto — medido: los silbatos salieron 'agotado' con la ficha
    viva). Por eso un mal estado se confirma con una segunda lectura separada; si
    las dos discrepan, queda 'error' (se reintenta otro día) y NUNCA se sustituye.
    """
    code, txt = curl_ficha(f"https://www.amazon.es/dp/{asin}")
    est1 = clasificar(code, txt)
    if est1 in ("ok", "bloqueado"):
        return est1
    time.sleep(pausa)
    code2, txt2 = curl_ficha(f"https://www.amazon.es/dp/{asin}")
    est2 = clasificar(code2, txt2)
    if est1 == est2:
        return est1
    return "error" if "ok" in (est1, est2) else est1      # discrepancia: no se afirma


def catalogo():
    d = json.loads(KITS.read_text(encoding="utf-8"))
    out = {}
    for k in d["kits"]:
        for s in k["secciones"]:
            for i in s.get("items", []):
                m = RX_ASIN.search(i.get("afiliado") or "")
                if m:
                    e = out.setdefault(m.group(1), {"titulo": i.get("producto", ""), "kits": set(),
                                                    "producto": i.get("producto", ""), "url": i["afiliado"],
                                                    "precio": i.get("precio_aprox")})
                    e["kits"].add(k["slug"])
    return out


def conectar():
    c = sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS fichas (
        asin TEXT PRIMARY KEY, titulo TEXT, estado TEXT, verificado TEXT,
        fallos INTEGER DEFAULT 0, primera_caida TEXT, ultimo_ok TEXT, intentos INTEGER DEFAULT 1)""")
    return c


def prioridad(c, asin, meta):
    row = c.execute("SELECT estado, verificado, fallos FROM fichas WHERE asin=?", (asin,)).fetchone()
    if not row:
        return (0, 0, -len(meta[asin]["kits"]), asin)
    est, verif, fallos = row
    peso = {"caido": 0, "agotado": 1, "sin_buybox": 2, "error": 3, "bloqueado": 4, "ok": 5}.get(est, 6)
    try:
        dias = (date.today() - date.fromisoformat(verif)).days
    except Exception:
        dias = 999
    return (1, peso, -dias, asin)


def tanda(args):
    meta = catalogo()
    c = conectar()
    asins = [args.asin.upper()] if args.asin else sorted(meta, key=lambda a: prioridad(c, a, meta[a]))
    if not args.asin:
        asins = asins[:args.cupo]
    hoy, t0 = date.today().isoformat(), time.time()
    cuenta = {}
    for n, asin in enumerate(asins, 1):
        estado = comprobar_con_confirmacion(asin)
        cuenta[estado] = cuenta.get(estado, 0) + 1
        row = c.execute("SELECT fallos, primera_caida, ultimo_ok FROM fichas WHERE asin=?", (asin,)).fetchone()
        fallos, pc, uo = row if row else (0, None, None)
        malo = estado in ("caido", "agotado", "sin_buybox")
        fallos = (fallos or 0) + 1 if malo else 0
        if malo and not pc:
            pc = hoy
        if estado == "ok":
            uo, pc = hoy, None
        tit = meta.get(asin, {}).get("titulo") or "(fuera del catálogo)"
        tit = tit[:110]
        c.execute("""INSERT INTO fichas (asin,titulo,estado,verificado,fallos,primera_caida,ultimo_ok,intentos)
                     VALUES (?,?,?,?,?,?,?,1)
                     ON CONFLICT(asin) DO UPDATE SET titulo=excluded.titulo, estado=excluded.estado,
                     verificado=excluded.verificado, fallos=excluded.fallos,
                     primera_caida=excluded.primera_caida, ultimo_ok=excluded.ultimo_ok,
                     intentos=intentos+1""", (asin, tit, estado, hoy, fallos, pc, uo))
        c.commit()
        if estado != "ok":
            print(f"  [{estado:10}] {asin} {tit[:58]}", file=sys.stderr)
        if n % 25 == 0:
            print(f"  ...{n}/{len(asins)} ({time.time()-t0:.0f}s)", file=sys.stderr)
        time.sleep(2.5)          # prudencia anti-bloqueo: ver pausa y confirmación
    print("tanda:", " | ".join(f"{k}={v}" for k, v in sorted(cuenta.items(), key=lambda x: -x[1])))
    exportar(c)
    if args.sustituir:
        sustituir(c, meta)


def exportar(c):
    """data/estado.json con los campos ya resueltos para la web."""
    meta = catalogo()
    hoy = date.today()
    por_url, por_asin = {}, {}
    for asin, estado, verif, titulo in c.execute("SELECT asin, estado, verificado, titulo FROM fichas"):
        try:
            dias = (hoy - date.fromisoformat(verif)).days
        except Exception:
            dias = None
        caducado = dias is None or dias > CADUCIDAD_DIAS
        # qué puede afirmar la web:
        if estado == "ok" and not caducado:
            aviso, texto = "ok", f"✅ disponible (verificado el {verif})"
        elif estado == "ok" and caducado:
            aviso, texto = "caducado", f"🕓 sin comprobar desde el {verif}"
        elif estado == "agotado":
            aviso, texto = "rotura", "⚠️ agotado en Amazon"
        elif estado == "caido":
            aviso, texto = "rotura", "❌ ficha caída"
        elif estado == "sin_buybox":
            aviso, texto = "rotura", "⚠️ sin venta directa"
        else:
            aviso, texto = "", ""          # bloqueado/error: no se afirma nada
        info = {"estado": estado, "aviso": aviso, "texto": texto, "fecha": verif,
                "dias": dias, "caducado": caducado, "titulo": titulo}
        por_asin[asin] = info
        if asin in meta:
            info_busqueda = {"busqueda": meta[asin]["producto"]}
            por_url[meta[asin]["url"]] = {**info, **info_busqueda}
    total = len(por_asin)
    ok = sum(1 for v in por_asin.values() if v["aviso"] == "ok")
    ESTADO_WEB.write_text(json.dumps({
        "generado": hoy.isoformat(), "caducidad_dias": CADUCIDAD_DIAS,
        "total": total, "ok": ok, "productos": por_url, "por_asin": por_asin,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"estado.json: {ok}/{total} confirmadas comprables y al día", file=sys.stderr)


def cmd_resumen(args):
    c = conectar()
    print("=== estado de las fichas (data/fichas.db) ===")
    for est, n in c.execute("SELECT estado, COUNT(*) FROM fichas GROUP BY estado ORDER BY COUNT(*) DESC"):
        print(f"  {est:11} {n}")
    tot = c.execute("SELECT COUNT(*) FROM fichas").fetchone()[0]
    print(f"  {'TOTAL':11} {tot}")
    print("\n=== hay que sustituir (caídas / agotadas) ===")
    for asin, titulo, est, fallos, pc in c.execute(
            "SELECT asin,titulo,estado,fallos,primera_caida FROM fichas WHERE estado IN ('caido','agotado') "
            "ORDER BY fallos DESC"):
        print(f"  [{est:8}] {asin} x{fallos} desde {pc} {titulo[:52]}")
    print("\n=== sin venta directa (revisar) ===")
    for asin, titulo in c.execute("SELECT asin,titulo FROM fichas WHERE estado='sin_buybox' LIMIT 15"):
        print(f"  {asin} {titulo[:60]}")
    print("\n=== caducadas (>7 días sin comprobar) ===")
    hoy = date.today()
    n = 0
    for asin, verif in c.execute("SELECT asin, verificado FROM fichas"):
        try:
            if (hoy - date.fromisoformat(verif)).days > CADUCIDAD_DIAS:
                n += 1
        except Exception:
            pass
    print(f"  {n} fichas")


def sustituir(c, meta):
    """Busca sustituto verificado para lo caído/agotado y lo cambia en TODOS los kits."""
    pend = list(c.execute("SELECT asin, titulo FROM fichas WHERE estado IN ('caido','agotado') AND fallos >= 2"))
    if not pend:
        return print("nada que sustituir (hacen falta 2 fallos seguidos)")
    for asin, titulo in pend:
        prod = meta.get(asin, {}).get("producto") or titulo
        q = re.sub(r"\(.*?\)|[—–:/]", " ", prod).strip().lower()
        print(f"sustituyendo {asin} ({prod[:50]}) -> buscando «{q}»", file=sys.stderr)
        r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "buscar-amazon.py"),
                            "--producto", q.split()[0] if q else prod], capture_output=True, text=True, cwd=RAIZ)
        nuevo = None
        for m in re.finditer(r"-> https://www\.amazon\.es/dp/([A-Z0-9]{10})", r.stdout or ""):
            nuevo = m.group(1)
        if not nuevo:
            print(f"  sin candidato verificado para {asin}", file=sys.stderr)
            continue
        subprocess.run([sys.executable, str(RAIZ / "scripts" / "catalogo.py"), "sustituir", asin, nuevo], cwd=RAIZ)
        print(f"  {asin} -> {nuevo} aplicado en todos los kits", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cupo", type=int, default=150)
    ap.add_argument("--asin", default=None)
    ap.add_argument("--resumen", action="store_true")
    ap.add_argument("--exportar", action="store_true")
    ap.add_argument("--sustituir", action="store_true")
    args = ap.parse_args()
    if args.resumen:
        return cmd_resumen(args)
    if args.exportar:
        return exportar(conectar())
    return tanda(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
