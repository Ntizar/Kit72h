# -*- coding: utf-8 -*-
"""Cron nocturno Kit72h: resolver fichas de Amazon pendientes + commit/push.
Script puro (sin LLM). Imprime resumen para Telegram; si no hay nada nuevo,
no imprime -> silencio (el vigilante ya informa por su cuenta)."""
import subprocess, sys
from pathlib import Path

REPO = Path(r"C:/Users/d_ant/Projects/kit72h")
PY = sys.executable

def run(*args, timeout=900):
    r = subprocess.run(args, cwd=REPO, capture_output=True, text=True, timeout=timeout)
    return r.stdout + r.stderr

out = run(PY, "scripts/buscar-amazon.py", "--cupo", "12")
print(out[-2500:])

# commit solo si hay cambios
status = run("git", "status", "--porcelain")
cambios = [l for l in status.splitlines() if any(f in l for f in ("kits.json", "propuestas-fichas", "buscador-log", "productos-pendientes"))]
if cambios:
    run("git", "add", "data/kits.json", "data/propuestas-fichas.json", "data/buscador-log.json", "data/productos-pendientes.xlsx")
    msg = "Buscador nocturno: fichas Amazon verificadas y aplicadas"
    run("git", "-c", "user.name=Mastermind", "-c", "user.email=david.antizar@mastermind.local", "commit", "-q", "-m", msg)
    if run("git", "push", "-q") and "error" in run("git", "push", "-q").lower():
        print("⚠️ push falló — revisar manual")
    else:
        print("🚀 push hecho (Pages se despliega solo)")
else:
    print("(sin cambios que commitear)")

# wrapper del cron kit72h-buscador (se ejecuta desde ~/AppData/Local/hermes/scripts/)
