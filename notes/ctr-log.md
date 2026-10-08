# Log de optimizaciones CTR (titles y meta descriptions)

Registro de los cambios de `<title>` / meta description que hace el cron
`kit72h-seo-ctr` (06:30) para maximizar CTR en Google: números, beneficio y
urgencia honesta. Cada entrada: fecha · página · antes → después · motivo.

---

## 2026-10-08 — 11 mejoras (7 títulos de blog + home + zona/fuentes)

**Orden aplicado:** prerender PRIMERO → optimización DESPUÉS → commitear solo lo
optimizado, sin re-prerender encima. Horneado con Playwright
(`~/.hermes/scripts/prerender-full-vm.py`) porque el CLI de Chrome
(`--dump-dom`) sigue colgado en el VM.

**Cambio estructural (para que la optimización NO se revierta):** el horneado
nocturno (05:00) regenera `index.html`, `/fuentes/` y `/zona/` desde
`js/ui.js` (document.title) y `scripts/prerender.py` (meta description), así que
cualquier título editado solo en el HTML se comía al día siguiente — demostrado
con `git log -S 'guía completa 2026' -- index.html`: añadido por el cron CTR y
revertido por el prerender dos veces. Ahora los valores nuevos están también en
`js/ui.js` y en `scripts/prerender.py`, así que el horneado los reproduce.

### Títulos de blog (data/blog.json, bug de `rstrip(")")` reparado en el script)

| Slug | Antes | Después | Motivo |
|---|---|---|---|
| mejor-estufa-sin-luz-apagon | Mejor estufa sin luz: 5 tipos comparados para sobrevivir a un apagón de invierno (80) | Mejor estufa sin luz: 5 tipos para sobrevivir al apagón (2026) (62) | año + más corto (no se trunca) |
| mejor-powerbank-emergencia-capacidad | …comparativa de 4 modelos (y cuántos mAh reales necesitas (2026) (108, paréntesis roto) | Mejor powerbank para kit de emergencia 2026: 4 modelos y mAh reales (67) | paréntesis cerrado, año duplicado fuera, ≤72 |
| bebes-ninos-emergencia-checklist-edades | …checklist por edades (0-3 y 4-12 (2026) (81, roto) | Bebés y niños en una emergencia: checklist por edades 0-3 y 4-12 (2026) (71) | paréntesis cerrado, edades delante |
| recursos-oficiales-emergencia | Los 7 recursos oficiales… (y en papel (2026) (84, roto) | Los 7 recursos oficiales para guardar en el móvil y en papel (2026) (67) | paréntesis cerrado, número «7» delante |
| kit-72h-vs-30-dias | …(spoiler: primero el primero (2026) (79, roto) | Kit 72h o kit de 30 días: cuál te toca (spoiler: el primero) (2026) (67) | paréntesis cerrado |
| coche-kit-emergencia-2026 | Coche y emergencias: lo obligatorio en 2026 y lo que conviene (2026) (68, año duplicado) | Coche y emergencias: lo obligatorio en 2026 y lo que conviene (61) | un solo año |
| botiquin-emergencia-que-llevar | …qué llevar de verdad (y qué sobra (2026) (64, roto) | Botiquín de emergencia: qué llevar de verdad (y qué sobra) (2026) (65) | paréntesis cerrado |

### Páginas estáticas

| Página | Campo | Antes | Después | Motivo |
|---|---|---|---|---|
| Home | title | Kit72h — Kits de emergencia 72 horas: DANA, apagón, coche y más | Kit72h — 20 kits de emergencia 72h: DANA, apagón, coche (2026) | número (20 kits reales) + año + escenarios |
| /zona/ | description | Mapa de tu entorno en España con hospitales… el 112, siempre a mano. (182, se truncaba) | Tu zona: mapa con hospitales, farmacias, refugios y puntos de encuentro cerca de ti. Elige ubicación y radio; el 112, siempre a mano. (132) | keyword delante + cabe entero en el SERP |
| /fuentes/ | title | Fuentes oficiales — Kit72h | Fuentes oficiales — Kit72h: UE, Protección Civil, AEMET y más | keywords de autoridad (61) |
| /fuentes/ | description | Documentos oficiales (Comisión Europea, Protección Civil, DGT)… (110) | Todas las fuentes oficiales de donde se basan los kits: UE, Protección Civil, AEMET, REE, AESAN y más. Actualizadas y verificadas. (130) | más fuentes nombradas + «actualizadas» |

### Arreglos del script `scripts/kit72h-seo-ctr.py`

- `titulo.rstrip(")") + " (2026)"` comía el paréntesis de cierre legítimo y
  generaba títulos rotos con el año duplicado (hasta 108 chars). Ahora: dict
  explícito `BLOG_TITULOS` + cierre de paréntesis sin rstrip + guardia de 72 chars.
- `/zona/` recibía el `HOME_TITLE` (título duplicado con la home): ahora conserva el suyo.
- `HOME_TITLE` nuevo (número + año + escenarios).
