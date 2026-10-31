## 2026-10-30 — 1 mejora
- Comparativa de arrancadores de batería portátiles: "Comparativa de arrancadores de batería portátiles ..." → "Comparativa de arrancadores de batería portátiles para coche..." (completado título incompleto)

---

Registro de los cambios de `<title>` / meta description que hace el cron
`kit72h-seo-ctr` (06:30) para maximizar CTR en Google: números, beneficio y
urgencia honesta. Cada entrada: fecha · página · antes → después · motivo.

## 2026-10-25 06:00 — SEO/CTR run

**Resultado:** 1 mejora aplicada.

**Páginas analizadas:** 85 rutas (20 kits + 62 blogs + 4 auxiliares + home).

**Cambio aplicado:**
- `mejor-kit-solar-portatil-para-casa`: resumen acortado (155→150 car.) para caber en SERP.

**Commit:** 5e478d8 — `feat(seo): optimizar meta tags para CTR (1 mejoras)`

## 2026-10-24

- SEO-CTR: 0 mejoras aplicadas — todos los meta tags ya optimizados. Sin cambios.

---

## 2026-10-23 — 1 mejora: agua-cuanta-y-como desc
- **Página:** /blog/agua-cuanta-y-como/
- **Title:** `Agua para emergencias: cuánto almacenar, cómo guardarla y potabilizarla` → `Agua para emergencias: 3 L/pers/día → 9 L (1), 36 L (familia 4). Bidones, garrafas, pastillas…`
- **Desc:** `3 litros por persona y día: la regla que todo mund...` → `3 litros por persona y día: 9 L en 72 h y 36 L para una familia de 4. Garrafas, bidones, pastillas o filtro: cuánta, dónde y cada cuánto renovarla.`
- **Motivo:** Añadir números concretos (9 L, 36 L) y palabras clave de búsqueda (garrafas, bidones, pastillas, filtro) para mejorar CTR.

## 2026-10-20 — 1 título truncado del post nuevo (cadenas de nieve)

**Orden aplicado:** prerender PRIMERO (`python3 scripts/prerender.py`, **82 rutas,
0 fallos**, 0 `index.html` a 0 bytes, **diff = 0** → el árbol ya estaba horneado y
sincronizado) → optimización DESPUÉS con `analizar_paginas()` (NO `main()`, que
haría commit → generar-seo → prerender → push y revertiría) → commiteado **sin
re-prerender encima**.

**Auditoría de las 82 páginas publicadas:** 0 descuadres JSON↔HTML, 0 descriptions
fuera de 90–155, 0 títulos sin 2026, **1 título fuera de rango** — el único post
nuevo desde la última run (publicado el 20-10).

### Títulos (1)

| Página | Antes | Después | Motivo |
|---|---|---|---|
| blog/mejores-cadenas-para-la-nieve | Mejores cadenas para la nieve 2026: 5 opciones comparadas y cuándo son obligatorias (**83, se trunca**) | Mejores cadenas para la nieve 2026: 5 opciones y cuándo exige la DGT (68) | keyword + año + número delante; «exige la DGT» es la sección 1 del propio artículo (13 menciones de DGT), no un claim inventado |

### Descriptions (0)

Todas en 90–155 con números y gancho; la del post de las cadenas ya era buena
(145: tipos, precio/uso, DGT y errores) → sin cambios.

**Dónde viven los cambios:** `data/blog.json` (fuente de verdad) +
`scripts/kit72h-seo-ctr.py` (`BLOG_TITULOS` con la entrada nueva y comentada, para
que ninguna run futura lo revierta) + **15 ficheros derivados** con la cadena vieja
reemplazada literalmente: la propia página (5 ocurrencias: `<title>`, og:title,
JSON-LD `headline`, breadcrumb y tarjeta), `blog/index.html` (2), interlinking «Sigue
leyendo» de 7 páginas, `index.html`, `feed.xml`, `llms.txt`, `llms-full.txt` y el
generador `scripts/agregar-blog-cadenas.py` — **sin rehornear**.

**Verificación:** 0 residuos del título viejo fuera de `notes/`; `html.parser` sin
fallos en los 15 HTML tocados; `<title>` nuevo (68 chars) presente en su página;
segunda pasada de `analizar_paginas()` → 0 cambios (idempotente); gate **✅ 0
errores** (6 avisos preexistentes).

---

## 2026-10-19 — 1 description recuperada (post DANA) + 5 posts re-horneados

