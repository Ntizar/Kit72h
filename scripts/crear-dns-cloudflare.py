#!/usr/bin/env python3
"""Kit72h — crear registros DNS en Cloudflare para apuntar kit72h.com a GitHub Pages.
Idempotente: salta los registros que ya existen. Token leído del .env de Hermes.
Sin dependencias: solo stdlib. Uso:  python scripts/crear-dns-cloudflare.py
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

DOMINIO = "kit72h.com"
GIT_USER = "ntizar"

A4 = ["185.199.108.153", "185.199.109.153", "185.199.110.153", "185.199.111.153"]
A6 = ["2606:50c0:8000::153", "2606:50c0:8001::153",
      "2606:50c0:8002::153", "2606:50c0:8003::153"]  # api.github.com/meta, verificado 2026-09-28


def _envs():
    """Dónde buscar el token: .env del repo, .env de Hermes (Linux) y el de Windows."""
    rutas = [Path(__file__).resolve().parents[1] / ".env", Path.home() / ".hermes" / ".env"]
    localappdata = os.environ.get("LOCALAPPDATA")
    if localappdata:
        rutas.append(Path(localappdata) / "hermes" / ".env")
    return rutas


def token():
    directo = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if directo:
        return directo
    for ruta in _envs():
        if not ruta.is_file():
            continue
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if linea.startswith("CLOUDFLARE_API_TOKEN="):
                valor = linea.split("=", 1)[1].strip().strip("\"'").strip()
                if valor:
                    return valor
    sys.exit("CLOUDFLARE_API_TOKEN no encontrado: expórtalo o ponlo en el .env del repo")



def api(metodo, ruta, datos=None):
    peticion = urllib.request.Request(
        "https://api.cloudflare.com/client/v4" + ruta,
        data=json.dumps(datos).encode() if datos else None,
        headers={"Authorization": "Bearer " + token(),
                 "Content-Type": "application/json"},
        method=metodo)
    with urllib.request.urlopen(peticion, timeout=30) as r:
        return json.load(r)


def main():
    zonas = api("GET", f"/zones?name={DOMINIO}")["result"]
    if not zonas:
        sys.exit(f"La zona {DOMINIO} no es visible con este token")
    zona = zonas[0]["id"]
    print(f"zona {DOMINIO}: {zona}")

    existentes = {
        (r["type"], r["name"].rstrip("."))
        for r in api("GET", f"/zones/{zona}/dns_records?per_page=100")["result"]
    }

    deseados = ([{"type": "A", "name": "@", "content": ip} for ip in A4]
                + [{"type": "AAAA", "name": "@", "content": ip} for ip in A6]
                + [{"type": "CNAME", "name": "www",
                    "content": f"{GIT_USER}.github.io"}])

    for d in deseados:
        nombre_full = DOMINIO if d["name"] == "@" else f"{d['name']}.{DOMINIO}"
        if (d["type"], nombre_full) in existentes:
            print(f"ya existe: {d['type']} {nombre_full}")
            continue
        r = api("POST", f"/zones/{zona}/dns_records", {**d, "ttl": 1, "proxied": False})
        estado = "creado" if r.get("success") else f"ERROR {r.get('errors')}"
        print(f"{estado}: {d['type']} {nombre_full} -> {d['content']}")

    print("\nSiguiente paso: esperar propagación (~10 min) y activar 'Enforce HTTPS'"
          " en Pages (repos/Ntizar/Kit72h/pages) + modo SSL/TLS Full en la zona.")


if __name__ == "__main__":
    main()
