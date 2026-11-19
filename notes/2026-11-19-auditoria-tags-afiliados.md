# Auditoría de los Tracking IDs de Amazon — 2.827 enlaces a cero y cómo se cierra (2026-11-19)

Pregunta de David: «hay cosas que no me cuadran, me han bajado mucho las ventas».
Auditoría completa del sitio vivo (683 URLs del sitemap, **5.284 enlaces de Amazon**
extraídos de los atributos reales, no por regex suelta) y del repo (731 ficheros).

## Lo que estaba mal (medido, no supuesto)

| Zona | Enlaces | Tag que llevaban | Qué pasaba |
|---|---|---|---|
| ES blog | 364 | `kit72h-blog-21` | ✅ cobran |
| ES fichas | 348 | `kit72h-21` | ✅ cobran |
| ES portada y varios | 15 | `ntizar-21` | ✅ cobran |
| `/de/` | 474 | `ntizar-21` en `amazon.de` | ❌ 0 € |
| `/en-gb/` | 474 | `ntizar-21` en `amazon.co.uk` | ❌ 0 € |
| `/fr/` | 474 | `ntizar-21` en `amazon.fr` | ❌ 0 € |
| `/it/` | 474 | `ntizar-21` en `amazon.it` | ❌ 0 € |
| `/nl/` | 474 | `ntizar-21` en `amazon.nl` | ❌ 0 € |
| `/en-us/` | 276 | `onamzntizar-21` en `amazon.es` | ❌ 0 € |
| Extranjeros | ~1.085 | **sin tag** | ❌ 0 € |
| `blog/el-conocimiento-dartnell/` | 1 (+7 páginas) | sin tag | ❌ 0 € |

**2.827 de 5.284 enlaces (53 %) no podían comisionar.** El sitio no daba ni un error:
la página carga, el usuario compra y el dinero se queda por el camino.

## Las cuatro causas

1. **`js/i18n.js` → `tag()`**: `return tags[seccion] || a.tag || 'ntizar-21'`. Si el
   mercado no tenía tag propio, se ponía el de España **en la tienda alemana**. El
   comentario del propio código lo admitía: *«Amazon lo ignora en otra tienda, pero el
   enlace no queda sin tag»*. Se prefirió que el enlace "pareciera" completo a cobrar.
2. **`scripts/mercados.py` → `reescribir_tags()`**: reescribía el `tag=` de **todos** los
   enlaces de Amazon del HTML, sin mirar la tienda. De ahí los 276 enlaces de `/en-us/`
   a `amazon.es` con el tag de la cuenta americana.
3. **`js/analiticas.js` → `esAfiliado()`**: solo contaba clics si el enlace llevaba
   `tag=ntizar-21`. El 14-nov se partió el tracking ID por secciones (portada / fichas /
   blog) y **el embudo propio se quedó a cero** (`clics_amazon: 0` con 38.190 páginas
   vistas). Eso hace que "parezca" que no se vende aunque Amazon cobre.
4. **`data/blog.json`**: la fuente del libro de Dartnell sin `?tag=`, que el prerender no
   podía inventar.

## La corrección

- **`data/tags-afiliado.json`** (nuevo): fuente única de qué tag existe, de qué programa
  es y en qué tiendas acredita. Un tag de marketplace (`ntizar-21`, `kit72h-21`,
  `kit72h-blog-21`) solo vale en `amazon.es`. Un tag **internacional/OneLink**
  (`onamzntizar-21`, confirmado por David) vale en `.com`, `.co.uk`, `.de`, `.fr`, `.it`
  y `.nl` — y **no** en `.es`, que tiene programa propio.
- **`js/i18n.js`**: fuera el fallback a España; nuevo `conTag()` que solo añade `tag=`
  si la URL es de la tienda del mercado; `retag()` ya no toca enlaces de otra tienda.
- **`scripts/mercados.py`**: `reescribir_tags(html, tag, dominio)` — solo reescribe en la
  tienda del mercado.
- **`js/analiticas.js`**: cuenta **cualquier** enlace a tienda Amazon y manda `tag` y
  `tienda` en el evento, para poder cruzar el embudo con el panel de Associates.
- **`data/mercados.json`**: los 5 mercados extranjeros pasan a `onamzntizar-21`
  (`tagPendiente: false`). **Cero mercados pendientes.**
- Versión de caché de `analiticas.js` subida a `20261119a`.

## El sistema para que no vuelva a pasar

| Cuándo | Guardia |
|---|---|
| al commitear | `auditar-tags.py` en `.githooks/pre-commit` |
| antes de publicar (crons) | gate en `kit72h-traducciones.py` y `kit72h-consejero.py` |
| antes del deploy | gate de CI en `.github/workflows/pages.yml` |
| después del deploy | job `auditar-vivo` contra `kit72h.com` |

```bash
python3 scripts/auditar-tags.py          # repo: rc=1 si hay un solo tag mal
python3 scripts/auditar-tags.py --vivo   # sitio publicado
python3 scripts/test-auditar-tags.py     # 18 casos: el auditor TIENE que ponerse rojo
```

La regla, escrita en el registro y en el gate: **un tag nunca cruza de marketplace**.
Y si un mercado no tiene tag, el enlace va sin tag y el auditor lo marca (`W1`), jamás
con el del vecino.

## Lecciones de método

- **El auditor también se audita.** La primera versión usaba `["']([^"']+)["']`: se comía
  la URL en el apóstrofo de `Trek'n` y en los paréntesis sin codificar, y fabricaba
  cientos de «sin tag» falsos. Se arregló con alternancia de comillas y decodificando
  `&amp;`. Sin el test de casos sembrados, ese falso positivo habría acabado en un commit.
- **Un test que no puede fallar no verifica.** El caso `W2` (tag de otra sección) destapó
  que esa comprobación **nunca se ejecutaba** (`zona.replace("es-","")` daba `kit`, no
  `kits`). Código muerto en el propio verificador.
- **`clics_amazon: 0` no significa «no venden»**: el embudo propio estaba roto por el
  filtro del tag, y el panel de Amazon infla clics con crawlers. Ver
  `notes/2026-11-04-panel-afiliados-no-cuadra.md`.
- **Amazon no valida tags por HTTP** (503/403 con tag bueno y con tag roto): la validez
  se confirma en el panel de Associates, no con `curl`. Comprobado en navegador real con
  IP doméstica: `tag=onamzntizar-21` y `tag=zzqqxx-test-21` devuelven **exactamente la
  misma página** (mismo título, 48 resultados, sin aviso). No hay verificación HTTP
  posible; por eso existe el registro y el auditor.
- **La caché del perfil de Chrome envenenaba el horneado**: tras dos ejecuciones
  interrumpidas, el prerender reutilizaba `prerender-<hash>` con su caché HTTP y servía
  un `data/mercados.json` viejo, horneando `/de/` con los tags de la configuración
  anterior. Arreglado con perfil único por proceso, `--disk-cache-size=1` y
  `Cache-Control: no-store` en el servidor efímero. Sin eso, «he cambiado los tags y la
  web sigue igual» no era un misterio: era caché.
