# Kit72h

Web estática en **https://kit72h.com** con kits de emergencia de **72 horas** por escenario
(DANA, apagón, coche, hogar, montaña, calor, evacuación, terremoto, incendio, frío, bebé,
mayores, mascotas, huerto y kit de 30 días), guías antes/durante/después, blog con fuentes
oficiales, página **Tu zona** (mapa de recursos cerca de ti) y **27 fuentes oficiales**
documentadas.

Todo se apoya en documentos públicos de organismos oficiales (Comisión Europea, Protección
Civil, Sanidad, AEMET, BOE) y en productos reales de Amazon con enlace de afiliado y
disclosure legal.

> Hecho con ❤️ por David Antizar

---

## La idea en dos frases

No hay build, ni backend, ni base de datos. Hay **un shell, unos JSON de contenido y un
prerender con Chrome headless** que convierte cada ruta en HTML real.

`index.html` es la plantilla y también la portada. `js/ui.js` dibuja según `location.pathname`.
`scripts/prerender.py` recorre todas las rutas con Chrome headless y guarda el resultado en
`kit/<slug>/index.html`, `blog/<slug>/index.html`, `fuentes/index.html`, `zona/index.html` y el
propio `index.html`.

De ahí sale la única regla estructural del repo: **`kit/`, `blog/`, `fuentes/`, `zona/` e
`index.html` son generados; el contenido vivo está en `data/`.** Se edita `data/` y se
regenera, en ese orden: primero el generador de SEO y después el prerender, porque el
prerender lee el shell que acaba de tocar el SEO.

El servidor interno del prerender sirve **siempre** el shell en las rutas de sección. Es
deliberado: así la cabecera se regenera en cada página y nunca se congela en la versión con
la que se creó cada una.

---

## Dónde se edita qué

| Quiero cambiar… | Fichero |
|---|---|
| Un kit (textos, secciones, fuentes del kit) | `data/kits.json` |
| Un producto o ASIN | `data/kits.json` y después `catalogo.py build` |
| Una entrada del blog | `data/blog.json` |
| Las fuentes oficiales de `/fuentes/` | `data/kits.json` → `meta.fuentes` (nombre, url, cat, nota) |
| Diseño, colores, tipografía | `css/styles.css` |
| Estructura o textos de una página | `js/ui.js` (home, kit, blog, fuentes, zona) |
| El mapa de «Tu zona» | `js/zona.js` |
| Cabecera y navegación | `index.html` — está fuera de `#app`, JS no la toca |

## Reglas que no se rompen

- `index.html`, `css/` y `js/` solo se tocan en rediseño; el resto es contenido.
- Enlaces internos con **URL real** (`/kit/kit-apagon/`, `/blog/otra-entrada/`). Nunca `#hash`.
- Todo enlace de Amazon lleva `tag=nti0c8-21` y `rel="sponsored nofollow noopener"`.
- **Nada de nombres personales** en `data/`, `js/` ni `index.html`.
- Nada de secretos fuera de `.env`; los workflows usan `${{ secrets.* }}`.
- Commits y mensajes en español.
- Las URLs se comprueban antes de publicarlas: aquí no se inventan enlaces.

---

## Estructura

```
kit72h/
├── index.html               shell + portada (GENERADO)
├── css/styles.css           sistema «Táctico»: radius 0, bordes 2px, Anton + IBM Plex Mono
├── js/                      SPA sin build
│   ├── state.js · blog.js   carga de data/kits.json y data/blog.json
│   ├── estado.js            estado de los enlaces de afiliado
│   ├── ui.js                home, kit, blog, fuentes, zona
│   ├── zona.js              Leaflet + IGN + OpenStreetMap
│   └── main.js · fondo.js   arranque y arte de fondo
├── data/                    FUENTE DE VERDAD
│   ├── kits.json            kits, productos, meta.fuentes
│   ├── blog.json            entradas
│   ├── catalogo.json        índice derivado agrupado por ASIN
│   └── estado.json · asins-estado · propuestas-fichas · logs
├── kit/ blog/ fuentes/ zona/    HTML prerenderizado (GENERADO)
├── scripts/                 prerender, SEO, catálogo, verificación, auditoría
├── notes/                   lo que se aprende, con fecha
├── CRONS.md · SPEC.md
├── _headers · robots.txt · CNAME
└── .github/workflows/       pages.yml · deploy-cloudflare.yml
```

