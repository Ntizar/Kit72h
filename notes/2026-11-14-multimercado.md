# Multi-mercado: 7 países, 6 idiomas, un solo repo — 2026-11-14

## Qué pidió David

«Ya puedo vender en todos los países. Al tener la API, es necesario crear un sistema con
los principales países europeos y USA: toda la web traducida a esos idiomas, con opción de
cambiar de país y que te lleve a un país u otro.»

Decisiones cerradas en la conversación:

| Pregunta | Decisión |
|---|---|
| Mercados | 7: ES, Reino Unido, Alemania, Francia, Italia, Países Bajos, EE. UU. |
| Tracking IDs | `ntizar-21` (.es) y `onamzntizar-21` (.com). Faltan los de .co.uk, .de, .fr, .it, .nl |
| Blog | Kits + interfaz ya; las 64 guías se traducen por lotes (cron) |
| Precios | € por ahora; moneda local cuando la API de Amazon esté conectada |

## Arquitectura

- **`data/mercados.json`** es la fuente de verdad de todo lo que cambia por país: dominio
  de Amazon, tag de afiliado, moneda, número de emergencia y autoridad. No hay país
  hardcodeado en el código.
- **El castellano se queda en la raíz** (`/`, `/kit/x/`, `/blog/y/`). Moverlo habría tirado
  a la basura ~190 páginas ya indexadas. Los demás mercados nacen en subcarpeta:
  `/en-gb/`, `/de/`, `/fr/`, `/it/`, `/nl/`, `/en-us/`.
- **`js/i18n.js`**: textos de interfaz, prefijo de rutas, dominio+tag de Amazon, conversión
  de precios y selector de país. Antes había ~150 textos en castellano hardcodeados en
  `js/ui.js`; ahora todos salen de `data/i18n/ui/<lang>.json`.
- **El contenido no se duplica**: `data/kits.json` y `data/blog.json` siguen siendo la
  fuente. Encima se fusiona `data/i18n/contenido/<lang>.json` (solo textos). ASINs, URLs
  y precios vienen siempre del original: un overlay a medias nunca rompe un enlace.
- **`scripts/mercados.py`**: fuente única de mercados, merge y rutas, compartida por el
  prerender y el generador de sitemap. Antes la lógica de rutas iba a estar en dos sitios.
- **Redirección por país**: cookie/localStorage (la elección manda siempre) → `/cdn-cgi/trace`
  de Cloudflare (`loc=DE`) → `navigator.language`. Los buscadores no se redirigen: la raíz
  se indexa en castellano y el `hreflang` hace el resto.

## Amazon: por qué fuera de España se enlaza a búsqueda

Un ASIN de `amazon.es` no siempre existe en `.de` ni en `.com`; un enlace muerto vende
cero y encima queda feo. Fuera de España el botón lleva a la **búsqueda del producto
traducido en el Amazon del país**, con su tag. Cuando la Product Advertising API esté
conectada, `asin_local`/`precio_local` toman el mando (el hueco ya está en el merge) y se
podrá montar cesta local. Los tags de .co.uk/.de/.fr/.it/.nl están vacíos en
`mercados.json` con `tagPendiente: true`: sin ellos el enlace abre la tienda correcta pero
no comisiona.

## Traducción

`scripts/traducir.py` (deepseek-v4-flash, medido: qwen3.8-max tardaba 280 s un lote que el
flash hace en 8):

- caché por cadena (`data/i18n/.cache/<lang>.json`, fuera de git) → solo traduce lo nuevo;
- lotes de ~2.200 caracteres, 4 hilos;
- valida que se conserven etiquetas HTML y marcadores `{n}`; si no, reintenta de una en una
  y, si vuelve a fallar, deja castellano antes que romper;
- un lote fallido **no se cachea** (bug detectado: se cacheaba el castellano y quedaba
  marcado como traducido). La siguiente pasada purga esos falsos positivos;
- el disclosure de afiliado y la FAQ del coche (baliza V-16 de la DGT) **no** los traduce
  el modelo: el texto legal va fijado a mano por idioma y la FAQ se adapta, porque contar
  la ley española a un alemán como si fuera la suya es peor que no traducir.

## Prerender y SEO

- Cada mercado hornea sus rutas: `/`, `/fuentes/`, `/blog/`, los 21 kits y —solo cuando
  están traducidas— las entradas de blog. Publicar 64 artículos en castellano bajo `/de/`
  sería contenido duplicado.
- `hreflang` completo en cada página (7 mercados + `x-default` → castellano) y sitemap con
  `<xhtml:link>` por URL.
- `/zona/` y `/noticias/` son de España (AEMET, IGN, Google News ES): no se generan fuera
  y desaparecen de la navegación (`html:not([data-mercado="es"]) .solo-es`).
- El gate de CI (`verificar-sitio.py`) ahora revisa además: `lang` correcto por mercado,
  `hreflang` mínimo, canonical con prefijo y que cada mercado enlace a **su** Amazon.

## Lo que queda

1. **Tracking IDs** de .co.uk, .de, .fr, .it, .nl (David, 5 min en Associates).
2. **Blog**: 64 guías × 5 idiomas. Se lanza por lotes; el prerender no publica una guía
   hasta que su overlay está completo.
3. **Product Advertising API**: credenciales por marketplace para ASIN y precio locales.
4. **Privacidad**: `/privacidad/` solo existe en castellano; falta versión por idioma.
