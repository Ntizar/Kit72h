# Activar analítica de Kit72h (Cloudflare Web Analytics) — para David

**Fecha:** 15-oct-2026 · **Estado:** listo para que David saque el token y lo pegue

## Qué hacer (2 minutos)

1. Entra en https://dash.cloudflare.com con tu cuenta (la del DNS de kit72h.com).
2. Menú lateral → **Web Analytics** → «Add a site» / «Añadir sitio».
3. Escribe `kit72h.com` (dominio raíz, sin www). No hace falta cambiar nada del DNS ni del proxy.
4. Te da un **snippet** con un token tipo:
   ```html
   <script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{"token": "ABCD1234..."}'></script>
   ```
5. Copia SOLO el valor del token (lo que va entre las comillas de `token`).
6. Pégamelo aquí en el chat y yo hago el resto (activar `js/analiticas.js`, verificar el beacon en producción y validar el panel). O si prefieres hacerlo tú:
   - Edita `js/analiticas.js` → línea `beacon_cloudflare: ""` → pon el token.
   - Bumpea `analiticas.js?v=` en las ~80 páginas (o dime y corro `scripts/instrumentar-analitica.py` que lo hace idempotente).
   - Commit + push.

## Qué pasa después

- A las ~1 h empieza a llegar visita real al dashboard de Cloudflare (Web Analytics).
- El cron `kit72h-analitica` (08:45 diario) rellena `data/analiticas.json` y el panel `/analiticas/` — pero necesita el token/credenciales para leer la API de Cloudflare (Graphql) también en el `.env`. Así que además del token público del beacon:
  - **Beacon token (público, va al JS):** lo que sacas del paso 4.
  - **API token (privado, va al `.env` del VM):** en Cloudflare → Mi perfil → **API Tokens** → «Create Token» → plantilla **"Web Analytics Read"** (o permiso `Web Analytics: Read` para la zona kit72h.com). Ese token es el que el cron usa para leer el JSON de visitas y rellenar el panel `/analiticas/`.
  - Pégame los dos (o solo el del beacon y el API token lo pegas en `~/.hermes/.env` como `CLOUDFLARE_ANALYTICS_TOKEN=...` — el nombre exacto de la var está en `scripts/kit72h-analiticas.py`).
  - NUNCA en el repo: el beacon va al JS (público por diseño), el API token al `.env` (no en git).
- El beacon no pone cookies ni rastrea PII (regla de la casa).

## Estado de esta sesión (lo que ya está hecho y desplegado)

- ✅ OG completos en las ~80 páginas (og:title/description/image/locale + twitter:card large) — verificado en producción.
- ✅ `assets/og-kit72h.png` (1200×630) servida con 200.
- ✅ Allowlist del deploy con `assets/`.
- ✅ Tag `<link rel=" icon">` roto eliminado del head.
- ✅ Favicon inline «72» en todas las páginas.
- ✅ Gate 0 errores.
- ⏳ Analítica Cloudflare: pendiente de tu token (pasos de arriba).
- ⏳ Search Console / Bing Webmaster: pendiente de verificar propiedad (necesita tu cuenta Google/Microsoft) — el sitemap es `https://kit72h.com/sitemap.xml`.
- ⏳ Posts Reddit/LinkedIn del plan del 14-oct: borradores listos, esperando tu OK.
