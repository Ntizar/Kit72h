#!/usr/bin/env python3
"""
Generador de página de blog y home para kit72h.com
Escanea todos los directorios de blog, extrae metadatos de cada index.html,
y regenera blog/index.html (con TODOS los posts) e index.html (con los últimos 9).
"""
import os
import re
import json
import sys
import argparse
from datetime import datetime, date
from pathlib import Path


def extract_blog_meta(html_content):
    """Extrae título, descripción y fecha de un HTML de blog."""
    meta = {}

    title_match = re.search(r'<title>(.*?)</title>', html_content, re.DOTALL)
    if title_match:
        title = title_match.group(1).strip()
        title = re.sub(r'\s*[\u2014\u2013\x2d]\s*Blog\s*Kit72h\s*$', '', title).strip()
        meta['titulo'] = title

    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']', html_content)
    if desc_match:
        meta['resumen'] = desc_match.group(1).strip()

    fecha_match = re.search(r'(\d{4}-\d{2}-\d{2})', html_content)
    if fecha_match:
        meta['fecha'] = fecha_match.group(1)

    lectura_match = re.search(r'(\d+\s*min)', html_content, re.IGNORECASE)
    if lectura_match:
        meta['lectura'] = lectura_match.group(1).strip()

    return meta


def scan_blog_dir(blogs_path):
    """Escanea todos los directorios de blog y devuelve lista de entradas."""
    entries = []
    if not os.path.isdir(blogs_path):
        print("ERROR: directorio no encontrado: " + blogs_path, file=sys.stderr)
        sys.exit(1)

    for entry_name in sorted(os.listdir(blogs_path)):
        entry_path = os.path.join(blogs_path, entry_name)
        if not os.path.isdir(entry_path):
            continue
        if entry_name == 'index.html':
            continue

        index_file = os.path.join(entry_path, 'index.html')
        if not os.path.exists(index_file):
            continue

        with open(index_file, 'r', encoding='utf-8') as f:
            html = f.read()

        meta = extract_blog_meta(html)
        if not meta.get('titulo'):
            continue

        meta['slug'] = entry_name
        meta['url'] = '/blog/' + entry_name + '/'
        entries.append(meta)

    return entries


