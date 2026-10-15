#!/usr/bin/env python3
"""Kit72h — añadir/actualizar la entrada de blog 'mejor-starlink-espana-precio'.

Re-ejecutable: si la entrada ya existe la REEMPLAZA (no falla), mantiene el
orden por fecha descendente y recalcula meta.total / meta.ultima_revision.
Fila del mapa de keywords: «mejor Starlink España precio» (Cluster C, P2,
comparativa de compra — la última fila sin cubrir).
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUTA = RAIZ / "data" / "blog.json"
HOY = "2026-10-15"
SLUG = "mejor-starlink-espana-precio"

CUERPO = """
<p>Casi todas las preguntas sobre Starlink que llegan a este blog empiezan igual: <strong>¿cuánto cuesta de verdad y qué plan me hace falta?</strong> En 2026 cambió dos veces: en marzo Starlink pasó de dos planes a tres, y en junio añadió <strong>10 €/mes por el alquiler del kit</strong> a las nuevas altas. Aquí van los precios oficiales del día, la comparativa y el veredicto por caso.</p>

<p>No es un producto de nicho: según el tráfico de red, Starlink ya sería la <strong>sexta operadora de España, con más de medio millón de usuarios</strong>, y en el apagón del 28 de abril de 2025 la satélite fue de las pocas que siguieron funcionando. Ese es el argumento de este sitio: que la conexión no desaparezca justo cuando la necesitas. Las lecciones de aquel día, en <a href="/blog/apagon-lecciones-28a/">el apagón del 28 de abril</a>; el equipo, en el <a href="/kit/kit-starlink/">kit de Starlink</a>.</p>

<h2>1. Los cinco planes de Starlink en España, comparados</h2>

<p>Starlink vende en España dos familias: <strong>Residencial</strong> (vivienda fija) e <strong>Itinerante</strong> (autocaravanas, veleros, uso en movimiento). Todos incluyen datos ilimitados y 30 días de prueba con devolución completa. Los precios son los de la web oficial de Starlink para España:</p>

<table>
<thead><tr><th>Plan</th><th>Precio/mes</th><th>Descarga</th><th>Prioridad</th><th>Para quién</th></tr></thead>
<tbody>
<tr><td>Residencial 100</td><td>35 €</td><td>hasta 100 Mb/s (limitados)</td><td>No</td><td>Piso pequeño, segunda vivienda, uso básico</td></tr>
<tr><td>Residencial 200</td><td>45 €</td><td>hasta 200 Mb/s</td><td>No</td><td>Familia con teletrabajo y varios dispositivos</td></tr>
<tr><td>Residencial Max</td><td>65 €</td><td>más de 400 Mb/s</td><td>Sí, la máxima</td><td>Casa grande, red mallada, muchas pantallas</td></tr>
<tr><td>Itinerante 100 GB</td><td>45 €</td><td>100 GB rápidos y luego a baja velocidad</td><td>No</td><td>Autocaravana o velero con uso puntual</td></tr>
<tr><td>Itinerante ilimitada</td><td>95 €</td><td>ilimitada en movimiento</td><td>No</td><td>Vida nómada, trabajo desde cualquier sitio</td></tr>
</tbody>
</table>

<p><strong>Ganadores por categoría:</strong> el <strong>Residencial 200 (45 €)</strong> es el punto dulce: dobla la velocidad del básico sin pagar la prioridad del Max. Para un piso pequeño o segunda residencia, el <strong>Residencial 100 (35 €)</strong> sobra. El <strong>Max (65 €)</strong> solo compensa con varios conectados a la vez o prioridad real en horas punta. Para la furgoneta, el <strong>Itinerante de 100 GB (45 €)</strong> con Modo de espera.</p>

<p>Un aviso: Starlink reajusta tarifas con frecuencia (en 2026, dos veces). <strong>Mira el precio en la contratación</strong> en la <a href="https://starlink.com/es/service-plans" target="_blank" rel="noopener">web oficial de planes</a>, no el de un artículo de hace seis meses.</p>

<h2>2. El equipo: desde junio de 2026 se alquila, no se compra</h2>

