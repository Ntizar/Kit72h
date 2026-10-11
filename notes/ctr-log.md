# Log de optimizaciones CTR (titles y meta descriptions)

Registro de los cambios de `<title>` / meta description que hace el cron
`kit72h-seo-ctr` (06:30) para maximizar CTR en Google: números, beneficio y
urgencia honesta. Cada entrada: fecha · página · antes → después · motivo.

---

## 2026-10-11 — 12 mejoras (6 títulos + 6 descriptions)

**Orden aplicado:** prerender PRIMERO → optimización DESPUÉS → commitear solo lo
optimizado, sin re-prerender encima (prompt del cron). El prerender previo salió
**73 rutas, 0 fallos** y con el árbol ya sincronizado (0 desfases JSON↔HTML), así
que no dejó nada pendiente. Optimización con `analizar_paginas()` a pelo (NO
`main()`, que haría commit → generar-seo → prerender → push).

**Dónde viven los cambios:** `data/kits.json`, `data/blog.json` (fuente de verdad)
y `index.html`. La home ya sirve la description nueva en producción; los títulos
de kits y los de blog los hornea el ciclo nocturno (`kit72h-editor`, 04:30, o el
prerender de la propia run de mañana) — el horneado los REPRODUCE porque salen de
los JSON, no los revierte.

### Títulos (6)

| Página | Antes | Después | Motivo |
|---|---|---|---|
| kit-dana | Kit DANA / Inundación: 14 artículos para proteger tu hogar (58) | …tu hogar (2026) (65) | año |
| huerto-autosuficiencia | Huerto Autosuficiente: 13 herramientas para autoprovisión (57) | …autoprovisión (2026) (64) | año |
| kit-frio | Kit Frío/Invierno: 27 artículos para sobrevivir al frío (55) | …al frío (2026) (62) | año |
| kit-electricidad | Kit Electricidad: energía sin red cuando se va la luz (2026) (60) | Kit Electricidad: 10 artículos para tener luz sin red (2026) (60) | número real (10 items) > genérico |
| starlink-emergencia-72h-conectividad | Starlink en un apagón: cómo montarlo, alimentarlo y cuándo merece la pena (2026) (**80, se trunca**) | Starlink en un apagón: montarlo, alimentarlo y si merece la pena (2026) (71) | ≤72, keyword delante |
| kit-emergencia-bebe-familia | Kit de emergencia para bebé: qué necesitas en casa (lista por bloques) (70, sin año) | Kit de emergencia para bebé: qué llevar en casa por bloques (2026) (66) | año + ≤72 |

### Descriptions (6)

| Página | Antes | Después | Motivo |
|---|---|---|---|
| botiquin-emergencia-lista-completa | El botiquín de emergencia para todo hogar (**41**) | Qué lleva un botiquín de emergencia y qué sobra: lista por bloques… 8 errores que lo dejan inútil. (140) | snippet malgastado → beneficio + número |
| mejor-linterna-emergencia-72h | Las 7 mejores linternas… (**53**) | 7 linternas comparadas por autonomía real (lúmenes y horas), precio y resistencia… (137) | ídem |
| mejor-radio-emergencia-manivela-solar | La mejor radio… (**55**) | Radios con manivela y panel solar comparadas: autonomía sin pilas, alcance, cargador móvil… (133) | ídem |
| alimentos-emergencia-caducidad-rotacion | Alimentos para emergencias… (**52**) | Qué alimentos aguantan años y cuáles caducan pronto: rotación por fecha… (132) | ídem |
| kit-emergencia-bebe-familia | Qué guardar en casa para un bebé… (**157, se trunca**) | …agua segura, fórmula, higiene sin agua, papeles y frío. Lista por bloques. (146) | ≤155 |
| Home (index.html) | Kits de emergencia 72 horas basados en las recomendaciones oficiales… (140) | 20 kits de emergencia de 72 horas con checklist marcable y cesta en 1 clic: DANA, apagón, coche, hogar y montaña. (150) | número + beneficio concreto + escenarios. Sobrevive al horneado: `prerender` usa `reemplazar_desc=False` en `/` |

### Script `scripts/kit72h-seo-ctr.py`

- Dict nuevo **`BLOG_DESCRIPCIONES`** (por slug, manda sobre la regla genérica de
  truncado) + regla 0c en `aplicar_mejoras_blog()`.
- `BLOG_TITULOS`: + starlink (80→71), + kit-emergencia-bebe-familia (año).
- `KIT_TITULOS`: año en kit-dana / huerto / kit-frio y regla nueva para
  `kit-electricidad` (kit nuevo que no tenía ninguna — el sondeo lo marcaba
  «SIN-REGLA»).
- El script sigue siendo idempotente: mañana reportará 0 mejoras.

