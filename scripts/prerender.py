#!/usr/bin/env python3
"""Kit72h — prerender: convierte cada ruta del SPA en HTML estático completo
con meta description, canonical, Open Graph y JSON-LD por página.

Google y los LLMs leen HTML; este script lo genera para:
  /  /fuentes/  /blog/  /kit/<slug>/  /blog/<slug>/

Servidor con fallback al shell (SPA) -> Chrome headless dump -> inyección
de metadatos -> fichero en ruta real (GH Pages y CF Pages lo sirven solos).
Determinista: CI lo relanza en cada push; crons, antes de commitear."""
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


def encontrar_chrome():
    import os
    cand = os.environ.get("CHROME_BIN")
    if cand:
        return cand
    w = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if w:
        return w
    win = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if Path(win).exists():
        return win
    raise SystemExit("No encuentro Chrome (usa CHROME_BIN=...)")


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        ruta = self.path.split("?")[0].split("#")[0]
        disco = (RAIZ / ruta.lstrip("/"))
        if ruta.endswith("/") and not (disco / "index.html").exists():
            # fallback SPA: sirve el shell para que Chrome renderice la ruta
            shell = (RAIZ / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(shell)))
            self.end_headers()
            self.wfile.write(shell)
            return
        super().do_GET()


def dump(chrome, url):
    perfil = Path(tempfile.gettempdir()) / f"prerender-{abs(hash(url)) % 99999}"
    r = subprocess.run(
        [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
         f"--user-data-dir={perfil}", "--hide-scrollbars",
         "--virtual-time-budget=9000", "--dump-dom", url],
        capture_output=True, timeout=90)
    shutil.rmtree(perfil, ignore_errors=True)
    html = r.stdout.decode("utf-8", "ignore")
    assert "<title>" in html and 'id="app"' in html, f"dump vacío: {url}"
    return html


def jsonld(bloque):
    """JSON-LD seguro para inyectar (escape de </script>)."""
    return json.dumps(bloque, ensure_ascii=False, indent=2).replace("</", "<\\/")


def inyectar(html, *, titulo, desc, canonical, ld=None, reemplazar_desc=True):
    head = []
    if reemplazar_desc and desc:
        nuevo, n = re.subn(r'<meta name="description" content="[^"]*">',
                           f'<meta name="description" content="{escape(desc, quote=True)}">',
                           html, count=1)
        if n:
            html = nuevo
        else:
            head.append(f'<meta name="description" content="{escape(desc, quote=True)}">')
    # canonical y OG: SIEMPRE reemplazar (el shell trae los de home)
    html = re.sub(r'<link rel="canonical" href="[^"]*">\s*', '', html)
    head.append(f'<link rel="canonical" href="{canonical}">')
    html = re.sub(r'<meta property="og:[^"]*" content="[^"]*">\s*', '', html)
    html = re.sub(r'<meta name="twitter:card" content="[^"]*">\s*', '', html)
    # JSON-LD inyectado en runs previos: quitar y reponer (los del shell: WebSite/FAQ/ItemList, se quedan)
    html = re.sub(
        r'<script type="application/ld\+json">\s*\{[\s\S]{0,3000}?"@type":\s*'
        r'"(?:Article|BreadcrumbList|BlogPosting|CollectionPage|Blog)"[\s\S]*?\}\s*</script>\s*',
        '', html)
    head.append('<meta property="og:type" content="website">')
    head.append(f'<meta property="og:url" content="{canonical}">')
    head.append('<meta property="og:site_name" content="Kit72h">')
    head.append(f'<meta property="og:title" content="{escape(titulo or "Kit72h", quote=True)}">')
    head.append(f'<meta property="og:description" content="{escape(desc or "", quote=True)}">')
    head.append('<meta name="twitter:card" content="summary">')
    if ld:
        for bloque in ld:
            head.append(f'<script type="application/ld+json">\n{jsonld(bloque)}\n</script>')
    html = html.replace("</head>", "\n".join(head) + "\n</head>", 1)
    return html


