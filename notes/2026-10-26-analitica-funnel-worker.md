# Analítica gratis de punta a punta: funnel de venta (2026-10-26)

Decisión pendiente desde 2026-10-13 (bloqueo Umami free, ver nota de ese día) ejecutada:
**Umami descartado por fin** → Worker propio de Cloudflare Workers + KV para eventos,
RUM de Cloudflare para visitas. 0 € y sin API de lectura limitada.

## Qué se implementó (Fase 1, commit b9238d3)

- **`worker-eventos/`** (nuevo): worker CF sin dependencias — ingesta `POST /e`
  (lotes desde `sendBeacon`), agregación por día en KV (`d:YYYY-MM-DD`, mapa
  `"evento|ruta" → n` y `"evento|ruta|pos-N" → n`), `GET /resumen?dias=30`
  protegido con Bearer (secret `TOKEN`). Sin PII: la IP nunca se escribe.
  Pasos de despliegue → `worker-eventos/README.md` (3 comandos wrangler).
- **`js/analiticas.js`**: `CONFIG.worker` (url vacía hasta desplegar) + transport
  COLA: lotes de 20, flush 15 s / pagehide / visibilitychange, ignora
  `navigator.webdriver` (el prerender nocturno no cuenta como tráfico).
- **`scripts/kit72h-analiticas.py`**: función `worker_eventos()` (env
  `KIT72H_EVENTOS_URL`/`KIT72H_EVENTOS_TOKEN`); el worker sustituye a Umami como
  contador de eventos cuando tiene datos (evita doble recuento). Estados
  distinguibles: sin-credenciales ≠ error (token malo del worker → "error").
- **`analiticas/index.html`**: sección "Funnel — dónde se muere la venta" con
  tabla cruzada (Página · Visitas · Leyeron 50 % · Al final 90 % · Clics Amazon ·
  CTR) y CTR = clics/visitas por página.
- **Instrumentación**: tag `v20261026a` en las 190 páginas (VER del
  instrumentar-analitica.py actualizado → el cron nocturno de la VM no revierte).
  99+ páginas nuevas de crons que estaban SIN analítica pasan a medirse.

## Fusiones con la VM (aprender del día)

La madrugada del 26 la VM pusheó 27 commits y hubo 2 conflictos:
1. `.py`: la VM usaba `serie` (nombre real de la variable); mi parche decía
   `mapa_fecha` (nombre que no existía en ese bloque). **Lección: al parchear
   variables, verificar el nombre real en el árbol vigente, no en mi copia local.**
2. Panel: unir FUENTES de ambos lados (su `cloudflare-zona` + mi `worker`).

## Falta para dejarlo encendido (5 min de David)

1. `npx wrangler kv namespace create EVENTOS` → pegar id en `worker-eventos/wrangler.toml`
2. `npx wrangler secret put TOKEN` (generar: `openssl rand -hex 24`)
3. `npx wrangler deploy` → anotar URL → ponerla en `CONFIG.worker.url` de
   `js/analiticas.js` + env `KIT72H_EVENTOS_URL`/`KIT72H_EVENTOS_TOKEN` (repo y host del cron)
4. Amazon Associates: 2-3 Tracking IDs por sección (atribución gratis en informes)

## Cómo se usa (el oro)

Panel → /analiticas/ → sección Funnel: página con MUCHAS visitas y CTR bajo =
ahí muere la venta → cambiar CTA/copy/orden → medir la semana siguiente.
La analítica no vende: el ciclo dato→cambio→medir semanal (F3) es lo que mueve
la aguja hacia 1 k€/mes.
