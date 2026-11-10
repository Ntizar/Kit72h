#!/usr/bin/env python3
"""Kit72h — cliente de la Creators API de Amazon Afiliados (PA-API 5.0 ya no existe).

Credenciales en el `.env` del repo (nunca en git):
    AMAZON_CREDENTIAL_ID, AMAZON_CREDENTIAL_SECRET, AMAZON_CREDENTIAL_VERSION,
    AMAZON_PARTNER_TAG, AMAZON_MARKETPLACE (opcional), AMAZON_TOKEN_URL (override)

Uso:
    python3 scripts/amazon_api.py estado
    python3 scripts/amazon_api.py item B08S17DS6N [ASIN…]
    python3 scripts/amazon_api.py buscar "filtro de agua" --n 3

Notas medidas contra la API real (2026-11):
- El precio vive en `offersV2.listings[0].price.money.amount` (con `displayAmount` ya
  formateado). Un lector de `price.amount` devuelve None en TODOS los productos.
- `getItems` acepta hasta 10 `itemIds` por petición: 233 ASIN = 24 llamadas, no 233.
- `savingBasis` trae el precio recomendado (el «antes» del descuento) cuando lo hay.
"""
from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ENV = RAIZ / ".env"
CACHE = RAIZ / ".cache" / "creators-token.json"
API = "https://creatorsapi.amazon/catalog/v1"

TOKEN_URLS = {
    "2.1": "https://creatorsapi.auth.us-east-1.amazoncognito.com/oauth2/token",
    "2.2": "https://creatorsapi.auth.eu-south-2.amazoncognito.com/oauth2/token",
    "2.3": "https://creatorsapi.auth.us-west-2.amazoncognito.com/oauth2/token",
    "3.1": "https://api.amazon.com/auth/o2/token",
    "3.2": "https://api.amazon.co.uk/auth/o2/token",
    "3.3": "https://api.amazon.co.jp/auth/o2/token",
}

RECURSOS = [
    "itemInfo.title",
    "itemInfo.byLineInfo",
    "images.primary.medium",
    "offersV2.listings.price",
    "offersV2.listings.availability",
]

MAX_IDS = 10          # tope real de itemIds por getItems


def cargar_env() -> dict:
    cfg = {}
    if ENV.exists():
        for linea in ENV.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            k, v = linea.split("=", 1)
            cfg[k.strip()] = v.strip().strip('"').strip("'")
    cfg.setdefault("AMAZON_MARKETPLACE", "www.amazon.es")
    cfg.setdefault("AMAZON_CREDENTIAL_VERSION", "3.2")
    return cfg


def _post(url: str, cuerpo: bytes, cabeceras: dict, timeout: int = 25) -> tuple[int, bytes]:
    req = urllib.request.Request(url, data=cuerpo, headers=cabeceras, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except urllib.error.URLError as e:
        raise SystemExit(f"Sin conexión con Amazon ({url}): {e.reason}")


def _pedir_token(url: str, cid: str, secreto: str, estilo_json: bool) -> tuple[int, bytes]:
    if estilo_json:  # Login with Amazon (credencial 3.x)
        cuerpo = json.dumps({
            "grant_type": "client_credentials",
            "client_id": cid,
            "client_secret": secreto,
            "scope": "creatorsapi::default",
        }).encode()
        cab = {"Content-Type": "application/json"}
    else:            # Cognito (credencial 2.x)
        cuerpo = urllib.parse.urlencode({
            "grant_type": "client_credentials",
            "scope": "creatorsapi/default",
        }).encode()
        cab = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + base64.b64encode(f"{cid}:{secreto}".encode()).decode(),
        }
    return _post(url, cuerpo, cab)


