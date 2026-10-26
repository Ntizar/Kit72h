/* Kit72h — worker-eventos: contador del funnel sin cookies, sin PII y sin
 * dependencias externas. Compañero de js/analiticas.js en el navegador.
 *
 * Qué guarda: recuentos por día de los eventos del funnel —
 *   clic-amazon (intención de compra), scroll-50 y scroll-90 (lectura).
 * La clave de KV es el día (d:YYYY-MM-DD) y el valor un mapa
 *   "evento|ruta"          → n
 *   "evento|ruta|pos-N"    → n   (posición del enlace clicado, opcional)
 * Un solo write por POST (el navegador agrupa eventos en lotes) → holgado
 * para el free tier de KV (1.000 writes/día). Carrera de escritura entre dos
 * POST simultáneos puede perder un recuento: aceptado a este volumen.
 *
 * Endpoints:
 *   GET  /                 → "ok" (healthcheck, sin auth)
 *   POST /e                → ingesta {"e":[{"n","p","q"}]} (solo desde kit72h.com)
 *   GET  /resumen?dias=30  → agregado al contrato de data/analiticas.json
 *                            (Authorization: Bearer <TOKEN>)
 *
 * Secretos: TOKEN (mismo valor que KIT72H_EVENTOS_TOKEN del .env del repo).
 * Bindings: EVENTOS = namespace KV.
 * Sin PII: solo se guardan ruta y recuento. La IP nunca se escribe.
 */

const ORIGEN = "https://kit72h.com";
const HOST = "kit72h.com";
const EVENTOS_VALIDOS = ["clic-amazon", "scroll-50", "scroll-90"];
const MAX_POR_POST = 20;
const MAX_RUTA = 200;

function respuesta(cuerpo, estado, extra) {
  const cab = { "Content-Type": "application/json; charset=utf-8" };
  if (extra) { for (const k in extra) { cab[k] = extra[k]; } }
  return new Response(JSON.stringify(cuerpo), { status: estado, headers: cab });
}

function rutaLimpia(p) {
  if (typeof p !== "string" || p.charAt(0) !== "/" || p.length > MAX_RUTA) { return null; }
  if (p.indexOf("://") !== -1) { return null; }
  return p.replace(/\/index\.html$/, "/");
}

/* Solo aceptamos eventos del propio sitio (el navegador manda Origin en los
 * POST cross-origin; Referer como reserva). Un curl falsificado podría saltarse
 * esto, pero el único daño posible es inflar nuestras propias métricas. */
function esDeLaWeb(request) {
  if (request.headers.get("Origin") === ORIGEN) { return true; }
  const ref = request.headers.get("Referer") || "";
  return ref.indexOf("https://" + HOST + "/") === 0 || ref.indexOf("https://" + HOST + ":") === 0;
}

async function ingestar(request, env) {
  if (!env || !env.EVENTOS) { return respuesta({ error: "KV no configurado" }, 500); }
  const cors = { "Access-Control-Allow-Origin": ORIGEN };
  if (request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": ORIGEN,
        "Access-Control-Allow-Methods": "POST",
        "Access-Control-Max-Age": "86400",
      },
    });
  }
  if (!esDeLaWeb(request)) { return respuesta({ error: "origen no permitido" }, 403, cors); }
  let crudo = null;
  try { crudo = await request.text(); } catch (e) { return respuesta({ error: "cuerpo ilegible" }, 400, cors); }
  if (!crudo || crudo.length > 4096) { return respuesta({ error: "cuerpo fuera de tamaño" }, 413, cors); }
  let datos = null;
  try { datos = JSON.parse(crudo); } catch (e) { return respuesta({ error: "JSON invalido" }, 400, cors); }
  const lote = Array.isArray(datos && datos.e) ? datos.e.slice(0, MAX_POR_POST) : null;
  if (!lote || !lote.length) { return respuesta({ error: "sin eventos" }, 400, cors); }

  const hoy = new Date().toISOString().slice(0, 10);
  const clave = "d:" + hoy;
  let mapa = null;
  try { mapa = await env.EVENTOS.get(clave, "json"); } catch (e) { mapa = null; }
  if (!mapa || typeof mapa !== "object" || Array.isArray(mapa)) { mapa = {}; }

  let aceptados = 0;
  for (const ev of lote) {
    if (!ev || typeof ev !== "object") { continue; }
    const n = EVENTOS_VALIDOS.indexOf(ev.n) !== -1 ? ev.n : null;
    const p = rutaLimpia(ev.p);
    if (!n || !p) { continue; }
    // El recuento base siempre; la posición del enlace, además (desglose).
    mapa[n + "|" + p] = (mapa[n + "|" + p] || 0) + 1;
    if (ev.q !== undefined && ev.q !== null) {
      const qi = Math.floor(Number(ev.q));
      if (isFinite(qi) && qi >= 1 && qi <= 999) {
        mapa[n + "|" + p + "|pos-" + qi] = (mapa[n + "|" + p + "|pos-" + qi] || 0) + 1;
      }
    }
    aceptados += 1;
  }
  if (aceptados > 0) {
    try {
      await env.EVENTOS.put(clave, JSON.stringify(mapa));
    } catch (e) {
      return respuesta({ error: "no se pudo escribir en KV" }, 500, cors);
    }
  }
  return new Response(null, { status: 204, headers: cors });
}

