# La cesta en 1 clic daba error: ASINs muertos (2026-09-28)

## Síntoma
Pulsar **«Cesta llena en 1 clic»** llevaba a la página de error de Amazon y no
entraban todos los productos del kit.

## Causa raíz (dos cosas distintas, no una)

**1. Un solo ASIN muerto tumba la cesta ENTERA.** `B09VH3MZG7` (la manta térmica)
devolvía **404**: Amazon rechaza el `add.html` completo si uno de los ASINs no
existe. Ese ASIN estaba en **3 kits** (básico, coche, evacuación), así que su cesta
estaba rota en los tres. Barrido de los 150 ASINs del catálogo: **5 muertos** —
`B09VH3MZG7` (manta), `B07VWLV1P7` (bolsas), `B01MZGQZK5` (abreconservas),
`B08BQXJ8ZG` (cazo), `B0F8JJCFQ2` (papilla del kit bebé).

**2. «Cesta llena» no podía estar llena.** El botón metía solo los `esencial`;
los `recomendado`/`extra` se quedaban fuera. Y 20 items del catálogo tienen
**enlace de búsqueda** (`/s?k=...`) en vez de ficha: sin ASIN no pueden entrar en
una cesta. kit-hogar era el peor: 16 de 22.

## Arreglos aplicados
- **5 fichas muertas sustituidas** por productos equivalentes VIVOS y en el mismo
  rango de precio (`verificar-asins.py` re-verificado: **151/151 vivos**).
- **`armarCesta(slug, modo)`**: `'todo'` (defecto, botón «Cesta llena») mete TODOS
  los items con ficha; `'esenciales'` (botón «Añadir los N imprescindibles») solo
  los esenciales. Antes los dos botones hacían lo mismo.
- **El recuento del botón ahora es el real**: contaba items y la cesta deduplica
  ASINs (decía 15 y añadía 10 en kit-hogar). Ahora cuenta ASINs únicos.
- **5 enlaces de búsqueda con espacios sin codificar** (`/s?k=detector monoxido
  carbono pilas`) → URL-encoded. Estaban todos en kit-hogar.

## Lecciones / reglas
1. **`comprobar-urls.py` existe pero llevaba un mes sin correr** (`data/estado.json`
   era del 1-sep). Un validador que no se ejecuta no es un validador: los 404
   entraron sin que nadie se enterara. Meterlo en el cron del editor.
2. **Al sustituir una ficha, sustituirla en TODOS los kits**: un mismo producto
   aparece en varios (la manta estaba en 3) y el fallo se multiplica.
3. **Un ASIN de ficha es obligatorio para la cesta**; un item con `es_busqueda`
   nunca entrará. Si se quiere la cesta completa de verdad, el buscador tiene que
   resolver esas 20 búsquedas a fichas concretas.
4. **Verificación**: `python scripts/verificar-asins.py` (4 hilos, ~1 s/ASIN, sale
   con código 1 si hay muertos → sirve tal cual en CI/cron).
