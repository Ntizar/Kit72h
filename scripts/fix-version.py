#!/usr/bin/env python3
"""Corregir bump doble: 20261025cbb → 20261025cb."""
from pathlib import Path

RAIZ = Path('/home/nan/Projects/kit72h').resolve()
EXCLUIR = {'pintout', 'sketches', 'busquedas', 'videos', '.git'}

reemplazos = [
    ('styles.css?v=20261025cbb', 'styles.css?v=20261025cb'),
    ('ui.js?v=20261025cbb', 'ui.js?v=20261025cb'),
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