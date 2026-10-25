#!/usr/bin/env python3
"""Kit72h — noticias: recolector de lo que está pasando AHORA.

Dos fuentes, las dos gratuitas y sin clave:

1. Google News RSS (edición España) para cuatro bloques:
   - paises que piden a su población tener provisiones
   - incendios
   - inundaciones
   - apagones / red eléctrica
2. AEMET (Meteoalerta): avisos oficiales por zona. La página de avisos
   publica un tar.gz de geojson con las zonas en alerta y su nivel; de ahí
   salen los polígonos que pinta /zona/ y el resumen por provincia.

Salidas (fuente de verdad del sitio, se commitean):
  data/noticias.json     -> titulares por bloque + meta
  data/alertas-es.json   -> niveles por provincia/zona + geometrías

Reglas:
  - Nunca se pisa un bloque con una lista vacía: si una fuente falla, se
    conserva lo último bueno y se anota el fallo en meta.aviso.
  - Todo lo que se escribe es dato real con fecha; nada inventado.
  - Se ejecuta desde el cron (script puro, 0 tokens).
"""
from __future__ import annotations

import io
import json
import re
import sys
import tarfile
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parents[1]
DATA = RAIZ / "data"
TZ = ZoneInfo("Europe/Madrid")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

TEMAS = [
    {
        "id": "provisiones",
        "titulo": "Países que piden provisiones",
        "claim": "Gobiernos diciendo a sus ciudadanos que tengan casa, agua y comida para tres días.",
        "consultas": [
            "provisiones emergencia gobierno",
            "kit de emergencia 72 horas",
            "preparación civil 72 horas hogares",
            "reservas de emergencia población",
        ],
        "claves": ["provisi", "kit de emergencia", "kit de supervivencia", "reservas",
                   "72 horas", "preparad", "prepararse", "almacen", "acopio",
                   "autoprotec", "abastec", "suministros", "supervivencia"],
        "max": 8,
    },
    {
        "id": "incendios",
        "ambito_es": True,
        "titulo": "Incendios",
        "claim": "Fuegos activos, evacuaciones y superficie quemada en España.",
        "consultas": [
            "incendio forestal España",
            "incendio activo evacuados",
            "incendios hectáreas quemadas España",
        ],
        "claves": ["incendio", "fuego", "forestal", "quemad", "evacuad", "extinguid",
                   "brigadista", "llamas", "desaloj"],
        "max": 8,
    },
    {
        "id": "inundaciones",
        "ambito_es": True,
        "titulo": "Inundaciones",
        "claim": "DANA, riadas, desbordamientos y avisos por lluvia.",
        "consultas": [
            "inundaciones España",
            "dana inundación España",
            "riada desbordamiento río",
        ],
        "claves": ["inundac", "dana", "riada", "desbord", "lluvia", "temporal",
                   "crecida", "barranco", "avenida", "anegad", "desaloj", "evacuad"],
        "max": 8,
    },
    {
        "id": "apagones",
        "ambito_es": True,
        "titulo": "Apagones y red eléctrica",
        "claim": "Cortes de luz, tensión en la red y lo que dice Red Eléctrica.",
        "consultas": [
            "apagón España",
            "corte de luz España",
            "Red Eléctrica apagón riesgo",
        ],
        "claves": ["apagón", "apagon", "corte de luz", "corte eléctrico", "red eléctrica",
                   "suministro eléctrico", "microcorte", "cero energético", "blackout"],
        "max": 8,
    },
]

VENTANA_DIAS = 30

