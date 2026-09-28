/* Kit72h — estado: comprobar si los enlaces de Amazon siguen activos */
const estado = {
  data: null,

  async cargar() {
    if (this.data) return this.data;
    try {
      const resp = await fetch('/data/estado.json');
      this.data = resp.ok ? await resp.json() : null;
    } catch (e) { this.data = null; }
    return this.data;
  },

  porAfiliado(url) {
    if (!this.data || !url) return null;
    return (this.data.productos || {})[url] || null;
  },

  // badge HTML para un item; vacío si no hay nada cierto que decir
  // (los estados los genera scripts/verificar-fichas.py: texto/aviso/caducado)
  badge(url) {
    const e = this.porAfiliado(url);
    if (!e || !e.texto) return '';
    const alt = e.aviso === 'ok' ? '' :
      ` — <a class="enlace-estado" href="https://www.amazon.es/s?k=${encodeURIComponent(e.busqueda || '')}&tag=nti0c8-21" target="_blank" rel="sponsored nofollow noopener">buscar alternativa</a>`;
    const clase = e.aviso === 'ok' ? 'ok' : 'rotura';
    const titulo = e.aviso === 'ok' ? `Ficha comprobada el ${e.fecha}` : `Última comprobación: ${e.fecha}`;
    return ` <span class="badge-estado ${clase}" title="${titulo}">${e.texto}${alt}</span>`;
  }
};
