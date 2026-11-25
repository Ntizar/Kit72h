# Alianza con Phaenyx Alert (Kit72h) — 2026-11-25

## Qué se firmó
Grégory Payotte (Phaenyx Alert, app.phaenyx.com) abrió su programa de tiendas asociadas: 3 plazas por región. Kit72h entró como una de ellas.

- **Código de tienda:** `KT72H` → activa el plan Familia gratis 1 año (valor 19 US$).
- **Enlace de activación:** https://app.phaenyx.com/?code=KT72H
- **Qué recibe el lector:** alertas oficiales para sus lugares (casa, pueblo, colegio), hasta 3 personas y botón «Estoy bien».
- **Qué recibe Kit72h:** logo y botón «Tienda» dentro de la app, estadísticas agregadas de activaciones (sin datos personales), descuento propio (PHAENYX10 de ejemplo).
- **Panel de estadísticas:** https://app.phaenyx.com/partenaire/stats/80ccb0c130de7bc4d2f5b9ab5b0ed6b1628714bbabd84ee5
- **Pendiente con Grégory:** enviarle logo (PNG/SVG). La app está solo en inglés y francés de momento.

## Qué se publicó (commit 395037dc)
1. **Banner en la portada** (`js/ui.js` → sección `.sec.phaenyx`), paleta medida de la app: fondo `#0E1013`, panel `#16191E`, naranja `#E8823A`, oro `#D6A64A`. Copy en 6 idiomas en `data/i18n/ui/*.json` con claves `phaenyx.*`. CSS en `css/styles.css`.
2. **Guía** `/blog/phaenyx-alert-avisos-oficiales/` en es/en/de/fr/it/nl (`data/blog.json` + `data/i18n/contenido/*.json`), con fuentes oficiales (DG ECHO y Protección Civil) y nota de transparencia.
3. SEO regenerado (sitemap, feed, llms) y token CSS `20261125a`.

## Lecciones operativas
- El prerender completo en Windows tarda >600 s: lanzarlo con `background=true` o por mercados con `--solo <mercado>`; si se corta, repetir solo el mercado incompleto.
- Las claves i18n del banner viven en `data/i18n/ui/<lang>.json` (no en `contenido`), y el blog en `data/i18n/contenido/<lang>.json`; `en-gb` y `en-us` comparten el fichero `en`.
