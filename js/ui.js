/* Kit72h — ui: render de vistas tácticas (datos en data/kits.json y data/blog.json) */
const ui = {
  tag: 'nti0c8-21',

  marquee(txt) {
    const span = `<span>${txt}</span>`;
    return (span + ' ·').repeat(1) + span + span + span + span + span + span;
  },

  irA(vista, slug = null) {
    location.hash = slug ? `#kit/${slug}` : vista === 'home' ? '' : `#${vista}`;
    this.render();
  },

  vistaDesdeHash() {
    const h = location.hash.replace('#', '');
    if (h.startsWith('kit/')) return { vista: 'kit', slug: h.split('/')[1] };
    if (h.startsWith('blog/')) return { vista: 'blog', slug: h.split('/')[1] };
    if (h === 'blog') return { vista: 'blog' };
    if (h === 'fuentes') return { vista: 'fuentes' };
    return { vista: 'home' };
  },

  async render() {
    const { vista, slug } = this.vistaDesdeHash();
    const app = document.getElementById('app');
    document.getElementById('disclosure').textContent = state.data.disclosure;
    await Promise.all([estado.cargar(), blog.cargar()]);

    if (vista === 'kit') {
      const kit = state.kitPorSlug(slug);
      if (!kit) { location.hash = ''; return this.render(); }
      app.innerHTML = this.htmlKit(kit);
      document.title = `${kit.titulo} — Kit72h`;
      this.progresoInit();
    } else if (vista === 'fuentes') {
      app.innerHTML = this.htmlFuentes();
      document.title = 'Fuentes oficiales — Kit72h';
    } else if (vista === 'blog') {
      const entrada = slug ? blog.porSlug(slug) : null;
      if (slug && !entrada) { location.hash = 'blog'; return this.render(); }
      app.innerHTML = entrada ? this.htmlEntrada(entrada) : this.htmlBlog();
      document.title = entrada ? `${entrada.titulo} — Blog Kit72h` : 'Blog — Kit72h';
    } else {
      app.innerHTML = this.htmlHome();
      document.title = 'Kit72h — Kits de emergencia 72 horas: DANA, apagón, coche y más';
    }
    window.scrollTo(0, 0);
  },

  /* ---- HOME: cartel táctico ---- */
  htmlHome() {
    const tarjetas = state.data.kits.map((k, i) => `
      <article class="card-kit" onclick="ui.irA('kit','${k.slug}')">
        <div class="fila-top"><span class="icono">${k.icono}</span><span class="num">${String(i+1).padStart(2,'0')}</span></div>
        <h2>${k.titulo}</h2>
        <p>${k.resumen}</p>
        <div class="pie">
          <span class="coste-kit">${k.coste_total || 'Lista gratuita'}</span>
          <span class="ir">Abrir →</span>
        </div>
      </article>`).join('');
    const blogFeatured = blog.entradas.slice(0, 3).map(e => `
      <article class="card-kit card-blog" onclick="location.hash='blog/${e.slug}'">
        <span class="num">${String(blog.entradas.indexOf(e)+1).padStart(2,'0')}</span>
        <h2>${e.titulo}</h2>
        <p>${e.resumen}</p>
        <span class="meta-blog">⏱ ${e.lectura} de lectura</span>
      </article>`).join('');
    return `
      <div class="hero">
        <div class="hero-arte" aria-hidden="true"></div>
        <div class="container">
          <span class="chip">Guía práctica · España · 72 horas</span>
          <h1><span class="l1">Se va la luz.</span><span class="l2">Empieza tu plan.</span></h1>
          <p class="hero-lead">${state.data.kits.length} kits de emergencia con listas de producto verificadas una a una: para quién son, cuánto cuestan y qué errores evitar. Basados en la Comisión Europea, Protección Civil y la DGT. Sin alarmismo.</p>
          <div class="hero-ctas">
            <a class="btn ambar" href="#kits">Haz tu kit ↓</a>
            <a class="btn negro" href="#blog">Leer las guías ↗</a>
          </div>
          <div class="hero-stats">
            <div><b>${state.data.kits.length}</b><span>Kits por escenario</span></div>
            <div><b>72 H</b><span>Autonomía</span></div>
            <div><b>180+</b><span>Productos verificados</span></div>
            <div><b>1-Clic</b><span>Cesta en Amazon</span></div>
          </div>
        </div>
      </div>
      <div class="ticker" aria-hidden="true"><div class="ticker-track">${this.marquee('AGUA · LUZ · ENERGÍA · SALUD · COMIDA · DOCUMENTOS')}</div></div>
      <section class="sec clara">
        <div class="container">
          <div class="watermark" aria-hidden="true">72</div>
          <div class="sec-inner">
            <span class="sec-label">01 / El plan</span>
            <div class="plan-head">
              <h2>Un plan claro.<br><span class="acento">Cero pánico.</span></h2>
              <p>Cuando falla la luz, el agua o la carretera, los primeros minutos deciden todo. No se trata de acumular: se trata de tener lo justo, saber dónde está y haberlo ensayado una vez. La Estrategia de Preparación de la UE pide 72 horas de autonomía en cada hogar. Aquí la construyes por partes, con presupuesto a la vista.</p>
            </div>
            <div class="plan-grid">
              <div class="card-plan"><span class="hora">00:00</span><h3>Paras y respiras</h3><p>Confirmas qué pasa con una radio a pilas, no con el grupo del barrio. Desconectas electrodomésticos y guardas el móvil.</p></div>
              <div class="card-plan"><span class="hora">00:30</span><h3>Activas tu kit</h3><p>Luz, agua, radio y botiquín salen de donde siempre: una caja por hogar que todos conocen. Sin buscar a oscuras.</p></div>
              <div class="card-plan"><span class="hora">72 H</span><h3>Aguantas sin ayudas</h3><p>Comes bien, te informas y ayudas al vecino. Cuando llegue la ayuda, tú ya no la necesitas.</p></div>
            </div>
            <p class="disclaimer">Preparación civil basada en fuentes oficiales. Las listas enlazan a Amazon como afiliado: si compras, a ti no te cuesta más y esta guía sigue viva.</p>
          </div>
        </div>
      </section>
      <section class="sec oscura" id="kits">
        <div class="container">
          <div class="watermark" aria-hidden="true">KITS</div>
          <div class="sec-inner">
            <span class="sec-label">02 / Los kits</span>
            <h2>Elige tu escenario.<br><span class="acento2">Empieza por lo que te falta.</span></h2>
            <p class="sec-intro">Cada kit es una checklist marcable: ve tachando lo que ya tienes. Al final, un botón llena tu cesta de Amazon con los imprescindibles en un clic.</p>
            <div class="grid-kits">${tarjetas}</div>
          </div>
        </div>
      </section>
      <div class="ticker" aria-hidden="true"><div class="ticker-track">${this.marquee('EMPIEZA POR LO QUE TE FALTA · SIN ALARMISMO · FUENTES OFICIALES')}</div></div>
      ${blogFeatured ? `
      <section class="sec clara" id="lecturas">
        <div class="container">
          <div class="watermark" aria-hidden="true">BLOG</div>
          <div class="sec-inner">
            <span class="sec-label">03 / Lecturas</span>
            <h2>Del diario<br><span class="acento">de supervivencia</span></h2>
            <div class="grid-kits">${blogFeatured}</div>
            <p><a class="btn negro" href="#blog">Todas las guías →</a></p>
          </div>
        </div>
      </section>` : ''}`;
  },

  /* ---- BLOG ---- */
  htmlBlog() {
    const tarjetas = blog.entradas.map((e, i) => `
      <article class="card-kit card-blog" onclick="location.hash='blog/${e.slug}'">
        <div class="fila-top"><span class="num">${String(i+1).padStart(2,'0')}</span></div>
        <h2>${e.titulo}</h2>
        <p>${e.resumen}</p>
        <span class="meta-blog">📅 ${e.fecha} · ⏱ ${e.lectura} de lectura ${(e.etiquetas||[]).map(t=>`<span class="tag-blog">${t}</span>`).join('')}</span>
      </article>`).join('');
    return `
      <section class="hero hero-blog">
        <div class="container">
          <span class="chip">Diario de supervivencia</span>
          <h1><span class="l1">Saber antes</span><span class="l2">de que haga falta.</span></h1>
          <p class="hero-lead">${blog.entradas.length} guías prácticas para estar listo: qué comprar, cómo almacenarlo y cómo actuar cuando toque. Todo con fuentes oficiales citadas.</p>
        </div>
      </section>
      <section class="sec clara"><div class="container"><div class="sec-inner">
        <span class="sec-label">Índice / Guías</span>
        <div class="grid-kits">${tarjetas}</div>
      </div></div></section>`;
  },

  htmlEntrada(e) {
    const otras = blog.entradas.filter(x => x.slug !== e.slug &&
      (x.etiquetas || []).some(t => (e.etiquetas || []).includes(t)))
      .slice(0, 5)
      .map(x => `<li><a href="#blog/${x.slug}">${x.titulo}</a></li>`).join('');
    const fuentes = (e.fuente || []).map(f =>
      `<li><a href="${f.url}" target="_blank" rel="noopener">${f.nombre}</a></li>`).join('');
    return `
      <section class="ficha entrada-blog">
        <a class="volver" href="#blog">← Blog</a>
        <h1>${e.titulo}</h1>
        <p class="meta-blog">📅 ${e.fecha} · ⏱ ${e.lectura} de lectura · ✍ ${e.autor || 'David Antizar'}</p>
        <div class="cuerpo-blog">${e.cuerpo}</div>
        ${fuentes ? `<div class="guia-kit"><h2>Fuentes de esta guía</h2><ul>${fuentes}</ul></div>` : ''}
        ${otras ? `<div class="guia-kit"><h2>Sigue leyendo</h2><ul>${otras}</ul></div>` : ''}
      </section>`;
  },

  /* ---- FICHA DE KIT ---- */
  htmlKit(kit) {
    let nEs = 0;
    const secciones = kit.secciones.map((s, si) => `
      <div class="seccion-kit">
        <h2>${String(si+1).padStart(2,'0')} / ${s.titulo}</h2>
        ${s.intro ? `<p class="intro-seccion">${s.intro}</p>` : ''}
        <ul class="items">
          ${s.items.map(i => {
            const m = i.afiliado ? /\/dp\/([A-Z0-9]{10})/.exec(i.afiliado) : null;
            const es = i.prioridad === 'esencial';
            if (es && m) nEs++;
            return `
            <li class="item${es ? ' esencial' : ''}" ${m ? `data-asin="${m[1]}"` : ''}>
              <input type="checkbox" class="chk" aria-label="Marcar ${i.producto.replace(/"/g, '')}">
              <div class="item-info">
                <span class="producto">${i.producto}</span>
                ${i.descripcion ? `<span class="descripcion">${i.descripcion}</span>` : ''}
                ${i.precio_aprox ? `<span class="precio">~ ${i.precio_aprox}</span>` : ''}
                ${i.es_busqueda ? '<span class="badge-busqueda">🔎 búsqueda en Amazon (aún sin ficha concreta)</span>' : ''}
                ${estado.badge(i.afiliado)}
              </div>
              <div class="item-acciones">
                ${i.afiliado
                  ? `<a class="btn-amazon" href="${i.afiliado}" target="_blank" rel="sponsored nofollow noopener">${i.es_busqueda ? 'Buscar en Amazon ↗' : 'Ver en Amazon ↗'}</a>`
                  : `<span class="sin-enlace">Consejo — no se compra online</span>`}
              </div>
            </li>`;}).join('')}
        </ul>
      </div>`).join('');

    const guia = kit.guia ? `
      <div class="guia-kit">
        <h2>Guía rápida</h2>
        ${['antes', 'durante', 'despues'].map(f => `
          <div class="bloque">
            <h3>${{ antes: '→ Antes', durante: '→ Durante', despues: '→ Después' }[f]}</h3>
            <ul>${kit.guia[f].map(p => `<li>${p}</li>`).join('')}</ul>
          </div>`).join('')}
      </div>` : '';

    const paraQuien = (kit.paraQuien || kit.paraQuien_no || kit.coste_total) ? `
      <div class="kit-paraquien">
        ${kit.paraQuien ? `<p class="pq"><strong>Para quién es.</strong> ${kit.paraQuien}</p>` : ''}
        ${kit.paraQuien_no ? `<p class="pq no"><strong>Cuándo no basta.</strong> ${kit.paraQuien_no}</p>` : ''}
        ${kit.coste_total ? `<p class="pq coste"><strong>Coste orientativo.</strong> ${kit.coste_total}</p>` : ''}
      </div>` : '';

    const errores = (kit.errores && kit.errores.length) ? `
      <div class="guia-kit kit-errores">
        <h2>Los 5 errores típicos (y cómo evitarlos)</h2>
        <ol>${kit.errores.map(e => `<li>${e}</li>`).join('')}</ol>
      </div>` : '';

    const entradas = blog.porKit(kit.slug).slice(0, 4);
    const blogBox = entradas.length ? `
      <div class="guia-kit kit-blog">
        <h2>Guías relacionadas del blog</h2>
        <ul>${entradas.map(e => `<li><a href="#blog/${e.slug}">${e.titulo}</a> — ${e.lectura} de lectura</li>`).join('')}</ul>
      </div>` : '';

    const fuente = kit.fuente ? `
      <p class="fuente">Fuente oficial: <a href="${kit.fuente.url}" target="_blank" rel="noopener">${kit.fuente.nombre}</a></p>` : '';

    return `
      <section class="ficha">
        <div class="ficha-cab">
          <a class="volver" href="#" onclick="ui.irA('home');return false">← Todos los kits</a>
          <h1><span class="icono-h1">${kit.icono}</span>${kit.titulo}</h1>
          <p class="resumen">${kit.resumen}</p>
          ${fuente}
        </div>
        <div class="barra-progreso">
          <b id="prog-num">0%</b>
          <div class="track"><div class="fill" id="prog-fill"></div></div>
          <span id="prog-ley">marca lo que ya tienes</span>
          <button class="btn ambar btn-cesta-top" onclick="ui.armarCesta('${kit.slug}')">Cesta llena en 1 clic →</button>
        </div>
        ${paraQuien}
        ${secciones}
        ${nEs > 0 ? `<button class="btn ambar full btn-cesta" onclick="ui.armarCesta('${kit.slug}')">Añadir los ${nEs} imprescindibles a tu cesta de Amazon →</button>` : ''}
        ${errores}
        ${guia}
        ${blogBox}
        <button class="btn negro full" onclick="window.print()">Imprimir hoja de campo ↓</button>
      </section>`;
  },

  /* ---- Progreso del checklist ---- */
  progresoInit() {
    const chks = [...document.querySelectorAll('#app .chk')];
    if (!chks.length) return;
    const esenciales = chks.filter(c => c.closest('li.esencial'));
    const objetivo = esenciales.length ? esenciales : chks;
    const upd = () => {
      const done = objetivo.filter(c => c.checked).length;
      const pct = Math.round(done / objetivo.length * 100);
      const fill = document.getElementById('prog-fill');
      if (fill) fill.style.width = pct + '%';
      const num = document.getElementById('prog-num');
      if (num) num.textContent = pct + '%';
      const ley = document.getElementById('prog-ley');
      if (ley) ley.textContent = `${done}/${objetivo.length} imprescindibles listos`;
    };
    chks.forEach(c => c.addEventListener('change', upd));
    upd();
  },

  /* ---- Cesta Amazon en 1 clic: los ASIN esenciales, uno por línea ---- */
  armarCesta(slug) {
    const kit = state.kitPorSlug(slug);
    if (!kit) return;
    const vistos = new Set(); const asins = [];
    kit.secciones.forEach(s => s.items.forEach(i => {
      if (i.prioridad !== 'esencial' || !i.afiliado) return;
      const m = /\/dp\/([A-Z0-9]{10})/.exec(i.afiliado);
      if (m && !vistos.has(m[1])) { vistos.add(m[1]); asins.push(m[1]); }
    }));
    if (!asins.length) return;
    const params = asins.map((a, idx) => `ASIN.${idx+1}=${a}&Quantity.${idx+1}=1`).join('&');
    window.open(`https://www.amazon.es/gp/aws/cart/add.html?${params}&tag=${this.tag}`, '_blank', 'noopener');
  },

  /* ---- FUENTES ---- */
  htmlFuentes() {
    const lista = state.data.meta.fuentes.map((f, i) =>
      `<li><span class="num">${String(i+1).padStart(2,'0')}</span><a href="${f.url}" target="_blank" rel="noopener">${f.nombre}</a></li>`).join('');
    return `
      <section class="ficha fuentes-pagina">
        <a class="volver" href="#" onclick="ui.irA('home');return false">← Inicio</a>
        <h1>Fuentes oficiales</h1>
        <p>Todo el contenido de este sitio se basa en documentos públicos de organismos oficiales. Revisamos periódicamente las fuentes para mantener las listas actualizadas (última revisión: ${state.data.meta.ultima_revision}).</p>
        <ul>${lista}</ul>
      </section>`;
  }
};
