#!/usr/bin/env python3
"""Kit72h — prerender multi-mercado.

Convierte cada ruta del SPA en HTML estático completo, por mercado:
  ES (raíz)      /  /fuentes/  /blog/  /zona/  /noticias/  /kit/<slug>/  /blog/<slug>/
  Otros          /<mercado>/  /<mercado>/fuentes/  /<mercado>/blog/
                 /<mercado>/kit/<slug>/  /<mercado>/blog/<slug>/

Reglas:
  - El contenido de cada mercado es el castellano + el overlay
    data/i18n/contenido/<idioma>.json (merge por slug/índice). Los enlaces de
    Amazon NO se traducen nunca: los pone el JS con el dominio y tag del mercado.
  - Fuera de España no se genera la página de una entrada de blog hasta que esa
    entrada está traducida: 64 títulos en castellano bajo /de/blog/ serían
    contenido duplicado. La home, /fuentes/ y el índice de kits sí van siempre.
  - Cada página lleva hreflang de todos los mercados donde existe esa misma ruta,
    más x-default → castellano. Es lo que hace que Google sirva /de/ a un alemán
    en vez de la portada española.
  - /zona/ y /noticias/ son de España (AEMET, IGN, Google News ES): no se generan
    fuera de la raíz.

Servidor con fallback al shell (SPA) -> Chrome headless dump -> inyección de
metadatos -> fichero en la ruta real. Determinista y re-ejecutable.
"""
import json
import http.server
import re
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BASE = "https://kit72h.com"
PUERTO = 8795

# Fuente única de mercados, contenido traducido y rutas (scripts/mercados.py).
from mercados import (  # noqa: E402  (import tras fijar la raíz)
    alternos as alternos_de,
    cargar_mercados,
    contenido as contenido_mercados,
    indice_hreflang,
    prefijo,
    rutas_de,
)


def encontrar_chrome():
    import os
    cand = os.environ.get("CHROME_BIN")
    if cand:
        return cand
    w = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if w:
        return w
    # VM NaN (sin root): chromium de playwright + librerías extraídas en ~/.chrome-libs.
    import glob as _glob
    pw = sorted(_glob.glob(os.path.expanduser(
        "~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome")))
    hs = (sorted(_glob.glob(os.path.expanduser(
              "~/.cache/chrome/chrome-headless-shell*/chrome-headless-shell")))
          + sorted(_glob.glob(os.path.expanduser(
              "~/.cache/chrome/chrome-headless-shell/*/chrome-headless-shell-linux64/chrome-headless-shell"))))
    elegido = pw[-1] if pw else (hs[-1] if hs else None)
    if elegido:
        libs = os.path.expanduser("~/.chrome-libs")
        if os.path.isdir(libs):
            extra = f"{libs}/usr/lib/x86_64-linux-gnu:{libs}/lib/x86_64-linux-gnu"
            actual = os.environ.get("LD_LIBRARY_PATH", "")
            if extra not in actual:
                os.environ["LD_LIBRARY_PATH"] = f"{extra}:{actual}" if actual else extra
        return elegido
    win = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if Path(win).exists():
        return win
    raise SystemExit("No encuentro Chrome (usa CHROME_BIN=...)")


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        ruta = self.path.split("?")[0].split("#")[0]
        # Siempre el shell en rutas de sección: así la cabecera/nav prerendeada
        # es SIEMPRE la actual (si se sirviera el fichero ya generado, la nav se
        # congelaría en la versión con la que se creó cada página).
        if ruta.endswith("/"):
            shell = (RAIZ / "index.html").read_text(encoding="utf-8")
            # OJO: index.html es shell Y portada horneada. Si se sirve tal cual, el
            # marcador de éxito («cta-kit», «data-mercado=») YA está en el HTML antes
            # de que corra el JS y el dump puede capturar la portada anterior: así se
            # horneó /en-gb/ en castellano (detectado por el gate el 2026-11-14).
            # Se vacía #app: cada página tiene que renderizarse de verdad.
            shell = re.sub(r'(<main id="app"[^>]*>).*?(</main>)', r'\1\2', shell, flags=re.S)
            datos = shell.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(datos)))
            self.end_headers()
            self.wfile.write(datos)
            return
        super().do_GET()


