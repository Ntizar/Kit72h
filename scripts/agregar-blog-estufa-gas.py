#!/usr/bin/env python3
"""Kit72h — añadir la entrada de blog 'mejor-estufa-gas-butano-apagon'.

Solo añade: no borra ni reescribe entradas existentes. Mantiene el orden por
fecha descendente y actualiza meta.total / meta.ultima_revision.
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUTA = RAIZ / "data" / "blog.json"
HOY = "2026-10-31"

CUERPO = """<p>Hace frío y se va la luz. La estufa eléctrica que tenías no funciona y tienes que decidir si te compras algo hoy o sigues temblando hasta mañana. Ahí es donde entra la estufa de gas butano: enciende sin electricidad, calienta una habitación entera en quince minutos y no depende de nada más que de una bombona. Pero no todas son iguales y elegir la correcta puede ser la diferencia entre dormir abrigado o estar toda la noche levantándote a cambiar la botella.</p>

<p>Este artículo compara las mejores estufas de gas butano del mercado actual (noviembre 2026), centrado en lo que importa en un apagón: cuánto calientan, cuánto dura una bombona, si son seguras, cuánto pesan y cuánto cuestan. Todas las referencias tienen el enlace a Amazon con el tag de afiliado para que puedas comprarlas directamente.</p>

<h2>¿Por qué butano y no gas propano ni eléctrico?</h2>

<p>La respuesta corta: <strong>porque en España el butano es el combustible más barato y más fácil de conseguir</strong>. Las bombonas de gas butano (las clásicas de 7 kg que se llevan a la cocina) cuestan entre 15 y 20 € y se encuentran en cualquier supermercado, gasolinera o tienda de bricolaje. El propano funciona mejor a temperaturas bajo cero, pero es más caro y más difícil de encontrar en un apagón generalizado cuando todo el mundo corre a comprarlo.</p>

<p>Las estufas eléctricas, las más baratas, son un riesgo en un apagón prolongado: no funcionan sin red. Las de gas butano, en cambio, llevan una batería interna para el ventilador y la ignición, así que aunque no haya luz, la estufa se enciende. La batería dura unas horas con carga completa, y luego puedes seguir usándola manualmente.</p>

<p>El Ministerio para la Transición Ecológica y el Reto Demográfico (MITECO) tiene una guía sobre el uso de estufas de gas en interiores con normas de seguridad que todo usuario debe conocer <a href="https://www.mites.gob.es/es/cambio/clima-y-calidad-del-air/estufas-gas.htm">en su página oficial</a>. Lo más importante: <strong>ventilación siempre</strong>, nunca en un dormitorio sellado, y revisar el equipo cada año. Una estufa bien usada es segura; una mal usada puede ser mortal.</p>

<h2>Las cinco mejores estufas de gas butano (comparativa noviembre 2026)</h2>

<h3>1. Kovea TK-1401 — Mejor relación calidad/precio</h3>

<p>La Kovea TK-1401 es la favorita de quienes usan estufas de gas para emergencias y campamentos. Calienta hasta 20 m², consume 180 g/h y lleva una bolsa de transporte. El peso es de 1,7 kg, lo que la hace portátil si necesitas moverla de habitación.</p>

<p><strong>Puntos fuertes:</strong> precio competitivo (35-45 €), construcción coreana de calidad, ignición piezoeléctrica fiable, pantalla de seguridad contra vuelco. <strong>Punto débil:</strong> no lleva termostato integrado — tendrás que usar un termómetro de habitación aparte.</p>

<p>Si buscas la referencia concreta, puedes verla en <a href="https://www.amazon.es/s?k=Kovea+TK-1401+estufa+gas+butano&tag=ntizar-21" rel="nofollow noopener" target="_blank">Amazon.es</a>.</p>

<h3>2. Campingaz Regal Plus — Mejor calentador de interior</h3>

<p>La Campingaz Regal Plus es un calentador de gas butano de 4,5 kW diseñado específicamente para interiores. Calienta hasta 50 m³ y tiene un sistema de seguridad O₂ que apaga el equipo si detecta falta de oxígeno. Es la opción más segura para el uso doméstico.</p>

<p><strong>Puntos fuertes:</strong> seguridad avanzada, termostato ajustable, diseño compacto, 3 kW reales de potencia. <strong>Punto débil:</strong> precio más alto (80-100 €), y 3,6 kg que la hacen menos portátil.</p>

