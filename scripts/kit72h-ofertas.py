#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — ofertas: precios reales de Amazon y oferta del día (script puro, 0 tokens).

Este cron ANTES era un no-op con apariencia de funcionar: `obtener_precios_actualizados()`
devolvía el propio `precio_ref` del catálogo, así que el «cambio» era siempre 0 % y nunca
detectaba una oferta. Corría cada mañana, no fallaba y no producía nada.

Ahora delega en `scripts/precios-amazon.py` (Creators API oficial de Amazon):
- refresca `data/precios.json` con una instantánea atómica del día,
- elige una selección editorial por rebaja real, stock y precio final,
- la web la pinta en caliente desde `js/ui.js`, sin rehornear.

No hornea: el horneado nocturno (kit72h-buscador, 05:15) ya sale con este JSON.
Sólo commitea si los precios o la oferta cambian de verdad.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PY = sys.executable
os.environ.setdefault("ARNES_EXENTO", "1")  # arnés git: el cron empuja a main por diseño
IDENT = ["-c", "user.name=Mastermind", "-c", "user.email=bot@kit72h.local"]
JSON = "data/precios.json"
HIST = "data/precios-historico.json"


def run(*args, timeout=600):
    return subprocess.run(args, cwd=RAIZ, capture_output=True, text=True, timeout=timeout)


def huella(datos: dict) -> str:
    """Lo que importa de verdad: precios, oferta y recuentos. El timestamp
    `meta.actualizado` cambia en cada run y no debe generar commits por sí solo."""
    if not datos:
        return ""
    limpio = {
        "productos": {a: {k: v.get(k) for k in ("precio", "precio_antes", "ahorro_pct", "disponible")}
                      for a, v in (datos.get("productos") or {}).items()},
        "oferta_dia": datos.get("oferta_dia"),
        "meta": {k: v for k, v in (datos.get("meta") or {}).items() if k != "actualizado"},
    }
    return json.dumps(limpio, sort_keys=True, ensure_ascii=False)


def verificar_publicacion(actualizado: str | None, asin: str | None,
                          espera: int = 240) -> bool:
    """GitHub Pages tarda; no damos por bueno el push sin leer la URL pública."""
    if not actualizado:
        return False
    url = f"https://kit72h.com/data/precios.json?v={int(time.time())}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 kit72h-verificador",
        "Cache-Control": "no-cache",
    })
    limite = time.time() + espera
    while time.time() < limite:
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                publicado = json.loads(r.read().decode("utf-8"))
            if publicado.get("meta", {}).get("actualizado") == actualizado:
                oferta = publicado.get("oferta_dia") or {}
                if not asin or oferta.get("asin") == asin:
                    return True
        except Exception:
            pass
        time.sleep(15)
    return False


def main() -> int:
    r = run(PY, "scripts/precios-amazon.py")
    if r.stdout:
        print(r.stdout.strip()[-1200:])
    if r.returncode != 0:
        print(f"❌ precios-amazon.py falló (exit {r.returncode}) — no se commitea nada")
        print((r.stderr or "").strip()[-600:])
        return r.returncode

    try:
        nuevo = json.loads((RAIZ / JSON).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ {JSON} ilegible: {e}")
        return 1

    viejo = {}
    head = run("git", "show", f"HEAD:{JSON}", timeout=60)
    if head.returncode == 0:
        try:
            viejo = json.loads(head.stdout)
        except json.JSONDecodeError:
            viejo = {}

    if huella(nuevo) == huella(viejo):
        run("git", "checkout", "--", JSON, HIST)   # árbol limpio: no bloquear los rebase de otros crons
        print("precios: sin cambios reales (sin commit)")
        return 0

    add = run("git", "add", "--", JSON, HIST)
    if add.returncode != 0:
        print(f"❌ git add falló: {(add.stderr or '').strip()[:200]}")
        return 1

    od = nuevo.get("oferta_dia") or {}
    resumen = (f"{od.get('producto')} a {od.get('precio_texto')} (-{od.get('ahorro_pct')}%)"
               if od else "sin oferta destacada")
    commit = run("git", *IDENT, "commit", "-q", "-m",
                 f"chore(precios): precios de hoy en Amazon y seleccion del dia — {resumen}"[:200])
    if commit.returncode != 0:
        print(f"❌ commit falló: {(commit.stdout + commit.stderr).strip()[:300]}")
        return 1

    pull = run("git", "pull", "--rebase", "-q", "origin", "main")
    if pull.returncode != 0:
        print(f"❌ pull --rebase falló: {(pull.stderr or '').strip()[:300]}")
        return 1
    push = run("git", "push", "-q", "origin", "main", timeout=180)
    if push.returncode != 0:
        print(f"❌ push falló: {(push.stderr or '').strip()[:300]}")
        return 1

    asin = od.get("asin")
    if not verificar_publicacion(nuevo.get("meta", {}).get("actualizado"), asin):
        print("❌ push OK, pero la URL pública no sirve aún la instantánea nueva")
        return 1
    print(f"✅ precios y oferta publicados y verificados · {resumen}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
