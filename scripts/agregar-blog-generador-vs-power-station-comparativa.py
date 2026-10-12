#!/usr/bin/env python3
"""Kit72h — añadir/actualizar la entrada de blog
'generador-vs-power-station-comparativa'.

Re-ejecutable: si la entrada ya existe la REEMPLAZA (no falla), mantiene el
orden por fecha descendente y recalcula meta.total / meta.ultima_revision.
Fila del mapa de keywords: «comparativa generador vs power station» (Cluster C).
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUTA = RAIZ / "data" / "blog.json"
HOY = "2026-10-12"
SLUG = "generador-vs-power-station-comparativa"

CUERPO = """
<p>El 28 de abril de 2025, a las 12:33:30, el sistema eléctrico peninsular se quedó a cero. El <strong>Comité para el análisis de las circunstancias que concurrieron en la crisis de electricidad del 28 de abril</strong> —creado por el Consejo de Seguridad Nacional y cuyo informe aprobó el Consejo de Ministros el 17 de junio de 2025— concluyó que el origen fue multifactorial, descartó el ciberataque y situó la reposición completa del suministro el 29 de abril a las 14:36. En muchas casas la luz volvió mucho antes; el problema fue todo lo que se quedó sin alimentar mientras tanto: la nevera, la caldera, el portero, la bomba de agua.</p>

<p>Por eso la pregunta de compra ya no es «qué me falta en el kit», sino <strong>cuánta potencia necesitas y, sobre todo, dónde la vas a poner</strong>. Ahí se cruzan dos respuestas muy distintas: un <strong>generador de combustible</strong> o una <strong>power station</strong> (batería estacionaria con inversor y, opcionalmente, panel solar). Los comparamos con datos de España —potencia, autonomía, coste por hora, ruido y normativa— para que decidas antes del próximo corte, no durante.</p>

<h2>Qué necesitas alimentar (haz esto antes de mirar precios)</h2>

<p>La potencia se mide en vatios y se gasta muy deprisa. Regla práctica orientativa para las primeras 72 horas:</p>

<ul>
<li><strong>100-200 W</strong>: router y ONT, cargadores de móvil, tres o cuatro luces LED, detector de monóxido. Cualquier cosa de este artículo lo mueve.</li>
<li><strong>300-700 W</strong>: portátil, televisión, hervidor, microondas a ratos, aspiradora.</li>
<li><strong>1.000-2.000 W</strong>: nevera doméstica en el arranque, caldera de gasóleo (solo la bomba de circulación), bomba de pozo.</li>
<li><strong>Por encima de 2.500 W</strong>: vitrocerámica, horno, lavadora, aire acondicionado. Ahí un generador pequeño se queda corto y una power station de 500 Wh no llega ni a un ciclo de horno.</li>
</ul>

<p>Con esa lista delante, la comparativa se aclara sola.</p>

<h2>Generador vs power station: la tabla</h2>

<table>
<thead><tr><th>Criterio</th><th>Generador de gasolina (inverter)</th><th>Power station + panel solar</th></tr></thead>
<tbody>
<tr><td><strong>Potencia continua</strong></td><td>1.000-3.000 W, con picos de hasta el doble al arrancar</td><td>600-2.000 W de salida y 500-2.000 Wh de capacidad</td></tr>
<tr><td><strong>Autonomía</strong></td><td>4-8 h por depósito de 4-5 L, y mientras quede gasolina</td><td>500 Wh ≈ 6-10 h de nevera pequeña o unas 10 h de router, luces y cargadores</td></tr>
<tr><td><strong>Coste por hora</strong></td><td>1-1,80 €/h de gasolina (orientativo)</td><td>0 € en uso; 150-400 € de gasto único en el panel</td></tr>
<tr><td><strong>Ruido</strong></td><td>58-75 dB(A) a 7 m según modelo</td><td><strong>Silencioso</strong>: solo el ventilador</td></tr>
<tr><td><strong>Uso en piso</strong></td><td><strong>Imposible</strong> ❌ (monóxido, ruido y normativa)</td><td><strong>Sí</strong> ✅ dentro de la vivienda</td></tr>
<tr><td><strong>Recarga</strong></td><td>Gasolina, con stock que caduca</td><td>Sol, red o motor del coche: gratis y sin gestión</td></tr>
<tr><td><strong>Peso</strong></td><td>15-30 kg</td><td>8-25 kg</td></tr>
<tr><td><strong>Precio orientativo</strong></td><td>350-900 € + 50-100 € de depósito</td><td>400-1.200 € + 100-300 € de panel</td></tr>
</tbody>
</table>

