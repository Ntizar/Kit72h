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

PRESUPUESTO DE TIEMPO (arreglo 2026-10-12): el job llevaba desde el 07-10 en `error`
porque runner-kit72h.py corta a 900s y buscar-amazon.py tardaba más en el VM (1 vCPU):
se rascaban 12 fichas y, como guardaba todo al final del bucle, se perdía el trabajo
entero — todas las noches. Ahora el buscador recibe --max-segundos 540 y guarda item
a item: corta limpio, imprime cuánto lleva, y lo que falte entra en la noche siguiente.
"""
import os
import subprocess
import sys
from pathlib import Path

REPO = Path.home() / "Projects" / "kit72h"   # sin ruta personal en el repo
PY = sys.executable
os.environ.setdefault("ARNES_EXENTO", "1")  # arnés git: el cron empuja a main por diseño (exención auditable)

IDENT = ["-c", "user.name=Mastermind", "-c", "user.email=bot@kit72h.local"]

# ficheros de datos que justifican el commit
DATOS = ("kits.json", "propuestas-fichas", "buscador-log")
# todo lo que se regenera a partir de los datos (debe entrar en el mismo commit)
GENERADO = ("data/kits.json", "data/propuestas-fichas.json", "data/buscador-log.json",
            "index.html", "sitemap.xml", "feed.xml", "llms.txt", "llms-full.txt",
            "kit", "blog", "fuentes", "zona")


def run(*args, timeout=900):
    """Nunca muere por timeout: buscar-amazon.py guarda item a item, así que un corte
    deja trabajo VÁLIDO en disco que hay que commitear igualmente (si no, cada noche
    se rascaba Amazon para nada → cron kit72h-buscador en `error` desde 2026-10-07)."""
    try:
        return subprocess.run(args, cwd=REPO, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        salida = e.stdout if isinstance(e.stdout, str) else (e.stdout or b"").decode("utf-8", "replace")
        print(f"⚠️ timeout de {timeout}s en {' '.join(str(a) for a in args[:2])}")
        return subprocess.CompletedProcess(args, 1, salida, "timeout")


def git(*args, timeout=300):
    return run("git", *args, timeout=timeout)

out = None
if os.environ.get("KIT72H_SKIP_BUSCAR") == "1":
    print("(buscador de Amazon saltado: KIT72H_SKIP_BUSCAR=1)")
else:
    # Presupuesto de 540s: deja margen para generar-seo + prerender + commit dentro
    # del corte de 900s de runner-kit72h.py, que era el que mataba el job.
    # Lo que no entre hoy entra mañana (rotación + guardado incremental).
    out = run(PY, "scripts/buscar-amazon.py", "--cupo", "12", "--max-segundos", "540")
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
    # GATE: sin prerender NO se pushea. La REGLA DE ORO de arriba dice que datos y
    # HTML salen del mismo run; commitear solo los datos deja la web a medias y el
    # audit de las 06:00 salta con "prerender desactualizado". Mejor un error honesto
    # (el cron lo canta) que un deploy silenciosamente viejo.
    print("❌ prerender.py falló → NO se commitea ni se pushea: " + " | ".join(cola))
    sys.exit(1)

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