**Orden aplicado:** prerender PRIMERO (`python3 scripts/prerender.py`, headless-shell
del fix `a1766f0`, **81 rutas, 0 fallos**, 0 `index.html` a 0 bytes) → optimización
DESPUÉS con `analizar_paginas()` (NO `main()`, que haría commit → generar-seo →
prerender → push y revertiría) → commiteado **sin re-prerender encima**.

**Hallazgo del prerender (11 errores heredados, gate en rojo al empezar):** la Action
`auto-content` había reescrito 5 posts (`alimentos-emergencia-caducidad-rotacion`,
`botiquin-emergencia-lista-completa`, `mejor-linterna-emergencia-72h`,
`mejor-powerbank-emergencia-capacidad`, `mejor-radio-emergencia-manivela-solar`) con su
plantilla: **sin `id="app"`, sin disclosure y con `styles.css?v=20261001c`** (11 = 5+5+1
del `?v=` inconsistente). El horneado desde `blog.json` los reescribió y el gate pasó a
**0 errores antes de tocar nada del CTR**.

### Títulos (0)

La auditoría da **0 títulos >72** y **0 descriptions fuera de 90-155** en los 73
títulos/66 resúmenes de `kits.json` + `blog.json` y en los `<title>` horneados: nada que
optimizar en títulos (todo lo de las runs del 13-18 sigue aplicado).

### Descriptions (1)

| Página | Antes | Después | Motivo |
|---|---|---|---|
| blog/dana-apagon-primeros-30-minutos | Los primeros 30 minutos de una DANA o un apagón, tramo a tramo: información, casa y decisión, con la secuencia que enseña Protección Civil. (134) | Los primeros 30 minutos deciden casi todo: secuencia de Protección Civil minuto a minuto (0-10 información, 10-20 casa, 20-30 plan) para DANA o apagón. (151) | el consejero re-publicó el post el 18-10 y **pisó la description CTR fijada el 14-10**; la recupera `BLOG_DESCRIPCIONES` (número + estructura real del artículo), snippet completo en vez de 134 chars genéricos |

**Dónde viven los cambios:** `data/blog.json` (fuente de verdad) + **4 ficheros
derivados** con las 6 ocurrencias de la cadena vieja reemplazadas literalmente
(`blog/dana-apagon-primeros-30-minutos/index.html` ×3 — meta, og:description, JSON-LD —,
`blog/index.html`, `llms.txt`, `llms-full.txt`) + los **5 posts re-horneados** del
reparo de auto-content — **sin re-prerender encima de la optimización**. Como el valor
nuevo está en `blog.json`, el horneado nocturno lo REPRODUCE.

**Verificación:** 0 residuos de la cadena vieja (fuera de `notes/`); metas del HTML de
la página DANA cuadrando con `blog.json` (título 62, description 151); `html.parser` sin
errores en los ficheros tocados; **segunda pasada de `analizar_paginas()` → 0 cambios**
(idempotente); 0 `index.html` a 0 bytes; auditoría de longitudes → 0 problemas.

- Gate: ✅ 0 errores (6 avisos preexistentes).

---

## 2026-10-18 — 2 títulos de los posts nuevos (77/79 → 66/72) + 2 descriptions con gancho

**Orden aplicado:** prerender PRIMERO (wrapper `kit72h-prerender-vm.py`, Playwright,
06:33-06:39, **árbol limpio al terminar** → horneado idempotente y 0 páginas a 0
bytes) → optimización DESPUÉS con `analizar_paginas()` (NO `main()`, que haría
commit → generar-seo → prerender → push y revirtiera los títulos) → commiteado
**sin re-prerender encima**.

**Auditoría:** las reglas automáticas sobre el árbol ya existente daban **0 cambios**
(todo lo de las runs anteriores aplicado). Los únicos problemas eran los **dos posts
más recientes** (`mejor-sai-ups-casa-apagon`, publicado el 17-10, y
`generador-solar-emergencia-72h`, rehecho por el consejero), ambos con `<title>` por
encima de 72 (Google los cortaba a media frase) y descriptions planas sin gancho.

### Títulos (2)

| Página | Antes | Después | Motivo |
|---|---|---|---|
| blog/mejor-sai-ups-casa-apagon | Mejor SAI (UPS) para casa y router en un apagón (2026): tipos y VA explicados (**77, se trunca**) | Mejor SAI (UPS) para casa y router: 6 tipos por VA y vatios (2026) (66) | keyword «Mejor SAI (UPS)» + número real (H2 «Los seis tipos, comparados») + año enteros |
| blog/generador-solar-emergencia-72h | Generador solar para emergencias: cuánta autonomía te da y cómo elegirlo (2026) (**79, se trunca**) | Generador solar para emergencias: cuánta autonomía da y 5 errores (2026) (72) | la pregunta del artículo + «5 errores» (H2 6) antes del corte |

