#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — analíticas web: descarga métricas y normaliza a data/analiticas.json.

Proveedor principal: **Umami Cloud** (visitas + páginas + referrers + países +
dispositivos + serie diaria + EVENTOS personalizados como `clic-amazon`).
Alternativa: Cloudflare Web Analytics (RUM) vía GraphQL, cuando no hay Umami.

Qué hace:
1. Lee credenciales de entorno (nunca hardcodeadas).
2. Con UMAMI_API_KEY: GET /websites para descubrir el websiteId (si no está en
   UMAMI_WEBSITE_ID) y consulta stats, pageviews, metrics (path/referrer/country/
   device/event) y events.
3. Sin Umami: descubre la cuenta de Cloudflare y el site tag de Web Analytics y
   consulta el dataset `rumPageloadEventsAdaptiveGroups`.
4. Escribe SIEMPRE data/analiticas.json — incluso sin credenciales — con el
   estado correspondiente, para que el dashboard pueda leerlo siempre.

Notas de robustez (el script NUNCA debe reventar, debe degradar):
- Si `sum { visits }` no está disponible, cae a `count` (camino Cloudflare).
- Si una consulta falla, esa sección queda vacía y se sigue con el resto.
- Sin credenciales escribe estado 'sin-credenciales' y sale con código 0.
- No reescribe el fichero si lo único que cambia es la marca de tiempo.

Solo stdlib (urllib). Sin dependencias externas.

Variables de entorno:
  UMAMI_API_KEY               (recomendada: activa Umami como proveedor completo)
  UMAMI_WEBSITE_ID            (opcional; si falta se autodescubre de GET /websites)
  UMAMI_HOST                  (opcional; por defecto https://api.umami.is → /v1)
  CLOUDFLARE_API_TOKEN        (alternativa si no hay Umami)
  CLOUDFLARE_ACCOUNT_ID       (opcional; si falta, se autodescubre)
  CF_RUM_SITE_TAG             (opcional; si falta, se busca por 'kit72h')
  KIT72H_ANALITICAS_DIAS      (opcional; por defecto 30)

Uso:
  python3 scripts/kit72h-analiticas.py            # escribe data/analiticas.json
  python3 scripts/kit72h-analiticas.py --stdout   # solo imprime el JSON
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "data" / "analiticas.json"
CF_API = "https://api.cloudflare.com/client/v4"
CF_GRAPHQL = CF_API + "/graphql"
TIMEOUT = 30  # segundos por petición HTTP


def _cargar_env_local():
    """Carga el .env del repo sin pisar lo que ya venga en el entorno.

    Así funciona igual lanzado a mano que desde el cron (que solo hereda el
    entorno de Hermes), y las credenciales viven en un único sitio: el .env
    del repo (ignorado por git).
    """
    ruta = RAIZ / ".env"
    if not ruta.is_file():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        clave = clave.strip()
        valor = valor.strip().strip("\"'")
        if clave and valor and clave not in os.environ:
            os.environ[clave] = valor


_cargar_env_local()


def _dias_ventana():
    """Número de días de la ventana (env KIT72H_ANALITICAS_DIAS, por defecto 30)."""
    try:
        n = int(os.environ.get("KIT72H_ANALITICAS_DIAS", "30") or "30")
    except ValueError:
        n = 30
    return n if n > 0 else 30


DIAS = _dias_ventana()


# ───────────────────────────── HTTP (stdlib) ──────────────────────────────

def http_json(url, method="GET", token=None, body=None):
    """Petición HTTP que devuelve (json|None, error|None). Nunca lanza excepción."""
    datos = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=datos, method=method)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "kit72h-analiticas/1.0")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    if datos is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            texto = resp.read().decode("utf-8", "replace")
        return json.loads(texto), None
    except urllib.error.HTTPError as exc:
        # Cloudflare devuelve errores útiles en el cuerpo aunque el HTTP falle.
        try:
            cuerpo = exc.read().decode("utf-8", "replace")
            return json.loads(cuerpo), "HTTP %s" % exc.code
        except Exception:
            return None, "HTTP %s" % exc.code
    except Exception as exc:  # timeout, DNS, TLS, JSON inválido...
        return None, str(exc)


# ──────────────────────── Cloudflare: cuenta y site ───────────────────────

def cf_cuenta(token):
    """Devuelve el account id (env CLOUDFLARE_ACCOUNT_ID o el primero de la lista)."""
    cuenta = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    if cuenta:
        return cuenta
    data, _err = http_json(CF_API + "/accounts", token=token)
    if data and data.get("result"):
        return data["result"][0].get("id")
    return None


def cf_site_tag(token, cuenta):
    """Devuelve el site tag de Web Analytics (env CF_RUM_SITE_TAG o el que tenga 'kit72h')."""
    override = os.environ.get("CF_RUM_SITE_TAG")
    if override:
        return override
    data, _err = http_json(
        "%s/accounts/%s/rum/site_info/list" % (CF_API, cuenta), token=token
    )
    sitios = (data or {}).get("result") or []
    for item in sitios:
        # El listado puede no exponer el host; buscamos 'kit72h' en todo el item.
        if "kit72h" in json.dumps(item).lower():
            tag = item.get("site_tag") or item.get("siteTag")
            if tag:
                return tag
    # Fallback tolerante: primer site con tag (mejor algo que nada).
    for item in sitios:
        tag = item.get("site_tag") or item.get("siteTag")
        if tag:
            return tag
    return None


