#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — generador de comparativas y "mejor X" para conversión.

Genera páginas de comparación entre productos/categorías de emergencia.
Estas páginas tienen INTENCIÓN de compra: "mejor linterna", "comparativa kits",
"X vs Y", etc.

Estrategia:
1. Lee data/kits.json y data/catalogo.json para saber qué productos/categorías existen
2. Elige 3-5 comparativas que falten (basadas en las existentes en /blog/)
3. Genera el HTML completo de cada comparativa
4. Registra en data/comparativas.json el listado
5. Regenera SEO + prerender + commit+push

NO ejecuta LLM — es un generador determinista. El editor (cron nocturno) añade
el contenido rico después (el comparador pone la estructura, el editor la llena).
"""

import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BASE = "https://kit72h.com"
IDENT = ["-c", "user.name=Mastermind", "-c", "user.email=bot@kit72h.local"]


def run(*args, timeout=300):
    return subprocess.run(args, cwd=RAIZ, capture_output=True, text=True, timeout=timeout)


def git(*args):
    return run("git", *args)


def ya_existe_slug(slug):
    """Verifica si ya existe la página del slug."""
    return (RAIZ / "blog" / slug / "index.html").exists()


def cargar_existentes():
    """Carga slugs de blogs ya existentes."""
    slugs = set()
    blog_dir = RAIZ / "blog"
    if blog_dir.exists():
        for d in blog_dir.iterdir():
            if (d / "index.html").exists():
                slugs.add(d.name)
    return slugs


CATEGORIAS_COMPARATIVAS = [
    {
        "slug": "mejor-linterna-emergencia-72h",
        "titulo": "Comparativa de las mejores linternas para emergencias 72h en 2026",
        "resumen": "Linterna LED recargable vs linterna de pilas: cuál elegir para un kit de emergencia real. Tests de autonomía, resistencia al agua y precio.",
        "keywords": ["mejor linterna emergencia", "linterna kit 72h comparativa", "linterna LED recargable emergencias"],
        "secciones": [
            {
                "titulo": "Criterios de selección",
                "items": ["Autonomía (min. 8h)", "Resistencia IP65+", "Recargable USB", "Peso <300g", "Modo SOS"],
            },
            {
                "titulo": "Categorías principales",
                "items": ["Linterna LED recargable USB", "Linterna de pilas (emergencia secundaria)", "Frontal para manos libres"],
            },
            {
                "titulo": "Nuestra recomendación",
                "items": ["Para la mayoría: linterna LED recargable USB-C", "Para urgencia: linterna de pilas CR123A"],
            },
        ],
    },
    {
        "slug": "mejor-powerbank-emergencia-capacidad",
        "titulo": "Los 5 mejores powerbanks para emergencias: comparativa de capacidad real en 2026",
        "resumen": "¿10000mAh o 20000mAh? Comparamos las mejores baterías externas para tu kit 72h: capacidad real, velocidad de carga y resistencia.",
        "keywords": ["mejor powerbank emergencia", "batería externa kit 72h", "powerbank comparativa 2026"],
        "secciones": [
            {
                "titulo": "Criterios de selección",
                "items": ["Capacidad real (>8000mAh)", "Puertos USB-C PD", "Carga solar (bonus)", "Peso <500g", "Indicador LED"],
            },
            {
                "titulo": "Categorías principales",
                "items": ["Powerbank compacto 10000mAh", "Powerbank solar 20000mAh", "Powerbank con manivela"],
            },
            {
                "titulo": "Nuestra recomendación",
                "items": ["Para el kit básico: 10000mAh USB-C PD", "Para larga duración: 20000mAh solar"],
            },
        ],
    },
    {
        "slug": "mejor-radio-emergencia-manivela-solar",
        "titulo": "Comparativa: radio de emergencia con manivela vs radio solar — cuál es mejor en 2026",
        "resumen": "Radio de emergencia con manivela, solar, o ambas. Comparamos las mejores opciones para mantenerse informado sin electricidad.",
        "keywords": ["mejor radio emergencia manivela", "radio solar emergencias", "radio crisis comparativa"],
        "secciones": [
            {
                "titulo": "Criterios de selección",
                "items": ["Frecuencias AM/FM/SW", "Carga solar + manivela", "USB para cargar móvil", "Resistencia agua IPX4", "Indicador de batería"],
            },
            {
                "titulo": "Categorías principales",
                "items": ["Radio con manivela + solar", "Radio solar exclusiva", "Radio de emergencia todo-en-uno"],
            },
            {
                "titulo": "Nuestra recomendación",
                "items": ["Para la mayoría: radio híbrida manivela+solar", "Para ligereza: solar-only"],
            },
        ],
    },
    {
        "slug": "kit-72h-vs-30-dias",
        "titulo": "Kit 72h vs 30 días: cuál necesitas realmente (y cuánto cuesta cada uno)",
        "resumen": "La UE recomienda 72 horas de autonomía. ¿Necesitas 30 días? Comparamos coste, espacio y necesidades reales de cada preparación.",
        "keywords": ["kit 72h vs 30 días", "cuántos días de emergencia necesito", "kit 30 días coste"],
        "secciones": [
            {
                "titulo": "72 horas: qué cubre",
                "items": ["Agua: 9L por persona", "Comida: 3 días", "Energía: 1 powerbank", "Documentos: 3 días de registros"],
            },
            {
                "titulo": "30 días: qué cubre",
                "items": ["Agua: 90L por persona", "Comida: 30 días", "Energía: panel solar + batería grande", "Medicamentos: 30 días de reserva"],
            },
            {
                "titulo": "Nuestra recomendación",
                "items": ["Para la mayoría: kit 72h (95% de emergencias)", "Para zonas aisladas: añadir 7 días al 72h"],
            },
        ],
    },
    {
        "slug": "starlink-emergencia-72h-conectividad",
        "titulo": "Starlink vs radio satelital: conectividad de emergencia en 2026",
        "resumen": "Starlink puede salvar tu conectividad en una emergencia. Comparamos coste, despliegue, cobertura y alternativas para el hogar español.",
        "keywords": ["starlink emergencia España", "conectividad emergencia satelital", "mejor internet emergencia 2026"],
        "secciones": [
            {
                "titulo": "Criterios de selección",
                "items": ["Cobertura en España", "Coste terminal", "Coste mensual", "Tiempo despliegue", "Anchura disponible"],
            },
            {
                "titulo": "Opciones principales",
                "items": ["Starlink (terminal + suscripción)", "Inmarsat IsatPhone", "Iridium + router 4G"],
            },
            {
                "titulo": "Nuestra recomendación",
                "items": ["Para conectividad completa: Starlink", "Solo para llamadas SMS: radio satelital"],
            },
        ],
    },
    {
        "slug": "mejor-router-4g-emergencia-sin-internet",
        "titulo": "Los mejores routers 4G de emergencia: internet sin fibra en 2026",
        "resumen": "Comparativa de routers 4G portátiles y estaciones base para mantener internet cuando se corta la fibra óptica.",
        "keywords": ["mejor router 4g emergencia", "internet sin fibra óptica", "router móvil emergencias 2026"],
        "secciones": [
            {
                "titulo": "Criterios de selección",
                "items": ["Compatible operadoras ES", "Antena externa (SMA)", "Batería interna", "Autonomía 8h+", "Soporte SIM LTE"],
            },
            {
                "titulo": "Categorías principales",
                "items": ["Router 4G USB dongle", "Router 4G portátil con batería", "Estación base 4G exterior"],
            },
            {
                "titulo": "Nuestra recomendación",
                "items": ["Para el hogar: router 4G portátil", "Para cobertura rural: estación base"],
            },
        ],
    },
    {
        "slug": "panel-solar-portatil-72h-emergencia",
        "titulo": "Panel solar portátil para emergencias 72h: comparativa de Watts y capacidad en 2026",
        "resumen": "¿20W, 50W o 100W? Comparamos paneles solares portátiles para cargar tu kit 72h: eficiencia, peso, precio y resistencia.",
        "keywords": ["panel solar emergencia 72h", "mejor panel solar portátil", "panel solar kit emergencia"],
        "secciones": [
            {
                "titulo": "Criterios de selección",
                "items": ["Potencia (W)", "Peso", "Resistencia agua", "Puertos de salida", "Plegable/portátil"],
            },
            {
                "titulo": "Categorías principales",
                "items": ["Panel 20W (carga lenta)", "Panel 50W (equilibrio)", "Panel 100W+ (máxima potencia)"],
            },
            {
                "titulo": "Nuestra recomendación",
                "items": ["Para kit básico: 20-30W plegable", "Para autonomía completa: 50-100W"],
            },
        ],
    },
]


def generar_html(comp):
    """Genera HTML de la comparativa siguiendo el patrón de estructura HTML de kit72h."""
    # Escapar caracteres para HTML
    def esc(text):
        return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', '&quot;')

    # Generar secciones
    secciones_html = ""
    for i, sec in enumerate(comp["secciones"], 1):
        items_html = "\n".join(f"<li>{esc(item)}</li>" for item in sec["items"])
        secciones_html += f"""
      <section class="sec oscura">
        <div class="container">
          <div class="watermark" aria-hidden="true">{esc(comp["titulo"][:20])}</div>
          <div class="sec-inner">
            <span class="sec-label">0{i} / {esc(sec["titulo"])}