def dump(chrome, url, marca_esperada):
    """Vuelca el DOM de una ruta. Chrome headless a veces devuelve el shell
    vacío (los JS no llegan a ejecutarse dentro del virtual-time-budget): el
    fallo es intermitente, así que se reintenta hasta 3 veces."""
    perfil = Path(tempfile.gettempdir()) / f"prerender-{abs(hash(url)) % 99999}"
    html = ""
    for _ in range(3):
        r = subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
             f"--user-data-dir={perfil}", "--hide-scrollbars",
             "--virtual-time-budget=12000", "--dump-dom", url],
            capture_output=True, timeout=90)
        html = r.stdout.decode("utf-8", "ignore")
        if marca_esperada in html:
            break
    shutil.rmtree(perfil, ignore_errors=True)
    assert "<title>" in html and 'id="app"' in html, f"dump vacío: {url}"
    return html


def jsonld(bloque):
    return json.dumps(bloque, ensure_ascii=False, indent=2).replace("</", "<\\/")


def inyectar(html, *, titulo, desc, canonical, ld=None, reemplazar_desc=True,
             locale="es_ES", inlang="es", alternos=None):
    head = []
    if reemplazar_desc and desc:
        nuevo, n = re.subn(r'<meta name="description" content="[^"]*">',
                           f'<meta name="description" content="{escape(desc, quote=True)}">',
                           html, count=1)
        if n:
            html = nuevo
        else:
            head.append(f'<meta name="description" content="{escape(desc, quote=True)}">')
    # canonical y OG: SIEMPRE reemplazar (el shell trae los de la portada)
    html = re.sub(r'<link rel="canonical" href="[^"]*">\s*', '', html)
    html = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\s*', '', html)
    head.append(f'<link rel="canonical" href="{canonical}">')
    for alt in (alternos or []):
        head.append(f'<link rel="alternate" hreflang="{alt[0]}" href="{alt[1]}">')
    html = re.sub(r'<meta property="og:[^"]*" content="[^"]*">\s*', '', html)
    html = re.sub(r'<meta name="twitter:card" content="[^"]*">\s*', '', html)
    # twitter:image y el favicon inline NO cubren los re.sub de arriba: sin
    # esto cada horneado AÑADÍA otra copia (vistas duplicadas en 78 páginas).
    html = re.sub(r'<meta name="twitter:image" content="[^"]*">\s*', '', html)
    html = re.sub(r'<link rel="icon" href="data:image/svg[^"]*">\s*', '', html)
    # JSON-LD inyectado en runs previos: quitar y reponer (los del shell se quedan)
    html = re.sub(
        r'<script type="application/ld\+json">\s*\{[\s\S]{0,3000}?"@type":\s*'
        r'"(?:Article|BreadcrumbList|BlogPosting|CollectionPage|Blog)"[\s\S]*?\}\s*</script>\s*',
        '', html)
    # ...pero los del shell son de la HOME y el servidor los sirve en TODAS las rutas.
    # Sin este strip, cada post declaraba a Google un FAQPage y un HowTo de montaje de
    # kit 72h que no están en su página (auditoría 2026-11-09).
    if canonical.rstrip("/") != BASE.rstrip("/"):
        html = re.sub(
            r'<script type="application/ld\+json"[^>]*data-nz="home-(?:faq|howto|kits)"[^>]*>'
            r'[\s\S]*?</script>\s*', '', html)
    head.append('<meta property="og:type" content="website">')
    head.append(f'<meta property="og:url" content="{canonical}">')
    head.append('<meta property="og:site_name" content="Kit72h">')
    head.append(f'<meta property="og:title" content="{escape(titulo or "Kit72h — Kits de emergencia 72 horas", quote=True)}">')
    head.append(f'<meta property="og:description" content="{escape(desc or "", quote=True)}">')
    head.append(f'<meta property="og:image" content="{BASE}/assets/og-kit72h.png">')
    head.append('<meta property="og:image:width" content="1200">')
    head.append('<meta property="og:image:height" content="630">')
    head.append(f'<meta property="og:locale" content="{locale}">')
    head.append('<meta name="twitter:card" content="summary_large_image">')
    head.append(f'<meta name="twitter:image" content="{BASE}/assets/og-kit72h.png">')
    head.append('<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 64 64\'%3E%3Crect width=\'64\' height=\'64\' fill=\'%23D14B27\'/%3E%3Ctext x=\'32\' y=\'42\' font-family=\'Arial Black,Arial\' font-size=\'26\' font-weight=\'900\' fill=\'%23F1EBDF\' text-anchor=\'middle\'%3E72%3C/text%3E%3C/svg%3E">')
    if ld:
        for bloque in ld:
            head.append(f'<script type="application/ld+json">\n{jsonld(bloque)}\n</script>')
    html = html.replace("</head>", "\n".join(head) + "\n</head>", 1)
    return html