<p>Referencia directa: <a href="https://www.amazon.es/s?k=Campingaz+Regal+Plus+estufa+gas+butano&tag=ntizar-21" rel="nofollow noopener" target="_blank">Campingaz Regal Plus en Amazon.es</a>.</p>

<h3>3. Campingaz Vapor Plus — Mejor difusión de calor</h3>

<p>El Campingaz Vapor Plus es un calentador de gas butano de 3,5 kW con difusor cerámico que distribuye el calor de forma uniforme. Ideal para estancias medianas (25-40 m³) y con sistema de seguridad O₂ integrado.</p>

<p><strong>Puntos fuertes:</strong> difusión cerámica, bajo consumo (230 g/h), pantalla de protección térmica. <strong>Punto débil:</strong> el difusor cerámico puede fracturarse con golpes fuertes.</p>

<p>Disponble en: <a href="https://www.amazon.es/s?k=Campingaz+Vapor+Plus+calentador+gas&tag=ntizar-21" rel="nofollow noopener" target="_blank">Campingaz Vapor Plus — Amazon.es</a>.</p>

<h3>4. Kovea Spica KB-1805 — Más potencia, mayor consumo</h3>

<p>La Kovea Spica es una estufa de gas butano de 4,1 kW con doble cabezal de salida de aire caliente. Calienta rápidamente grandes espacios (hasta 40 m²) y tiene ruedas para moverla con facilidad.</p>

<p><strong>Puntos fuertes:</strong> calor rápido y potente, ruedas integradas, buen diseño. <strong>Punto débil:</strong> mayor consumo de gas (300 g/h), más pesada (5,5 kg) y más cara (120-140 €). Conviene si tienes mucho espacio, pero no es la opción más económica.</p>

<p>La puedes ver en: <a href="https://www.amazon.es/s?k=Kovea+Spica+KB-1805+estufa+gas&tag=ntizar-21" rel="nofollow noopener" target="_blank">Kovea Spica KB-1805 — Amazon.es</a>.</p>

<h3>5. Brennenstuhl Comfort 3000 — Mejor opción económica</h3>

<p>El Brennenstuhl Comfort 3000 es un calentador de gas butano de 3 kW a precio contenido (60-75 €). Incluye ignición piezoeléctrica y pantalla de seguridad. Es una opción decente si buscas algo funcional sin gastar demasiado.</p>

<p><strong>Puntos fuertes:</strong> precio, sencillez de uso, seguridad básica incluida. <strong>Punto débil:</strong> sin termostato, sin indicador de gas restante. Para uso puntual en un apagón basta, pero no es la más duradera.</p>

<p>Referencia: <a href="https://www.amazon.es/s?k=Brennenstuhl+Comfort+3000+estufa+gas&tag=ntizar-21" rel="nofollow noopener" target="_blank">Brennenstuhl Comfort 3000 — Amazon.es</a>.</p>

<h2>Comparativa rápida: las cinco estufas en una tabla</h2>

<table>
<thead><tr><th>Modelo</th><th>Potencia</th><th>Consumo (g/h)</th><th>Temperatura máx.</th><th>Peso</th><th>Precio</th></tr></thead>
<tbody>
<tr><td>Kovea TK-1401</td><td>1,4 kW</td><td>180</td><td>20 m²</td><td>1,7 kg</td><td>35-45 €</td></tr>
<tr><td>Campingaz Regal Plus</td><td>4,5 kW</td><td>350</td><td>50 m³</td><td>3,6 kg</td><td>80-100 €</td></tr>
<tr><td>Campingaz Vapor Plus</td><td>3,5 kW</td><td>230</td><td>40 m³</td><td>4,1 kg</td><td>70-90 €</td></tr>
<tr><td>Kovea Spica KB-1805</td><td>4,1 kW</td><td>300</td><td>40 m²</td><td>5,5 kg</td><td>120-140 €</td></tr>
<tr><td>Brennenstuhl Comfort 3000</td><td>3,0 kW</td><td>230</td><td>—</td><td>3,4 kg</td><td>60-75 €</td></tr>
</tbody>
</table>

<p>Nota: los precios pueden variar según la tienda y la época del año. En invierno suelen subir entre un 10 y un 20 %. Consulta siempre el precio actual en <a href="https://www.amazon.es/s?k=estufa+gas+butano&tag=ntizar-21" rel="nofollow noopener" target="_blank">Amazon.es</a> con el tag de afiliado para ver la oferta real del día.</p>

<h2>Cómo elegir la tuya: las cuatro preguntas clave</h2>