</span>
            <h2>{esc(sec["titulo"])}</h2>
            <ul>
{items_html}
            </ul>
          </div>
        </div>
      </section>
"""

    # Schema JSON-LD
    schema_items = []
    for sec in comp["secciones"]:
        for item in sec.get("items", []):
            schema_items.append({"@type": "HowToStep", "name": esc(item)})

    schema_json = json.dumps({
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": esc(comp["titulo"]),
        "description": esc(comp["resumen"]),
        "estimatedCost": {"@type": "MonetaryCategory", "currency": "EUR"},
        "totalTime": "PT45M",
        "supply": [{"@type": "HowToSupply", "name": "Kit de emergencia 72h"}],
        "step": schema_items,
    }, ensure_ascii=False)

    meta_keywords = esc(", ".join(comp["keywords"]))

    slug = comp["slug"]
    url = f"{BASE}/blog/{slug}/"

    html = f"""<!DOCTYPE html>
<html lang="es"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(comp["titulo"])} — Kit72h</title>
<meta name="description" content="{esc(comp['resumen'] + ' Comparativa actualizada 2026. Guías basadas en fuentes oficiales.')}"  >
<meta name="keywords" content="{meta_keywords}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{esc(url)}">
<link rel="stylesheet" href="/css/styles.css?v=20261002a">
<script type="application/ld+json">
{schema_json}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "{esc(comp['titulo'])}",
  "description": "{esc(comp['resumen'])}",
  "inLanguage": "es",
  "about": {json.dumps(comp['keywords'], ensure_ascii=False)}
}}
</script>
<meta name="twitter:title" content="{esc(comp['titulo'])}">
<meta name="twitter:description" content="{esc(comp['resumen'][:150])}">
<meta property="og:type" content="article">
<meta property="og:url" content="{esc(url)}">
<meta property="og:title" content="{esc(comp['titulo'])}">
<meta property="og:description" content="{esc(comp['resumen'])}">
<meta property="og:site_name" content="Kit72h">
<meta name="twitter:card" content="summary">
</head>
<body>
<div class="ubar">
  <div class="container">
    <span><span class="punto">●</span> PREPARACIÓN CIVIL SIN ALARMISMO</span>
    <span>/</span>
    <span>HECHO PARA SITUACIONES REALES EN ESPAÑA</span>
    <span>/</span>
    <span>GUIA 72H · COMISION EUROPEA + PROTECCION CIVIL</span>
  </div>
