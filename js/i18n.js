/* Kit72h — i18n y mercados
   Un mercado = país + dominio de Amazon + idioma (data/mercados.json).
   Aquí vive TODO lo que cambia por país: textos de interfaz, moneda, número de
   emergencia, dominio y tag de afiliado. El código no debe hardcodear país nunca.

   Orden de carga: i18n.js antes que state.js/blog.js/ui.js/main.js. */
const i18n = {
  mercados: [],
  mercado: null,
  ui: {},          // textos del idioma activo
  base: {},        // textos en castellano: red de seguridad si falta una clave
  tiposCambio: {},
  listo: false,

  async init() {
    if (this.listo) return this;
    try {
      const [mr, es] = await Promise.all([
        fetch('/data/mercados.json'),
        fetch('/data/i18n/ui/es.json')
      ]);
      const m = await mr.json();
      this.mercados = (m.mercados || []).filter(x => x.activo !== false);
      this.tiposCambio = m.tiposCambio || {};
      this.base = await es.json();
      this.mercado = this.detectarMercado();
      this.ui = this.mercado.lang === 'es'
        ? this.base
        : await this.cargarTextos(this.mercado);
      this.listo = true;
    } catch (e) {
      // Sin mercados.json el sitio no puede quedarse en blanco: modo castellano.
      this.mercado = this.mercado || {
        id: 'es', ruta: '/', locale: 'es-ES', lang: 'es', contenido: 'es',
        paisLocal: 'España', bandera: '🇪🇸',
        amazon: { dominio: 'www.amazon.es', tag: 'ntizar-21', moneda: 'EUR', simbolo: '€' },
        emergencias: { numero: '112', nombre: '112' }
      };
      this.ui = this.base || {};
      this.listo = true;
    }
    return this;
  },

  /* El mercado se deduce del primer segmento de la URL. La raíz es España. */
  detectarMercado() {
    const p = location.pathname;
    const m = this.mercados
      .filter(x => x.ruta !== '/' && (p === x.ruta.replace(/\/$/, '') || p.startsWith(x.ruta)))
      .sort((a, b) => b.ruta.length - a.ruta.length)[0];
    return m || this.mercados.find(x => x.ruta === '/') || this.mercados[0];
  },

  mercadoPorId(id) {
    return this.mercados.find(x => x.id === id) || null;
  },

  async cargarTextos(mercado) {
    try {
      const r = await fetch(`/data/i18n/ui/${mercado.lang}.json`);
      if (r.ok) return Object.assign({}, this.base, await r.json());
    } catch (e) { /* idioma sin fichero: cae al castellano clave a clave */ }
    return this.base;
  },

  /* t('clave', {n: 3}) — sustituye {n} y cae al castellano si falta la clave. */
  t(clave, vars) {
    let s = this.ui[clave];
    if (s == null) s = this.base[clave];
    if (s == null) return clave;
    if (vars) s = String(s).replace(/\{(\w+)\}/g, (m, k) => (vars[k] != null ? vars[k] : m));
    return s;
  },

  /* Prefija una ruta interna con el mercado activo: '/kit/x/' -> '/de/kit/x/' */
  url(ruta) {
    const r = String(ruta == null ? '/' : ruta);
    if (/^(https?:|mailto:|tel:|#|data:)/.test(r)) return r;
    const base = this.mercado ? this.mercado.ruta : '/';
    if (r === '/') return base;
    if (r.startsWith('/#')) return base + r.slice(1);
    return base + r.replace(/^\//, '');
  },

  /* Ruta sin el prefijo del mercado: '/de/kit/x/' -> '/kit/x/' */
  sinMercado(pathname) {
    const p = pathname || location.pathname;
    const base = this.mercado && this.mercado.ruta !== '/' ? this.mercado.ruta : null;
    if (base && p.startsWith(base)) return '/' + p.slice(base.length);
    return p;
  },

  /* --- Amazon: dominio y tag del mercado activo --- */
  get amazon() {
    return (this.mercado && this.mercado.amazon) || { dominio: 'www.amazon.es', tag: 'ntizar-21', moneda: 'EUR', simbolo: '€' };
  },

  tag() {
    return this.amazon.tag || 'ntizar-21';
  },

  amazonBusqueda(q) {
    return `https://${this.amazon.dominio}/s?k=${encodeURIComponent(q)}&tag=${this.tag()}`;
  },

  /* Enlace de compra de un producto.
     ES: se usa la ficha /dp/ verificada del catálogo (es la que está comprobada).
     Otros mercados: búsqueda por el nombre traducido del producto. Un ASIN de
     amazon.es no siempre existe en amazon.de, y un enlace muerto vende cero.
     Cuando la API de Amazon esté conectada, `asin_local` manda. */
  enlaceProducto(item, kit) {
    if (!item) return null;
    if (this.mercado && this.mercado.id === 'es') return item.afiliado || null;
    if (item.asin_local) {
      return `https://${this.amazon.dominio}/dp/${item.asin_local}?tag=${this.tag()}`;
    }
    const q = item.producto || (kit && kit.titulo) || '';
    return q ? this.amazonBusqueda(q) : null;
  },

  cesta(asins) {
    const params = asins.map((a, i) => `ASIN.${i + 1}=${a}&Quantity.${i + 1}=1`).join('&');
    return `https://${this.amazon.dominio}/gp/aws/cart/add.html?${params}&tag=${this.tag()}`;
  },

  /* --- Precios: los textos de las fichas están en euros --- */
  _num(s) {
    return parseFloat(String(s).replace(/\.(?=\d{3}\b)/g, '').replace(',', '.'));
  },

  precio(txt) {
    if (txt == null) return '';
    if (this.amazon.moneda === 'EUR') return String(txt);
    const tipo = this.amazon.moneda === 'GBP'
      ? (this.tiposCambio.EUR_GBP || 0.85)
      : (this.tiposCambio.EUR_USD || 1.08);
    const sim = this.amazon.simbolo || '';
    const n = x => sim + Math.round(this._num(x) * tipo);
    let s = String(txt);
    // Primero los rangos ("20-40 €", "2.000 a 5.000 €" no: esos llevan letra y no
    // se tocan), y después las cifras sueltas con €.
    s = s.replace(/(\d{1,3}(?:\.\d{3})+|\d+)\s*[-–]\s*(\d{1,3}(?:\.\d{3})+|\d+)\s*€/g,
      (m, a, b) => `${n(a)}-${n(b)}`);
    s = s.replace(/(\d{1,3}(?:\.\d{3})+|\d+)\s*€/g, (m, a) => n(a));
    return s;
  },

  /* --- Cabecera y pie: traduce lo que vive fuera de #app --- */
  aplicarDOM() {
    // Variables para los textos con marcadores: {pais}, {num}.
    const vars = {
      pais: (this.mercado && this.mercado.paisLocal) || 'España',
      num: (this.mercado && this.mercado.emergencias && this.mercado.emergencias.numero) || '112'
    };
    document.querySelectorAll('[data-i18n]').forEach(el => {
      el.textContent = this.t(claveDe(el), vars);
    });
    document.querySelectorAll('[data-i18n-html]').forEach(el => {
      el.innerHTML = this.t(claveDe(el), vars);
    });
    document.querySelectorAll('[data-ruta]').forEach(el => {
      el.setAttribute('href', this.url(el.getAttribute('data-ruta')));
    });
    document.querySelectorAll('[data-i18n-titulo]').forEach(el => {
      el.setAttribute('title', this.t(claveDe(el, 'data-i18n-titulo')));
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      el.setAttribute('placeholder', this.t(claveDe(el, 'data-i18n-placeholder')));
    });
    // Botones de compra de la cabecera: dominio y tag del mercado, no amazon.es fijo.
    document.querySelectorAll('[data-amazon]').forEach(el => {
      el.setAttribute('href', this.amazonBusqueda(this.t('bloque.busqueda.q')));
    });
    document.documentElement.lang = (this.mercado && this.mercado.lang) || 'es';
    document.documentElement.setAttribute('data-mercado', (this.mercado && this.mercado.id) || 'es');
    this.pintarSelector();
    const d = document.getElementById('disclosure');
    if (d) d.textContent = this.t('disclosure');
  },

  /* Selector de país de la cabecera. Se pinta aquí para que el prerender lo
     capture traducido y con la opción activa marcada. */
  pintarSelector() {
    const caja = document.getElementById('pais-selector');
    if (!caja) return;
    const actual = this.mercado ? this.mercado.id : 'es';
    caja.innerHTML = `
      <label class="pais-et" for="pais-select">${this.t('pais.etiqueta')}</label>
      <select id="pais-select" aria-label="${this.t('pais.etiqueta')}"
              onchange="i18n.cambiarPais(this.value)">
        ${this.mercados.map(m => `<option value="${m.id}"${m.id === actual ? ' selected' : ''}>${m.bandera} ${m.paisLocal}</option>`).join('')}
      </select>`;
  },

  /* Cambiar de país conserva la ruta: /de/kit/kit-dana/ -> /fr/kit/kit-dana/ */
  cambiarPais(id) {
    const destino = this.mercadoPorId(id);
    if (!destino) return;
    try {
      localStorage.setItem('kit72h-pais', id);
      document.cookie = `kit72h-pais=${id}; path=/; max-age=31536000; samesite=lax`;
    } catch (e) { /* modo privado: la elección dura la sesión */ }
    const resto = this.sinMercado(location.pathname);
    const limpio = resto === '/' ? '' : resto.replace(/^\//, '');
    location.href = destino.ruta + limpio + location.hash;
  },

  /* --- Redirección por país: solo en la raíz y solo la primera vez --- */
  async autoPais() {
    if (!this.mercado || this.mercado.id !== 'es') return false;
    if (location.pathname !== '/' || location.hash) return false;
    const q = new URLSearchParams(location.search);
    if (q.get('pais')) return false;
    let guardado = null;
    try { guardado = localStorage.getItem('kit72h-pais'); } catch (e) {}
    if (guardado) {
      if (guardado !== 'es' && this.mercadoPorId(guardado)) {
        location.replace(this.mercadoPorId(guardado).ruta);
        return true;
      }
      return false;
    }
    // Los buscadores no se redirigen: se indexa la raíz en castellano.
    if (/bot|crawl|spider|slurp|bingpreview|google-inspection|headless|lighthouse|prerender/i.test(navigator.userAgent)) return false;

    let iso = '';
    try {
      const r = await fetch('/cdn-cgi/trace', { cache: 'no-store' });
      if (r.ok) {
        const txt = await r.text();
        const m = /^loc=([A-Z]{2})$/m.exec(txt);
        if (m) iso = m[1];
      }
    } catch (e) { /* sin Cloudflare: se usa el idioma del navegador */ }
    if (!iso) {
      const nav = (navigator.language || '').toUpperCase();
      iso = nav.slice(0, 2) === 'ES' ? 'ES' : nav.slice(3, 5) || nav.slice(0, 2);
    }
    const paisAIso = { GB: 'en-gb', UK: 'en-gb', DE: 'de', FR: 'fr', IT: 'it', NL: 'nl', US: 'en-us' };
    const destinoId = paisAIso[iso];
    if (destinoId) {
      const d = this.mercadoPorId(destinoId);
      if (d) { location.replace(d.ruta); return true; }
    }
    return false;
  },

  /* Nota legal de afiliado por mercado (el texto de EE. UU. no es el español) */
  disclosure() { return this.t('disclosure'); }
};

function claveDe(el, attr) {
  return el.getAttribute(attr || 'data-i18n') || '';
}
