#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — verificar-sitio: el gate de calidad ANTES de pushear.

POR QUÉ EXISTE
--------------
El 2026-10-02 se desplegó a producción una ficha de kit que era, literalmente,
la home entera copiada: 0 secciones, 0 productos y 0 enlaces de compra. El
`curl` devolvía 200 y nadie se enteró hasta verlo con los ojos. Este script
caza ese fallo (y toda la familia) sin depender de mirar la web a mano.

QUÉ VALIDA (ERROR = bloquea el commit/deploy; AVISO = informa)
-------------------------------------------------------------
 1. JSON de datos coherente: kits.json (esquema por kit), blog.json.
 2. Cruce bidireccional: kit/<slug>/ ↔ kits.json ↔ sitemap.xml.
 3. Cada kit de kits.json tiene contenido real: >=1 sección, cada sección
    con items, cada item con producto/descripcion/precio y con enlace de
    compra (afiliado o búsqueda) con el tag de afiliado correcto.
 4. Cada kit/<slug>/index.html generado es una FICHA de verdad:
    section.ficha + ficha-cab + volver + >=1 seccion-kit + barra-progreso +
    al menos un enlace Amazon; y NO contiene marcadores de la home
    (hero-arte, kpro-banner, starlink-banner-wrap, ticker) → caza la
    «home copiada dentro del kit».
 5. Estructura HTML común de las páginas publicadas: ubar + site-header +
    main + footer.
 6. Versión CSS/JS: un ÚNICO valor en todas las páginas publicadas y sin
    etiquetas rotas (`ui.js?v=...` sin `"></script>`).
 7. JSON-LD: parsea y sin dobles llaves `{{`; ItemList sin rutas muertas.
 8. Enlaces internos /kit/<slug>/ de la home (index.html + ui.js) existen.
 9. blog.json: ninguna entrada sin `cuerpo` (evita el `<div>undefined</div>`).
10. Guardia de privacidad: ningún término vetado en el sitio publicable.

Uso:
  python scripts/verificar-sitio.py            # informe + exit 1 si hay ERROR
  python scripts/verificar-sitio.py --solo-kit kit-kit-profesional
  python scripts/verificar-sitio.py --aviso-error   # trata AVISOs como ERROR
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
TAG = "ntizar-21"

# Rutas publicables (espejo de .github/workflows/pages.yml, paso allowlist).
PUBLICADAS = ["index.html"]
for carpeta in ("kit", "blog", "fuentes", "zona"):
    PUBLICADAS.append(carpeta)

# Marcadores de la HOME que NUNCA deben aparecer dentro de una ficha de kit.
MARCADORES_HOME = [
    ("hero-arte", 'bloque hero de la home'),
    ("kpro-banner", 'banner del kit PRO de la home'),
    ("starlink-banner-wrap", 'banner de Starlink de la home'),
    ('class="ticker"', 'ticker de la home'),
    ("bloque-lista", 'lista de bloques de la home'),
]

# Términos que no pueden viajar al sitio público (igual que el guardia del CI).
VETADOS = [
    r"david[ ._-]?antizar",
    r"d_ant\b",
    r"mastermind\.local",
    r"C:[/\\]Users[/\\]d_ant",
]

errores: list[str] = []
avisos: list[str] = []


def err(msg: str) -> None:
    errores.append(msg)


def avi(msg: str) -> None:
    avisos.append(msg)


def htmls_publicadas(raiz: Path) -> list[Path]:
    """Todas las páginas HTML que entran al artefacto publicado."""
    out: list[Path] = []
    if (raiz / "index.html").exists():
        out.append(raiz / "index.html")
    for carpeta in ("kit", "blog", "fuentes", "zona"):
        d = raiz / carpeta
        if d.is_dir():
            out.extend(sorted(d.rglob("*.html")))
    return out