# ─────────────────────── Cloudflare: consulta GraphQL ─────────────────────

def cf_graphql(token, query):
    """Ejecuta una consulta GraphQL y devuelve (data|None, error|None)."""
    data, err = http_json(CF_GRAPHQL, method="POST", token=token, body={"query": query})
    if not data:
        return None, err or "respuesta vacía"
    if data.get("errors"):
        msgs = "; ".join(str(e.get("message", e)) for e in data["errors"][:3])
        return None, msgs
    return data, None


def _esc(valor):
    """Escapa un valor para incrustarlo entre comillas en la query GraphQL."""
    return str(valor).replace("\\", "\\\\").replace('"', '\\"')


def cf_desglose(token, cuenta, site, ini, fin, dimension, orden, limite, con_sum):
    """Una consulta de agregación sobre una dimensión. Devuelve (filas|None, error|None)."""
    campos = "count"
    if con_sum:
        campos += "\n            sum { visits }"
    query = (
        '{ viewer { accounts(filter: {accountTag: "%s"}) {'
        ' g: rumPageloadEventsAdaptiveGroups(limit: %d,'
        ' filter: {siteTag: "%s", datetime_geq: "%s", datetime_leq: "%s"},'
        ' orderBy: [%s]) {'
        " %s"
        " dimensions { %s }"
        " } } } }"
    ) % (_esc(cuenta), limite, _esc(site), ini, fin, orden, campos, dimension)
    data, err = cf_graphql(token, query)
    if err:
        return None, err
    try:
        return data["data"]["viewer"]["accounts"][0]["g"], None
    except (KeyError, IndexError, TypeError):
        return None, "estructura inesperada en la respuesta"


def cf_consultar(token, cuenta, site, ini, fin, dimension, orden="count_DESC", limite=500):
    """Consulta tolerante con reintentos. Prefiere count; sum{visits} como fallback.

    Verificado 2026-10-19: el GraphQL de RUM de Cloudflare es intermitente
    («unable to execute query, please try again later») y con `sum { visits }`
    devuelve muestras absurdas (series de 4 fechas con cifras redondas y
    visitas=0 con count=1000). Sin `sum`, todo responde bien → primero count;
    si la intermitencia lo bloquea, se reintenta alternando y con pausa.
    """
    filas, err = None, None
    for intento, con_sum in enumerate((False, True, False, True, False)):
        filas, err = cf_desglose(token, cuenta, site, ini, fin, dimension, orden, limite, con_sum)
        if filas:
            return filas
        time.sleep(2 * (intento + 1))
    if err:
        print("  ⚠️ consulta '%s' falló: %s" % (dimension, str(err)[:160]), file=sys.stderr)
    return []


def cf_serie_diaria(token, cuenta, site, hoy, dias):
    """Serie diaria de visitas consultando por VENTANAS de 7 días y fusionando.

    TRAMPA EVITADA: una sola consulta de 30 días sobre `rumPageloadEventsAdaptiveGroups`
    devuelve los días antiguos y CORTA los recientes (comprobado 2026-10-25: pedidos
    2026-09-26..2026-10-25 devolvía hasta el 19-oct; el 20, 21 y 22 —con 9, 3 y 1
    visitas reales— salían como 0, y el panel los pintaba como caída de tráfico).
    Trocear en ventanas de 7 días devuelve todos los días. No subir VENTANA sin
    volver a comprobar la serie contra la API (último día con datos y suma total).
    Devuelve {fecha_iso: visitas}.
    """
    VENTANA = 7
    mapa = {}
    fin_dia = hoy
    while fin_dia >= hoy - timedelta(days=dias - 1):
        ini_dia = max(fin_dia - timedelta(days=VENTANA - 1), hoy - timedelta(days=dias - 1))
        filas = cf_consultar(
            token, cuenta, site,
            ini_dia.strftime("%Y-%m-%dT00:00:00Z"),
            fin_dia.strftime("%Y-%m-%dT23:59:59Z"),
            "date", "date_ASC", 5000)
        for fecha, visitas in agrupar(filas, "date"):
            mapa[fecha] = mapa.get(fecha, 0) + int(visitas)
        fin_dia = ini_dia - timedelta(days=1)
    return mapa


# ─────────────────────────── Normalización ────────────────────────────────

def visitas_de(fila):
    """Visitas de una fila: sum.visits si existe, si no count."""
    try:
        v = (fila.get("sum") or {}).get("visits")
        if v is not None:
            return int(v)
    except Exception:
        pass
    try:
        return int(fila.get("count", 0) or 0)
    except Exception:
        return 0


# ────────────── Cloudflare: analítica de ZONA (red de seguridad) ──────────
# El dataset RUM (`rumPageloadEventsAdaptiveGroups`) depende de que Web
# Analytics esté ACTIVO en la zona y de que el beacon llegue: si se desactiva,
# el endpoint de ingesta `/cdn-cgi/rum` devuelve 404 y el panel se queda a 0
# aunque la web tenga cientos de visitas (pasó el 2026-10-20: 0 visitas en el
# panel con 327-410 únicos/día reales).
#
# La analítica de ZONA (`httpRequests*Groups`) NO depende del beacon: mide lo
# que pasa por Cloudflare. Sirve de respaldo permanente. Contrapartidas que el
# panel debe decir sin adornos: incluye bots/crawlers y no hay `refererHost`
# (campo restringido en plan gratuito), así que los orígenes quedan vacíos.