<p>Cifras orientativas para España, hechas para comparar, no para firmar un pedido: se parte de una gasolina en torno a 1,5 €/L y de horquillas habituales de tienda. Un generador convencional sin inverter es más barato, pero entrega una onda que estropea electrónica sensible: si vas a enchufar el ordenador o el router, exige <strong>salida sinusoidal pura</strong>.</p>

<h2>Ganador por categoría</h2>

<ul>
<li><strong>Piso o apartamento en ciudad</strong> → <strong>power station</strong>. No quema combustible, no hace ruido y no emite monóxido. Con una estación de 1.000-1.500 Wh y un panel plegable se cubren nevera pequeña, luces y móviles: <a href="https://www.amazon.es/s?k=power+station+portatil+1000w&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">ver power stations portátiles</a> y <a href="https://www.amazon.es/dp/B0D9JMS8H2?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">panel solar plegable de 20-40 W</a>, el mínimo para no bajar la carga de móviles y linternas.</li>
<li><strong>Casa con trastero, garaje ventilado o jardín</strong> → <strong>generador inverter</strong>. Es la única vía para hervir, calentar o mover una nevera grande durante días: <a href="https://www.amazon.es/s?k=generador+inverter+silencioso&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">ver generadores inverter</a>.</li>
<li><strong>Router y ordenador (lo primero que se salva)</strong> → <strong>SAI/UPS</strong>. Barato, silencioso e instantáneo: <a href="https://www.amazon.es/dp/B07DPWBBDP?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">SAI de 600-900 VA</a>. No sustituye a los dos anteriores: compra los primeros minutos mientras decides.</li>
<li><strong>Escenario largo (varios días)</strong> → <strong>los dos</strong>: estación para el día a día y generador para los grandes consumos, con el panel como red de seguridad.</li>
</ul>

<h2>El ruido: por qué un generador no entra en un portal</h2>

<p>Aquí la comparativa se gana por puntos, y es el dato que casi nadie se guarda antes de comprar. Un generador inverter «silenciado» ronda los <strong>58-65 dB(A) a siete metros</strong> según ficha técnica; un convencional pasa de 70. Un portero automático de portal está en torno a los 50-55 dB. En una calle en calma a las tres de la mañana, un generador en el balcón se oye desde el piso de al lado.</p>

<p>Y el marco legal no da margen: el <strong>artículo 7.2 de la Ley de Propiedad Horizontal</strong> prohibe desarrollar en la vivienda actividades que «contravengan las disposiciones generales sobre actividades molestas, insalubres, nocivas, peligrosas o ilícitas», mientras que los valores límite de ruido en zona residencial los fija la <a href="https://www.boe.es/biblioteca_juridica/codigos/codigo.php?id=184" target="_blank" rel="noopener">Ley 37/2003 del Ruido y sus reales decretos de desarrollo (Código del Ruido, BOE)</a> junto con la ordenanza municipal de cada ayuntamiento. Traducción práctica: enchufar un generador en el balcón o en el garaje de un edificio de vecinos es, a la vez, un conflicto de convivencia y una infracción. Si quieres el detalle normativo, está en el <a href="https://www.boe.es/biblioteca_juridica/codigos/abrir_pdf.php?fich=416_Codigo_de_Comunidad_de_Propietarios.pdf" target="_blank" rel="noopener">Código de la Comunidad de Propietarios del BOE</a>.</p>

<h2>El monóxido: el argumento que cierra la discusión</h2>

<p>La regla es corta y no admite excepciones: <strong>un generador nunca se usa dentro de casa, ni en el garaje, ni en el portal, ni pegado a una ventana</strong>. El motor emite monóxido de carbono inodoro, y las intoxicaciones graves en apagones suelen ocurrir exactamente así, con alguien intentando pasar la noche más caliente o cargar el móvil en el trastero. <a href="https://www.proteccioncivil.es/gestion-riesgos/recomendaciones" target="_blank" rel="noopener">Protección Civil</a> y el <a href="https://commission.europa.eu/topics/preparedness_es" target="_blank" rel="noopener">plan de preparación de la Comisión Europea</a> coinciden en lo mismo: distancia, ventilación y un <a href="https://www.amazon.es/dp/B0D66LK5NP?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">detector de monóxido a pilas</a> en la pared, a un metro de la cama y lejos del techo.</p>

<p>Si la casa es de piso, esa línea ni se plantea: el generador queda fuera de la ecuación y la power station gana por incomparecencia.</p>

<h2>Compras en 10 minutos</h2>

