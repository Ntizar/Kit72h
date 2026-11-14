/* Kit72h — state: carga y acceso a datos.
   data/kits.json es la fuente de verdad en castellano. Para otros idiomas se
   carga encima data/i18n/contenido/<lang>.json y se fusiona: los enlaces de
   Amazon, ASINs y estructura NUNCA se traducen, solo los textos. */
const state = {
  data: null,

  async cargar() {
    if (this.data) return this.data;
    const resp = await fetch('/data/kits.json');
    if (!resp.ok) throw new Error('No se pudo cargar data/kits.json');
    const base = await resp.json();
    this.data = await fusionarContenido(base, 'kits');
    return this.data;
  },

  kitPorSlug(slug) {
    return this.data.kits.find(k => k.slug === slug) || null;
  }
};

/* Fusiona el overlay traducido sobre el contenido base. Tolera que falte
   cualquier campo: si el overlay está a medias, el castellano rellena. */
async function fusionarContenido(base, tipo) {
  const mercado = (typeof i18n !== 'undefined' && i18n.mercado) ? i18n.mercado : null;
  const idioma = mercado && mercado.contenido ? mercado.contenido : 'es';
  if (!mercado || idioma === 'es' || mercado.id === 'es') return base;
  let ov = null;
  try {
    const r = await fetch(`/data/i18n/contenido/${idioma}.json`);
    if (r.ok) ov = await r.json();
  } catch (e) { /* sin overlay: se queda en castellano, nunca en blanco */ }
  if (!ov) return base;

  if (tipo === 'kits') {
    if (ov.disclosure) base.disclosure = ov.disclosure;
    if (ov.meta && ov.meta.fuentes && Array.isArray(base.meta && base.meta.fuentes)) {
      ov.meta.fuentes.forEach((f, i) => {
        const b = base.meta.fuentes[i];
        if (!b) return;
        if (f.cat) b.cat = f.cat;
        if (f.nota) b.nota = f.nota;
      });
    }
    (base.kits || []).forEach(k => {
      const t = ov.kits && ov.kits[k.slug];
      if (!t) return;
      ['titulo', 'resumen', 'coste_total', 'paraQuien', 'paraQuien_no', 'busc'].forEach(c => {
        if (t[c]) k[c] = t[c];
      });
      if (t.guia) {
        ['antes', 'durante', 'despues'].forEach(f => {
          if (Array.isArray(t.guia[f])) k.guia[f] = t.guia[f];
        });
      }
      if (Array.isArray(t.errores)) k.errores = t.errores;
      if (Array.isArray(t.secciones)) {
        t.secciones.forEach((s, i) => {
          const dk = (k.secciones || [])[i];
          if (!dk) return;
          if (s.titulo) dk.titulo = s.titulo;
          if (s.intro) dk.intro = s.intro;
          (s.items || []).forEach((it, j) => {
            const di = (dk.items || [])[j];
            if (!di) return;
            if (it.producto) di.producto = it.producto;
            if (it.descripcion) di.descripcion = it.descripcion;
            // Hueco para cuando la API de Amazon devuelva el ASIN y el precio locales.
            if (it.asin_local) di.asin_local = it.asin_local;
            if (it.precio_local) di.precio_local = it.precio_local;
          });
        });
      }
      k._traducido = true;
    });
  } else if (tipo === 'blog') {
    (base.entradas || []).forEach(e => {
      const t = ov.blog && ov.blog[e.slug];
      if (!t) return;
      ['titulo', 'resumen', 'cuerpo'].forEach(c => { if (t[c]) e[c] = t[c]; });
      if (Array.isArray(t.etiquetas)) e.etiquetas = t.etiquetas;
      if (Array.isArray(t.fuente)) {
        t.fuente.forEach((f, i) => {
          if (e.fuente && e.fuente[i] && f.nombre) e.fuente[i].nombre = f.nombre;
        });
      }
      e._traducido = true;
    });
  }
  return base;
}
