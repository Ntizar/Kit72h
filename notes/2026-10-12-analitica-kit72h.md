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

## Dos trampas que costaron un susto (¡leer antes de tocar esto!)

1. **El sitio se re-hornea cada noche con Chromium** (`scripts/prerender.py`).
   Todo lo que un JS añade al DOM **queda escrito** en el HTML estático. Si el
   cargador inyectase el beacon en runtime sin comprobar nada, el beacon
   acabaría **duplicado** al día siguiente (visitas contadas dos veces). Por eso
   `cargar()` de `js/analiticas.js` no añade una etiqueta cuyo `src` ya exista.
   Regla general: en esta web, cualquier cosa que se inyecte desde JS debe ser
   **idempotente**.

2. **Los crons LLM del repo hacen `git add -A` y publican.** El 12/10 a las
   06:43 el cron de CTR barrió el árbol y **publicó en producción este trabajo
   antes de que David diera el ✅** (commit `8be99b4`, que además añadió
   `analiticas` a la lista de copia de `.github/workflows/pages.yml`, cambio
   necesario sin el cual el panel no se habría desplegado). Consecuencia
   operativa: **nunca dejar trabajo a medias en el árbol del repo** — se publica
   solo. Si hay que preparar algo sin publicarlo, hacerlo en otra rama o en
   `~/scratch`.

3. **El pie también se toca por script**: el enlace discreto al panel lo pone
   `scripts/instrumentar-analitica.py` (`--solo-pie` hace solo esa parte). El
   bump de la versión del CSS es **quirúrgico** (solo el número tras `?v=`):
   el 02/10 un regex goloso se comió el `">` del `<link>` en 67 ficheros y dejó
   la web sin CSS. Validar siempre con `python3 scripts/verificar-sitio.py`
   (chequea que `styles.css?v=` sea consistente en todas las páginas).

