# Kit72h

Web estática en **https://kit72h.com** con kits de emergencia para **72 horas** por escenario (DANA, apagón, coche, hogar, montaña, calor, evacuación, terremoto, incendio, frío, bebé, mayores, mascotas, huerto y kit 30 días), guía antes/durante/después y blog. Contenido basado en fuentes oficiales (Comisión Europea, Protección Civil, DGT, sanidad) + productos reales de Amazon con enlace de afiliado y disclosure legal.

> Hecho con ❤️ por David Antizar

---

## Cómo funciona (léelo antes de tocar nada)

No es un generador de estáticos ni un framework: es un **SPA con shell estático que se hornea a HTML real**.

1. `index.html` es la **plantilla/shell** (marca, CSS, JS, contenido de home).
2. `js/ui.js` renderiza según `location.pathname` (`/kit/<slug>/`, `/blog/<slug>/`, `/fuentes/`).
3. `scripts/prerender.py` recorre **todas** las rutas con Chrome headless y deja el HTML ya renderizado en su ruta:
   `kit/<slug>/index.html`, `blog/<slug>/index.html`, `fuentes/index.html` y el propio `index.html`.

Por eso **`kit/`, `blog/`, `fuentes/` y `index.html` son GENERADOS**: nunca se editan a mano (solo se tocan en rediseño). El contenido real vive en `data/`.

```
edición en data/*.json  →  generar-seo.py  →  prerender.py  →  commit  →  push  →  CI despliega
```

### La página `/zona/`

Mapa de **qué tienes cerca cuando algo falla**: sanidad, farmacias, policía y bomberos,
refugios y puntos de encuentro, con el 112 siempre a mano.

- **Mapa base:** IGN WMTS (`IGNBase-gris`, CC BY 4.0), con topográfico y satélite Esri de alternativa.
- **Datos:** OpenStreetMap vía **Overpass API**, consultados en vivo por radio (2/5/10/25 km)
  alrededor de tu ubicación, de tu ciudad o de un punto que toques en el mapa.
- **Sin backend, sin claves, sin build:** Leaflet se carga bajo demanda desde CDN;
  `js/zona.js` hace geolocalización (Nominatim para ciudad y reverse).
- Si Overpass se satura (429) la página lo dice y ofrece **reintentar** — nunca deja pantalla vacía.
- La parte de texto sale en HTML prerenderizado; solo el mapa necesita JavaScript.

---

## Estructura

```
kit72h/
├── index.html              ← SHELL + home (GENERADO, no editar a mano)
├── css/styles.css          ← estilos (solo en rediseño)
├── js/                     ← SPA (solo en rediseño)
│   ├── state.js            ← carga de data/kits.json
│   ├── blog.js             ← carga de data/blog.json
│   ├── estado.js           ← progreso de checklists (localStorage)
│   ├── ui.js               ← render de home, kit, blog, fuentes, zona
│   ├── zona.js             ← mapa /zona/: Leaflet + IGN + OpenStreetMap
│   ├── main.js             ← orquestador
│   └── fondo.js            ← arte de fondo
├── data/                   ← FUENTE DE VERDAD del contenido
│   ├── kits.json           ← kits, secciones, productos, fuentes
│   ├── blog.json           ← entradas del blog
│   ├── catalogo.json       ← ÍNDICE DERIVADO de productos (agrupado por ASIN)
│   ├── asins-estado.json   ← estado de verificación de cada ficha Amazon
│   ├── propuestas-fichas.json ← fichas pendientes de validar
│   ├── buscador-log.json   ← log del buscador nocturno
│   └── estado.json         ← estado de los enlaces de afiliado (ok / posible_rotura)
├── kit/  blog/  fuentes/  zona/  ← HTML prerenderizado (GENERADO)
├── scripts/                ← motor (ver tabla)
├── notes/                  ← notas de aprendizaje del proyecto
├── sketchs/ videos/ busquedas/  ← material de trabajo, no se publica
├── SPEC.md                 ← spec original del proyecto
├── CRONS.md                ← los 5 crons: qué hacen, cuándo, modelo y tokens
├── _headers · robots.txt · CNAME
└── .github/workflows/
    ├── pages.yml               ← GitHub Pages (despliegue real, OK)
    └── deploy-cloudflare.yml   ← Cloudflare Pages (en fallo, ver «Deploy»)
```

---

## Dónde se edita qué

| Quiero cambiar… | Fichero | Después ejecuto |
|---|---|---|
| Un kit (texto, secciones, fuentes) | `data/kits.json` | `generar-seo.py` + `prerender.py` |
| Un producto / ASIN de un kit | `data/kits.json` | `python scripts/catalogo.py build` + los dos de arriba |
| Una entrada del blog | `data/blog.json` | `generar-seo.py` + `prerender.py` |
| Diseño / colores / maquetación | `css/styles.css`, `js/ui.js`, `index.html` | los dos de arriba (y solo entonces) |

