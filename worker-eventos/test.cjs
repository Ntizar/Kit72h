/* Test del worker-eventos con KV simulado (Map) — Node puro, sin dependencias.
 * Cubre: POST válido (204, cero ops KV en el camino), umbral de eventos (50),
 * contenido exacto del volcado (prefijo d:), fundir() sobre mapa plano,
 * vencimiento temporal (con FLUSH_SECS acortado) y cache del resumen
 * (2ª lectura = 0 ops nuevas).
 * Uso: node test.cjs  (VM: ~/.hermes/node/bin/node)
 */
const assert = require("assert");
const fs = require("fs");
const path = require("path");

const CODIGO = fs.readFileSync(path.join(__dirname, "src", "index.js"), "utf8");
// Convertir el módulo ES en evaluable: export default → return del objeto.
function cargar(remplazos) {
  let cuerpo = CODIGO;
  for (const [de, a] of remplazos || []) { cuerpo = cuerpo.replace(de, a); }
  return new Function(cuerpo.replace(/export default/, "return"))();
}

/* ── KV simulado ─────────────────────────────────────────────────────────── */
function mockKV() {
  const store = new Map();
  const ops = { get: 0, put: 0, list: 0 };
  return {
    ops,
    store,
    async get(clave) {
      ops.get += 1;
      if (!store.has(clave)) { return null; }
      return JSON.parse(store.get(clave));
    },
    async put(clave, valor) { ops.put += 1; store.set(clave, valor); },
    async list(opts) {
      ops.list += 1;
      const pref = (opts && opts.prefix) || "";
      const claves = [...store.keys()].filter((k) => k.indexOf(pref) === 0).sort().map((name) => ({ name }));
      return { keys: claves, list_complete: true };
    },
  };
}

function mockCtx() {
  const pendientes = [];
  return {
    waitUntil: (p) => pendientes.push(p),
    _drenar: async () => { while (pendientes.length) { await pendientes.shift(); } },
  };
}

const envMock = () => ({ EVENTOS: mockKV(), TOKEN: "t-token-test" });
const post = (body) => new Request("https://kit72h-eventos.example/e", {
  method: "POST",
  headers: { "Origin": "https://kit72h.com" },
  body: JSON.stringify(body),
});
const HOY = new Date().toISOString().slice(0, 10);