def main():
    chrome = encontrar_chrome()
    kits_d = json.loads((RAIZ / "data/kits.json").read_text(encoding="utf-8"))
    blog_d = json.loads((RAIZ / "data/blog.json").read_text(encoding="utf-8"))
    rev = kits_d.get("meta", {}).get("ultima_revision", "2026-09-28")

    rutas = [("/", None), ("/fuentes/", None), ("/blog/", None)]
    for k in kits_d["kits"]:
        rutas.append((f"/kit/{k['slug']}/", ("kit", k)))
    for e in blog_d["entradas"]:
        rutas.append((f"/blog/{e['slug']}/", ("blog", e)))

    srv = socketserver.TCPServer(("127.0.0.1", PUERTO), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    ok = fallos = 0
    try:
        for ruta, ctx in rutas:
            url = f"http://127.0.0.1:{PUERTO}{ruta}"
            try:
                html = dump(chrome, url)
                # asserts de contenido horneado: si el render vino vacío, FALLO
                if ctx and ctx[0] == "kit":
                    esperado = "barra-progreso"
                elif ctx and ctx[0] == "blog":
                    esperado = "cuerpo-blog"
                elif ruta == "/blog/":
                    esperado = "card-blog"
                elif ruta == "/fuentes/":
                    esperado = "fuentes-pagina"
                else:
                    esperado = "hero-stats"
                assert esperado in html, f"contenido no horneado (falta {esperado})"
                canonical = BASE + ruta
                if ctx is None:
                    if ruta == "/":
                        html = inyectar(html, titulo="", desc="", canonical=BASE + "/",
                                        reemplazar_desc=False)
                        dest = RAIZ / "index.html"
                    elif ruta == "/fuentes/":
                        html = inyectar(html, titulo="Fuentes oficiales — Kit72h",
                                        desc="Documentos oficiales (Comisión Europea, "
                                             "Protección Civil, DGT) en los que se basan "
                                             "los kits y guías de Kit72h.",
                                        canonical=canonical,
                                        ld=[{
                                            "@context": "https://schema.org",
                                            "@type": "CollectionPage",
                                            "name": "Fuentes oficiales — Kit72h",
                                            "url": canonical,
                                            "isPartOf": {"@type": "WebSite", "url": BASE + "/"},
                                        }])
                        dest = RAIZ / "fuentes" / "index.html"
                    else:  # /blog/
                        html = inyectar(html, titulo="Blog de preparación — Kit72h",
                                        desc=f"{len(blog_d['entradas'])} guías prácticas "
                                             "de preparación civil: qué comprar, cómo "
                                             "almacenarlo y cómo actuar. Fuentes oficiales.",
                                        canonical=canonical,
                                        ld=[{
                                            "@context": "https://schema.org",
                                            "@type": "Blog",
                                            "name": "Blog de preparación Kit72h",
                                            "url": BASE + "/blog/",
                                            "blogPost": [
                                                {"@type": "BlogPosting",
                                                 "headline": e["titulo"],
                                                 "url": f"{BASE}/blog/{e['slug']}/",
                                                 "datePublished": e["fecha"]}
                                                for e in blog_d["entradas"][:20]],
                                        }])
                        dest = RAIZ / "blog" / "index.html"
                elif ctx[0] == "kit":
                    k = ctx[1]
                    crumbs = ["Kit72h", "Kits", k["titulo"]]
                    html = inyectar(
                        html, titulo=f"{k['titulo']} — Kit72h", desc=k["resumen"],
                        canonical=canonical,
                        ld=[
                            {"@context": "https://schema.org", "@type": "Article",
                             "headline": k["titulo"], "description": k["resumen"],
                             "dateModified": rev,
                             "author": {"@type": "Organization", "name": "Kit72h"},
                             "publisher": {"@type": "Organization", "name": "Kit72h"},
                             "mainEntityOfPage": canonical,
                             "inLanguage": "es"},
                            {"@context": "https://schema.org", "@type": "BreadcrumbList",
                             "itemListElement": [
                                 {"@type": "ListItem", "position": 1, "name": "Kit72h",
                                  "item": BASE + "/"},
                                 {"@type": "ListItem", "position": 2, "name": "Kits",
                                  "item": BASE + "/#kits"},
                                 {"@type": "ListItem", "position": 3, "name": k["titulo"],
                                  "item": canonical}]},
                        ])
                    dest = RAIZ / "kit" / k["slug"] / "index.html"
                else:
                    e = ctx[1]
                    html = inyectar(
                        html, titulo=f"{e['titulo']} — Blog Kit72h", desc=e["resumen"],
                        canonical=canonical,
                        ld=[
                            {"@context": "https://schema.org", "@type": "BlogPosting",
                             "headline": e["titulo"], "description": e["resumen"],
                             "datePublished": e["fecha"], "dateModified": e["fecha"],
                             "author": {"@type": "Organization", "name": "Kit72h"},
                             "publisher": {"@type": "Organization", "name": "Kit72h"},
                             "mainEntityOfPage": canonical,
                             "keywords": ", ".join(e.get("etiquetas", [])),
                             "inLanguage": "es",
                             "wordCount": len(re.sub(r"<[^>]+>", " ", e.get("cuerpo", "")))},
                            {"@context": "https://schema.org", "@type": "BreadcrumbList",
                             "itemListElement": [
                                 {"@type": "ListItem", "position": 1, "name": "Kit72h",
                                  "item": BASE + "/"},
                                 {"@type": "ListItem", "position": 2, "name": "Blog",
                                  "item": BASE + "/blog/"},
                                 {"@type": "ListItem", "position": 3, "name": e["titulo"],
                                  "item": canonical}]},
                        ])
                    dest = RAIZ / "blog" / e["slug"] / "index.html"

                dest.parent.mkdir(parents=True, exist_ok=True)
                html = html.replace("</body>",
                                    "<!-- GENERADO por scripts/prerender.py — no editar a mano -->\n</body>", 1)
                dest.write_text(html, encoding="utf-8", newline="\n")
                ok += 1
                print(f"  ok  {ruta}")
            except Exception as ex:
                fallos += 1
                print(f"  FALLO {ruta}: {ex}")
    finally:
        srv.shutdown()
    print(f"prerender: {ok} rutas generadas, {fallos} fallos")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
