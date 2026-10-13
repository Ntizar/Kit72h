# Analítica: el plan gratis de Umami NO sirve para automatizar (2026-10-13)

## El bloqueo (verificado, no de memoria)

La nota del 12/10 y `references/analitica.md` daban por bueno «Umami Cloud free tier
(10k eventos) + `UMAMI_API_KEY`». **Es falso y bloquea todo el pipeline**, porque sin
API key no se puede leer nada por script y `data/analiticas.json` se queda en
`estado: "sin-credenciales"` para siempre.

Evidencia (contrastada hoy en fuentes primarias):

- `https://umami.is/pricing` → tabla de planes: **`API access`: Hobby = «—», Pro = ✓**.
  (También MCP y email reports van de Pro para arriba.)
- `https://umami.is/` → «Query your analytics from your AI assistant: **Available on
  Umami Cloud Pro plans and above**, and on self-hosted Umami v3.4 or later».
- `docs.umami.is/docs/cloud/api-key` no menciona el gating por plan (describe *cómo*
  crear la key), pero la tabla de precios es la fuente de verdad comercial.
- El free tier da 100K eventos/mes, 1 sitio, 6 meses de retención y **sí** soporta
  eventos personalizados — pero solo se ven **en el panel de Umami**, a mano.

Coste de la alternativa de pago: **Umami Pro = 20 $/mes** (1M eventos, API incluida).

## Lo que sí es gratis y automatizable

| Vía | Visitas | Clics a Amazon | API de lectura | Coste | Trabajo |
|---|---|---|---|---|---|
| Umami Cloud Hobby | ✅ | ✅ (evento) | ❌ **no hay** | 0 € | 3 min de alta |
| Umami Pro | ✅ | ✅ | ✅ | 20 $/mes | pagar |
| Umami self-hosted | ✅ | ✅ | ✅ | 0 € | servidor (no cabe en el VM de NaN) |
| **Cloudflare Web Analytics** | ✅ | ❌ (sin eventos) | ✅ GraphQL (plan free) | 0 € | token + activar en el panel |
| **Worker propio + KV** (para clics) | — | ✅ | ✅ (endpoint propio) | 0 € (free tier CF) | construir el Worker |

Cloudflare Web Analytics gratis consultado por API: confirmado en varias fuentes
(el dataset `rumPageloadEventsAdaptiveGroups` por GraphQL responde con un token de
`Account · Account Analytics · Read`, y la propia doc de CF dice que Web Analytics es
gratuito en todos los planes). **Limitación dura: no soporta eventos personalizados**,
así que el clic a Amazon NO se puede medir con el beacon de CF.

De ahí la pareja que sí encaja con la regla de casa (todo gratis, sin terceros):
**visitas por Cloudflare RUM + clics por un contador propio (Worker + KV)** en la zona
que ya está en Cloudflare. El panel `/analiticas/` no cambia de contrato: solo cambia de
dónde bebe cada mitad.

## Lo que solo puede hacer David (Turnstile bloquea la automatización)

El navegador automatizado no puede pasar el login/Turnstile de Cloudflare ni de Umami:
las altas y los tokens son **manuales, siempre**. Nada de pegar secretos en el chat:
el token de lectura va al `.env` de la VM (`~/.hermes/.env`); el `website_id`/beacon
es público y va en `js/analiticas.js` (`CONFIG`).

## Pendiente de decisión

Elegir vía: (a) Umami Hobby solo como observatorio manual, (b) Umami Pro pagando,
(c) **Cloudflare RUM + Worker propio** (la única gratis y automática de punta a punta),
(d) self-hosted en otro sitio. `references/analitica.md` y el skill `kit72h` dicen lo
contrario de lo que aquí se demuestra: **hay que corregirlos**.