<ul>
<li><strong>Primero lo pequeño:</strong> <a href="/kit/kit-basico-72h/">kit básico de 72 horas</a> y <a href="/blog/mejor-powerbank-emergencia-capacidad/">powerbank de 20.000 mAh</a>. Cuestan menos que una hora de generador y resuelven el 80 % de las noches.</li>
<li><strong>Si vives en piso:</strong> power station de 1.000 Wh más panel plegable. El cálculo de vatios está en <a href="/blog/panel-solar-portatil-72h-emergencia/">panel solar portátil: cuántos vatios necesitas de verdad</a>.</li>
<li><strong>Si tienes trastero o jardín:</strong> generador inverter de 2.000 W con salida sinusoidal pura, y <a href="/blog/generador-solar-emergencia-72h/">la alternativa de generador solar</a> para no vivir de gasolina.</li>
<li><strong>Lo que no se compra dos veces:</strong> antes de enchufar calefacción, revisa <a href="/blog/mejor-estufa-sin-luz-apagon/">la comparativa de estufas sin luz</a>; la nevera y el resto de la lista están en <a href="/kit/kit-apagon/">kit apagón</a> y en <a href="/kit/kit-electricidad/">kit de electricidad</a>.</li>
</ul>

<p>Con el 28-A encima de la mesa —las conclusiones oficiales están en el <a href="https://www.lamoncloa.gob.es/consejodeministros/resumenes/Documents/2025/Informe-no-confidencial-Comite-de-analisis-28A.pdf" target="_blank" rel="noopener">informe no confidencial del Comité de análisis</a>— la pregunta ya no es si habrá otro corte, sino si esa tarde tendrás la nevera funcionando o llamarás al vecino. Elegir entre generador y power station no es elegir tecnología: es elegir si tu casa tiene dónde guardar veinte kilos de hierro ruidoso… o no.</p>
"""

ENTRADA = {
    "slug": SLUG,
    "titulo": "Generador vs power station: comparativa 2026 para el apagón",
    "fecha": HOY,
    "lectura": "7 min",
    "resumen": "¿Generador o power station? Comparamos potencia, autonomía, ruido, "
               "coste por hora y normativa para aguantar un apagón en España.",
    "autor": "Redacción Kit72h",
    "fuente": [
        {"nombre": "La Moncloa / Consejo de Ministros — Informe no confidencial del Comité de análisis de la crisis eléctrica del 28 de abril de 2025",
         "url": "https://www.lamoncloa.gob.es/consejodeministros/resumenes/Documents/2025/Informe-no-confidencial-Comite-de-analisis-28A.pdf"},
        {"nombre": "MITECO — Se presenta el informe del Comité de análisis de la crisis eléctrica del 28 de abril",
         "url": "https://www.miteco.gob.es/es/prensa/ultimas-noticias/2025/junio/se-presenta-el-informe-del-comite-de-analisis-de-la-crisis-elect.html"},
        {"nombre": "BOE — Código del Ruido (Ley 37/2003 del Ruido y desarrollo reglamentario)",
         "url": "https://www.boe.es/biblioteca_juridica/codigos/codigo.php?id=184"},
        {"nombre": "BOE — Código de la Comunidad de Propietarios (Ley 49/1960 de Propiedad Horizontal, art. 7.2)",
         "url": "https://www.boe.es/biblioteca_juridica/codigos/abrir_pdf.php?fich=416_Codigo_de_Comunidad_de_Propietarios.pdf"},
        {"nombre": "Protección Civil — Recomendaciones generales por riesgo",
         "url": "https://www.proteccioncivil.es/gestion-riesgos/recomendaciones"},
        {"nombre": "Comisión Europea — Estrategia de la Unión de la Preparación (mínimo 72 horas de autonomía)",
         "url": "https://commission.europa.eu/topics/preparedness_es"}
    ],
    "cuerpo": CUERPO.strip(),
    "kits_relacionados": ["kit-apagon", "kit-basico-72h", "kit-electricidad"],
    "etiquetas": ["apagón", "energía", "generador", "power station",
                  "comparativas", "preparacion", "escenarios"]
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
for m in re.findall(r'href="(/(?:blog|kit)/[^"]+)"', cuerpo):
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
prefijo = f"{HOY}: entrada '{SLUG}' (editor nocturno) — comparativa generador vs power station; "
if prefijo not in nota:
    blog["meta"]["nota_editor"] = prefijo + (
        "6 fuentes oficiales (Comité 28-A/La Moncloa, MITECO, BOE Código del Ruido y LPH, "
        "Protección Civil, Comisión Europea). " + nota)

with open(RUTA, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(blog, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"OK: {len(blog['entradas'])} entradas, total={blog['meta']['total']}")
print(f"cuerpo={palabras} palabras | resumen={len(ENTRADA['resumen'])} car.")
print("primera:", blog["entradas"][0]["slug"], blog["entradas"][0]["fecha"])
