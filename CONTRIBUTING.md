# Kit72h - Sistema de automatización automática

## Workflow de GitHub Actions (auto-content.yml)
- **Lunes y Jueves a las 06:00 CET**: Genera nuevos artículos de blog
- **Miércoles a las 12:00 CET**: Genera pines para Pinterest
- **Cada ejecución**: Actualiza el sitemap

## Scripts principales
- `scripts/generar-articulos.py`: Crea artículos con SEO completo (schemas, OG, Twitter cards)
- `scripts/generar-pins.py`: Genera 3 variantes de pin por artículo (diseño Aurora 7)
- `scripts/actualizar-sitemap.py`: Actualiza el sitemap con nuevos artículos

## Cómo añadir nuevo contenido
1. Añadir artículo a la lista `ARTICLES` en `scripts/generar-articulos.py`
2. Ejecutar `python scripts/generar-articulos.py` (o esperar al cron)

## Contenido generado automáticamente
- HTML con SEO completo (schema.org, Open Graph, Twitter Cards)
- 3 variantes de pin para Pinterest (rojo, ámbar, negro)
- Sitemap.xml actualizado
- Push a GitHub para deploy automático