def token(cfg: dict, renovar: bool = False) -> str:
    """OAuth cacheado en disco (3.600 s), renovado 60 s antes de caducar."""
    if not renovar and CACHE.exists():
        try:
            d = json.loads(CACHE.read_text())
            if d.get("expira", 0) - 60 > time.time() and d.get("id") == cfg["AMAZON_CREDENTIAL_ID"]:
                return d["token"]
        except (json.JSONDecodeError, KeyError):
            pass

    version = cfg["AMAZON_CREDENTIAL_VERSION"]
    url = cfg.get("AMAZON_TOKEN_URL") or TOKEN_URLS.get(version)
    if not url:
        raise SystemExit(f"Versión de credencial desconocida: {version}. Define AMAZON_TOKEN_URL en .env "
                         f"(conocidas: {list(TOKEN_URLS)})")

    cid, secreto = cfg["AMAZON_CREDENTIAL_ID"], cfg["AMAZON_CREDENTIAL_SECRET"]
    estado, resp = _pedir_token(url, cid, secreto, version.startswith("3"))
    if estado >= 400:  # el otro estilo, una sola vez
        estado, resp = _pedir_token(url, cid, secreto, not version.startswith("3"))
    if estado >= 400:
        texto = resp.decode(errors="replace")
        if "AssociateNotEligible" in texto:
            raise SystemExit("AssociateNotEligible: la cuenta no cumple el umbral de ventas de Amazon "
                             "(10 ventas cualificadas/30 días). Las claves son válidas; no hay nada que "
                             "configurar. Ver skill amazon-creators-api.")
        raise SystemExit(f"Token rechazado ({estado}) en {url}\n{texto[:600]}")

    d = json.loads(resp.decode())
    t = d.get("access_token")
    if not t:
        raise SystemExit(f"Respuesta de token sin access_token: {resp.decode()[:400]}")
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps({"token": t, "expira": time.time() + int(d.get("expires_in", 3600)),
                                 "id": cid}))
    return t


def llamar(cfg: dict, operacion: str, payload: dict, intentos: int = 3) -> dict:
    """POST a la API con reintento (401 → token nuevo; 5xx/429 → espera y reintenta)."""
    cuerpo = json.dumps(payload, ensure_ascii=False).encode()
    ultimo = ""
    for n in range(intentos):
        cab = {
            "Authorization": "Bearer " + token(cfg, renovar=(n > 0)),
            "Content-Type": "application/json",
            "x-marketplace": cfg["AMAZON_MARKETPLACE"],
        }
        estado, resp = _post(f"{API}/{operacion}", cuerpo, cab)
        texto = resp.decode(errors="replace")
        if estado < 400:
            return json.loads(texto)
        ultimo = f"HTTP {estado} en {operacion}: {texto[:400]}"
        if estado == 403 and "AssociateNotEligible" in texto:
            raise SystemExit(ultimo + "\n(AssociateNotEligible: cuenta por debajo del umbral de ventas)")
        if estado not in (401, 429, 500, 502, 503, 504):
            break
        time.sleep(1.5 * (n + 1))
    raise RuntimeError(ultimo)


def _money(bloque) -> dict:
    """`{'money': {...}}` (forma 2026) o `{'amount': …}` (forma plana antigua)."""
    if not isinstance(bloque, dict):
        return {}
    m = bloque.get("money") if isinstance(bloque.get("money"), dict) else bloque
    return m if isinstance(m, dict) else {}


def _oferta(item: dict) -> dict | None:
    for rama in ("offersV2", "offers"):
        lista = (item.get(rama) or {}).get("listings") or []
        if lista:
            return lista[0]
    return None


def precio(item: dict) -> float | None:
    o = _oferta(item)
    return _money((o or {}).get("price")).get("amount")


def precio_texto(item: dict) -> str | None:
    o = _oferta(item)
    return _money((o or {}).get("price")).get("displayAmount")


def precio_antes(item: dict) -> float | None:
    """Precio recomendado (el «antes» tachado). Ojo: vive DENTRO de `price`,
    no en el listing — `price.savingBasis`, no `savingBasis`."""
    o = _oferta(item) or {}
    for contenedor in (o.get("price") or {}, o):
        for clave in ("savingBasis", "listPrice", "priceBeforeDiscount"):
            m = _money(contenedor.get(clave))
            if m.get("amount"):
                return m["amount"]
    return None


def ahorro_pct(item: dict) -> float | None:
    """Descuento real en %: manda `price.savings.percentage` de Amazon; si no
    viene, se calcula sobre el precio recomendado."""
    o = _oferta(item) or {}
    pct = ((o.get("price") or {}).get("savings") or {}).get("percentage")
    if isinstance(pct, (int, float)) and pct > 0:
        return round(float(pct), 1)
    actual, antes = precio(item), precio_antes(item)
    if not actual or not antes or antes <= actual:
        return None
    return round((antes - actual) / antes * 100, 1)


def disponible(item: dict) -> bool | None:
    o = _oferta(item) or {}
    tipo = ((o.get("availability") or {}).get("type") or "").upper()
    if not tipo:
        return None
    return tipo == "IN_STOCK"


def normalizar(item: dict) -> dict:
    """Forma estable que consume la web (data/precios.json)."""
    titulo = ((item.get("itemInfo") or {}).get("title") or {}).get("displayValue")
    return {
        "asin": item.get("asin"),
        "titulo": titulo,
        "precio": precio(item),
        "precio_texto": precio_texto(item),
        "precio_antes": precio_antes(item),
        "ahorro_pct": ahorro_pct(item),
        "disponible": disponible(item),
        "imagen": (((item.get("images") or {}).get("primary") or {}).get("medium") or {}).get("url"),
        "url": item.get("detailPageURL"),
    }


