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

## Estado del despliegue (hecho el 26-10 por Mastermind)

- ✅ Namespace KV `kit72h-eventos-EVENTOS` creado (id `e6642d8a966042e1ad636b670ead57da` en wrangler.toml)
- ✅ Worker desplegado: **https://kit72h-eventos.dantizar.workers.dev** (OAuth de dantizar@gmail.com)
- ✅ Secret `TOKEN` subido (`openssl rand -hex 24`), también en `.env` local del PC
- ✅ Test end-to-end en producción: ingesta válida agrega (incluida posición), evento inválido rechazado, `/resumen` exige token (401 sin él), origen malicioso rechazado. Datos de prueba borrados (KV `eventos: []`)
- ✅ `CONFIG.worker.url` conectado → tag `v20261026b` en las 190 páginas, pusheado (CI verde)

## Falta (2 cosillas)

1. **`.env` de la VM** (para que el cron de analítica de allí lea el worker). Un comando desde cualquier terminal git-bash de este PC:
   `grep "^KIT72H_EVENTOS" ~/Projects/kit72h/.env | ssh -p 30222 uuid@ssh.nan.builders 'cat >> ~/Projects/kit72h/.env'`
   (pedirá la contraseña de la VM). Alternativa: pegar las 2 líneas `KIT72H_EVENTOS_URL/TOKEN` del `.env` local en el chat del agente de la VM.
2. **Amazon Associates**: 2-3 Tracking IDs por sección (atribución gratis en informes) — 5 min en dash.amazon-adsystem.com.

## Cómo se usa (el oro)

Panel → /analiticas/ → sección Funnel: página con MUCHAS visitas y CTR bajo =
ahí muere la venta → cambiar CTA/copy/orden → medir la semana siguiente.
La analítica no vende: el ciclo dato→cambio→medir semanal (F3) es lo que mueve
la aguja hacia 1 k€/mes.