**Reglas sagradas**

- `index.html`, `css/` y `js/` solo se tocan en rediseño.
- Enlaces internos **siempre con URL real** (`/kit/kit-apagon/`, `/blog/otra-entrada/`). Prohibido `#hash`.
- Todo enlace de Amazon lleva el tag `nti0c8-21` y `rel="sponsored nofollow noopener"`.
- **Nunca** aparece «David Antizar» en `data/`, `js/` ni `index.html` (verificar con grep antes de commitear).
- Nada de secretos fuera de `.env`.
- Commits y mensajes en español.

---

## Flujo de una edición (checklist)

```bash
# 1. editar data/*.json  (y si tocas productos)
python scripts/catalogo.py build

# 2. regenerar — ambos deben terminar «0 fallos»
python scripts/generar-seo.py
python scripts/prerender.py

# 3. comprobar
grep -ri "David Antizar" data/ js/ index.html   # debe ser vacío

# 4. commit + push
git add data/ kit/ blog/ fuentes/ index.html sitemap.xml feed.xml llms.txt llms-full.txt
git commit -m "tipo(alcance): descripción en español"
git push
```

---

## Scripts

| Script | Qué hace |
|---|---|
| `scripts/prerender.py` | Hornea cada ruta a HTML estático con Chrome headless. **Debe correr siempre después de `generar-seo.py`.** |
| `scripts/generar-seo.py` | `sitemap.xml` con URLs reales, `feed.xml`, `llms.txt`, `llms-full.txt`, ItemList en el shell. |
| `scripts/catalogo.py` | Catálogo central de productos: `build`, `donde <ASIN>`, `compartidos`, `huecos`, `sustituir VIEJO NUEVO`, `verificar`. **Un producto = un sitio.** |
| `scripts/verificar-fichas.py` | ¿Se puede comprar de verdad? Detecta fichas vivas vs. muertas (caducidad 7 días). |
| `scripts/verificar-asins.py` | Comprobación en lote de que cada ASIN sigue vivo. |
| `scripts/comprobar-urls.py` | Regenera `data/estado.json` con `ok` / `posible_rotura` por enlace de afiliado. |
| `scripts/buscar-amazon.py` | Buscador de fichas reales para cubrir huecos del catálogo. |
| `scripts/vigilar-fuentes.py` | Vigila cambios en las fuentes oficiales. |
| `scripts/auditar-crons.py` | Qué cron se dispara, con qué modelo y cuántos tokens gasta (`--kit`, `--runs`). |
| `scripts/kit72h-buscador.py` | **Cron 05:15** — resuelve fichas Amazon pendientes, regenera SEO+prerender y commitea. |
| `scripts/kit72h-seo-audit.py` | **Cron 06:00** — auditor determinista del SEO y del prerender. Tiene auto-fix. |
| `scripts/fusionar-mejoras.py` · `migrar-blog.py` | Migraciones puntuales de datos. |
| `scripts/agregar-blog-*.py`, `mejorar-kit-*.py` | One-shots ya ejecutados (quedan como registro). |
| `scripts/crear-dns-cloudflare.py` | Registros DNS de `kit72h.com`. |

> Los crons ejecutan la copia que vive en `%LOCALAPPDATA%\hermes\scripts\`. Si toques uno de
> esos dos, cópialo también ahí — o al revés: aquí es donde se versiona.

---

## Crons

Hay **5 crons de esta web** (3 con LLM, 2 scripts puros). Qué hace cada uno, a qué hora, con qué modelo y cuántos tokens se gastan → **[CRONS.md](CRONS.md)**.

Resumen: `editor` 04:30 → `buscador` 05:15 → `seo-audit` 06:00 (diarios) y `vigilante` + `revision-urls` (lunes 09:00).

---

## Deploy

- **`kit72h.com` se sirve desde GitHub Pages** (origen) con Cloudflare delante como proxy DNS. La workflow `pages.yml` es la que despliega de verdad y va verde.
- `deploy-cloudflare.yml` sube también a Cloudflare Pages, pero **falla en cada push** (token de Wrangler inválido → `Getting User settings…` exit 1) y el dominio no apunta ahí. Mientras no se arregle, es ruido rojo en cada commit.
- El CI de Cloudflare regenera SEO y prerender antes de publicar, así que el HTML de producción no depende de que el committer lo recuerde.

---

## Verificación

```bash
python scripts/comprobar-urls.py        # enlaces de afiliado
python scripts/verificar-asins.py       # ASINs vivos
python scripts/prerender.py             # «45 rutas · 0 fallos»
```
Auditoría diaria automática: `%LOCALAPPDATA%\hermes\scripts\kit72h-seo-audit.py`
(comprueba sitemap ↔ ficheros, prerender al día, canonical, disclosure…).

---

## Créditos

Hecho con ❤️ por David Antizar
