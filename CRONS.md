# Crons de Kit72h

Los 5 trabajos programados que tocan esta web. Qué hace cada uno, a qué hora, con qué modelo y cuántos tokens se gastan.

> **Medido, no estimado.** Los tokens salen de `%LOCALAPPDATA%\hermes\cron\usage_audit.jsonl` (365 runs registrados desde el 27/08/2026, una línea por ejecución: `job_id`, `total_tokens`, `model`, `duration_ms`, `error`). El estado y los horarios salen de `%LOCALAPPDATA%\hermes\cron\jobs.json`.

---

## Resumen

| Cron | ID | Cuándo | Tipo | Modelo | Estado | Runs | Tokens totales | Media/run |
|---|---|---|---|---|---|---:|---:|---:|
| `kit72h-editor` | `b8c32d5eff46` | diario **04:30** | LLM | `mimo-v2.6-flash` | ✅ ok | 21 | 32.152.979 | 1.531.094 |
| `kit72h-buscador` | `5a577913b9db` | diario **05:15** | script (sin LLM) | — | ✅ ok | 20 | **0** | 0 |
| `kit72h-seo-audit` | `323767d865e7` | diario **06:00** | script (sin LLM) | — | ⚠️ **error** | 1 | **0** | 0 |
| `kit72h-vigilante` | `e518c0973b6a` | lunes **09:00** | LLM | `mimo-v2.6-flash` | ⏸️ **pausado** | 24 | 21.019.999 | 875.833 |
| `kit72h-revision-urls` | `1ac91e8ca632` | lunes **09:00** | LLM | `mimo-v2.6-flash` | ✅ ok | 1 | 209.804 | 209.804 |

**Total Kit72h: 53.382.782 tokens en 46 runs** ≈ **1,6 M tokens/día**.
(Equivalente a ≈ 0,6–0,8 €/día con un modelo *flash*. El límite real no son euros: es la **cuota de allowance** de NaN.builders, no el coste.)

Los 3 LLM cuestan; los 2 scripts puros son **gratis** y hacen el trabajo pesado (SEO, prerender, verificación). Ese es el reparto correcto.

---

## La cadena nocturna (los 3 diarios, en orden)

```
04:30  kit72h-editor      LLM      escribe contenido → generar-seo → prerender → commit+push
05:15  kit72h-buscador     script   resuelve fichas Amazon → generar-seo → prerender → commit+push
06:00  kit72h-seo-audit    script   comprueba que todo lo anterior cuadra → avisa por Telegram
```

El orden importa: el **buscador regenera el prerender en el mismo run** para que la auditoría de las 06:00 no vea HTML desfasado respecto a `data/`. Si alguien toca `data/` fuera de esa cadena (a mano, o desde otra sesión), el audit salta.

---

## Ficha de cada cron

### `kit72h-editor` — diario 04:30 · LLM · `mimo-v2.6-flash`

El único que **crea contenido**. Trabaja en `C:\Users\d_ant\Projects\kit72h`.

1. Escribe una entrada de blog nueva o mejora una existente: 700–1.200 palabras, titular con keyword, resumen <160 car., datos de España y **fuentes oficiales citadas con enlace**. Sin campo `autor`.
2. Enlaces internos con **URL real** (`/blog/…/`, `/kit/…/`), nunca `#hash`.
3. Si toca productos: ASIN real + `tag=nti0c8-21`.
4. **Antes de commit**: `generar-seo.py` + `prerender.py` (ambos «0 fallos») y grep de «David Antizar».
5. Commit en español + push → el CI despliega.
6. Si no hay nada con valor: «sin cambios», sin relleno.

- **Duración media:** 296 s · **completion medio:** 15.755 tokens
- **3 errores** de 21 runs (históricos en `qwen3.6`/`deepseek-v4-flash`; hoy anclado a `mimo-v2.6-flash`)
- Entrega el informe a **Telegram**.

### `kit72h-buscador` — diario 05:15 · script puro · 0 tokens