### Descriptions (2)

| Página | Antes | Después | Motivo |
|---|---|---|---|
| blog/mejor-sai-ups-casa-apagon | SAI o UPS para casa: seis tipos comparados por VA y vatios, cuánto aguanta router y PC… (130) | ¿Cuánto aguanta tu router y PC en un apagón? 6 SAI comparados por VA y vatios, ganadores por caso y los 5 errores que más se repiten (2026). (143) | gancho de pregunta + las secciones reales («Ganadores por caso», «los cinco errores») |
| blog/generador-solar-emergencia-72h | Generador solar para emergencias: cuánta autonomía te da de verdad, qué carga y qué no… (137) | ¿Cuánta batería necesitas de verdad? Autonomía real en vatios-hora, qué carga y qué no, cuántos paneles y 5 errores al elegir (2026). (133) | la cuenta que abre el artículo (H2 «La cuenta que importa: vatios-hora») como pregunta |

**Dónde viven los cambios:** `data/blog.json` (fuente de verdad) +
`scripts/kit72h-seo-ctr.py` (`BLOG_TITULOS` + `BLOG_DESCRIPCIONES` con los 2 slugs,
para que ninguna run futura los revierta) + **31 ficheros derivados** con las 4
cadenas viejas reemplazadas literalmente (58 reemplazos: las 2 páginas ×5 y ×3
ocurrencias — `<title>`, meta, og:*, JSON-LD, breadcrumb —, el interlinking de 21
posts + 4 kits, `blog/index.html`, `index.html`, `feed.xml`, `llms.txt`,
`llms-full.txt` y el generador `scripts/agregar-blog-sai.py`) — **sin rehornear**.
Como los valores nuevos están en `blog.json`, el horneado nocturno los REPRODUCE.

**Verificación:** 0 residuos de las 4 cadenas viejas (fuera de `notes/`); `<title>`
y meta del HTML de los 2 posts cuadrando con `blog.json`; longitudes 66/72 (títulos)
y 143/133 (descriptions, dentro de 90-155); `html.parser` sin errores en los 32
ficheros tocados; **segunda pasada de `analizar_paginas()` → 0 cambios**
(idempotente); 0 `index.html` a 0 bytes; `tag=ntizar-21` intacto (lo valida el gate).

- Gate: ✅ 0 errores (6 avisos preexistentes).

---

## 2026-10-17 — 2 títulos (post nuevo del extintor + coche) + 9 descriptions de kit <115

**Orden aplicado:** prerender PRIMERO (79 rutas, 0 fallos; árbol limpio al terminar
→ rerun idempotente) → optimización DESPUÉS con `analizar_paginas()` (NO `main()`),
que aplicó 1 arreglo + auditoría manual de longitudes → commiteado **sin re-prerender
encima**. Segunda pasada de `analizar_paginas()` → 0 cambios.

**Automático (1):** `blog/coche-kit-emergencia-2026` — el consejero lo publicó el
16/10 con «Kit de coche para emergencias 2026: obligatorios de la DGT y equipo para
DANA, nieve y averías» (**94**) y las reglas lo devolvieron al fix de `BLOG_TITULOS`
«Coche y emergencias: lo obligatorio en 2026 y lo que conviene» (**61**).

### Títulos (1 automático + 1 manual)

| Página | Antes | Después | Motivo |
|---|---|---|---|
| blog/coche-kit-emergencia-2026 | Kit de coche para emergencias 2026: obligatorios de la DGT y equipo para DANA, nieve y averías (94) | Coche y emergencias: lo obligatorio en 2026 y lo que conviene (61) | automático: el fix ya vivía en `BLOG_TITULOS` y el publish del consejero lo había pisado |
| blog/mejor-extintor-domestico | Mejor extintor doméstico 2026: 6 tipos comparados y dónde colocarlo en casa (75 → 70 con la cola « — Blog Kit72h», en el borde del corte) | Mejor extintor doméstico 2026: 6 tipos y dónde colocarlo (56) | único título >72 del sitio (post nuevo del 17/10): keyword + año + número enteros, y «dónde colocarlo» es el gancho práctico |

### Descriptions (9 de kit — todas <115, malgastaban 40-53 chars de snippet)

