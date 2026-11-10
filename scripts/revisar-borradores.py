#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate editorial de los borradores de Kit72h.

Uso:
    python3 scripts/revisar-borradores.py --estricto

Comprueba que los borradores que se van a publicar tengan cuerpo suficiente,
fuentes con URL y ninguna de las afirmaciones retiradas en la auditoría del
2026-11-10. No sustituye la revisión humana: evita que vuelvan los errores ya
detectados.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PLAN = RAIZ / "notes" / "plan-crecimiento"

BORRADORES = {
    "montana-kit-salvavidas": PLAN / "_entrada-revamp-montana-kit-salvavidas.json",
    "alimentos-emergencia-caducidad-rotacion": PLAN / "_entrada-revamp-alimentos-2026-10-23.json",
}

# Afirmaciones que la auditoría retiró por no ser defendibles o por ser peligrosas.
PROHIBIDAS = {
    r"25\s*veces": "multiplicador de pérdida de calor sin fuente",
    r"4\s*veces": "multiplicador de pérdida de calor sin fuente",
    r"Loratadina": "medicamento para anafilaxia sin indicación médica",
    r"20\s*[-–]\s*30\s*años": "vida útil de arroz sin condiciones de envasado",
    r"3\s*[-–]\s*5\s*años\s*más": "extensión genérica de caducidad",
    r"serviciosmeteorologol": "URL rota de AEMET",
    r"infinita": "caducidad infinita sin matices",
    r"cocoyata": "error tipográfico",
}


def revisar(slug: str, ruta: Path) -> list[str]:
    errores: list[str] = []
    if not ruta.exists():
        return [f"{slug}: falta {ruta.name}"]
    try:
        entrada = json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as ex:
        return [f"{slug}: JSON inválido: {ex}"]

    cuerpo = entrada.get("cuerpo") or ""
    texto = re.sub(r"<[^>]+>", " ", cuerpo)
    palabras = len(texto.split())
    if palabras < 1200:
        errores.append(f"{slug}: solo {palabras} palabras (mínimo 1200)")
    if "<h2>" not in cuerpo or "<p>" not in cuerpo:
        errores.append(f"{slug}: falta estructura <h2>/<p>")

    fuentes = entrada.get("fuente") or []
    validas = [f for f in fuentes if isinstance(f, dict) and f.get("url", "").startswith("https://")]
    if len(validas) < 4:
        errores.append(f"{slug}: {len(validas)} fuentes https (mínimo 4)")

    for patron, motivo in PROHIBIDAS.items():
        if re.search(patron, texto, flags=re.IGNORECASE):
            errores.append(f"{slug}: afirmación prohibida «{patron}» ({motivo})")
    return errores


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--estricto", action="store_true", help="falla ante cualquier error")
    args = parser.parse_args()
    errores: list[str] = []
    for slug, ruta in BORRADORES.items():
        errores.extend(revisar(slug, ruta))
        if ruta.exists():
            e = json.loads(ruta.read_text(encoding="utf-8"))
            print(f"· {slug}: {len(e.get('fuente', []))} fuentes · {len(re.sub(r'<[^>]+>', ' ', e.get('cuerpo', '')).split())} palabras")
    if errores:
        print("\n❌ Gate editorial:")
        for e in errores:
            print(" -", e)
        return 1 if args.estricto else 0
    print("✅ Borradores con fuentes y sin afirmaciones retiradas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
