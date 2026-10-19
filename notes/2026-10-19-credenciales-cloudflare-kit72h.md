# Credenciales de Cloudflare en kit72h (VM Linux)

El token de Cloudflare vivía solo en el PC de Windows (`C:\Users\d_ant\Projects\kit72h\.env`),
así que en la VM el pipeline de analíticas escribía `estado: sin-credenciales` y el panel
`/analiticas/` se quedaba a cero. Desde hoy el `.env` canónico del proyecto está en el repo,
en la VM.

## Dónde vive

- **Fuente única:** `~/Projects/kit72h/.env` (`.env` y `.env.*` ignorados en `.gitignore`,
  permisos 600). No se copia a `~/.hermes/.env`: una fuente por tema.
- **Quién lo lee:** `scripts/kit72h-analiticas.py` lo carga él mismo (`_cargar_env_local()`),
  sin pisar lo que ya venga exportado. Así funciona igual a mano que desde el cron, que solo
  hereda el entorno de Hermes.
- **Alta del token:** `python3 scripts/guardar-token-cloudflare.py` — entrada oculta, valida
  contra `/user/tokens/verify` y solo escribe si el token está activo.

## Claves

| Clave | Valor | Nota |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` | (secreto) | token de la foto, verificado `active` |
| `CLOUDFLARE_ACCOUNT_ID` | `142476a78dab7d271ec55d5c4a46dd7c` | visible en el panel |
| `CF_RUM_SITE_TAG` | `2cd51d4e9fe241849269fc0bed3083cc` | **obligatorio** con este token |

## Lo que este token puede y no puede

Comprobado con llamadas reales:

- ✅ `/user/tokens/verify` → `active`.
- ✅ `/zones?name=kit72h.com` → zona `28caa73218ad32b8ad69a35254459a82`, `active`.
- ✅ `POST /graphql` con `rumPageloadEventsAdaptiveGroups` → datos reales (2.830 visitas / 30 días).
- ❌ `/user` y `/accounts` → `403 9109` (sin permiso de lectura de cuenta).
- ❌ `/accounts/{id}/rum/site_info/list` → `403`.

Consecuencia: **el site tag no se puede autodescubrir**, va fijo en `CF_RUM_SITE_TAG`. Si algún
día se rota el token, pedirle al menos *Account Analytics: Read* + *Zone: Read* para que el
descubrimiento vuelva a funcionar.

El site tag se sacó por GraphQL, pidiendo la dimensión `siteTag` junto a `requestHost`
(la variante con `requestHost` es la que dice a qué dominio pertenece cada tag).

## Trampa que casi muerde

`scripts/cron/runner-kit72h.py` termina con `git add -A` en el repo. Sin `.env` en `.gitignore`,
el primer cron habría commiteado el token al repositorio **público**. Ahora está ignorado y
`git check-ignore .env` lo confirma.

## OCR de fotos de pantalla: no

El token se transcribió de una foto y Cloudflare lo rechazó dos veces (401): `1` vs `l` en
`TgElAK`/`dql9` fue suficiente. Un secreto se copia como texto o se pega por consola, nunca
se transcribe de una foto.
