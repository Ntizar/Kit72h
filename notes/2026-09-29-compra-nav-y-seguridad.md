# De «tachar» a «comprar», cabecera a una fila y auditoría de seguridad (2026-09-29)

## 1. El sistema de tachado se quitó entero

La ficha de kit tenía un checkbox por producto, una barra de progreso pegajosa con
`17% · 2/12 IMPRESCINDIBLES LISTOS` y el texto «marca lo que ya tienes». Eso invita a
hacer inventario, no a comprar.

Además **no servía para nada funcional**: `ui.armarCesta()` nunca leía los checkboxes —
recorría `data/kits.json` directamente. El tachado era cosmético puro, con su estado y su
lógica encima.

Cambios:

- Sin checkboxes y sin `progresoInit()`.
- La barra pasa a **`16 PRODUCTOS · 12 IMPRESCINDIBLES` + «Llévate todo el kit →»**.
- La etiqueta ESENCIAL se mantiene: informa sobre la compra, no sobre el tachado.
- CSS muerto fuera: `.prueba`, `.pr-check`, `.adapt-grid`, `.card-adapt`, `.track`, `.fill`.

Regla que se extrae: **si un control no cambia nada de lo que el usuario consigue, es
ruido** — y en una web de emergencia el ruido cuesta más caro que en otro sitio.

## 2. Cabecera en móvil: una sola fila

Antes el `nav` saltaba a una segunda fila (`width:100%`) con las pestañas grandes. Ahora,
con `flex-wrap:nowrap`, logo + 5 enlaces caben juntos.

Medido a 360 px con métricas de dispositivo en el navegador:

| Métrica | Valor |
|---|---|
| Filas de enlaces visibles | **1** |
| Derecha del último enlace | 352 px de 360 |
| Overflow horizontal | no |
| Altura de la cabecera | 54 px |
| Botón «Compra tu kit» | oculto en móvil (ya está en el hero) |

## 3. `/fuentes/` de 5 a 27 entradas

Antes: cinco enlaces en una lista plana. Ahora **8 grupos con contador** (Unión Europea 4,
Protección Civil 4, Sanidad 4, Meteorología 2, Suministros 3, Seguridad 3, Normativa 2,
Datos del mapa 5) y **una nota por fuente** explicando para qué sirve en este sitio.

**Ninguna URL se mete sin comprobarla.** De 30 candidatas: 26 con 200, 2 con 403 de WAF
(se mantienen: `interior.gob.es` y `consilium.europa.eu` existen y solo bloquean al robot),
`guardiacivil.es` verificado aparte, y **descartadas las cinco que daban 404** (un par de
rutas de Protección Civil y Sanidad que ya no existen, y tres intentos de página del 112
europeo). De paso quedó confirmada la regla del repo: probar antes de publicar.

## 4. Auditoría de seguridad del repo público

`Ntizar/Kit72h` es **público**. Barrido de los 146 ficheros trackeados con patrones de
token (GitHub, OpenAI/NaN, Bearer, Cloudflare, AWS, Telegram, private keys, contraseñas,
cookies de Amazon, rutas de Windows, correos):

- **Cero tokens, cero claves, cero cookies.** El historial de git nunca contuvo `.env` ni
  cookies (`amz_cookies.txt` está en `.gitignore` y no se commiteó jamás).
- Los dos workflows usan `${{ secrets.* }}`; `crear-dns-cloudflare.py` lee el token del
  `.env`, no lo lleva dentro.
- «David Antizar» no aparece en `data/`, `js/ ni `index.html`.

Lo que sí había que arreglar:

1. `CRONS.md` y los tres scripts de cron contenían la **ruta personal de Windows**
   (`C:\Users\...`). Documentación y scripts pasan a `%LOCALAPPDATA%` y `Path.home()`.
2. `data/fichas.db` estaba **trackeado** aunque `.gitignore` lo excluía: SQLite generado
   por `verificar-fichas.py`. Baja con `git rm --cached` (el fichero sigue en disco).

Los correos que salen en `data/snapshots/` son direcciones públicas de Protección Civil:
no son PII.

## 5. README

Se fue el bloque «Flujo de una edición (checklist)» con su lista de comandos — no
comunicaba nada. Ahora el fichero tiene dos partes: qué es y dónde se edita cada cosa, y
una sección nueva **«Replicar este patrón en otra web»** con qué copiar, los tres
literales que hay que tocar en el prerender, identidad, contenido en `data/` y la lista
de comprobaciones previas a dar un cambio por bueno.

Punto técnico que se documenta ahí: los `assert` del prerender deben usar una marca
**exclusiva** de cada página. Con una marca compartida el test pasa aunque la página
salga equivocada — así el índice del blog estuvo renderizando la portada durante semanas
sin que la comprobación cantara.

---

Verificación final: prerender 51 rutas / 0 fallos · `kit72h-seo-audit` verde (51/51) ·
en vivo 0 checkboxes en el kit, 16 «Comprar ↗», 8 grupos y 27 enlaces en `/fuentes/`,
home en 4 secciones · Deploy GitHub Pages success.

Hecho con ❤️ por David Antizar
