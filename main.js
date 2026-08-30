/* Kit72h — entry point */
(async () => {
  await state.cargar();
  ui.render();
  window.addEventListener('hashchange', () => ui.render());
})();