def load_existing_blog_data(data_path):
    """Carga blog.json existente y devuelve dict con slug -> entry."""
    blog_json = os.path.join(data_path, 'blog.json')
    if not os.path.exists(blog_json):
        return None

    with open(blog_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    entries_dict = {}
    for e in data.get('entradas', []):
        entries_dict[e.get('slug', '')] = e

    return {'data': data, 'entries': entries_dict}


def build_new_blog_entries(data_path, scanned_entries, existing_data):
    """Construye la lista: existentes + nuevas (sin perder las existentes)."""
    entries_dict = existing_data['entries'] if existing_data else {}
    meta_data = existing_data['data'].get('meta', {}) if existing_data else {}

    new_entries = []
    added_slugs = set()

    for slug, entry in entries_dict.items():
        blog_index = os.path.join(data_path, '..', 'blog', slug, 'index.html')
        if os.path.exists(blog_index):
            new_entries.append(entry)
            added_slugs.add(slug)

    for entry in scanned_entries:
        slug = entry['slug']
        if slug not in added_slugs:
            new_entries.append(entry)
            added_slugs.add(slug)

    new_entries.sort(key=lambda e: e.get('fecha', '0000-00-00'), reverse=True)

    total = len(new_entries)
    meta_data['total'] = total
    meta_data['actualizado'] = date.today().strftime('%Y-%m-%d')
    meta_data['ultima_revision'] = meta_data.get('ultima_revision', meta_data['actualizado'])
    meta_data['nota_editor'] = (
        meta_data['actualizado'] + ': generador automático reconectó ' + str(total)
        + ' entradas. Escaneo completo de ' + str(total) + ' directorios.'
    )

    return {'meta': meta_data, 'entradas': new_entries}


def build_card_html(entry, i):
    """Construye el HTML de una tarjeta de blog."""
    slug = entry['slug']
    titulo = entry.get('titulo', 'Sin título')
    resumen = entry.get('resumen', '')
    lectura = entry.get('lectura', '')
    fecha = entry.get('fecha', '')

    fecha_display = ''
    if fecha:
        try:
            d = datetime.strptime(fecha, '%Y-%m-%d')
            fecha_display = d.strftime('%d/%m/%Y')
        except Exception:
            fecha_display = fecha

    parts = []
    parts.append('      <a class="card-kit card-blog" href="/blog/' + slug + '/">')
    parts.append('        <div class="fila-top"><span class="num">' + str(i).zfill(2) + '</span></div>')
    parts.append('        <h2>' + titulo + '</h2>')
    parts.append('        <p>' + resumen + '</p>')
    parts.append('        <span class="meta-blog">')

    if lectura:
        parts.append('\u23f1 ' + lectura)
    if fecha_display:
        if lectura:
            parts.append(' \u00b7 ')
        parts.append(fecha_display)

    parts.append('</span>')
    parts.append('      </a>')
    return '\n'.join(parts)


def generate_blog_index(new_data, css_version):
    """Genera blog/index.html con TODAS las entradas."""
    entries = new_data['entradas']
    cards_html = []
    for i, entry in enumerate(entries, 1):
        cards_html.append(build_card_html(entry, i))

    cards_block = '\n'.join(cards_html)
    desc = new_data['meta'].get('descripcion', '')

    html_parts = []
    html_parts.append('<!DOCTYPE html>')
    html_parts.append('<html lang="es"><head>')
    html_parts.append('<meta charset="UTF-8">')
    html_parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html_parts.append('<title>Blog \u2014 Kit72h</title>')
    html_parts.append('<meta name="description" content="' + desc + '">')
    html_parts.append('<link rel="preconnect" href="https://fonts.googleapis.com">')
    html_parts.append('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="">')
    html_parts.append('<link href="https://fonts.googleapis.com/css2?family=Anton&amp;family=IBM+Plex+Mono:wght@400;700&amp;display=swap" rel="stylesheet">')
    html_parts.append('<link rel="stylesheet" href="/css/styles.css?v=' + css_version + '">')
    html_parts.append('<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 64 64\'%3E%3Crect width=\'64\' height=\'64\' fill=\'%23D14B27\'/%3E%3Ctext x=\'32\' y=\'42\' font-family=\'Arial Black,Arial\' font-size=\'26\' font-weight=\'900\' fill=\'%23F1EBDF\' text-anchor=\'middle\'%3E72%3C/text%3E%3C/svg%3E">')

    # Schema WebSite
    html_parts.append('<script type="application/ld+json">')
    html_parts.append('{')
    html_parts.append('  "@context": "https://schema.org",')
    html_parts.append('  "@type": "WebSite",')
    html_parts.append('  "name": "Kit72h",')
    html_parts.append('  "url": "https://kit72h.com/",')
    html_parts.append('  "inLanguage": "es",')
    html_parts.append('  "description": "Kits de emergencia 72 horas y 30 días para hogares en España, basados en las recomendaciones oficiales de la Unión Europea y Protección Civil. Listas de producto verificadas y guías prácticas.",')
    html_parts.append('  "about": ["preparación ante emergencias", "kit 72 horas", "DANA", "apagón", "supervivencia urbana", "protección civil España"]')
    html_parts.append('}')
    html_parts.append('</script>')

    # Schema FAQPage
    html_parts.append('<script type="application/ld+json">')
    html_parts.append('{')
    html_parts.append('  "@context": "https://schema.org",')
    html_parts.append('  "@type": "FAQPage",')
    html_parts.append('  "mainEntity": [')
    html_parts.append('    {')
    html_parts.append('      "@type": "Question",')
    html_parts.append('      "name": "\\u00bfQu\\u00e9 es un kit de emergencia de 72 horas?",')
    html_parts.append('      "acceptedAnswer": { "@type": "Answer", "text": "Es el conjunto de suministros (agua, comida no perecedera, luz, radio, botiquín y documentación) para que un hogar sea autónomo 72 horas ante un apagón, DANA o catástrofe. La Estrategia de Preparación de la Unión Europea de marzo de 2025 recomienda que todos los hogares tengan provisiones para 72 horas. En Kit72h tienes la lista completa basada en fuentes oficiales." }')
    html_parts.append('    },')
    html_parts.append('    {')
    html_parts.append('      "@type": "Question",')
    html_parts.append('      "name": "\\u00bfCuánta agua debo almacenar para una emergencia?",')
    html_parts.append('      "acceptedAnswer": { "@type": "Answer", "text": "3 litros por persona y día solo para beber, más 2-4 litros adicionales para higiene básica. Para 72 horas, una familia de 4 personas necesita unos 36 litros de agua potable. El agua debe renovarse cada 6 meses y guardarse lejos del sol y de productos de limpieza." }')
    html_parts.append('    },')
    html_parts.append('    {')
    html_parts.append('      "@type": "Question",')
    html_parts.append('      "name": "\\u00bfQué es obligatorio llevar en el coche en España en 2026?",')
    html_parts.append('      "acceptedAnswer": { "@type": "Answer", "text": "Desde el 1 de enero de 2026, la baliza V-16 conectada homologada por la DGT es el único medio legal de se\\u00f1alizar una parada en vía, sustituyendo a los triángulos. Adem\\u00e1s son obligatorios el chaleco reflectante dentro del habit\\u00e1culo y la documentaci\\u00f3n del veh\\u00edculo." }')
    html_parts.append('    },')
    html_parts.append('    {')
    html_parts.append('      "@type": "Question",')
    html_parts.append('      "name": "\\u00bfQué hacer en los primeros 30 minutos de un apagón?",')
    html_parts.append('      "acceptedAnswer": { "@type": "Answer", "text": "No llamar al 112 salvo emergencia real (usa mensajes), encender una radio a pilas o de dinamo para informarte de fuentes oficiales, desconectar electrodomésticos sensibles al retorno de la luz, usar linterna en lugar de velas y racionar la bater\\u00eda del móvil en modo avión." }')
    html_parts.append('    }')
    html_parts.append('  ]')
    html_parts.append('}')
    html_parts.append('</script>')
    html_parts.append('</head><body>')
    # Header igual que la home
    html_parts.append('<div class="ubar"><div class="container"><span><span class="punto">\u25cf</span> PREPARACI\u00d3N CIVIL SIN ALARMISMO</span><span>/</span><span>HECHO PARA SITUACIONES REALES EN ESPA\u00d1A</span></div></div>')
    html_parts.append('<header class="site-header"><div class="container"><a href="/" class="logo">KIT<span class="accent">72H</span><span class="tagline">Diario de supervivencia</span></a><nav><a href="/#plan">El plan</a><a href="/#kits">Kits</a><a href="/blog/">Blog</a><a class="btn negro" href="https://www.amazon.es/s?k=kit+emergencia+72+horas&amp;tag=nti0c8-21" target="_blank" rel="sponsored nofollow noopener">Compra tu kit \u2192</a></nav></div></header>')
    html_parts.append('<main class="container">')
    html_parts.append('  <section class="sec oscura">')
    html_parts.append('    <div class="container">')
    html_parts.append('      <div class="watermark" aria-hidden="true">BLOG</div>')
    html_parts.append('      <div class="sec-inner">')
    html_parts.append('        <span class="sec-label">Blog</span>')
    html_parts.append('        <h2>Todas las guías</h2>')
    html_parts.append('        <p class="sec-intro">' + desc + '</p>')
    html_parts.append('        <div class="grid-kits">')
    html_parts.append(cards_block)
    html_parts.append('      </div>')
    html_parts.append('      </div>')
    html_parts.append('    </div>')
    html_parts.append('  </section>')
    html_parts.append('</main>')
    html_parts.append('</body></html>')

    return '\n'.join(html_parts)


def generate_home_blog_section(new_data, num_shown=9):
    """Genera el bloque BLOG para la home con los últimos N blogs."""
    entries = new_data['entradas'][:num_shown]
    total = len(new_data['entradas'])

    cards_html = []
    for i, entry in enumerate(entries, 1):
        cards_html.append(build_card_html(entry, i))

    cards_block = '\n'.join(cards_html)

    parts = []
    parts.append('        <div class="home-blog">')
    parts.append('          <div class="sec-label">04 / Blog</div>')
    parts.append('          <h2>Del diario<br><span class="acento">de supervivencia</span></h2>')
    parts.append('          <div class="grid-kits">')
    parts.append(cards_block)
    parts.append('          </div>')
    parts.append('          <p><a class="btn negro" href="/blog/">Todas las guías (' + str(total) + ' \u2192)</a></p>')
    parts.append('        </div>')

    return '\n'.join(parts)


def main():
    parser = argparse.ArgumentParser(description='Genera blog/index.html e index.html desde blog.json')
    parser.add_argument('repo_path', nargs='?', default=None)
    args = parser.parse_args()

    if args.repo_path:
        repo_path = os.path.abspath(args.repo_path)
    else:
        repo_path = os.getcwd()
        search = Path(repo_path)
        for parent in [search] + list(search.parents):
            if (parent / 'data' / 'blog.json').exists():
                repo_path = str(parent)
                break
        else:
            print("ERROR: no se encontró el repo kit72h", file=sys.stderr)
            sys.exit(1)

    print("Repo: " + repo_path)

    data_path = os.path.join(repo_path, 'data')
    blog_path = os.path.join(repo_path, 'blog')

    # 1. Escanear
    print("Escaneando directorios de blog...")
    scanned = scan_blog_dir(blog_path)
    print("  " + str(len(scanned)) + " directorios de blog encontrados")

    # 2. Cargar blog.json existente
    existing = load_existing_blog_data(data_path)
    if existing:
        print("  blog.json existente: " + str(len(existing['entries'])) + " entradas")
    else:
        print("  No se encontró blog.json (se creará)")

    # 3. Construir lista
    print("Sincronizando datos...")
    new_data = build_new_blog_entries(data_path, scanned, existing)
    print("  " + str(len(new_data['entradas'])) + " entradas totales")

    if existing:
        old_slugs = set(existing['entries'].keys())
        new_slugs = set(e['slug'] for e in new_data['entradas'])
        added = new_slugs - old_slugs
        if added:
            print("  " + str(len(added)) + " blogs nuevos añadidos: " + ', '.join(sorted(added)[:5]) + "...")

    # 4. Actualizar blog.json
    blog_json_path = os.path.join(data_path, 'blog.json')
    with open(blog_json_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    print("  blog.json: " + str(len(new_data['entradas'])) + " entradas escritas")

    # 5. Generar blog/index.html
    print("Generando blog/index.html...")
    index_path = os.path.join(repo_path, 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        home_html = f.read()

    css_match = re.search(r'styles\.css\?v=(\S+)', home_html)
    css_version = css_match.group(1).rstrip("'>\"\'\\") if css_match else '20261001c'

    blog_index_html = generate_blog_index(new_data, css_version)
    blog_index_path = os.path.join(blog_path, 'index.html')
    with open(blog_index_path, 'w', encoding='utf-8') as f:
        f.write(blog_index_html)
    print("  blog/index.html escrito (" + str(len(blog_index_html)) + " chars, " + str(len(new_data['entradas'])) + " tarjetas)")

    # 6. Actualizar home (index.html) - reemplazar el bloque BLOG
    print("Actualizando index.html (home)...")
    home_blog_section = generate_home_blog_section(new_data, num_shown=9)

    # Buscar el bloque blog en la home (por id="lecturas" o "Del diario")
    idx = home_html.find('id="lecturas"')
    if idx < 0:
        idx = home_html.find('Del diario')
    if idx >= 0:
        section_start = home_html.rfind('<section', 0, idx)
        section_end = home_html.find('</section>', idx)
        if section_end > 0:
            section_end += 10  # include </section>
            full_section = '  <section class="sec clara" id="lecturas">\n' + home_blog_section + '\n  </section>'
            home_html = home_html[:section_start] + full_section + home_html[section_end:]
            print("  index.html actualizado")
        else:
            print("  WARNING: no se encontró </section> para blog-home")
    else:
        print("  WARNING: no se encontró id='lecturas' ni 'Del diario' en index.html")

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(home_html)

    # 7. Summary
    print("")
    print("Resumen:")
    print("  - " + str(len(new_data['entradas'])) + " blogs sincronizados")
    print("  - blog/index.html generado con TODOS los posts")
    print("  - index.html actualizado con los últimos 9")
    print("  - CSS version: " + css_version)

    version_part = css_version.split('v=')[1] if 'v=' in css_version else css_version
    new_version = version_part + 'b'
    print("")
    print("ACTIVAR: cambiar styles.css?v=" + css_version + " a styles.css?v=" + new_version + " en TODOS los HTML del repo")


if __name__ == '__main__':
    main()