| Página | Antes | Después |
|---|---|---|
| kit/kit-comunicacion | (102) | Kit comunicación sin red: walkies PMR446 sin licencia… 6 artículos desde 80 € (148) |
| kit/kit-mayores | (107) | …medicación crónica, ayudas técnicas, anti-caídas… Desde 60 € (153) |
| kit/kit-bebe | (109) | …alimentación sin luz, higiene, abrigo y documentos. Desde 90 € (149) |
| kit/kit-starlink | (110) | …(400-600 € + 50-60 €/mes), router 4G de respaldo (144) |
| kit/kit-incendio | (111) | …respirar sin humo, salir en 10 minutos… Desde 60 € (154) |
| kit/huerto-autosuficiencia | (112) | …semillas, compost, riego autónomo. Desde 50 €; 300 € montado (154) |
| kit/kit-terremoto | (112) | …caídas y vidrios, cortar gas y agua. Luz, botiquín y dinero (145) |
| kit/kit-calor | (113) | …hidratación, frescura y protección solar. Desde 30 € (142) |
| kit/kit-30-dias | (114) | …180 L de agua para 2, despensa, cocinar sin luz. 300-500 € (154) |

Motivo común: **cifras reales de cada ficha** (nº de artículos, coste real del kit,
180 L/30 días) + beneficio concreto, en vez del resumen genérico — sin inventar nada.

**Dónde viven los cambios:** `data/kits.json`, `data/blog.json` y
`scripts/kit72h-seo-ctr.py` (fuente de verdad: `KIT_DESCRIPCIONES` ×9 + nueva entrada
de extintor en `BLOG_TITULOS`) + **30 ficheros derivados** parcheados con replace
literal (las 9 páginas de kit ×4 apariciones, `index.html` ×9, el interlinking de
10 posts, `blog/index.html`, `feed.xml`, `llms.txt` y `llms-full.txt`) — **sin
rehornear**.

**Atención (2ª vez):** el commit de esta run lo barrió de nuevo el cron
`kit72h-ofertas` a las 07:00:52 (`137a19d`, «cambios automáticos») con los cambios
aún sin commitear aquí. El diff son exactamente los **33 ficheros** de esta
optimización (data + script + 30 derivados) y ya estaba en `origin/main`; esta
entrada y la verificación final van en un commit propio.

**Verificación:** 0 residuos de las 11 cadenas viejas (fuera de `notes/`); títulos
JSON ≤72 (máx. 61) y descriptions en 90-155 (las 9 nuevas: 142-154); segunda pasada
de `analizar_paginas()` → 0 (idempotente); gate ✅ **0 errores** (6 avisos
preexistentes); `tag=ntizar-21` intacto (lo valida el gate en todos los enlaces
Amazon).

---

## 2026-10-16 — los 2 últimos títulos >72 + la description cortada del post de CO

**Orden aplicado:** prerender PRIMERO (horneado Playwright completo, 06:43-06:48,
0 páginas a 0 bytes) → optimización DESPUÉS → commit solo de lo optimizado, sin
re-hornear encima. `analizar_paginas()` aplicó 3 mejoras; segunda pasada → 0
(idempotente); gate 0 errores (6 avisos preexistentes).

**Hallazgo del prerender:** el horneado ya NO era idempotente — `inyectar()`
añadía `twitter:image` + favicon inline SIN quitar los existentes (bug del
commit de ofertas `a84b5c3`): salían 78 páginas con las 2 etiquetas duplicadas
(+2 líneas cada una). Se revirtió ese horneado y se arregló `inyectar()`
(`re.sub` previo, igual que con `og:*`, en `scripts/prerender.py`) → la próxima
horneda vuelve a ser cirugía cero.

**Atención:** el commit de esta run lo barrió el cron `kit72h-ofertas` a las
07:00:53 (`d4d3e92`, «cambios automáticos») mientras esta sesión tenía los
cambios sin commitear (pitfall conocido). El contenido es 100% el de esta
optimización (28 ficheros) y la CI acabó en `success`.

### Títulos (2 posts)

| Página | Antes | Después | Motivo |
|---|---|---|---|
| blog/mejor-detector-monoxido-carbono | Mejor detector de monóxido de carbono para casa (2026): 6 tipos comparados y la norma que los valida (100) | Mejor detector de monóxido de carbono: 6 tipos comparados (2026) (64) | el título más largo del sitio: Google cortaba a media frase; keyword + número + año enteros |
| blog/antena-externa-movil-cobertura-montana | Antena externa para móvil: cómo ganar cobertura en montaña y valle (2026) (73) | Antena externa para móvil: cobertura real en montaña y valle (2026) (67) | el único otro >72; «cobertura real» (beneficio) en vez de «cómo ganar» |

### Descriptions (1)