CF_ZONA_NOMBRE = "kit72h.com"


def cf_zona_id(token):
    """Zone id de CF_ZONA_NOMBRE (el token del repo puede leer /zones)."""
    data, _err = http_json(CF_API + "/zones?name=" + urllib.parse.quote(CF_ZONA_NOMBRE),
                           token=token)
    for fila in ((data or {}).get("result") or []):
        if fila.get("name") == CF_ZONA_NOMBRE and fila.get("id"):
            return fila["id"]
    return None


def cf_zona_serie(token, zona, hoy, dias):
    """(serie_diaria, total_paginas) desde httpRequests1dGroups.

    `uniq.uniques` = visitantes únicos del día; `sum.pageViews` = páginas.
    Devuelve ({fecha_iso: uniques}, total_pageViews).
    """
    ini = hoy - timedelta(days=dias - 1)
    query = (
        '{ viewer { zones(filter: {zoneTag: "%s"}) {'
        ' g: httpRequests1dGroups(limit: %d,'
        ' filter: {date_geq: "%s", date_leq: "%s"}) {'
        ' dimensions { date } sum { pageViews } uniq { uniques } } } } }'
    ) % (_esc(zona), dias + 2, ini.isoformat(), hoy.isoformat())
    data, err = cf_graphql(token, query)
    mapa, paginas = {}, 0
    if err:
        print("  ⚠️ zona serie: %s" % str(err)[:140], file=sys.stderr)
        return mapa, paginas
    try:
        filas = data["data"]["viewer"]["zones"][0]["g"]
    except (KeyError, IndexError, TypeError):
        print("  ⚠️ zona serie: estructura inesperada", file=sys.stderr)
        return mapa, paginas
    for fila in filas:
        dia = (fila.get("dimensions") or {}).get("date")
        if not dia:
            continue
        try:
            mapa[str(dia)[:10]] = int(((fila.get("uniq") or {}).get("uniques")) or 0)
        except Exception:
            mapa[str(dia)[:10]] = 0
        try:
            paginas += int(((fila.get("sum") or {}).get("pageViews")) or 0)
        except Exception:
            pass
    return mapa, paginas


def cf_zona_dim(token, zona, ini, fin, dimension, limite=500):
    """Filas de httpRequestsAdaptiveGroups sobre una dimensión de la zona."""
    query = (
        '{ viewer { zones(filter: {zoneTag: "%s"}) {'
        ' g: httpRequestsAdaptiveGroups(limit: %d,'
        ' filter: {datetime_geq: "%sT00:00:00Z", datetime_leq: "%sT23:59:59Z"},'
        ' orderBy: [count_DESC]) { count dimensions { %s } } } } }'
    ) % (_esc(zona), limite, ini, fin, dimension)
    data, err = cf_graphql(token, query)
    if err:
        print("  ⚠️ zona %s: %s" % (dimension, str(err)[:140]), file=sys.stderr)
        return []
    try:
        return data["data"]["viewer"]["zones"][0]["g"] or []
    except (KeyError, IndexError, TypeError):
        return []


_EXT_ASSET = (".css", ".js", ".json", ".png", ".jpg", ".jpeg", ".webp", ".svg",
              ".ico", ".txt", ".xml", ".woff", ".woff2", ".map", ".gz")


def _es_pagina(ruta):
    """¿La ruta es una página (no un asset, ni una ruta interna, ni un reto ACME)?"""
    r = str(ruta or "")
    if not r.startswith("/") or r.startswith("/cdn-cgi/") or r.startswith("/data/"):
        return False
    if r.startswith("/.well-known"):
        return False
    bajo = r.lower().split("?")[0]
    if bajo.endswith(_EXT_ASSET):
        return False
    # Retos ACME / hostname-challenge: segmentos largos y aleatorios.
    if any(len(seg) > 24 for seg in bajo.split("/") if seg):
        return False
    return bajo.endswith("/") or bajo.endswith(".html") or "." not in bajo.rsplit("/", 1)[-1]


def cf_zona_paginas(token, zona, ini, fin):
    """Ranking de páginas de la zona, sin assets. [(ruta, pageviews)]."""
    filas = cf_zona_dim(token, zona, ini, fin, "clientRequestPath", 500)
    pares = agrupar([f for f in filas
                     if _es_pagina((f.get("dimensions") or {}).get("clientRequestPath"))],
                    "clientRequestPath",
                    lambda v: str(v or "/").replace("/index.html", "/"))
    return pares


