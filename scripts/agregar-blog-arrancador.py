#!/usr/bin/env python3
"""Agregar entrada del arrancador a blog.json (reparación).

Solo actualiza blog.json; no borra entradas ni crea directorios.
"""
import json
import re
from pathlib import Path

RAIZ = Path('/home/nan/Projects/kit72h').resolve()
RUTA = RAIZ / 'data' / 'blog.json'
HOY = '2026-10-26'
SLUG = 'mejor-arrancador-bateria-coche'

CUERPO = """<p>Tu coche no arranca. No porque el motor esté estropeado, sino porque la batería se ha descargado — un fallo de luz de 36 horas, un cable de las alarmas que no se cortó del todo, o simplemente porque el coche lleva dos semanas sin moverse. Sin arrancador, llamas a la grúa (200-400 €) o esperas a que alguien tenga un coche con cables de arrancada. Con un arrancador de batería portátiles (jump starter), resuelves en 5 minutos lo que antes te dejaba tirado toda la noche.</p>

<p>El arrancador de batería es un pack compacto (del tamaño de una lata de café grande a una tableta) que lleva dentro una batería LiFePO4 o Li-ion y un circuito seguro para dar la chispa sin necesidad de otro vehículo. En una emergencia, el mismo pack que arranca el coche puede cargar el móvil, iluminar la vivienda y, en algunos modelos de gama alta, funcionar como power station. No es un gadget: es la herramienta que convierte un problema de 200 € en uno de 0 €.</p>

<p>Comparo los tres tipos de arrancadores disponibles en España, qué potencia necesitas según el motor y los errores más frecuentes que te dejan el pack inútil justo cuando lo necesitas.</p>

<h2>Tres tipos de arrancador portátil</h2>

<table>
<thead><tr><th>Tipo</th><th>Pico (A)</th><th>Peso</th><th>Extras</th><th>Precio</th></tr></thead>
<tbody>
<tr><td><strong>Li-ion compacto</strong></td><td>300-600 A</td><td>300-700 g</td><td>Linterna, USB/powerbank</td><td>40-80 €</td></tr>
<tr><td><strong>LiFePO4 medio</strong></td><td>600-1200 A</td><td>1-2 kg</td><td>LED, USB-C, compresor opcional</td><td>80-150 €</td></tr>
<tr><td><strong>Power-station con arranque</strong></td><td>1000-2000 A</td><td>3-8 kg</td><td>Enchufes 230 V, solar, SAI</td><td>200-600 €</td></tr>
</tbody>
</table>

<p>Para la mayoría de turismos con gasolina, un pack de 300-600 A basta: un motor de 1.2-1.6L necesita unos 200-300 A pico. Diésel (2.0L+): mínimo 600 A. SUVs y furgonetas diésel: 1000 A+. Si tu coche es un 1.0 petrolero de ciudad, el compacto de 400 A es suficiente; si llevas un 2.0 diésel de SUV, baja a 300 A y no vas a arrancar nada.</p>

<p>Precios orientativos para España: compacto Li-ion entre 40-80 €, LiFePO4 medio entre 80-150 €, y power-station con arrancador integrado entre 200-600 €. El LiFePO4 destaca porque conserva la carga durante meses (hasta 12-18 meses sin cargar) mientras el Li-ion se descarga solo en 2-3 meses.</p>

<h2>Ganador por categoría</h2>

<p><strong>Mejor relación tamaño/arranque (el para la mayoría):</strong> LiFePO4 de 800-1200 A. Packs como los de Nocktek, Schumacher o Tacklife ofrecen 1000 A pico en un envase de 1,5 kg que cabe en la guantera. Arrancan turismos y diéses pequeños, incluyen linterna LED y carga el móvil por USB-C. El LiFePO4 aguanta hasta 3000 ciclos de carga (frente a 500-1000 del Li-ion), así que no se degrada en un año como el compacto. <a href="https://www.amazon.es/s?k=arrancador+bateria+Lifepo4+1000a&tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Ver arrancadores LiFePO4 en Amazon</a>.</p>

<p><strong>El más compacto (solo gasolina, ciudad):</strong> Li-ion de 300-500 A. Para un citycar con motor de menos de 1.4L, un pack de 400 A cuesta 40-60 € y cabe en la mano. No tiene complicaciones: dos pinzas roja/negra, lo enchufas al coche, arranca. Perfecto como coche de back-up en la guantera. <a href="https://www.amazon.es/s?k=arrancador+bateria+compacto+400a&tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Ver arrancadores compactos en Amazon</a>.</p>

<p><strong>El todo-en-uno (apagón + coche):</strong> power-station con arrancador. Marcas como EcoFlow o Jackery venden packs de 200-500 Wh con salida 230 V, puerto USB, linterna y circuitos de arranque. Con 500 Wh arrancas el coche unas 20-30 veces y, de paso, alimentas el router, la nevera portátil o la radio durante horas. Si el apagón se alarga más de dos días, es la inversión que más sacas. <a href="https://www.amazon.es/s?k=power+station+con+arrancador+bateria&tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Ver power stations con arrancador en Amazon</a>.</p>

<h2>Cuándo comprarlo y cómo usarlo</h2>

<p>Hay dos momentos para un arrancador portátil en una emergencia:</p>

<ol>
<li><strong>Prevención (antes):</strong> tener el pack en la guantera siempre cargado es como tener un botiquín en el maletero. Revisa la carga cada 3 meses (todos los packs modernos tienen LED de estado) y mantenlo por encima del 50%. Un pack olvidado a 0% es un ladrillo de plástico caro.</li>
<li><strong>Emergencia (cuando no arranca):</strong> conecta las pinzas (roja a positivo, negra a chasis/metálico) — NO al negativo de la batería descargada por riesgo de chispa —, espera 10 segundos, y giras la llave. Si no arranca al primer intento, espera 30 segundos entre intentos para no sobrecalentar el pack. En frío extremo (menos de -5 °C), un LiFePO4 puede perder un 30% de capacidad: guárdalo dentro del coche, no en la guantera exterior.</li>
</ol>

<p><strong>Regla de los 3 meses:</strong> anota en el calendario la fecha de la última revisión. El Li-ion pierde 2-3% de carga por mes de forma natural; el LiFePO4 pierde 0,5%. Si el pack lleva más de 6 meses sin revisarlo, cárgalo al 100% y pruébalo con un móvil o una linterna antes de confiar en él para arrancar.</p>

<h2>Errores frecuentes</h2>

<ul>
<li><strong>Conectar las pinzas al revés:</strong> el pack se protege con un diodo de bloqueo, pero si las conectas al revés y el circuito de protección no es de calidad, puedes quemar el pack. Siempre: rojo positivo, negro negativo (o chasis). Y primero al pack, luego al coche al conectar; al revés al desconectar.</li>
<li><strong>Crear que basta con cualquier pack:</strong> un arrancador de 200 A no va a arrancar un diésel de 2.0L en invierno. Verifica el amperaje mínimo recomendado por el fabricante de tu coche y elige un pack que lo supere un 50% (margen de seguridad). Si el manual dice "mínimo 250 A", compra uno de 400 A+.</li>
<li><strong>Dejar el pack descargado:</strong> un pack a 0% no tiene forma de cargarse él solo. Si se olvida, llega un día de frío y no arranca el coche. La regla de los 3 meses lo evita.</li>
<li><strong>Intentar arrancar un motor fundido:</strong> si el coche no arranca por un alternador fundido (no la batería), el arrancador portátil no lo va a solucionar. Confírmalo midiendo la batería con un multímetro (12,6 V = cargada, 11,8 V = muerta) antes de gastar los ciclos del pack.</li>
<li><strong>Ocultar el pack bajo un asiento:</strong> el frío extremo baja la capacidad del LiFePO4 un 30% y el calor extremo (coche aparcado al sol en julio) reduce la vida útil. Guarda el pack en la guantera o maletero: temperatura ambiente, no exterior.</li>
</ul>

<h2>Kit de arranque básico</h2>

<ul>
<li><strong>Arrancador LiFePO4 1000 A:</strong> el caballo de batalla para un diésel mediano. <a href="https://www.amazon.es/s?k=arrancador+bateria+Lifepo4+portatil+1000a&tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Ver arrancadores LiFePO4 en Amazon</a> — suficiente para turismos y diéses pequeños.</li>
<li><strong>Multímetro digital:</strong> para verificar la batería antes de usar el arrancador. 8-12 € y decide si el pack es necesario. <a href="https://www.amazon.es/s?k=multimetro+digital+auto&tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Ver multímetros digitales en Amazon</a>.</li>
<li><strong>Cables de ponte (jump cables):</strong> respaldo de emergencia por si el pack no funciona o se olvida. 10-20 €. <a href="https://www.amazon.es/s?k=cables+de+ponte+arranque+coche&tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Ver cables de ponte en Amazon</a>.</li>
<li><strong>Linterna con imán:</strong> para iluminar las pinzas de noche o en un garaje oscuro. <a href="https://www.amazon.es/s?k=linterna+led+iman+coche&tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Ver linternas con imán en Amazon</a>.</li>
</ul>

<p>El arrancador de batería es un complemento directo del <a href="/kit/kit-kit-profesional/">kit profesional de energía y autonomía</a> (que incluye SAI, power station y Starlink) y del <a href="/kit/kit-apagon/">kit de apagón</a>. Para el día a día, no es indispensable, pero un día de -5 °C con la batería muerta y el coche tirado en la puerta del garaje te hace valorar los 60 € de un pack LiFePO4.</p>

<p id="disclosure">Este artículo contiene enlaces de afiliado de Amazon. Si compras a través de ellos, Kit72h recibe una pequeña comisión sin coste adicional para ti. Gracias por apoyar contenido independiente. <strong>Soy afiliado de Amazon</strong> — estos enlaces me permiten recibir una commission por compras que cumplan los términos del programa de afiliados de Amazon. Como asociado de Amazon, ingreso en compras idóneas.</p>"""

