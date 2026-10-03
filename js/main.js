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

/* ---- Carta PRO (grid) y cuadro KIT PRO del hero: el destello sigue al ratón ----
   Es lo que hace que una carta holográfica se sienta "viva".
   El cuadro del hero recibe el destello y el brillo, pero no el giro 3D
   (es un CTA grande: girarlo mareaba). Si el puntero no es fino (móvil),
   no pasa nada: queda la animación CSS. */
document.addEventListener('pointermove', (e) => {
  const c = e.target && e.target.closest ? e.target.closest('.card-pro-pokemon, .kpro-hero-btn') : null;
  if (c) {
    const r = c.getBoundingClientRect();
    const x = ((e.clientX - r.left) / r.width) * 100;
    const y = ((e.clientY - r.top) / r.height) * 100;
    c.style.setProperty('--px', x.toFixed(1) + '%');
    c.style.setProperty('--py', y.toFixed(1) + '%');
    if (c.classList.contains('card-pro-pokemon')) {
      const rx = ((y - 50) / 50) * -3.2;
      const ry = ((x - 50) / 50) * 3.2;
      c.style.transform = 'perspective(900px) rotateX(' + rx.toFixed(2) + 'deg) rotateY('
        + ry.toFixed(2) + 'deg) translate(-2px,-2px)';
    }
  } else {
    document.querySelectorAll('.card-pro-pokemon').forEach((el) => {
      if (el.style.transform) el.style.transform = '';
    });
  }
}, {passive: true});