def _items(r: dict) -> list:
    for clave in ("itemsResult", "getItemsResult", "searchResult", "searchItemsResult"):
        if isinstance(r.get(clave), dict) and r[clave].get("items"):
            return r[clave]["items"]
    return []


def items_por_asin(cfg: dict, asins: list[str], pausa: float = 0.35) -> dict:
    """getItems en lotes de 10.

    Devuelve:
      ok            {asin: normalizado}
      sin_datos     ASIN que la API respondió pero no devolvió
      lotes_fallidos listas de ASIN cuyo lote falló por red/API
    """
    salida, fallos, lotes_fallidos = {}, [], []
    asins = [a for a in dict.fromkeys(asins) if a]
    for i in range(0, len(asins), MAX_IDS):
        lote = asins[i:i + MAX_IDS]
        payload = {
            "itemIds": lote,
            "partnerTag": cfg["AMAZON_PARTNER_TAG"],
            "marketplace": cfg["AMAZON_MARKETPLACE"],
            "resources": RECURSOS,
        }
        try:
            r = llamar(cfg, "getItems", payload)
        except RuntimeError as e:
            print(f"  ! lote {i//MAX_IDS + 1} falló: {str(e)[:160]}")
            fallos.extend(lote)
            lotes_fallidos.append(lote)
            continue
        vistos = set()
        for it in _items(r):
            n = normalizar(it)
            if n["asin"]:
                salida[n["asin"]] = n
                vistos.add(n["asin"])
        fallos.extend([a for a in lote if a not in vistos])
        if pausa:
            time.sleep(pausa)
    return {"ok": salida, "sin_datos": fallos, "lotes_fallidos": lotes_fallidos}


def buscar(cfg: dict, keywords: str, n: int = 3) -> list:
    r = llamar(cfg, "searchItems", {
        "keywords": keywords,
        "itemCount": max(1, min(n, 10)),
        "partnerTag": cfg["AMAZON_PARTNER_TAG"],
        "marketplace": cfg["AMAZON_MARKETPLACE"],
        "resources": RECURSOS,
    })
    return [normalizar(it) for it in _items(r)]


def main(argv: list[str]) -> int:
    cfg = cargar_env()
    if not cfg.get("AMAZON_CREDENTIAL_ID") or not cfg.get("AMAZON_CREDENTIAL_SECRET"):
        print("Faltan credenciales de la Creators API en .env "
              "(AMAZON_CREDENTIAL_ID / AMAZON_CREDENTIAL_SECRET / AMAZON_CREDENTIAL_VERSION).",
              file=__import__("sys").stderr)
        return 2
    orden = argv[1] if len(argv) > 1 else "estado"

    if orden == "item":
        asins = argv[2:]
        if not asins:
            print("uso: amazon_api.py item ASIN [ASIN…]", file=__import__("sys").stderr)
            return 2
        res = items_por_asin(cfg, asins)
        for a in asins:
            d = res["ok"].get(a)
            if d:
                antes = f" (antes {d['precio_antes']:.2f} €)" if d.get("precio_antes") else ""
                print(f"{a}  {d['precio_texto'] or '—':>9}{antes}  {(d['titulo'] or '')[:90]}")
            else:
                print(f"{a}  sin datos")
        return 0

    if orden == "buscar":
        kw = argv[2] if len(argv) > 2 else "kit de emergencia"
        for d in buscar(cfg, kw, 3):
            print(f"{d['asin']}  {d['precio_texto'] or '—':>9}  {(d['titulo'] or '')[:90]}")
        return 0

    print(f"marketplace={cfg['AMAZON_MARKETPLACE']}  versión={cfg['AMAZON_CREDENTIAL_VERSION']}  "
          f"tag={cfg['AMAZON_PARTNER_TAG']}")
    print("1/2 autenticando…")
    token(cfg)
    print("2/2 getItems de prueba (B08S17DS6N, B0DVLGQX5N)…")
    res = items_por_asin(cfg, ["B08S17DS6N", "B0DVLGQX5N"])
    for a, d in res["ok"].items():
        print(f"  {a}  {d['precio_texto'] or '—':>9}  "
              f"{('-' + str(d['ahorro_pct']) + '%') if d.get('ahorro_pct') else '':>6}  "
              f"{(d['titulo'] or '')[:70]}")
    if not res["ok"]:
        print("CREATORS API: sin datos", file=__import__("sys").stderr)
        return 1
    print("CREATORS API OK")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
