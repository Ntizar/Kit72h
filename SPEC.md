# KitsEmergencia.es — SPEC v1.0

## Visión
Web de referencia en castellano para **kits de emergencia** con fuente de verdad oficial (Protección Civil / Ministerio del Interior) + productos reales Amazon con enlaces de afiliado. Publicación automática nocturna vía cron + informe Telegram.

## Alcance

### Sí hace
- Web estática con 6-8 kits de emergencia: DANA, apagón, coche, hogar, montaña, evacuación, calor/ola de calor, terremoto
- Cada kit: lista oficial Protección Civil + productos Amazon recomendados (enlace de afiliado) + checklist descargable
- Guías antes/durante/después por tipo de emergencia
- Página "Fuentes oficiales" (transparencia → confianza → SEO)
- Contenido en `data/kits.json` generado/mantenido por cron nocturno
- Informe Telegram nocturno: cambios detectados en fuentes oficiales, páginas nuevas, estado del sitio

### NO hace (non-goals)
- Backend, login, usuarios, base de datos
- Carrito o compra directa (enlaces a Amazon)
- Contenido generado sin fuente oficial verificable
- Afiliación Awin/TravelPayouts en v1 (solo Amazon Afiliados)

## Pantallas
1. **Home**: grid de kits por tipo de emergencia + banner "fuente: Protección Civil"
2. **Ficha de kit**: lista oficial + productos + checklist descargable + guías antes/durante/después
3. **Guías**: qué hacer antes/durante/después por emergencia
4. **Fuentes oficiales**: lista de enlaces a Protección Civil, DG Protección Civil, Ministerio del Interior

## Datos
| Fuente | Tipo | Actualización | Volumen |
|--------|------|---------------|---------|
| Protección Civil (recomendaciones oficiales) | scrape/web | nocturna | ~8 listas oficiales |
| Amazon Afiliados | enlaces manuales en JSON | manual | ~10-20 productos/kit |

## Arquitectura

### Capas
| Capa | Archivo | Responsabilidad |
|------|---------|----------------|
| Datos | `data/kits.json` | Kits, productos, fuentes |
| Estado | `js/state.js` | Carga del JSON y estado |
| UI | `js/ui.js` | Render de kits, fichas, guías |
| Render | `js/render.js` | Checklists, enlaces de afiliado, print |
| Entry | `index.html` | Estructura DOM |
| Estilos | `css/styles.css` | Diseño (fondo blanco, sin dark, sin liquid glass) |

### Estado global
JSON único `data/kits.json` → state.js carga al iniciar → ui.js renderiza.

### Cron nocturno (Hermes)
- Descarga/revisa fuentes oficiales (Protección Civil)
- Compara con data/kits.json
- Si hay cambios → actualiza JSON, commit, push, deploy automático GitHub Pages
- Envía informe Telegram: cambios detectados, páginas nuevas, estado OK/error

## Stack
- Frontend: HTML/CSS/JS vanilla
- Datos: JSON estático
- Deploy: GitHub Pages (actions/deploy-pages@v4)
- Automatización: cron Hermes

## Criterios de éxito
- Carga < 2s (estático puro)
- Cada producto con enlace de afiliado correcto y disclosure legal (obligatorio Amazon)
- 6-8 kits publicados con fuente oficial citada
- Cron nocturno activo e informe Telegram operativo
- Mobile-first

## Anti-patrones (lo que evitamos)
- Contenido AI sin fuente oficial citada → riesgo de desindexación
- Dark theme / liquid glass / border-left cards (rechazado por David)
- Pestañas con datos hardcodeados inútiles
- Subagentes para archivos > 3000 líneas
- Enlaces de afiliado sin disclosure legal

## Referencias
- Diseño: preferencias David (fondo blanco, sombras sutiles, hover elevación, tipografía compacta, azul #2563eb)
- Proyectos similares: DataHubEspana (static digest), ISOTime (isócronas)
- Atribución: "Hecho con ❤️ por David Antizar"
