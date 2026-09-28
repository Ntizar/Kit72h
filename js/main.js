/* Kit72h — entry point */
(async () => {
  // Enlaces antiguos (#kit/slug) -> URLs reales
  const h = location.hash;
  if (h.startsWith('#kit/')) return location.replace('/kit/' + h.slice(5) + '/');
  if (h.startsWith('#blog/')) return location.replace('/blog/' + h.slice(6) + '/');
  if (h === '#blog') return location.replace('/blog/');
  if (h === '#fuentes') return location.replace('/fuentes/');
  await state.cargar();
  ui.render();
  window.addEventListener('hashchange', () => ui.render());
})();
