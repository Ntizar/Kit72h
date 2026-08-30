/* Kit72h — ui: render de vistas */
const ui = {
  irA(vista, slug = null) {
    location.hash = slug ? `#kit/${slug}` : vista === 'home' ? '' : `#${vista}`;
    this.render();
  },

  vistaDesdeHash() {
    const h = location.hash.replace('#', '');
    if (h.startsWith('kit/')) return { vista: 'kit', slug: h.split('/')[1] };
    if (h === 'fuentes') return { vista: 'fuentes' };
    return { vista: 'home' };
  },

  render() {
    const { vista, slug } = this.vistaDesdeHash();
    const app = document.getElementById('app');
    document.getElementById('disclosure').textContent = state.data.disclosure;

    if (vista === 'kit') {
      const kit = state.kitPorSlug(slug);
      if (!kit) { location.hash = ''; return this.render(); }
      app.innerHTML = this.htmlKit(kit);
      document.title = `${kit.titulo} — Kit72h`;
    } else if (vista === 'fuentes') {
      app.innerHTML = this.htmlFuentes();
      document.title = 'Fuentes oficiales — Kit72h';
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
      </div>`).join('');
    return `
      <section class="hero">
        <h1>Tu kit de emergencia para 72 horas</h1>
        <p>Listas basadas en las recomendaciones oficiales de la Unión Europea y de Protección Civil. Elige tu escenario y prepárate hoy.</p>
        <span class="badge-fuente">📋 Fuente: Comisión Europea + Protección Civil</span>
      </section>
      <section class="grid-kits">${tarjetas}</section>`;
  },

  htmlKit(kit) {
    const secciones = kit.secciones.map(s => `
      <div class="seccion-kit">
        <h2>${s.titulo}</h2>
        <ul class="items">
          ${s.items.map(i => `
            <li class="item${i.prioridad === 'esencial' ? ' esencial' : ''}">
              <div class="item-info">
                <span class="producto">${i.producto}${i.prioridad ? ` <em class="prio prio-${i.prioridad}">${i.prioridad}</em>` : ''}</span>
                ${i.descripcion ? `<span class="descripcion">${i.descripcion}</span>` : ''}
                ${i.precio_aprox ? `<span class="precio">~ ${i.precio_aprox}</span>` : ''}
              </div>
              <a class="btn-amazon" href="${i.afiliado}" target="_blank" rel="sponsored nofollow noopener">Ver en Amazon</a>
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

    const fuente = kit.fuente ? `
      <p class="fuente">Fuente oficial: <a href="${kit.fuente.url}" target="_blank" rel="noopener">${kit.fuente.nombre}</a></p>` : '';

    return `
      <section class="ficha">
        <a class="volver" href="#" onclick="ui.irA('home');return false">← Todos los kits</a>
        <h1>${kit.icono} ${kit.titulo}</h1>
        <p class="resumen">${kit.resumen}</p>
        ${fuente}
        ${secciones}
        ${guia}
        <button onclick="window.print()">🖨️ Imprimir checklist</button>
      </section>`;
  },

  htmlFuentes() {
    const lista = state.data.meta.fuentes.map(f =>
      `<li><a href="${f.url}" target="_blank" rel="noopener">${f.nombre}</a></li>`).join('');
    return `
      <section class="fuentes-pagina">
        <h1>Fuentes oficiales</h1>
        <p>Todo el contenido de este sitio se basa en documentos públicos de organismos oficiales. Revisamos periódicamente las fuentes para mantener las listas actualizadas.</p>
        <ul>${lista}</ul>
      </section>`;
  }
};
