# 2026-09-28 — SEO máximo: URLs reales + prerender + crons v2

## Arquitectura SEO (la grande)
- De SPA con #hash (invisible para Google/LLMs) a **URLs reales estáticas**: /kit/<slug>/, /blog/<slug>/, /blog/, /fuentes/.
- `scripts/prerender.py`: servidor con fallback SPA + Chrome headless por ruta (perfil fresco) → HTML horneado con asserts de contenido, canonical/OG **siempre reemplazados por ruta** (no heredar los de home), JSON-LD inyectado sin duplicar (Article/BlogPosting + Breadcrumb; el shell conserva WebSite/FAQ/ItemList). 45 rutas.
- `scripts/generar-seo.py` v2: sitemap con URLs reales (0 hashes), feed.xml RSS, llms.txt con URLs completas, llms-full.txt (188 KB texto plano).
- Assets y fetches con rutas ABSOLUTAS (`/data/...`, `/js/...`) — sin eso las rutas anidadas no cargan nada.
- `.gitignore`: `*.html` global → `/*.html` (si no, las páginas generadas no se commiteaban).
- CI (deploy-cloudflare.yml): generar-seo + prerender antes de wrangler.
- `_headers` (CF Pages): CORS `*` en /data, /llms*, /feed, sitemap; caché 1d en assets.
- Sin "David Antizar" en ningún dato/render (autor eliminado de blog.json, blog-nuevas, attribution de kits.json, JSON-LD author).

## Bugs cazados en la travesía (lecciones)
1. **Fetches/assets relativos** → rutas anidadas servían shell vacío (fetch 404 → render nunca corría).
2. **Ficheros prerenderizados envenenados**: los primeros generados (rotos) se servían en runs siguientes en vez del shell; se limpia con `rm -rf kit blog fuentes` si algo huele raro.
3. **Perfil Chrome por defecto cacheaba** ui.js viejo → perfil fresco por ruta obligatorio.
4. **canonical heredado de home**: el shell ya traía canonical/og de home y el inyector los respetaba → reemplazo forzoso.

## Crons v2 (Hermes)
- `kit72h-editor` (4:30, deepseek): prompt nuevo — calidad, URLs reales en enlaces, `<table>` semántica (wrapper .tabla-scroll), sin campo autor, prerender+generar-seo obligatorios antes del push, css/js/index sagrados.
- `kit72h-revision-urls`: semanal lunes 9:00 (antes mensual) + prerender en el flujo.
- `kit72h-vigilante`: prompt nuevo (kit72h.com) pero **pausado** hasta 01/10 (allowance 402).
- **`kit72h-seo-audit` NUEVO** (323767d865e7): script puro, diario 6:00, Telegram. Audita sitemap↔ficheros, canonical, JSON-LD, robots IA, feed/llms, ausencia de autor personal y frescura del prerender.
- Tablas del blog: envueltas en `.tabla-scroll` (scroll interno, página intacta — medido 520/346 a 390px).

## Pendiente (David)
- DNS: apuntar kit72h.com + www a kit72h.pages.dev (token sin Zone:DNS:Edit).
- Token CF con Pages edit para que la action de deploy funcione (error 10000 desde runners).