| Página | Antes | Después | Motivo |
|---|---|---|---|
| blog/mejor-detector-monoxido-carbono | …6 tipos comparados con precio orientativo, dónde colocarlo y qué hacer si suena la alarma. (157) | …6 tipos comparados con precio, dónde colocarlo y qué hacer si suena la alarma. (145) | 157 > 155: el snippet cortaba a media palabra; se quita solo «orientativo» |

**Dónde viven los cambios:** `scripts/kit72h-seo-ctr.py` (`BLOG_TITULOS` +
`BLOG_DESCRIPCIONES`, para que ninguna run futura los revierta) + `data/blog.json`
+ **25 ficheros derivados** con las cadenas viejas reemplazadas literalmente (las
2 páginas tocadas — `<title>`, meta, og:*, JSON-LD, breadcrumb —, el listado de
`blog/index.html`, el interlinking de 10 páginas más, `feed.xml`, `index.html`,
`llms.txt`, `llms-full.txt` y `scripts/agregar-blog-detector-co.py`) — **sin
rehornear**.

**Verificación:** 0 residuos de las 3 cadenas viejas (fuera de `notes/`); parser
HTML sin errores; longitudes 64/67 (títulos) y 145 (description); segunda pasada
de `analizar_paginas()` → 0 cambios; gate ✅ 0 errores; CI `Deploy GitHub Pages`
de `d4d3e92` → `success`; producción comprobada con curl (título y description
nuevos en las 2 páginas; `tag=ntizar-21` intacto).

---

## 2026-10-15 — 75 páginas: fin del sufijo de marca en `<title>` + 2 títulos

**Orden aplicado:** el prerender ya había corrido a las 06:29 (lo lanzó antes que
este cron la sesión de la feature OG-image) → optimización DESPUÉS, sin
re-prerender encima. Previo: rebase de los 2 commits de `origin` (auto-content
del jueves 06:00 + pins Pinterest) resolviendo a favor de nuestra versión
horneada en los 5 posts que auto-content pisa (se quedan og:image + disclosure).
`analizar_paginas()` sobre las reglas del script ya daba **0 cambios** (todo lo
de las runs anteriores estaba aplicado); el trabajo real era otro:

**El problema nuevo:** el `<title>` horneado añadía ` — Kit72h` / ` — Blog Kit72h`
al título del JSON (cola de 10-14 chars). La medición de ayer «52/52 ≤72» era
sobre el JSON *sin la cola*: con ella, **49 de 73 páginas se pasaban de 72**
(47 posts + 2 kits; el peor, 91 chars) y Google truncaba el año y el gancho
final del título. Además `feed.xml`/`llms.txt` ya publicaban el título *sin*
cola → la página salía incoherente con el feed.

### Títulos (75 páginas)

| Página | Antes | Después | Motivo |
|---|---|---|---|
| 53 posts de blog | `<título JSON> — Blog Kit72h` (55-91) | `<título JSON>` (47-72) | la cola empujaba Google a cortar el `(2026)` final; ahora el `<title>` = el del feed = el JSON |
| 20 kits | `<título JSON> — Kit72h` (64-74) | `<título JSON>` (54-64) | ídem; el `<title>` queda idéntico al H1 |
| blog/index.html | Blog — Kit72h (13) | Blog de preparación: guías de emergencia 2026 — Kit72h (54) | keyword + año en el índice de sección |
| nevera-portatil-emergencia-72h | Nevera portátil para emergencias: cuánto aguanta sin luz y cuál elegir (2026) (77) | …cuánto aguanta sin luz (2026) (63) | único >72 tras quitar la cola; hook de curiosidad intacto |
| ej. mejor-purificador | Mejor purificador de agua para emergencias (2026): 7 filtros comparados — Blog Kit72h (85) | …comparados (71) | número + año enteros en el snippet |

**Dónde viven los cambios (sobreviven al horneado):**
- `js/ui.js` — `document.title` de kit/blog/índice: es lo que el prerender
  vuelca al HTML, así que la próxima hornada lo REPRODUCE, no lo revierte.
- `scripts/generar-blog-home.py` (plantilla del índice) y
  `scripts/kit72h-comparador.py` (comparativas futuras) alineados.
- `scripts/kit72h-seo-ctr.py` → `BLOG_TITULOS` fija el título nuevo de la nevera.
- Sustitución literal SIN rehornear en los 75 HTML + `data/blog.json` +
  `feed.xml` + `llms.txt` + `llms-full.txt`.
- **`ui.js?v` 20261008a → 20261015a en las 77 páginas publicadas** (solo se
  tocó ui.js; `styles.css` y `main.js` intactos, sin bump).
- **`og:title` MANTIENE la cola** (`scripts/prerender.py`): en tarjetas
  sociales la marca ayuda y ese fichero pertenecía a otra sesión; cosmético,
  no afecta al SERP.

