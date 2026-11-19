# Crons de Kit72h

Los 7 trabajos que mantienen la web. Horarios en **UTC** (GitHub y Hermes); la
hora de Madrid va +1 en invierno y +2 en verano.

> Estado y horarios reales: `hermes cron list` / `~/.hermes/cron/jobs.json`.
> Este documento explica el contrato, no duplica la programación.

## Resumen

| Cron | Cuándo (UTC) | Tipo | Qué hace |
|---|---|---|---|
| `kit72h-buscador` | diario 05:15 | script | Resuelve ASIN con Creators API, refresca precios y pre-renderiza |
| `kit72h-crecimiento` | diario 06:00 | LLM | SEO/CTR + consejero; deja `_entrada.json` encolada |
| `kit72h-ofertas` | diario 07:00 | script | Instantánea atómica de precios y selección del día |
| `kit72h-publicador` | diario 08:30 y 12:30 | script | Publica la cola, pasa el gate y pushea el blog |
| `kit72h-analitica` | diario 09:05 | script | Instrumenta páginas y refresca `data/analiticas.json` |
| `kit72h-noticias` | cada 3 h, minuto 10 | script | Noticias y avisos AEMET en JSON |
| `revision-semanal` | lunes 09:00 | LLM | Digest de Mastermind + vigilante de Kit72h |

## Orden y dependencias

```
05:15  buscador      → ASIN + precios + prerender + commit
06:00  crecimiento   → SEO/CTR y _entrada.json (NO publica)
07:00  ofertas       → precios frescos + selección + commit verificado
08:30  publicador    → blog + gate + commit/push
09:05  analítica     → instrumentación y panel (después del publicador)
10:10  noticias      → cada 3 h; JSON que leen /noticias/ y /zona/
```

El publicador de las 12:30 recoge cualquier entrada que el consejero haya dejado
después de las 08:30. Si no hay cola, imprime una línea y sale con 0.

## Contratos de fallo

- **Runner** (`~/.hermes/scripts/runner-kit72h.py`): solo commitea las salidas
  declaradas en `scripts/cron_git.py`. Un script desconocido con cambios deja el
  árbol sucio y rc=2; nunca hace `git add -A`. Los scripts que se autocommiten
  (buscador, ofertas) solo se aceptan si dejan el árbol limpio.
- **Buscador/ofertas**: commit, pull o push fallidos devuelven rc≠0. Ofertas
  además lee `https://kit72h.com/data/precios.json` y no declara éxito hasta que
  la instantánea nueva está servida.
- **Publicador**: una marca `.publicado-<slug>` solo vale si contiene
  `hash_sha256` y coincide con `data/blog.json`. Marca vacía o distinta = rc=2,
  cola conservada. La entrada se archiva después del commit/push; si falla, se
  restaura a la cola.
- **Gate editorial**: antes de publicar exige título, slug, ≥800 palabras
  (≥1200 en revamp) y ≥2 fuentes con URL. Después corre `verificar-sitio.py`.
- **Precios**: si un lote falla o no hay ninguna cotización, `precios.json` no
  se toca. Los ASIN no devueltos no heredan el precio del día anterior.
- **Analítica**: `instrumentar-analitica.py` lee el token CSS vivo de
  `index.html`; no hardcodea versiones que puedan revertir un bump.

## Comprobación rápida

```bash
python3 scripts/verificar-sitio.py          # 0 errores antes de push
python3 -m unittest discover -s tests -v    # 29 tests de contrato
python3 scripts/verificar-produccion.py     # artículos y precios en URL viva
```

Un cron que falla debe dejar rastro en stdout/stderr y rc≠0. Silencio solo es
válido cuando no había trabajo y el árbol quedó limpio.


---

## `kit72h-traducciones` — los idiomas al día (diario 02:30)

Script puro + la API de modelos (`scripts/traducir.py`), orquestado por
`scripts/kit72h-traducciones.py`. **No usa el agente**: cero tokens de razonamiento.

```
02:30  traducir.py blog --pendientes   → solo lo que falta (caché por cadena)
       generar-seo.py                  → sitemap con hreflang de los 7 mercados
       prerender.py                    → hornea los mercados (~234 páginas)
       verificar-sitio.py              → gate; si falla, NO se publica
       git commit + push               → publica en GitHub Pages
```

- **Incremental y resumible**: presupuesto de 3 h; lo que no entre, la noche siguiente.
- **Un lote fallido no se cachea** (si se cachea el original queda «traducido» para siempre).
- Una entrada de blog **no se hornea en otros idiomas hasta que su traducción existe**.
- Medición: 21 kits × 5 idiomas = 1.400 cadenas en ~9 min con 4 hilos (deepseek-v4-flash).

---

## `kit72h-tags` — los Tracking IDs de Amazon, vigilados

Un tag equivocado no da ningún error: la página carga, el usuario compra y la
comisión se va a la basura. No hay cron propio: el guardián se cuelga de **los
sitios por donde el sitio se publica**, así no depende de que nadie se acuerde de
lanzarlo.

| Cuándo | Qué | Dónde |
|---|---|---|
| al commitear | `auditar-tags.py` en el hook `pre-commit` | `.githooks/pre-commit` |
| antes de publicar (crons) | gate en traducciones y en el consejero | `kit72h-traducciones.py`, `kit72h-consejero.py` |
| antes del deploy | gate de CI (bloquea el push a producción) | `.github/workflows/pages.yml` |
| después del deploy | `auditar-tags.py --vivo` sobre `kit72h.com` | `pages.yml`, job `auditar-vivo` |

```bash
python3 scripts/auditar-tags.py            # repo local (HTML horneado + fuentes)
python3 scripts/auditar-tags.py --vivo     # sitio publicado, vía sitemap
python3 scripts/test-auditar-tags.py       # 15 casos: el auditor TIENE que ponerse rojo
```

**La regla que no se negocia:** el tag de un marketplace nunca se aplica a la
tienda de otro. `ntizar-21` es de `amazon.es`; en `amazon.de` Amazon lo ignora y
la venta se pierde sin aviso. Si un mercado no tiene tag propio, el enlace se
construye **sin tag** y el auditor lo marca como pendiente (`W1`), nunca con el
tag del vecino.

- Fuente única: `data/tags-afiliado.json` (qué tag existe y de qué mercado es).
  `data/mercados.json` solo dice qué tag usa cada mercado y sección; si se
  contradicen, el auditor falla con `E6`.
- Añadir un mercado nuevo con tag = crear el Tracking ID en Associates **primero**
  y añadirlo a los dos ficheros en el mismo commit. Añadirlo solo a
  `mercados.json` rompe el gate a propósito.
- Códigos: `E1` tag desconocido · `E2` tag de otro mercado · `E3` sin tag
  habiendo tag · `E4` tag vacío o duplicado · `E5` dominio sin mapear · `E6`
  registro incoherente. `W1` mercado pendiente · `W2` tag de otra sección ·
  `W3` enlace corto (`amzn.to`) · `W4` tag registrado que nadie usa.