<p>Lo que más gente se salta: desde junio de 2026, las nuevas altas pagan además <strong>10 €/mes por el kit</strong> (antena y router):</p>

<ul>
<li><strong>Residencial 100: 45 €/mes reales</strong> (35 de tarifa + 10 de kit).</li>
<li><strong>Residencial 200: 55 €/mes reales</strong> (45 + 10).</li>
<li><strong>Residencial Max: 75 €/mes reales</strong> (65 + 10).</li>
<li>Los 10 € son 120 € al año, y el equipo <strong>no es tuyo</strong>: si te das de baja, se devuelve.</li>
</ul>

<p>Dos matices: a menudo aparece un «ajuste del alquiler» que deja esos 10 € en 0, así que cuenta el precio de la contratación, no el de la tabla; y la instalación profesional es opcional, <strong>desde unos 172 €</strong>, solo para tejados complicados (la app te dice dónde apuntar; la básica la monta cualquiera).</p>

<p>Si eliges una sola cosa, el <strong>Starlink Mini</strong>: cabe en una mochila, router integrado, alimentación de CC directa y pasa de 200 Mb/s. Es el que tiene sentido en un kit de emergencia; aquí puedes <a href="https://www.amazon.es/s?k=starlink+mini&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">ver accesorios y soportes para Starlink Mini ↗</a>.</p>

<h2>3. ¿Merece la pena en tu caso? Sí si…, no si…</h2>

<p><strong>Merece la pena cuando:</strong> no llega la fibra o llega a 20 Mb/s de verdad; el 5G fijo se cae por la noche; vives en un pueblo o una casa de montaña aislada; o es una segunda residencia de uso por semanas (con el Modo de espera a unos 10 €/mes en vez de pagar la tarifa completa todo el año).</p>

<p><strong>No merece la pena cuando:</strong> tienes fibra estable y barata; cuando necesitas internet <em>en cualquier punto</em> del país y no en una dirección (para eso sirven los datos móviles); o si no quieres cuota mensual, porque la parte grande del coste es la de cada mes.</p>

<p>Y el punto que casi nadie calcula antes: <strong>la energía</strong>. Una terminal consume <strong>60-75 W en activo y 20-40 W en reposo</strong>, así que sin luz hay que alimentarla: con una <a href="https://www.amazon.es/s?k=estacion+de+energia+portatil&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">estación de energía portátil ↗</a>, con un <a href="https://www.amazon.es/dp/B0D9JMS8H2?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">panel solar plegable</a> que recupera por el día o, si es instalación fija, con el <a href="https://www.amazon.es/dp/B07DPWBBDP?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">SAI del router</a>. Un <a href="https://www.amazon.es/dp/B0DFLHZQ18?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">powerbank de 20.000 mAh</a> se queda corto para la antena. Cuántos vatios de verdad: <a href="/blog/panel-solar-portatil-72h-emergencia/">panel solar portátil para 72 horas</a> y <a href="/blog/generador-vs-power-station-comparativa/">generador frente a power station</a>.</p>

<p>Hace falta además <strong>cielo despejado</strong>: un árbol o un tejado mal orientado estropean la conexión como un apagón. Si la antena no ve el cielo, Starlink no es tu solución: mira antes <a href="/blog/mejor-router-4g-emergencia-sin-internet/">el mejor router 4G de emergencia</a>.</p>

<h2>4. Alternativas más baratas antes de pagar 45 € al mes</h2>

<table>
<thead><tr><th>Opción</th><th>Cuándo gana</th><th>Coste típico</th></tr></thead>
<tbody>
<tr><td><a href="https://www.amazon.es/s?k=router+4g+5g+sim&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Router 4G/5G con SIM de datos ↗</a></td><td>Hay cobertura móvil en tu calle y no necesitas más de 100 GB</td><td>Equipo 0-100 € + 15-40 €/mes</td></tr>
<tr><td>eSIM / segunda SIM de datos</td><td>Para salir del pueblo o el segundo dispositivo de la familia</td><td>0-20 € + franja de datos</td></tr>
<tr><td>Starlink Residencial 100</td><td>No hay cobertura móvil fiable y necesitas ancho de banda real</td><td>35 €/mes (+ kit)</td></tr>
<tr><td>Mensajería satelital y GPS</td><td>Solo avisos y localización sin cobertura: poco tráfico, mucha autonomía</td><td>Equipo + cuota anual</td></tr>
<tr><td><a href="https://www.amazon.es/dp/B071NWGL29?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Walkie-talkies PMR446 ↗</a></td><td>Comunicación interna del grupo sin ninguna red disponible</td><td>40-80 € el par</td></tr>
</tbody>
</table>