def cf_zona_desgloses(token, zona, ini, fin):
    """Páginas, países y dispositivos coherentes entre sí, con UNA sola query.

    TRAMPA EVITADA: pedir el país o el dispositivo sin más cuenta TODOS los
    requests (CSS, JS, /cdn-cgi/rum…) y devuelve cifras 7-9× mayores que las
    visitas (`escritorio 64.960` en un panel que dice `9.580 visitas`). Se piden
    las tres dimensiones juntas y solo se suman las filas que son página.

    Devuelve (pares_paginas, pares_paises, pares_dispositivos).
    """
    query = (
        '{ viewer { zones(filter: {zoneTag: "%s"}) {'
        ' g: httpRequestsAdaptiveGroups(limit: 5000,'
        ' filter: {datetime_geq: "%sT00:00:00Z", datetime_leq: "%sT23:59:59Z"},'
        ' orderBy: [count_DESC]) {'
        ' count dimensions { clientRequestPath clientCountryName clientDeviceType }'
        ' } } } }'
    ) % (_esc(zona), ini, fin)
    data, err = cf_graphql(token, query)
    if err:
        print("  ⚠️ zona desgloses: %s" % str(err)[:140], file=sys.stderr)
        return [], [], []
    try:
        filas = data["data"]["viewer"]["zones"][0]["g"] or []
    except (KeyError, IndexError, TypeError):
        return [], [], []
    acum = {"ruta": {}, "pais": {}, "tipo": {}}
    for fila in filas:
        dims = fila.get("dimensions") or {}
        ruta = dims.get("clientRequestPath")
        if not _es_pagina(ruta):
            continue
        try:
            n = int(fila.get("count") or 0)
        except Exception:
            continue
        ruta = str(ruta).replace("/index.html", "/")
        pais = str(dims.get("clientCountryName") or "(desconocido)")
        tipo = norm_dispositivo(dims.get("clientDeviceType"))
        for clave, valor in (("ruta", ruta), ("pais", pais), ("tipo", tipo)):
            acum[clave][valor] = acum[clave].get(valor, 0) + n
    orden = {k: sorted(v.items(), key=lambda kv: (-kv[1], kv[0]))
             for k, v in acum.items()}
    return orden["ruta"], orden["pais"], orden["tipo"]


def cf_zona_resultado(token, hoy, clics_amazon, motivo, eventos=None,
                      zona=None, mapa=None, total_paginas=None):
    """Resultado completo usando la analítica de zona (sin beacon).

    Acepta la serie ya consultada (`zona`, `mapa`, `total_paginas`) para no
    repetir la query cuando el que llama ya la tiene.

    Devuelve None si la zona no se puede leer o no trae ni una visita: en ese
    caso el que llama conserva lo que tuviera (nunca se empeora el panel).
    """
    zona = zona or cf_zona_id(token)
    if not zona:
        print("  ⚠️ zona: no se pudo resolver el zone id de %s" % CF_ZONA_NOMBRE,
              file=sys.stderr)
        return None
    if mapa is None:
        mapa, total_paginas = cf_zona_serie(token, zona, hoy, DIAS)
    if not mapa:
        return None
    ini = (hoy - timedelta(days=DIAS - 1)).isoformat()
    fin = hoy.isoformat()
    serie = [{"fecha": (hoy - timedelta(days=i)).isoformat(),
              "visitas": int(mapa.get((hoy - timedelta(days=i)).isoformat(), 0))}
             for i in range(DIAS - 1, -1, -1)]
    total_visitas = sum(p["visitas"] for p in serie)
    if total_visitas == 0:
        return None

    pares_pag, pares_pais, pares_dev = cf_zona_desgloses(token, zona, ini, fin)
    if not pares_pag:
        pares_pag = cf_zona_paginas(token, zona, ini, fin)

    resultado = plantilla(
        "ok",
        "%s Se está midiendo con la analítica de ZONA de Cloudflare (sin beacon): "
        "cuenta todo el tráfico que pasa por la CDN, incluidos bots, y no puede "
        "desglosar orígenes ni clics a Amazon." % motivo,
        fuente="cloudflare-zona")
    resultado["totales"] = {
        "visitas": total_visitas,
        "paginas": total_paginas or sum(v for _, v in pares_pag),
        "clics_amazon": clics_amazon,
    }
    resultado["serie_diaria"] = serie
    resultado["paginas"] = con_pct_sobre(pares_pag, "ruta", limite=30)
    resultado["referrers"] = []
    resultado["paises"] = con_pct_sobre(pares_pais, "pais", limite=20)
    resultado["dispositivos"] = con_pct_sobre(pares_dev, "tipo")
    resultado["eventos"] = eventos or []
    return resultado


def paginas_vistas_de(fila):
    """Páginas vistas de una fila (campo `count`)."""
    try:
        return int(fila.get("count", 0) or 0)
    except Exception:
        return 0


def agrupar(filas, clave, normaliza=None):
    """Agrupa filas por una dimensión sumando visitas. Devuelve [(etiqueta, visitas)]."""
    acumulado = {}
    for fila in filas:
        dims = fila.get("dimensions") or {}
        valor = dims.get(clave)
        if normaliza:
            valor = normaliza(valor)
        if valor in (None, ""):
            valor = "(desconocido)"
        valor = str(valor)
        acumulado[valor] = acumulado.get(valor, 0) + visitas_de(fila)
    return sorted(acumulado.items(), key=lambda kv: (-kv[1], kv[0]))


def con_pct(pares, clave):
    """[(etiqueta, visitas)] → [{clave: etiqueta, 'visitas': v, 'pct': float}].

    OJO: el dashboard lee `pct` como NÚMERO. Antes se metía aquí el dict entero
    de con_pct y el panel pintaba el porcentaje como objeto (bug detectado el
    2026-10-12 con el arnés de pruebas de Umami).
    """
    total = sum(v for _, v in pares) or 1
    return [
        {clave: k, "visitas": v, "pct": round(100.0 * v / total, 1)}
        for k, v in pares
    ]