async function resumen(request, url, env) {
  if (!env || !env.EVENTOS) { return respuesta({ error: "KV no configurado" }, 500); }
  if (!env.TOKEN) {
    return respuesta({ error: "TOKEN sin configurar (wrangler secret put TOKEN)" }, 500);
  }
  const auth = request.headers.get("Authorization") || "";
  if (auth !== "Bearer " + env.TOKEN) { return respuesta({ error: "no autorizado" }, 401); }

  let dias = Math.floor(Number(url.searchParams.get("dias") || "30"));
  if (!isFinite(dias) || dias < 1) { dias = 30; }
  if (dias > 400) { dias = 400; }
  const desde = new Date(Date.now() - (dias - 1) * 86400000).toISOString().slice(0, 10);

  // Recorrido de todas las claves diarias (d:) dentro de la ventana.
  const mapa = {};
  let cursor;
  for (;;) {
    const lista = await env.EVENTOS.list({ prefix: "d:", cursor: cursor });
    for (const k of lista.keys) {
      if (k.name.slice(2) < desde) { continue; }
      let dia = null;
      try { dia = await env.EVENTOS.get(k.name, "json"); } catch (e) { dia = null; }
      if (!dia || typeof dia !== "object" || Array.isArray(dia)) { continue; }
      for (const clave in dia) {
        const n = dia[clave];
        if (typeof n !== "number" || !isFinite(n)) { continue; }
        mapa[clave] = (mapa[clave] || 0) + n;
      }
    }
    if (lista.list_complete) { break; }
    cursor = lista.cursor;
  }

  // Separa los recuentos por posición del enlace (claves …|pos-N).
  const normal = {};
  const posiciones = {};
  for (const clave in mapa) {
    const m = /^(.*)\|pos-(\d+)$/.exec(clave);
    if (m) {
      if (!posiciones[m[1]]) { posiciones[m[1]] = {}; }
      posiciones[m[1]][m[2]] = (posiciones[m[1]][m[2]] || 0) + mapa[clave];
    } else {
      normal[clave] = (normal[clave] || 0) + mapa[clave];
    }
  }

  // Normaliza al contrato de data/analiticas.json:
  // eventos: [{nombre, total, por_pagina: [{ruta, total}], por_posicion?: [{pos, total}]}]
  const claves = Object.keys(normal).sort((a, b) => normal[b] - normal[a] || (a < b ? -1 : 1));
  const acumulado = {};
  for (const clave of claves) {
    const corte = clave.indexOf("|");
    const nombre = clave.slice(0, corte) || "evento";
    const ruta2 = clave.slice(corte + 1) || "/";
    if (!acumulado[nombre]) { acumulado[nombre] = { total: 0, paginas: {} }; }
    acumulado[nombre].total += normal[clave];
    acumulado[nombre].paginas[ruta2] = (acumulado[nombre].paginas[ruta2] || 0) + normal[clave];
  }

  const eventos = [];
  for (const nombre in acumulado) {
    const datos = acumulado[nombre];
    const por_pagina = Object.keys(datos.paginas)
      .sort((a, b) => datos.paginas[b] - datos.paginas[a] || (a < b ? -1 : 1))
      .map((ruta2) => ({ ruta: ruta2, total: datos.paginas[ruta2] }));
    const ev = { nombre: nombre, total: datos.total, por_pagina: por_pagina };

    const posGlobal = {};
    for (const clave2 in posiciones) {
      if (clave2.indexOf(nombre + "|") !== 0) { continue; }
      for (const pos in posiciones[clave2]) {
        posGlobal[pos] = (posGlobal[pos] || 0) + posiciones[clave2][pos];
      }
    }
    const posLista = Object.keys(posGlobal)
      .sort((a, b) => Number(a) - Number(b))
      .map((pos) => ({ pos: Number(pos), total: posGlobal[pos] }));
    if (posLista.length) { ev.por_posicion = posLista; }
    eventos.push(ev);
  }

  return respuesta({
    generado: new Date().toISOString().replace(/\.\d+Z$/, "Z"),
    dias: dias,
    eventos: eventos,
  }, 200);
}

export default {
  async fetch(request, env) {
    try {
      const url = new URL(request.url);
      if (request.method === "GET" && url.pathname === "/") {
        return new Response("ok", { headers: { "Content-Type": "text/plain; charset=utf-8" } });
      }
      if (request.method === "POST" && url.pathname === "/e") { return await ingestar(request, env); }
      if (request.method === "GET" && url.pathname === "/resumen") { return await resumen(request, url, env); }
      return respuesta({ error: "ruta no encontrada" }, 404);
    } catch (e) {
      return respuesta({ error: "error interno: " + String((e && e.message) || e) }, 500);
    }
  },
};
