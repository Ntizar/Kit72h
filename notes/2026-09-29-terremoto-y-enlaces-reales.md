# 2026-09-29 — Entrada del terremoto y fin de los enlaces #legacy en el blog

## Nueva entrada
`/blog/terremoto-espana-que-hacer/` — «Terremoto en España: qué hacer antes, durante y
después». 1.183 palabras, resumen de 142 caracteres, tabla semántica de sismicidad y
10 fuentes (Protección Civil, IGN, BOE, Comisión Europea, IAGPDS-UGR, RTVE, SINC).

- **Gancho con demanda real**: la serie sísmica de Granada del 14-18 de agosto de 2026
  (4,8 el 15 y otro 4,8 el 18 a las 10:37, epicentro al NO de Gójar; desalojo preventivo
  de 371 viviendas / 600 personas en Las Gabias; 3 heridos leves; Alhambra cerrada).
  Cifras confirmadas en tres fuentes independientes (RTVE, ABC, COPE/UGR: 1.214 eventos
  en la red del IAGPDS hasta las 11:30 del 18/08).
- **Datos IGN verificados del PDF oficial** (`SIS-Tablas_estadisticas_PIberica.pdf`,
  descargado y leído con `pdftotext`, que está instalado en el entorno): Península,
  totales 2021-2025 = 11.329 / 8.843 / 5.099 / 4.916 / 5.729; «sentidos» 806 / 308 / 198 /
  203 / 182; por encima de M4 = 25 / 23 / 6 / 3 / 7. Ojo: la tabla es **solo Península**.
- Cita literal de la guía de riesgo sísmico de la DGPCE: «No existe actualmente ningún
  método capaz de predecir el tiempo, lugar y magnitud de un terremoto».
- La norma es **NCSE-02, Real Decreto 997/2002** (BOE 11/10/2002, id BOE-A-2002-19687) —
  no el «RD 365/2002», que es otro tema; verificar siempre el BOE antes de citar.

## Migración de enlaces #legacy (data/blog.json)
86 enlaces del cuerpo pasan de hash a URL real: 62 `#kit/`, 22 `#blog/`, 1 `#fuentes`
y 1 `href="#"` («kits» → `/`). Dos casos especiales:
- `huerto-emergencia-semillas-germinados` se enlazaba a sí misma → `/blog/`.
- `conservar-comida-sin-nevera-ni-frio` dependía solo del fallback de `blog.porKit`
  (`cuerpo.includes('#kit/…')`) → ahora `kit-hogar` está en su `kits_relacionados`.

**Regla para quien añada contenido:** tras migrar, revisar `kits_relacionados`: el
fallback de `porKit` solo detecta `#kit/<slug>`, no `/kit/<slug>/`, así que un kit
enlazado solo en el cuerpo deja de aparecer en la ficha del kit.

## Hallazgo pendiente (js sagrado, no tocado)
`js/ui.js:298` («Sigue leyendo» de cada entrada) y `js/ui.js:374` (guías relacionadas de
cada kit) generan `href="#blog/<slug>"`. En las páginas prerenderizadas `vistaDesdeHash()`
da prioridad al `pathname` sobre el hash, así que al hacer clic **no navega**: re-renderiza
la página actual y sube al principio. Hay 151 de esos enlaces en el HTML generado.
Mismo caso `js/ui.js:11` (`irA` con `location.hash`) y `js/blog.js:28`.
El fix es de una línea por sitio (`/blog/${slug}/`), pero `js/` es sagrado: va al próximo
rediseño.

También quedan plantillas con `#hash` en los helpers antiguos
`scripts/agregar-blog-mental.py` y `scripts/agregar-blog-pmr.py`: si se reutilizan,
reintroducen enlaces legacy.

## Verificaciones de la noche
- `python scripts/generar-seo.py` → 50 URLs reales, 31 entradas en llms.txt, 214 KB de
  llms-full, feed con el nuevo item.
- `python scripts/prerender.py` → **50 rutas generadas, 0 fallos**.
- `grep -c "David Antizar" data/ js/ index.html` → 0; también 0 en `blog/` y `kit/`.
- Nuevas URLs en el sitemap: los cuatro kits que faltaban (mascotas, frio, terremoto,
  incendio) + la entrada nueva.
