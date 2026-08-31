/* Kit72h — estado: comprobar si los enlaces de Amazon siguen activos */
const estado = {
  data: null,

  async cargar() {
    if (this.data) return this.data;
    try {
      const resp = await fetch('data/estado.json');
      this.data = resp.ok ? await resp.json() : null;
    } catch (e) { this.data = null; }
    return this.data;
  },

  porAfiliado(url) {
    if (!this.data || !url) return null;
    return this.data.productos[url] || null;
  },

  // badge HTML para un item
  badge(url) {
    const e = this.porAfiliado(url);
    if (!e) return '';
    if (e.estado === 'ok') return ' <span class="badge-estado ok" title="Verificado el ' + e.fecha + '">✅ disponible</span>';
    if (e.estado === 'posible_rotura') return ' <span class="badge-estado rotura" title="Verificado el ' + e.fecha + '">⚠️ posible rotura — <a class="enlace-estado" href="https://www.amazon.es/s?k=' + encodeURIComponent(e.busqueda || '') + '&tag=nti0c8-21" target="_blank" rel="sponsored nofollow noopener">buscar alternativa</a></span>';
    return '';
  }
};
