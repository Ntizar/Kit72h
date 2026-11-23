#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""auditar-tags.py — guardián de los Tracking IDs de afiliado de Amazon.

Una sola fuente de verdad: `data/tags-afiliado.json` (qué tag existe, de qué
marketplace es y para qué sección). Este script compara TODO enlace de Amazon
publicado con ese registro.

Uso:
    python3 scripts/auditar-tags.py              # audita el repo (HTML horneado + fuentes)
    python3 scripts/auditar-tags.py --vivo       # audita https://kit72h.com vía sitemap
    python3 scripts/auditar-tags.py --json x.json --quiet
    python3 scripts/auditar-tags.py --estricto   # los avisos también hacen fallar

Códigos de salida: 0 = sin errores · 1 = errores · 2 = no se pudo auditar.

Reglas duras (ERROR):
  E1  tag que no está en el registro (typo, tag ajeno, tag viejo)
  E2  tag de un marketplace aplicado a otro dominio (Amazon lo ignora: comisión 0)
  E3  enlace de afiliado SIN tag en un mercado que sí tiene tag
  E4  `tag=` vacío o dos valores de tag distintos en la misma URL
Avisos (WARN):
  W1  enlaces sin tag en mercados sin Tracking ID propio (pendiente de Amazon)
  W2  tag que no es el de la sección (portada / fichas / blog)
  W3  enlace corto (amzn.to / amzn.eu): no se puede auditar el tag
"""
from __future__ import annotations

import argparse
import collections
import html as htmlmod
import json
import re
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

RAIZ = Path(__file__).resolve().parents[1]
REGISTRO = RAIZ / "data" / "tags-afiliado.json"
BASE = "https://kit72h.com"

# --- qué es un enlace de afiliado y qué no -----------------------------------
# Los que NO comisionan: CDN de imágenes, APIs y programas de Amazon.
NO_AFILIADO = (
    "m.media-amazon.com", "images-na.ssl-images-amazon", "images-eu.ssl-images-amazon",
    "amazon-adsystem.com", "api.amazon", "webservices.amazon", "affiliate-program.amazon",
    "associates.amazon", "amzn-oss.com",
)
DOMINIO_RE = re.compile(r"(?:^|\.)amazon\.[a-z]{2,3}(?:\.[a-z]{2})?$|amzn\.(?:to|eu)$|a\.co$", re.I)

# formato de Tracking ID de Associates (p.ej. kit72h-21, onamzntizar-21)
TAG_RE = re.compile(r"^[a-z0-9][a-z0-9\-_]{2,29}-\d{2}$")

# carpetas que no son sitio publicado ni fuentes del sitio
EXCLUIDAS = {".git", "node_modules", "__pycache__", "busquedas", "videos", "pintout",
             ".wrangler", ".venv", "sketches", "notes"}
EXT_FUENTE = {".html", ".js", ".json", ".xml"}

ATRIBUTO_RE = re.compile(
    r"""(?:href|src|data-href|data-url|action)\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.I)
URL_SUELTA_RE = re.compile(r"""https?://(?:[^\s"'<>\\`()\[\]{}]|\([^\s"'<>\\`()]*\)|%[0-9A-Fa-f]{2})+""")

MERCADO_POR_DOMINIO = {
    "amazon.es": "es", "amazon.com": "us", "amazon.co.uk": "uk", "amazon.de": "de",
    "amazon.fr": "fr", "amazon.it": "it", "amazon.nl": "nl", "amazon.co.jp": "jp",
    "amazon.ca": "ca", "amazon.com.mx": "mx", "amazon.com.br": "br", "amazon.com.au": "au",
    "amazon.in": "in", "amazon.se": "se", "amazon.pl": "pl", "amazon.com.tr": "tr",
    "amazon.ae": "ae", "amazon.sg": "sg", "amazon.com.be": "be", "amazon.ie": "ie",
}


def cargar_registro():
    if not REGISTRO.exists():
        sys.exit(f"[auditar-tags] falta el registro: {REGISTRO}")
    d = json.loads(REGISTRO.read_text(encoding="utf-8"))
    tags = d.get("tags") or {}
    for t, meta in tags.items():
        if not TAG_RE.match(t):
            sys.exit(f"[auditar-tags] Tracking ID con formato imposible en el registro: {t!r}")
        if not meta.get("mercado"):
            sys.exit(f"[auditar-tags] el tag {t} no declara mercado")
        if meta.get("mercado") == "intl" and not meta.get("dominios"):
            sys.exit(f"[auditar-tags] el tag {t} es internacional y no declara 'dominios'")
    return d