def con_pct_sobre(pares, clave, total=None, limite=None):
    """Como con_pct, pero con el % sobre un total dado (y recorte opcional).

    El panel de zona puede traer 200 rutas: se muestran las 30 primeras, pero
    el porcentaje se calcula sobre TODO el tráfico, no sobre el top (si no, el
    top sumaría 100 % y parecería que la home es el 44 % de 30 páginas).
    """
    total = total or sum(v for _, v in pares) or 1
    if limite:
        pares = pares[:limite]
    return [
        {clave: k, "visitas": v, "pct": round(100.0 * v / total, 1)}
        for k, v in pares
    ]


def norm_referrer(valor):
    """'' o null → '(directo)'."""
    return "(directo)" if valor in (None, "") else valor


def norm_dispositivo(valor):
    """Traduce el deviceType de Cloudflare a etiqueta en español."""
    tabla = {"desktop": "escritorio", "mobile": "móvil", "tablet": "tableta"}
    if valor in (None, ""):
        return "(desconocido)"
    return tabla.get(str(valor).lower(), valor)


# ─────────────────────────── Umami (proveedor completo) ───────────────────
# API real de Umami Cloud (docs.umami.is, contrastada el 2026-10-12):
#   base   : https://api.umami.is/v1      (en self-hosted sería /api)
#   auth   : Authorization: Bearer <API key>   (Settings > API keys)
#   GET /websites                              → lista (permite autodescubrir el websiteId)
#   GET /websites/{id}/stats?startAt&endAt     → visits, pageviews, visitors, bounces…
#   GET /websites/{id}/pageviews?…&unit=day    → {pageviews:[{x,y}], sessions:[…]}
#   GET /websites/{id}/metrics?type=<dim>&limit → [{x,y}]  (path|referrer|country|device|event)
#   GET /websites/{id}/events?…&event=<nombre> → {data:[{urlPath,eventName,…}]}
# Los timestamps van en MILISEGUNDOS. Los eventos personalizados
# (`clic-amazon`, `scroll-50/90`) llegan por /metrics?type=event y el desglose
# por página por /events?event=<nombre> — de ahí sale el CTR a Amazon por página.

PAISES_ES = {
    "ES": "España", "MX": "México", "AR": "Argentina", "CO": "Colombia",
    "CL": "Chile", "PE": "Perú", "VE": "Venezuela", "EC": "Ecuador",
    "US": "Estados Unidos", "GB": "Reino Unido", "FR": "Francia",
    "DE": "Alemania", "IT": "Italia", "PT": "Portugal", "NL": "Países Bajos",
    "BE": "Bélgica", "BR": "Brasil", "UY": "Uruguay", "CR": "Costa Rica",
}


def umami_base():
    """Base de la API: Umami Cloud sirve bajo /v1, self-hosted bajo /api."""
    host = (os.environ.get("UMAMI_HOST") or "https://api.umami.is").rstrip("/")
    if not (host.endswith("/v1") or host.endswith("/api")):
        host += "/v1"
    return host


def umami_ventana_ms():
    """(inicio, fin) en milisegundos de la ventana de DIAS días."""
    ahora = datetime.now(timezone.utc)
    return (int((ahora - timedelta(days=DIAS)).timestamp() * 1000),
            int(ahora.timestamp() * 1000))


def umami_web_id(base, clave):
    """UMAMI_WEBSITE_ID del entorno; si falta, lo autodescubre de GET /websites."""
    web_id = os.environ.get("UMAMI_WEBSITE_ID")
    if web_id:
        return web_id
    data, err = http_json(base + "/websites", token=clave)
    filas = data.get("data") if isinstance(data, dict) else data
    if not isinstance(filas, list):
        print("  ⚠️ Umami /websites: %s" % (str(err or data)[:160]), file=sys.stderr)
        return None
    candidatos = [f for f in filas if isinstance(f, dict)]
    for f in candidatos:
        if "kit72h" in json.dumps(f, ensure_ascii=False).lower():
            return f.get("id") or f.get("websiteId")
    # sin coincidencia: si solo hay una web, se asume que es esa
    return (candidatos[0].get("id") or candidatos[0].get("websiteId")) if len(candidatos) == 1 else None


def _umami_valor(bloque):
    """Los stats vienen como {'value': N, 'prev': M}: nos quedamos con value."""
    if isinstance(bloque, dict):
        bloque = bloque.get("value")
    try:
        return int(bloque or 0)
    except Exception:
        return 0


def _umami_metricas(base, clave, web_id, tipo, ini, fin, limite=25):
    """Ranking de una dimensión → [(etiqueta, visitas)]."""
    url = "%s/websites/%s/metrics?type=%s&limit=%d&startAt=%d&endAt=%d" % (
        base, web_id, tipo, limite, ini, fin)
    data, err = http_json(url, token=clave)
    if not isinstance(data, list):
        print("  ⚠️ Umami metrics %s: %s" % (tipo, str(err or data)[:120]), file=sys.stderr)
        return []
    pares = []
    for fila in data:
        if not isinstance(fila, dict):
            continue
        try:
            pares.append((str(fila.get("x")), int(fila.get("y") or 0)))
        except Exception:
            continue
    return pares


