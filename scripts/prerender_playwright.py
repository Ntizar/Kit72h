#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — horneado con Playwright (alternativa al CLI de Chrome).

Motivo: en el VM de NaN el CLI de Chrome (`--dump-dom`) se CUELGA sin devolver
nada, incluso en una página trivial → `scripts/prerender.py` acumula un FALLO de
90 s por página y deja chromes huérfanos. Playwright, en cambio, hornea la home
en ~8 s.

Reutiliza `scripts/prerender.py` ENTERO (rutas, inyección de metadatos, JSON-LD,
marcadores) y solo cambia cómo obtiene el DOM: Playwright navega y devuelve
`page.content()`. Todas las rutas son relativas al propio script, así que
funciona igual en el repo canónico y en una copia.

Uso (requiere playwright; en el VM vive en ~/.mastermind/venv):
    ~/.mastermind/venv/bin/python scripts/prerender_playwright.py
"""
import os
import sys
from pathlib import Path

# libs de Chrome (libatk, etc.) que no están en el sistema: sin esto el
# chromium de Playwright arranca con exitCode=127 (libatk-1.0.so.0 missing).
_libs = f"{Path.home()}/.chrome-libs"
_extra = f"{_libs}/usr/lib/x86_64-linux-gnu:{_libs}/lib/x86_64-linux-gnu"
_actual = os.environ.get("LD_LIBRARY_PATH", "")
if _extra not in _actual:
    os.environ["LD_LIBRARY_PATH"] = f"{_extra}:{_actual}" if _actual else _extra

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prerender as P  # noqa: E402

try:
    from playwright.sync_api import sync_playwright  # noqa: E402
except ImportError:
    sys.stderr.write("FALTA playwright: instala con 'uv pip install playwright && playwright install chromium'\n")
    raise SystemExit(3)

_ctx = {"pw": None, "browser": None, "page": None}


def dump_pw(chrome, url, marca_esperada, timeout=45000):
    """Igual que P.dump pero con Playwright: 3 intentos hasta ver la marca."""
    html = ""
    for intento in range(3):
        try:
            _ctx["page"].goto(url, wait_until="domcontentloaded", timeout=timeout)
            _ctx["page"].wait_for_timeout(4500)
            html = _ctx["page"].content()
        except Exception as ex:
            print("    retry %d %s: %s" % (intento, url, ex), flush=True)
        if marca_esperada in html:
            break
    if "<title>" not in html or 'id="app"' not in html:
        raise AssertionError("dump vacío: %s" % url)
    return html


def main():
    P.encontrar_chrome = lambda: "playwright"   # main() no usará el CLI
    P.dump = dump_pw

    _ctx["pw"] = sync_playwright().start()
    _ctx["browser"] = _ctx["pw"].chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    _ctx["page"] = _ctx["browser"].new_page(viewport={"width": 1366, "height": 900})
    code = 0
    try:
        P.main()
    except SystemExit as e:
        code = int(e.code or 0)
    finally:
        try:
            _ctx["browser"].close()
            _ctx["pw"].stop()
        except Exception:
            pass
    sys.exit(code)


if __name__ == "__main__":
    main()