/* ── Tests ───────────────────────────────────────────────────────────────── */
async function main() {
  // 1. POST válido → 204 y NADA de KV en el camino de respuesta.
  {
    const env = envMock();
    const ctx = mockCtx();
    const r = await worker.fetch(post({ e: [{ n: "clic-amazon", p: "/kit/kit-apagon/" }] }), env, ctx);
    assert.strictEqual(r.status, 204);
    await ctx._drenar();
    assert.strictEqual(env.EVENTOS.ops.put, 0, "el POST no debe escribir a KV (flush diferido)");
    assert.strictEqual(env.EVENTOS.ops.get, 0, "el POST no debe leer KV");
  }

  // 2. Umbral de eventos (50) → 1 write con clave d: y contenido fundido.
  //    MAX_POR_POST=20: cada POST llega recortado a 20 eventos → 3 POSTs = 60.
  {
    const env = envMock();
    const ctx = mockCtx();
    const lote = [];
    for (let i = 0; i < 20; i++) {
      lote.push({ n: "clic-amazon", p: "/kit/kit-apagon/", q: 2 });
    }
    for (let i = 0; i < 3; i++) { await worker.fetch(post({ e: lote }), env, ctx); }
    await ctx._drenar();
    assert.strictEqual(env.EVENTOS.ops.put, 1, "1 write por ráfaga (60 eventos)");
    assert.strictEqual(env.EVENTOS.ops.get, 1, "1 get read-modify-write");
    const guardado = env.EVENTOS.store.get("d:" + HOY);
    assert.ok(guardado, "la clave lleva prefijo d: (bug 26-10-29 cazado aquí)");
    const mapa = JSON.parse(guardado);
    // 61, no 60: el evento pendiente del bloque 1 viaja en este mismo flush
    // (los bloques comparten el worker y su MEMORIA global — comportamiento real).
    assert.strictEqual(mapa["clic-amazon|/kit/kit-apagon/"], 61);
    // 60 en pos-2: el residual del bloque 1 no llevaba q (posición).
    assert.strictEqual(mapa["clic-amazon|/kit/kit-apagon/|pos-2"], 60, "posición registrada");
  }

  // 3. fundir() sobre mapa existente: lo previo sobrevive, lo nuevo se suma.
  {
    const env = envMock();
    const ctx = mockCtx();
    env.EVENTOS.store.set("d:" + HOY, JSON.stringify({ "scroll-50|/": 7 }));
    const lote = [];
    for (let i = 0; i < 20; i++) { lote.push({ n: "scroll-90", p: "/" }); }
    for (let i = 0; i < 3; i++) { await worker.fetch(post({ e: lote }), env, ctx); }
    await ctx._drenar();
    const mapa = JSON.parse(env.EVENTOS.store.get("d:" + HOY));
    assert.strictEqual(mapa["scroll-50|/"], 7, "lo previo sobrevive (fundir no anida)");
    assert.strictEqual(mapa["scroll-90|/"], 60, "lo nuevo se suma");
  }

  // 4. Vencimiento temporal: instancia con FLUSH_SECS=1 (no se puede esperar
  //    1200 s en un test) → el flush por tiempo escribe lo pendiente.
  {
    const workerRapido = cargar([[/const FLUSH_SECS = 1200;/, "const FLUSH_SECS = 1;"]]);
    const env = envMock();
    const ctx = mockCtx();
    const r = await workerRapido.fetch(post({ e: [{ n: "scroll-50", p: "/" }] }), env, ctx);
    assert.strictEqual(r.status, 204);
    await new Promise((ok) => setTimeout(ok, 1500)); // > FLUSH_SECS
    await ctx._drenar();
    assert.ok(env.EVENTOS.ops.put >= 1, "el vencimiento temporal dispara el volcado");
  }

  // 5. Resumen: correcto y con cache de memoria (2ª llamada = 0 ops nuevas).
  {
    const env = envMock();
    const ctx = mockCtx();
    env.EVENTOS.store.set("d:2026-11-01", JSON.stringify({ "clic-amazon|/kit/x/": 3 }));
    env.EVENTOS.store.set("d:2026-11-02", JSON.stringify({ "clic-amazon|/kit/x/": 2, "scroll-50|/": 9 }));
    const req = () => new Request("https://kit72h-eventos.example/resumen?dias=30",
      { headers: { Authorization: "Bearer t-token-test" } });
    const r1 = await worker.fetch(req(), env, ctx);
    const j1 = await r1.json();
    assert.strictEqual(r1.status, 200);
    const clic = j1.eventos.find((e) => e.nombre === "clic-amazon");
    assert.strictEqual(clic.total, 5);
    const scroll = j1.eventos.find((e) => e.nombre === "scroll-50");
    assert.strictEqual(scroll.total, 9);
    const ops1 = { ...env.EVENTOS.ops };
    const r2 = await worker.fetch(req(), env, ctx);
    const j2 = await r2.json();
    assert.strictEqual(j2.eventos.find((e) => e.nombre === "clic-amazon").total, 5, "cache de memoria devuelve lo mismo");
    assert.strictEqual(env.EVENTOS.ops.list, ops1.list, "2ª lectura: 0 list");
    assert.strictEqual(env.EVENTOS.ops.get, ops1.get, "2ª lectura: 0 get");
    assert.strictEqual(r2.headers.get("X-Resumen-Cache"), "memoria");
    // 401 sin token
    const r3 = await worker.fetch(new Request("https://kit72h-eventos.example/resumen"), env, ctx);
    assert.strictEqual(r3.status, 401);
    // Origen ajeno rechazado
    const r4 = await worker.fetch(new Request("https://kit72h-eventos.example/e", {
      method: "POST", headers: { Origin: "https://malicioso.example" },
      body: JSON.stringify({ e: [{ n: "clic-amazon", p: "/" }] }),
    }), env, ctx);
    assert.strictEqual(r4.status, 403);
  }

  console.log("OK — todos los tests en verde (5 bloques)");
}

const worker = cargar();
main().catch((e) => { console.error("FALLO:", e.message); process.exit(1); });
