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
    const p = location.pathname.replace(/\/+$/, '') || '/';
    if (p.startsWith('/kit/')) return { vista: 'kit', slug: p.split('/')[2] };
    if (p.startsWith('/blog/')) { const s = p.split('/')[2]; return s ? { vista: 'blog', slug: s } : { vista: 'blog' }; }
    if (p === '/fuentes') return { vista: 'fuentes' };
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
    const ancla = location.hash;
    const objetivo = ancla && !ancla.startsWith('#kit/') && !ancla.startsWith('#blog/')
      && ancla !== '#fuentes' ? document.querySelector(ancla) : null;
    if (objetivo) objetivo.scrollIntoView(); else window.scrollTo(0, 0);
  },

  /* ---- HOME: espejo de la referencia (diario de supervivencia) ---- */
  htmlHome() {
    const bloques = [
      {k:'agua', n:'01', cat:'AGUA', t:'Lo primero', d:'Reserva agua potable para cada persona y ajústala a su edad, salud y circunstancia. Revisa envases y caducidad.', p:'5–20 €', q:'garrafa+agua+potable+almacenamiento', b:'Buscar recipientes',
       ic:'<path d="M12 3 C12 3 5 10.5 5 15 a7 7 0 0 0 14 0 C19 10.5 12 3 12 3 Z"/><path d="M9 15.5 a3 3 0 0 0 3 3"/>'},
      {k:'luz', n:'02', cat:'LUZ', t:'Ver sin red', d:'Una linterna LED fiable y pilas de repuesto. Una por hogar es un comienzo; reparte más si sois varios.', p:'10–30 €', q:'linterna+led+pilas+emergencia', b:'Buscar linternas',
       ic:'<path d="M12 3 a6 6 0 0 1 3.5 10.9 c-.6.5-1 1.3-1 2.1 H9.5 c0-.8-.4-1.6-1-2.1 A6 6 0 0 1 12 3 Z"/><path d="M9.5 19 h5 M10.5 21.5 h3"/>'},
      {k:'energia', n:'03', cat:'ENERGÍA', t:'Sigue conectado', d:'Batería externa cargada, cable compatible y, si te encaja, radio de pilas para recibir información.', p:'20–65 €', q:'powerbank+20000mah+radio+emergencia', b:'Buscar energía',
       ic:'<path d="M13 2 L5 14 h6 l-2 8 8-12 h-6 z"/>'},
      {k:'salud', n:'04', cat:'SALUD', t:'Cuida de los tuyos', d:'Botiquín básico, tus medicamentos habituales y necesidades específicas de bebés, mayores o mascotas.', p:'15–45 €', q:'botiquin+primeros+auxilios+hogar', b:'Buscar botiquines',
       ic:'<rect x="3.5" y="3.5" width="17" height="17"/><path d="M12 8 v8 M8 12 h8"/>'},
      {k:'comida', n:'05', cat:'COMIDA', t:'Algo que comer', d:'Alimentos duraderos que ya consumís, adaptados a alergias y dietas. Rótalos y añade un abrelatas si lo necesitas.', p:'15–50 €', q:'alimentos+no+perecederos+emergencia', b:'Buscar comida',
       ic:'<path d="M7 7 h10 v13 a1.5 1.5 0 0 1 -1.5 1.5 h-7 A1.5 1.5 0 0 1 7 20 Z"/><ellipse cx="12" cy="7" rx="5" ry="2"/><path d="M7 11 h10"/>'},
      {k:'docs', n:'06', cat:'DOCUMENTOS', t:'Lo irreemplazable', d:'Copias de identificación, contactos importantes y una funda impermeable. Guárdalos con cuidado, fuera del alcance ajeno.', p:'7–25 €', q:'bolsa+impermeable+documentos', b:'Buscar fundas',
       ic:'<path d="M7 3 h7 l4 4 v14 H7 Z"/><path d="M14 3 v4 h4"/><path d="M10 12 h6 M10 16 h6"/>'}
    ].map(b => `
      <article class="bloque-lista b-${b.k}">
        <div class="bloque-top">
          <span class="bloque-flag">${b.n} / ${b.cat}</span>
          <svg class="bloque-icono" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${b.ic}</svg>
        </div>
        <h3>${b.t}</h3>
        <p>${b.d}</p>
        <div class="bloque-pie">
          <span class="presup">Presupuesto orientativo: ${b.p}</span>
          <a class="btn-amazon" href="https://www.amazon.es/s?k=${b.q}&tag=${this.tag}" target="_blank" rel="sponsored nofollow noopener">${b.b} ↗</a>
        </div>
      </article>`).join('');

    const pruebaItems = [
      'Agua almacenada para quienes viven contigo',
      'Linterna con pilas o carga comprobada',
      'Batería externa cargada y cable',
      'Botiquín y medicación necesaria',
      'Comida no perecedera y abrelatas si hace falta',
      'Copias de documentos y contactos protegidos'
    ].map((t, i) => `
      <label class="pr-check"><input type="checkbox" class="pr-chk" id="pr${i}" onchange="ui.pruebaAct()"><span>${t}</span></label>`).join('');

    const adapt = [
      ['01', 'Corte de luz', 'Ten iluminación, batería, radio y agua accesibles. Comprueba cómo abrir persianas o puertas eléctricas sin corriente.', 'kit-apagon', 'Empieza por luz y energía'],
      ['02', 'DANA e inundación', 'Protege documentos y medicación de la humedad y sigue los avisos oficiales. No atravieses zonas inundadas.', 'kit-dana', 'Empieza por documentos'],
      ['03', 'Familia y cuidados', 'Bebés, mayores y mascotas cambian la lista: alimentación, higiene, medicación y necesidades propias.', 'kit-bebe', 'Empieza por salud']
    ].map(a => `
      <a class="card-adapt" href="/kit/${a[3]}/">
        <span class="n">${a[0]}</span>
        <h3>${a[1]}</h3>
        <p>${a[2]}</p>
        <span class="ir">${a[4]} →</span>
      </a>`).join('');

    const tarjetas = state.data.kits.map((k, i) => `
      <a class="card-kit" href="/kit/${k.slug}/">
        <div class="fila-top"><span class="icono">${k.icono}</span><span class="num">${String(i+1).padStart(2,'0')}</span></div>
        <h2>${k.titulo}</h2>
        <p>${k.resumen}</p>
        <div class="pie">
          <span class="coste-kit">${k.coste_total || 'Lista gratuita'}</span>
          <span class="ir">Abrir →</span>
        </div>
      </a>`).join('');

    const blogFeatured = blog.entradas.slice(0, 3).map((e, i) => `
      <a class="card-kit card-blog" href="/blog/${e.slug}/">
        <div class="fila-top"><span class="num">${String(i+1).padStart(2,'0')}</span></div>
        <h2>${e.titulo}</h2>
        <p>${e.resumen}</p>
        <span class="meta-blog">⏱ ${e.lectura} de lectura</span>
      </a>`).join('');

    const arte = `<div class="hero-arte" aria-hidden="true"><svg viewBox="0 0 1440 420" preserveAspectRatio="xMidYMax slice" xmlns="http://www.w3.org/2000/svg">
      <circle cx="1200" cy="110" r="44" fill="#8F7B45"/>
      <path d="M0,300 L180,175 L340,268 L520,145 L700,258 L880,185 L1060,278 L1240,195 L1440,288 L1440,300 L0,300 Z" fill="#D14B27"/>
      <path d="M0,300 L220,225 L430,300 L640,215 L860,300 L1080,235 L1300,300 L1440,258 L1440,300 L0,300 Z" fill="#9E3417"/>
      <rect y="300" width="1440" height="120" fill="#EFA02B"/>
      <rect y="300" width="1440" height="6" fill="#0E0C09" opacity="0.25"/>
    </svg></div>`;

    return `
      <div class="hero">
        ${arte}
        <div class="container">
          <span class="chip">Guía práctica · España · 72 horas</span>
          <h1><span class="l1">Se va la luz.</span><span class="l2">Empieza tu plan.</span></h1>
          <p class="hero-lead">Los primeros 30 minutos no son para buscar pilas a oscuras. Un kit 72h reúne lo esencial para pasar un corte de suministros o una evacuación breve con más margen y menos improvisación.</p>
          <div class="hero-ctas">
            <a class="btn ambar" href="#kits">Preparar mi kit →</a>
            <a class="btn negro" href="#prueba">¿Qué tengo ya? ↓</a>
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
      <section class="sec clara" id="plan">
        <div class="container">
          <div class="watermark" aria-hidden="true">72</div>
          <div class="sec-inner">
            <span class="sec-label">01 / El plan</span>
            <div class="plan-head">
              <h2>No es supervivencia.<br><span class="acento">Es estar listo.</span></h2>
              <p>No necesitas comprarlo todo hoy. Reúne primero lo que ya tienes, identifica huecos y prepara una bolsa accesible. El kit cambia según quién viva contigo.</p>
            </div>
            <div class="plan-grid">
              <div class="card-plan"><span class="hora">00:00</span><h3>Se interrumpe</h3><p>La luz, la señal o el agua pueden fallar. Ten una linterna a mano y sigue las indicaciones oficiales de tu zona.</p></div>
              <div class="card-plan"><span class="hora">00:30</span><h3>Localiza tu bolsa</h3><p>Agua, medicación habitual, radio, batería y documentos, juntos y fáciles de coger.</p></div>
              <div class="card-plan"><span class="hora">72 H</span><h3>Ganas margen</h3><p>Un kit adaptado a tu hogar te ayuda mientras se restablecen servicios o recibes instrucciones.</p></div>
            </div>
            <p class="disclaimer">No hay una garantía de autonomía universal: necesidades, clima y situación cambian. Ante una emergencia, sigue siempre a los servicios oficiales. Esta página no sustituye sus indicaciones.</p>
          </div>
        </div>
      </section>
      <section class="sec oscura" id="prueba">
        <div class="container">
          <div class="sec-inner">
            <span class="sec-label">02 / Prueba rápida</span>
            <h2>¿Cuánto tienes<br><span class="acento2">ya preparado?</span></h2>
            <div class="prueba">
              <p style="font-size:13.5px;color:#c9c0b0;margin:0">Marca solo lo que tienes en casa, está accesible y funciona. No es una predicción de cuántas horas aguantarás: es una foto de tu preparación en seis piezas.</p>
              <div class="prueba-grid">${pruebaItems}</div>
              <div class="prueba-res">
                <b id="pr-count">0</b><span style="font-family:var(--display);font-size:22px;color:var(--ambar)">/6</span>
                <p>Empieza por el agua y la luz. Dos básicos que agradecerás tener localizados.</p>
                <a class="btn ambar" href="#kits">Ver qué me falta →</a>
              </div>
            </div>
          </div>
        </div>
      </section>
      <section class="sec clara">
        <div class="container">
          <div class="watermark" aria-hidden="true">LISTA</div>
          <div class="sec-inner">
            <span class="sec-label">03 / Tu lista</span>
            <h2>El kit, <span class="acento">sin humo.</span></h2>
            <p class="sec-intro" style="color:#4a4238">Seis bloques. Antes de comprar, mira qué tienes. Los botones abren búsquedas en Amazon.es con los rangos de presupuesto para planificar.</p>
            <div class="lista-bloques">${bloques}</div>
            <div class="ruta-corta">
              <div>
                <span class="bloque-num" style="border:none;padding:0">La ruta corta</span>
                <h3>Una bolsa.<br>Un plan.<br>Más calma.</h3>
              </div>
              <div>
                <ul>
                  <li>Revisa el contenido real de los kits ya preparados</li>
                  <li>Personaliza para bebés y mayores</li>
                  <li>Comprueba caducidades cada cierto tiempo</li>
                </ul>
                <a class="btn ambar" href="https://www.amazon.es/s?k=kit+emergencia+72+horas&tag=${this.tag}" target="_blank" rel="sponsored nofollow noopener">Buscar kit 72h en Amazon ↗</a>
              </div>
            </div>
            <p class="lista-nota">* Los rangos son ejemplos de presupuesto para planificar, no precios actuales ni ofertas verificadas. Medicación y dietas especiales no incluidas.</p>
          </div>
        </div>
      </section>
      <section class="sec oscura" id="kits">
        <div class="container">
          <div class="watermark" aria-hidden="true">KITS</div>
          <div class="sec-inner">
            <span class="sec-label">04 / Los kits</span>
            <h2>Elige tu escenario.<br><span class="acento2">Empieza por lo que te falta.</span></h2>
            <p class="sec-intro">Cada kit es una checklist marcable: ve tachando lo que ya tienes. Al final, un botón llena tu cesta de Amazon con los imprescindibles en un clic.</p>
            <div class="grid-kits">${tarjetas}</div>
          </div>
        </div>
      </section>
      ${blogFeatured ? `
      <section class="sec clara" id="lecturas">
        <div class="container">
          <div class="watermark" aria-hidden="true">BLOG</div>
          <div class="sec-inner">
            <span class="sec-label">05 / Lecturas</span>
            <h2>Del diario<br><span class="acento">de supervivencia</span></h2>
            <div class="grid-kits">${blogFeatured}</div>
            <p><a class="btn negro" href="/blog/">Todas las guías →</a></p>
          </div>
        </div>
      </section>` : ''}
      <section class="sec clara" id="adaptalo">
        <div class="container">
          <div class="watermark" aria-hidden="true">TUYO</div>
          <div class="sec-inner">
            <span class="sec-label">06 / Adáptalo</span>
            <h2>Tu casa. <span class="acento">Tu kit.</span></h2>
            <p class="sec-intro" style="color:#4a4238">Un kit genérico es solo el comienzo. Hazlo útil para tu vida real.</p>
            <div class="adapt-grid">${adapt}</div>
          </div>
        </div>
      </section>
      <section class="cta-final">
        <div class="container">
          <span class="sec-label">El siguiente paso es pequeño</span>
          <h2>El mejor día<br>para empezar <span class="acento">es hoy.</span></h2>
          <p>Reúne lo que ya tienes esta noche. Después completa los huecos. Sin miedo fabricado ni compras a ciegas: un kit que sea tuyo.</p>
          <div class="hero-ctas">
            <a class="btn ambar" href="#kits">Hacer mi lista →</a>
            <a class="btn negro" href="https://www.amazon.es/s?k=kit+emergencia+72+horas&tag=${this.tag}" target="_blank" rel="sponsored nofollow noopener">Explorar kits en Amazon ↗</a>
          </div>
        </div>
      </section>`;
  },

  pruebaAct() {
    const chks = [...document.querySelectorAll('.pr-chk')];
    const n = chks.filter(c => c.checked).length;
    const el = document.getElementById('pr-count');
    if (el) el.textContent = String(n);
  },

  /* ---- BLOG ---- */
  htmlBlog() {
    const tarjetas = blog.entradas.map((e, i) => `
      <a class="card-kit card-blog" href="/blog/${e.slug}/">
        <div class="fila-top"><span class="num">${String(i+1).padStart(2,'0')}</span></div>
        <h2>${e.titulo}</h2>
        <p>${e.resumen}</p>
        <span class="meta-blog">📅 ${e.fecha} · ⏱ ${e.lectura} de lectura ${(e.etiquetas||[]).map(t=>`<span class="tag-blog">${t}</span>`).join('')}</span>
      </a>`).join('');
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
        <a class="volver" href="/blog/">← Blog</a>
        <h1>${e.titulo}</h1>
        <p class="meta-blog">📅 ${e.fecha} · ⏱ ${e.lectura} de lectura</p>
        <div class="cuerpo-blog">${this.tablasSeguras(e.cuerpo)}</div>
        ${fuentes ? `<div class="guia-kit"><h2>Fuentes de esta guía</h2><ul>${fuentes}</ul></div>` : ''}
        ${otras ? `<div class="guia-kit"><h2>Sigue leyendo</h2><ul>${otras}</ul></div>` : ''}
      </section>`;
  },

  /* ---- FICHA DE KIT ---- */
  htmlKit(kit) {
    let nEs = 0;
    const asinsEs = new Set();   // ASINs unicos imprescindibles (la cesta deduplica)

    const secciones = kit.secciones.map((s, si) => `
      <div class="seccion-kit">
        <h2>${String(si+1).padStart(2,'0')} / ${s.titulo}</h2>
        ${s.intro ? `<p class="intro-seccion">${s.intro}</p>` : ''}
        <ul class="items">
          ${s.items.map(i => {
            const m = i.afiliado ? /\/dp\/([A-Z0-9]{10})/.exec(i.afiliado) : null;
            const es = i.prioridad === 'esencial';
            if (es && m) asinsEs.add(m[1]);
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

    nEs = asinsEs.size;

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
          <a class="volver" href="/">← Todos los kits</a>
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
        ${nEs > 0 ? `<button class="btn ambar full btn-cesta" onclick="ui.armarCesta('${kit.slug}','esenciales')">Añadir los ${nEs} imprescindibles a tu cesta de Amazon →</button>` : ''}
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

  /* ---- Cesta Amazon en 1 clic, un ASIN por línea y sin repetir ----
     modo 'todo' (por defecto): TODOS los productos con ficha del kit.
     modo 'esenciales': solo los marcados como imprescindibles.          */
  armarCesta(slug, modo) {
    const kit = state.kitPorSlug(slug);
    if (!kit) return;
    const soloEsenciales = modo === 'esenciales';
    const vistos = new Set(); const asins = [];
    kit.secciones.forEach(s => s.items.forEach(i => {
      if (!i.afiliado) return;
      if (soloEsenciales && i.prioridad !== 'esencial') return;
      const m = /\/dp\/([A-Z0-9]{10})/.exec(i.afiliado);
      if (m && !vistos.has(m[1])) { vistos.add(m[1]); asins.push(m[1]); }
    }));
    if (!asins.length) return;
    const params = asins.map((a, idx) => `ASIN.${idx+1}=${a}&Quantity.${idx+1}=1`).join('&');
    window.open(`https://www.amazon.es/gp/aws/cart/add.html?${params}&tag=${this.tag}`, '_blank', 'noopener');
  },

tablasSeguras(html) {
    return String(html)
      .replace(/<table/gi, '<div class="tabla-scroll"><table')
      .replace(/<\/table>/gi, '</table></div>');
  },

  /* ---- FUENTES ---- */
  htmlFuentes() {
    const lista = state.data.meta.fuentes.map((f, i) =>
      `<li><span class="num">${String(i+1).padStart(2,'0')}</span><a href="${f.url}" target="_blank" rel="noopener">${f.nombre}</a></li>`).join('');
    return `
      <section class="ficha fuentes-pagina">
        <a class="volver" href="/">← Inicio</a>
        <h1>Fuentes oficiales</h1>
        <p>Todo el contenido de este sitio se basa en documentos públicos de organismos oficiales. Revisamos periódicamente las fuentes para mantener las listas actualizadas (última revisión: ${state.data.meta.ultima_revision}).</p>
        <ul>${lista}</ul>
      </section>`;
  }
};
