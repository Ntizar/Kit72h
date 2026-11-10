#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación de producción de Kit72h (sin navegador, sin tokens).

Comprueba que las dos entradas recuperadas sirven el contenido corregido y que
la instantánea pública de precios es de hoy. Sale con código 1 si algo falla.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen

PAGINAS = {
    "https://kit72h.com/blog/montana-kit-salvavidas/": "15 artículos que de verdad importan",
    "https://kit72h.com/blog/alimentos-emergencia-caducidad-rotacion/": "qué comer, cuánto guardar",
}
PRECIOS = "https://kit72h.com/data/precios.json"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131 Safari/537.36"


def get(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
    with urlopen(req, timeout=30) as r:
        return r.read()


def texto(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def main() -> int:
    fallos: list[str] = []
    for url, esperado in PAGINAS.items():
        try:
            html = get(url + "?v=" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")).decode("utf-8", "replace")
            palabras = len(texto(html).split())
            if esperado not in html:
                fallos.append(f"{url}: falta «{esperado}»")
            if palabras < 1200:
                fallos.append(f"{url}: solo {palabras} palabras")
            print(f"✅ {url} · {palabras} palabras")
        except Exception as ex:  # noqa: BLE001
            fallos.append(f"{url}: {ex}")

    try:
        datos = json.loads(get(PRECIOS + "?v=" + str(int(datetime.now().timestamp()))))
        hoy = datetime.now(timezone.utc).date().isoformat()
        actualizado = (datos.get("meta") or {}).get("actualizado", "")
        if not actualizado.startswith(hoy):
            fallos.append(f"precios: instantánea {actualizado!r}, no de hoy ({hoy})")
        ofertas = datos.get("ofertas") or []
        if not ofertas:
            fallos.append("precios: no hay ninguna selección con stock")
        else:
            print(f"✅ precios · {actualizado} · {len(datos.get('productos', {}))} productos · "
                  f"selección: {ofertas[0].get('producto')}")
    except Exception as ex:  # noqa: BLE001
        fallos.append(f"precios: {ex}")

    if fallos:
        print("\n❌ Producción:")
        for f in fallos:
            print(" -", f)
        return 1
    print("\n✅ Producción verificada")
    return 0


if __name__ == "__main__":
    sys.exit(main())
