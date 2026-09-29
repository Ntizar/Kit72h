# Landing: quiz fuera, CTA de compra dentro — y el bug de la nav congelada (2026-09-29)

## Qué se cambió

- Cabecera: **«Haz tu kit ↗» → «Compra tu kit ↗»**, apuntando a Amazon con el tag
  en vez de a una ancla interna.
- **Fuera** la sección `02 / Prueba rápida` (el quiz 0/6) y **fuera** `06 / Adáptalo`.
  La home queda en 4 bloques: `01 El plan` · `02 Tu lista` · `03 Los kits` · `04 Lecturas`.
- El bloque de cifras (16 kits / 72 H / 180+ / 1-Clic), que no aportaba nada,
  se sustituye por un CTA grande: **«No pierdas el tiempo: compra tu kit completo»**
  → `amazon.es/s?k=kit+emergencia+72+horas&tag=nti0c8-21`.
- Botones de producto **«Ver en Amazon ↗» → «Comprar ↗»** («Ver precios ↗» cuando
  no hay ficha, solo búsqueda). Cesta: «Llévate todo el kit →» /
  «Llévate solo lo esencial — los N imprescindibles →».
- Enlaces con `#hash` en «Sigue leyendo» y «Guías relacionadas» → `/blog/<slug>/`.

## El bug de raíz: la nav se congelaba por página

Síntoma: «hay enlaces que aparecen y desaparecen, como Tu zona» — `Tu zona` y
`Compra tu kit` solo estaban en `/` y `/zona/`, y el resto de páginas llevaba una
nav vieja.

Causa: el servidor HTTP interno de `prerender.py` servía **el fichero ya generado**
de cada ruta siempre que existiera (solo caía al shell si no existía). Chrome
re-renderizaba `#app` con el JS actual, pero **la cabecera es HTML estático fuera de
`#app`**, así que se quedaba tal cual se había generado esa página la primera vez.
La cabecera solo se refrescaba en las páginas que se generan desde el shell: `/`
(porque el shell es la propia home) y `/zona/` (que era nueva).

**Fix:** el handler sirve **siempre** el shell en las rutas que terminan en `/`.
Resultado medido: **50/50 páginas con la misma nav** (antes 46 con nav vieja).

Lección: en un prerender de SPA, **todo lo estático que no vive dentro del nodo que
JS reescribe se congela**. O se sirve siempre el shell, o hay que refrescarlo a mano
en cada página.

## El blog: la promesa no cuadraba con el contenido

`lectura` era un campo escrito a mano en `data/blog.json`. Medido:

| | |
|---|---|
| Posts con cuerpo < 400 palabras | 8 de 31 (245–393 palabras) |
| Lo que anunciaban | «6 min» / «7 min» de lectura |
| Lo que había de verdad | 1–2 min |
| Posts largos de verdad | `kit-emergencia-trabajo-oficina` (2.863 pal) y `panel-solar` (1.572) |

El HTML prerrenderizado **no recorta nada**: siempre tiene *más* palabras que el
JSON (el delta ≈ 74 son los titulares, fuentes y «sigue leyendo»). El problema era
el contenido, no el volcado.

**Fix:** `ui.lectura(e)` calcula los minutos del cuerpo real (200 palabras/min) y se
usa en home, índice, ficha y «guías relacionadas». La promesa cuadra y **crece sola**
cuando se amplíe el contenido.

**Pendiente (editorial):** ampliar los 8 posts cortos a 700–1.200 palabras. El cron
`kit72h-editor` ya sabe escribir a ese largo; conviene que también *mejore* los
existentes en lugar de añadir siempre uno nuevo.

## Verificación (producción)

`prerender 51 rutas / 0 fallos` · `kit72h-seo-audit` verde (51 páginas / 51 urls) ·
en vivo: home sin quiz ni Adáptalo, `cta-kit` presente, 5/5 páginas con nav nueva,
11 «Comprar ↗» en `kit-apagon`, 0 enlaces `#blog/`.

---

Hecho con ❤️ por el equipo Kit72h
