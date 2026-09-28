# 2026-09-28 — Rediseño táctico + dominio vivo

## Qué se hizo
- Rediseño completo "táctico" (Anton + IBM Plex Mono, negro #0E0C09 / crema #F1EBDF, acentos #D14B27/#EFA02B/#A9D6E5, radius 0, bordes 2px, sin sombras): hero con atardecer flat (clip-path), tickers, plan 00:00→72H, watermarks. Commit 94bc0ce, deploy verde.
- Footer sin "Hecho con ❤️" (eliminado .attribution).
- Checklist marcable con barra de progreso (% sobre los esenciales con ASIN) y botón **cesta Amazon en 1 clic**: `https://www.amazon.es/gp/aws/cart/add.html?ASIN.1=...&Quantity.1=1&...&tag=nti0c8-21` — un ASIN por línea, sin repetir; abre en pestaña nueva.
- kit72h.com responde 200 end-to-end (CF proxied → GitHub Pages, SSL Full, edge LE). Enforce HTTPS activado por API.

## Lecciones (para no repetir)
- **Watermark absoluto sin padre position:relative** = se posiciona contra el viewport, escapa del overflow:hidden y genera scroll horizontal (10px). Fix: `.sec{position:relative;overflow:hidden}`.
- **Chrome headless --window-size clampa a 500px de ancho** → NO sirve para auditar móvil; el dump-dom mostraba 0 overflow y era falso negativo. Vía correcta: navegador real + `Emulation.setDeviceMetricsOverride` (390px) y medir `scrollWidth` + bisección de culpables ocultando elementos.
- La auditoría por captura puede mentir (capture_screenshot pisa siempre el mismo tmp/shot.png); guardar copia con shutil tras cada captura.
- El arnés de humo (scratch/smoke2.py) quedó como patrón: 13 asserts DOM + capturas.
- Vision backend puede caerse por timeout: verificar fuentes con `document.fonts.check` y estilos con getComputedStyle por JS.

## Pendiente (roadmap con David)
- GitHub privado (viable solo con GitHub Pro o migrando a Cloudflare Pages; el repo está limpio de secretos).
- Crons v2: más kits y blog, buscador de ofertas del día, top de ventas por clics (necesita registro de clics), revisión de comentarios Amazon y variantes hombre/mujer/unisex.
