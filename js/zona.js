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
      cont.innerHTML = '<p class="zona-aviso">No se ha podido cargar el mapa ' +
        '(sin conexión o bloqueado por el navegador). ' +
        'Llama al <b>112</b> y busca «hospital», «farmacia» o ' +
        '<a href="https://www.google.com/maps/search/hospital" target="_blank" rel="noopener">míralo en un mapa ↗</a>.</p>';
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
    L.control.layers(capasBase, null, { position: 'topright' }).addTo(this.map);

    this.CAPAS.forEach(c => {
      this.grupos[c.id] = L.layerGroup().addTo(this.map);
      this.cuentas[c.id] = 0;
    });

    // Clic en el mapa = buscar ahí (lo más rápido en móvil)
    this.map.on('click', e => this.buscarEn(e.latlng.lat, e.latlng.lng, null));

    this.pintarEstado();
  },

  baseIGN(capa) {
    return L.tileLayer(
      'https://www.ign.es/wmts/ign-base?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0' +
      `&LAYER=${capa}&STYLE=default&TILEMATRIXSET=GoogleMapsCompatible` +
      '&TILEMATRIX={z}&TILECOL={x}&TILEROW={y}&FORMAT=image/jpeg',
      { attribution: '© IGN — Instituto Geográfico Nacional (CC BY 4.0)', maxZoom: 19 });
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
      this.pintar(els);
      const total = Object.values(this.cuentas).reduce((a, b) => a + b, 0);
      const donde = this.esc(this.pos.etiqueta || '');
      aviso.innerHTML = total
        ? `${total} recursos a menos de ${this.radio} km de ${donde}.`
        : `No hay nada etiquetado en OSM a ${this.radio} km de ${donde}. ` +
          `Prueba con más radio o con otra ubicación.`;
      this.pintarEstado();
    } catch (e) {
      // Suele ser 429 (saturación puntual de Overpass), no un bug del mapa.
      aviso.innerHTML = 'OpenStreetMap está saturado ahora mismo y no ha respondido. ' +
        'Es raro y dura poco: <button type="button" class="zona-reintento" ' +
        'onclick="zona.reintentar()">reintentar</button> — mientras tanto, ' +
        '<b>el 112 no depende de esta web</b>.';
    } finally {
      this.cargando = false;
    }
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