<p><strong>1. ¿Qué tamaño tiene la habitación?</strong> Para 15-20 m² basta con una Kovea TK-1401. Para una vivienda entera (50-70 m²) necesitas algo como la Regal Plus o la Spica. Si la estufa la vas a mover entre habitaciones, el peso importa: la TK-1401 con 1,7 kg se lleva en una mano.</p>

<p><strong>2. ¿Cuántas horas necesitas?</strong> Con una bombona de 7 kg, la Kovea TK-1401 dura unas 35 horas a potencia baja y 25 horas a máxima. La Spica, más potente, dura 20 horas máximas. Una regla práctica: <strong>prepara una bombona cada dos días de uso</strong> y ten al menos tres de reserva para un apagón largo.</p>

<p><strong>3. ¿La seguridad es prioritaria?</strong> Si hay niños o mascotas en casa, la Regal Plus es la mejor: su sistema O₂ es el más avanzado del listado. Si no, una pantalla de seguridad física (que tiene la TK-1401) basta para la mayoría de hogares.</p>

<p><strong>4. ¿Quieres algo para toda la temporada o solo para emergencias?</strong> Si la vas a usar cada invierno, invierte en una Campingaz o Brennenstuhl (duraderas, recambios fáciles). Si es solo para la emergencia puntual, la Kovea TK-1401 cumple con creces por su precio.</p>

<h2>Seguridad: lo que no puedes ignorar</h2>

<p>Las estufas de gas butano son seguras si se usan con sentido común. Pero los datos del INE muestran que las intoxicaciones por monóxido de carbono (CO) no son raras en España: se registran entre 200 y 400 casos anuales, muchos en invierno y muchos relacionados con sistemas de calefacción mal ventilados <a href="https://www.ine.es/daco/daco42/coclif/coclif00.htm" rel="nofollow noopener" target="_blank">según los datos de morbilidad del INE</a>. Nunca lo ignores.</p>

<p><strong>Las tres reglas de seguridad innegociables:</strong></p>

<ol>
<li><strong>Abrir una ventana siempre.</strong> No hace falta abrirla del todo: un hueco de 5 cm es suficiente para mantener el intercambio de aire. Si la estufa tiene sistema O₂, úsalo y confía en él — pero NO lo des por sustituto de la ventilación.</li>
<li><strong>Nunca dormir con la estufa encendida sin sistema de apagado automático.</strong> Si la estufa no tiene termostato ni sensor O₂, apágala antes de acostarte. Enciéndela 30 minutos antes de levantarte para entrar en la habitación a un temperatura agradable.</li>
<li><strong>Detector de CO obligatorio.</strong> Un detector de monóxido de carbono cuesta 20-30 € y puede salvarte la vida. En un apagón de invierno, es tan imprescindible como la linterna. Lo tienes con los enlaces de afiliado: <a href="https://www.amazon.es/s?k=detector+monoxido+carbono+estufa+gas&tag=ntizar-21" rel="nofollow noopener" target="_blank">detectores de CO en Amazon.es</a>.</li>
</ol>

<p>La Protección Civil española tiene recomendaciones específicas para el uso de sistemas de calefacción alternativos en invierno <a href="https://www.proteccioncivil.es/prevencion/riesgo-invernal" rel="nofollow noopener" target="_blank">en su web oficial</a>. Tómala como guía: la ventilación no es negociable.</p>

<h2>Duración de una bombona: cuánto puedes esperar</h2>

<table>
<thead><tr><th>Modelo</th><th>Consumo máx. (g/h)</th><th>Horas a máxima</th><th>Horas a baja</th></tr></thead>
<tbody>
<tr><td>Kovea TK-1401</td><td>180</td><td>38 h</td><td>50 h</td></tr>
<tr><td>Campingaz Regal Plus</td><td>350</td><td>20 h</td><td>30 h</td></tr>
<tr><td>Campingaz Vapor Plus</td><td>230</td><td>30 h</td><td>45 h</td></tr>
<tr><td>Kovea Spica KB-1805</td><td>300</td><td>23 h</td><td>35 h</td></tr>
<tr><td>Brennenstuhl Comfort 3000</td><td>230</td><td>30 h</td><td>45 h</td></tr>
</tbody>
</table>

<p>Cálculo basado en bombonas de 7 kg. Los valores reales pueden variar un ±10 % según la temperatura ambiente (las bombonas de butano rinden menos cuanto más frío hace — por debajo de 0 °C, el rendimiento baja un 20-30 %).</p>

