# Analítica de Kit72h: qué se mide, cómo y qué falta (2026-10-12)

## El problema de partida

Kit72h vende (poco) y no había **ni una sola métrica**: sin analítica en el
HTML (cero scripts de medición) y sin acceso a los informes de Amazon. Es decir,
la frase «pocas visitas» era una impresión, no un dato. No se puede optimizar lo
que no se mide: sin saber qué página trae gente y qué enlace se pulsa, los crons
nocturnos optimizan a ciegas (SEO, CTR, ofertas… todo a ciegas).

## Las dos métricas que de verdad importan

1. **Visitas por página + de dónde vienen** → qué contenido trae gente
   (Pinterest, Google, directo, IA).
2. **Clic al enlace de Amazon** → la intención de compra. Es el paso previo a la
   comisión y el único que podemos medir sin depender de Amazon.

Cruce de las dos = CTR a Amazon por página. Ahí está el aprendizaje: hay páginas
que convierten con 20 visitas y páginas que son decorativas con 200.

## Lo que se ha montado (todo gratis, sin cookies, sin PII)

| Pieza | Fichero | Qué hace |
|---|---|---|
| Cliente | `js/analiticas.js` | Carga el proveedor configurado + eventos `clic-amazon` (con posición del enlace) y `scroll-50/90`. Si no hay proveedor, no hace ninguna petición. |
| Instrumentación | `scripts/instrumentar-analitica.py` | Mete el `<script>` en el `<head>` de las 75 páginas. Idempotente (2ª pasada = 0 cambios). Se salta `pintout/` (renders de Pinterest) y `sketches/`. |
| Pipeline | `scripts/kit72h-analiticas.py` | Baja métricas (Cloudflare RUM / Umami) y escribe `data/analiticas.json` con un esquema fijo. |
| Panel | `/analiticas/` | Dashboard Aurora que pinta ese JSON. `noindex` + `Disallow` en robots.txt. |
| Cron | `kit72h-analitica` (08:45, VM) | Instrumenta lo nuevo + refresca el JSON + push vía `runner-kit72h.py`. |

Decisiones de diseño y por qué:

- **Analítica sin cookies** → no hace falta banner de consentimiento (nada que
  consentir: no hay cookies ni identificadores). Reflejado en `/privacidad/`.
- **Instrumentación por script, no editando 7 generadores**: los crons nocturnos
  reescriben HTML; un script idempotente que corre cada mañana después de ellos
  garantiza que ninguna página nueva se quede sin medir, sin tocar los
  generadores (menos superficie de rotura).
- **La query string nunca se envía**: solo `location.pathname`. El buscador
  interno podría llevar texto del usuario y eso es dato personal.
- **Proveedor agnóstico**: Cloudflare Web Analytics para visitas (gratis, ya
  tiene la cuenta) y Umami Cloud si además queremos eventos (su free tier
  soporta eventos personalizados; Cloudflare no). Cambiar de proveedor = editar
  el objeto `CONFIG` de `js/analiticas.js`.

## Qué falta (y quién lo desbloquea)

1. **Visitas**: activar **Cloudflare Web Analytics** para kit72h.com y pegar el
   token del beacon en `CONFIG.beacon_cloudflare`. Para que el cron lea los
   datos hace falta además un **token de API de Cloudflare con permiso
   `Account > Account Analytics > Read`** en el `.env` de Hermes
   (`CLOUDFLARE_API_TOKEN`, opcional `CLOUDFLARE_ACCOUNT_ID`, `CF_RUM_SITE_TAG`).
   *Aprendizaje:* el token que había era solo de DNS (no vale para leer RUM), y
   **Turnstile de Cloudflare bloquea el navegador automatizado** → la gestión de
   Cloudflare es manual de David, siempre.
2. **Clics a Amazon**: elegir Umami Cloud (gratis, 10k eventos/mes) si se quieren
   eventos por página. Alternativa sin terceros: *Cloudflare Pages Function + KV*
   como contador propio (`/api/clic`) — más trabajo, control total.
3. **«Quién compra y qué»** (fase 3): eso vive en **Amazon Associates**. Dos vías:
   informes de Associates (requiere login → hay que resolverlo con navegador real
   o exportando el CSV a mano) o **PA-API 5.0** con Access/Secret key, que sí es
   automatizable por script y da pedidos, unidades, precio y comisión por ASIN —
   **nunca la identidad del comprador** (Amazon no la expone, y está bien).
   Con PA-API + este JSON se cierra el embudo entero:
   visita → clic → pedido → comisión.

## Recordatorio de seguridad

Los tokens **nunca** van al repo ni se pegan en el chat: van al `.env` de Hermes
en el PC (`%LOCALAPPDATA%\hermes\.env`) y, para el cron, al de la VM
(`~/.hermes/.env`). El único fichero público es `js/analiticas.js`, y ahí solo
puede vivir el **token del beacon** de Cloudflare (que es público por diseño: va
en el HTML de todas formas).