`kit72h-buscador.py` (sin LLM): resuelve fichas Amazon pendientes del catálogo y **regenera SEO + prerender en el mismo run**, luego commit+push.

> REGLA DE ORO documentada en el propio script: el HTML de `kit/`, `blog/`, `fuentes/` e `index.html` debe salir del **mismo commit** que `data/kits.json`. Si se commitean datos sin regenerar, la web queda desfasada y el audit de las 06:00 salta.

### `kit72h-seo-audit` — diario 06:00 · script puro · 0 tokens · ⚠️ FALLANDO

`kit72h-seo-audit.py`, determinista. Comprueba: `sitemap.xml` ↔ ficheros existentes, URLs sin `#hash`, prerender al día respecto a `data/`, canonical, disclosure de afiliado… Imprime **una línea si todo está bien** o un *bullet* por problema.

- **Último run (29/09 06:00): FALLÓ**
  ```
  SEO AUDIT — 1 problemas:
  - prerender desactualizado: 50 paginas mas antiguas que data/
  ```
  Causa raíz ya localizada → ver «Hallazgos».

### `kit72h-vigilante` — lunes 09:00 · LLM · `mimo-v2.6-flash` · ⏸️ PAUSADO

Chequeo semanal de salud de la web:

1. `git pull` + estado del repo.
2. `generar-seo.py` y `prerender.py` sin fallos (45 rutas).
3. `HEAD` a `https://kit72h.com/` y a `/kit/kit-apagon/` esperando 200 con HTML estático.
4. Si algo falla → commit del arreglo; si no → «todo verde».

- **24 runs, 21.019.999 tokens** (875.833 de media, el más barato de los LLM), duración media 285 s.
- **Pausado** tras un `HTTP 402` de `qwen3.8-flash` (allowance agotada: 500.015.345 de 500.000.000 tokens). Ya está **reanclado a `mimo-v2.6-flash`**, así que se puede reanudar sin miedo.

### `kit72h-revision-urls` — lunes 09:00 · LLM · `mimo-v2.6-flash`

Comprueba los enlaces de afiliado con `scripts/comprobar-urls.py` → regenera `data/estado.json`.

- Si hay cambios: `generar-seo.py` + `prerender.py` + commit + push.
- Si aparece un enlace roto, propone alternativas de búsqueda con el mismo tag (`amazon.es/s?k=…&tag=nti0c8-21`) para que el editor nocturno las sustituya.
- **1 solo run registrado** (01/09, 209.804 tokens) → ver «Hallazgos».

---

## Hallazgos y limpieza propuesta

| # | Hallazgo | Impacto | Propuesta |
|---|---|---|---|
| 1 | **`revision-urls` no se dispara desde el 1 de septiembre** (4 lunes perdidos: 8, 15, 22 y 29/09). `completed: 1` en jobs.json. | Los enlaces de afiliado llevan un mes sin revisarse. | Diagnosticar (`hermes cron status 1ac91e8ca632`) y reactivar. |
| 2 | **`vigilante` y `revision-urls` a la vez: lunes 09:00** | Ambos hacen `git push` al mismo repo → choque «fetch first». | Desfasar: vigilante 08:30, revision-urls 09:15. |
| 3 | **`vigilante` pausado** por 402 de `qwen3.8-flash` | Sin chequeo semanal de salud. | Ya anclado a `mimo-v2.6-flash` → `hermes cron resume e518c0973b6a`. |
| 4 | **`seo-audit` en rojo**: prerender desactualizado (50 páginas) | El aviso diario es ruido si siempre canta. | Arreglar la causa (ver abajo) y dejarlo en verde. |
| 5 | **`prerender.py` NO es idempotente**: cada run añade un comentario `<!-- GENERADO … -->` al final de cada página (index.html acumula **12**). | Repo permanentemente sucio: 50 ficheros modificados en cada `git status`, diffs eternos, commits de ruido. | 3 líneas: quitar los marcadores previos antes de añadir el nuevo. |
| 6 | El check del audit compara **mtimes** (`página` vs `data/`): cualquier toque de `data/` sin regenerar lo rompe, aunque no cambie nada. | Falsos positivos. | Comparar contenido/hash, o regenerar siempre al tocar `data/`. |
| 7 | `deploy-cloudflare.yml` **falla en cada push** (Wrangler: `Getting User settings…` exit 1) mientras `pages.yml` va verde. | CI rojo permanente = ruido. | Arreglar el token o desactivar la workflow (GitHub Pages es lo que sirve hoy). |
| 8 | El run del `editor` del **29/09 02:54** se comió **7.482.661 tokens en 1.413 s** — 6× su media (1,5 M / 296 s). | Seis veces el consumo habitual de golpe. | Mirar ese run (`hermes cron runs b8c32d5eff46`): ¿reintentos, sub-agentes o contexto desbordado? |

