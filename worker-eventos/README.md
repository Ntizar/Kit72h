# worker-eventos — contador del funnel de kit72h.com

Worker de Cloudflare + KV que recibe los eventos de `js/analiticas.js`
(`clic-amazon`, `scroll-50`, `scroll-90`) y los agrega por día. Sin cookies,
sin PII: solo ruta y recuento. Free tier de punta a punta (0 €).

Los `scripts/kit72h-analiticas.py` lo lee por `/resumen` y lo mete en
`data/analiticas.json` junto a las visitas de Cloudflare Web Analytics.

## Despliegue (una vez, ~5 minutos)

```bash
# 1. Crear el namespace KV y copiar el id que devuelve:
npx wrangler kv namespace create EVENTOS
#    → pega el id en wrangler.toml ([[kv_namespaces]] id = "...")

# 2. Token de lectura (el mismo valor irá al .env del repo):
npx wrangler secret put TOKEN
#    → genera uno largo, p. ej.: openssl rand -hex 24

# 3. Subir el worker:
npx wrangler deploy
#    → anota la URL que imprime (https://kit72h-eventos.<subdomain>.workers.dev)
```

## Dejarlo conectado

En el `.env` del repo (y en el `.env` del host donde corra el cron):

```
KIT72H_EVENTOS_URL=https://kit72h-eventos.<subdomain>.workers.dev
KIT72H_EVENTOS_TOKEN=<el mismo token del paso 2>
```

y en `js/analiticas.js` (`CONFIG.worker.url`) la misma URL. Bump de `?v=` con
`scripts/instrumentar-analitica.py` para que las páginas carguen el JS nuevo.

## Comprobación

```bash
curl https://kit72h-eventos.<subdomain>.workers.dev/            # → ok
curl -s -X POST "$URL/e" -H "Origin: https://kit72h.com" \
     -d '{"e":[{"n":"clic-amazon","p":"/kit/kit-apagon/","q":2}]}' -w "%{http_code}"
# → 204
curl -s "$URL/resumen?dias=30" -H "Authorization: Bearer $TOKEN"
# → {"generado":...,"dias":30,"eventos":[{"nombre":"clic-amazon",...}]}
```

## Límites conocidos

- KV free tier: 1.000 writes/día. El navegador agrupa eventos en lotes (1 write
  por POST), así que el techo real está en las mil páginas con evento al día.
- Dos POST simultáneos sobre la misma clave diaria pueden perder un recuento
  (read-modify-write sin transacción): aceptado, el volumen no lo nota.
- `/e` acepta cualquier POST que finja `Origin: kit72h.com`. El único daño
  posible es inflar nuestras propias métricas; no guarda nada más.