def _umami_serie(base, clave, web_id, ini, fin):
    """Serie diaria de páginas vistas → [{'fecha', 'visitas'}] con días a 0."""
    url = "%s/websites/%s/pageviews?startAt=%d&endAt=%d&unit=day" % (base, web_id, ini, fin)
    data, err = http_json(url, token=clave)
    mapa = {}
    if isinstance(data, dict):
        for fila in (data.get("pageviews") or []):
            if isinstance(fila, dict):
                mapa[str(fila.get("x"))[:10]] = int(fila.get("y") or 0)
    elif err:
        print("  ⚠️ Umami pageviews: %s" % str(err)[:120], file=sys.stderr)
    hoy = datetime.now(timezone.utc).date()
    return [{"fecha": (hoy - timedelta(days=i)).isoformat(),
             "visitas": mapa.get((hoy - timedelta(days=i)).isoformat(), 0)}
            for i in range(DIAS - 1, -1, -1)]


def _umami_eventos_por_pagina(base, clave, web_id, nombre, ini, fin):
    """Desglose de un evento por página (urlPath), de mayor a menor."""
    url = "%s/websites/%s/events?startAt=%d&endAt=%d&event=%s&pageSize=500" % (
        base, web_id, ini, fin, urllib.parse.quote(nombre))
    data, err = http_json(url, token=clave)
    filas = data.get("data") if isinstance(data, dict) else data
    if not isinstance(filas, list):
        return []
    acumulado = {}
    for fila in filas:
        if not isinstance(fila, dict):
            continue
        ruta = fila.get("urlPath") or "/"
        ruta = str(ruta).replace("/index.html", "/") or "/"
        acumulado[ruta] = acumulado.get(ruta, 0) + 1
    return [{"ruta": r, "total": t}
            for r, t in sorted(acumulado.items(), key=lambda kv: (-kv[1], kv[0]))]


def umami_eventos(base=None, clave=None, web_id=None):
    """Eventos agregados [{nombre,total,por_pagina}] o None si no hay nada."""
    clave = clave or os.environ.get("UMAMI_API_KEY")
    if not clave:
        return None
    base = base or umami_base()
    web_id = web_id or umami_web_id(base, clave)
    if not web_id:
        return None
    ini, fin = umami_ventana_ms()
    nombres = _umami_metricas(base, clave, web_id, "event", ini, fin, 25)
    eventos = []
    for nombre, total in nombres:
        eventos.append({
            "nombre": nombre,
            "total": total,
            "por_pagina": _umami_eventos_por_pagina(base, clave, web_id, nombre, ini, fin),
        })
    return eventos or None


def umami_completo():
    """Proveedor completo: visitas, páginas, referrers, países, dispositivos,
    serie diaria y eventos. Devuelve el `resultado` listo para escribir, o None
    si Umami no responde (para que main() pueda caer a Cloudflare)."""
    clave = os.environ.get("UMAMI_API_KEY")
    if not clave:
        return None
    base = umami_base()
    web_id = umami_web_id(base, clave)
    if not web_id:
        print("  ⚠️ Umami: no se pudo determinar el websiteId (define UMAMI_WEBSITE_ID).",
              file=sys.stderr)
        return None
    ini, fin = umami_ventana_ms()

    stats, err = http_json(
        "%s/websites/%s/stats?startAt=%d&endAt=%d" % (base, web_id, ini, fin), token=clave)
    if not isinstance(stats, dict):
        print("  ⚠️ Umami stats: %s" % str(err or "respuesta inesperada")[:160], file=sys.stderr)
        return None

    visitas = _umami_valor(stats.get("visits"))
    paginas_vistas = _umami_valor(stats.get("pageviews"))

    pares_pag = _umami_metricas(base, clave, web_id, "path", ini, fin, 25)
    pares_ref = [(norm_referrer(k), v) for k, v in _umami_metricas(base, clave, web_id, "referrer", ini, fin, 15)]
    pares_pais = [((PAISES_ES.get(k.upper(), k) if len(k) == 2 else k), v)
                  for k, v in _umami_metricas(base, clave, web_id, "country", ini, fin, 15)]
    pares_dev = [(norm_dispositivo(k), v) for k, v in _umami_metricas(base, clave, web_id, "device", ini, fin, 10)]

    eventos = umami_eventos(base, clave, web_id) or []
    clics_amazon = sum(e["total"] for e in eventos if "amazon" in e["nombre"].lower())

    serie = _umami_serie(base, clave, web_id, ini, fin)

    resultado = plantilla("ok", "Métricas de Umami leídas correctamente.", fuente="umami")
    resultado["totales"] = {
        "visitas": visitas,
        "paginas": paginas_vistas,
        "clics_amazon": clics_amazon,
    }
    resultado["serie_diaria"] = serie
    resultado["paginas"] = con_pct(pares_pag, "ruta")
    resultado["referrers"] = con_pct(pares_ref, "origen")
    resultado["paises"] = con_pct(pares_pais, "pais")
    resultado["dispositivos"] = con_pct(pares_dev, "tipo")
    resultado["eventos"] = eventos

    if visitas == 0 and paginas_vistas == 0:
        resultado["estado"] = "sin-datos"
        resultado["mensaje"] = (
            "Umami respondió pero no hay visitas en los últimos %d días "
            "(el beacon acaba de instalarse o la web aún no recibe tráfico)." % DIAS)
    return resultado


# ───────────────────────────── Salida ─────────────────────────────────────

