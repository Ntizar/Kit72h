# Crons de Kit72h

Los 7 trabajos programados que tocan esta web. Qué hace cada uno, a qué hora, con qué modelo y cuántos tokens se gastan.

> **Medido, no estimado.** Los tokens salen de `%LOCALAPPDATA%\hermes\cron\usage_audit.jsonl`. El estado y los horarios salen de `%LOCALAPPDATA%\hermes\cron\jobs.json`.

---

## Resumen

| Cron | Cuándo | Tipo | Estado |
|---|---|---|---|
| `kit72h-comparador` | diario 04:00 | LLM | ✅ |
| `kit72h-editor` | diario 04:30 | LLM | ✅ (prioridad: comparativas) |
| `kit72h-buscador` | diario 05:15 | script | ✅ |
| `kit72h-seo-audit` | diario 06:00 | script | ✅ |
| `kit72h-seo-ctr` | diario 06:30 | LLM | ✅ |
| `kit72h-ofertas` | diario 07:00 | LLM | ✅ |
| `kit72h-vigilante` | lunes 09:00 | LLM | ✅ (reactivado) |
| `kit72h-pins` | diario 08:00 | script | ✅ **NUEVO** |
| `kit72h-revision-urls` | 15 mes 09:00 | LLM | ✅ (bonus) |

**8 crons activos + 1 bonus.** Todos verdes.

---

## El sistema de tráfico (Pinterest + SEO)

```
08:00  pins           script   → 63 pins Pinterest HTML + PNG (kits + blog)
```

**Pinterest** = 500M+ usuarios, pins con vida de meses/años (no horas como Twitter).
Cada pin genera una tarjeta visual que enlaza a una página de kit72h.com.

**Cómo funciona:**
1. `generar-pins.py` genera HTML de pins (1000x1500px, estilo Aurora 7)
2. Cada pin enlaza a un kit o blog con URL real (63 URLs verificadas 200)
3. **Render automático HTML → PNG 1000x1500** (Chromium headless) → listo para subir
4. Se ejecuta cada noche → pins nuevos si hay contenido nuevo

**63 pins en el catálogo:** 19 kits + 44 blog entries. Los PNG viven en `pintout/`.

### Otros crons de venta

| Cron | Qué hace | Impacto en ventas |
|---|---|---|
| `comparador` | Genera páginas "Mejor X", "Top 5", "A vs B" | 🔴 Conversión directa |
| `seo-ctr` | Optimiza títulos y descriptions para CTR | 🟠 Más clics desde Google |
| `ofertas` | Monitoriza deals Amazon → pin en home | 🟠 Urgencia → clic → compra |
| `pins` | Genera pins Pinterest → tráfico masivo | 🟠 500M+ usuarios Pinterest |
| `editor` | Escribe blogs con prioridad comparativas | 🔴 Contenido de conversión |

---

## La cadena nocturna (diario)

```
04:00  comparador     LLM      → genera comparativas (mejor X, top 5, A vs B)
04:30  editor         LLM      → escribe/amplía blog (prioridad: comparativas)
05:15  buscador       script   → resuelve ASINs, regenera SEO+prerender
06:00  seo-audit      script   → auditoría SEO + auto-repara prerender
06:30  seo-ctr        LLM      → optimiza meta tags para CTR
07:00  ofertas        LLM      → monitoriza deals, inserta pin de ofertas
08:00  pins           script   → genera pins Pinterest (kits + blog)
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
