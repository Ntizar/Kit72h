# Crons de Kit72h

Los 7 trabajos programados que tocan esta web. Qué hace cada uno, a qué hora, con qué modelo y cuántos tokens se gastan.

> **Medido, no estimado.** Los tokens salen de `%LOCALAPPDATA%\hermes\cron\usage_audit.jsonl`. El estado y los horarios salen de `%LOCALAPPDATA%\hermes\cron\jobs.json`.

---

## Resumen

| Cron | Cuándo | Tipo | Estado |
|---|---|---|---|
| `kit72h-comparador` | diario 04:00 | LLM | ✅ **NUEVO** |
| `kit72h-editor` | diario 04:30 | LLM | ✅ EDITADO (prioridad: comparativas) |
| `kit72h-buscador` | diario 05:15 | script | ✅ OK |
| `kit72h-seo-audit` | diario 06:00 | script | ✅ OK (regex JSON-LD arreglado) |
| `kit72h-seo-ctr` | diario 06:30 | LLM | ✅ **NUEVO** |
| `kit72h-ofertas` | diario 07:00 | LLM | ✅ **NUEVO** |
| `kit72h-vigilante` | lunes 09:00 | LLM | ✅ **REACTIVADO** |
| `kit72h-revision-urls` | 15 mes 09:00 | LLM | ✅ OK (bonus) |

**Todos verdes.** Cadena nocturna: comparador → editor → buscador → seo-audit → seo-ctr → ofertas.

---

## La cadena nocturna (diario)

```
04:00  comparador     LLM      → genera comparativas (mejor X, top 5, A vs B)
04:30  editor         LLM      → escribe/amplía blog (prioridad: comparativas)
05:15  buscador       script   → resuelve ASINs, regenera SEO+prerender
06:00  seo-audit      script   → auditoría SEO + auto-repara prerender
06:30  seo-ctr        LLM      → optimiza meta tags para CTR
07:00  ofertas        LLM      → monitoriza deals, inserta pin de ofertas
09:00  vigilante      LLM      → lunes: chequeo completo semanal
```

---

## Nuevos crons

### `kit72h-comparador` (04:00)

Genera páginas de comparativas para conversión: "Mejor linterna 2026", "Kit 72h vs 30 días", "Starlink vs radio satelital". Cada comparativa tiene tabla + links de afiliado → clicks → ventas.

### `kit72h-seo-ctr` (06:30)

Optimiza meta tags: títulos `[N] + keyword + beneficio + año` y descriptions `[problema] + [solución] + [urgencia]` para maximizar CTR en Google.

### `kit72h-ofertas` (07:00)

Monitoriza bajadas de precio >15% en productos Amazon. Inserta pin de ofertas en la home → urgencia → clic → compra.

---

## Arreglos del día (2026-10-02)

| Fix | Impacto |
|---|---|
| JSON-LD roto: `\\+json` → `\+json` | ✅ SEO-audit pasa |
| ItemList eliminado del prerender | ✅ generar-seo.py con fallback automático |
| Blog sin campo `fecha` | ✅ Todos los posts tienen fecha |
| Blog con `{{author}}` y "David Antizar" | ✅ 7 posts limpiados |
| blog/index.html sin canonical | ✅ Añadido |
| vigilante pausado (402 qwen3.8-flash) | ✅ Reactivado en mimo-v2.6-flash |
| revision-urls + vigilante a la hora | ✅ Desfasado al día 15 |

---

## Cómo volver a medir

```bash
python scripts/auditar-crons.py --kit --runs   # detalle por cron
hermes cron list   # estado de todos los jobs
```

---

Hecho con ❤️ por David Antizar
