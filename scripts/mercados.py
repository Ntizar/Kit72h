#!/usr/bin/env python3
"""Kit72h — mercados: fuente única de verdad para todo lo que depende del país.

Lo usan scripts/prerender.py (horneado) y scripts/generar-seo.py (sitemap con
hreflang). Si la lista de mercados o el esquema de rutas cambia, cambia aquí y
los dos se enteran: regla del repo, una sola fuente por tema.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BASE = "https://kit72h.com"


def cargar_json(ruta, defecto=None):
    ruta = Path(ruta)
    if not ruta.exists():
        return defecto
    return json.loads(ruta.read_text(encoding="utf-8"))


def cargar_mercados():
    d = cargar_json(RAIZ / "data/mercados.json") or {"mercados": []}
    return [m for m in d["mercados"] if m.get("activo", True)]


def prefijo(mercado):
    """'' para España (raíz) y 'de/' para los demás."""
    return "" if mercado["ruta"] == "/" else mercado["ruta"].strip("/") + "/"


def textos_ui(mercado):
    base = cargar_json(RAIZ / "data/i18n/ui/es.json", {})
    if mercado["lang"] == "es":
        return base
    ov = cargar_json(RAIZ / f"data/i18n/ui/{mercado['lang']}.json", {}) or {}
    base.update({k: v for k, v in ov.items() if not k.startswith("_")})
    return base


def fusionar(base, ov):
    """Mismo merge que js/state.js: por slug y por índice, solo textos.
    Un ASIN, una URL o un precio en € no se tocan nunca."""
    if not ov:
        return base
    if ov.get("disclosure"):
        base["disclosure"] = ov["disclosure"]
    fuentes = (base.get("meta") or {}).get("fuentes") or []
    for i, f in enumerate((ov.get("meta") or {}).get("fuentes") or []):
        if i < len(fuentes):
            for c in ("cat", "nota"):
                if f.get(c):
                    fuentes[i][c] = f[c]
    for k in base.get("kits", []):
        t = (ov.get("kits") or {}).get(k["slug"])
        if not t:
            continue
        for c in ("titulo", "resumen", "coste_total", "paraQuien", "paraQuien_no", "busc"):
            if t.get(c):
                k[c] = t[c]
        if isinstance(t.get("guia"), dict):
            for f in ("antes", "durante", "despues"):
                if isinstance(t["guia"].get(f), list):
                    k.setdefault("guia", {})[f] = t["guia"][f]
        if isinstance(t.get("errores"), list):
            k["errores"] = t["errores"]
        for si, s in enumerate(t.get("secciones") or []):
            if si >= len(k.get("secciones") or []):
                continue
            dk = k["secciones"][si]
            if s.get("titulo"):
                dk["titulo"] = s["titulo"]
            if s.get("intro"):
                dk["intro"] = s["intro"]
            for ii, it in enumerate(s.get("items") or []):
                if ii >= len(dk.get("items") or []):
                    continue
                di = dk["items"][ii]
                for c in ("producto", "descripcion", "asin_local", "precio_local"):
                    if it.get(c):
                        di[c] = it[c]
    return base


def fusionar_blog(base, ov):
    if not ov:
        return base
    for e in base.get("entradas", []):
        t = (ov.get("blog") or {}).get(e["slug"])
        if not t:
            continue
        for c in ("titulo", "resumen", "cuerpo"):
            if t.get(c):
                e[c] = t[c]
        if isinstance(t.get("etiquetas"), list):
            e["etiquetas"] = t["etiquetas"]
        for i, f in enumerate(t.get("fuente") or []):
            if i < len(e.get("fuente") or []) and f.get("nombre"):
                e["fuente"][i]["nombre"] = f["nombre"]
        e["_traducido"] = True
    return base


def contenido():
    """{id_mercado: {mercado, kits, blog, ui, traducidas}}"""
    kits_es = cargar_json(RAIZ / "data/kits.json") or {"kits": []}
    blog_es = cargar_json(RAIZ / "data/blog.json") or {"entradas": []}
    salida = {}
    for m in cargar_mercados():
        if m["id"] == "es" or m["contenido"] == "es":
            kits, blogd = kits_es, blog_es
        else:
            ov = cargar_json(RAIZ / f"data/i18n/contenido/{m['contenido']}.json", None)
            kits = fusionar(copy.deepcopy(kits_es), ov)
            blogd = fusionar_blog(copy.deepcopy(blog_es), ov)
        salida[m["id"]] = {
            "mercado": m,
            "kits": kits,
            "blog": blogd,
            "ui": textos_ui(m),
            "traducidas": {e["slug"] for e in blogd["entradas"] if e.get("_traducido")},
        }
    return salida


def rutas_de(mercado, datos_mercado):
    """[(ruta_publica, clave_logica)] del mercado. La clave lógica es igual en
    todos los mercados y es lo que empareja los hreflang."""
    pre = prefijo(mercado)
    r = [("/" + pre, "home"), ("/" + pre + "fuentes/", "fuentes"),
         ("/" + pre + "blog/", "blogidx")]
    if mercado["id"] == "es":
        # AEMET + IGN + Google News ES: páginas que solo tienen sentido en España.
        r += [("/zona/", "zona"), ("/noticias/", "noticias")]
    for k in datos_mercado["kits"]["kits"]:
        r.append(("/" + pre + f"kit/{k['slug']}/", f"kit/{k['slug']}"))
    for e in datos_mercado["blog"]["entradas"]:
        # Fuera de España, solo las guías ya traducidas: duplicar 64 artículos en
        # castellano bajo /de/ sería contenido duplicado.
        if mercado["id"] != "es" and e["slug"] not in datos_mercado["traducidas"]:
            continue
        r.append(("/" + pre + f"blog/{e['slug']}/", f"blog/{e['slug']}"))
    return r


def indice_hreflang(datos):
    """{clave_logica: {id_mercado: ruta}}"""
    idx = {}
    for mid, d in datos.items():
        for ruta, clave in rutas_de(d["mercado"], d):
            idx.setdefault(clave, {})[mid] = ruta
    return idx


def alternos(clave, datos, idx):
    """Lista [(hreflang, url_absoluta)] incluyendo x-default → castellano."""
    salida = []
    for mid, d in datos.items():
        ruta = idx.get(clave, {}).get(mid)
        if ruta:
            salida.append((d["mercado"]["hreflang"], BASE + ruta))
    if idx.get(clave, {}).get("es"):
        salida.append(("x-default", BASE + idx[clave]["es"]))
    return salida
