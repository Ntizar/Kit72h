/* Kit72h — analítica sin cookies, sin PII y sin dependencias.
 *
 * Un solo fichero que carga el proveedor que esté configurado abajo y añade
 * los eventos que de verdad importan en esta web: el CLIC AL ENLACE DE AMAZON
 * (el momento en el que se puede ganar dinero) y la profundidad de scroll.
 *
 * Reglas:
 *  - Nada de cookies, localStorage ni huella de navegador.
 *  - Solo se envía la RUTA (location.pathname), nunca la query (jamás un dato
 *    de búsqueda del usuario).
 *  - Si no hay proveedor configurado, este fichero no hace ABSOLUTAMENTE NADA
 *    (ni una petición de red) y no rompe nada.
 *
 * Para activarlo: rellenar CONFIG.beacon_cloudflare (Cloudflare Web Analytics)
 * o CONFIG.umami.website_id (Umami Cloud, permite eventos personalizados) o
 * CONFIG.goatcounter.code. Ver notes/2026-10-12-analitica-kit72h.md
 */
(function () {
  "use strict";

  var CONFIG = {
    // Cloudflare Web Analytics: token del beacon (Web Analytics > kit72h.com).
    // Da visitas, páginas, referrers, países y dispositivos. Sin cookies.
    beacon_cloudflare: "2cd51d4e9fe241849269fc0bed3083cc",
    // Umami Cloud (opcional): permite EVENTOS personalizados (clic a Amazon).
    umami: { website_id: "", src: "https://cloud.umami.is/script.js" },
    // GoatCounter (opcional): alternativa gratuita con eventos.
    goatcounter: { code: "" },
    // Interruptor maestro para los eventos de clic/scroll (independiente del
    // proveedor: solo se envían si hay uno con soporte de eventos).
    eventos: true
  };

  function cargar(src, atributos) {
    try {
      // TRAMPA EVITADA: este sitio se re-hornea cada noche con Chromium
      // (scripts/prerender.py) y lo que el JS añade al DOM al vuelo queda
      // escrito en el HTML estático. Sin esta guarda, el beacon acabaría
      // DUPLICADO (y las visitas contadas dos veces). Nunca añadir si ya
      // existe una etiqueta con ese src.
      if (document.querySelector('script[src="' + src + '"]')) { return; }
      var s = document.createElement("script");
      s.async = true;
      s.defer = true;
      s.src = src;
      if (atributos) {
        for (var k in atributos) {
          if (Object.prototype.hasOwnProperty.call(atributos, k)) {
            s.setAttribute(k, atributos[k]);
          }
        }
      }
      (document.head || document.documentElement).appendChild(s);
    } catch (e) { /* nunca romper la página por analítica */ }
  }

  // --- Proveedores de visitas -------------------------------------------
  var hayEventos = false;

  if (CONFIG.beacon_cloudflare) {
    cargar("https://static.cloudflareinsights.com/beacon.min.js", {
      "data-cf-beacon": JSON.stringify({ token: CONFIG.beacon_cloudflare })
    });
  }

  if (CONFIG.umami && CONFIG.umami.website_id) {
    cargar(CONFIG.umami.src, {
      "data-website-id": CONFIG.umami.website_id,
      "data-do-not-track": "true"
    });
    hayEventos = true;
  }

  if (CONFIG.goatcounter && CONFIG.goatcounter.code) {
    window.goatcounter = { no_onload: false };
    cargar("https://gc.zgo.at/count.js", {
      "data-goatcounter": "https://" + CONFIG.goatcounter.code + ".goatcounter.com/count"
    });
    hayEventos = true;
  }

  // --- Eventos: lo que de verdad mueve la aguja --------------------------
  function evento(nombre, datos) {
    if (!CONFIG.eventos || !hayEventos) { return; }
    try {
      if (window.umami && typeof window.umami.track === "function") {
        window.umami.track(nombre, datos || {});
      } else if (window.goatcounter && typeof window.goatcounter.count === "function") {
        var etiqueta = nombre;
        if (datos && datos.pagina) { etiqueta += " " + datos.pagina; }
        window.goatcounter.count({ path: etiqueta, title: nombre, event: true });
      }
    } catch (e) { /* silencio */ }
  }

  function ruta() {
    try {
      // Normaliza /kit/kit-apagon/index.html → /kit/kit-apagon/ para que las
      // dos formas de URL no partan las estadísticas de una misma página.
      return location.pathname.replace(/\/index\.html$/, "/");
    } catch (e) { return "/"; }
  }

  // Clic en un enlace de afiliado de Amazon = intención de compra.
  function esAfiliado(a) {
    if (!a || !a.href) { return false; }
    if (a.href.indexOf("amazon.") === -1) { return false; }
    return a.href.indexOf("tag=ntizar-21") !== -1;
  }

  function initClics() {
    document.addEventListener("click", function (ev) {
      var a = ev.target;
      while (a && a.nodeName !== "A") { a = a.parentNode; }
      if (!esAfiliado(a)) { return; }
      var enlaces = document.querySelectorAll('a[href*="amazon."][href*="tag=ntizar-21"]');
      var posicion = 0;
      for (var i = 0; i < enlaces.length; i++) {
        if (enlaces[i] === a) { posicion = i + 1; break; }
      }
      evento("clic-amazon", { pagina: ruta(), posicion: posicion });
    }, true);
  }

  // Scroll: si alguien llega al 90% de una ficha, el contenido interesa.
  function initScroll() {
    var marcas = [50, 90];
    var vistas = {};
    function comprobar() {
      var alto = document.documentElement.scrollHeight - window.innerHeight;
      if (alto <= 0) { return; }
      var pct = (window.scrollY || window.pageYOffset || 0) / alto * 100;
      for (var i = 0; i < marcas.length; i++) {
        var m = marcas[i];
        if (pct >= m && !vistas[m]) {
          vistas[m] = true;
          evento("scroll-" + m, { pagina: ruta() });
        }
      }
    }
    window.addEventListener("scroll", comprobar, { passive: true });
  }

  function arrancar() {
    try {
      if (CONFIG.eventos) { initClics(); initScroll(); }
    } catch (e) { /* silencio */ }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", arrancar);
  } else {
    arrancar();
  }
})();
