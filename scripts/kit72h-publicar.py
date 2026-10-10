#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — publicador de la entrada encolada por el consejero.

Lo ejecuta el cron `kit72h-publicador` (modo script, --no-agent) en el VM. Lee
`notes/plan-crecimiento/_entrada.json` (que escribe el consejero LLM a las
07:30) y la publica: upsert en blog.json, materializa el directorio, regenera
home+SEO, hornea con Playwright y pasa el gate. Si el gate falla NO commitea.

Es idempotente: si ya existe la marca `.publicado-<slug>`, no repite nada.
Salida: 1-5 líneas para el deliver del cron; VACÍO si no hay nada que publicar.
"""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PLAN = REPO / "notes" / "plan-crecimiento"
ENTRADA = PLAN / "_entrada.json"
IDENT = ["-c", "user.name=Mastermind", "-c", "user.email=bot@kit72h.local"]
# SOLO estos paths: nunca `git add -A` (arrastraría cambios ajenos del árbol).
# OJO: incluir TODO lo que reescribe el horneado (kit/fuentes/zona/index/sitemap…)
# o el árbol queda sucio y el `git pull --rebase` de la cadena siguiente falla.
PATHS = ["data/blog.json", "blog", "kit", "fuentes", "zona", "index.html",
         "sitemap.xml", "feed.xml", "llms.txt", "llms-full.txt",
         "notes/plan-crecimiento", "notes/mapa-keywords.md"]


def git(*args, timeout=300):
    return subprocess.run(["git", "-C", str(REPO)] + list(args),
                          capture_output=True, text=True, timeout=timeout)


def main():
    if not ENTRADA.exists():
        return 0  # nada encolado: silencio
    try:
        slug = json.loads(ENTRADA.read_text(encoding="utf-8")).get("slug", "")
    except Exception as ex:
        print("publicador: _entrada.json ilegible (%s)" % ex)
        return 1
    if not slug:
        print("publicador: _entrada.json sin slug")
        return 1

    marca = PLAN / (".publicado-" + slug)
    if marca.exists():
        ENTRADA.unlink(missing_ok=True)
        return 0  # ya publicado: silencio

    sys.path.insert(0, str(REPO / "scripts"))
    import importlib
    consejero = importlib.import_module("kit72h-consejero")  # noqa

    rc = consejero.publicar(str(ENTRADA))
    if rc != 0:
        print("❌ Publicador: la publicación de «%s» FALLÓ (ver arriba). NO se commitea." % slug)
        return 1

    marca.write_text("publicado\n", encoding="utf-8")  # antes del add: entra en el commit
    git("add", *PATHS)
    st = git("status", "--porcelain")
    if not st.stdout.strip():
        print("Publicador: «%s» ya estaba en el árbol (sin cambios que commitear)." % slug)
        return 0

    c = git(*IDENT, "commit", "-m", "consejero: publicar «%s» (blog)" % slug)
    if c.returncode != 0:
        print("❌ commit falló: %s" % (c.stderr or c.stdout).strip()[:200])
        return 1
    git("pull", "--rebase", "-q", "origin", "main")
    push = git("push", "-q", "origin", "main")
    if push.returncode != 0:
        print("❌ push falló: %s" % (push.stderr or "").strip()[:200])
        return 1

    ix = subprocess.run(["python3", "scripts/indexnow.py", "--desde-git", "HEAD~1"],
                        cwd=REPO, capture_output=True, text=True, timeout=90)
    nota_ix = (ix.stdout.strip().splitlines() or [""])[-1][:80]
    marca.write_text("publicado\n", encoding="utf-8")
    print("🚀 Publicado /blog/%s/ · gate ✔ · push ✔%s"
          % (slug, (" · " + nota_ix) if nota_ix else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