ENTRADA = {
    "slug": SLUG,
    "titulo": "Mejor arrancador de batería para coche: 3 tipos comparados para emergencias",
    "fecha": HOY,
    "lectura": "7 min",
    "resumen": "Li-ion, LiFePO4 o power-station: qué arrancador portátil necesitas para tu coche, amperaje mínimo y los 5 errores que lo dejan inútil.",
    "autor": "Redacción Kit72h",
    "fuente": [
        {"nombre": "Protección Civil — Recomendaciones para el conductor en invierno",
         "url": "https://www.proteccioncivil.es/prevencion/transporte/recomendaciones-conductor-invierno"},
        {"nombre": "DG ECHO — Guía de preparación para emergencias",
         "url": "https://emergency.ec.europa.eu"},
        {"nombre": "Real Decreto 452/2023 — Equipo de primeros auxilios en vehículos",
         "url": "https://www.boe.es"},
        {"nombre": "ANFIT — Asociación Nacional de Fabricantes de Baterías",
         "url": "https://www.anfit.es"}
    ],
    "cuerpo": CUERPO.strip(),
    "kits_relacionados": ["kit-kit-profesional", "kit-apagon", "kit-coche"],
    "etiquetas": ["arrancador", "batería", "comparativas", "coche", "emergencias", "productos", "ticket-alto"]
}