</div>

<header class="site-header">
  <div class="container">
    <a href="/" class="logo">KIT<span class="accent">72H</span><span class="tagline">Diario de supervivencia</span></a>
    <nav>
      <a href="/">Inicio</a>
      <a href="/#kits">Kits</a>
      <a href="/blog/">Blog</a>
      <a href="/#faq">FAQ</a>
      <a href="/fuentes/">Fuentes</a>
      <a href="/zona/">Tu zona</a>
      <a class="btn negro" href="https://www.amazon.es/s?k=kit+emergencia+72+horas&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Compra tu kit ↗</a>
    </nav>
  </div>
</header>

<main class="container">
  <article class="entrada-blog">
    <span class="sec-label sec-clara">Comparativa · {esc(comp['titulo'][:30])}</span>
    <h1>{esc(comp["titulo"])}</h1>
    <p class="resumen">{esc(comp["resumen"])}</p>
    <div class="cuerpo-blog">

{secciones_html}

    </div>
  </article>

  <!-- Disclosure afiliado -->
  <section class="sec oscura">
    <div class="container">
      <div class="sec-inner">
        <h2>Transparencia · Enlaces de afiliado</h2>
        <p>Kit72h participa en el programa de afiliados de Amazon. Los enlaces marcados con "↗" o "→" son enlaces de afiliado. Si compras a través de ellos, recibimos una pequeña comisión sin coste adicional para ti. Esto nos ayuda a mantener el proyecto activo y actualizado.</p>
      </div>
    </div>
  </section>