# Para incendios, inundaciones y apagones el sitio habla de España: si el
# titular no menciona nada de aquí, no entra (evita «incendio en California»
# y «tormenta en Estados Unidos»).
TOPONIMOS_ES = [
    "espana", "espanol", "espanola", "nacional", "peninsula", "canarias",
    "baleares", "andalucia", "aragon", "asturias", "cantabria", "castilla",
    "cataluna", "valencia", "extremadura", "galicia", "madrid", "murcia",
    "navarra", "pais vasco", "rioja", "ceuta", "melilla", "aemet", "112",
    "red electrica", "proteccion civil", "ume", "dana", "guadalquivir", "ebro",
    "jucar", "turia", "segura", "duero", "tajo", "genil", "llobregat",
    "almeria", "cadiz", "cordoba", "granada", "huelva", "jaen", "malaga",
    "sevilla", "huesca", "teruel", "zaragoza", "albacete", "ciudad real",
    "cuenca", "guadalajara", "toledo", "avila", "burgos", "leon", "palencia",
    "salamanca", "segovia", "soria", "valladolid", "zamora", "barcelona",
    "girona", "lleida", "tarragona", "alicante", "castellon", "badajoz",
    "caceres", "coruna", "lugo", "ourense", "pontevedra", "mallorca",
    "menorca", "ibiza", "tenerife", "gran canaria", "lanzarote", "fuerteventura",
    "bizkaia", "gipuzkoa", "alava", "asturiano", "cantabro", "gallego",
    "valenciano", "andaluz", "aragonés", "aragonés", "madrileno", "catalan",
]


# ─────────────────────────── utilidades ───────────────────────────