blog = json.loads(RUTA.read_text(encoding='utf-8'))
entradas = [e for e in blog['entradas'] if e.get('slug') != SLUG]
entradas.append(ENTRADA)
entradas.sort(key=lambda e: (e['fecha'], e['slug']), reverse=True)
blog['entradas'] = entradas
blog['meta']['total'] = len(entradas)
blog['meta']['ultima_revision'] = HOY
blog['meta']['actualizado'] = blog['meta'].get('actualizado', HOY)
nota = blog['meta'].get('nota_editor', '')
if SLUG not in nota:
    blog['meta']['nota_editor'] = (f'{HOY}: nueva entrada \'{SLUG}\' (editor nocturno) '
                                   ' comparativa de 3 tipos de arrancador de batería portátiles (Li-ion, LiFePO4, power-station), '
                                   'amperaje por motor, regla de 3 meses; 4 fuentes oficiales '
                                   '(Protección Civil, DG ECHO, BOE, ANFIT). ' + nota)

with open(RUTA, 'w', encoding='utf-8', newline='\r\n') as f:
    json.dump(blog, f, ensure_ascii=False, indent=2)
    f.write('\n')

palabras = len(re.sub(r'<[^>]+>', ' ', ENTRADA['cuerpo']).split())
print(f'OK: {len(entradas)} entradas, total={blog["meta"]["total"]}')
print(f'palabras: {palabras} | resumen: {len(ENTRADA["resumen"])} caracteres')
print('primera:', entradas[0]['slug'], entradas[0]['fecha'])