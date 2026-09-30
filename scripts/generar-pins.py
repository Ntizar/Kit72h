#!/usr/bin/env python3
"""Generador de pines para Pinterest desde los artículos de Kit72h.
Crea imágenes planas estilo editorial (Aurora 7) con título + logo Kit72h.
Formato: 1000x1500px (ratio 2:3, ideal para Pinterest)."""

import os
import html
import json
from datetime import datetime

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_DIR = os.path.join(PROJECT, 'blog')
PINTOUT_DIR = os.path.join(PROJECT, 'pintout')

os.makedirs(PINTOUT_DIR, exist_ok=True)


def extract_blog_title(content):
    """Extraer el título de un HTML de blog."""
    import re
    m = re.search(r'<title>([^<]+)</title>', content)
    if m:
        return html.unescape(m.group(1))
    return ""


def extract_meta_desc(content):
    """Extraer la meta descripción de un blog."""
    import re
    m = re.search(r'<meta name="description" content="([^"]+)"', content)
    if m:
        return html.unescape(m.group(1))
    return ""


def generate_pin_html(title, desc, slug, pin_id):
    """Generar el HTML de un pin estilo Aurora 7."""
    # Colores Aurora 7
    colores = [
        ("#D14B27", "#F1EBDF"),  # Rojo sobre crema
        ("#EFA02B", "#F1EBDF"),  # Ámbar sobre crema
        ("#26201A", "#F1EBDF"),  # Negro sobre crema
        ("#D14B27", "#FFFFFF"),  # Rojo sobre blanco
        ("#EFA02B", "#0E0C09"),  # Ámbar sobre negro
    ]
    bg, fg = colores[pin_id % len(colores)]
    
    # Fragmento del título (max 60 chars para que quepa)
    title_short = title[:55]
    if len(title) > 55:
        title_short += "…"
    
    # Fragmento de descripción (max 80 chars)
    desc_short = desc[:75] if desc else ""
    
    pin_html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Pin {pin_id} — Kit72h</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=IBM+Plex+Mono:wght@400;700&display=swap');
body {{
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1000px;
  height: 1500px;
  background: {bg};
  font-family: 'IBM Plex Mono', monospace;
}}
.container {{
  max-width: 800px;
  padding: 60px 40px;
  text-align: center;
  color: {fg};
}}
.logo {{
  font-family: 'Anton', sans-serif;
  font-size: 42px;
  letter-spacing: 3px;
  margin-bottom: 40px;
  text-transform: uppercase;
  border-bottom: 4px solid {fg};
  display: inline-block;
  padding-bottom: 8px;
}}
.logo .accent {{
  color: {'#EFA02B' if fg == '#F1EBDF' or fg == '#FFFFFF' else '#EFA02B'};
}}
.title {{
  font-family: 'Anton', sans-serif;
  font-size: 52px;
  line-height: 1.15;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 30px;
}}
.desc {{
  font-size: 22px;
  line-height: 1.6;
  opacity: 0.85;
  margin-bottom: 40px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}}
.cta {{
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 3px;
  text-transform: uppercase;
  border: 2px solid {fg};
  padding: 16px 32px;
  display: inline-block;
  opacity: 0.7;
}}
.pin-id {{
  position: absolute;
  bottom: 30px;
  right: 40px;
  font-size: 11px;
  opacity: 0.4;
  letter-spacing: 2px;
}}
</style>
</head>
<body>
<div class="container">
  <div class="logo">KIT<span class="accent">72H</span></div>
  <div class="title">{title_short}</div>
  <div class="desc">{desc_short}</div>
  <div class="cta">Leer artículo →</div>
</div>
<div class="pin-id">kit72h.com · pin-{pin_id}</div>
</body>
</html>'''
    return pin_html


if __name__ == "__main__":
    pins_created = []
    
    # Recorrer todos los artículos del blog
    for d in sorted(os.listdir(BLOG_DIR)):
        blog_path = os.path.join(BLOG_DIR, d)
        if not os.path.isdir(blog_path):
            continue
        
        index_path = os.path.join(blog_path, 'index.html')
        if not os.path.exists(index_path):
            continue
        
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title = extract_blog_title(content)
        desc = extract_meta_desc(content)
        
        if not title:
            continue
        
        # Generar 3 variantes de pin por artículo
        for variant in range(3):
            pin_html = generate_pin_html(title, desc, d, variant + 1)
            pin_filename = f'pin-{d}-{variant+1}.html'
            pin_path = os.path.join(PINTOUT_DIR, pin_filename)
            
            with open(pin_path, 'w', encoding='utf-8') as f:
                f.write(pin_html)
            
            pins_created.append({
                "blog": d,
                "title": title,
                "pin": pin_filename,
                "path": pin_path
            })
    
    # Guardar índice
    index_path = os.path.join(PINTOUT_DIR, 'indice.json')
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(pins_created, f, indent=2, ensure_ascii=False)
    
    print(f"✓ {len(pins_created)} pines generados en {PINTOUT_DIR}")
    print(f"  Índice: {index_path}")
    print("\nPara convertir a imágenes:")
    print("  1. Instalar: pip install playwright")
    print("  2. Ejecutar: python scripts/render-pins.py")
    print("  3. Subir los HTML/PNG a Pinterest")