# ─────────────────────────── main ───────────────────────────
def main():
    chrome = encontrar_chrome()
    datos = contenido_mercados()
    mercados = [d["mercado"] for d in datos.values()]
    # --solo es,de  → hornea solo esos mercados (desarrollo y pruebas)
    solo = None
    if "--solo" in sys.argv:
        solo = sys.argv[sys.argv.index("--solo") + 1].split(",")
        mercados = [m for m in mercados if m["id"] in solo]
    rev = (datos["es"]["kits"].get("meta") or {}).get("ultima_revision", "2026-09-28")

    # Índice global clave lógica -> {id_mercado: ruta}: empareja los hreflang.
    indice = indice_hreflang(datos)

    def alternos_para(clave):
        return alternos_de(clave, datos, indice)

    socketserver.TCPServer.allow_reuse_address = True
    try:
        srv = socketserver.TCPServer(("127.0.0.1", PUERTO), H)
    except OSError:
        srv = socketserver.TCPServer(("127.0.0.1", 0), H)
        print(f"puerto {PUERTO} ocupado → usando el {srv.server_address[1]}")
    puerto = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    ok = fallos = 0
    try:
        for m in mercados:
            d = datos[m["id"]]
            ui = d["ui"]
            print(f"\n== {m['id']} ({m['locale']}) ==", flush=True)
            for ruta, clave in rutas_de(m, datos[m["id"]]):
                url = f"http://127.0.0.1:{puerto}{ruta}"
                try:
                    # Marca que SOLO existe en la página de destino (una marca
                    # compartida hacía pasar el test con la portada copiada).
                    if clave == "home":
                        esperado = "cta-kit"
                    elif clave == "fuentes":
                        esperado = "fuentes-pagina"
                    elif clave == "blogidx":
                        esperado = "hero-blog"
                    elif clave == "zona":
                        esperado = "zona-mapa"
                    elif clave == "noticias":
                        esperado = "noticias-pagina"
                    elif clave.startswith("kit/"):
                        slug = clave.split("/", 1)[1]
                        kit = next(k for k in d["kits"]["kits"] if k["slug"] == slug)
                        esperado = "barra-progreso" if kit.get("secciones") else f"/kit/{slug}/"
                    else:
                        esperado = "cuerpo-blog"
                    html = dump(chrome, url, esperado)
                    assert esperado in html, f"contenido no horneado (falta {esperado})"
                    # Guardia de mercado: el JS es el único que escribe este atributo,
                    # así que su presencia prueba que la página es de ESTE país.
                    assert f'data-mercado="{m["id"]}"' in html, \
                        f"página horneada como otro mercado (falta data-mercado={m['id']})"

                    canonical = BASE + ruta
                    alternos = alternos_para(clave)
                    common = dict(canonical=canonical, locale=m["locale"].replace("-", "_"),
                                  inlang=m["lang"], alternos=alternos)

                    if clave == "home":
                        html = inyectar(html, titulo=ui.get("meta.home"),
                                        desc=ui.get("meta.homeDesc", ""),
                                        reemplazar_desc=False, **common)
                        dest = (RAIZ / "index.html") if m["id"] == "es" else (RAIZ / prefijo(m) / "index.html")
                    elif clave == "fuentes":
                        html = inyectar(html, titulo=ui.get("meta.fuentes"),
                                        desc=ui.get("meta.fuentesDesc", ""),
                                        ld=[{"@context": "https://schema.org", "@type": "CollectionPage",
                                             "name": ui.get("meta.fuentes"),
                                             "url": canonical,
                                             "inLanguage": m["lang"],
                                             "isPartOf": {"@type": "WebSite", "url": BASE + "/"}}],
                                        **common)
                        dest = RAIZ / prefijo(m) / "fuentes" / "index.html"
                    elif clave == "blogidx":
                        entradas_m = [e for e in d["blog"]["entradas"]
                                      if m["id"] == "es" or e["slug"] in d["traducidas"]]
                        html = inyectar(html, titulo=ui.get("meta.blog"),
                                        desc=ui.get("meta.blogDesc", ""),
                                        ld=[{"@context": "https://schema.org", "@type": "Blog",
                                             "name": ui.get("meta.blog"),
                                             "url": canonical,
                                             "inLanguage": m["lang"],
                                             "blogPost": [
                                                 {"@type": "BlogPosting", "headline": e["titulo"],
                                                  "url": f"{BASE}{prefijo(m)}blog/{e['slug']}/",
                                                  "datePublished": e["fecha"]}
                                                 for e in entradas_m[:20]]}],
                                        **common)
                        dest = RAIZ / prefijo(m) / "blog" / "index.html"
                    elif clave == "zona":
                        html = inyectar(html,
                                        titulo="Tu zona: hospital, farmacia, refugio y 112 — Kit72h",
                                        desc="Tu zona: mapa con hospitales, farmacias, refugios y "
                                             "puntos de encuentro cerca de ti. Elige ubicación y "
                                             "radio; el 112, siempre a mano.",
                                        ld=[{"@context": "https://schema.org", "@type": "CollectionPage",
                                             "name": "Tu zona — Kit72h", "url": canonical,
                                             "inLanguage": "es",
                                             "isPartOf": {"@type": "WebSite", "url": BASE + "/"}}],
                                        **common)
                        dest = RAIZ / "zona" / "index.html"
                    elif clave == "noticias":
                        html = inyectar(html,
                                        titulo="Lo que está pasando: provisiones, incendios, "
                                               "inundaciones y apagones — Kit72h",
                                        desc="Titulares reales sobre países que piden provisiones a su "
                                             "población, incendios, inundaciones y apagones, y el nivel "
                                             "de alerta oficial (AEMET) provincia a provincia.",
                                        ld=[{"@context": "https://schema.org", "@type": "CollectionPage",
                                             "name": "Lo que está pasando — Kit72h", "url": canonical,
                                             "inLanguage": "es",
                                             "isPartOf": {"@type": "WebSite", "url": BASE + "/"}}],
                                        **common)
                        dest = RAIZ / "noticias" / "index.html"
                    elif clave.startswith("kit/"):
                        slug = clave.split("/", 1)[1]
                        k = next(x for x in d["kits"]["kits"] if x["slug"] == slug)
                        html = inyectar(
                            html, titulo=f"{k['titulo']} — Kit72h", desc=k.get("resumen", ""),
                            ld=[
                                {"@context": "https://schema.org", "@type": "Article",
                                 "headline": k["titulo"], "description": k.get("resumen", ""),
                                 "dateModified": rev,
                                 "author": {"@type": "Organization", "name": "Kit72h"},
                                 "publisher": {"@type": "Organization", "name": "Kit72h"},
                                 "mainEntityOfPage": canonical, "inLanguage": m["lang"]},
                                {"@context": "https://schema.org", "@type": "BreadcrumbList",
                                 "itemListElement": [
                                     {"@type": "ListItem", "position": 1, "name": "Kit72h",
                                      "item": BASE + "/"},
                                     {"@type": "ListItem", "position": 2, "name": "Kits",
                                      "item": BASE + ("/" + prefijo(m) + "#kits" if prefijo(m) else "/#kits")},
                                     {"@type": "ListItem", "position": 3, "name": k["titulo"],
                                      "item": canonical}]},
                            ], **common)
                        dest = RAIZ / prefijo(m) / "kit" / slug / "index.html"
                    else:  # entrada de blog
                        slug = clave.split("/", 1)[1]
                        e = next(x for x in d["blog"]["entradas"] if x["slug"] == slug)
                        html = inyectar(
                            html, titulo=f"{e['titulo']} — Blog Kit72h", desc=e.get("resumen", ""),
                            ld=[
                                {"@context": "https://schema.org", "@type": "BlogPosting",
                                 "headline": e["titulo"], "description": e.get("resumen", ""),
                                 "datePublished": e["fecha"], "dateModified": e["fecha"],
                                 "author": {"@type": "Organization", "name": "Kit72h"},
                                 "publisher": {"@type": "Organization", "name": "Kit72h"},
                                 "mainEntityOfPage": canonical,
                                 "keywords": ", ".join(e.get("etiquetas", [])),
                                 "inLanguage": m["lang"],
                                 "wordCount": len(re.sub(r"<[^>]+>", " ", e.get("cuerpo", "")))},
                                {"@context": "https://schema.org", "@type": "BreadcrumbList",
                                 "itemListElement": [
                                     {"@type": "ListItem", "position": 1, "name": "Kit72h",
                                      "item": BASE + "/"},
                                     {"@type": "ListItem", "position": 2, "name": "Blog",
                                      "item": BASE + prefijo(m) + "blog/"},
                                     {"@type": "ListItem", "position": 3, "name": e["titulo"],
                                      "item": canonical}]},
                            ], **common)
                        dest = RAIZ / prefijo(m) / "blog" / slug / "index.html"

                    dest.parent.mkdir(parents=True, exist_ok=True)
                    html = re.sub(
                        r'(?:<!-- GENERADO por scripts/prerender\.py — no editar a mano -->\s*)+',
                        '', html)
                    html = html.replace("</body>",
                                        "<!-- GENERADO por scripts/prerender.py — no editar a mano -->\n</body>", 1)
                    dest.write_text(html, encoding="utf-8", newline="\n")
                    ok += 1
                    print(f"  ok  {ruta}", flush=True)
                except Exception as ex:
                    fallos += 1
                    print(f"  FALLO {ruta}: {ex}", flush=True)
    finally:
        srv.shutdown()
    print(f"\nprerender: {ok} rutas generadas, {fallos} fallos")
    sys.exit(1 if fallos else 0)


def _reexec_playwright_si_procede():
    """En el VM de NaN el CLI de Chrome (--dump-dom) cuelga; si existe el venv con
    Playwright, delega en scripts/prerender_playwright.py."""
    import os
    if os.environ.get("KIT72H_NO_REEXEC") == "1":
        return
    venv = Path.home() / ".mastermind" / "venv" / "bin" / "python"
    if not venv.exists():
        return
    if not list((venv.parent.parent).glob("lib/python*/site-packages/playwright/__init__.py")):
        print("prerender: el venv no tiene playwright → uso el CLI de Chrome local",
              flush=True)
        return
    alt = Path(__file__).resolve().parent / "prerender_playwright.py"
    if not alt.exists():
        return
    print("prerender: el CLI cuelga en este VM → delegando en %s (Playwright)"
          % alt.name, flush=True)
    os.execve(str(venv), [str(venv), str(alt), *sys.argv[1:]],
              dict(os.environ, KIT72H_NO_REEXEC="1"))


if __name__ == "__main__":
    _reexec_playwright_si_procede()
    main()