def sin_acentos(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn").lower()


def bajar(url: str, timeout: int = 25, cabeceras: dict | None = None) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(cabeceras or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def iso(dt: datetime) -> str:
    return dt.astimezone(TZ).isoformat(timespec="seconds")


def fecha_corta(dt: datetime) -> str:
    meses = ["ene", "feb", "mar", "abr", "may", "jun",
             "jul", "ago", "sep", "oct", "nov", "dic"]
    return f"{dt.astimezone(TZ).day} {meses[dt.astimezone(TZ).month - 1]}"


# ─────────────────────────── 1. prensa (RSS) ───────────────────────────

def _limpia_html(s: str, tope: int = 220) -> str:
    t = re.sub(r"<[^>]+>", " ", s or "")
    t = re.sub(r"\s+", " ", t).strip()
    return t[:tope].rsplit(" ", 1)[0] + "…" if len(t) > tope else t


def _fecha(pub: str):
    try:
        dt = parsedate_to_datetime(pub)
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def leer_bing(consulta: str, timeout: int = 20) -> list[dict]:
    """Bing News RSS: enlace real del medio (el de Google es un redirect suyo)."""
    url = ("https://www.bing.com/news/search?q=" + urllib.parse.quote_plus(consulta)
           + "&format=RSS&setlang=es&cc=ES")
    arbol = ET.fromstring(bajar(url, timeout=timeout))
    salida = []
    for it in arbol.findall(".//item"):
        titulo = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        if not titulo or not link:
            continue
        dt = _fecha(it.findtext("pubDate") or "")
        if not dt:
            continue
        # Bing envuelve el enlace: apiclick.aspx?...&url=<destino percent-encoded>
        real = link
        m = re.search(r"[?&]url=([^&]+)", link)
        if m:
            real = urllib.parse.unquote(m.group(1))
        fuente = ""
        for hijo in it:
            if hijo.tag.endswith("}Source") or hijo.tag.endswith(":Source"):
                fuente = (hijo.text or "").strip()
        salida.append({
            "titulo": titulo,
            "url": real,
            "fuente": fuente or "Prensa",
            "resumen": _limpia_html(it.findtext("description") or ""),
            "fecha": iso(dt),
            "fecha_txt": fecha_corta(dt),
            "_dt": dt,
        })
    return salida


def leer_google(consulta: str, timeout: int = 20) -> list[dict]:
    """Google News RSS: segunda fuente (más volumen, enlace con redirect)."""
    url = ("https://news.google.com/rss/search?q=" + urllib.parse.quote_plus(consulta)
           + "&hl=es&gl=ES&ceid=ES:es")
    arbol = ET.fromstring(bajar(url, timeout=timeout))
    salida = []
    for it in arbol.findall(".//item"):
        titulo = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        dt = _fecha(it.findtext("pubDate") or "")
        if not titulo or not link or not dt:
            continue
        fuente = it.findtext("source") or ""
        if fuente and titulo.endswith(" - " + fuente):
            titulo = titulo[: -len(" - " + fuente)].strip()
        salida.append({"titulo": titulo, "url": link, "fuente": fuente or "Google News",
                       "resumen": "", "fecha": iso(dt), "fecha_txt": fecha_corta(dt),
                       "_dt": dt})
    return salida


def recolectar_tema(tema: dict, fallos: list[str]) -> list[dict]:
    vistos: dict[str, dict] = {}
    limite = datetime.now(timezone.utc) - timedelta(days=VENTANA_DIAS)
    for consulta in tema["consultas"]:
        items = []
        for lector, nombre in ((leer_bing, "bing"), (leer_google, "google")):
            try:
                items += lector(consulta)
            except Exception as e:  # red, 429, XML roto… se anota y se sigue
                fallos.append(f"{tema['id']}/{nombre}/{consulta}: {type(e).__name__}")
        for it in items:
            if it["_dt"] < limite:
                continue
            texto = sin_acentos(it["titulo"] + " " + (it.get("resumen") or ""))
            if not any(k in texto for k in [sin_acentos(k) for k in tema["claves"]]):
                continue
            if tema.get("ambito_es") and not any(t in texto for t in TOPONIMOS_ES):
                continue
            clave = re.sub(r"\W+", " ", sin_acentos(it["titulo"])).strip()[:70]
            previo = vistos.get(clave)
            # gana el más reciente; a igualdad, el que trae enlace directo (Bing)
            if (previo is None or it["_dt"] > previo["_dt"]
                    or (it["_dt"] == previo["_dt"] and not previo["url"].startswith("https://news.google"))):
                vistos[clave] = it
    lista = sorted(vistos.values(), key=lambda x: x["_dt"], reverse=True)[: tema["max"]]
    for it in lista:
        it.pop("_dt", None)
    return lista


# ─────────────────────────── 2. AEMET ───────────────────────────

NIVELES = {1: "Rojo", 2: "Naranja", 3: "Amarillo"}
FENOMENOS = {
    "CO": "Fenómenos costeros", "VI": "Viento", "PR": "Lluvia",
    "NE": "Nieve", "TO": "Tornado", "AT": "Tormenta", "BT": "Bruma",
    "RI": "Río", "GA": "Galerna", "NI": "Niebla", "DH": "Deshielo",
    "VS": "Visibilidad", "AL": "Aludes", "TE": "Temperaturas extremas",
    "HU": "Huracán", "LL": "Lluvias", "SV": "Sequía",
}
CCAA_ORDEN = [
    "Andalucía", "Aragón", "Principado de Asturias", "Illes Balears", "Canarias",
    "Cantabria", "Castilla-La Mancha", "Castilla y León", "Cataluña",
    "Comunitat Valenciana", "Extremadura", "Galicia", "Comunidad de Madrid",
    "Región de Murcia", "Comunidad Foral de Navarra", "País Vasco", "La Rioja",
    "Ciudad de Ceuta", "Ciudad de Melilla",
]


def catalogo_provincias() -> list[dict]:
    """Provincias y CCAA tal y como las agrupa AEMET (para poder decir
    «sin aviso» de las que no salen en el geojson)."""
    html = bajar("https://www.aemet.es/es/eltiempo/prediccion/avisos").decode(
        "iso-8859-15", "replace")
    marca = "var comunidades = "
    i = html.find(marca)
    if i < 0:
        return []
    obj, _ = json.JSONDecoder().raw_decode(html[i + len(marca):])
    salida = []
    for ccaa in obj:
        for prov in ccaa.get("provincias", []):
            salida.append({"nombre": prov.get("nombre", ""),
                           "ccaa": ccaa.get("nombre", ""),
                           "id": prov.get("id", ""),
                           "zonas_previstas": len(prov.get("zonasAvisos", []))})
    return salida


def cap_actual() -> tuple[list[dict], dict]:
    """Descarga el tar.gz de geojson de avisos y devuelve (features, meta)."""
    html = bajar("https://www.aemet.es/es/eltiempo/prediccion/avisos").decode(
        "iso-8859-15", "replace")
    m = re.search(r"(?:https://www\.aemet\.es)?/es/geojson/download/avisos/"
                  r"geojson_\d+\.tar\.gz", html)
    if not m:
        raise RuntimeError("no encuentro el enlace del geojson de avisos")
    url_geo = m.group(0)
    if url_geo.startswith("/"):
        url_geo = "https://www.aemet.es" + url_geo
    tar_bytes = bajar(url_geo, timeout=60)
    features: list[dict] = []
    meta: dict = {"url_geojson": url_geo, "ficheros": [], "elaborado": ""}
    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:gz") as tf:
        for mi in tf.getmembers():
            nombre = mi.name
            if not nombre.endswith(".geojson"):
                continue
            # D+0 = hoy; penbal (península y Baleares) + can (Canarias)
            if not nombre.startswith("r_D+0_"):
                continue
            if "_penbal_" not in nombre and "_can_" not in nombre:
                continue
            if mi.size < 300:          # fichero vacío: sin avisos en esa área
                continue
            crudo = tf.extractfile(mi).read().decode("utf-8", "replace")
            try:
                fc = json.loads(crudo)
            except json.JSONDecodeError:
                continue
            meta["ficheros"].append(nombre)
            mm = re.search(r"r_D\+0_(\d{14})_", nombre)
            if mm and not meta["elaborado"]:
                meta["elaborado"] = mm.group(1)
            for ft in fc.get("features", []):
                props = ft.get("properties", {}) or {}
                avisos = props.get("Avis_COCO") or []
                nivel = 0
                for a in avisos:
                    try:
                        nivel = max(nivel, int(a.get("nivel_num") or 0))
                    except (TypeError, ValueError):
                        pass
                if not nivel:
                    try:
                        nivel = int(props.get("Av_mayor") or props.get("Nivel_COCO") or 0)
                    except (TypeError, ValueError):
                        nivel = 0
                features.append({
                    "zona": props.get("Nombre_zona", ""),
                    "provincia": props.get("Provincia", ""),
                    "codigo": props.get("COD_Z", ""),
                    "nivel": nivel,
                    "avisos": [{
                        "fenomeno": a.get("fenomeno", ""),
                        "fenomeno_txt": FENOMENOS.get(a.get("fenomeno", ""), a.get("parametro", "")),
                        "nivel": a.get("nivel_num"),
                        "severidad": a.get("severity", ""),
                        "descripcion": a.get("descripcion", ""),
                        "desde": a.get("onset_local", ""),
                        "hasta": a.get("expires_local", ""),
                        "probabilidad": a.get("prob", ""),
                        "certainty": a.get("certainty", ""),
                    } for a in avisos],
                    "geometry": redondear(ft.get("geometry")),
                })
    return features, meta


def redondear(geo, decimales: int = 4):
    """Baja la precisión de las coordenadas: mismo mapa, fichero más ligero."""
    if isinstance(geo, list):
        return [redondear(x, decimales) for x in geo]
    if isinstance(geo, dict):
        return {k: redondear(v, decimales) for k, v in geo.items()}
    if isinstance(geo, float):
        return round(geo, decimales)
    return geo


def construir_alertas(features: list[dict], meta_aemet: dict) -> dict:
    provincias = catalogo_provincias()
    por_prov: dict[str, dict] = {}
    for f in features:
        p = f["provincia"] or "—"
        d = por_prov.setdefault(p, {"nombre": p, "nivel": 0, "zonas": []})
        d["nivel"] = max(d["nivel"], f["nivel"])
        d["zonas"].append({
            "nombre": f["zona"], "nivel": f["nivel"],
            "avisos": [{k: a[k] for k in ("fenomeno", "fenomeno_txt", "descripcion",
                                          "desde", "hasta", "probabilidad")}
                       for a in f["avisos"]],
        })
    ccaa_por_prov = {p["nombre"]: p["ccaa"] for p in provincias}
    lista = []
    for nombre, ccaa in [(p["nombre"], p["ccaa"]) for p in provincias]:
        d = por_prov.get(nombre, {"nombre": nombre, "nivel": 0, "zonas": []})
        lista.append({
            "nombre": nombre,
            "ccaa": ccaa,
            "nivel": d["nivel"],
            "nivel_txt": NIVELES.get(d["nivel"], "Sin aviso"),
            "zonas": d["zonas"],
        })
    # provincias que AEMET devuelve y no estaban en el catálogo (por si acaso)
    for nombre, d in por_prov.items():
        if nombre not in ccaa_por_prov and nombre != "—":
            lista.append({"nombre": nombre, "ccaa": ccaa_por_prov.get(nombre, ""),
                          "nivel": d["nivel"], "nivel_txt": NIVELES.get(d["nivel"], "Sin aviso"),
                          "zonas": d["zonas"]})
    lista.sort(key=lambda x: (-x["nivel"], x["nombre"]))

    cuenta = {"rojo": 0, "naranja": 0, "amarillo": 0, "sin_aviso": 0}
    for p in lista:
        if p["nivel"] == 1:
            cuenta["rojo"] += 1
        elif p["nivel"] == 2:
            cuenta["naranja"] += 1
        elif p["nivel"] == 3:
            cuenta["amarillo"] += 1
        else:
            cuenta["sin_aviso"] += 1

    return {
        "meta": {
            "fuente": "AEMET — Meteoalerta (avisos oficiales por zona)",
            "url": "https://www.aemet.es/es/eltiempo/prediccion/avisos",
            "elaborado": meta_aemet.get("elaborado", ""),
            "actualizado": iso(datetime.now(timezone.utc)),
            "caducidad": "Los avisos se refrescan cada hora; AEMET los valida hasta 72 h.",
            "licencia": "© AEMET. Reproducción autorizada citando a AEMET como autora.",
            "ficheros": meta_aemet.get("ficheros", []),
        },
        "resumen": {**cuenta,
                    "zonas_en_aviso": len(features),
                    "provincias": len(lista)},
        "provincias": lista,
        "zonas": {"type": "FeatureCollection",
                  "features": [{"type": "Feature", "properties": {
                      "zona": f["zona"], "provincia": f["provincia"],
                      "nivel": f["nivel"], "nivel_txt": NIVELES.get(f["nivel"], "Sin aviso"),
                      "avisos": f["avisos"]}, "geometry": f["geometry"]}
                               for f in features]},
    }


# ─────────────────────────── 3. main ───────────────────────────

def escribir(ruta: Path, datos: dict) -> None:
    tmp = ruta.with_suffix(".tmp")
    tmp.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(ruta)


def main() -> int:
    DATA.mkdir(exist_ok=True)
    fallos: list[str] = []
    ahora = datetime.now(timezone.utc)

    # --- prensa -------------------------------------------------------------
    previo = {}
    ruta_noticias = DATA / "noticias.json"
    if ruta_noticias.exists():
        try:
            previo = json.loads(ruta_noticias.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            previo = {}
    viejos = {t["id"]: t for t in previo.get("temas", [])}

    temas_salida = []
    for tema in TEMAS:
        items = recolectar_tema(tema, fallos)
        if not items and tema["id"] in viejos:
            items = viejos[tema["id"]].get("items", [])
            fallos.append(f"{tema['id']}: sin resultados, se conserva lo anterior")
        temas_salida.append({
            "id": tema["id"],
            "titulo": tema["titulo"],
            "claim": tema["claim"],
            "items": items,
        })
        print(f"  {tema['id']}: {len(items)} titulares")

    noticias = {
        "meta": {
            "actualizado": iso(ahora),
            "fuente": "Bing News + Google News RSS (edición España)",
            "ventana_dias": VENTANA_DIAS,
            "aviso": "; ".join(fallos) if fallos else "",
        },
        "temas": temas_salida,
    }
    escribir(ruta_noticias, noticias)

    # --- avisos AEMET -------------------------------------------------------
    ruta_alertas = DATA / "alertas-es.json"
    try:
        features, meta_aemet = cap_actual()
        alertas = construir_alertas(features, meta_aemet)
        escribir(ruta_alertas, alertas)
        r = alertas["resumen"]
        print(f"  AEMET: {r['zonas_en_aviso']} zonas en aviso · "
              f"{r['amarillo']} prov. amarillo · {r['naranja']} naranja · {r['rojo']} rojo")
    except Exception as e:
        fallos.append(f"aemet: {type(e).__name__}: {e}")
        print(f"  AEMET FALLO: {e} (se conserva data/alertas-es.json)", file=sys.stderr)

    print(f"noticias: {sum(len(t['items']) for t in temas_salida)} titulares, "
          f"{len(fallos)} incidencias")
    return 0


if __name__ == "__main__":
    sys.exit(main())
