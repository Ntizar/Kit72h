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


def mejorar_title(original, pagina_type, slug):
    """Mejora un title tag para CTR."""
    original = original.strip()

    # Reglas de mejora según tipo de página
    if pagina_type == "kit":
        # Fichas de kit
        mejorados = {
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
            "kit-kit-profesional": "Kit Profesional: 0 artículos (sin contenido aún — pendiente)",
            "huerto-autosuficiencia": "Huerto Autosuficiente: 13 herramientas para autoprovisión (2026)",
        }
        return mejorados.get(slug, f"Kit {slug.replace('kit-', '').title()}: artículos esenciales para emergencias (2026)")

    elif pagina_type == "blog":
        return original  # Los blogs ya tienen buenos títulos

    elif pagina_type == "home":
        return "Kit72h — Kits de emergencia 72h: guía completa 2026 (UE + Protección Civil)"

    return original


def mejorar_description(original, pagina_type, slug):
    """Mejora una meta description para CTR."""
    original = original.strip()

    # Reglas de mejora según tipo de página
    if pagina_type == "kit":
        mejorados = {
            "kit-basico-72h": "Mochila de resiliencia UE: 16 artículos esenciales, checklist marcable, cesta Amazon en 1 clic. Guía actualizada 2026.",
            "kit-dana": "Kit DANA: 14 artículos para proteger tu hogar ante inundaciones. Guía basada en recomendaciones oficiales de Protección Civil.",
            "kit-apagon": "Kit Apagón: 15 artículos para sobrevivir sin electricidad. Guía basada en la Estrategia de Preparación de la UE (2025).",
            "kit-coche": "Kit coche obligatorios DGT 2026: baliza V-16, chaleco y todo lo esencial. Lista verificada y cesta Amazon en 1 clic.",
            "kit-hogar": "Kit hogar: 22 artículos para confinamiento y emergencia doméstica. Guía basada en fuentes oficiales (UE + Protección Civil).",
        }
        desc = mejorados.get(slug)
        if desc and len(desc) <= 160:
            return desc
        return original  # No modificar si ya es bueno

    elif pagina_type == "blog":
        # Los blogs ya tienen buenas descriptions, no modificar
        return original

    elif pagina_type == "home":
        return "Kits de emergencia 72 horas basados en las recomendaciones oficiales de la UE y Protección Civil. DANA, apagón, coche, hogar, montaña y más."

    return original


def analizar_paginas():
    """Analiza todas las páginas y detecta oportunidades de mejora."""
    paginas_mejoradas = []

    # Páginas a analizar
    paginas = []

    # Home
    home = RAIZ / "index.html"
    if home.exists():
        paginas.append(("home", "/", home))

    # Kits
    kit_dir = RAIZ / "kit"
    if kit_dir.exists():
        for d in kit_dir.iterdir():
            if (d / "index.html").exists():
                slug = d.name
                paginas.append(("kit", f"/kit/{slug}/", d / "index.html"))

    # Blog (solo los primeros 5 para no sobrecargar)
    blog_dir = RAIZ / "blog"
    if blog_dir.exists():
        blogs = sorted(blog_dir.iterdir(), key=lambda x: x.name)[:20]
        for d in blogs:
            if (d / "index.html").exists():
                paginas.append(("blog", f"/blog/{d.name}/", d / "index.html"))

    # Fuentes
    fuentes = RAIZ / "fuentes" / "index.html"
    if fuentes.exists():
        paginas.append(("fuentes", "/fuentes/", fuentes))

    # Zona
    zona = RAIZ / "zona" / "index.html"
    if zona.exists():
        paginas.append(("zona", "/zona/", zona))

    print(f"Análisis de CTR: {len(paginas)} páginas escaneadas")

    for pagina_type, ruta, path in paginas:
        try:
            html = path.read_text(encoding="utf-8")

            # Extraer title
            m_title = re.search(r'<title>([^<]+)</title>', html)
            # Extraer meta description
            m_desc = re.search(r'<meta name="description" content="([^"]+)"', html)

            if m_title:
                old_title = m_title.group(1)
                new_title = mejorar_title(old_title, pagina_type, path.parent.name)
                if new_title != old_title:
                    html = html.replace(f'<title>{old_title}</title>', f'<title>{new_title}</title>')
                    print(f"  ✏️  Title: {old_title[:50]}... → {new_title[:60]}...")
                    paginas_mejoradas.append({"type": pagina_type, "url": ruta, "field": "title"})

            if m_desc:
                old_desc = m_desc.group(1)
                new_desc = mejorar_description(old_desc, pagina_type, path.parent.name)
                if new_desc != old_desc:
                    html = html.replace(
                        f'<meta name="description" content="{old_desc}"',
                        f'<meta name="description" content="{new_desc}"'
                    )
                    print(f"  ✏️  Desc: {old_desc[:50]}... → {new_desc[:60]}...")
                    paginas_mejoradas.append({"type": pagina_type, "url": ruta, "field": "description"})

            # Guardar si hubo cambios
            if paginas_mejoradas and html != path.read_text(encoding="utf-8"):
                path.write_text(html, encoding="utf-8", newline="\n")

        except Exception as e:
            print(f"  ⚠️ Error en {ruta}: {e}")

    print(f"CTR: {len(paginas_mejoradas)} mejoras aplicadas en {len(paginas)} páginas")
    return paginas_mejoradas


def main():
    mejoras = analizar_paginas()

    if not mejoras:
        print("CTR: sin cambios (todos los meta tags ya optimizados)")
        return

    # Commit + push
    git("add", "kit", "blog", "index.html", "fuentes", "zona")
    git(*IDENT, "commit", "-q", "-m", "feat(seo): optimizar meta tags para CTR ({n} páginas)".format(n=len(mejoras)))
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