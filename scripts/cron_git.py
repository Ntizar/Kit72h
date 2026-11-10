# -*- coding: utf-8 -*-
"""Contrato de staging para los crons de Kit72h.

El runner solo puede commitear las salidas declaradas por el script que acaba
de ejecutar. Un script desconocido NO se commitea: sus cambios quedan visibles
en `git status` para revisión humana.

Regla de la auditoría 2026-11-10: nunca `git add -A` en un cron.
"""
from __future__ import annotations

from pathlib import Path

# Pathspecs relativos a la raíz del repo. `:(glob)` permite comodines de Git.
PATHS_POR_SCRIPT: dict[str, tuple[str, ...]] = {
    "noticias.py": ("data/noticias.json", "data/alertas-es.json"),
    "kit72h-analiticas.py": ("data/analiticas.json",),
    # instrumentar toca HTML de páginas; excluye pintout/sketches/analiticas
    "instrumentar-analitica.py": (
        ":(glob)**/*.html",
        ":(exclude,glob)pintout/**",
        ":(exclude,glob)sketches/**",
        ":(exclude,glob)analiticas/**",
    ),
    "generar-seo.py": (
        "index.html", "sitemap.xml", "feed.xml", "llms.txt", "llms-full.txt",
    ),
    "prerender.py": ("index.html", "blog", "kit", "fuentes", "zona", "404.html"),
    "kit72h-seo-ctr.py": (
        "index.html", ":(glob)**/*.html",
        ":(exclude,glob)pintout/**", ":(exclude,glob)sketches/**",
        ":(exclude,glob)analiticas/**",
    ),
    "catalogo.py": ("data/kits.json", "data/catalogo.json"),
    "comprobar-urls.py": ("data/urls-estado.json",),
}


def paths_for(nombre: str) -> tuple[str, ...] | None:
    """Devuelve los paths declarados para un script, o None si no está mapeado."""
    return PATHS_POR_SCRIPT.get(Path(nombre).name)


def existentes(repo: Path, paths: tuple[str, ...]) -> list[str]:
    """Filtra paths literales que no existen; conserva pathspecs con comodines."""
    salida = []
    for p in paths:
        if p.startswith(":(") or any(c in p for c in "*?["):
            salida.append(p)
        elif (repo / p).exists():
            salida.append(p)
    return salida
