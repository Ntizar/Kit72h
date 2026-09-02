/* Kit72h — ui: render de vistas (datos en data/kits.json y data/blog.json) */
const ui = {
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
      document.title = 'Kit72h — Kits de emergencia basados en recomendaciones oficiales';
    }
    window.scrollTo(0, 0);
  },

  htmlHome() {
    const tarjetas = state.data.kits.map(k => `
      <div class="card-kit" onclick="ui.irA('kit','${k.slug}')">
        <div class="icono">${k.icono}</div>
        <h2>${k.titulo}</h2>
        <p>${k.resumen}</p>
        ${k.coste_total ? `<span class="coste-kit">💰 ${k.coste_total}</span>` : ''}
      </div>`).join('');
    const nKits = state.data.kits.length;
    const blogFeatured = blog.entradas.slice(0, 3).map(e => `
      <div class="card-kit card-blog" onclick="location.hash='blog/${e.slug}'">
        <h2>${e.titulo}</h2>
        <p>${e.resumen}</p>
        <span class="meta-blog">⏱️ ${e.lectura} de lectura</span>
      </div>`).join('');
    return `
      <section class="hero">
        <h1>Tu kit de emergencia para 72 horas</h1>
        <p>${nKits} kits con listas de producto verificadas, explicados uno a uno: para quién son, cuánto cuestan y qué errores evitar. Basados en las recomendaciones oficiales de la Unión Europea, Protección Civil y la DGT.</p>
        <span class="badge-fuente">📋 Fuente: Comisión Europea + Protección Civil</span>
      </section>
      <section class="grid-kits">${tarjetas}</section>
      ${blogFeatured ? `
      <section class="home-blog">
        <h2>Del blog de preparación</h2>
        <div class="grid-kits">${blogFeatured}</div>
        <p><a class="ver-todo" href="#blog">Ver todas las guías →</a></p>
      </section>` : ''}`;
  },

  htmlBlog() {
    const porEtiqueta = {};
    blog.entradas.forEach(e => (e.etiquetas || []).forEach(t =>
      (porEtiqueta[t] = (porEtiqueta[t] || 0) + 1)));
    const tarjetas = blog.entradas.map(e => `
      <div class="card-kit card-blog" onclick="location.hash='blog/${e.slug}'">
        <h2>${e.titulo}</h2>
        <p>${e.resumen}</p>
        <span class="meta-blog">📅 ${e.fecha} · ⏱️ ${e.lectura} de lectura ${(e.etiquetas||[]).map(t=>`<span class="tag-blog">${t}</span>`).join('')}</span>
      </div>`).join('');
    return `
      <section class="hero">
        <h1>Blog de preparación</h1>
        <p>${blog.entradas.length} guías prácticas para estar listo: qué comprar, cómo almacenarlo y cómo actuar cuando toque. Todo con fuentes oficiales citadas.</p>
      </section>
      <section class="grid-kits">${tarjetas}</section>`;
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
        <p class="meta-blog">📅 ${e.fecha} · ⏱️ ${e.lectura} de lectura · ✍️ ${e.autor || 'David Antizar'}</p>
        <div class="cuerpo-blog">${e.cuerpo}</div>
        ${fuentes ? `<div class="guia-kit"><h2>Fuentes de esta guía</h2><ul>${fuentes}</ul></div>` : ''}
        ${otras ? `<div class="guia-kit"><h2>Sigue leyendo</h2><ul>${otras}</ul></div>` : ''}
      </section>`;
  },

  htmlKit(kit) {
    const secciones = kit.secciones.map(s => `
      <div class="seccion-kit">
        <h2>${s.titulo}</h2>
        ${s.intro ? `<p class="intro-seccion">${s.intro}</p>` : ''}
        <ul class="items">
          ${s.items.map(i => `
            <li class="item${i.prioridad === 'esencial' ? ' esencial' : ''}">
              <div class="item-info">
                <span class="producto">${i.producto}${i.prioridad ? ` <em class="prio prio-${i.prioridad}">${i.prioridad}</em>` : ''}</span>
                ${i.descripcion ? `<span class="descripcion">${i.descripcion}</span>` : ''}
                ${i.precio_aprox ? `<span class="precio">~ ${i.precio_aprox}</span>` : ''}
                ${i.es_busqueda ? '<span class="badge-busqueda">🔎 búsqueda en Amazon (aún sin ficha concreta)</span>' : ''}
                ${estado.badge(i.afiliado)}
              </div>
              ${i.afiliado
                ? `<a class="btn-amazon" href="${i.afiliado}" target="_blank" rel="sponsored nofollow noopener">${i.es_busqueda ? 'Buscar en Amazon' : 'Ver en Amazon'}</a>`
                : `<span class="sin-enlace">Consejo — no se compra online</span>`}
            </li>`).join('')}
        </ul>
      </div>`).join('');

    const guia = kit.guia ? `
      <div class="guia-kit">
        <h2>Guía rápida</h2>
        ${['antes', 'durante', 'despues'].map(f => `
          <div class="bloque">
            <h3>${{ antes: '✅ Antes', durante: '⚡ Durante', despues: '🔄 Después' }[f]}</h3>
            <ul>${kit.guia[f].map(p => `<li>${p}</li>`).join('')}</ul>
          </div>`).join('')}
      </div>` : '';

    const paraQuien = (kit.paraQuien || kit.paraQuien_no || kit.coste_total) ? `
      <div class="kit-paraquien">
        ${kit.paraQuien ? `<p class="pq"><strong>👥 Para quién es.</strong> ${kit.paraQuien}</p>` : ''}
        ${kit.paraQuien_no ? `<p class="pq no"><strong>🚫 Cuándo no basta.</strong> ${kit.paraQuien_no}</p>` : ''}
        ${kit.coste_total ? `<p class="pq coste"><strong>💰 Coste orientativo.</strong> ${kit.coste_total}</p>` : ''}
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
        <a class="volver" href="#" onclick="ui.irA('home');return false">← Todos los kits</a>
        <h1>${kit.icono} ${kit.titulo}</h1>
        <p class="resumen">${kit.resumen}</p>
        ${fuente}
        ${paraQuien}
        ${secciones}
        ${errores}
        ${guia}
        ${blogBox}
        <button onclick="window.print()">🖨️ Imprimir checklist</button>
      </section>`;
  },

  htmlFuentes() {
    const lista = state.data.meta.fuentes.map(f =>
      `<li><a href="${f.url}" target="_blank" rel="noopener">${f.nombre}</a></li>`).join('');
    return `
      <section class="fuentes-pagina">
        <h1>Fuentes oficiales</h1>
        <p>Todo el contenido de este sitio se basa en documentos públicos de organismos oficiales. Revisamos periódicamente las fuentes para mantener las listas actualizadas (última revisión: ${state.data.meta.ultima_revision}).</p>
        <ul>${lista}</ul>
      </section>`;
  }
};
