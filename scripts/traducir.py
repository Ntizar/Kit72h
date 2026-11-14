#!/usr/bin/env python3
"""Kit72h — traductor de contenido.

Traduce el castellano (fuente de verdad) a los idiomas de los mercados y escribe
los overlays que consume la web:

  data/i18n/ui/<lang>.json            textos de interfaz
  data/i18n/contenido/<lang>.json     kits + fuentes + disclosure

Reglas que respeta:
  - Solo se traducen TEXTOS. ASINs, URLs, precios con €, iconos y estructura no
    se tocan: el castellano sigue siendo la fuente y el merge es por índice.
  - Caché por cadena (data/i18n/.cache/<lang>.json): un relanzamiento solo
    traduce lo que falta o ha cambiado. Así el cron nocturno es incremental.
  - Validación dura: si una respuesta no trae el mismo número de cadenas, se
    reintenta; si vuelve a fallar, se deja el castellano antes que romper.
  - Los textos legales (disclosure de afiliado) NO los inventa el modelo: van
    fijados a mano por idioma.

Uso:
  python scripts/traducir.py ui                    # interfaz, 5 idiomas
  python scripts/traducir.py kits                  # 21 kits
  python scripts/traducir.py blog --limite 5       # 5 entradas (por defecto todas)
  python scripts/traducir.py todo
  --langs en,de,fr,it,nl   --modelo qwen3.8-max   --seco (no escribe)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
IDIOMAS = ["en", "de", "fr", "it", "nl"]
NOMBRES = {
    "en": "English (neutral international English)",
    "de": "German (Deutsch, Germany)",
    "fr": "French (français, France)",
    "it": "Italian (italiano, Italy)",
    "nl": "Dutch (Nederlands, Netherlands)",
}
ENDPOINT = "https://api.nan.builders/v1/chat/completions"
# deepseek-v4-flash medido 2026-11-14: ~8 s por lote de 600 caracteres con 4 hilos.
# qwen3.8-max tardaba 280 s el mismo lote: imposible para 765 k caracteres.
MODELO = "deepseek-v4-flash"

# Texto legal de afiliado por idioma. No se traduce con el modelo: es texto con
# consecuencias legales y debe ser el estándar de cada programa de Amazon.
DISCLOSURE = {
    "es": "Como Afiliado de Amazon, obtengo ingresos por las compras adscritas que cumplen los requisitos aplicables. Los precios pueden variar. Fuente de las recomendaciones: Protección Civil y Comisión Europea.",
    "en": "As an Amazon Associate I earn from qualifying purchases. Prices may vary. Recommendations are based on official sources: the EU Civil Protection Mechanism and national civil protection authorities.",
    "de": "Als Amazon-Partner verdiene ich an qualifizierten Verkäufen. Preise können variieren. Grundlage der Empfehlungen sind offizielle Quellen: EU-Zivilschutz und nationale Katastrophenschutzbehörden.",
    "fr": "En tant que Partenaire Amazon, je réalise un bénéfice sur les achats remplissant les conditions requises. Les prix peuvent varier. Sources des recommandations : protection civile de l'UE et autorités nationales de sécurité civile.",
    "it": "In qualità di Affiliato Amazon, ricevo un guadagno dagli acquisti idonei. I prezzi possono variare. Le raccomandazioni si basano su fonti ufficiali: Protezione civile dell'UE e autorità nazionali di protezione civile.",
    "nl": "Als Amazon-partner verdien ik aan kwalificerende aankopen. Prijzen kunnen varieren. De aanbevelingen zijn gebaseerd op officiele bronnen: EU-bescherming en nationale rampenbestrijding.",
}

SISTEMA = (
    "Eres traductor profesional de sitios web de preparación ante emergencias. "
    "Traduces del español a {idioma}. Reglas ESTRICTAS:\n"
    "1. Devuelve SOLO un array JSON de cadenas, en el mismo orden y con el mismo número de elementos que la entrada. Sin texto antes ni después.\n"
    "2. Conserva EXACTAMENTE las etiquetas HTML (<a>, <b>, <br>, <strong>...) y sus atributos href=\"...\". Traduce solo el texto visible.\n"
    "3. Conserva los marcadores entre llaves tal cual: {n}, {p}, {pais}, {num}, {e}, {amazon}.\n"
    "4. No traduzcas: marcas (Kit72h, Amazon, Starlink, BWL/FONES, SAI, LFP, V-16, DGT, AEMET, IGN, FEMA, BBK, Protezione Civile), códigos de producto (B0XXXXXXXX), URLs ni correos.\n"
    "5. Los importes en euros se dejan como están (los convierte el código, no tú).\n"
    "6. Si una cadena son solo siglas o un nombre propio, devuélvela igual.\n"
    "7. Tono: directo, útil, sin sensacionalismo. Nada de promesas de supervivencia.\n"
    "8. Naturalidad local: usa el término que de verdad se emplea en ese país para «kit de emergencia» (p. ej. en alemán «Notfallkit», en neerlandés «noodpakket»)."
)

LETRAS = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]")
ETIQUETA = re.compile(r"</?(a|b|i|br|strong|em|p|ul|ol|li|span|small|table|tr|td|th)\b", re.I)
MARCADOR = re.compile(r"\{[a-z]+\}")


def cargar_mercados():
    d = json.loads((RAIZ / "data/mercados.json").read_text(encoding="utf-8"))
    return d


def integra(src: str, dst: str) -> bool:
    """¿La traducción conserva la estructura? Mismas etiquetas HTML y mismos
    marcadores {n}. Si no, se prefiere el castellano a un HTML roto."""
    from collections import Counter
    return (Counter(x.lower() for x in ETIQUETA.findall(src)) ==
            Counter(x.lower() for x in ETIQUETA.findall(dst)) and
            sorted(MARCADOR.findall(src)) == sorted(MARCADOR.findall(dst)))


def clave(texto: str) -> str:
    return hashlib.sha1(texto.encode("utf-8")).hexdigest()


class Traductor:
    def __init__(self, lang, modelo=MODELO, api_key=None, seco=False, hilos=5):
        self.lang = lang
        self.idioma = NOMBRES[lang]
        self.modelo = modelo
        self.api_key = api_key or os.environ.get("HERMES_CUSTOM_OPENAI_COMPATIBLE_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise SystemExit("Falta la clave: exporta HERMES_CUSTOM_OPENAI_COMPATIBLE_API_KEY")
        self.seco = seco
        self.hilos = hilos
        self.cache_path = RAIZ / "data/i18n/.cache" / f"{lang}.json"
        self.cache = json.loads(self.cache_path.read_text(encoding="utf-8")) if self.cache_path.exists() else {}
        self.nuevas = 0
        self.fallos = 0
        self.fallidos = set()   # cadenas que no se pudieron traducir: no se cachean

    # ---------- API ----------
    def _llamar(self, lote, intento=0):
        cuerpo = {
            "model": self.modelo,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": SISTEMA.replace("{idioma}", self.idioma)},
                {"role": "user", "content": json.dumps(lote, ensure_ascii=False)},
            ],
        }
        req = urllib.request.Request(
            ENDPOINT,
            data=json.dumps(cuerpo).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read().decode("utf-8"))
            txt = d["choices"][0]["message"]["content"].strip()
            txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt, flags=re.S)
            salida = json.loads(txt)
            if not isinstance(salida, list) or len(salida) != len(lote):
                raise ValueError(f"esperaba {len(lote)} cadenas, llegaron "
                                 f"{len(salida) if isinstance(salida, list) else 'no-lista'}")
            return [str(x) for x in salida]
        except urllib.error.HTTPError as ex:
            # 429 = demasiadas peticiones: esperar de verdad, no reintentar en caliente.
            espera = 20 if ex.code == 429 else (3 * (intento + 1))
            if intento >= 3:
                self.fallos += 1
                self.fallidos.update(lote)   # NO se cachean: se reintentan otro día
                print(f"    ! lote de {len(lote)} sin traducir (HTTP {ex.code})", flush=True)
                return list(lote)
            time.sleep(espera)
            return self._llamar(lote, intento + 1)
        except (urllib.error.URLError, ValueError, KeyError,
                json.JSONDecodeError, TimeoutError, OSError) as ex:
            if intento >= 3:
                self.fallos += 1
                self.fallidos.update(lote)
                print(f"    ! lote de {len(lote)} sin traducir ({type(ex).__name__})", flush=True)
                return list(lote)  # castellano antes que romper
            time.sleep(2 * (intento + 1))
            return self._llamar(lote, intento + 1)

    # ---------- traducción de una lista ----------
    def traducir(self, textos):
        textos = ["" if t is None else str(t) for t in textos]
        # Purga: si la caché tiene la MISMA cadena que el original y es una frase
        # larga, es un fallo anterior que quedó mal cacheado. Se reintenta.
        purgadas = 0
        for t in textos:
            if t and len(t) > 25 and LETRAS.search(t):
                k = clave(t)
                if self.cache.get(k) == t:
                    del self.cache[k]
                    purgadas += 1
        if purgadas:
            print(f"  {self.lang}: {purgadas} traducciones fallidas en caché → se reintentan",
                  flush=True)
        pendientes = []
        for t in textos:
            if t and LETRAS.search(t) and clave(t) not in self.cache and t not in pendientes:
                pendientes.append(t)
        if pendientes:
            lotes = []
            actual, tam = [], 0
            for t in pendientes:
                if tam + len(t) > 2200 and actual:
                    lotes.append(actual)
                    actual, tam = [], 0
                actual.append(t)
                tam += len(t)
            if actual:
                lotes.append(actual)
            print(f"  {self.lang}: {len(pendientes)} cadenas nuevas en {len(lotes)} lotes", flush=True)
            with ThreadPoolExecutor(max_workers=self.hilos) as ex:
                resultados = list(ex.map(self._llamar, lotes))
            malas = []
            for lote, trad in zip(lotes, resultados):
                for src, dst in zip(lote, trad):
                    if src in self.fallidos:
                        continue          # se reintenta en la próxima pasada
                    if integra(src, dst):
                        self.cache[clave(src)] = dst
                        self.nuevas += 1
                    else:
                        malas.append(src)
            # Segunda pasada, de una en una, solo para las que rompieron estructura.
            if malas:
                print(f"    {len(malas)} cadenas con HTML/marcadores rotos → reintento individual", flush=True)
                for src in malas:
                    dst = self._llamar([src])[0]
                    self.cache[clave(src)] = dst if integra(src, dst) else src
                    self.nuevas += 1
            self._guardar_cache()
        return [self.cache.get(clave(t), t) if t else "" for t in textos]

    def _guardar_cache(self):
        if self.seco:
            return
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(json.dumps(self.cache, ensure_ascii=False, indent=0), encoding="utf-8")

    def escribir(self, ruta, datos):
        if self.seco:
            print(f"  [seco] no escribo {ruta.relative_to(RAIZ)}")
            return
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  -> {ruta.relative_to(RAIZ)}")


# ---------- UI ----------
CAMPOS_UI_HTML = {"faq.a1", "faq.a2", "faq.a3", "faq.a4", "faq.a5", "faq.a6", "faq.a7",
                  "faq.ctaT", "fuentes.lead", "fuentes.cierre", "blog.vacio",
                  "hero.ctaT", "ruta.h2"}

# La FAQ 4 es una pregunta de España (baliza V-16 de la DGT). Traducirla tal cual
# fuera de España sería contarle a un alemán la ley española como si fuera la
# suya. Se sustituye por la versión neutral + mención de que cada país tiene la
# suya. Estos textos van a mano, no los inventa el traductor.
FAQ_AUTO = {
    "en": ("What should you always carry in your car?",
           "The basics are the same almost everywhere in Europe: a hi-vis vest for every occupant "
           "(stored inside the cabin, not in the boot), a warning triangle, a first-aid kit and a torch. "
           "In winter add warm clothes and a blanket; on long trips, water and a charged power bank. "
           "Check your own country's highway code before you rely on it: Spain, for example, has required "
           "a connected V-16 beacon instead of triangles since 1 January 2026."),
    "de": ("Was sollte immer im Auto liegen?",
           "In fast ganz Europa gilt dasselbe: eine Warnweste für jede Person im Fahrzeug (im Innenraum, "
           "nicht im Kofferraum), ein Warndreieck, ein Verbandkasten und eine Taschenlampe. Im Winter "
           "kommen warme Kleidung und eine Decke dazu, auf langen Fahrten Wasser und eine geladene "
           "Powerbank. Prüfe vorher die Regeln deines Landes: In Spanien ist seit dem 1. Januar 2026 "
           "statt des Warndreiecks eine vernetzte V-16-Warnleuchte vorgeschrieben."),
    "fr": ("Que faut-il toujours avoir dans sa voiture ?",
           "Les bases sont les mêmes presque partout en Europe : un gilet haute visibilité par occupant "
           "(rangé dans l'habitacle, pas dans le coffre), un triangle de présignalisation, une trousse de "
           "premiers secours et une lampe. En hiver, ajoutez des vêtements chauds et une couverture ; sur "
           "les longs trajets, de l'eau et une batterie externe chargée. Vérifiez le code de la route de "
           "votre pays avant de partir : l'Espagne, par exemple, impose depuis le 1er janvier 2026 un "
           "balise V-16 connectée à la place du triangle."),
    "it": ("Cosa bisogna tenere sempre in auto?",
           "Le basi sono quasi le stesse in tutta Europa: un gilet ad alta visibilità per ogni occupante "
           "(nell'abitacolo, non nel bagagliaio), un triangolo, una cassetta di pronto soccorso e una "
           "torcia. D'inverno aggiungi indumenti caldi e una coperta; nei viaggi lunghi acqua e un "
           "power bank carico. Controlla il codice della strada del tuo paese: la Spagna, per esempio, "
           "dal 1° gennaio 2026 richiede una luce V-16 connessa al posto del triangolo."),
    "nl": ("Wat moet er altijd in de auto liggen?",
           "De basis is in bijna heel Europa hetzelfde: een veiligheidshesje voor elke inzittende (in het "
           "interieur, niet in de kofferbak), een gevarendriehoek, een verbandtrommel en een zaklamp. In "
           "de winter komen warme kleding en een deken erbij, op lange ritten water en een opgeladen "
           "powerbank. Check de regels van je eigen land: Spanje bijvoorbeeld verplicht sinds 1 januari "
           "2026 een connected V-16-lamp in plaats van de gevarendriehoek."),
}


# Siglas que el traductor deja en castellano porque van en la lista de «no tocar»
# y que en cada idioma tienen su equivalente. Se sustituyen a mano.
SUSTITUCIONES = {
    "en": {"SAI": "UPS"},
    "de": {"SAI": "USV"},
    "fr": {"SAI": "onduleur"},
    "it": {"SAI": "gruppo di continuità"},
    "nl": {"SAI": "UPS"},
}


def traducir_ui(tr: Traductor):
    base = json.loads((RAIZ / "data/i18n/ui/es.json").read_text(encoding="utf-8"))
    claves = [k for k in base if not k.startswith("_")]
    salida = {"_meta": {"lang": tr.lang, "desde": "data/i18n/ui/es.json",
                        "generado": time.strftime("%Y-%m-%d")}}
    valores = tr.traducir([base[k] for k in claves])
    for k, v in zip(claves, valores):
        salida[k] = v
    # El disclosure no lo decide el modelo: es texto legal.
    salida["disclosure"] = DISCLOSURE[tr.lang]
    # La FAQ del coche se adapta al país, no se traduce literal.
    if tr.lang in FAQ_AUTO:
        salida["faq.q4"], salida["faq.a4"] = FAQ_AUTO[tr.lang]
    # Siglas con equivalente propio (SAI → USV/UPS/onduleur).
    for viejo, nuevo in SUSTITUCIONES.get(tr.lang, {}).items():
        for k, v in list(salida.items()):
            if isinstance(v, str) and viejo in v:
                salida[k] = v.replace(viejo, nuevo)
    tr.escribir(RAIZ / f"data/i18n/ui/{tr.lang}.json", salida)


# ---------- Contenido (kits) ----------
def traducir_kits(tr: Traductor, limite=None):
    base = json.loads((RAIZ / "data/kits.json").read_text(encoding="utf-8"))
    kits = base["kits"][:limite] if limite else base["kits"]

    # 1. Recolectar todas las cadenas en orden determinista.
    tareas = []   # (etiqueta, texto)
    def añade(etiqueta, texto):
        if isinstance(texto, str) and texto.strip():
            tareas.append((etiqueta, texto))

    for k in kits:
        sl = k["slug"]
        for c in ("titulo", "resumen", "coste_total", "paraQuien", "paraQuien_no", "busc"):
            añade(f"kit/{sl}/{c}", k.get(c))
        for f in ("antes", "durante", "despues"):
            for i, p in enumerate((k.get("guia") or {}).get(f) or []):
                añade(f"kit/{sl}/guia/{f}/{i}", p)
        for i, e in enumerate(k.get("errores") or []):
            añade(f"kit/{sl}/errores/{i}", e)
        for si, s in enumerate(k.get("secciones") or []):
            añade(f"kit/{sl}/secciones/{si}/titulo", s.get("titulo"))
            añade(f"kit/{sl}/secciones/{si}/intro", s.get("intro"))
            for ii, it in enumerate(s.get("items") or []):
                añade(f"kit/{sl}/secciones/{si}/items/{ii}/producto", it.get("producto"))
                añade(f"kit/{sl}/secciones/{si}/items/{ii}/descripcion", it.get("descripcion"))
    for i, f in enumerate((base.get("meta") or {}).get("fuentes") or []):
        añade(f"fuentes/{i}/cat", f.get("cat"))
        añade(f"fuentes/{i}/nota", f.get("nota"))

    print(f"kits: {len(tareas)} cadenas de {len(kits)} kits", flush=True)
    traducidas = tr.traducir([t for _, t in tareas])
    mapa = {et: tx for (et, _), tx in zip(tareas, traducidas)}

    # 2. Reconstruir la estructura espejo.
    salida = {
        "_meta": {"lang": tr.lang, "fuente": "data/kits.json",
                  "generado": time.strftime("%Y-%m-%d %H:%M"),
                  "kits": len(kits)},
        "disclosure": DISCLOSURE[tr.lang],
        "meta": {"fuentes": []},
        "kits": {},
    }
    for i, f in enumerate((base.get("meta") or {}).get("fuentes") or []):
        salida["meta"]["fuentes"].append({
            "cat": mapa.get(f"fuentes/{i}/cat", f.get("cat")),
            "nota": mapa.get(f"fuentes/{i}/nota", f.get("nota")),
        })
    for k in kits:
        sl = k["slug"]
        kk = {}
        for c in ("titulo", "resumen", "coste_total", "paraQuien", "paraQuien_no", "busc"):
            if f"kit/{sl}/{c}" in mapa:
                kk[c] = mapa[f"kit/{sl}/{c}"]
        if k.get("guia"):
            kk["guia"] = {}
            for f in ("antes", "durante", "despues"):
                vals = [mapa[f"kit/{sl}/guia/{f}/{i}"] for i in range(len((k.get("guia") or {}).get(f) or []))
                        if f"kit/{sl}/guia/{f}/{i}" in mapa]
                if vals:
                    kk["guia"][f] = vals
        if k.get("errores"):
            kk["errores"] = [mapa[f"kit/{sl}/errores/{i}"] for i in range(len(k["errores"]))
                             if f"kit/{sl}/errores/{i}" in mapa]
        secciones = []
        for si, s in enumerate(k.get("secciones") or []):
            ss = {}
            if f"kit/{sl}/secciones/{si}/titulo" in mapa:
                ss["titulo"] = mapa[f"kit/{sl}/secciones/{si}/titulo"]
            if f"kit/{sl}/secciones/{si}/intro" in mapa:
                ss["intro"] = mapa[f"kit/{sl}/secciones/{si}/intro"]
            items = []
            for ii, it in enumerate(s.get("items") or []):
                d = {}
                for c in ("producto", "descripcion"):
                    et = f"kit/{sl}/secciones/{si}/items/{ii}/{c}"
                    if et in mapa:
                        d[c] = mapa[et]
                items.append(d)
            ss["items"] = items
            secciones.append(ss)
        kk["secciones"] = secciones
        salida["kits"][sl] = kk

    tr.escribir(RAIZ / f"data/i18n/contenido/{tr.lang}.json", salida)


# ---------- Blog ----------
def traducir_blog(tr: Traductor, limite=None, solo_pendientes=False):
    ruta = RAIZ / f"data/i18n/contenido/{tr.lang}.json"
    base = json.loads((RAIZ / "data/blog.json").read_text(encoding="utf-8"))
    entradas = base["entradas"]
    ya = {}
    if ruta.exists():
        try:
            ya = json.loads(ruta.read_text(encoding="utf-8")).get("blog") or {}
        except json.JSONDecodeError:
            ya = {}
    if solo_pendientes:
        entradas = [e for e in entradas if e["slug"] not in ya]
        print(f"  {tr.lang}: {len(entradas)} entradas pendientes de {len(base['entradas'])}",
              flush=True)
    if limite:
        entradas = entradas[:limite]
    if not entradas:
        print(f"  {tr.lang}: blog al día, nada que traducir", flush=True)
        return

    tareas = []
    def añade(et, tx):
        if isinstance(tx, str) and tx.strip():
            tareas.append((et, tx))
    for e in entradas:
        sl = e["slug"]
        añade(f"blog/{sl}/titulo", e.get("titulo"))
        añade(f"blog/{sl}/resumen", e.get("resumen"))
        añade(f"blog/{sl}/cuerpo", e.get("cuerpo"))
        for i, t in enumerate(e.get("etiquetas") or []):
            añade(f"blog/{sl}/etiquetas/{i}", t)
        for i, f in enumerate(e.get("fuente") or []):
            añade(f"blog/{sl}/fuente/{i}/nombre", f.get("nombre"))

    print(f"blog: {len(tareas)} cadenas de {len(entradas)} entradas", flush=True)
    traducidas = tr.traducir([t for _, t in tareas])
    mapa = {et: tx for (et, _), tx in zip(tareas, traducidas)}

    salida = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {
        "_meta": {"lang": tr.lang}, "disclosure": DISCLOSURE[tr.lang], "kits": {}, "blog": {}}
    salida.setdefault("blog", {})
    for e in entradas:
        sl = e["slug"]
        d = {"titulo": mapa.get(f"blog/{sl}/titulo", e.get("titulo")),
             "resumen": mapa.get(f"blog/{sl}/resumen", e.get("resumen")),
             "cuerpo": mapa.get(f"blog/{sl}/cuerpo", e.get("cuerpo"))}
        if e.get("etiquetas"):
            d["etiquetas"] = [mapa.get(f"blog/{sl}/etiquetas/{i}", t) for i, t in enumerate(e["etiquetas"])]
        if e.get("fuente"):
            d["fuente"] = [{"nombre": mapa.get(f"blog/{sl}/fuente/{i}/nombre", f.get("nombre"))}
                           for i, f in enumerate(e["fuente"])]
        salida["blog"][sl] = d
    salida["_meta"]["blog_traducido"] = len(salida["blog"])
    salida["_meta"]["generado"] = time.strftime("%Y-%m-%d %H:%M")
    tr.escribir(ruta, salida)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("que", choices=["ui", "kits", "blog", "todo"])
    ap.add_argument("--langs", default=",".join(IDIOMAS))
    ap.add_argument("--modelo", default=MODELO)
    ap.add_argument("--limite", type=int, default=None, help="máximo de kits/entradas (pruebas)")
    ap.add_argument("--pendientes", action="store_true",
                    help="blog: solo las entradas que aún no están en el overlay")
    ap.add_argument("--seco", action="store_true")
    ap.add_argument("--hilos", type=int, default=4)
    a = ap.parse_args()

    idiomas = [x.strip() for x in a.langs.split(",") if x.strip()]
    t0 = time.time()
    total_nuevas = 0
    for lang in idiomas:
        if lang not in NOMBRES:
            print(f"idioma no soportado: {lang}", file=sys.stderr)
            continue
        print(f"\n== {lang} ==", flush=True)
        tr = Traductor(lang, modelo=a.modelo, seco=a.seco, hilos=a.hilos)
        if a.que in ("ui", "todo"):
            traducir_ui(tr)
        if a.que in ("kits", "todo"):
            traducir_kits(tr, a.limite)
        if a.que in ("blog", "todo"):
            traducir_blog(tr, a.limite, a.pendientes)
        print(f"  {tr.nuevas} cadenas nuevas, {tr.fallos} lotes fallidos", flush=True)
        total_nuevas += tr.nuevas
    print(f"\ntraducir: {total_nuevas} cadenas nuevas en {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