---

## Scripts

| Script | Qué hace |
|---|---|
| `prerender.py` | Hornea cada ruta a HTML con Chrome headless. Siempre después de `generar-seo.py`. |
| `generar-seo.py` | `sitemap.xml` con URLs reales, `feed.xml`, `llms.txt`, `llms-full.txt`, ItemList en el shell. |
| `catalogo.py` | Catálogo central de productos: `build`, `donde <ASIN>`, `compartidos`, `huecos`, `sustituir VIEJO NUEVO`, `verificar`. **Un producto = un sitio.** |
| `verificar-fichas.py` · `verificar-asins.py` | ¿Se puede comprar de verdad? Fichas vivas frente a muertas (caducidad 7 días). |
| `comprobar-urls.py` | Regenera `data/estado.json` con `ok` / `posible_rotura` por enlace. |
| `buscar-amazon.py` | Buscador de fichas reales para cubrir huecos del catálogo. |
| `vigilar-fuentes.py` | Vigila cambios en las fuentes oficiales. |
| `auditar-crons.py` | Qué cron se dispara, con qué modelo y cuántos tokens gasta (`--kit`, `--runs`). |
| `kit72h-buscador.py` | **Cron 05:15** — resuelve fichas Amazon, regenera SEO+prerender y commitea. |
| `kit72h-seo-audit.py` | **Cron 06:00** — auditor determinista del SEO y del prerender. Tiene auto-fix. |
| `fusionar-mejoras.py` · `migrar-blog.py` · `agregar-blog-*.py` · `mejorar-kit-*.py` | Migraciones y one-shots ya ejecutados; quedan como registro. |
| `crear-dns-cloudflare.py` | Registros DNS de `kit72h.com`; el token se lee del `.env`, nunca va en el repo. |

