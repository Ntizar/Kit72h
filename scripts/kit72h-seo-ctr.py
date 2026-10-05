#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — optimización de meta tags para CTR (Click-Through-Rate).

Script que:
1. Lee todas las páginas HTML del sitio
2. Analiza los meta title y description actuales
3. Mejora los títulos y descriptions para maximizar CTR en Google
   - Añadir números (más de 10 elementos)
   - Añadir urgencia/beneficio (2026, actualizado, guía completa)
   - Mantener <70 caracteres para título, <160 para description
4. Actualiza los metadatos sin cambiar el contenido
5. Regenera SEO + prerender + commit+push

Estrategia de CTR:
- Títulos: [Nº] + [keyword] + [beneficio] + [año]
  Ej: "Kit 72h: los 16 esenciales que la UE recomienda (2026)"
- Descriptions: [problema] + [solución] + [urgencia]
  Ej: "Los primeros 30 minutos no son para buscar pilas a oscuras..."
"""

import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
IDENT = ["-c", "user.name=Mastermind", "-c", "user.email=bot@kit72h.local"]


def run(*args, timeout=300):
    return subprocess.run(args, cwd=RAIZ, capture_output=True, text=True, timeout=timeout)


def git(*args):
    return run("git", *args)


# ── Reglas de mejora SEO ─────────────────────────────────────────────────
# Se aplican a los campos JSON (titulo/resumen) y prerender los inyecta
# en <title>, <meta description>, og:title, og:description del HTML.

KIT_TITULOS = {
    "kit-basico-72h": "Kit 72h Básico: los 16 esenciales de la UE (2026) → Guía completa",
    "kit-dana": "Kit DANA / Inundación: 14 artículos que protegen tu hogar (2026)",
    "kit-apagon": "Kit Apagón: 15 artículos para sobrevivir sin luz (2026)",
    "kit-coche": "Kit Coche 2026: obligatorios + opcionales DGT (guardar en maletero)",
    "kit-hogar": "Kit Hogar/Confinamiento: 22 artículos de supervivencia (2026)",
    "kit-montana": "Kit Montaña: 13 esenciales para supervivencia outdoor (2026)",
    "kit-calor": "Kit Calor/ Ola de calor: 7 artículos que salvan vidas (2026)",
    "kit-evacuacion": "Kit Evacuación: 14 artículos para huir con vida (2026)",
    "huerto-autosuficiencia": "Huerto Autosuficiente: 13 herramientas para autoprovisión (2026)",
    "kit-30-dias": "Kit 30 Días: 16 artículos para un mes sin suministros (2026)",
    "kit-bebe": "Kit Bebé: 32 artículos esenciales para proteger a tu hijo (2026)",
    "kit-mayores": "Kit Mayores: 27 artículos para proteger a personas dependientes (2026)",
    "kit-mascotas": "Kit Mascotas: 23 artículos para proteger a tu animal (2026)",
    "kit-frio": "Kit Frío/Invierno: 27 artículos para sobrevivir al frío (2026)",
    "kit-terremoto": "Kit Terremoto: 26 artículos para protección sísmica (2026)",
    "kit-incendio": "Kit Incendio: 21 artículos para protección contra incendios (2026)",
    "kit-kit-profesional": "Kit Profesional: energía y autonomía total (2026)",
    "kit-comunicacion": "Kit Comunicación: walkies, radio y messenger satelital (2026)",
    "kit-starlink": "Kit Starlink: internet satelital para emergencias (2026)",
}

KIT_DESCRIPCIONES = {
    "kit-basico-72h": "Mochila de resiliencia UE: 16 artículos esenciales, checklist marcable, cesta Amazon en 1 clic. Guía actualizada 2026.",
    "kit-dana": "Kit DANA: 14 artículos para proteger tu hogar ante inundaciones. Guía basada en recomendaciones oficiales de Protección Civil.",
    "kit-apagon": "Kit Apagón: 15 artículos para sobrevivir sin electricidad. Guía basada en la Estrategia de Preparación de la UE (2025).",
    "kit-coche": "Kit coche obligatorios DGT 2026: baliza V-16, chaleco y todo lo esencial. Lista verificada y cesta Amazon en 1 clic.",
    "kit-hogar": "Kit hogar: 22 artículos para confinamiento y emergencia doméstica. Guía basada en fuentes oficiales (UE + Protección Civil).",
    "kit-montana": "Kit montaña: 13 esenciales para supervivencia outdoor. Navegación, abrigo y comunicación sin red. Guía práctica 2026.",
    "kit-calor": "Kit calor: 7 artículos que salvan vidas ante ola de calor extrema. Hidratación, abrigo solar y primeros auxilios.",
    "kit-evacuacion": "Kit evacuación: 14 artículos para huir con vida. Mochila ligera con lo esencial en 30 segundos. Preparación rápida 2026.",
    "huerto-autosuficiencia": "Huerto autosuficiente: 13 herramientas para autoprovisión de alimentos. Semillas, compost y riego autónomo 2026.",
    "kit-30-dias": "Kit 30 días: 16 artículos para un mes sin suministros. Agua, comida y energía para sobrevivir un mes sin red 2026.",
    "kit-bebe": "Kit bebé: 32 artículos esenciales para proteger a tu hijo en emergencias. Alimentación, higiene y salud 2026.",
    "kit-mayores": "Kit mayores: 27 artículos para proteger a personas dependientes. Medicación, movilidad y comunicación 2026.",
    "kit-mascotas": "Kit mascotas: 23 artículos para proteger a tu animal en emergencias. Alimentación, identificación y primeros auxilios.",
    "kit-frio": "Kit frío: 27 artículos para sobrevivir al invierno extremo. Calefacción alternativa, abrigo y gestión del frío 2026.",
    "kit-terremoto": "Kit terremoto: 26 artículos para protección sísmica. Estructura, iluminación y comunicación post-terremoto 2026.",
    "kit-incendio": "Kit incendio: 21 artículos para protección contra incendios forestales. Respiración, refugio y evacuación 2026.",
    "kit-kit-profesional": "Kit profesional: energía y autonomía total con paneles solares, baterías y Starlink 2026.",
    "kit-comunicacion": "Kit comunicación: walkies PMR446, radio y messenger satelital cuando falla la red. Guía completa 2026.",
    "kit-starlink": "Kit Starlink: internet satelital cuando se caen todas las redes. Conectividad real desde cualquier punto 2026.",
}

HOME_TITLE = "Kit72h — Kits de emergencia 72h: guía completa 2026 (UE + Protección Civil)"
HOME_DESC = "Kits de emergencia 72 horas basados en las recomendaciones oficiales de la UE y Protección Civil. DANA, apagón, coche, hogar, montaña y más."

# ── Aplicar mejoras ──────────────────────────────────────────────────────


def aplicar_mejoras_kits():
    """Actualiza titulo y resumen en data/kits.json con valores SEO-optimizados."""
    with open(RAIZ / "data/kits.json", encoding="utf-8") as f:
        data = json.load(f)

    mejoradas = []
    for kit in data["kits"]:
        slug = kit["slug"]
        nuevo_titulo = KIT_TITULOS.get(slug)
        nuevo_resumen = KIT_DESCRIPCIONES.get(slug)

        if nuevo_titulo and kit["titulo"] != nuevo_titulo:
            print(f"  ✏️  Titulo (JSON): {kit['titulo'][:50]}... → {nuevo_titulo[:60]}...")
            kit["titulo"] = nuevo_titulo
            mejoradas.append({"slug": slug, "field": "title"})

        if nuevo_resumen and kit["resumen"] != nuevo_resumen:
            print(f"  ✏️  Resumen: {kit['resumen'][:50]}... → {nuevo_resumen[:60]}...")
            kit["resumen"] = nuevo_resumen
            mejoradas.append({"slug": slug, "field": "description"})

    if mejoradas:
        with open(RAIZ / "data/kits.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")

    return mejoradas


def aplicar_mejoras_blog():
    """Actualiza titulo y resumen en data/blog.json con valores SEO-optimizados."""
    with open(RAIZ / "data/blog.json", encoding="utf-8") as f:
        data = json.load(f)

    mejoradas = []
    for entrada in data["entradas"]:
        slug = entrada["slug"]
        # Reglas de mejora para blog: añadir año, numero si falta
        titulo = entrada.get("titulo", "")
        resumen = entrada.get("resumen", "")

        # Regla 1: añadir (2026) si no está
        if "(2026)" not in titulo and not titulo.endswith("(2025)"):
            nuevo = titulo.rstrip(")") + " (2026)"
            print(f"  ✏️  Blog title: {titulo[:50]}... → {nuevo[:60]}...")
            entrada["titulo"] = nuevo
            mejoradas.append({"slug": slug, "field": "title"})

        # Regla 2: resumen > 155 caracteres → trunca
        if len(resumen) > 155:
            nuevo = resumen[:152] + "..."
            print(f"  ✏️  Blog desc: {resumen[:50]}... → {nuevo[:60]}...")
            entrada["resumen"] = nuevo
            mejoradas.append({"slug": slug, "field": "description"})

    if mejoradas:
        with open(RAIZ / "data/blog.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")

    return mejoradas


def aplicar_mejoras_index():
    """Actualiza meta title/description en index.html (no lo toca prerender)."""
    home = RAIZ / "index.html"
    if not home.exists():
        return []

    html = home.read_text(encoding="utf-8")
    mejoradas = []

    # Title
    m = re.search(r'<title>([^<]+)</title>', html)
    if m and m.group(1) != HOME_TITLE:
        html = html.replace(m.group(0), f'<title>{HOME_TITLE}</title>')
        print(f"  ✏️  Home title: {m.group(1)[:50]}... → {HOME_TITLE[:60]}...")
        mejoradas.append({"field": "title"})

    # Description
    m = re.search(r'<meta name="description" content="([^"]+)"', html)
    if m and m.group(1) != HOME_DESC:
        html = html.replace(m.group(0), f'<meta name="description" content="{HOME_DESC}"')
        print(f"  ✏️  Home desc: {m.group(1)[:50]}... → {HOME_DESC[:60]}...")
        mejoradas.append({"field": "description"})

    if mejoradas:
        home.write_text(html, encoding="utf-8", newline="\n")

    return mejoradas


def analizar_paginas():
    """Analiza y mejora meta tags en fuentes reales (JSON → prerender, index.html directo)."""
    mejoradas = []

    # 1. JSON kits (prerender lee de aquí)
    mejoradas += aplicar_mejoras_kits()

    # 2. JSON blog (prerender lee de aquí)
    mejoradas += aplicar_mejoras_blog()

    # 3. index.html (prerender no lo regenera completo)
    mejoradas += aplicar_mejoras_index()

    # 4. zona/ y fuentes/ (no regenerados por prerender)
    for path_name in ["zona", "fuentes"]:
        path = RAIZ / path_name / "index.html"
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        m_title = re.search(r'<title>([^<]+)</title>', html)
        m_desc = re.search(r'<meta name="description" content="([^"]+)"', html)

        if m_title:
            new_title = HOME_TITLE if path_name == "zona" else "Fuentes oficiales — Kit72h: UE, Protección Civil, AEMET y más"
            if m_title.group(1) != new_title:
                html = html.replace(m_title.group(0), f'<title>{new_title}</title>')
                print(f"  ✏️  {path_name} title: {m_title.group(1)[:50]}... → {new_title[:60]}...")
                mejoradas.append({"page": path_name, "field": "title"})

        if m_desc:
            new_desc = "Tu zona: mapa interactivo con hospitales, farmacias, refugios y puntos de encuentro en OpenStreetMap. Consulta OpenStreetMap y la Overpass API en tiempo real." if path_name == "zona" else "Todas las fuentes oficiales de donde se basan los kits: UE, Protección Civil, AEMET, REE, AESAN y más. Actualizadas y verificadas."
            if m_desc.group(1) != new_desc:
                html = html.replace(m_desc.group(0), f'<meta name="description" content="{new_desc}"')
                print(f"  ✏️  {path_name} desc: {m_desc.group(1)[:50]}... → {new_desc[:60]}...")
                mejoradas.append({"page": path_name, "field": "description"})

        # Guardar
        new_html = path.read_text(encoding="utf-8")
        if html != new_html:
            path.write_text(html, encoding="utf-8", newline="\n")

    print(f"CTR: {len(mejoradas)} mejoras aplicadas en JSON + HTML")
    return mejoradas


def main():
    mejoras = analizar_paginas()

    if not mejoras:
        print("CTR: sin cambios (todos los meta tags ya optimizados)")
        return

    # 1. Añadir TODO (JSON fuentes + HTML prerender + scripts)
    git("add", "data/kits.json", "data/blog.json")
    git("add", "kit/", "blog/", "index.html", "fuentes/", "zona/")
    git("add", "scripts/generar-seo.py", "scripts/prerender.py", "scripts/kit72h-seo-ctr.py")
    git("add", "llms.txt", "sitemap.xml")
    git(*IDENT, "commit", "-q", "-m", "feat(seo): optimizar meta tags para CTR ({n} mejoras)".format(n=len(mejoras)))

    # 2. Regenerar SEO y prerender (sobrescribe HTML con los nuevos valores de JSON)
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

    # 3. Añadir HTML regenerados y push (todo junto: JSON fuente + HTML final)
    git("add", "-A")
    git(*IDENT, "commit", "--amend", "-q", "--no-edit")
    git("pull", "--rebase", "-q", "origin", "main")
    p = git("push", "-q", "origin", "main")
    if p.returncode == 0:
        print("  ✓ Push completado")
    else:
        print(f"  ⚠️ Push falló: {(p.stderr or '').strip()[:200]}")


if __name__ == "__main__":
    main()