**Verificación (receipts):**
- `analizar_paginas()` 2ª pasada → **0 cambios** (idempotente).
- Gate: ✅ **0 errores** (6 avisos preexistentes), antes y después de commitear.
- 0 residuos de la cadena vieja (fuera de `notes/`), 0 `<title>` con cola en
  kit/posts, 0 títulos JSON >72, `html.parser` sin rotos, `ui.js?v` única 77/77.
- Commits: `a84b5c3` (feature OG-image ajena, commiteada por el cron ofertas
  cuando su sesión murió sin commitear; la subí yo tras el rebase) +
  **`72b6a13`** (este cambio). Actions de ambos: `conclusion: success`.
- En vivo: `/kit/kit-basico-72h/` → `<title>Kit 72h Básico: 16 esenciales de la UE (2026)</title>`,
  `/blog/nevera-portatil-emergencia-72h/` → título nuevo, `/blog/` → título de
  índice nuevo, `js/ui.js?v=20261015a` → 200, `assets/og-kit72h.png` → 200.

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

---

## Run 2026-10-12 (06:34 UTC) — horneado primero, CTR después

**Orden ejecutado (el que no revierte títulos):** horneado Playwright completo
(`prerender_playwright.py`, 73 rutas, 0 fallos, 0 ficheros a 0 bytes) →
`analizar_paginas()` de `scripts/kit72h-seo-ctr.py` → sincronización de metas
de la ficha afectada → gate → commit solo con lo optimizado (sin rehornear
encima).

**Cambio de la run — 1 página:**

| Página | Campo | Antes | Después | Motivo |
|---|---|---|---|---|
| `/blog/panel-solar-portatil-72h-emergencia/` | description | …comparativa por escenario y los cinco errores que lo dejan inútil. Enlaces y fuentes oficiales. (179, Google lo cortaba) | Panel solar portátil para emergencias: tipos, vatios reales y comparativa por escenario, con 5 errores que lo dejan inútil. Fuentes oficiales. (142) | cabía entero en el snippet, número (5) + beneficio + autoridad («fuentes oficiales»); la regla genérica de truncado dejaba «…inútil. E…» cortado a media palabra, así que se fijó en `BLOG_DESCRIPCIONES` |

**Detalles:**
- La optimización se hizo DESPUÉS del horneado y los metas del HTML horneado se
  igualaron a `data/blog.json` a mano (meta + og:description + JSON-LD
  BlogPosting) para que el cambio llegue a producción hoy y lo reproduzca el
  próximo horneado nocturno, sin rehornear encima.
- Títulos: sin cambios — todos los títulos ya estaban optimizados y espejados en
  `js/ui.js` / `scripts/prerender.py` (ningún revert en el horneado).
- Trabajo pendiente de sesiones anteriores commiteado aparte antes de hornear:
  `ca475f0` (ficha verificada del forro polar) y `b302d24` (analítica: beacon en
  75 páginas, panel `/analiticas/`, cron, allowlist de `pages.yml`, robots).
- Gate: ✅ 0 errores (6 avisos preexistentes).

---

## Run 2026-10-13 (06:37 UTC) — horneado primero, 3 títulos + 21 descriptions

**Orden ejecutado (el que no revierte títulos):** horneado Playwright completo
con el wrapper del cron (`kit72h-prerender-vm.py`, 457 s, exit 0) →
`analizar_paginas()` de `scripts/kit72h-seo-ctr.py` (**0 mejoras automáticas**:
las reglas genéricas ya estaban aplicadas en todo el árbol) → optimización
manual → gate → commit SOLO con lo optimizado, **sin rehornear encima**.

**Sanidad del horneado (el wrapper trunca el resumen de rutas):** las 75
páginas publicadas tienen `mtime ≥ 06:37`, es decir, **0 rutas fallidas**; árbol
limpio tras el horneado (idempotente), 0 ficheros a 0 bytes.

**Cambio 1 — 3 títulos** (los únicos que no pasaban la auditoría CTR):

| Página | Antes | Después | Motivo |
|---|---|---|---|
| `/blog/nevada-en-casa-que-necesito/` | Nevada en casa: qué necesito para aguantar los días de nieve sin luz (68, **sin número y sin año**) | Nevada en casa: 8 claves para aguantar los días sin luz (2026) (62) | post del editor nocturno; «8 claves» = los 8 H2 numerados del artículo |
| `/blog/panel-solar-portatil-72h-emergencia/` | Panel solar portátil para emergencias: tipos, potencia real y cómo elegirlo (2026) (**82** → Google lo cortaba a media palabra) | Panel solar portátil para emergencias: 3 tipos y 5 errores (2026) (65) | números exactos del artículo («Los tres tipos de panel», «Los cinco errores») |
| `/blog/botiquin-emergencia-lista-completa/` | El botiquín de emergencia para todo hogar (2026) (48, genérico, sin número) | Botiquín de emergencia completo: 15 objetos que no pueden faltar (2026) (71) | «15 objetos» sale del H2 «El botiquín base: 15 objetos no negociables» |

