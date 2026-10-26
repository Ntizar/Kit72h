#!/usr/bin/env python3
"""Bump versión CSS y JS en TODOS los HTML del repo (solo páginas publicadas)."""
from pathlib import Path

RAIZ = Path('/home/nan/Projects/kit72h').resolve()
EXCLUIR = {'pintout', 'sketches', 'busquedas', 'videos', '.git'}

reemplazos = [
    ('styles.css?v=20261025c', 'styles.css?v=20261025cb'),
    ('ui.js?v=20261025c', 'ui.js?v=20261025cb'),
    ('main.js?v=20261008a', 'main.js?v=20261008b'),
]

modificados = 0
for html_file in RAIZ.glob('**/*.html'):
    partes = html_file.parts
    if any(p in EXCLUIR for p in partes):
        continue
    
    contenido = html_file.read_text(encoding='utf-8')
    nuevo = contenido
    for viejo, nuevo_ver in reemplazos:
        nuevo = nuevo.replace(viejo, nuevo_ver)
    
    if nuevo != contenido:
        html_file.write_text(nuevo, encoding='utf-8')
        modificados += 1
        print(f'  {html_file.relative_to(RAIZ)}')

print(f'\nTotal ficheros modificados: {modificados}')