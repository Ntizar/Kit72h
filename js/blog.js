/* Kit72h — blog: cargador de data/blog.json
   El contenido vive en datos (data/blog.json) para que el cron nocturno
   pueda ampliar entradas sin tocar código. */
const blog = {
  entradas: [],
  meta: {},

  async cargar() {
    if (this.entradas.length) return this;
    try {
      const resp = await fetch('data/blog.json');
      if (resp.ok) {
        const d = await resp.json();
        this.entradas = d.entradas || [];
        this.meta = d.meta || {};
      }
    } catch (e) { /* sin blog: el resto del sitio sigue funcionando */ }
    return this;
  },

  porSlug(slug) {
    return this.entradas.find(e => e.slug === slug) || null;
  },

  porKit(slugKit) {
    return this.entradas.filter(e =>
      (e.kits_relacionados || []).includes(slugKit) ||
      (e.cuerpo || '').includes(`#kit/${slugKit}`));
  }
};
