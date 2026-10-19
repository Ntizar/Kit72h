#!/usr/bin/env python3
"""Kit72h — guardar el token de Cloudflare en el .env del repo, sin que pase por el chat.

Pide el token por consola con la entrada oculta (getpass), lo valida contra la API
(GET /user/tokens/verify) y solo entonces lo escribe en `.env`. Nunca imprime el valor.

Uso:  python3 scripts/guardar-token-cloudflare.py
Sin dependencias: solo stdlib.
"""
import getpass
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ENV = Path(__file__).resolve().parents[1] / ".env"
API = "https://api.cloudflare.com/client/v4"


def verificar(token):
    """Devuelve (ok, mensaje). No expone el token."""
    peticion = urllib.request.Request(
        API + "/user/tokens/verify",
        headers={"Authorization": f"Bearer {token}",
                 "User-Agent": "kit72h-token-check/1.0"},
    )
    try:
        with urllib.request.urlopen(peticion, timeout=20) as r:
            datos = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return False, f"la API respondió HTTP {e.code} (token inválido o sin permisos)"
    except Exception as e:  # red, DNS, timeout
        return False, f"no se pudo contactar con la API: {e}"
    estado = (datos.get("result") or {}).get("status")
    if datos.get("success") and estado == "active":
        return True, "token activo"
    return False, f"la API no lo da por activo (status={estado})"


def escribir(token):
    """Sustituye o añade CLOUDFLARE_API_TOKEN en el .env sin tocar el resto."""
    lineas = ENV.read_text(encoding="utf-8").splitlines() if ENV.is_file() else []
    salida, puesto = [], False
    for linea in lineas:
        if linea.startswith("CLOUDFLARE_API_TOKEN="):
            salida.append(f"CLOUDFLARE_API_TOKEN={token}")
            puesto = True
        else:
            salida.append(linea)
    if not puesto:
        salida.append(f"CLOUDFLARE_API_TOKEN={token}")
    ENV.write_text("\n".join(salida).rstrip("\n") + "\n", encoding="utf-8")
    ENV.chmod(0o600)


def main():
    token = getpass.getpass("Token de Cloudflare (no se verá al escribir): ").strip()
    if not token:
        sys.exit("Token vacío: nada que guardar.")
    ok, mensaje = verificar(token)
    if not ok:
        sys.exit(f"No guardado: {mensaje}")
    escribir(token)
    print(f"Guardado en {ENV} — {mensaje}. Permisos del fichero: 600.")


if __name__ == "__main__":
    main()