def plantilla(estado, mensaje, fuente="ninguna"):
    """Estructura de salida con todos los campos del contrato a cero/lista vacía."""
    return {
        "generado": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fuente": fuente,
        "estado": estado,
        "mensaje": mensaje,
        "ventana_dias": DIAS,
        "totales": {"visitas": 0, "paginas": 0, "clics_amazon": 0},
        "serie_diaria": [],
        "paginas": [],
        "referrers": [],
        "paises": [],
        "dispositivos": [],
        "eventos": [],
    }


def escribir(resultado, a_stdout):
    """Escribe data/analiticas.json (salvo --stdout) e imprime el JSON si procede.

    No reescribe el fichero si lo único que cambia es la marca de tiempo: el
    cron diario no debe dejar un commit vacío (y un push) cada día. Sin datos
    nuevos, el panel conserva el fichero anterior.
    """
    payload = json.dumps(resultado, ensure_ascii=False, indent=2)
    if a_stdout:
        print(payload)
        return
    try:
        SALIDA.parent.mkdir(parents=True, exist_ok=True)
        if SALIDA.exists():
            try:
                previo = json.loads(SALIDA.read_text(encoding="utf-8"))
                a = dict(previo)
                b = dict(resultado)
                a.pop("generado", None)
                b.pop("generado", None)
                if a == b:
                    return  # mismos datos: se deja el fichero como estaba
            except Exception:
                pass
        SALIDA.write_text(payload + "\n", encoding="utf-8")
    except Exception as exc:
        print("  ⚠️ no se pudo escribir %s: %s" % (SALIDA, exc), file=sys.stderr)


def resumen(resultado):
    """Resumen de 5 líneas para el log del cron."""
    t = resultado["totales"]
    print("=== kit72h analíticas · %s · ventana %d días ===" % (
        resultado["generado"], resultado["ventana_dias"]))
    print("Estado: %s (%s) — %s" % (
        resultado["estado"], resultado["fuente"], resultado["mensaje"]))
    print("Totales: %d visitas · %d páginas vistas · %d clics Amazon" % (
        t["visitas"], t["paginas"], t["clics_amazon"]))
    top_pag = resultado["paginas"][:3]
    top_ref = resultado["referrers"][:3]
    print("Top páginas: " + (
        " · ".join("%s (%d)" % (p["ruta"], p["visitas"]) for p in top_pag)
        if top_pag else "(sin datos)"))
    print("Top referrers: " + (
        " · ".join("%s (%d)" % (r["origen"], r["visitas"]) for r in top_ref)
        if top_ref else "(sin datos)"))