**Cambio 2 — 21 de 51 descriptions cortadas a media palabra**: la Regla 2 vieja
hacía `resumen[:152] + "..."`, y 21 posts acababan en «…messenger s...»,
«…Guía práctica con el marc...» o «…por menos de ...». Cada una se reescribió
con el **texto original recuperado de la historia de git**
(`git show 13ed362:data/blog.json`) y recortado limpio a ≤155 chars sin puntos
suspensivos. Dos ejemplos:

| Página | Antes | Después |
|---|---|---|
| `/blog/radiocomunicacion-pmr446-walkie-talkies/` | …Sin licencia, por menos de **…** (155, cortado) | Cuando caen las redes móviles, la PMR446 sigue: sin licencia, por menos de 40 € el par y legal en toda España. Cómo elegirla, según Protección Civil. (149) |
| `/blog/plan-familiar-de-emergencia/` | …La diferencia no fue la mo**…** (155, cortado) | Dos familias, el mismo aviso, resultados opuestos: una se reencontró en dos horas, la otra tardó tres días. La diferencia no fue la mochila: fue el plan. (153) |

Balance: **51/51 descriptions en 90–155 chars y 0 terminando en `...`**;
**0 títulos de blog por encima de 72 chars**.

**Mecánica:** reemplazo literal de las 24 cadenas (3 títulos + 21
descriptions) en `data/blog.json` y en los 54 ficheros derivados que las
repiten — páginas horneadas, interlinking «Sigue leyendo», `blog/index.html`,
`index.html`, `feed.xml`, `llms.txt`, `llms-full.txt` y los generadores
`scripts/agregar-blog-nevada.py` y `scripts/generar-articulos.py` — **sin
rehornear** (el HTML queda igual que lo produciría el próximo horneado
nocturno, porque la fuente `blog.json` ya lleva los valores nuevos).
Verificación: 24/24 cadenas viejas fuera del árbol, JSON-LD parseando en todas
las páginas tocadas, `html.parser` sin errores y gate en verde.

**Regla raíz corregida en `scripts/kit72h-seo-ctr.py`:** Regla 2 ahora corta
en límite de palabra y **sin `...`** (así el próximo corte no vuelve a dejar
snippets a media palabra), y los 3 títulos nuevos se fijan en `BLOG_TITULOS`
para que ninguna run futura los revierta.

**Fuera de alcance a propósito:** `data/pins-generados.json` y `pintout/`
(artefactos de Pinterest, se regeneran con su cron) y `notes/` (historial).

- Gate: ✅ 0 errores (6 avisos preexistentes).

---

## Run 2026-10-14 (06:30 UTC) — horneado primero, 2 títulos + 4 descriptions

**Orden aplicado:** prerender PRIMERO (**76 rutas, 0 fallos**; el árbol quedó
limpio: la rerun resultó idempotente, 0 desfases JSON↔HTML) → optimización
DESPUÉS con `analizar_paginas()` (NO `main()`, que haría commit → generar-seo →
prerender → push) → commitear solo lo optimizado, **sin re-prerender encima**.

**Auditoría:** las reglas automáticas ya no encontraban nada (0 cambios: los 52
títulos llevan año y ninguna description se pasa de 155). La revisión manual
encontró **6 mejoras reales**: 2 títulos que Google truncaba por encima de 80
chars y 4 descriptions de 89–117 chars, que malgastaban el snippet.

### Títulos (2)

| Página | Antes | Después | Motivo |
|---|---|---|---|
| blog/generador-ruido-normativa-comunidad | Generador y ruido en la comunidad: qué dice la normativa y cuántos dB te toleran (2026) (**87, se trunca**) | Generador y ruido en la comunidad: cuántos dB te toleran (2026) (63) | ≤70 con la keyword intacta y el gancho numérico (dB) antes del corte |
| blog/mejor-sim-datos-emergencia-cobertura | Mejor SIM de datos de emergencia: qué operadora te salva cuando se va la luz (2026) (**83, se trunca**) | Mejor SIM de datos de emergencia (2026): qué operadora te salva (63) | año al medio, «qué operadora te salva» cabe entero en el snippet |

