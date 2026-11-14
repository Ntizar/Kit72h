# Coordinación con el agente de la VM — leer antes de tocar nada

> **Este fichero es el parte de trabajo en paralelo.** Si eres el agente de la VM de NaN
> (o cualquier otra sesión) y vas a hacer un `git pull` de `kit72h`, mira aquí primero qué
> está en vuelo. Se actualiza al empezar y al cerrar, y se borra cuando el trabajo termina.

## En vuelo ahora: multi-mercado i18n (2026-11-14, PC Windows)

**Rama:** `main` · **Autor:** sesión de Mastermind en el PC · **Estado:** montando y publicando

### Qué está cambiando (y por qué)

La web pasa de un solo país (España, `amazon.es`, castellano) a **7 mercados**: ES, Reino
Unido, Alemania, Francia, Italia, Países Bajos y EE. UU. Cada mercado tiene su idioma, su
dominio de Amazon, su tag de afiliado, su moneda y su número de emergencia.

### Ficheros que estoy tocando — NO los edites a mano en paralelo

| Fichero | Qué cambia |
|---|---|
| `data/mercados.json` | **nuevo**: fuente única por país |
| `js/i18n.js` | **nuevo**: capa de idioma, rutas, Amazon y precios por mercado |
| `data/i18n/ui/*.json` | **nuevos**: textos de interfaz (base `es.json` = fuente) |
| `data/i18n/contenido/*.json` | **nuevos**: kits traducidos (overlay) |
| `js/ui.js` | literales castellanos → `i18n.t()`; conserva `precios` (API) tal cual |
| `js/state.js` · `js/blog.js` · `js/estado.js` | fusionan el overlay por slug/índice |
| `js/main.js` | arranca `i18n` y redirige por país |
| `index.html` | cabecera con selector de país, `data-i18n`, `i18n.js` primero |
| `css/styles.css` | bloque `.pais-selector` / `.solo-es` / `.aviso-idioma` (al final) |
| `scripts/mercados.py` | **nuevo**: mercados + rutas, compartido por prerender y SEO |
| `scripts/traducir.py` | **nuevo**: traductor con caché y validación |
| `scripts/pre-render`, `scripts/generar-seo.py`, `scripts/verificar-sitio.py` | multi-mercado: 7× rutas, hreflang, gate por mercado |
| `.github/workflows/pages.yml` | el artefacto incluye `data/i18n/` y las carpetas de país |

### Lo que NO cambia

- `data/kits.json` y `data/blog.json` **siguen siendo la fuente de verdad en castellano**.
  El overlay solo lleva textos; ASINs, URLs y estructura vienen del original.
- `scripts/precios-amazon.py`, `data/precios.json` y el bloque `const precios` de `ui.js`
  son de la VM: se respetan tal cual. Los precios son de `amazon.es` y **solo se muestran
  en el mercado español**; fuera se usa el rango orientativo convertido.
- `/zona/` y `/noticias/` siguen siendo solo de España (AEMET, IGN, Google News ES): no se
  generan fuera y se ocultan con `.solo-es`.

### Si tienes que pushear mientras esto está en vuelo

1. `git pull --rebase` **antes** de commitear.
2. No regeneres `kit/`, `blog/`, `fuentes/`, `zona/` ni `index.html` a mano: el prerender
   escribe 234 páginas (7 mercados). Si tu cron rehornea con la versión vieja del script,
   **borra las carpetas de país**. Después de tu push: `python scripts/prerender.py`.
3. Si hay conflicto en `js/ui.js`, `index.html` o `scripts/prerender.py`: **no lo resuelvas
   a ciegas**. Mi versión lleva la capa i18n; la tuya puede llevar precios, promo o tests.
   Abre el fichero, quédate con las dos cosas y avisa en el parte.

### Pendiente (para no duplicar trabajo)

- [ ] **Tracking IDs de Amazon** de `.co.uk`, `.de`, `.fr`, `.it`, `.nl` — los pide David.
  Mientras falten, `mercados.json` los marca con `tagPendiente: true` y el gate los lista.
- [ ] **Blog en 5 idiomas**: lo hace el cron `kit72h-traducciones` (02:30) por lotes.
  Una entrada no se hornea en otro idioma hasta que su traducción existe.
- [ ] **Privacidad por idioma**: `/privacidad/` sigue solo en castellano.
- [ ] **Precios locales**: cuando la API tenga credenciales por marketplace, `asin_local`
  y `precio_local` ya tienen hueco en el merge.

### Cómo verificar sin romper nada

```bash
python scripts/verificar-traducciones.py     # estructura y cadenas sin traducir
python scripts/generar-seo.py                # sitemap con hreflang (7 mercados)
python scripts/prerender.py                  # 234 páginas (o --solo de,fr)
python scripts/verificar-sitio.py            # gate: lang, hreflang, canonical, dominio
```
