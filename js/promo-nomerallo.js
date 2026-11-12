/* Kit72h — guiño cruzado a nomerallo.com (menús de 7 días con la cesta y el precio).
   Pegatina abajo a la derecha, cerrable, se recuerda 30 días. Sin cookies: sólo una
   clave local de preferencia, sin identificadores ni datos personales. */
(function () {
  var CLAVE = 'k72_promo_nr';
  var DIAS = 30;
  var URL = 'https://nomerallo.com/?utm_source=kit72h&utm_medium=tarjeta&utm_campaign=menu7dias';

  // Fuera del horneado de scripts/prerender.py: el snapshot se toma con
  // chrome-headless-shell (--dump-dom) y, si no se corta aquí, la tarjeta queda
  // congelada en el HTML de las 97 páginas (invisible y duplicada).
  var UA = navigator.userAgent || '';
  if (navigator.webdriver || UA.indexOf('HeadlessChrome') !== -1) return;

  try {
    var guardado = localStorage.getItem(CLAVE);
    if (guardado && Date.now() - Number(guardado) < DIAS * 86400000) return;
  } catch (e) { /* modo privado: se muestra igual, sólo no recuerda el cierre */ }

  var mostrada = false;

  function pintar() {
    if (mostrada || document.querySelector('.nr-promo')) return;
    mostrada = true;

    var caja = document.createElement('aside');
    caja.className = 'nr-promo';
    caja.setAttribute('role', 'complementary');
    caja.setAttribute('aria-label', 'Recomendación: nomerallo, menús de 7 días');
    caja.innerHTML =
      '<button class="nr-promo-x" type="button" aria-label="Cerrar recomendación">×</button>' +
      '<span class="nr-promo-etq">nomerallo</span>' +
      '<h2 class="nr-promo-t">¿Tú también estás harto de ir a hacer la compra?</h2>' +
      '<p class="nr-promo-b">Menús de 7 días con la cesta ya sumada: precio por persona, kcal y lista del súper. Gratis.</p>' +
      '<a class="nr-promo-cta" href="' + URL + '" target="_blank" rel="noopener">Ver los menús →</a>';

    document.body.appendChild(caja);
    // Reflow forzado + clase: arranca la transición sin depender de requestAnimationFrame
    // (en headless y con la pestaña en segundo plano rAF puede no dispararse nunca).
    void caja.offsetWidth;
    caja.classList.add('is-on');

    caja.querySelector('.nr-promo-x').addEventListener('click', function () {
      caja.classList.remove('is-on');
      try { localStorage.setItem(CLAVE, String(Date.now())); } catch (e) {}
      setTimeout(function () { caja.remove(); }, 260);
    });
  }

  function alScroll() {
    var alto = document.documentElement.scrollHeight - window.innerHeight;
    if (alto > 0 && window.scrollY / alto >= 0.35) {
      window.removeEventListener('scroll', alScroll);
      pintar();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', arrancar);
  } else {
    arrancar();
  }

  function arrancar() {
    // En móvil no se entra por tiempo: la tarjeta a ancho completo taparía el CTA
    // del hero. Ahí sólo aparece cuando el visitante ya ha avanzado en la página.
    var movil = window.matchMedia('(max-width: 520px)').matches;
    if (!movil) setTimeout(pintar, 7000);
    window.addEventListener('scroll', alScroll, { passive: true });
  }
})();