<p>La comparativa completa: <a href="/blog/conectividad-emergencia-starlink-radios-redundancia/">conectividad de emergencia</a>, <a href="/blog/mejor-sim-datos-emergencia-cobertura/">mejor SIM de datos</a> y <a href="/blog/comunicar-sin-red-movil/">comunicar sin red móvil</a>. La regla: <strong>capas</strong> — móvil para el día a día, router o Starlink para la casa, satélite o radio cuando todo lo demás se cae.</p>

<h2>5. Los cinco errores que más se repiten al contratar</h2>

<ul>
<li><strong>Contratar el Max por costumbre.</strong> La prioridad solo se nota en horas punta; para una casa normal, el Residencial 200 rinde igual 30 €/mes más barato.</li>
<li><strong>Leer solo la tarifa.</strong> El precio real es tarifa + alquiler: 45, 55 o 75 € al mes. Mira siempre el total del primer recibo.</li>
<li><strong>Instalarlo sin comprobar el cielo.</strong> La app tiene un mapa de obstrucciones: úsalo ANTES de pagar y de taladrar el tejado.</li>
<li><strong>Dejar la prueba para el apagón.</strong> Tienes 30 días de devolución: pruébalo un día normal, con lluvia y con la tele puesta.</li>
<li><strong>Olvidar de dónde saldrá la energía.</strong> Sin enchufe, Starlink es un plato de metal: primero la <a href="https://www.amazon.es/dp/B0D9JMS8H2?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">fuente de energía</a> y la <a href="/blog/panel-solar-portatil-72h-emergencia/">batería que la sostiene</a>.</li>
</ul>

<h2>6. Por dónde empezar hoy</h2>

<p>Si la decisión es «sí, lo quiero», ve a la <a href="https://starlink.com/es/residential" target="_blank" rel="noopener">web oficial de contratación</a>, comprueba tu dirección en el <a href="https://starlink.com/es/map" target="_blank" rel="noopener">mapa de cobertura</a> y decide entre el 100 y el 200. La instalación paso a paso, en <a href="/blog/starlink-emergencia-72h-conectividad/">Starlink en un apagón</a>.</p>