def tag_vale_en(meta, host):
    """¿Este Tracking ID acredita en esta tienda?
    - Tag de marketplace: solo en SU dominio (kit72h-21 en amazon.es).
    - Tag internacional/OneLink: en los dominios que declare (onamz… en .com/.de/.fr…),
      nunca en amazon.es, que tiene programa propio."""
    doms = meta.get("dominios")
    if doms:
        h = host.lower()
        return any(h == d.lower() or h.endswith("." + d.lower()) for d in doms)
    return meta.get("mercado") == mercado_del_host(host)


def mercado_del_host(host):
    h = host.lower().lstrip(".")
    for sufijo, m in MERCADO_POR_DOMINIO.items():
        if h == sufijo or h.endswith("." + sufijo):
            return m
    return ""


def enlaces_de_html(texto):
    """Devuelve las URLs de los atributos de enlace (entidades ya decodificadas)."""
    out = []
    for m in ATRIBUTO_RE.finditer(texto):
        v = htmlmod.unescape(m.group(1) if m.group(1) is not None else m.group(2)).strip()
        if "amazon." in v.lower() or "amzn." in v.lower():
            out.append(v)
    return out


def enlaces_sueltos(texto):
    out = []
    for m in URL_SUELTA_RE.finditer(texto):
        v = htmlmod.unescape(m.group(0)).rstrip(".,;:")
        if "amazon." in v.lower() or "amzn." in v.lower():
            out.append(v)
    return out


def es_no_afiliado(url):
    host = urlsplit(url).netloc.lower()
    return any(c in host for c in NO_AFILIADO)


def tags_de(url):
    """Valores de `tag` en la query (decodificados). Detecta también `&amp;`."""
    q = urlsplit(url).query
    vals = parse_qs(q, keep_blank_values=True).get("tag", [])
    if not vals:  # por si viene con entidades sin decodificar
        vals = re.findall(r"(?:^|[?&])(?:amp;)?tag=([^&#]*)", htmlmod.unescape(url))
    return [v.strip() for v in vals]


def zona_de(ruta):
    """Mercado/zona a partir de la ruta publicada ('/de/blog/x/' -> 'de')."""
    p = ruta.strip("/")
    if not p:
        return "es-home"
    primero = p.split("/")[0]
    if primero in ("en-gb", "en-us", "de", "fr", "it", "nl"):
        return primero
    if primero == "blog":
        return "es-blog"
    if primero == "kit":
        return "es-kit"
    return "es-otro"


def analizar(registro, enlaces, origen, zona):
    """Clasifica cada enlace. Devuelve lista de hallazgos."""
    tags_ok = registro["tags"]
    mercados_pendientes = set(registro.get("mercadospendientes") or [])
    hallazgos = []

    def add(nivel, codigo, url, detalle):
        hallazgos.append({"nivel": nivel, "codigo": codigo, "origen": origen,
                          "zona": zona, "url": url, "detalle": detalle})

    for url in enlaces:
        if es_no_afiliado(url):
            continue
        host = urlsplit(url).netloc.lower()
        if urlsplit(url).path.startswith(("/gp/help", "/gp/customer", "/gp/legal")):
            continue                       # páginas legales/ayuda: no son afiliado
        mercado_enlace = mercado_del_host(host)
        if not mercado_enlace:            # dominio amazon raro/no mapeado
            add("ERROR", "E5", url, f"dominio de Amazon no mapeado: {host}")
            continue
        vals = tags_de(url)
        if host in ("amzn.to", "amzn.eu") or host.endswith("a.co"):
            add("AVISO", "W3", url, "enlace corto: el tag no es auditable")
            continue
        if len(set(vals)) > 1:
            add("ERROR", "E4", url, f"varios tags distintos: {sorted(set(vals))}")
            continue
        if vals and vals[0] == "":
            add("ERROR", "E4", url, "parámetro tag vacío")
            continue
        if not vals:
            # ¿hay algún Tracking ID que acredite en ESTA tienda?
            con_tag = {t for t, m in tags_ok.items() if tag_vale_en(m, host)}
            if con_tag:
                add("ERROR", "E3", url, f"sin tag y esta tienda tiene "
                                        f"{len(con_tag)} tag(s) válidos: {sorted(con_tag)}")
            elif mercado_enlace in mercados_pendientes:
                add("AVISO", "W1", url, f"mercado '{mercado_enlace}' sin Tracking ID todavía")
            else:
                add("ERROR", "E3", url, f"sin tag (mercado '{mercado_enlace}' no declarado pendiente)")
            continue
        tag = vals[0]
        meta = tags_ok.get(tag)
        if meta is None:
            add("ERROR", "E1", url, f"tag '{tag}' no está en el registro")
            continue
        if not tag_vale_en(meta, host):
            add("ERROR", "E2", url, f"tag '{tag}' ({meta.get('mercado')}) no acredita en "
                                    f"'{host}' (Amazon lo ignora: comisión 0)")
            continue
        roles = meta.get("roles") or []
        seccion = {"es-home": "home", "es-kit": "kits", "es-blog": "blog"}.get(zona, "")
        if roles and seccion and seccion not in roles:
            add("AVISO", "W2", url, f"tag '{tag}' declarado para {roles}, usado en sección '{seccion}'")
    return hallazgos