### Descriptions (4)

| Página | Antes | Después | Motivo |
|---|---|---|---|
| blog/dana-apagon-primeros-30-minutos | Las primeras decisiones son las que importan. Una guía directa… (**108**) | Los primeros 30 minutos deciden casi todo: secuencia de Protección Civil minuto a minuto (0-10 información, 10-20 casa, 20-30 plan)… (151) | número + estructura real del artículo |
| blog/como-montar-tu-kit-72h | La UE pide a cada hogar autonomía de 72 horas. Esto es lo que necesitas… (**114**) | Desde marzo de 2025 la UE recomienda 72 h de autonomía: agua, comida, luz y botiquín en una mochila por 100-150 €… (147) | fecha + coste concreto (100-150 €) del propio texto |
| blog/agua-cuanta-y-como | 3 litros por persona y día es la cifra oficial, pero ¿en qué?… (**117**) | 3 litros por persona y día: 9 L en 72 h y 36 L para una familia de 4. Garrafas, bidones, pastillas o filtro… (147) | la cuenta completa (9 L / 36 L), que es el gancho del artículo |
| kit/kit-kit-profesional | Kit profesional: energía y autonomía total con paneles solares… (**89**) | Kit profesional: 800 W de placas, baterías LFP de 19,2 kWh, SAI y Starlink para pasar un apagón largo sin cortes… (135) | datos reales de la ficha PRO (2×400 W, 2×9,6 kWh) en vez de «autonomía total» |

**Dónde viven los cambios:** `data/blog.json` y `data/kits.json` (fuente de
verdad) + `scripts/kit72h-seo-ctr.py` (`BLOG_TITULOS`, `BLOG_DESCRIPCIONES` y
`KIT_DESCRIPCIONES` actualizados, para que ninguna run futura los revierta) +
**55 ficheros derivados** con la cadena vieja reemplazada literalmente: las 6
páginas tocadas (4-5 ocurrencias cada una: `<title>`, meta, og:*, JSON-LD
`headline`/`description` y breadcrumb), el interlinking «Sigue leyendo» de otras
40 páginas, `blog/index.html` (7), `index.html`, `feed.xml` (2), `llms.txt` y
`llms-full.txt` (6 cada uno) y el generador
`scripts/agregar-blog-generador-ruido.py` — **sin rehornear**.

**Verificación:** 0 residuos de las 6 cadenas viejas (fuera de `notes/`); 72
páginas con `<title>`, meta description, og:title, og:description y JSON-LD
cuadrando con el JSON; `html.parser` sin errores; **segunda pasada de
`analizar_paginas()` → 0 cambios** (idempotente); 52/52 títulos ≤72 chars y
todas las descriptions en 90–155.

- Gate: ✅ 0 errores (6 avisos preexistentes).
## 2026-10-22 07:30 — SEO/CTR run

**Resultado:** 0 mejoras (todos los meta tags ya optimizados). La última carrera (5c35ab8) aplicó 2 mejoras al botiquín.

**Páginas analizadas:** 82 rutas (20 kits + 58 blogs + 4 auxiliares + home).

**Sin cambios necesarios hoy.**

## 2026-10-25 06:00 — SEO/CTR run

**Resultado:** 1 mejora aplicada.

**Páginas analizadas:** 85 rutas (20 kits + 62 blogs + 4 auxiliares + home).

**Cambio aplicado:**
- : resumen acortado para caber en SERP (155→150 car.).

**Commit:** 5e478d8 — 

## 2026-10-26 06:03 — SEO/CTR run

**Resultado:** 2 mejoras aplicadas (resumens acortados a ≤150 car.).

**Páginas analizadas:** 85 rutas (20 kits + 62 blogs + 4 auxiliares + home).

**Cambios aplicados:**
- `blog/cuanta-agua-comida-reserva-emergencia-casa`: resumen 155→150 car. para caber en SERP.
- `blog/mejor-bomba-achuite-inundacion`: resumen 155→150 car. para caber en SERP.

**Commit:** 68e2a08 — `feat(seo): optimizar meta tags para CTR (2 mejoras)`
**Push:** ✅ origin/main

## 2026-10-31 06:00 — SEO/CTR run

**Resultado:** 1 mejora aplicada (description de un blog).

**Páginas analizadas:** 85 rutas (20 kits + 62 blogs + 4 auxiliares + home).

**Cambio aplicado:**
- `blog/paso-paso-mochila-emergencia`: description acortada para caber en SERP.

**Commit:** faae574 — `feat(seo): optimizar meta tags para CTR (1 mejoras)`
**Push:** ✅ origin/main
