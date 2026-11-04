# El panel de Afiliados no cuadra con la web — diagnóstico completo (2026-11-04)

Contexto: captura del panel (30 días, 04/11) con pico brutal el 2-nov (~3.000 clics,
~100 pedidos). Pregunta de David: «¿la web va como un tiro? ¿por qué no cuadran los
números?». Respuesta corta: **el pico no son compradores, son bots**. Y hay dos
sistemas de medición rotos que lo tapan.

## Lectura correcta de la tabla del panel (las cifras que NO son ingresos)

| Etiqueta del panel | Valor | Qué es de verdad |
|---|---|---|
| Número de Clics | 6.109 | clics a enlaces con `tag=ntizar-21` (incluye crawlers) |
| Productos pedidos | 203 | pedidos hechos en 24 h tras clic |
| Conversión | 3,32 % | pedidos/clics (inflada de bots si hay clics fantasma) |
| Productos enviados | 139 | de los 203, los que Amazon envió |
| Ingresos por productos enviados | **2.399,31 €** | FACTURACIÓN de Amazon, NO nuestros ingresos |
| Facturación de productos pedidos | 3.984,05 € | facturación de los pedidos aún no enviados |
| **Total de ingresos** | **82,75 €** | LA comisión real del mes (3,45 % de lo enviado) |

Regla: en el panel de Afiliados solo «Total de ingresos» es dinero. Las dos cifras
grandes (2.399 € / 3.984 €) son facturación de Amazon. 82,75 € / 139 enviados =
**0,60 € por pedido enviado** — el cuello de botella sigue siendo el ticket medio
(powerbanks de 20 €), no el tráfico. Confirmado de nuevo: ticket alto manda.

## Por qué el pico del 2-nov NO son compradores

Cruzado con `data/analiticas.json` (fuente cloudflare-zona) y la API GraphQL de Cloudflare:

- **Zona:** 5.475 pageviews el 2-nov vs 400-950 los días normales (10× pico exacto).
- **Países del mes:** AR, CN, IT, IN, KR, HK, GB, TW, JP, FI — España ni está en el top 10.
- **Páginas top del mes:** `/proc/self/environ`, `/_profiler/phpinfo` → olas de vuln-scan.
- **RUM (beacon):** muerto desde el 20-oct (último día con datos; cero desde entonces
  pese al JS en producción). Por eso el pipeline cae a `cloudflare-zona`, que cuenta bots.
- Los clics fantasma son un fenómeno documentado del programa: los crawlers (los
  scanners del 2-nov y nuestros **AI crawlers permitidos** en robots.txt — GPTBot,
  PerplexityBot siguen enlaces) hacen GET a las URLs con `tag=` y Amazon los cuenta
  como clics. 3K clics / 5.475 páginas servidas ≈ 0,55 clics por página: ratio de
  crawler que sigue 1 enlace por página, no de humanos.

## Lo roto (3 cosas) y su arreglo

1. **Beacon de Cloudflare muerto desde el 20-oct** → POST a `cloudflareinsights.com/cdn-cgi/rum`
   responde **404** con el site tag actual: el sitio de Web Analytics fue borrado o el
   token invalidado. REQUIERE DASHBOARD: Cloudflare → kit72h.com → Analytics & Logs →
   Web Analytics → verificar sitio (o crear uno nuevo y pegar el site tag nuevo en
   `js/analiticas.js` → `CONFIG.beacon_cloudflare` + bump `VER` en
   `scripts/instrumentar-analitica.py`). El token de API no tiene permisos para esto.
2. **`clics_amazon: 0` y funnel vacío** → el worker de eventos SÍ ingiere
   (`POST /e` con Origin → 204 verificado), pero el `.env` de la VM no tiene
   `KIT72H_EVENTOS_URL`/`KIT72H_EVENTOS_TOKEN` y el lector no puede leer `/resumen`
   (401). El token (48 hex) no está en el repo ni en `state.db` de la VM: vive en el
   `.env` del **PC** (nota 2026-10-26 del funnel). Copiar con el comando de esa nota
   (git-bash del PC → ssh append al `.env` de la VM). Mientras el KV queme su cupo
   diario (v1 sin deployar por permisos), `/resumen` puede dar 429: el pipeline ya
   cae a zona con aviso — ok mientras tanto.
3. **Sin credenciales de Afiliados por API**: el panel nuevo (affiliate-program.amazon.com)
   no tiene API pública de lectura y las cookies de sesión están vacías (26-10).
   La lectura es manual: pedir a David la captura o el CSV de «Informes detallados»
   (desglose por Tracking ID y por tipo de enlace) para separar clics humanos de
   crawlers. Proponer 3 Tracking IDs (`kit72h-home-21`, `kit72h-kits-21`,
   `kit72h-blog-21`) para que el desglose sea posible: hoy solo existe `ntizar-21`.

## Adelgazar el ruido de bots

- `robots.txt`: bloqueo explícito de scanners conocidos (añadido hoy). Los probes de
  rutas (`/proc/…`) no leen robots: el corte de verdad va por **WAF de Cloudflare**
  (regla custom: `http.request.uri.path contains "/proc/"` → Block), que también
  requiere dashboard (el token no tiene Zone:Edit).
- Decisión pendiente de David: mantener la bienvenida a AI crawlers (visibilidad en
  respuestas de IA) sabiendo que generan clics fantasma en el panel, o restringirlos.
  El desglose por Tracking ID + el informe por tipo de enlace dirán cuánto pesan.

## Lecciones operativas

- **`curl` a `amazon.es/?tag=…` desde servidor da 503/403 SIEMPRE (muro anti-bot)**:
  no es señal ni de tag válido ni de tag roto. El 404 del endpoint del beacon tampoco
  se confunde con el muro: ese es del lado de Cloudflare Insights.
- **El panel miente por diseño si hay crawlers**: cualquier pico de clics se cruza
  SIEMPRE con la zona de Cloudflare (países + rutas) antes de celebrar nada.
- RUM por cuenta, no por zona: `accounts(filter:{accountTag:…}).rumPageloadEventsAdaptiveGroups`
  con `siteTag` en el filtro (sin `sum.pageViews`, solo `count` — ese campo no existe
  en el schema actual).
