# Maquetas Kit72h — comparativa (2026-09-28)

Tres posturas de diseño distintas, manteniendo la esencia (cobre, petróleo, Rubik Dirt, tono directo). Abre cada `index.html` en el navegador.

## Variante 001 — Refinería (evolución)
- **Postura:** el tema actual, pulido. Lo que ya funciona (dark + cobre + polvo) con jerarquía real: hero con cifras, chips de categoría, tarjetas limpias con coste y nº de productos, blog integrado.
- **Fuerte en:** continuidad de marca, cero riesgo, mejor móvil.
- **Débil en:** no añade utilidad nueva; es cosmética avanzada.
- **Ideal si:** lo que molesta del sitio actual es el "aspecto desordenado" (manchas, tarjetas iguales), no la falta de funciones.

## Variante 002 — Sala de mando (acción)
- **Postura:** primero la acción. Barra de alerta contextual (DANA en temporada), buscador con filtro en vivo, tabs por categoría, KPIs, panel "arranque rápido" de 3 pasos y checklist marcable con barra de progreso (localStorage).
- **Fuerte en:** conversión y utilidad: el visitante busca, entra, marca, imprime. Es la que más vende.
- **Débil en:** más JS; pierde algo de atmósfera "Mad Max".
- **Ideal si:** el objetivo es que la gente llegue de Google, encuentre SU kit y lo complete.

## Variante 003 — Manual de campaña (editorial)
- **Postura:** confianza y lectura. Páginas de "cuaderno de campo" en papel sobre noche, índice numerado tipo libro, checklists tipo formulario imprimible con bolígrafo. Print stylesheet de primera.
- **Fuerte en:** diferenciación brutal frente a otras webs de afiliación, lectura larga del blog, impresión de checklists.
- **Débil en:** el papel claro rompe la identidad dark; menos sensación de "app".
- **Ideal si:** se quiere que el blog pese (SEO largo) y que la web parezca un manual serio, no una tienda.

## Mi recomendación
**002 (Sala de mando) como base, robando de 003 el checklist imprimible tipo manual** (la página de kit puede llevar el checkbox web Y imprimirse como hoja de campo). El alert contextual se alimenta de un campo `alertas` en `data/kits.json` (lo llena el cron vigilante: AEMET/Protección Civil), así no es decorativo sino contenido real.

Datos de ejemplo: solo el kit apagón lleva contenido completo (marcado en cada maqueta).
