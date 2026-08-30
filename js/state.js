/* Kit72h — state: carga y acceso a datos */
const state = {
  data: null,

  async cargar() {
    const resp = await fetch('data/kits.json');
    if (!resp.ok) throw new Error('No se pudo cargar data/kits.json');
    this.data = await resp.json();
    return this.data;
  },

  kitPorSlug(slug) {
    return this.data.kits.find(k => k.slug === slug) || null;
  }
};