def auditar_registro(registro):
    """Coherencia entre el registro y data/mercados.json (la asignación por sección)."""
    ruta = RAIZ / "data" / "mercados.json"
    if not ruta.exists():
        return []
    mercados = json.loads(ruta.read_text(encoding="utf-8")).get("mercados") or []
    hallazgos = []

    def add(codigo, detalle):
        hallazgos.append({"nivel": "ERROR", "codigo": codigo, "origen": "data/mercados.json",
                          "zona": "registro", "url": "data/mercados.json", "detalle": detalle})

    vistos = collections.Counter()
    for m in mercados:
        if not m.get("activo", True):
            continue
        amz = m.get("amazon") or {}
        dominio = amz.get("dominio") or ""
        mercado = mercado_del_host(dominio)
        if not mercado:
            add("E6", f"mercado {m.get('id')}: dominio de Amazon no reconocido ({dominio!r})")
            continue
        asignados = [t for t in [amz.get("tag") or ""] + list((amz.get("tags") or {}).values()) if t]
        for t in set(asignados):
            vistos[t] += 1
            meta = registro["tags"].get(t)
            if meta is None:
                add("E6", f"mercado {m.get('id')}: asigna el tag '{t}', que no está en el registro")
            elif not tag_vale_en(meta, dominio):
                add("E6", f"mercado {m.get('id')} ({dominio}) asigna el tag '{t}', que no acredita "
                          f"en esa tienda → comisión 0 garantizada")
        if amz.get("tagPendiente") and asignados:
            add("E6", f"mercado {m.get('id')}: marcado tagPendiente pero asigna {sorted(set(asignados))}")
        if not amz.get("tagPendiente") and not asignados:
            add("E6", f"mercado {m.get('id')}: sin tag y no está marcado como pendiente")
    for t in registro["tags"]:
        if (registro["tags"][t] or {}).get("retirado"):
            continue          # ID retirado a propósito: sigue existiendo en Amazon, no en el sitio
        if not vistos[t]:
            hallazgos.append({"nivel": "AVISO", "codigo": "W4", "origen": "data/mercados.json",
                              "zona": "registro", "url": "data/tags-afiliado.json",
                              "detalle": f"el tag '{t}' está en el registro pero ningún mercado lo usa"})
    return hallazgos


def auditar_repo(registro):
    objetivo = []
    for p in RAIZ.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in EXT_FUENTE:
            continue
        if EXCLUIDAS & set(p.parts):
            continue
        objetivo.append(p)
    hallazgos = []
    for p in sorted(objetivo):
        rel = str(p.relative_to(RAIZ)).replace("\\", "/")
        texto = p.read_text(encoding="utf-8", errors="ignore")
        enlaces = enlaces_de_html(texto) if p.suffix.lower() in (".html", ".xml") else enlaces_sueltos(texto)
        zona = zona_de(rel) if p.suffix.lower() == ".html" else "fuente:" + rel
        hallazgos += analizar(registro, enlaces, rel, zona)
    return hallazgos, len(objetivo)


