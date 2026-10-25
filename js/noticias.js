/* Kit72h — noticias: cargador de data/noticias.json + data/alertas-es.json
   Los datos los refresca scripts/noticias.py (prensa vía Google News RSS y
   avisos oficiales de AEMET). Aquí solo se leen y se formatean.
   Si los ficheros no llegan, la página sigue en pie con el HTML horneado. */
const noticias = {
  datos: null,
  alertas: null,
  cargado: false,

  async cargar() {
    if (this.cargado) return this;
    this.cargado = true;
    const [n, a] = await Promise.all([
      fetch('/data/noticias.json', { cache: 'no-store' })
        .then(r => (r.ok ? r.json() : null)).catch(() => null),
      fetch('/data/alertas-es.json', { cache: 'no-store' })
        .then(r => (r.ok ? r.json() : null)).catch(() => null)
    ]);
    this.datos = n;
    this.alertas = a;
    return this;
  },

  /* «2026-10-25T11:24:29+01:00» -> «25 oct» */
  fecha(iso) {
    if (!iso) return '';
    const meses = ['ene', 'feb', 'mar', 'abr', 'may', 'jun',
                   'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
    const d = new Date(iso);
    if (isNaN(d)) return '';
    return d.getDate() + ' ' + meses[d.getMonth()];
  },

  /* «2026-10-25T21:35:00+01:00» -> «25 oct · 21:35» */
  fechaHora(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    if (isNaN(d)) return '';
    const hh = String(d.getHours()).padStart(2, '0');
    const mm = String(d.getMinutes()).padStart(2, '0');
    return this.fecha(iso) + ' · ' + hh + ':' + mm;
  },

  esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, m =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[m]));
  },

  /* Niveles AEMET: 1 rojo · 2 naranja · 3 amarillo · 0 sin aviso */
  NIVEL: {
    1: { txt: 'Rojo', color: '#D30000', clase: 'n1' },
    2: { txt: 'Naranja', color: '#EE8B1C', clase: 'n2' },
    3: { txt: 'Amarillo', color: '#E3C400', clase: 'n3' },
    0: { txt: 'Sin aviso', color: '#4C7A5A', clase: 'n0' }
  },

  nivel(n) {
    return this.NIVEL[n] || this.NIVEL[0];
  }
};