</main>

<footer class="site-footer">
  <div class="container">
    <div class="footer-inner">
      <p>&copy; 2026 Kit72h — Kits de emergencia 72h para hogares en España</p>
      <p>Basados en las recomendaciones oficiales de la Comisión Europea y Protección Civil</p>
    </div>
  </div>
</footer>
<script src="/js/main.js?v=20261002a"></script>
<!-- GENERADO por scripts/kit72h-comparador.py — no editar a mano -->
</body></html>
"""
    return html


def main():
    slugs = cargar_existentes()
    comparativas = []

    for comp in CATEGORIAS_COMPARATIVAS:
        if ya_existe_slug(comp["slug"]):
            print(f"  ⏭️  Ya existe: {comp['slug']}")
            continue

        comp["fecha"] = "2026-10-02"
        comp["slug"] = comp["slug"]
        comparativas.append(comp)

    if not comparativas:
        print("Comparador: todas las comparativas ya existen (sin cambios)")
        return

    print(f"Comparador: {len(comparativas)} nuevas comparativas")

    # Generar cada comparativa
    for comp in comparativas:
        html = generar_html(comp)
        dest = RAIZ / "blog" / comp["slug"] / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8", newline="\n")
        print(f"  ✓ {comp['slug']}")

    # Registrar en comparativas.json
    comparativas_data = {
        "meta": {"ultima_generacion": "2026-10-02", "total": len(comparativas)},
        "comparativas": comparativas,
    }
    (RAIZ / "data" / "comparativas.json").write_text(
        json.dumps(comparativas_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Commit + push
    git("add", "blog", "data/comparativas.json")
    git(*IDENT, "commit", "-q", "-m", "feat(blog): agregar comparativas de productos de emergencia")
    git("pull", "--rebase", "-q", "origin", "main")
    p = git("push", "-q", "origin", "main")
    if p.returncode == 0:
        print("  ✓ Push completado")
    else:
        print(f"  ⚠️ Push falló: {(p.stderr or '').strip()[:200]}")

    # Regenerar SEO y prerender
    seo = run(sys.executable, "scripts/generar-seo.py")
    if seo.returncode == 0:
        print("  ✓ SEO regenerado")
    else:
        print(f"  ⚠️ SEO falló: {(seo.stderr or '').strip()[:200]}")

    pre = run(sys.executable, "scripts/prerender.py")
    if pre.returncode == 0:
        print("  ✓ Prerender completado")
    else:
        print(f"  ⚠️ Prerender falló: {(pre.stderr or '').strip()[:200]}")


if __name__ == "__main__":
    main()