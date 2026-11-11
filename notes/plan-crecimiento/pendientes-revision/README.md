# Revisiones pendientes de revisión humana

Aquí se apartan los borradores de mejora que el publicador NO puede publicar solo:
ya existe entrada con el mismo slug y el cuerpo es distinto (`reemplazo`), o la marca
`.publicado-<slug>` es antigua y no guarda hash.

Cada fichero conserva la entrada tal cual la escribió el consejero. Para publicarla:
`python3 scripts/kit72h-publicar.py --reemplazo` (tras revisar el diff) o devolverla a
`_entrada.json`. Para descartarla: borrar el fichero.