def _get(url, timeout=45, intentos=3):
    """Descarga con reintentos. Un 503 o un corte de conexión de GitHub Pages no
    es un tag roto, y un gate que se pone rojo al azar deja de mirarse."""
    ultimo = None
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; Kit72hAudit/2.0; +https://kit72h.com)",
                "Accept-Encoding": "gzip"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    import gzip
                    data = gzip.decompress(data)
                return data.decode("utf-8", "ignore")
        except Exception as e:                        # noqa: BLE001
            ultimo = e
            if i < intentos - 1:
                time.sleep(2 * (i + 1))
    raise ultimo


def auditar_vivo(registro, limite=None):
    from concurrent.futures import ThreadPoolExecutor
    xml = _get(BASE + "/sitemap.xml", timeout=60)
    paginas = re.findall(r"<loc>([^<]+)</loc>", xml)
    if limite:
        paginas = paginas[:limite]
    if not paginas:
        sys.exit("[auditar-tags] el sitemap vivo no devolvió URLs")

    def una(u):
        try:
            return u, _get(u)
        except Exception as e:                        # noqa: BLE001
            return u, "\0ERROR:" + str(e)

    hallazgos = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for url, texto in ex.map(una, paginas):
            if texto.startswith("\0ERROR:"):
                hallazgos.append({"nivel": "ERROR", "codigo": "E0", "origen": url,
                                  "zona": zona_de(urlsplit(url).path), "url": url,
                                  "detalle": "no se pudo descargar: " + texto[7:]})
                continue
            hallazgos += analizar(registro, enlaces_de_html(texto), url, zona_de(urlsplit(url).path))
    return hallazgos, len(paginas)


def informe(hallazgos, unidades, modo, json_salida=None, quiet=False):
    errores = [h for h in hallazgos if h["nivel"] == "ERROR"]
    avisos = [h for h in hallazgos if h["nivel"] == "AVISO"]
    if json_salida:
        Path(json_salida).write_text(json.dumps({"modo": modo, "unidades": unidades,
                                                 "errores": errores, "avisos": avisos},
                                                ensure_ascii=False, indent=1), encoding="utf-8")
    if quiet:
        return len(errores)
    print(f"auditar-tags · {modo} · {unidades} ficheros/páginas")
    for nivel, lista in (("ERROR", errores), ("AVISO", avisos)):
        if not lista:
            continue
        print(f"\n{nivel}: {len(lista)}")
        porcod = collections.Counter(h["codigo"] for h in lista)
        print("   " + "  ".join(f"{k}={v}" for k, v in sorted(porcod.items())))
        vistos = set()
        for h in lista:
            clave = (h["codigo"], h["detalle"])
            if clave in vistos:
                continue
            vistos.add(clave)
            if len(vistos) > 25:
                print("   … (recorte; usa --json para el listado completo)")
                break
            print(f"   [{h['codigo']}] {h['detalle']}\n        {h['origen']}\n        {h['url'][:150]}")
    if not errores and not avisos:
        print("OK — todos los enlaces de Amazon llevan un Tracking ID válido de su marketplace.")
    return len(errores)


def main():
    ap = argparse.ArgumentParser(description="Audita los Tracking IDs de afiliado de Amazon.")
    ap.add_argument("--vivo", action="store_true", help="audita el sitio publicado (sitemap)")
    ap.add_argument("--limite", type=int, help="con --vivo, primeras N páginas del sitemap")
    ap.add_argument("--json", dest="json_salida", help="escribe el informe completo en JSON")
    ap.add_argument("--quiet", action="store_true", help="solo el código de salida")
    ap.add_argument("--estricto", action="store_true", help="los avisos también fallan")
    a = ap.parse_args()

    registro = cargar_registro()
    previos = auditar_registro(registro)
    if a.vivo:
        hallazgos, n = auditar_vivo(registro, a.limite)
        modo = "sitio vivo " + BASE
    else:
        hallazgos, n = auditar_repo(registro)
        modo = "repo local"
    hallazgos = previos + hallazgos

    errores = informe(hallazgos, n, modo, a.json_salida, a.quiet)
    if a.quiet:
        print(json.dumps({"modo": modo, "unidades": n,
                          "errores": errores,
                          "avisos": sum(1 for h in hallazgos if h["nivel"] == "AVISO")}))
    if errores:
        return 1
    if a.estricto and any(h["nivel"] == "AVISO" for h in hallazgos):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