<p>Para el plan completo, el <a href="/kit/kit-starlink/">kit de Starlink</a> recoge la selección, la <a href="/kit/kit-apagon/">lista de un apagón</a> cubre el resto de la casa y el método, en <a href="/blog/como-montar-tu-kit-72h/">cómo montar tu kit de 72 horas</a>. Pruébalo una tarde: el día que haga falta, importará que ya lo habías probado.</p>
"""

ENTRADA = {
    "slug": SLUG,
    "titulo": "Mejor Starlink en España: precio, planes y cuál elegir (2026)",
    "fecha": HOY,
    "lectura": "7 min",
    "resumen": "Starlink en España 2026: los tres planes residenciales con precio "
               "oficial, el alquiler del kit de 10 €/mes, Itinerante y cuál te conviene.",
    "autor": "Redacción Kit72h",
    "fuente": [
        {"nombre": "Starlink — Planes de servicio (precios oficiales para España)",
         "url": "https://starlink.com/es/service-plans"},
        {"nombre": "Starlink — Residencial (tarifas, Mini y prueba de 30 días)",
         "url": "https://starlink.com/es/residential"},
        {"nombre": "Starlink — Mapa de disponibilidad y velocidades",
         "url": "https://starlink.com/es/map"},
        {"nombre": "20minutos — Starlink cobra 10 €/mes por el alquiler del kit (junio 2026)",
         "url": "https://www.20minutos.es/tecnologia/fabricantes/starlink-sube-precios-espana-alquiler-antena-10-euros-mes_6982235_0.html"},
        {"nombre": "Banda Ancha — Starlink sube los precios en España y ya es la sexta operadora",
         "url": "https://bandaancha.eu/articulos/starlink-sube-precios-fuerza-espana-11775"},
        {"nombre": "Comisión Europea — Estrategia de la Unión de la Preparación (mínimo 72 horas de autonomía)",
         "url": "https://commission.europa.eu/topics/preparedness_es"},
        {"nombre": "Protección Civil — Recomendaciones generales por riesgo",
         "url": "https://www.proteccioncivil.es/gestion-riesgos/recomendaciones"},
    ],
    "cuerpo": CUERPO.strip(),
    "kits_relacionados": ["kit-starlink", "kit-apagon", "kit-basico-72h", "kit-electricidad"],
    "etiquetas": ["starlink", "internet satelital", "conectividad", "apagon",
                  "comparativa", "precios", "preparacion"]
}

# --- validaciones antes de escribir (mismas guardas que el publicador) -------
cuerpo = ENTRADA["cuerpo"]
palabras = len(re.sub(r"<[^>]+>", " ", cuerpo).split())
assert 700 <= palabras <= 1200, f"cuerpo con {palabras} palabras (fuera de 700-1200)"
assert "<p>" in cuerpo and "<h2>" in cuerpo, "cuerpo sin estructura"
assert len(ENTRADA["resumen"]) < 160, f"resumen con {len(ENTRADA['resumen'])} car."
assert "amazon.es" not in cuerpo or "tag=ntizar-21" in cuerpo, "Amazon sin tag"
for m in re.findall(r'href="(https://www\.amazon\.es/[^"]+)"', cuerpo):
    assert "tag=ntizar-21" in m, f"enlace sin tag: {m}"
internos = re.findall(r'href="(/(?:blog|kit)/[^"]+)"', cuerpo)
assert len(internos) >= 3, "menos de 3 enlaces internos"
for m in internos:
    ruta = RAIZ / (m.strip("/") + "/index.html")
    assert ruta.exists(), f"enlace interno roto: {m}"

blog = json.loads(RUTA.read_text(encoding="utf-8"))
previas = {e.get("slug"): e for e in blog["entradas"]}
t_norm = ENTRADA["titulo"].strip().lower()
for s, e in previas.items():
    if s != SLUG and (e.get("titulo") or "").strip().lower() == t_norm:
        raise SystemExit(f"canibalización: título duplicado con «{s}»")

fecha_previa = previas.get(SLUG, {}).get("fecha")  # un replace conserva la fecha
ENTRADA["fecha"] = fecha_previa or HOY
ENTRADA["lectura"] = "%d min" % max(3, round(palabras / 200))

nuevo = [e for e in blog["entradas"] if e.get("slug") != SLUG]
nuevo.append(ENTRADA)
nuevo.sort(key=lambda e: (e.get("fecha", ""), e.get("slug", "")), reverse=True)
blog["entradas"] = nuevo
blog["meta"]["total"] = len(nuevo)
blog["meta"]["ultima_revision"] = HOY
nota = blog["meta"].get("nota_editor", "")
prefijo = f"{HOY}: entrada '{SLUG}' (editor nocturno) — "
if prefijo not in nota:
    blog["meta"]["nota_editor"] = prefijo + (
        "comparativa Starlink España: 5 planes con precio oficial, alquiler del kit "
        "de 10 €/mes, alternativas y errores; 7 fuentes (Starlink oficial, 20minutos, "
        "Banda Ancha, Comisión Europea, Protección Civil). " + nota)

with open(RUTA, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(blog, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"OK: {len(blog['entradas'])} entradas, total={blog['meta']['total']}")
print(f"cuerpo={palabras} palabras | resumen={len(ENTRADA['resumen'])} car. | "
      f"internos={len(internos)}")
print("primera:", blog["entradas"][0]["slug"], blog["entradas"][0]["fecha"])
