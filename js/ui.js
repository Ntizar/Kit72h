/* Kit72h — ui: render de vistas tácticas.
   Datos: data/kits.json + data/blog.json (castellano, fuente de verdad) y, para
   otros idiomas, el overlay data/i18n/contenido/<lang>.json que se fusiona encima.
   Textos de interfaz: i18n.t(). País, Amazon, moneda y emergencias: i18n.mercado.
   NADA de país ni de texto de interfaz hardcodeado aquí. */

/* Precios reales de Amazon (data/precios.json, lo escribe scripts/precios-amazon.py).
   Si el fichero no está o el ASIN no trae precio, la web cae al rango de siempre:
   nunca se pinta una cifra inventada. Los precios son de amazon.es: solo se usan
   en el mercado español; fuera se muestra el rango orientativo convertido. */
const precios = {
  data: null,
  async cargar() {
    if (this.data) return this.data;
    try {
      const r = await fetch('/data/precios.json');
      this.data = r.ok ? await r.json() : null;
    } catch (e) { this.data = null; }
    return this.data;
  },
  porAsin(asin) {
    const p = asin && this.data ? (this.data.productos || {})[asin] : null;
    return (p && p.precio) ? p : null;
  },
  /* 1 = Amazon dice agotado · 0 = sin listado/precio · null = no lo sabemos */
  sinPrecio(asin) {
    if (!asin || !this.data) return null;
    const s = this.data.sin_precio || {};
    return Object.prototype.hasOwnProperty.call(s, asin) ? s[asin] : null;
  },
  /* Coste real del kit con los precios de hoy: total y sólo imprescindibles.
     Sólo cuenta lo que Amazon devuelve con precio; nunca estima lo que falta. */
  costeKit(kit) {
    let suma = 0, n = 0, total = 0, esSuma = 0, nEs = 0;
    (kit.secciones || []).forEach(s => (s.items || []).forEach(i => {
      total++;
      const m = i.afiliado ? /\/dp\/([A-Z0-9]{10})/.exec(i.afiliado) : null;
      const p = m ? this.porAsin(m[1]) : null;
      if (p) {
        n++; suma += p.precio;
        if (i.prioridad === 'esencial') { nEs++; esSuma += p.precio; }
      }
    }));
    return { suma: Math.round(suma * 100) / 100, n, total, esSuma: Math.round(esSuma * 100) / 100, nEs };
  },
  eur(n) {
    const loc = (typeof i18n !== 'undefined' && i18n.mercado) ? i18n.mercado.locale : 'es-ES';
    return Number(n).toLocaleString(loc, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';
  },
  /* «315,49 € 369,99 € · -15%» — el antes tachado y el % sólo si Amazon los publica */
  sello(p) {
    if (!p) return '';
    const antes = (p.precio_antes && p.precio_antes > p.precio)
      ? ` <s>${this.eur(p.precio_antes)}</s>` : '';
    const rebaja = (p.ahorro_pct >= 10) ? ` · -${Math.round(p.ahorro_pct)}%` : '';
    return `<span class="precio">${p.precio_texto || this.eur(p.precio)}${antes}${rebaja}</span>`;
  },
  fecha() {
    const iso = this.data && this.data.meta && this.data.meta.actualizado;
    if (!iso) return '';
    const d = new Date(iso);
    const loc = (typeof i18n !== 'undefined' && i18n.mercado) ? i18n.mercado.locale : 'es-ES';
    return isNaN(d) ? '' : d.toLocaleDateString(loc, { day: '2-digit', month: '2-digit' });
  }
};

const ui = {
  get tag() { return i18n.tag(); },

  T(clave, vars) { return i18n.t(clave, vars); },
  url(ruta) { return i18n.url(ruta); },

  /* Prefija los href internos de un bloque de HTML venido de datos (FAQ, blog,
     guías). En castellano es un no-op; en /de/ convierte /kit/x/ en /de/kit/x/. */
  hrefs(html) {
    const base = (i18n.mercado && i18n.mercado.ruta !== '/') ? i18n.mercado.ruta : '/';
    if (base === '/') return String(html);
    return String(html).replace(/href="\//g, `href="${base}`);
  },

  esEspana() { return !i18n.mercado || i18n.mercado.id === 'es'; },
  numEmergencias() { return (i18n.mercado && i18n.mercado.emergencias && i18n.mercado.emergencias.numero) || '112'; },

  marquee(txt) {
    const span = `<span>${txt}</span>`;
    return (span + ' ·').repeat(1) + span + span + span + span + span + span;
  },

  irA(vista, slug = null) {
    location.hash = slug ? `#kit/${slug}` : vista === 'home' ? '' : `#${vista}`;
    this.render();
  },

  /* La ruta se lee SIN el prefijo del mercado: /de/kit/x/ -> vista kit x. */
  vistaDesdeHash() {
    const p = i18n.sinMercado(location.pathname).replace(/\/+$/, '') || '/';
    if (p === '/fuentes') return { vista: 'fuentes' };
    if (p === '/zona') return { vista: 'zona' };
    if (p === '/noticias') return { vista: 'noticias' };
    if (p.startsWith('/kit/')) return { vista: 'kit', slug: p.split('/')[2] };
    // OJO: '/blog/' recorta la barra final -> '/blog' y startsWith('/blog/') nunca casa.
    // Sin esta línea, /blog/ (el índice) cae a 'home' y el índice prerenderizado ES la home.
    if (p === '/blog' || p.startsWith('/blog/')) { const s = p.split('/')[2]; return s ? { vista: 'blog', slug: s } : { vista: 'blog' }; }
    const h = location.hash.replace('#', '');
    if (h.startsWith('kit/')) return { vista: 'kit', slug: h.split('/')[1] };
    if (h.startsWith('blog/')) return { vista: 'blog', slug: h.split('/')[1] };
    if (h === 'blog') return { vista: 'blog' };
    if (h === 'fuentes') return { vista: 'fuentes' };
    if (h === 'noticias') return { vista: 'noticias' };
    return { vista: 'home' };
  },

  async render() {
    const { vista, slug } = this.vistaDesdeHash();
    const app = document.getElementById('app');
    i18n.aplicarDOM();
    await Promise.all([estado.cargar(), blog.cargar(), precios.cargar(),
                       typeof noticias !== 'undefined' ? noticias.cargar() : null]);

    if (vista === 'kit') {
      const kit = state.kitPorSlug(slug);
      if (!kit) { location.hash = ''; return this.render(); }
      app.innerHTML = this.htmlKit(kit);
      document.title = `${kit.titulo} — Kit72h`;
    } else if (vista === 'fuentes') {
      app.innerHTML = this.htmlFuentes();
      document.title = this.T('meta.fuentes');
    } else if (vista === 'zona' && this.esEspana()) {
      app.innerHTML = this.htmlZona();
      document.title = 'Tu zona: hospital, farmacia, refugio y 112 — Kit72h';
      // 'const zona' NO cuelga de window: no comprobar window.zona, nunca arrancaría.
      try { if (typeof zona !== 'undefined') zona.iniciar(); } catch (e) { /* sin mapa: el texto sigue ahí */ }
      // Los avisos de AEMET no dependen del mapa: se pintan aunque Leaflet falle.
      try { if (typeof zona !== 'undefined') zona.cargarAlertas(); } catch (e) { /* la lista queda vacía */ }
    } else if (vista === 'noticias' && this.esEspana()) {
      app.innerHTML = this.htmlNoticias();
      document.title = 'Lo que está pasando: provisiones, incendios, inundaciones y apagones — Kit72h';
    } else if (vista === 'blog') {
      const entrada = slug ? blog.porSlug(slug) : null;
      if (slug && !entrada) { location.hash = 'blog'; return this.render(); }
      app.innerHTML = entrada ? this.htmlEntrada(entrada) : this.htmlBlog();
      document.title = entrada ? `${entrada.titulo} — Kit72h` : this.T('meta.blog');
    } else {
      app.innerHTML = this.htmlHome();
      document.title = this.T('meta.home');
    }
    const ancla = location.hash;
    const objetivo = ancla && !ancla.startsWith('#kit/') && !ancla.startsWith('#blog/')
      && ancla !== '#fuentes' ? document.querySelector(ancla) : null;
    if (objetivo) objetivo.scrollIntoView({ block: 'start' }); else window.scrollTo(0, 0);
  },

  /* ---- HOME: espejo de la referencia (diario de supervivencia) ---- */
  /* Bandera suiza en SVG (Windows NO renderiza el emoji 🇨🇭: pinta "CH").
     Cuadrada y con los brazos 6:7, como la bandera oficial. */
  banderaCH(clase) {
    return `<svg class="bandera-ch${clase ? ' ' + clase : ''}" viewBox="0 0 32 32" role="img" aria-label="Bandera de Suiza"><rect width="32" height="32" fill="#DA291C"/><rect x="13" y="6" width="6" height="20" fill="#fff"/><rect x="6" y="13" width="20" height="6" fill="#fff"/></svg>`;
  },

  htmlHome() {
    const T = (k, v) => this.T(k, v);
    const compra = i18n.amazonBusqueda(T('bloque.busqueda.q'));
    const bloques = [
      { k: 'agua', n: '01', ic: '<path d="M12 3 C12 3 5 10.5 5 15 a7 7 0 0 0 14 0 C19 10.5 12 3 12 3 Z"/><path d="M9 15.5 a3 3 0 0 0 3 3"/>' },
      { k: 'luz', n: '02', ic: '<path d="M12 3 a6 6 0 0 1 3.5 10.9 c-.6.5-1 1.3-1 2.1 H9.5 c0-.8-.4-1.6-1-2.1 A6 6 0 0 1 12 3 Z"/><path d="M9.5 19 h5 M10.5 21.5 h3"/>' },
      { k: 'energia', n: '03', ic: '<path d="M13 2 L5 14 h6 l-2 8 8-12 h-6 z"/>' },
      { k: 'salud', n: '04', ic: '<rect x="3.5" y="3.5" width="17" height="17"/><path d="M12 8 v8 M8 12 h8"/>' },
      { k: 'comida', n: '05', ic: '<path d="M7 7 h10 v13 a1.5 1.5 0 0 1 -1.5 1.5 h-7 A1.5 1.5 0 0 1 7 20 Z"/><ellipse cx="12" cy="7" rx="5" ry="2"/><path d="M7 11 h10"/>' },
      { k: 'docs', n: '06', ic: '<path d="M7 3 h7 l4 4 v14 H7 Z"/><path d="M14 3 v4 h4"/><path d="M10 12 h6 M10 16 h6"/>' }
    ].map(b => `
      <article class="bloque-lista b-${b.k}">
        <div class="bloque-top">
          <span class="bloque-flag">${b.n} / ${T('bloque.' + b.k + '.cat')}</span>
          <svg class="bloque-icono" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${b.ic}</svg>
        </div>
        <h3>${T('bloque.' + b.k + '.t')}</h3>
        <p>${T('bloque.' + b.k + '.d')}</p>
        <div class="bloque-pie">
          <span class="presup">${T('lista.presupuesto', { p: i18n.precio(T('bloque.' + b.k + '.p')) })}</span>
          <a class="btn-amazon" href="${i18n.amazonBusqueda(T('bloque.' + b.k + '.q'))}" target="_blank" rel="sponsored nofollow noopener">${T('bloque.' + b.k + '.b')} ↗</a>
        </div>
      </article>`).join('');

    /* Tarjetas de kit: los normales en rejilla; Starlink como tarjeta
       destacada; y el PRO al final, ocupando las 3 columnas con holo. */
    const tarjetaKit = (k, i) => {
      const c = precios.costeKit(k);
      return `
      <a class="card-kit" href="${this.url('/kit/' + k.slug + '/')}">
        <div class="fila-top"><span class="icono${k.bandera ? ' icono--bandera' : ''}">${k.bandera === 'ch' ? this.banderaCH() : k.icono}</span><span class="num">${String(i+1).padStart(2,'0')}</span></div>
        <h2>${k.titulo}</h2>
        <p>${k.resumen}</p>
        <div class="pie">
          <span class="coste-kit">${k.coste_total ? i18n.precio(k.coste_total) : T('kit.gratis')}</span>
          ${this.esEspana() && c.n >= 3 ? `<span class="coste-hoy">${T('precio.hoy', { p: precios.eur(c.suma) })}</span>` : ''}
          <span class="ir">${T('kit.abrir')}</span>
        </div>
      </a>`;
    };

    const tarjetaStarlink = `
      <a class="card-kit card-starlink" href="${this.url('/kit/kit-starlink/')}">
        <div class="fila-top"><span class="icono">📡</span><span class="num">⭐</span></div>
        <h2>${T('starlink.t')}</h2>
        <p>${T('starlink.d')}</p>
        <div class="pie">
          <span class="coste-kit" style="color:var(--rojo)">${i18n.precio(T('starlink.coste'))}</span>
          <span class="ir" style="color:var(--rojo)">${T('kit.verFicha')}</span>
        </div>
      </a>`;

    const tarjetaPro = (k) => `
      <a class="card-kit card-pro-pokemon" href="${this.url('/kit/' + k.slug + '/')}">
        <div class="holo-glare"></div>
        <div class="holo-shine"></div>
        <div class="pro-left">
          <div class="pro-badge-wrap"><span class="pro-badge">PRO</span></div>
          <h2>${k.titulo}</h2>
          <p>${k.resumen}</p>
          <span class="pro-coste">${k.coste_total ? i18n.precio(k.coste_total) : ''}</span>
        </div>
        <div class="pro-right"><span class="pro-cta">${T('kit.proCta')}</span></div>
      </a>`;

    const normales = state.data.kits.filter(k => !k.premium && k.slug !== 'kit-starlink');
    const premium = state.data.kits.filter(k => k.premium);
    const tarjetas = normales.map(tarjetaKit).join('')
      + tarjetaStarlink
      + premium.map(tarjetaPro).join('');

    const blogFeatured = (this.esEspana() ? blog.entradas : blog.entradas.filter(e => e._traducido))
      .slice(0, 3).map((e, i) => `
      <a class="card-kit card-blog" href="${this.url('/blog/' + e.slug + '/')}">
        <div class="fila-top"><span class="num">${String(i+1).padStart(2,'0')}</span></div>
        <h2>${e.titulo}</h2>
        <p>${e.resumen}</p>
        <span class="meta-blog">⏱ ${T('blog.lectura', { n: this.lectura(e) })}</span>
      </a>`).join('');

    const arte = `<div class="hero-arte" aria-hidden="true"><svg viewBox="0 0 1440 420" preserveAspectRatio="xMidYMax slice" xmlns="http://www.w3.org/2000/svg">
      <circle cx="1200" cy="110" r="44" fill="#8F7B45"/>
      <path d="M0,300 L180,175 L340,268 L520,145 L700,258 L880,185 L1060,278 L1240,195 L1440,288 L1440,300 L0,300 Z" fill="#D14B27"/>
      <path d="M0,300 L220,225 L430,300 L640,215 L860,300 L1080,235 L1300,300 L1440,258 L1440,300 L0,300 Z" fill="#9E3417"/>
      <rect y="300" width="1440" height="120" fill="#EFA02B"/>
      <rect y="300" width="1440" height="6" fill="#0E0C09" opacity="0.25"/>
    </svg></div>`;

    const faq = [1, 2, 3, 4, 5, 6, 7].map(n => `
        <details class="faq-item"><summary>${T('faq.q' + n)}</summary><p>${this.hrefs(T('faq.a' + n, { num: this.numEmergencias() }))}</p></details>`).join('');

    return `
      <div class="hero">
        ${arte}
        <div class="container">
          <span class="chip">${T('hero.chip', { pais: (i18n.mercado && i18n.mercado.paisLocal) || 'España' })}</span>
          <h1><span class="l1">${T('hero.l1')}</span> <span class="l2">${T('hero.l2')}</span></h1>
          <p class="hero-lead">${T('hero.lead')}</p>
          <div class="hero-ctas">
            <a class="btn ambar" href="#kits">${T('hero.verKits')}</a>
            <a class="btn negro" href="${compra}" target="_blank" rel="sponsored nofollow noopener">${T('hero.comprar')}</a>
          </div>
          <div class="hero-oferta">
          <a class="cta-kit" href="${compra}" target="_blank" rel="sponsored nofollow noopener">
            <span class="cta-kit-t">${T('hero.ctaT')}</span>
            <span class="cta-kit-b">${T('hero.ctaB')}</span>
          </a>
          <!-- Kit profesional: cuadro «carta PRO» plateada (mismo acabado que la de la grid) -->
          <a class="kpro-hero-btn" href="${this.url('/kit/kit-kit-profesional/')}">
            <div class="holo-glare"></div>
            <div class="holo-shine"></div>
            <span class="kpro-hero-chip">${T('hero.proChip')}</span>
            <span class="kpro-hero-title">${T('hero.proT1')}<br>${T('hero.proT2')}</span>
            <span class="kpro-hero-sub">${T('hero.proSub')}</span>
            <span class="kpro-hero-cta">${T('hero.proCta')}</span>
          </a>
          </div>
        </div>
      </div>
      <div class="ticker" aria-hidden="true"><div class="ticker-track">${this.marquee(T('ticker'))}</div></div>
      ${this.htmlOfertaDia()}
      <section class="sec clara" id="plan">
        <div class="container">
          <div class="watermark" aria-hidden="true">72</div>
          <div class="sec-inner">
            <span class="sec-label">${T('plan.label')}</span>
            <div class="plan-head">
              <h2>${T('plan.h2a')}<br><span class="acento">${T('plan.h2b')}</span></h2>
              <p>${T('plan.intro')}</p>
            </div>
            <div class="plan-grid">
              <div class="card-plan"><span class="hora">${T('plan.c1h')}</span><h3>${T('plan.c1t')}</h3><p>${T('plan.c1p')}</p></div>
              <div class="card-plan"><span class="hora">${T('plan.c2h')}</span><h3>${T('plan.c2t')}</h3><p>${T('plan.c2p')}</p></div>
              <div class="card-plan"><span class="hora">${T('plan.c3h')}</span><h3>${T('plan.c3t')}</h3><p>${T('plan.c3p')}</p></div>
            </div>
            <p class="disclaimer">${T('plan.disclaimer')}</p>
          </div>
        </div>
      </section>
      <section class="sec clara">
        <div class="container">
          <div class="watermark" aria-hidden="true">LISTA</div>
          <div class="sec-inner">
            <span class="sec-label">${T('lista.label')}</span>
            <h2>${T('lista.h2a')}<span class="acento">${T('lista.h2b')}</span></h2>
            <p class="sec-intro" style="color:#4a4238">${T('lista.intro', { amazon: 'Amazon.' + i18n.amazon.dominio.split('.').pop() })}</p>
            <div class="lista-bloques">${bloques}</div>
            <div class="ruta-corta">
              <div>
                <span class="bloque-num" style="border:none;padding:0">${T('ruta.label')}</span>
                <h3>${T('ruta.h2')}</h3>
              </div>
              <div>
                <ul>
                  <li>${T('ruta.li1')}</li>
                  <li>${T('ruta.li2')}</li>
                  <li>${T('ruta.li3')}</li>
                </ul>
                <a class="btn ambar" href="${i18n.amazonBusqueda(T('bloque.busqueda.q'))}" target="_blank" rel="sponsored nofollow noopener">${T('ruta.btn')}</a>
              </div>
            </div>
            <p class="lista-nota">${T('lista.nota')}</p>
            ${this.esEspana() ? '' : `<p class="lista-nota">${T('precio.nota')}</p>`}
          </div>
        </div>
      </section>
      <section class="sec oscura" id="kits">
        <div class="container">
          <div class="watermark" aria-hidden="true">KITS</div>
          <div class="sec-inner">
            <span class="sec-label">${T('kits.label')}</span>
            <h2>${T('kits.h2a')}<br><span class="acento2">${T('kits.h2b')}</span></h2>
            <p class="sec-intro">${T('kits.intro')}</p>
            <div class="grid-kits">${tarjetas}</div>
          </div>
        </div>
      </section>
      <section class="sec clara" id="faq">
  <div class="container">
    <div class="sec-inner">
      <span class="label">${T('faq.label')}</span>
      <h2>${T('faq.h2')}</h2>
      <div class="faq-lista">${faq}
      </div>
      <div class="faq-compra">
        <div class="faq-compra-txt">${T('faq.ctaT')}</div>
        <a class="btn negro" href="${this.url('/kit/kit-basico-72h/')}">${T('faq.ctaBtn')}</a>
      </div>
    </div>
  </div>
</section>
      ${blogFeatured ? `
      
      <section class="sec clara" id="lecturas">
        <div class="container">
          <div class="watermark" aria-hidden="true">BLOG</div>
          <div class="sec-inner">
            <span class="sec-label">${T('lecturas.label')}</span>
            <h2>${T('lecturas.h2a')}<br><span class="acento">${T('lecturas.h2b')}</span></h2>
            <div class="grid-kits">${blogFeatured}</div>
            <p><a class="btn negro" href="${this.url('/blog/')}">${T('blog.todas')}</a></p>
          </div>
        </div>
      </section>` : ''}
      <section class="cta-final">
        <div class="container">
          <span class="sec-label">${T('cta.label')}</span>
          <h2>${T('cta.h2a')}<br>${T('cta.h2b')}<span class="acento">${T('cta.h2c')}</span></h2>
          <p>${T('cta.p')}</p>
          <div class="hero-ctas">
            <a class="btn ambar" href="#kits">${T('cta.btn1')}</a>
            <a class="btn negro" href="${i18n.amazonBusqueda(T('bloque.busqueda.q'))}" target="_blank" rel="sponsored nofollow noopener">${T('cta.btn2')}</a>
          </div>
        </div>
      </section>`;
  },

  /* ---- BLOG ---- */
  /* Minutos de lectura calculados del cuerpo real. La promesa del titular
     tiene que cuadrar con lo que hay: había posts de 245 palabras
     anunciando «7 min de lectura». */
  lectura(e) {
    const txt = String(e.cuerpo || '').replace(/<[^>]+>/g, ' ');
    const n = (txt.trim().match(/\S+/g) || []).length;
    return `${Math.max(1, Math.round(n / 200))} min`;
  },

  htmlBlog() {
    const T = (k, v) => this.T(k, v);
    const aviso = this.esEspana() ? '' : `<p class="aviso-idioma">${T('blog.aviso')}</p>`;
    // Fuera de España solo se listan las guías YA traducidas: enseñar decenas de
    // títulos en castellano bajo /de/ sería contenido duplicado y mala experiencia.
    const lista = this.esEspana() ? blog.entradas : blog.entradas.filter(e => e._traducido);
    const vacio = (!this.esEspana() && !lista.length)
      ? `<p class="aviso-idioma">${this.hrefs(T('blog.vacio'))}</p>` : '';
    const tarjetas = lista.map((e, i) => `
      <a class="card-kit card-blog" href="${this.url('/blog/' + e.slug + '/')}">
        <div class="fila-top"><span class="num">${String(i+1).padStart(2,'0')}</span></div>
        <h2>${e.titulo}</h2>
        <p>${e.resumen}</p>
        <span class="meta-blog">📅 ${e.fecha} · ⏱ ${T('blog.lectura', { n: this.lectura(e) })} ${(e.etiquetas||[]).map(t=>`<span class="tag-blog">${t}</span>`).join('')}</span>
      </a>`).join('');
    return `
      <section class="hero hero-blog">
        <div class="container">
          <span class="chip">${T('blog.chip')}</span>
          <h1><span class="l1">${T('blog.hero1')}</span><span class="l2">${T('blog.hero2')}</span></h1>
          <p class="hero-lead">${T('blog.heroLead', { n: lista.length })}</p>
        </div>
      </section>
      <section class="sec clara"><div class="container"><div class="sec-inner">
        <span class="sec-label">${T('blog.indice')}</span>
        ${aviso}
        ${vacio}
        <div class="grid-kits">${tarjetas}</div>
      </div></div></section>`;
  },

  htmlEntrada(e) {
    const T = (k, v) => this.T(k, v);
    const otras = blog.entradas.filter(x => x.slug !== e.slug && x._traducido !== false &&
      (x.etiquetas || []).some(t => (e.etiquetas || []).includes(t)))
      .slice(0, 5)
      .map(x => `<li><a href="${this.url('/blog/' + x.slug + '/')}">${x.titulo}</a></li>`).join('');
    const fuentes = (e.fuente || []).map(f =>
      `<li><a href="${f.url}" target="_blank" rel="noopener">${f.nombre}</a></li>`).join('');
    // Hasta que el cron traduzca el cuerpo, un aviso honesto en vez de castellano suelto.
    const aviso = (!this.esEspana() && !e._traducido) ? `<p class="aviso-idioma">${T('blog.aviso')}</p>` : '';
    return `
      <section class="ficha entrada-blog">
        <a class="volver" href="${this.url('/blog/')}">${T('blog.volver')}</a>
        ${aviso}
        <h1>${e.titulo}</h1>
        <p class="meta-blog">📅 ${e.fecha} · ⏱ ${T('blog.lectura', { n: this.lectura(e) })}</p>
        <div class="cuerpo-blog">${this.hrefs(this.tablasSeguras(e.cuerpo))}</div>
        ${fuentes ? `<div class="guia-kit"><h2>${T('blog.fuentes')}</h2><ul>${fuentes}</ul></div>` : ''}
        ${otras ? `<div class="guia-kit"><h2>${T('blog.sigue')}</h2><ul>${otras}</ul></div>` : ''}
      </section>`;
  },

  /* ---- SELECCIÓN DEL DÍA (data/precios.json: rebaja real + stock + precio) ----
     Solo España: los precios vienen de la API de Amazon.es en euros. */
  textoOferta(o) {
    const pct = Math.round(o.ahorro_pct);
    const ahorro = precios.eur(Math.max(0, (o.precio_antes || 0) - o.precio));
    const n = Object.keys((precios.data && precios.data.productos) || {}).length;
    const variantes = [
      this.T('oferta.v1', { pct, ahorro, kit: o.kit_titulo }),
      this.T('oferta.v2', { pct, ahorro, kit: o.kit_titulo, n }),
      this.T('oferta.v3', { pct, ahorro, kit: o.kit_titulo }),
    ];
    return variantes[new Date().getDate() % variantes.length];
  },

  htmlOfertaDia() {
    if (!this.esEspana()) return '';
    const o = precios.data && precios.data.oferta_dia;
    if (!o || !o.precio) return '';
    const antes = o.precio_antes && o.precio_antes > o.precio
      ? `${this.T('oferta.antes', { p: precios.eur(o.precio_antes) })} · ` : '';
    return `
      <section class="sec oscura" id="oferta-dia">
        <div class="container">
          <div class="sec-inner">
            <span class="sec-label">${this.T('oferta.label')}${precios.fecha() ? ' · ' + precios.fecha() : ''}</span>
            <a class="cta-kit" href="${o.url}" target="_blank" rel="sponsored nofollow noopener">
              <span class="cta-kit-t">${o.producto}<br>${this.T('oferta.hoy', { p: o.precio_texto })}</span>
              <span class="cta-kit-b">${antes}-${Math.round(o.ahorro_pct)}% · ${this.T('oferta.enKit', { kit: o.kit_titulo })}</span>
            </a>
            <p class="oferta-texto">${this.textoOferta(o)}</p>
            <p class="lista-nota">${this.T('oferta.nota')}</p>
          </div>
        </div>
      </section>`;
  },

  /* ---- FICHA DE KIT ---- */
  htmlKit(kit) {
    const T = (k, v) => this.T(k, v);
    const esES = this.esEspana();
    const coste = precios.costeKit(kit);
    const asinsEs = new Set();   // ASINs unicos imprescindibles (la cesta deduplica)
    let nProd = 0;               // productos totales
    let nEs = 0;                 // imprescindibles REALES (con ficha o sin ella)
    let nConFicha = 0;           // items con ficha /dp/ (se pueden añadir a la cesta)

    const secciones = kit.secciones.map((s, si) => `
      <div class="seccion-kit">
        <h2>${String(si+1).padStart(2,'0')} / ${s.titulo}</h2>
        ${s.intro ? `<p class="intro-seccion">${s.intro}</p>` : ''}
        <ul class="items">
          ${s.items.map(i => {
            nProd++;
            const m = i.afiliado ? /\/dp\/([A-Z0-9]{10})/.exec(i.afiliado) : null;
            if (esES && m) nConFicha++;
            const es = i.prioridad === 'esencial';
            if (es) nEs++;
            if (esES && es && m) asinsEs.add(m[1]);
            const real = (esES && m) ? precios.porAsin(m[1]) : null;
            const sinP = (esES && m) ? precios.sinPrecio(m[1]) : null;
            const alt = (!real && sinP !== null)
              ? i18n.amazonBusqueda(i.producto)
              : null;
            // En el mercado español, el enlace es la ficha verificada; fuera, búsqueda
            // del producto traducido en el Amazon del país (ver i18n.enlaceProducto).
            const enlace = i18n.enlaceProducto(i, kit);
            return `
            <li class="item${es ? ' esencial' : ''}" ${m && esES ? `data-asin="${m[1]}"` : ''}>
              <div class="item-info">
                <div class="item-media">${real && real.img
                  ? `<img class="item-foto" src="${real.img}" alt="" width="64" height="64" loading="lazy">`
                  : '<span class="item-foto item-foto--vacia" aria-hidden="true"></span>'}</div>
                <div class="item-texto">
                <span class="producto">${i.producto}</span>
                ${i.descripcion ? `<span class="descripcion">${i.descripcion}</span>` : ''}
                ${real ? precios.sello(real)
                       : (i.precio_aprox ? `<span class="precio">~ ${i18n.precio(i.precio_aprox)}</span>` : '')}
                ${alt ? `<span class="badge-agotado">${sinP === 1 ? T('item.sinStock') : T('item.sinPrecio')}</span>` : ''}
                ${i.es_busqueda ? `<span class="badge-busqueda">${T('kit.busqueda')}</span>` : ''}
                ${esES ? estado.badge(i.afiliado) : ''}
                </div>
              </div>
              <div class="item-acciones">
                ${alt
                  ? `<a class="btn-amazon" href="${alt}" target="_blank" rel="sponsored nofollow noopener">${T('item.buscarAlt')}</a>`
                  : (enlace
                     ? `<a class="btn-amazon" href="${enlace}" target="_blank" rel="sponsored nofollow noopener">${esES ? (i.es_busqueda ? T('kit.verPrecios') : T('kit.comprar')) : T('kit.verBusqueda')}</a>`
                     : `<span class="sin-enlace">${T('kit.sinEnlace')}</span>`)}
              </div>
            </li>`;}).join('')}
        </ul>
      </div>`).join('');

    // La cesta («Llévate todo el kit») sólo tiene sentido si la mayoría de los
    // productos tienen ficha /dp/ que añadir. Con poca cobertura el botón
    // llevaría a una cesta casi vacía: en ese caso se ofrece la búsqueda.
    // Fuera de España no hay ASIN local verificado: se enlaza a la búsqueda.
    const cartable = esES && nProd > 0 && (nConFicha / nProd) >= 0.4;

    const guia = kit.guia ? `
      <div class="guia-kit">
        <h2>${T('kit.guia')}</h2>
        ${['antes', 'durante', 'despues'].map(f => `
          <div class="bloque">
            <h3>${T('kit.' + f)}</h3>
            <ul>${kit.guia[f].map(p => `<li>${p}</li>`).join('')}</ul>
          </div>`).join('')}
      </div>` : '';

    const paraQuien = (kit.paraQuien || kit.paraQuien_no || kit.coste_total) ? `
      <div class="kit-paraquien">
        ${kit.paraQuien ? `<p class="pq"><strong>${T('kit.paraQuien')}</strong> ${kit.paraQuien}</p>` : ''}
        ${kit.paraQuien_no ? `<p class="pq no"><strong>${T('kit.noBasta')}</strong> ${kit.paraQuien_no}</p>` : ''}
        ${kit.coste_total ? `<p class="pq coste"><strong>${T('kit.coste')}</strong> ${i18n.precio(kit.coste_total)}</p>` : ''}
        ${esES && coste.n >= 3 ? `<p class="pq coste-hoy"><strong>${T('kit.costeHoy')}</strong> ${T('kit.costeHoyDetalle', { suma: precios.eur(coste.suma), n: coste.n, total: coste.total, fecha: precios.fecha() })}${coste.nEs ? ` ${T('kit.costeHoyEsenciales', { nEs: coste.nEs, esSuma: precios.eur(coste.esSuma) })}` : ''}</p>` : ''}
      </div>` : '';

    const errores = (kit.errores && kit.errores.length) ? `
      <div class="guia-kit kit-errores">
        <h2>${T('kit.errores')}</h2>
        <ol>${kit.errores.map(e => `<li>${e}</li>`).join('')}</ol>
      </div>` : '';

    const entradas = blog.porKit(kit.slug).filter(e => this.esEspana() || e._traducido).slice(0, 4);
    const blogBox = entradas.length ? `
      <div class="guia-kit kit-blog">
        <h2>${T('kit.blogRel')}</h2>
        <ul>${entradas.map(e => `<li><a href="${this.url('/blog/' + e.slug + '/')}">${e.titulo}</a> — ${T('blog.lectura', { n: this.lectura(e) })}</li>`).join('')}</ul>
      </div>` : '';

    const fuente = kit.fuente ? `
      <p class="fuente">${T('kit.fuente')} <a href="${kit.fuente.url}" target="_blank" rel="noopener">${kit.fuente.nombre}</a></p>` : '';

    /* Banda de la bandera: rectángulo rojo con la cruz blanca, solo para el
       kit que se apoya en una lista oficial extranjera (hoy, Suiza). */
    const banda = kit.bandera === 'ch' ? `
      <div class="banda-suiza">
        ${this.banderaCH()}
        <span><b>${T('banda.suiza')}</b>${T('banda.suizaTxt')}</span>
      </div>` : '';

    const buscarKit = i18n.amazonBusqueda(kit.busc || kit.titulo.replace(/^Kit\s+/i, ''));
    const ctaPrincipal = cartable
      ? `<button class="btn ambar btn-cesta-top" onclick="ui.armarCesta('${kit.slug}')">${T('kit.cestaTodo')}</button>`
      : `<a class="btn ambar btn-cesta-top" href="${buscarKit}" target="_blank" rel="sponsored nofollow noopener" title="${T('kit.cestaTip')}">${T('kit.verAmazon')}</a>`;

    return `
      <section class="ficha">
        <div class="ficha-cab">
          <a class="volver" href="${this.url('/')}">${T('kit.todos')}</a>
          <h1><span class="icono-h1${kit.bandera ? ' icono-h1--bandera' : ''}">${kit.bandera === 'ch' ? this.banderaCH() : kit.icono}</span>${kit.titulo}</h1>
          <p class="resumen">${kit.resumen}</p>
          ${banda}
          ${fuente}
        </div>
        <div class="barra-progreso">
          <div class="bp-txt">
            <b>${nProd}</b>
            <span>${T('kit.productos', { n: nProd, e: nEs })}${cartable ? '' : T('kit.sinFichas')}</span>
          </div>
          ${ctaPrincipal}
        </div>
        ${paraQuien}
        ${secciones}
        ${esES && precios.data ? `<p class="lista-nota">${T('precio.avisoApi', { fecha: precios.fecha() || T('precio.hoyTxt') })}</p>` : ''}
        ${cartable && asinsEs.size > 0 ? `<button class="btn ambar full btn-cesta" onclick="ui.armarCesta('${kit.slug}','esenciales')">${T('kit.cestaEsenciales', { n: asinsEs.size })}</button>` : ''}
        ${errores}
        ${guia}
        ${blogBox}
        <button class="btn negro full" onclick="window.print()">${T('kit.imprimir')}</button>
      </section>`;
  },

  /* ---- Cesta Amazon en 1 clic, un ASIN por línea y sin repetir ----
     modo 'todo' (por defecto): TODOS los productos con ficha del kit.
     modo 'esenciales': solo los marcados como imprescindibles.          */
  armarCesta(slug, modo) {
    const kit = state.kitPorSlug(slug);
    if (!kit) return;
    const soloEsenciales = modo === 'esenciales';
    // Un ASIN repetido en el kit (p.ej. 2ª batería LFP) NO es dedupe: hay que
    // llevar N unidades, así que se acumula la cantidad en vez de descartarlo.
    const cant = new Map();
    if (modo !== 'buscar' && this.esEspana()) {
      kit.secciones.forEach(s => s.items.forEach(i => {
        if (!i.afiliado) return;
        if (soloEsenciales && i.prioridad !== 'esencial') return;
        const m = /\/dp\/([A-Z0-9]{10})/.exec(i.afiliado);
        if (m) cant.set(m[1], (cant.get(m[1]) || 0) + 1);
      }));
    }
    const asins = [...cant.keys()];
    if (asins.length) {
      const params = asins.map((a, idx) => `ASIN.${idx+1}=${a}&Quantity.${idx+1}=${cant.get(a)}`).join('&');
      window.open(`https://${i18n.amazon.dominio}/gp/aws/cart/add.html?${params}&tag=${this.tag}`, '_blank', 'noopener');
      return;
    }
    // Sin fichas /dp/ suficientes no se puede montar la cesta (el botón quedaría
    // muerto): fallback honesto → búsqueda del kit en Amazon (kit.busc o título).
    const q = kit.busc || kit.titulo.replace(/^Kit\s+/i, '');
    window.open(i18n.amazonBusqueda(q), '_blank', 'noopener');
  },

tablasSeguras(html) {
    return String(html)
      .replace(/<table/gi, '<div class="tabla-scroll"><table')
      .replace(/<\/table>/gi, '</table></div>');
  },

  /* ---- NOTICIAS: lo que está pasando (datos de scripts/noticias.py) ----
     Solo España: el lector mira Google News edición España y los avisos son de
     AEMET. En otros mercados la página no se genera ni aparece en la nav. */
  htmlNoticias() {
    const N = (typeof noticias !== 'undefined') ? noticias : null;
    const esc = s => (N ? N.esc(s) : String(s == null ? '' : s));
    const d = N && N.datos;
    const al = N && N.alertas;
    const inicio = this.url('/');
    const zonaUrl = this.url('/zona/');

    if (!d || !d.temas) {
      return `
      <section class="ficha noticias-pagina">
        <a class="volver" href="${inicio}">← Inicio</a>
        <span class="sec-label">Ahora</span>
        <h1>Lo que está pasando</h1>
        <p class="noticias-lead">No se han podido cargar los titulares ahora mismo
        (sin conexión o el lector de noticias no ha respondido). <b>Recarga la página</b>
        en unos segundos; el resto del sitio no depende de esto.</p>
        <p><a class="btn negro" href="${zonaUrl}">Ver el nivel de alerta de tu zona →</a></p>
      </section>`;
    }

    const fecha = N.fechaHora(d.meta && d.meta.actualizado);

    // Bloque «España ahora» con el resumen oficial de AEMET
    let espana = '';
    if (al && al.resumen) {
      const r = al.resumen;
      const avisos = (al.provincias || []).filter(p => p.nivel > 0);
      const chips = avisos.slice(0, 8).map(p => {
        const nv = N.nivel(p.nivel);
        return `<li class="aviso-chip ${nv.clase}"><span class="aviso-punto" style="background:${nv.color}"></span>
          <b>${esc(p.nombre)}</b><small>${esc(nv.txt)}</small></li>`;
      }).join('');
      const cuenta = [];
      if (r.rojo) cuenta.push(`<b>${r.rojo}</b> en rojo`);
      if (r.naranja) cuenta.push(`<b>${r.naranja}</b> en naranja`);
      if (r.amarillo) cuenta.push(`<b>${r.amarillo}</b> en amarillo`);
      if (!cuenta.length) cuenta.push('Sin avisos activos');
      espana = `
      <div class="avisos-esp">
        <div class="avisos-esp-cab">
          <h2>España ahora · nivel de alerta</h2>
          <span class="avisos-esp-fecha">AEMET · ${esc(al.meta && al.meta.elaborado ? al.meta.elaborado.slice(6, 8) + '/' + al.meta.elaborado.slice(4, 6) + ' ' + al.meta.elaborado.slice(8, 10) + ':' + al.meta.elaborado.slice(10, 12) : fecha)}</span>
        </div>
        <p class="avisos-esp-estado">${cuenta.join(' · ')} — ${r.zonas_en_aviso} zonas en aviso,
        ${r.sin_aviso} demarcaciones sin aviso.</p>
        ${chips ? `<ul class="avisos-esp-lista">${chips}</ul>` : ''}
        <p class="avisos-esp-pie">El mapa de <a href="${zonaUrl}">tu zona</a> pinta estas zonas con
        su color y te dice qué se espera en cada una. Los avisos los emite AEMET y se refrescan
        en cada visita.</p>
      </div>`;
    }

    const bloques = d.temas.map(t => {
      const items = (t.items || []).map(it => `
        <li class="noticia-item">
          <a href="${esc(it.url)}" target="_blank" rel="noopener nofollow">${esc(it.titulo)}</a>
          ${it.resumen ? `<p class="noticia-resumen">${esc(it.resumen)}</p>` : ''}
          <span class="noticia-meta">${esc(it.fuente)} · ${esc(it.fecha_txt || N.fecha(it.fecha))}</span>
        </li>`).join('');
      return `
      <article class="noticias-bloque" id="tema-${esc(t.id)}">
        <header class="noticias-bloque-cab">
          <h2>${esc(t.titulo)}<span class="noticias-n">${(t.items || []).length}</span></h2>
          <p>${esc(t.claim)}</p>
        </header>
        ${items ? `<ul class="noticias-lista">${items}</ul>`
                : `<p class="noticias-vacio">Sin titulares nuevos en los últimos días.</p>`}
      </article>`;
    }).join('');

    return `
      <section class="ficha noticias-pagina">
        <a class="volver" href="${inicio}">← Inicio</a>
        <span class="sec-label">Ahora</span>
        <h1>Lo que está pasando</h1>
        <p class="noticias-lead">Titulares reales, con su medio y su fecha: gobiernos que piden
        provisiones a su población, incendios, inundaciones y apagones. Sin alarmismo y sin
        inventar: si algo no está publicado en un medio o en AEMET, aquí no aparece.
        Actualizado ${esc(fecha)}.</p>

        ${espana}

        <p class="noticias-contexto"><b>El patrón se repite.</b> La Estrategia de Preparación de la
        UE (marzo de 2025) ya pedía a cada hogar autonomía para 72 horas, y en octubre de 2026 el
        Gobierno británico ha dicho a sus ciudadanos que tengan en casa comida, agua y efectivo
        para tres días. No es una profecía: es una recomendación oficial que casi nadie ha
        cumplido todavía.</p>

        <div class="noticias-grid">${bloques}</div>

        <div class="noticias-cierre">
          <h2>Leer esto no prepara a nadie. Tenerlo en casa, sí.</h2>
          <p>Si has llegado hasta aquí y en tu casa no hay agua para tres días, una linterna que
          funcione y una radio, el titular de hoy es tu lista de la compra.</p>
          <p class="noticias-cierre-ctas">
            <a class="btn rojo" href="${this.url('/kit/kit-basico-72h/')}">Kit básico 72 h →</a>
            <a class="btn negro" href="${this.url('/blog/plan-familiar-de-emergencia/')}">Plan familiar →</a>
            <a class="btn ambar" href="${zonaUrl}">Mi zona y sus avisos →</a>
          </p>
        </div>

        <p class="disclaimer">Los titulares enlazan al medio que los publica y no se reproducen
        íntegros. La selección la hace un lector automático sobre Google News (edición España) y
        puede incluir noticias que no afecten a tu provincia. Los avisos por zona son de
        <a href="https://www.aemet.es/es/eltiempo/prediccion/avisos" target="_blank" rel="noopener">AEMET</a>
        (Meteoalerta) y no sustituyen a las indicaciones de Protección Civil:
        <b>ante una emergencia real, llama al ${this.numEmergencias()}</b>.</p>
      </section>`;
  },

  /* ---- TU ZONA: mapa de recursos cerca de ti (solo España: IGN + AEMET + Overpass) ---- */
  htmlZona() {
    const caps = zona.CAPAS.map(c => `
      <label class="zona-cap">
        <input type="checkbox" checked data-capa="${c.id}"
               onchange="zona.alternar('${c.id}', this.checked)">
        <span class="zona-dep" style="background:${c.color}"></span>
        <span class="zona-cap-txt"><b>${c.nombre}</b><small>${c.que}</small></span>
      </label>`).join('');

    return `
      <section class="ficha zona-pagina">
        <a class="volver" href="${this.url('/')}">← Inicio</a>
        <span class="sec-label">Tu zona</span>
        <h1>Cuando algo falla, qué tienes cerca</h1>
        <p class="zona-lead">Un mapa con los puntos que de verdad importan en los primeros
        minutos: dónde hay un hospital, una farmacia, quién atiende, y dónde refugiarte o
        encontrarte. Elige tu ubicación y el radio; los datos los pinta OpenStreetMap en
        directo, desde tu navegador y sin cuenta de nada.</p>

        <div class="zona-acciones">
          <button class="btn ambar" type="button" onclick="zona.usarMiUbicacion()">Usar mi ubicación →</button>
          <form class="zona-busca" onsubmit="event.preventDefault(); zona.buscarCiudad(this.q.value)">
            <input name="q" autocomplete="address-level2" placeholder="O escribe tu ciudad (Madrid, Ceuta…)" aria-label="Ciudad">
            <button class="btn negro" type="submit">Buscar</button>
          </form>
        </div>

        <p id="zona-aviso" class="zona-aviso">Pulsa «Usar mi ubicación», escribe tu ciudad o toca
        directamente el mapa. <b>Nada se guarda</b>: la consulta va de tu navegador a
        OpenStreetMap y vuelta.</p>

        <div class="avisos-esp zona-avisos" id="zona-alertas">
          <div class="avisos-esp-cab">
            <h2>Nivel de alerta en España</h2>
            <span class="avisos-esp-fecha" id="zona-alertas-fecha">AEMET · Meteoalerta</span>
          </div>
          <p class="avisos-esp-estado" id="zona-alertas-estado">Leyendo los avisos oficiales de AEMET…</p>
          <ul class="avisos-esp-lista" id="zona-alertas-lista"></ul>
          <p class="avisos-esp-pie">
            <span class="avisos-leyenda"><i style="background:#D30000"></i>Rojo</span>
            <span class="avisos-leyenda"><i style="background:#EE8B1C"></i>Naranja</span>
            <span class="avisos-leyenda"><i style="background:#E3C400"></i>Amarillo</span>
            <span class="avisos-leyenda"><i style="background:#4C7A5A"></i>Sin aviso</span>
            — Las zonas en aviso se pintan sobre el mapa con su color.
          </p>
        </div>

        <div class="zona-mapa-wrap">
          <div id="zona-mapa" class="zona-mapa" role="application"
               aria-label="Mapa de recursos de emergencia cercanos"></div>
          <aside class="zona-panel">
            <div class="zona-bloque">
              <h3>Radio</h3>
              <div class="zona-radios">
                <button type="button" data-radio="2" class="on" onclick="zona.cambiarRadio(2)">2 km</button>
                <button type="button" data-radio="5" onclick="zona.cambiarRadio(5)">5 km</button>
                <button type="button" data-radio="10" onclick="zona.cambiarRadio(10)">10 km</button>
                <button type="button" data-radio="25" onclick="zona.cambiarRadio(25)">25 km</button>
              </div>
            </div>
            <div class="zona-bloque">
              <h3>Capas</h3>
              <div class="zona-caps">${caps}</div>
            </div>
            <ul id="zona-cuentas" class="zona-cuentas" aria-live="polite">
              <li><b>0</b> elige tu ubicación para empezar</li>
            </ul>
          </aside>
        </div>

        <div class="zona-112">
          <b class="zona-112-num">${this.numEmergencias()}</b>
          <div>
            <h3>El que no falla</h3>
            <p>Emergencias en toda España. Gratis, 24 horas y desde cualquier móvil —
            aunque no tengas línea de tu operadora, la llamada sale por cualquier red
            disponible. Guardado en la lista de contactos de todos los móviles de casa
            es la mejor preparación de las que no cuestan nada.</p>
            <a class="btn rojo" href="tel:${this.numEmergencias()}">Llamar al ${this.numEmergencias()} →</a>
          </div>
        </div>

        <p class="disclaimer">Los puntos proceden de <a href="https://www.openstreetmap.org/copyright"
        target="_blank" rel="noopener">OpenStreetMap</a> (ODbL) y se consultan en directo: pueden
        estar incompletos o desactualizados, sobre todo en refugios y protecciones civiles. El mapa
        base es del <a href="https://www.ign.es" target="_blank" rel="noopener">IGN</a> (CC BY 4.0)
        y los avisos por zona, de <a href="https://www.aemet.es/es/eltiempo/prediccion/avisos"
        target="_blank" rel="noopener">AEMET</a> (Meteoalerta).
        <b>Esta página no sustituye a las indicaciones de Protección Civil ni a los servicios de
        emergencia: ante una emergencia real, llama al 112.</b></p>
      </section>`;
  },

  /* ---- FUENTES ---- */
  htmlFuentes() {
    const T = (k, v) => this.T(k, v);
    const fuentes = state.data.meta.fuentes || [];
    const grupos = {};
    fuentes.forEach(f => {
      const c = f.cat || T('fuentes.otras');
      (grupos[c] = grupos[c] || []).push(f);
    });
    const bloques = Object.entries(grupos).map(([cat, lista]) => `
      <div class="fuentes-grupo">
        <h2>${cat}<span class="fuentes-n">${lista.length}</span></h2>
        <ul>
          ${lista.map(f => `<li>
            <a href="${f.url}" target="_blank" rel="noopener">${f.nombre}</a>
            ${f.nota ? `<p>${f.nota}</p>` : ''}
          </li>`).join('')}
        </ul>
      </div>`).join('');
    return `
      <section class="ficha fuentes-pagina">
        <a class="volver" href="${this.url('/')}">${T('fuentes.volver')}</a>
        <h1>${T('fuentes.h1')}</h1>
        <p class="fuentes-lead">${T('fuentes.lead', { n: fuentes.length, fecha: state.data.meta.ultima_revision })}</p>
        ${bloques}
        <p class="fuentes-cierre">${T('fuentes.cierre', { num: this.numEmergencias() })}</p>
      </section>`;
  }
};