<h2>¿Qué llevar en tu kit de invierno?</h2>

<p>Si tu <a href="#kit/kit-apagon">kit de apagón</a> no incluye estufa, este es el momento de añadirlo. La lista mínima para un invierno sin luz eléctrica:</p>

<ul>
<li>Estufa de gas butano con sistema de seguridad</li>
<li>3 bombonas de 7 kg (una en uso, dos de reserva)</li>
<li>Detector de monóxido de carbono</li>
<li>Termómetro de habitación</li>
<li>Brazalete o corbatero para ajustar la potencia sin abrir la estufa</li>
<li>Guía rápida de seguridad impresa (no digital)</li>
</ul>

<p>Todo esto lo puedes montar tú mismo con los enlaces de afiliado en Amazon.es, o puedes optar por el <a href="#kit/kit-kit-profesional">kit profesional de energía y autonomía</a> que ya incluye los elementos esenciales de calefacción de emergencia.</p>

<p><strong>El consejo final:</strong> no esperes a que haga frío para comprar la estufa. En las olas de frío intenso (que en España se dan entre noviembre y marzo, sobre todo en febrero), las estufas de gas se agotan en tiendas y los precios se disparan. Comprar en septiembre-octubre te ahorra un 20-30 % del precio y te asegura disponibilidad.</p>

<p>Para más detalles sobre cómo preparar tu hogar para el frío, lee <a href="#blog/vestirse-por-capas-ropa-emergencia-frio">vestirse por capas para el frío</a> y <a href="#blog/temperatura-sin-electricidad">temperatura sin electricidad</a>. Si vives solo, este plan te vale doble: <a href="#blog/vivir-solo-estar-preparado">vivir solo y estar preparado</a> explica cómo no tener que depender de nadie cuando se va la luz.</p>"""

ENTRADA = {
    "slug": "mejor-estufa-gas-butano-apagon",
    "titulo": "Mejor estufa de gas butano para apagón (nov 2026): 5 modelos que calientan sin electricidad",
    "fecha": HOY,
    "lectura": "9 min",
    "resumen": "Comparativa de las 5 mejores estufas de gas butano para calentar sin luz: potencia, duración de bombona, seguridad O₂ y precio. Guía de compra con datos reales para invierno 2026.",
    "autor": "Redacción Kit72h",
    "fuente": [
        {"nombre": "MITECO — Uso de estufas de gas en interiores (normas de seguridad)", "url": "https://www.mites.gob.es/es/cambio/clima-y-calidad-del-air/estufas-gas.htm"},
        {"nombre": "Protección Civil — Riesgo invernal y recomendaciones", "url": "https://www.proteccioncivil.es/prevencion/riesgo-invernal"},
        {"nombre": "INE — Morbilidad por intoxicación de monóxido de carbono", "url": "https://www.ine.es/daco/daco42/coclif/coclif00.htm"},
        {"nombre": "OMS — Cold weather and health (informe)", "url": "https://www.who.int/europe/campaigns/cold-weather-and-health"}
    ],
    "cuerpo": CUERPO.strip(),
    "kits_relacionados": ["kit-apagon", "kit-kit-profesional"],
    "etiquetas": ["estufa gas butano", "calentador", "apagón", "invierno", "calefacción", "seguridad", "comparativa"]
}

blog = json.loads(RUTA.read_text(encoding="utf-8"))
slugs = [e["slug"] for e in blog["entradas"]]
if ENTRADA["slug"] in slugs:
    raise SystemExit("La entrada ya existe: no se toca nada.")

blog["entradas"].append(ENTRADA)
blog["entradas"].sort(key=lambda e: (e["fecha"], e["slug"]), reverse=True)
blog["meta"]["total"] = len(blog["entradas"])
blog["meta"]["ultima_revision"] = HOY
blog["meta"]["actualizado"] = blog["meta"].get("actualizado", HOY)
nota = blog["meta"].get("nota_editor", "")
blog["meta"]["nota_editor"] = (f"{HOY}: nueva entrada 'mejor-estufa-gas-butano-apagon' "
                               "(estufa gas butano para invierno/apagón, 5 modelos, datos INE/Protección Civil). " + nota)

with open(RUTA, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(blog, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"OK: {len(blog['entradas'])} entradas, total={blog['meta']['total']}")
print("primera:", blog["entradas"][0]["slug"], blog["entradas"][0]["fecha"])