> Los crons ejecutan la copia que vive en `%LOCALAPPDATA%\hermes\scripts\`. Si se toca uno de
> esos dos, hay que copiarlo también ahí — o al revés: el repo es donde se versiona.

---

## Publicación

Un push a `main` dispara dos workflows:

- **`pages.yml` → GitHub Pages**, el que sirve el sitio de verdad. Verde siempre.
- **`deploy-cloudflare.yml` → Cloudflare Pages**, que hoy falla en cada push (token de
  Wrangler inválido → `Getting User settings…`, exit 1). El dominio no apunta ahí: es ruido
  rojo en cada commit.

Cloudflare delante actúa de proxy DNS de `kit72h.com`. El CI regenera SEO y prerender antes de
publicar, así que producción no depende de que quien commitea se acuerde.

---

## Automatización

Cinco trabajos programados: tres diarios (`editor` 04:30, `buscador` 05:15, `seo-audit` 06:00)
y dos del lunes (`vigilante` y `revision-urls`, 09:00). Dos son scripts puros —cuestan cero
tokens— y tres usan LLM. Qué hace cada uno, con qué modelo y cuántos gasta:
**[CRONS.md](CRONS.md)**. Medición al día: `python scripts/auditar-crons.py --kit --runs`.

---

## La página `/zona/`

Mapa de **qué tienes cerca cuando algo falla**: sanidad, farmacias, policía y bomberos,
refugios y puntos de encuentro, con el 112 siempre a mano.

- **Mapa base:** IGN WMTS (`IGNBase-gris`, CC BY 4.0), con topográfico y satélite Esri de
  alternativa.
- **Datos:** OpenStreetMap vía **Overpass API**, consultados en vivo por radio (2/5/10/25 km)
  alrededor de tu ubicación, de tu ciudad o de un punto que toques.
- **Sin backend, sin claves, sin build:** Leaflet desde CDN bajo demanda; `js/zona.js` hace
  geolocalización y búsqueda de ciudad con Nominatim.
- Si Overpass se satura (429) la página lo explica y ofrece **reintentar** — nunca deja
  pantalla vacía.
- El texto sale prerenderizado; solo el mapa necesita JavaScript.

---

## Cómo se verificó por última vez

Prerender de todas las rutas sin fallos, auditoría SEO en verde contando páginas y URLs del
sitemap, navegación idéntica en las 50 páginas generadas, y revisión de capturas en local a
360px y a escritorio antes de publicar. La evidencia de cada iteración queda en `notes/`.

---

---

# Replicar este patrón en otra web

El objetivo de este README es que montar **la siguiente web del estilo** cueste días, no
semanas. El motor ya está probado; lo que cambia es el nicho.

## 1. Qué se copia y qué no

Se lleva el repo **sin** `data/` ni el HTML generado: `index.html`, `css/styles.css`, `js/`
(quedándose fuera el módulo propio del nicho, aquí `zona.js`), `scripts/prerender.py`,
`scripts/generar-seo.py`, `scripts/kit72h-seo-audit.py`, `scripts/auditar-crons.py` si la web
también va con crons, más `_headers`, `robots.txt` y `.github/workflows/pages.yml`.

No se copian `data/`, `kit/`, `blog/`, `fuentes/`, `zona/`, `notes/`, `SPEC.md`.

`prerender.py` y `generar-seo.py` son genéricos salvo tres literales: la constante `BASE`
(URL de producción), el listado de rutas y los `assert` de contenido por ruta. Esos asserts
se escriben con una marca que **solo** existe en la página de destino: con una marca
compartida el test pasa aunque la página salga equivocada — así se coló durante semanas el
índice del blog renderizando la portada.

## 2. Identidad

Un solo juego de tokens de color y tres tipografías. Aquí es el sistema «Táctico»: fondo
crema sobre negro, bordes de 2px, radio 0, sin sombras suaves, Anton para titulares e IBM
Plex Mono para todo lo demás. Cambiar de nicho sin tocar el sistema se consigue solo con las
variables de `:root`.

Si hay mapa, el criterio usado: **España → IGN WMTS primero** (CC BY 4.0, gratuito,
oficial), alternativas `Esri Dark/Light Gray Canvas`, y evitar CARTO y Mapbox por el
rate-limit. Los datos, de OpenStreetMap vía Overpass, consultados en vivo y sin claves.

## 3. El contenido vive en `data/`

Dos ficheros bastan para arrancar: `kits.json` (con `meta.fuentes`) y `blog.json`. El
generador de SEO y el prerender se alimentan de ellos, así que añadir entrada es editar JSON
y regenerar — no hay código que tocar.

Para productos, un índice derivado agrupado por ASIN evita el problema clásico de tener el
mismo producto copiado en N sitios: se corrige una vez y se propaga a todos.

## 4. Publicación y control

Push a `main` → GitHub Pages. La auditoría diaria compara sitemap, ficheros generados,
canónicas y disclosure, y avisa por Telegram si algo no cuadra; tiene auto-fix para lo
meramente mecánico. Si la web vende, el disclosure de afiliado es obligatorio en cada enlace.

## 5. Antes de dar por bueno cualquier cambio

- Regenerar y mirar que las cuentas cuadren: páginas generadas = URLs del sitemap.
- Abrir en el navegador a 360px **y** a escritorio; la cabecera debe caber en una sola fila.
- Comprobar que la navegación es idéntica en todas las rutas.
- Contrastar lo que el texto promete (tiempos de lectura, cifras, precios) con lo que
  realmente hay: una promesa que no cuadra cuesta más confianza que el defecto que tapa.
- Pasar un escáner de secretos y de datos personales **antes** de que el repo sea público.

---

Hecho con ❤️ por David Antizar