# ────────────────────────────── Principal ─────────────────────────────────

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Descarga y normaliza las analíticas web de kit72h a data/analiticas.json.")
    ap.add_argument("--stdout", action="store_true",
                    help="No escribir el fichero; solo imprimir el JSON por stdout.")
    args = ap.parse_args(argv)

    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    umami_key = os.environ.get("UMAMI_API_KEY")

    # Sin credenciales de nada → estado explícito, listas vacías, código 0.
    if not token and not umami_key:
        resultado = plantilla(
            "sin-credenciales",
            "Sin credenciales de analítica. Falta UMAMI_API_KEY (Umami Cloud; el "
            "websiteId se autodescubre) o, en su lugar, CLOUDFLARE_API_TOKEN + "
            "CLOUDFLARE_ACCOUNT_ID. El dashboard seguirá leyendo el fichero con totales a 0.")
        escribir(resultado, args.stdout)
        resumen(resultado)
        return 0

    # ── Umami: proveedor COMPLETO (visitas + páginas + eventos) si hay clave ──
    if umami_key:
        completo = umami_completo()
        if completo is not None:
            escribir(completo, args.stdout)
            resumen(completo)
            return 0
        if not token:
            resultado = plantilla(
                "error",
                "Umami no respondió (revisa UMAMI_API_KEY, UMAMI_WEBSITE_ID y UMAMI_HOST) "
                "y no hay CLOUDFLARE_API_TOKEN alternativo.")
            escribir(resultado, args.stdout)
            resumen(resultado)
            return 0

    # Eventos de Umami para el camino de Cloudflare (Umami = visitas, CF = eventos).
    eventos = umami_eventos() if umami_key else None
    clics_amazon = 0
    if eventos:
        clics_amazon = sum(e["total"] for e in eventos if "amazon" in e["nombre"].lower())

    # ── Recorrido Cloudflare (proveedor principal) ──
    if token:
        ahora = datetime.now(timezone.utc)
        hoy = ahora.date()
        ini = (hoy - timedelta(days=DIAS - 1)).strftime("%Y-%m-%dT00:00:00Z")
        fin = hoy.strftime("%Y-%m-%dT23:59:59Z")

        cuenta = cf_cuenta(token)
        if not cuenta:
            resultado = plantilla(
                "error",
                "No se pudo determinar la cuenta de Cloudflare: CLOUDFLARE_ACCOUNT_ID ausente "
                "y el autodescubrimiento (GET /accounts) falló.")
        else:
            site = cf_site_tag(token, cuenta)
            if not site:
                resultado = plantilla(
                    "error",
                    "No se encontró ningún site tag de Web Analytics en la cuenta de Cloudflare "
                    "(define CF_RUM_SITE_TAG para forzarlo).")
            else:
                filas_pag = cf_consultar(token, cuenta, site, ini, fin, "requestPath",
                                         "count_DESC", 500)
                filas_ref = cf_consultar(token, cuenta, site, ini, fin, "refererHost",
                                         "count_DESC", 500)
                filas_pais = cf_consultar(token, cuenta, site, ini, fin, "countryName",
                                          "count_DESC", 500)
                filas_dev = cf_consultar(token, cuenta, site, ini, fin, "deviceType",
                                         "count_DESC", 50)

                # Serie diaria por ventanas de 7 días (ver cf_serie_diaria: una sola
                # consulta de 30 días corta los días recientes) y relleno con 0.
                mapa_fecha = cf_serie_diaria(token, cuenta, site, hoy, DIAS)
                serie = []
                for i in range(DIAS - 1, -1, -1):
                    dia = (hoy - timedelta(days=i)).isoformat()
                    serie.append({"fecha": dia, "visitas": int(mapa_fecha.get(dia, 0))})

                pares_pag = agrupar(filas_pag, "requestPath")
                pares_ref = agrupar(filas_ref, "refererHost", norm_referrer)
                pares_pais = agrupar(filas_pais, "countryName")
                pares_dev = agrupar(filas_dev, "deviceType", norm_dispositivo)

                total_visitas = sum(p["visitas"] for p in serie)
                total_paginas = sum(paginas_vistas_de(f) for f in filas_pag)

                resultado = plantilla(
                    "ok", "Métricas de Cloudflare Web Analytics leídas correctamente.",
                    fuente="cloudflare")
                resultado["totales"] = {
                    "visitas": total_visitas,
                    "paginas": total_paginas,
                    "clics_amazon": clics_amazon,
                }
                resultado["serie_diaria"] = serie
                resultado["paginas"] = con_pct(pares_pag, "ruta")
                resultado["referrers"] = con_pct(pares_ref, "origen")
                resultado["paises"] = con_pct(pares_pais, "pais")
                resultado["dispositivos"] = con_pct(pares_dev, "tipo")
                resultado["eventos"] = eventos or []

                if total_visitas == 0 and not filas_pag and not serie:
                    resultado["estado"] = "sin-datos"
                    resultado["mensaje"] = (
                        "Cloudflare respondió pero no hay visitas en los últimos %d días "
                        "(o el site tag no recibe tráfico aún)." % DIAS)

                # ── Contraste con la ZONA (mide todo el tráfico de la CDN) ──
                # El RUM depende del beacon: si Web Analytics se apaga o el beacon
                # no llega, el panel marca 0 con la web llena. La zona no depende
                # de nada: es lo que pasa por Cloudflare. Se guarda SIEMPRE como
                # contraste y, si el beacon está claramente caído, se usa como
                # fuente principal en vez de mentir con ceros.
                zona = cf_zona_id(token)
                if zona:
                    mapa_zona, pag_zona = cf_zona_serie(token, zona, hoy, DIAS)
                    if mapa_zona:
                        serie_zona = [
                            {"fecha": (hoy - timedelta(days=i)).isoformat(),
                             "visitas": int(mapa_zona.get(
                                 (hoy - timedelta(days=i)).isoformat(), 0))}
                            for i in range(DIAS - 1, -1, -1)]
                        reb_zona = sum(p["visitas"] for p in serie_zona[-3:])
                        reb_rum = sum(p["visitas"] for p in serie[-3:])
                        cobertura = (round(100.0 * reb_rum / reb_zona, 1)
                                     if reb_zona else None)
                        resultado["zona"] = {
                            "totales": {"visitas": sum(p["visitas"] for p in serie_zona),
                                        "paginas": pag_zona},
                            "serie_diaria": serie_zona,
                            "cobertura_ultimos_3_dias_pct": cobertura,
                        }
                        if reb_zona >= 50 and reb_rum < 10:
                            respaldo = cf_zona_resultado(
                                token, hoy, clics_amazon,
                                "El beacon de Cloudflare Web Analytics está caído "
                                "(últimos 3 días: %d medidos frente a %d reales en la CDN)."
                                % (reb_rum, reb_zona),
                                eventos=eventos, zona=zona, mapa=mapa_zona,
                                total_paginas=pag_zona)
                            if respaldo:
                                resultado = respaldo
                                print("  ℹ️ beacon caído: fuente = analítica de zona.",
                                      file=sys.stderr)
                        elif cobertura is not None and cobertura < 50:
                            resultado["mensaje"] += (
                                " Ojo: el beacon solo ve el %s %% del tráfico real "
                                "de la CDN (incluye bots)." % cobertura)

    else:
        # Sin Cloudflare pero con Umami: usar lo que haya.
        if eventos:
            resultado = plantilla(
                "ok", "Solo se pudieron leer los eventos de Umami (falta CLOUDFLARE_API_TOKEN).",
                fuente="umami")
            resultado["eventos"] = eventos
            resultado["totales"]["clics_amazon"] = clics_amazon
        else:
            resultado = plantilla(
                "error",
                "Sin CLOUDFLARE_API_TOKEN y no se pudieron leer eventos de Umami "
                "(revisa UMAMI_API_KEY/UMAMI_WEBSITE_ID o UMAMI_HOST).",
                fuente="ninguna")

    escribir(resultado, args.stdout)
    resumen(resultado)
    return 0


if __name__ == "__main__":
    sys.exit(main())
