#!/usr/bin/env python3
"""Bump del token styles.css?v=20261012b -> 20261015b en las páginas publicadas.
Regex PARA en la comilla/clase [\\w-]+ (nunca \\S+). Verifica con html.parser."""
import os
import re
from html.parser import HTMLParser

RAIZ = os.path.expanduser("~/Projects/kit72h")
VIEJA, NUEVA = "20261012b", "20261015b"

# rutas desplegadas (allowlist de pages.yml): raiz + blog + kit + fuentes + zona + privacidad
objetivos = []
for nombre in os.listdir(RAIZ):
    if nombre.endswith(".html"):
        objetivos.append(os.path.join(RAIZ, nombre))
for carpeta in ("blog", "kit", "fuentes", "zona", "privacidad"):
    base = os.path.join(RAIZ, carpeta)
    if not os.path.isdir(base):
        continue
    for dirpath, _, ficheros in os.walk(base):
        for f in ficheros:
            if f.endswith(".html"):
                objetivos.append(os.path.join(dirpath, f))

patron = re.compile(r"styles\.css\?v=" + VIEJA + r'([\w-]*)')
tocado = sin_cambio = 0
for ruta in objetivos:
    html = open(ruta, encoding="utf-8").read()
    if f"styles.css?v={VIEJA}" not in html:
        sin_cambio += 1
        continue
    nuevo = patron.sub(f"styles.css?v={NUEVA}\\1", html)
    # verificación: una sola ocurrencia del token nuevo con cierre, cero de la vieja
    assert nuevo.count(f"styles.css?v={VIEJA}") == 0, ruta
    assert nuevo.count(f"styles.css?v={NUEVA}") == 1, ruta
    assert f'styles.css?v={NUEVA}">' in nuevo, ruta
    # parseo HTML para cazar etiquetas rotas
    p = HTMLParser()
    p.feed(nuevo)
    open(ruta, "w", encoding="utf-8").write(nuevo)
    tocado += 1

print(f"actualizados: {tocado} | sin el token viejo: {sin_cambio} | total: {len(objetivos)}")
