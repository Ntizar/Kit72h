/* Kit72h — Tu zona: mapa de recursos de emergencia cerca de ti.
   - Mapa base: IGN WMTS (CC BY 4.0). Alternativas: IGN topográfico y Esri satélite.
   - Datos: OpenStreetMap vía Overpass API (ODbL), consultados en vivo por radio.
   - Sin backend, sin build, sin claves: todo en el navegador.
   - El 112 es lo primero y no depende de este mapa. */

const zona = {
  map: null,
  grupos: {},          // idCapa -> L.LayerGroup
  cuentas: {},         // idCapa -> nº de puntos
  pos: null,           // {lat, lon, etiqueta}
  radio: 2,            // km (por defecto 2: a 5 km en una capital los puntos se pispan)
  cargando: false,
  leafletListo: null,

  CAPAS: [
    { id: 'sanidad', nombre: 'Sanidad', color: '#A9D6E5', rad: 7,
      filtros: [['amenity', 'hospital'], ['amenity', 'clinic'], ['amenity', 'doctors']],
      que: 'Hospitales, centros de salud y consultorios.' },
    { id: 'farmacias', nombre: 'Farmacias', color: '#EFA02B', rad: 6,
      filtros: [['amenity', 'pharmacy']],
      que: 'La de guardia está en el cartel de la puerta o en el visado del colegio farmacéutico.' },
    { id: 'emergencias', nombre: 'Policía y bomberos', color: '#D14B27', rad: 8,
      filtros: [['amenity', 'police'], ['emergency', 'fire_station']],
      que: 'Comisarías, cuartelillos de la Guardia Civil y parques de bomberos.' },
    { id: 'refugios', nombre: 'Refugios y evacuación', color: '#26201A', rad: 9,
      filtros: [['amenity', 'shelter'], ['emergency', 'assembly_point'], ['office', 'civil_defence']],
      que: 'Refugios, puntos de encuentro y dependencias de protección civil.' }
  ],

  /* ---------- Helpers ---------- */
  esc(s) {
    return String(s).replace(/[&<>"]/g, m =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[m]));
  },

  /* ---------- Leaflet bajo demanda ---------- */
  cargarLeaflet() {
    if (window.L) return Promise.resolve();
    if (this.leafletListo) return this.leafletListo;
    this.leafletListo = new Promise((ok, mal) => {
      const css = document.createElement('link');
      css.rel = 'stylesheet';
      css.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      document.head.appendChild(css);
      const s = document.createElement('script');
      s.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
      s.onload = ok;
      s.onerror = () => mal(new Error('No se pudo cargar Leaflet'));
      document.head.appendChild(s);
    });
    return this.leafletListo;
  },

  /* ---------- Arranque ---------- */
  async iniciar() {
    const cont = document.getElementById('zona-mapa');
    if (!cont || this.map) return;
    try {
      await this.cargarLeaflet();
    } catch (e) {
      cont.innerHTML = '<p class="zona-aviso">El mapa no está disponible en este ' +
        'navegador ahora mismo. <b>El 112 no depende de esta web.</b></p>';
      this.alertaMapa(navigator.onLine === false ? 'sinred' : 'leaflet');
      return;
    }

    this.map = L.map('zona-mapa', {
      scrollWheelZoom: false,
      attributionControl: true,
      zoomSnap: 0.5
    }).setView([40.2, -3.7], 6);

    const capasBase = {
      'IGN gris (recomendado)': this.baseIGN('IGNBase-gris'),
      'IGN topográfico': this.baseIGN('IGNBaseTodo'),
      'Satélite': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        { attribution: '© Esri, Maxar, Earthstar Geographics', maxZoom: 19 })
    };
    capasBase['IGN gris (recomendado)'].addTo(this.map);
    // Si el mapa base no carga (CDN caído, red cortada), también se avisa:
    // un mapa en blanco engaña más que un mapa ausente.
    let teselasMalas = 0;
    this.map.on('tileerror', () => {
      if (++teselasMalas === 10) this.alertaMapa(navigator.onLine === false ? 'sinred' : 'teselas');
    });
    L.control.layers(capasBase, null, { position: 'topright' }).addTo(this.map);

    this.CAPAS.forEach(c => {
      this.grupos[c.id] = L.layerGroup().addTo(this.map);
      this.cuentas[c.id] = 0;
    });

    // Clic en el mapa = buscar ahí (lo más rápido en móvil)
    this.map.on('click', e => this.buscarEn(e.latlng.lat, e.latlng.lng, null));

    // Si los avisos ya estaban cargados (fetch más rápido que Leaflet), se pintan ahora
    if (this.alertas) this.dibujarZonas(this.alertas);

    this.pintarEstado();
  },

  baseIGN(capa) {
    return L.tileLayer(
      'https://www.ign.es/wmts/ign-base?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0' +
      `&LAYER=${capa}&STYLE=default&TILEMATRIXSET=GoogleMapsCompatible` +
      '&TILEMATRIX={z}&TILECOL={x}&TILEROW={y}&FORMAT=image/jpeg',
      { attribution: '© IGN — Instituto Geográfico Nacional (CC BY 4.0)', maxZoom: 19 });
  },

  /* ---------- Avisos oficiales por zona (AEMET) ----------
     Los avisos no dependen del mapa: si Leaflet o Overpass fallan, la lista
     por provincia se pinta igual. Los polígonos son los de AEMET (las mismas
     zonas con las que emite el aviso), no una reconstrucción nuestra. */
  alertas: null,
  grupoAvisos: null,

  COLOR_NIVEL: { 1: '#D30000', 2: '#EE8B1C', 3: '#E3C400', 0: '#4C7A5A' },
  TXT_NIVEL: { 1: 'Rojo', 2: 'Naranja', 3: 'Amarillo', 0: 'Sin aviso' },

  async cargarAlertas() {
    const caja = document.getElementById('zona-alertas');
    if (!caja || this.alertas) return this.alertas;
    const estado = document.getElementById('zona-alertas-estado');
    try {
      const r = await fetch('/data/alertas-es.json', { cache: 'no-store' });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      const d = await r.json();
      this.alertas = d;
      this.pintarAlertas(d);
      if (this.map) this.dibujarZonas(d);
    } catch (e) {
      if (estado) {
        estado.innerHTML = 'No se han podido leer los avisos de AEMET ahora mismo. ' +
          '<b>El 112 no depende de esta web:</b> ante una emergencia real, llama al 112.';
      }
    }
    return this.alertas;
  },

  pintarAlertas(d) {
    const estado = document.getElementById('zona-alertas-estado');
    const lista = document.getElementById('zona-alertas-lista');
    const fecha = document.getElementById('zona-alertas-fecha');
    if (!lista) return;
    const res = d.resumen || {};
    const enAviso = (d.provincias || []).filter(p => p.nivel > 0);
    if (fecha && d.meta && d.meta.elaborado) {
      const e = d.meta.elaborado;   // AAAAMMDDHHMMSS
      fecha.textContent = `AEMET · ${e.slice(6, 8)}/${e.slice(4, 6)} ${e.slice(8, 10)}:${e.slice(10, 12)}`;
    }
    if (estado) {
      const partes = [];
      if (res.rojo) partes.push(`<b>${res.rojo}</b> en rojo`);
      if (res.naranja) partes.push(`<b>${res.naranja}</b> en naranja`);
      if (res.amarillo) partes.push(`<b>${res.amarillo}</b> en amarillo`);
      estado.innerHTML = partes.length
        ? `Ahora mismo: ${partes.join(' · ')}. <b>${res.zonas_en_aviso || 0}</b> zonas en aviso; ` +
          `${res.sin_aviso || 0} demarcaciones sin aviso.`
        : `Ahora mismo no hay avisos activos en ninguna de las ${res.provincias || 0} demarcaciones.`;
    }
    lista.innerHTML = enAviso.map(p => {
      const color = this.COLOR_NIVEL[p.nivel] || this.COLOR_NIVEL[0];
      const zonas = p.zonas.map(z => {
        const fen = z.avisos.map(a => a.fenomeno_txt).filter(Boolean);
        return `<li>${this.esc(z.nombre)}${fen.length ? ' — <i>' + this.esc(fen.join(', ')) + '</i>' : ''}</li>`;
      }).join('');
      return `<li class="aviso-prov">
        <span class="aviso-punto" style="background:${color}"></span>
        <div><b>${this.esc(p.nombre)}</b>
        <small>${this.esc(this.TXT_NIVEL[p.nivel] || '')}${p.ccaa ? ' · ' + this.esc(p.ccaa) : ''}</small>
        ${zonas ? `<ul class="aviso-zonas">${zonas}</ul>` : ''}</div>
      </li>`;
    }).join('') || '<li class="aviso-prov"><div>Sin avisos activos: toda España en verde.</div></li>';
  },

  dibujarZonas(d) {
    if (!this.map || !d || !d.zonas || this.grupoAvisos) return;
    this.grupoAvisos = L.geoJSON(d.zonas, {
      style: ft => {
        const n = ft.properties.nivel || 0;
        return { color: this.COLOR_NIVEL[n] || this.COLOR_NIVEL[0], weight: 2,
                 fillColor: this.COLOR_NIVEL[n] || this.COLOR_NIVEL[0],
                 fillOpacity: 0.22 };
      },
      onEachFeature: (ft, capa) => {
        const p = ft.properties;
        const avisos = (p.avisos || []).map(a =>
          `<li><b>${this.esc(a.fenomeno_txt)}</b> — ${this.esc(this.TXT_NIVEL[a.nivel] || '')}<br>` +
          `${this.esc(a.descripcion)}<br><small>${this.esc((a.desde || '').slice(0, 16).replace('T', ' '))}` +
          ` → ${this.esc((a.hasta || '').slice(0, 16).replace('T', ' '))}` +
          `${a.probabilidad ? ' · ' + this.esc(a.probabilidad) : ''}</small></li>`).join('');
        capa.bindPopup(`<b>${this.esc(p.zona)}</b><br>` +
          `<span class="zona-pop-tipo">${this.esc(p.provincia)} · ${this.esc(this.TXT_NIVEL[p.nivel] || '')}</span>` +
          `${avisos ? '<ul class="zona-pop-avisos">' + avisos + '</ul>' : ''}`);
        capa.on('mouseover', () => capa.setStyle({ fillOpacity: 0.38 }));
        capa.on('mouseout', () => capa.setStyle({ fillOpacity: 0.22 }));
      }
    }).addTo(this.map);
    // Que los pines de recursos queden SIEMPRE por encima de las manchas de aviso
    Object.values(this.grupos).forEach(g => g.bringToFront && g.bringToFront());
  },

  /* ---------- Entradas ---------- */
  async usarMiUbicacion() {
    const aviso = document.getElementById('zona-aviso');
    if (!navigator.geolocation) {
      aviso.textContent = 'Tu navegador no da la ubicación. Busca tu ciudad abajo o toca el mapa.';
      return;
    }
    aviso.textContent = 'Pidiendo tu ubicación…';
    navigator.geolocation.getCurrentPosition(
      p => this.buscarEn(p.coords.latitude, p.coords.longitude, null),
      () => { aviso.textContent = 'No hemos podido leer tu ubicación. Escribe tu ciudad o toca el mapa.'; },
      { enableHighAccuracy: false, timeout: 12000, maximumAge: 300000 }
    );
  },

  async buscarCiudad(q) {
    const aviso = document.getElementById('zona-aviso');
    if (!q || !q.trim()) return;
    aviso.textContent = `Buscando «${q}»…`;
    try {
      const url = 'https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&countrycodes=es&q='
        + encodeURIComponent(q.trim());
      const r = await fetch(url, { headers: { 'Accept': 'application/json' } });
      const d = await r.json();
      if (!d.length) { aviso.textContent = `No encuentro «${q}» en España.`; return; }
      await this.buscarEn(parseFloat(d[0].lat), parseFloat(d[0].lon), d[0].display_name);
    } catch (e) {
      aviso.textContent = 'No he podido buscar esa ciudad. Toca el mapa directamente.';
      this.alertaMapa(navigator.onLine === false ? 'sinred' : 'busqueda');
    }
  },

  /* ---------- Consulta ---------- */
  async buscarEn(lat, lon, etiqueta) {
    if (this.cargando) return;
    const aviso = document.getElementById('zona-aviso');
    this.pos = { lat, lon, etiqueta: etiqueta || `${lat.toFixed(4)}, ${lon.toFixed(4)}` };
    this.map.setView([lat, lon],
      this.radio <= 2 ? 14.5 : this.radio <= 5 ? 13.5 : this.radio <= 10 ? 12.5 : 11.5,
      { animate: true });

    if (!etiqueta) this.reverse(lat, lon);

    this.cargando = true;
    aviso.textContent = `Leyendo OpenStreetMap en un radio de ${this.radio} km…`;
    try {
      const els = await this.overpass(lat, lon, this.radio);
      this.alertaMapa(null);          // hubo respuesta: la alerta ya no aplica
      this.pintar(els);
      const total = Object.values(this.cuentas).reduce((a, b) => a + b, 0);
      const donde = this.esc(this.pos.etiqueta || '');
      aviso.innerHTML = total
        ? `${total} recursos a menos de ${this.radio} km de ${donde}.`
        : `No hay nada etiquetado en OSM a ${this.radio} km de ${donde}. ` +
          `Prueba con más radio o con otra ubicación.`;
      this.pintarEstado();
    } catch (e) {
      // Suele ser 429 (saturación puntual de Overpass) o un corte de red,
      // no un bug del mapa. El fallo se cuenta como lo que es: el escenario.
      aviso.innerHTML = 'Sin datos de OpenStreetMap ahora mismo. ' +
        '<b>El 112 no depende de esta web.</b>';
      this.alertaMapa(navigator.onLine === false ? 'sinred' : 'overpass');
    } finally {
      this.cargando = false;
    }
  },

  /* ---------- Alerta de fallo ----------
     Cuando el mapa o OpenStreetMap fallan, no se pide disculpas: se usa el
     fallo como el argumento de la casa. La web puede caerse; el kit no. */
  alertaMapa(motivo) {
    const caja = document.getElementById('zona-alerta');
    if (!caja) return;
    if (!motivo) { caja.hidden = true; caja.innerHTML = ''; return; }

    const MOTIVOS = {
      leaflet:  ['EL MAPA NO HA CARGADO',
                 'La librería del mapa no ha llegado. Bloqueada, sin conexión o el CDN caído. Da igual el motivo: ahora mismo no puedes ver dónde está el hospital más cercano.'],
      overpass: ['OPENSTREETMAP NO CONTESTA',
                 'La consulta de hospitales, farmacias y refugios ha muerto. Ahora mismo esta web no sabe decirte dónde hay ayuda.'],
      busqueda: ['NO SÉ DÓNDE ESTÁS',
                 'La búsqueda de direcciones ha fallado. La web se ha quedado sin saber en qué pueblo estás.'],
      teselas:  ['EL MAPA ESTÁ EN BLANCO',
                 'No carga ni el mapa base. Hay un mapa delante de ti y no se ve nada. Eso también pasa el día que de verdad hace falta.'],
      sinred:   ['TE HAS QUEDADO SIN CONEXIÓN',
                 'Sin red no hay mapa, ni datos, ni avisos que lleguen. Solo lo que tengas en casa y en la cabeza.']
    };
    const [titulo, que] = MOTIVOS[motivo] || MOTIVOS.overpass;

    caja.innerHTML =
      '<div class="zona-alerta-cuerpo">' +
        '<span class="zona-alerta-label">Sin mapa · sin datos</span>' +
        '<p class="zona-alerta-motivo">' + this.esc(titulo) + '</p>' +
        '<h3 class="zona-alerta-tit">Esto es exactamente lo que pasó el 29 de octubre de 2024.</h3>' +
        '<p>' + this.esc(que) + '</p>' +
        '<p>Ese día el agua se llevó la luz, la cobertura y los accesos. A las 20:11 sonó la ' +
          'alerta en los móviles de Valencia: <b>cuando sonó, la mayoría de las 229 personas ' +
          'que murieron ya habían muerto.</b> No les falló un mapa. Les faltó todo lo demás.</p>' +
        '<p><b>Mira lo que tienes ahora mismo en casa.</b> ¿El plan familiar escrito en papel? ' +
          '¿Agua para tres días? ¿Sabes a qué altura está tu casa y a dónde subirías? ' +
          'Si la respuesta es no, este fallo acaba de enseñarte lo único que importa: ' +
          'la web va a fallar, la luz va a fallar, la cobertura va a fallar. ' +
          '<b>Lo que no falla es lo que preparaste antes.</b></p>' +
        '<div class="zona-alerta-acciones">' +
          '<a class="btn rojo" href="/blog/plan-familiar-de-emergencia/">Prepáralo ahora →</a>' +
          '<a class="btn ambar" href="/kit/kit-basico-72h/">Kit 72 h →</a>' +
          '<button type="button" class="zona-reintento" onclick="zona.reintentar()">reintentar</button>' +
        '</div>' +
        '<p class="zona-alerta-nota">Emergencia real: <a href="tel:112">112</a> · gratis, 24 h, ' +
          'marca aunque no tengas cobertura de tu operadora. Es lo único de esta página que ' +
          'va a funcionar cuando todo lo demás se caiga.</p>' +
      '</div>';
    caja.hidden = false;
  },

  reintentar() {
    if (this.pos) this.buscarEn(this.pos.lat, this.pos.lon, this.pos.etiqueta);
    else this.usarMiUbicacion();
  },

  async reverse(lat, lon) {
    try {
      const r = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lon}&zoom=14`);
      const d = await r.json();
      const av = document.getElementById('zona-aviso');
      if (d && d.display_name && this.pos && this.pos.lat === lat && av &&
          av.innerHTML.includes('recursos')) {
        this.pos.etiqueta = d.display_name.split(',').slice(0, 2).join(',').trim();
        av.innerHTML = av.innerHTML.replace(/de [\d.-]+, [\d.-]+\./,
          `de ${this.esc(this.pos.etiqueta)}.`);
      }
    } catch (e) { /* sin reverse: nos quedamos con las coordenadas */ }
  },

  async overpass(lat, lon, km) {
    const dLat = km / 111.32;
    const dLon = km / (111.32 * Math.max(0.15, Math.cos(lat * Math.PI / 180)));
    const bbox = [lat - dLat, lon - dLon, lat + dLat, lon + dLon].join(',');

    const partes = [];
    this.CAPAS.forEach(c => c.filtros.forEach(([k, v]) => {
      partes.push(`  node["${k}"="${v}"](${bbox});`);
      partes.push(`   way["${k}"="${v}"](${bbox});`);
    }));
    const query = '[out:json][timeout:60];(\n' + partes.join('\n') + '\n);\nout tags center 6000;';

    const endpoints = ['https://overpass-api.de/api/interpreter',
                       'https://overpass.kumi.systems/api/interpreter'];
    let ultimo = null;
    for (const ep of endpoints) {
      try {
        const ctrl = new AbortController();
        const reloj = setTimeout(() => ctrl.abort(), 25000);
        const r = await fetch(ep, {
          method: 'POST',
          signal: ctrl.signal,
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: 'data=' + encodeURIComponent(query)
        });
        clearTimeout(reloj);
        if (!r.ok) throw new Error('HTTP ' + r.status);
        const j = await r.json();
        return j.elements || [];
      } catch (e) { ultimo = e; }
    }
    throw ultimo || new Error('sin respuesta');
  },

  /* ---------- Pintado ---------- */
  clasificar(t) {
    for (const c of this.CAPAS) {
      for (const [k, v] of c.filtros) if (t[k] === v) return c;
    }
    return null;
  },

  pintar(els) {
    const visto = new Set();
    this.CAPAS.forEach(c => { this.grupos[c.id].clearLayers(); this.cuentas[c.id] = 0; });

    els.forEach(e => {
      const t = e.tags || {};
      const lat = e.lat || (e.center && e.center.lat);
      const lon = e.lon || (e.center && e.center.lon);
      if (lat == null || lon == null) return;
      const capa = this.clasificar(t);
      if (!capa) return;

      const clave = capa.id + '|' + (t['addr:street'] || '') + (t['addr:housenumber'] || '') + (t.name || '') + lat + lon;
      if (visto.has(clave)) return;
      visto.add(clave);

      const m = L.circleMarker([lat, lon], {
        radius: capa.rad,
        color: '#0E0C09', weight: 2, fillOpacity: 0.95,
        fillColor: capa.color, className: 'zona-pin'
      });
      m.bindPopup(this.popup(t, capa));
      m.bindTooltip(t.name || capa.nombre, { direction: 'top', offset: [0, -6], className: 'zona-tip' });
      m.addTo(this.grupos[capa.id]);
      this.cuentas[capa.id]++;
    });
  },

  popup(t, capa) {
    const esc = s => String(s).replace(/[&<>"]/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[m]));
    const nombre = esc(t.name || capa.nombre);
    const dir = [t['addr:street'], t['addr:housenumber']].filter(Boolean).join(' ');
    const tel = t.phone || t['contact:phone'] || t['emergencies:phone'];
    const tipo = esc(capa.nombre);
    let h = `<b>${nombre}</b><br><span class="zona-pop-tipo">${tipo}</span>`;
    if (dir) h += `<br>${esc(dir)}${t['addr:postcode'] ? ' · ' + esc(t['addr:postcode']) : ''}`;
    if (tel) h += `<br><a href="tel:${String(tel).replace(/[^+\d]/g, '')}">${esc(tel)}</a>`;
    if (t.opening_hours) h += `<br><small>${esc(t.opening_hours)}</small>`;
    return h;
  },

  /* ---------- Controles ---------- */
  cambiarRadio(km) {
    this.radio = km;
    document.querySelectorAll('[data-radio]').forEach(b =>
      b.classList.toggle('on', Number(b.dataset.radio) === km));
    if (this.pos) this.buscarEn(this.pos.lat, this.pos.lon, this.pos.etiqueta);
  },

  alternar(id, ver) {
    const c = this.CAPAS.find(x => x.id === id);
    if (!c) return;
    if (ver) this.grupos[id].addTo(this.map);
    else this.map.removeLayer(this.grupos[id]);
  },

  pintarEstado() {
    const ul = document.getElementById('zona-cuentas');
    if (!ul) return;
    ul.innerHTML = this.CAPAS.map(c =>
      `<li><span class="zona-dep" style="background:${c.color}"></span>` +
      `<b>${this.cuentas[c.id] || 0}</b> ${c.nombre.toLowerCase()}</li>`).join('');
  }
};