---

## Cómo volver a medir

```bash
# tokens por cron: runs, errores, modelo anclado, media, detalle run a run
python scripts/auditar-crons.py             # todos los jobs del gateway
python scripts/auditar-crons.py --kit       # solo los 5 de esta web
python scripts/auditar-crons.py --kit --runs  # + últimas ejecuciones de cada uno

# consumo por sesión (input/output/cache/coste)
C:/Users/d_ant/AppData/Local/Programs/Python/Python312/python.exe \
  "%LOCALAPPDATA%\hermes\skills\mastermind\mastermind-system-ops\scripts\auditar-tokens.py" [YYYY-MM-DD]

# estado y horarios de todos los jobs
hermes cron list
hermes cron status <id>
hermes cron runs <id>
```

> Los datos de `state.db` y de `usage_audit.jsonl` no cuadran del todo: el primero mide **por sesión** (incluye caché leída) y el segundo **por run de cron** (prompt + completion). Para «cuánto gasta cada cron» manda `usage_audit.jsonl`.

---

## Anexo — resto de jobs del mismo gateway (17 en total)

No tocan esta web, pero comparten cuota de NaN.builders. Tokens medidos en la misma ventana (27/08 → 29/09):

| Job | Cuándo | Modelo | Runs | Tokens totales |
|---|---|---|---:|---:|
| `mastermind-scout` | 01, 07, 13, 19 h | `deepseek-v4-flash` | 103 | 83.038.493 |
| Gobierno IA — Pase de lista matinal | 10:25 | `deepseek-v4-flash` | 24 | 75.373.179 |
| Gobierno IA — Consejo de Ministros | 22:00 | `deepseek-v4-flash` | 23 | 61.948.641 |
| Gobierno IA — Informe presidencial cómico | 08:00 | `deepseek-v4-flash` | 27 | 44.166.811 |
| Gobierno IA — Auditoría del Estado | 23:30 | `deepseek-v4-flash` | 23 | 34.668.994 |
| **Kit72h (5 jobs)** | ver arriba | varios | **46** | **53.382.782** |
| Gobierno IA — Café informal | 09:30 | `deepseek-v4-flash` | 18 | 19.559.422 |
| `mastermind-digest` | 07:00 | `deepseek-v4-flash` | 10 | 19.475.487 |
| `Maratón nocturno de stars` | 1–6 h del 01/09 | `qwen3.8-flash` | 17 | 8.253.151 |
| `mastermind-doctor` | 10:00 | `deepseek-v4-flash` | 26 | 7.932.235 |
| `mastermind-weekly-digest` | lunes 09:00 | `deepseek-v4-flash` | 6 | 966.224 · ⚠️ **401** el último |
| `vigia-cron` | cada 30 min | script (sin LLM) | 914 | **0** |
| `skills-usage-report` | lunes 08:00 | script (sin LLM) | 3 | **0** |
| 4 jobs ya borrados | — | `qwen3.6`/`qwen3.8-flash` | 42 | 23.183.177 (histórico) |

**Total del gateway: ≈ 431,9 M tokens en 33 días** ≈ 13 M/día ≈ 5–7 €/día equivalentes. Kit72h es el **12 %** de eso.

---

Hecho con ❤️ por David Antizar
