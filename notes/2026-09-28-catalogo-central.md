# Catálogo central de productos (2026-09-28)

## El problema que resuelve
El catálogo tenía **154 productos repartidos en 174 apariciones por 12 kits**: 17
productos estaban **copiados a mano en 2-4 kits** (la radio FM en 3, el chubasquero
en 3, la linterna frontal en 3...). Copiar significa que un producto se mantiene N
veces. Cuando un ASIN murió (la manta térmica), hubo que sustituirlo en 3 sitios
distintos y la cesta de los 3 kits se rompió a la vez.

## La pieza
`data/catalogo.json` — **índice derivado** de `data/kits.json`, agrupado por ASIN:
nombre canónico, url, precio de referencia, categorías, en qué kits aparece cada uno
y con qué prioridad, más el estado de verificación de la ficha.

`kits.json` sigue siendo la fuente que lee la web (no se toca el front), pero para
**productos** la vista de verdad es el catálogo.

## Herramienta: `scripts/catalogo.py`
```
build                  regenera el índice desde kits.json
donde <ASIN>           en qué kits se usa ese producto
compartidos            los usados en 2+ kits (los que hoy viven duplicados)
huecos                 items sin ficha: comprables vs consejos no comprables
sustituir VIEJO NUEVO  cambia el ASIN en TODOS los kits de una pasada (+ reindexa)
verificar              valida las 154 fichas (HTTP) y marca estado/fecha
```
`sustituir` es la razón de ser: arregla un producto muerto **una vez** y actualiza
todos los kits que lo usan. Antes eso era N ediciones a mano.

## Números de hoy
- 154 productos, **17 compartidos** en 2+ kits, **154/154 fichas vivas**.
- Huecos: 24 comprables (el buscador nocturno los va resolviendo) y 5 que son
  consejos, no productos (efectivo, hoja de contactos, acuerdo de vecindad...):
  esos se muestran como "Consejo — no se compra online", correcto.

## Reglas
1. **Antes de añadir un producto a un kit nuevo, mirar `catalogo.py compartidos`**:
   si ya existe un producto que sirve, se reutiliza el ASIN (mismo objeto en varios
   kits es deseable: es el criterio de David).
2. Tras tocar `kits.json`: `catalogo.py build` y commitear los dos ficheros juntos.
3. Un producto muerto se arregla con `catalogo.py sustituir`, nunca a mano kit a kit.
