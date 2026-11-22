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
      await this.detectarPais();
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

  /* --- Amazon: dominio y tag del mercado activo ---
     `amazon` NO es siempre el de la página: si el visitante está en un país que
     ese idioma cubre y ese mercado tiene tag propio, los enlaces van a SU tienda
     (un inglés en /en-us/ acaba en amazon.co.uk; un estadounidense en /en-gb/
     acaba en amazon.com). Así cada país compra en su moneda y con su tag. */
  get amazon() {
    return this.amazonEfectivo();
  },

  /* País del visitante (ISO-2), una sola vez por sesión.
     Orden: ?pais=XX (pruebas) -> sessionStorage -> /cdn-cgi/trace de Cloudflare
     -> región de navigator.language. En headless/bots NO se detecta: el HTML
     horneado debe llevar los enlaces del mercado de la URL, no los de mi IP. */
  async detectarPais() {
    const forzado = new URLSearchParams(location.search).get('pais');
    if (forzado && /^[A-Za-z]{2}$/.test(forzado)) { this.paisISO = forzado.toUpperCase(); return; }
    try {
      const guardado = sessionStorage.getItem('kit72h-iso');
      if (guardado) { this.paisISO = guardado; return; }
    } catch (e) { /* modo privado */ }
    const ua = navigator.userAgent || '';
    if (navigator.webdriver || /bot|crawl|spider|headless|lighthouse|prerender/i.test(ua)) return;
    let iso = '';
    try {
      const r = await fetch('/cdn-cgi/trace', { cache: 'no-store' });
      if (r.ok) {
        const m = /^loc=([A-Z]{2})$/m.exec(await r.text());
        if (m) iso = m[1];
      }
    } catch (e) { /* sin Cloudflare delante: se tira del navegador */ }
    if (!iso) {
      const reg = (navigator.language || '').split('-')[1];
      if (reg && reg.length === 2) iso = reg.toUpperCase();
    }
    if (iso) {
      this.paisISO = iso;
      try { sessionStorage.setItem('kit72h-iso', iso); } catch (e) {}
    }
  },

  /* Mercado del visitante dentro del MISMO idioma. null si no hay uno claro. */
  mercadoSugerido() {
    if (!this.paisISO || !this.mercado) return null;
    return this.mercados.find(m => m.lang === this.mercado.lang &&
                                   (m.paises || []).includes(this.paisISO)) || null;
  },

  /* Amazon que se usa en los enlaces.
     Solo se cambia de tienda si el mercado del visitante tiene tag propio: si no,
     se queda el de la página. Cambiar a una tienda sin tag nos dejaría sin
     comisión y sin nada a cambio. */
  amazonEfectivo() {
    const propio = (this.mercado && this.mercado.amazon)
      || { dominio: 'www.amazon.es', tag: 'ntizar-21', moneda: 'EUR', simbolo: '€' };
    const sugerido = this.mercadoSugerido();
    if (sugerido && sugerido.id !== (this.mercado && this.mercado.id)
        && sugerido.amazon && sugerido.amazon.tag) {
      return sugerido.amazon;
    }
    return propio;
  },

  /* Sección de la página: decide qué tracking ID se usa.
     /kit/x/ → kits · /blog/… → blog · resto (portada, fuentes, zona) → home */
  seccion(ruta) {
    const p = String(ruta || location.pathname);
    const s = (typeof this.sinMercado === 'function') ? this.sinMercado(p) : p;
    if (/^\/kit\//.test(s)) return 'kits';
    if (/^\/blog(\/|$)/.test(s)) return 'blog';
    return 'home';
  },

  /* Tracking ID del mercado para una sección.
     REGLA DURA: el tag de un marketplace NUNCA se aplica a la tienda de otro
     (Amazon lo ignora en silencio y la venta se pierde). Si el mercado no tiene
     tag propio se devuelve '' y el enlace se construye SIN tag; los mercados
     pendientes los lista data/tags-afiliado.json y los audita
     scripts/auditar-tags.py. */
  tag(seccion) {
    const a = this.amazon || {};
    const tags = a.tags || {};
    return tags[seccion || this.seccion()] || a.tag || '';
  },

  /* Añade `tag=` a una URL de Amazon solo si hay tag y la URL es de SU tienda. */
  conTag(url) {
    const t = this.tag();
    if (!t || !url) return url;
    const dom = (this.amazon && this.amazon.dominio) || '';
    if (dom && url.indexOf(dom) === -1) return url;   // otra tienda: sin tag, nunca cruzado
    return url + (url.indexOf('?') === -1 ? '?' : '&') + 'tag=' + t;
  },

  /* Reescribe el tag de los enlaces de Amazon que vienen ya escritos en el HTML
     (los cuerpos del blog traen ?tag=ntizar-21 de fábrica). Solo cambia el valor
     del parámetro y SOLO en enlaces de la tienda del mercado activo: dominio,
     ASIN y ruta no se tocan nunca. */
  retag(html) {
    const t = this.tag();
    const s = String(html == null ? '' : html);
    if (!s || s.indexOf('amazon.') === -1) return s;
    const dom = ((this.amazon && this.amazon.dominio) || '').replace(/^www\./, '');
    return s.replace(/(https?:\/\/[^"'\s]*?amazon\.[a-z.]+[^"'\s]*?[?&](?:amp;)?)tag=[\w-]+/g,
      (m, base) => {
        if (!dom || base.indexOf(dom) === -1) return m;   // otra tienda: se queda su tag
        return t ? `${base}tag=${t}` : m;
      });
  },

  amazonBusqueda(q) {
    return this.conTag(`https://${this.amazon.dominio}/s?k=${encodeURIComponent(q)}`);
  },

  /* Enlace de compra de un producto.
     ES: se usa la ficha /dp/ verificada del catálogo (es la que está comprobada).
     Otros mercados: búsqueda por el nombre traducido del producto. Un ASIN de
     amazon.es no siempre existe en amazon.de, y un enlace muerto vende cero.
     La ficha /dp/ solo se usa si la tienda efectiva sigue siendo la española. */
  enlaceProducto(item, kit) {
    if (!item) return null;
    const esTiendaES = this.amazon.dominio === 'www.amazon.es';
    if (esTiendaES && this.mercado && this.mercado.id === 'es' && item.afiliado) {
      // El catálogo trae el tag de fábrica (ntizar-21): se reescribe al de la
      // sección que se está viendo (fichas → kit72h-21). Sin esto el HTML
      // horneado dice una cosa y el navegador sirve otra: el panel de Amazon
      // solo veía ventas en ntizar-21 y los demás tags parecían muertos.
      return this.retag(item.afiliado);
    }
    if (item.asin_local) {
      return this.conTag(`https://${this.amazon.dominio}/dp/${item.asin_local}`);
    }
    const q = item.producto || (kit && kit.titulo) || '';
    return q ? this.amazonBusqueda(q) : null;
  },

  cesta(asins) {
    const params = asins.map((a, i) => `ASIN.${i + 1}=${a}&Quantity.${i + 1}=1`).join('&');
    return this.conTag(`https://${this.amazon.dominio}/gp/aws/cart/add.html?${params}`);
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
    // A qué mercado corresponde el país: sale de data/mercados.json ('paises'),
    // no de una lista escrita a mano aquí. Añadir un país es editar el JSON.
    const destino = this.mercados.find(m => m.id !== 'es' && (m.paises || []).includes(iso));
    if (destino) { location.replace(destino.ruta); return true; }
    return false;
  },

  /* Nota legal de afiliado por mercado (el texto de EE. UU. no es el español) */
  disclosure() { return this.t('disclosure'); }
};

function claveDe(el, attr) {
  return el.getAttribute(attr || 'data-i18n') || '';
}
