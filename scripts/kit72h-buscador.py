# -*- coding: utf-8 -*-
"""Cron nocturno Kit72h: resolver fichas de Amazon pendientes + regenerar SEO y
prerender + commit/push. Script puro (sin LLM). Imprime resumen para Telegram;
si no hay nada nuevo, una linea de silencio informativo.

REGLA DE ORO (por que existe este orden): el HTML prerenderizado de kit/ blog/
fuentes/ e index.html debe salir del MISMO run que data/kits.json. Si se
commitean datos sin regenerar, la web estatica queda desfasada y la auditoria
diaria (kit72h-seo-audit) salta con "prerender desactualizado" — justo lo que
paso el 2026-09-29: el buscador toco kits.json a las 05:17 y el audit de las
06:00 cazo 50 paginas viejas.
"""
import os
import subprocess
import sys
from pathlib import Path

REPO = Path.home() / "Projects" / "kit72h"   # sin ruta personal en el repo
PY = sys.executable
IDENT = ["-c", "user.name=Mastermind", "-c", "user.email=david.antizar@mastermind.local"]

# ficheros de datos que justifican el commit
DATOS = ("kits.json", "propuestas-fichas", "buscador-log")
# todo lo que se regenera a partir de los datos (debe entrar en el mismo commit)
GENERADO = ("data/kits.json", "data/propuestas-fichas.json", "data/buscador-log.json",
            "index.html", "sitemap.xml", "feed.xml", "llms.txt", "llms-full.txt",
            "kit", "blog", "fuentes", "zona")


def run(*args, timeout=900):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True, timeout=timeout)


def git(*args, timeout=300):
    return run("git", *args, timeout=timeout)

out = None
if os.environ.get("KIT72H_SKIP_BUSCAR") == "1":
    print("(buscador de Amazon saltado: KIT72H_SKIP_BUSCAR=1)")
else:
    out = run(PY, "scripts/buscar-amazon.py", "--cupo", "12")
if out is not None:
    print(out.stdout[-2500:] if out.stdout else "")
    if out.returncode != 0 and out.stderr:
        print(f"⚠️ buscar-amazon.py falló (exit {out.returncode})")

# commit solo si hay cambios
status = git("status", "--porcelain")
cambios = [l for l in status.stdout.splitlines() if any(f in l for f in DATOS)]
if not cambios:
    print("(sin cambios que commitear)")
    sys.exit(0)

# 1) Regenerar SEO + prerender ANTES de commitear (mismo run = misma foto)
seo = run(PY, "scripts/generar-seo.py")
if seo.returncode != 0:
    print(f"⚠️ generar-seo.py falló (exit {seo.returncode}): {(seo.stderr or '').strip()[:200]}")

pre = run(PY, "scripts/prerender.py")
if pre.returncode != 0:
    cola = [l for l in (pre.stdout or "").splitlines() if l.strip()][-3:]
    print("⚠️ prerender.py falló, la web estática queda desfasada: " + " | ".join(cola))

# 2) Commit con datos + generado
for f in GENERADO:
    if (REPO / f).exists():
        git("add", f)

commit = git(*IDENT, "commit", "-q", "-m",
             "Buscador nocturno: fichas Amazon verificadas + prerender regenerado")
if commit.returncode != 0:
    print(f"⚠️ commit falló (exit {commit.returncode}): {(commit.stderr or '').strip()[:200]}")
    sys.exit(0)

# 3) Push con rebase (otro cron pudo adelantar un commit)
git("pull", "--rebase", "-q", "origin", "main")
push = git("push", "-q", "origin", "main")
if push.returncode != 0:
    print(f"⚠️ push falló (exit {push.returncode}): {(push.stderr or '').strip()[:200]}")
else:
    estado = "prerender OK" if pre.returncode == 0 else "prerender con fallos ⚠️"
    print(f"🚀 push hecho (Pages se despliega solo) — {estado}")
