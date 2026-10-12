#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — analíticas web: descarga métricas y normaliza a data/analiticas.json.

Proveedor principal: Cloudflare Web Analytics (RUM) vía GraphQL Analytics API.
Proveedor opcional de eventos (clics de afiliado): Umami Cloud.

Qué hace:
1. Lee credenciales de entorno (nunca hardcodeadas).
2. Descubre la cuenta de Cloudflare (env o autodescubrimiento) y el site tag
   de Web Analytics (env CF_RUM_SITE_TAG o búsqueda por 'kit72h').
3. Consulta el dataset `rumPageloadEventsAdaptiveGroups` y agrega:
   página (requestPath), referrer (refererHost), país (countryName),
   dispositivo (deviceType) y serie diaria (30 días, días sin datos = 0).
4. Si hay env de Umami, añade los eventos (p. ej. clic-amazon).
5. Escribe SIEMPRE data/analiticas.json — incluso sin credenciales — con el
   estado correspondiente, para que el dashboard pueda leerlo siempre.

Notas de robustez (el script NUNCA debe reventar, debe degradar):
- Si `sum { visits }` no está disponible, cae a `count`.
- Si una consulta falla, esa sección queda vacía y se sigue con el resto.
- Sin credenciales escribe estado 'sin-credenciales' y sale con código 0.

Solo stdlib (urllib). Sin dependencias externas.

Variables de entorno:
  CLOUDFLARE_API_TOKEN        (obligatoria para Cloudflare)
  CLOUDFLARE_ACCOUNT_ID       (opcional; si falta, se autodescubre)
  CF_RUM_SITE_TAG             (opcional; si falta, se busca por 'kit72h')
  UMAMI_API_KEY               (opcional, para eventos)
  UMAMI_WEBSITE_ID            (opcional, para eventos)
  UMAMI_HOST                  (opcional; por defecto https://api.umami.is)
  KIT72H_ANALITICAS_DIAS      (opcional; por defecto 30)

Uso:
  python3 scripts/kit72h-analiticas.py            # escribe data/analiticas.json
  python3 scripts/kit72h-analiticas.py --stdout   # solo imprime el JSON
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "data" / "analiticas.json"
CF_API = "https://api.cloudflare.com/client/v4"
CF_GRAPHQL = CF_API + "/graphql"
TIMEOUT = 30  # segundos por petición HTTP


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
    """Consulta tolerante: primero con sum{visits}; si falla, reintenta solo con count."""
    filas, err = cf_desglose(token, cuenta, site, ini, fin, dimension, orden, limite, True)
    if filas is None:
        filas, err = cf_desglose(token, cuenta, site, ini, fin, dimension, orden, limite, False)
    if filas is None and err:
        print("  ⚠️ consulta '%s' falló: %s" % (dimension, str(err)[:160]), file=sys.stderr)
    return filas or []


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


def con_pct(pares):
    """Convierte [(etiqueta, visitas)] en [{clave, visitas, pct}] con pct a 1 decimal."""
    total = sum(v for _, v in pares) or 1
    return [
        {"clave": k, "visitas": v, "pct": round(100.0 * v / total, 1)}
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


# ─────────────────────────── Umami (eventos) ──────────────────────────────

def umami_eventos():
    """Lee y agrega eventos de Umami. Devuelve lista [{nombre,total,por_pagina}] o None."""
    clave = os.environ.get("UMAMI_API_KEY")
    web_id = os.environ.get("UMAMI_WEBSITE_ID")
    if not clave or not web_id:
        return None
    host = (os.environ.get("UMAMI_HOST") or "https://api.umami.is").rstrip("/")
    ahora = datetime.now(timezone.utc)
    start = int((ahora - timedelta(days=DIAS)).timestamp() * 1000)
    end = int(ahora.timestamp() * 1000)
    url = "%s/api/websites/%s/events?startAt=%d&endAt=%d" % (host, web_id, start, end)
    data, err = http_json(url, token=clave)
    if data is None:
        if err:
            print("  ⚠️ Umami no disponible: %s" % str(err)[:160], file=sys.stderr)
        return None
    filas = data.get("data") if isinstance(data, dict) else data
    if not isinstance(filas, list) or not filas:
        return None
    acumulado = {}
    for fila in filas:
        if not isinstance(fila, dict):
            continue
        nombre = fila.get("eventName") or fila.get("event_name") or "(sin nombre)"
        ruta = fila.get("urlPath") or fila.get("url_path") or "/"
        entrada = acumulado.setdefault(nombre, {"total": 0, "paginas": {}})
        entrada["total"] += 1
        entrada["paginas"][ruta] = entrada["paginas"].get(ruta, 0) + 1
    eventos = []
    for nombre in sorted(acumulado, key=lambda n: -acumulado[n]["total"]):
        e = acumulado[nombre]
        por_pagina = [
            {"ruta": r, "total": t}
            for r, t in sorted(e["paginas"].items(), key=lambda kv: (-kv[1], kv[0]))
        ]
        eventos.append({"nombre": nombre, "total": e["total"], "por_pagina": por_pagina})
    return eventos


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
    """Escribe data/analiticas.json (salvo --stdout) e imprime el JSON si procede."""
    payload = json.dumps(resultado, ensure_ascii=False, indent=2)
    if a_stdout:
        print(payload)
        return
    try:
        SALIDA.parent.mkdir(parents=True, exist_ok=True)
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
    umami_id = os.environ.get("UMAMI_WEBSITE_ID")

    # Sin credenciales de nada → estado explícito, listas vacías, código 0.
    if not token and not (umami_key and umami_id):
        faltan = []
        if not token:
            faltan.append("CLOUDFLARE_API_TOKEN")
        if not umami_key:
            faltan.append("UMAMI_API_KEY")
        if not umami_id:
            faltan.append("UMAMI_WEBSITE_ID")
        resultado = plantilla(
            "sin-credenciales",
            "Sin credenciales de analítica; faltan: " + ", ".join(faltan) +
            ". El dashboard seguirá leyendo el fichero con totales a 0.")
        escribir(resultado, args.stdout)
        resumen(resultado)
        return 0

    # Eventos de Umami (opcional, independiente de Cloudflare).
    eventos = umami_eventos()
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
                filas_serie = cf_consultar(token, cuenta, site, ini, fin, "date",
                                           "date_ASC", 5000)

                # Serie diaria rellenando con 0 los días sin datos.
                mapa_fecha = dict(agrupar(filas_serie, "date"))
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
                resultado["paginas"] = [
                    {"ruta": k, "visitas": v, "pct": p}
                    for (k, v), p in zip(pares_pag, con_pct(pares_pag))
                ]
                resultado["referrers"] = [
                    {"origen": k, "visitas": v, "pct": p}
                    for (k, v), p in zip(pares_ref, con_pct(pares_ref))
                ]
                resultado["paises"] = [
                    {"pais": k, "visitas": v, "pct": p}
                    for (k, v), p in zip(pares_pais, con_pct(pares_pais))
                ]
                resultado["dispositivos"] = [
                    {"tipo": k, "visitas": v, "pct": p}
                    for (k, v), p in zip(pares_dev, con_pct(pares_dev))
                ]
                resultado["eventos"] = eventos or []

                if total_visitas == 0 and not filas_pag and not filas_serie:
                    resultado["estado"] = "sin-datos"
                    resultado["mensaje"] = (
                        "Cloudflare respondió pero no hay visitas en los últimos %d días "
                        "(o el site tag no recibe tráfico aún)." % DIAS)

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
