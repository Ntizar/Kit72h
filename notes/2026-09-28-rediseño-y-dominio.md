# 2026-09-28 — Rediseño «Manual de campaña» + dominio kit72h.com

- Estética elegida: la maqueta 003 (cuaderno de campo). Papel crema sobre noche,
  Georgia + Rubik Dirt + Barlow Condensed, índice numerado, checkbox en listas,
  print como hoja de campo. Three.js y fondo procedural JUBILADOS (js/fondo.js
  queda huérfano en el repo, sin referencias — borrar en próxima limpieza).
- Dominio: kit72h.com comprado por David en Cloudflare. CNAME en repo,
  `cname` fijado por API de GitHub. Falta DNS (David, en el dashboard):
  A @ → 185.199.108.153/109/110.111 + AAAA @ → 2606:ef50:3100:901f::1/2
  (o CNAME www → ntizar.github.io) con proxy DNS-only; luego activar HTTPS.
- Turnstile de dash.cloudflare.com bloquea el navegador automatizado: la gestión
  DNS en Cloudflare es manual siempre (no perder tiempo intentándolo).
- Fuente de dominio en SEO: scripts/generar-seo.py BASE=https://kit72h.com.
- Precios de registradores verificados ( Porkbun NO vende .es; .es gratis año 1
  en dominios.es → 14,08 € renovación; STRATO .es 0,96 €/4,92 €; Cloudflare .com
  ~10,44 USD plano) → skill nichos-afiliacion-web.
- ACTUALIZACIÓN: David pasó token de Cloudflare → guardado en .env de Hermes
  (CLOUDFLARE_API_TOKEN, nunca en el repo). Zona kit72h.com active, 0 registros.
  DNS pendiente por bloqueo de aprobaciones → script idempotente listo:
  `python scripts/crear-dns-cloudflare.py` (crea A+AAAA+www, salta existentes).
