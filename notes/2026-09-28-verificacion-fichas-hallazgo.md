# Verificar fichas de Amazon: por qué "vivo" no es "se puede comprar" (2026-09-28)

## El hallazgo (comprobado)
Pedirle la página a Amazon por HTTP simple **no sirve para saber si un producto se
puede comprar**. A una petición automática (urllib, curl sin sesión) Amazon le
devuelve una página de **3.789 bytes sin título y sin botón de compra** — idéntica
para un producto vivo y para uno muerto.

Consecuencia: el chequeo `200 + <title>` que veníamos usando **solo es fiable para
detectar 404** (eso sí: un ASIN muerto responde 404 de verdad, y así se cazaron los
5 caídos). Para "¿está a la venta?" es ciego. Decir "151/151 vivas" era cierto para
lo que medía, y engañoso para lo que la web promete.

Con navegador real sí se ve la verdad:
- manta térmica `B0CYDF32J3` → título + botón de compra + 6,90 € (`buybox: true`)
- ASIN muerto `B09VH3MZG7` → página de 1.637 bytes, sin título

## Cuidado con el detector (falsos positivos medidos)
En una muestra de 10 fichas con navegador, 3 salieron "sin cesta" **y las tres
mostraban título y precio correctos**: el `id` del botón de compra varía por layout
y por variante de página. El método fiable es el que ya usaba `buscar-amazon.py`
(curl `--compressed` + cookie jar persistente): devuelve la página real de 2,4 MB.

**Y en masa, Amazon frena.** Verificando 3 fichas seguidas con ese método, la misma
manta que 5 minutos antes daba `ok` pasó a `bloqueado`, y una ficha perfecta (los
silbatos) salió `agotado`. Dos reglas que salen de ahí:
- **Un estado malo se confirma con una segunda lectura separada**; si las dos
  discrepan, queda `error` y NO se sustituye nada (`comprobar_con_confirmacion`).
- **Presupuesto pequeño y pausas largas** (2,5 s entre fichas, ~40 por tanda). Sin
  eso el sistema fabrica falsos positivos a escala de miles.

## Diseño para miles de fichas
1. **Registro con estado y fecha** (SQLite `data/fichas.db`, ya creado): estado por
   ASIN, última verificación, fallos consecutivos, primera caída, último OK, histórico.
2. **Estados honestos**: `ok` / `sin_cesta` / `agotado` / `caido` / `bloqueado` /
   `error`. **Un bloqueo (403/429/503) NUNCA es una caída** — es la regla que evita
   marcar como muerto medio catálogo cuando Amazon nos frena.
3. **Presupuesto y prioridad, no barrido total**: cada tanda verifica N fichas
   ordenadas por (sin verificar → peor estado → más días sin mirar → más kits donde
   aparece). Las estables se revisan menos. Con miles de fichas esto es la única
   forma de que el sistema no se ahogue.
4. **La web no afirma lo que no ha verificado**: mostrar la fecha y, si el estado no
   está confirmado, degradar a "Buscar en Amazon" en vez de dar por buena la ficha.
5. **Sustitución automática**: K fallos honestos consecutivos → buscar sustituto (con
   ficha verificada de verdad) y cambiarlo en TODOS los kits con
   `catalogo.py sustituir`. Es el bucle que impide que se acumulen enlaces muertos.
6. **El camino bueno a escala es la Product Advertising API** (la oficial del programa
   de afiliados): devuelve disponibilidad y precio estructurados por ASIN, sin parsear
   HTML y sin bloqueos. Requiere acceso aprobado del programa; mientras no lo haya,
   navegador real priorizado por tandas.

## GitHub Actions y Cloudflare (mismo día)
El token de Cloudflare **funciona**: verificado con la API (Pages 200), con wrangler
(`whoami` autentica) y con un deploy real desde el PC (`pages deploy` → success).
En GitHub Actions el **mismo token** (hash verificado idéntico) responde **401
Authentication error**. Descartado el account ID (uno incorrecto daría 403, probado).
Hipótesis principal: el token tiene **restricción por IP** — funciona desde la red de
David, no desde las IPs de los runners. Alternativa mejor a largo plazo: conectar el
repo a Cloudflare Pages por integración Git (despliega sin token ni workflow).
