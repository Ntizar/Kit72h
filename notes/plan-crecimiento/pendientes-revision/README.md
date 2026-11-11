# Revisiones pendientes de revisión humana

Aquí se apartan los borradores de mejora que el publicador NO puede publicar solo:
ya existe entrada con el mismo slug y el cuerpo es distinto (`reemplazo`), o la marca
`.publicado-<slug>` es antigua y no guarda hash.

Cada fichero conserva la entrada tal cual la escribió el consejero. Para publicarla:
`python3 scripts/kit72h-publicar.py --reemplazo` (tras revisar el diff) o devolverla a
`_entrada.json`. Para descartarla: borrar el fichero.

- `2026-11-11-huerto-emergencia-semillas-germinados.json` — slug `huerto-emergencia-semillas-germinados`, 1347 palabras, `_mejora=True`, hash cuerpo `fe8b52c1c4b2…`. Apartada el 2026-11-11: la entrada publicada (2026-08-31) tiene otro cuerpo y la marca `.publicado-…` es de formato antiguo (sin hash), así que el publicador devolvía CONFLICTO y bloqueaba toda la cola.
- `20261111T135036Z-huerto-emergencia-semillas-germinados.json` — apartada el 2026-11-11: requiere revisión humana (`--reemplazo`).