def leer(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


# ─────────────────────────── 1-3. Datos y contenido ───────────────────────────

def validar_kits_json(raiz: Path) -> list[dict]:
    p = raiz / "data" / "kits.json"
    if not p.exists():
        err("no existe data/kits.json")
        return []
    try:
        data = json.loads(leer(p))
    except json.JSONDecodeError as e:
        err(f"data/kits.json no parsea: {e}")
        return []

    kits = data.get("kits", [])
    if not kits:
        err("data/kits.json no tiene 'kits'")
        return []

    campos = ("id", "titulo", "slug", "icono", "resumen", "secciones",
              "paraQuien", "paraQuien_no", "coste_total")
    vistos: set[str] = set()
    for k in kits:
        slug = k.get("slug", "?")
        for c in campos:
            if not k.get(c):
                err(f"kit '{slug}': falta el campo obligatorio '{c}'")

        if slug in vistos:
            err(f"slug duplicado en kits.json: '{slug}'")
        vistos.add(slug)

        secciones = k.get("secciones") or []
        if not secciones:
            err(f"kit '{slug}': sin secciones (ficha vacía = página rota)")
            continue
        total_items = 0
        for si, s in enumerate(secciones, 1):
            if not s.get("titulo"):
                err(f"kit '{slug}' secc.{si}: sin título")
            items = s.get("items") or []
            if not items:
                err(f"kit '{slug}' secc.{si}: sin items")
                continue
            for it in items:
                total_items += 1
                prod = (it.get("producto") or "").strip()
                if not prod:
                    err(f"kit '{slug}' secc.{si}: item sin 'producto'")
                if not (it.get("descripcion") or "").strip():
                    avi(f"kit '{slug}' secc.{si} '{prod[:40]}': item sin descripción")
                if not (it.get("precio_aprox") or "").strip():
                    avi(f"kit '{slug}' secc.{si} '{prod[:40]}': item sin precio_aprox")
                enlace = it.get("afiliado") or it.get("busqueda")
                if not enlace:
                    # Hay items legítimamente no comprables (medicación con receta,
                    # acuerdos, consejos). El render los pinta como «no se compra
                    # online». No es un error; el invariante real está en la ficha
                    # (debe tener compra), que se valida en validar_ficha_generada.
                    avi(f"kit '{slug}' secc.{si} '{prod[:40]}': item sin enlace "
                        f"(consejo/no comprable — marcar 'sin_enlace': true)")
                elif "amazon." in enlace and f"tag={TAG}" not in enlace:
                    err(f"kit '{slug}' secc.{si} '{prod[:40]}': enlace sin tag={TAG}")
        # Un kit debe ser comprable: si casi nada tiene enlace, es media página.
        con_enlace = sum(1 for s in secciones for it in (s.get("items") or [])
                         if it.get("afiliado") or it.get("busqueda"))
        if total_items and con_enlace == 0:
            err(f"kit '{slug}': ninguna sección tiene enlace de compra")
        elif total_items and con_enlace / total_items < 0.3:
            avi(f"kit '{slug}': solo {con_enlace}/{total_items} items con enlace "
                f"(<30%) — ¿kit poco comprable?")
        if total_items == 0:
            err(f"kit '{slug}': 0 items en todas las secciones")
    return kits


def validar_blog_json(raiz: Path) -> None:
    p = raiz / "data" / "blog.json"
    if not p.exists():
        avi("no existe data/blog.json (¿aún no generado?)")
        return
    try:
        data = json.loads(leer(p))
    except json.JSONDecodeError as e:
        err(f"data/blog.json no parsea: {e}")
        return
    for e in data.get("entradas", []):
        slug = e.get("slug", "?")
        if not isinstance(e.get("cuerpo"), str) or not e.get("cuerpo").strip():
            err(f"blog '{slug}': sin 'cuerpo' → la ficha saldría con 'undefined'")
        if not e.get("titulo"):
            err(f"blog '{slug}': sin título")
        if not e.get("fecha"):
            avi(f"blog '{slug}': sin 'fecha' (generar-seo.py puede fallar)")


# ─────────────────── 2. Cruce dirs ↔ kits.json ↔ sitemap ───────────────────

def validar_cruce(raiz: Path, kits: list[dict]) -> None:
    slugs = {k["slug"] for k in kits if k.get("slug")}
    dirs = {d.name for d in (raiz / "kit").iterdir() if d.is_dir()} if (raiz / "kit").is_dir() else set()

    for d in sorted(dirs - slugs):
        err(f"kit/{d}/: directorio sin entrada en kits.json (página invisible)")
    for s in sorted(slugs - dirs):
        err(f"kit '{s}': en kits.json pero sin directorio kit/{s}/ (enlace = 404)")

    for s in sorted(slugs):
        if s.startswith("kit-kit-"):
            avi(f"slug con prefijo duplicado: '{s}' (revisar generación de slug)")

    sm = raiz / "sitemap.xml"
    if sm.exists():
        urls = re.findall(r"<loc>([^<]+)</loc>", leer(sm))
        en_sm = {u.rstrip("/").split("/")[-1] for u in urls if "/kit/" in u}
        for s in sorted(slugs - en_sm):
            err(f"kit '{s}': falta en sitemap.xml")
        for s in sorted(en_sm - slugs):
            err(f"sitemap.xml: ruta /kit/{s}/ que no corresponde a ningún kit")
    else:
        avi("no existe sitemap.xml")


# ──────────────── 4. La ficha generada es una ficha de verdad ────────────────

def validar_ficha_generada(raiz: Path, slug: str, kit: dict) -> None:
    p = raiz / "kit" / slug / "index.html"
    if not p.exists():
        err(f"kit/{slug}/index.html no existe")
        return
    h = leer(p)

    def falta(cond: bool, msg: str) -> None:
        if not cond:
            err(f"kit/{slug}: {msg}")

    falta('class="ficha"' in h, "sin <section class=\"ficha\"> (no es una ficha)")
    falta("ficha-cab" in h, "sin .ficha-cab (cabecera de ficha)")
    falta('class="volver"' in h, "sin enlace «← Volver»")
    n_sec = h.count('class="seccion-kit"')
    falta(n_sec >= 1, "sin ninguna .seccion-kit (página vacía)")

    tiene_items = any((s.get("items") or []) for s in (kit.get("secciones") or []))
    if tiene_items:
        falta("barra-progreso" in h, "sin .barra-progreso")
        falta("btn-amazon" in h or "amazon.es" in h,
              "sin ningún enlace de compra Amazon (media página)")
        falta("armarCesta" in h, "sin botón de cesta (armarCesta)")

    for marca, desc in MARCADORES_HOME:
        if marca in h:
            err(f"kit/{slug}: contiene '{marca}' ({desc}) → parece la HOME "
                f"copiada dentro del kit")

    # Contador de imprescindibles: debe cuadrar con kits.json (si no, sale
    # «N productos · 0 imprescindibles» y el botón de esenciales desaparece).
    n_es_real = sum(1 for s in (kit.get("secciones") or [])
                    for it in (s.get("items") or [])
                    if it.get("prioridad") == "esencial")
    m_cnt = re.search(r"productos\s*·\s*(\d+)\s*imprescindibles", h)
    if m_cnt and int(m_cnt.group(1)) != n_es_real:
        err(f"kit/{slug}: la ficha dice '{m_cnt.group(1)} imprescindibles' pero "
            f"kits.json tiene {n_es_real} con prioridad=esencial")

    # Botón de cesta coherente: «Llévate todo el kit» sólo si la mayoría de los
    # productos tienen ficha /dp/ que añadir al carrito. Con poca cobertura el
    # botón llevaría a una cesta casi vacía (botón muerto/engañoso).
    items_k = [it for s in (kit.get("secciones") or []) for it in (s.get("items") or [])]
    n_dp = sum(1 for it in items_k
               if re.search(r"/dp/[A-Z0-9]{10}", it.get("afiliado") or ""))
    cov = (n_dp / len(items_k)) if items_k else 0
    if cov < 0.4 and "Llévate todo el kit" in h:
        err(f"kit/{slug}: botón «Llévate todo el kit» con solo {cov:.0%} de fichas "
            f"/dp/ (no añadiría el kit: debería ser la búsqueda de Amazon)")
    if cov >= 0.4 and "Ver todo el kit en Amazon" in h:
        err(f"kit/{slug}: botón de búsqueda con {cov:.0%} de fichas /dp/ "
            f"(podría montar la cesta de verdad)")

    # La ficha debe conservar la estructura envolvente.
    for mini in ("site-header", "site-footer", 'id="app"'):
        falta(mini in h, f"falta '{mini}' (estructura rota)")


# ──────────────── 5-6. Estructura común y versión CSS/JS ────────────────

def validar_estructura(raiz: Path) -> None:
    for p in htmls_publicadas(raiz):
        h = leer(p)
        rel = p.relative_to(raiz).as_posix()
        for marcador, nombre in (("site-header", "cabecera"), ("site-footer", "pie"),
                                 ('id="app"', "contenedor #app")):
            if marcador not in h:
                err(f"{rel}: sin {nombre} ('{marcador}')")
        if 'class="ubar"' not in h:
            avi(f"{rel}: sin barra superior (.ubar)")


def validar_versiones(raiz: Path) -> None:
    css_v: dict[str, list[str]] = {}
    ui_v: dict[str, list[str]] = {}
    rotas: list[str] = []
    malformadas: list[str] = []
    for p in htmls_publicadas(raiz):
        h = leer(p)
        rel = p.relative_to(raiz).as_posix()
        m = re.search(r"styles\.css\?v=([0-9a-zA-Z]+)", h)
        if m:
            css_v.setdefault(m.group(1), []).append(rel)
        else:
            avi(f"{rel}: sin styles.css?v=")
        m = re.search(r"ui\.js\?v=([0-9a-zA-Z]+)", h)
        if m:
            ui_v.setdefault(m.group(1), []).append(rel)
            # Etiqueta rota: ui.js?v=XXX sin cierre ">
            if not re.search(r'ui\.js\?v=[0-9a-zA-Z]+"\s*>', h):
                rotas.append(rel)

        # ATRIBUTOS ROTOS: un href/src cuyo valor se «come» el salto de línea.
        # (El 2026-10-02 un regex de bump de versión se comió el '">' del <link>
        #  de styles.css en 67 ficheros y dejó TODA la web sin CSS.)
        for mm in re.finditer(r'(?:href|src)="[^"\n]*\n', h):
            malformadas.append(f"{rel}: {mm.group().strip()[:80]}")
        # El propio <link> del CSS debe cerrar bien.
        for lm in re.finditer(r'<link[^>]*styles\.css[^>]*>', h):
            if not lm.group().endswith('">'):
                malformadas.append(f"{rel}: <link styles.css> sin cerrar: {lm.group()[:80]}")

    if len(css_v) > 1:
        err(f"styles.css?v= inconsistente: { {k: len(v) for k, v in css_v.items()} }")
    if len(ui_v) > 1:
        err(f"ui.js?v= inconsistente: { {k: len(v) for k, v in ui_v.items()} }")
    if rotas:
        err(f"etiqueta <script ui.js> rota (sin '\"></script>') en: {rotas[:5]}")
    if malformadas:
        err(f"HTML MAL FORMADO (atributo sin cerrar) en {len(malformadas)} sitio(s): "
            f"{malformadas[:5]} — la web saldría SIN CSS")


# ──────────────── 7. JSON-LD ────────────────

def validar_jsonld(raiz: Path, kits: list[dict]) -> None:
    slugs = {k["slug"] for k in kits}
    rx = re.compile(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', re.S)
    for p in htmls_publicadas(raiz):
        h = leer(p)
        rel = p.relative_to(raiz).as_posix()
        for i, m in enumerate(rx.finditer(h), 1):
            raw = m.group(1)
            if "{{" in raw or "}}" in raw:
                err(f"{rel}: JSON-LD #{i} con dobles llaves {{{{" )
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError as e:
                err(f"{rel}: JSON-LD #{i} no parsea ({e})")
                continue
            if obj.get("@type") == "ItemList":
                for it in obj.get("itemListElement", []):
                    u = it.get("url", "")
                    if "/kit/" in u:
                        s = u.rstrip("/").split("/")[-1]
                        if s not in slugs:
                            err(f"{rel}: ItemList referencia /kit/{s}/ inexistente")
            if rel.startswith("blog/") and "author" in obj:
                a = obj.get("author")
                nombre = a.get("name", "") if isinstance(a, dict) else str(a)
                # Organization "Kit72h" es la marca: correcto. Solo molesta si
                # aparece un nombre de persona.
                if (isinstance(a, dict) and a.get("@type") == "Person") or \
                   (nombre and "kit72h" not in nombre.lower()):
                    avi(f"{rel}: JSON-LD con 'author' = {nombre!r} (no debe haber nombres)")


# ──────────────── 8. Enlaces internos de la home ────────────────

def validar_enlaces_home(raiz: Path, kits: list[dict]) -> None:
    slugs = {k["slug"] for k in kits}
    fuentes = [raiz / "index.html", raiz / "js" / "ui.js"]
    rx = re.compile(r'href="(/kit/[^"#?]+)"')
    for p in fuentes:
        if not p.exists():
            continue
        h = leer(p)
        for href in sorted(set(rx.findall(h))):
            if "${" in href:
                continue  # template literal (p. ej. `/kit/${k.slug}/`), no es un enlace real
            s = href.rstrip("/").split("/")[-1]
            if s and s not in slugs:
                err(f"{p.name}: enlace interno {href} → no existe ese kit")


# ──────────────── 10. Guardia de privacidad ────────────────

def validar_privacidad(raiz: Path) -> None:
    rx = re.compile("|".join(VETADOS), re.I)
    for p in htmls_publicadas(raiz):
        h = leer(p)
        m = rx.search(h)
        if m:
            err(f"{p.relative_to(raiz).as_posix()}: término vetado '{m.group()}'")


# ─────────────────────────────── main ───────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description="Gate de calidad de kit72h")
    ap.add_argument("--solo-kit", help="valida solo un kit por slug")
    ap.add_argument("--aviso-error", action="store_true",
                    help="trata los AVISOs como ERROR (modo estricto)")
    args = ap.parse_args()

    kits = validar_kits_json(RAIZ)
    validar_blog_json(RAIZ)

    if args.solo_kit:
        kits = [k for k in kits if k.get("slug") == args.solo_kit]
        if not kits:
            err(f"--solo-kit {args.solo_kit}: no existe en kits.json")
    else:
        validar_cruce(RAIZ, kits)
        validar_estructura(RAIZ)
        validar_versiones(RAIZ)
        validar_jsonld(RAIZ, kits)
        validar_enlaces_home(RAIZ, kits)
        validar_privacidad(RAIZ)

    for k in kits:
        validar_ficha_generada(RAIZ, k["slug"], k)

    print("═" * 62)
    print("  GATE DE CALIDAD — kit72h")
    print("═" * 62)

    if avisos:
        print(f"\n⚠  AVISOS ({len(avisos)}):")
        for a in avisos:
            print(f"   · {a}")

    if errores:
        print(f"\n❌ ERRORES ({len(errores)}) — NO PUSHEAR:")
        for e in errores:
            print(f"   ✗ {e}")
    else:
        print("\n✅ 0 errores.")

    if args.aviso_error and avisos:
        print("\n(modo estricto: AVISOs cuentan como ERROR)")
        return 1
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