### Verificación (2026-10-11 06:50 UTC)

- Prerender previo: 73 rutas, 0 fallos, 0 `index.html` a 0 bytes, árbol sin
  cambios (HEAD ya estaba horneado).
- Gate `verificar-sitio.py`: ✅ 0 errores (6 avisos preexistentes).

---

## 2026-10-09 — 23 títulos de blog acortados (≤72 chars)

**Orden aplicado:** prerender PRIMERO → optimización DESPUÉS → re-horneado
(final, para que el HTML publicado lleve los títulos nuevos — están en
`data/blog.json`, la fuente de verdad, así que el horneado LOS REPRODUCE, no
los revierte) → gate → commit. Horneado con `prerender-full-vm.py` (Playwright).

**Situación:** `kit72h-seo-ctr.py` reporta 0 mejoras de sus reglas (todo ya
optimizado por la ronda del 08), pero 23 de 46 entradas de blog tenían
`<title>` de **74–111 chars**: Google los trunca en el SERP (~60-70 visibles),
perdiendo el beneficio/keyword final. Keyword delante, año dentro, todo ≤72.

### Títulos de blog (data/blog.json)

| Slug | Antes | Después |
|---|---|---|
| salud-mental-y-sueno-en-una-emergencia | …cómo sostener la cabeza (y a los tuyos) cuando todo se desordena (2026) (111) | Salud mental y sueño en una emergencia: cómo sostenerse (2026) (62) |
| vestirse-por-capas-ropa-emergencia-frio | …la técnica que marca la diferencia entre una noche de frío y un riesgo mortal (2026) (104) | Vestirse por capas: la técnica que evita el frío mortal (2026) (62) |
| panel-solar-portatil-realista-quantos-watts-urgente | Panel solar portátil realista: cuántos watts de verdad necesitas para una emergencia (2026) (91) | Panel solar portátil: cuántos watts necesitas de verdad (2026) (62) |
| el-conocimiento-dartnell | "El Conocimiento" de Lewis Dartnell: el manual para reconstruir el mundo desde cero (2026) (90) | «El Conocimiento» de Dartnell: reconstruir el mundo (2026) (58) |
| kit-emergencia-trabajo-oficina | Kit de emergencia en el trabajo: qué guardar en el cajón y cómo salir del edificio (2026) (89) | Kit de emergencia en el trabajo: qué guardar y qué hacer (2026) (63) |
| kit-emergencia-50-euros | Prepararse con 50 euros: el kit de emergencia que ya tienes casi entero en casa (2026) (86) | Kit de emergencia por 50 €: casi todo ya está en casa (2026) (60) |
| medicion-cronica-personas-dependientes | Medicación crónica y personas dependientes: cómo asegurar 2-4 semanas sin farmacia (2026) (89) | Medicación crónica sin farmacia: 2-4 semanas aseguradas (2026) (62) |
| + 16 más | 74–85 chars | 55–68 chars |

*(16 restantes: nevera-portatil, mejor-sim-datos, mejor-router-4g, generador-solar,
conectividad, antena-externa, conservar-comida, seguridad-pasiva, pmr446,
volver-a-casa, vivir-solo, plan-familiar, comer-sin-luz, temperatura,
huerto, carpeta-documentos — todos keyword delante + (2026) + ≤72.)*

### Script `scripts/kit72h-seo-ctr.py`

- Los 23 títulos nuevos añadidos al dict `BLOG_TITULOS` (mandan sobre las
  reglas genéricas): el cron de las 06:30 es idempotente sobre ellos y no
  vuelve a tocarlos.

### Verificación (2026-10-09)

- `prerender-full-vm.py`: 70 rutas, 0 fallos, 0 `index.html` a 0 bytes.
- Gate `verificar-sitio.py`: ✅ 0 errores (6 avisos preexistentes).

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

### Verificación (2026-10-08 07:04 UTC)

- Gate `scripts/verificar-sitio.py`: ✅ 0 errores (6 avisos preexistentes).
- Push `51ddf69` + `bf69a58` → run de `pages.yml` **completed / success** (el gate bloquea el deploy, así que el verde = desplegado).
- Producción verificada con curl: home, `/fuentes/`, `/zona/` y los 7 posts de blog sirven los títulos/descriptions nuevos; `styles.css?v=20261008a` en la home.
- Rebase rutinario contra `eac03ad` (Action `auto-content.yml`): sus 5 páginas generadas traían `?v=20261001c` (versión obsoleta), 8 KB frente a 24 KB del horneado desde `blog.json`, y **sin `disclosure`** con enlaces `tag=ntizar-21` (el gate daría ERROR). Se resolvió a favor de la versión horneada desde la fuente de verdad. `git log -S` confirma que su HTML no está en `blog.json`: el horneado nocturno lo reescribe igual.
