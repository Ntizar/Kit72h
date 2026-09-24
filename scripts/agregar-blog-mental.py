#!/usr/bin/env python3
"""Kit72h — añadir la entrada de blog 'salud-mental-y-sueno-en-una-emergencia'.

Solo añade: no borra ni reescribe entradas existentes. Mantiene el orden por
fecha descendente y actualiza meta.total / meta.ultima_revision.
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUTA = RAIZ / "data" / "blog.json"
HOY = "2026-09-24"

CUERPO = """
<p>Son las 21:40 y se va la luz. En veinte minutos ya tienes resuelta la nevera: sabes qué tirar y qué no. Lo que nadie te ha enseñado a resolver es lo otro. El niño que pregunta si la luz volverá antes de dormir, tu madre que a las dos de la mañana te llama asustada porque no ve nada, o tu propio cerebro que a las tres sigue repasando la lista de cosas que aún pueden ir mal. Las emergencias no se ganan solo con linternas y garrafas de agua: se ganan durmiendo, comiendo y con la cabeza en su sitio. Esta es la parte del kit que no se guarda en una caja.</p>

<p>Y no es un tema blando ni secundario. El estrés sostenido te quita el hambre y el sueño, y cuando llevas dos noches casi sin dormir tomas peores decisiones: dejas la puerta abierta, conduce de noche para «llegar antes», no ves el charco que cruza la carretera. La OMS lo tiene estudiado desde hace años en sus guías de emergencias y la conclusión es muy práctica: lo que ayuda en las primeras 72 horas no es un discurso, son cuatro cosas concretas —seguridad, información, contacto humano y descanso— y todas se pueden preparar hoy.</p>

<h2>1. Lo que los manuales oficiales dicen: mirar, escuchar, conectar</h2>

<p>La guía de referencia en español es <strong>«Primera ayuda psicológica: guía para trabajadores de campo»</strong>, de la OMS con War Trauma Foundation y World Vision International. Está pensada para gente que ayuda a otra en un desastre, pero el marco es tan sencillo que sirve igual para una vecina, para tu padre o para ti mismo. Se resume en tres acciones.</p>

<ul>
<li><strong>Mirar:</strong> comprobar que estás en un lugar seguro, quién necesita ayuda primero y qué falta de lo básico: agua, abrigo, sitio seco, información real. Antes de hablar de sentimientos, se resuelve la sed, el frío y el ruido.</li>
<li><strong>Escuchar:</strong> acercarte, presentarte, preguntar qué necesita en ese momento y <em>no forzar el relato</em>. La propia guía recuerda una conclusión del grupo de trabajo mhGAP de la OMS: a una persona muy angustiada hay que ofrecerle primera ayuda psicológica, y no obligarla a repasar lo ocurrido. Dejar hablar al que quiere hablar, sí; interrogar al que no quiere, no.</li>
<li><strong>Conectar:</strong> ayudar a llegar a la familia, a los servicios que funcionan y a la información práctica. Un dato bueno dicho a tiempo (cuándo vuelve la luz, dónde hay agua potable, qué carretera está cortada) calma más que cualquier frase bonita.</li>
</ul>

<p><strong>Lo que puedes hacer en los próximos 10 minutos:</strong> bebe un vaso de agua y come algo aunque no tengas hambre. Siéntate y haz dos minutos de respiración lenta (cuatro segundos al inspirar, seis al espirar). Usa la técnica del 5-4-3-2-1 —nombra en voz baja cinco cosas que ves, cuatro que oyes, tres que tocas, dos que hueles, una que saboreas— cuando notes que la cabeza se te va en bucle. Y ordena una sola habitación para convertirla en vuestra «sala de mando»: una mesa con la radio o el móvil cargado, la linterna, el agua, el papel y el bolígrafo. El orden visible se traduce en calma.</p>

<p><strong>Lo que parece buena idea y no lo es:</strong> usar el alcohol para dormir (te deja la primera parte de la noche dormido y la segunda despierto y más ansioso), tener la televisión o la radio con noticias en bucle a todas horas (alimenta la sensación de catástrofe y no da un solo dato útil), tomar prestado un somnífero de un vecino (si usas algo para dormir, que sea con tu médico o tu farmacéutico de por medio) y decir «ya dormiremos cuando esto pase», porque la deuda de sueño también se paga en las decisiones del día siguiente.</p>

<h2>2. Dormir cuando no hay luz, ni silencio, ni calma</h2>

<p>La segunda o tercera noche de una emergencia es el momento más crítico: has agotado la adrenalina del primer día y llegas destrozado, pero la cabeza no baja. Cuatro medidas resuelven buena parte del problema, y ninguna cuesta dinero si ya tienes el kit montado.</p>

<ul>
<li><strong>Horarios fijos.</strong> Acuéstate y levántate a la misma hora, aunque estés sin trabajar y duermas a ratos. El reloj interno no entiende de apagones: entiende de rutina.</li>
<li><strong>La cama, solo para dormir.</strong> Si a los 20-30 minutos no te has dormido, sal de la cama y haz algo tranquilo con luz tenue —leer, escribir, ordenar— hasta que vuelva el sueño. Es la recomendación clásica de las guías de sueño y contra el insomnio de rebote funciona mejor que dar vueltas.</li>
<li><strong>Menos cafeína por la tarde y nada de excitantes de madrugada.</strong> El café, el té y las bebidas de cola se notan durante horas; si estás de guardia, racionarlos.</li>
<li><strong>Tapa pantallas y usa reloj a pilas.</strong> El móvil te informa y te roba el sueño: fija dos momentos al día para consultar noticias —por la mañana y a última hora de la tarde— y deja el teléfono cargando en otra habitación por la noche. Un reloj despertador a pilas de 8-12 euros evita mirar la hora a las 3:40 de la madrugada.</li>
</ul>

<p>Para el ambiente, tres cosas de sentido común que casi nadie prepara: <strong>oscuridad</strong> (un antifaz, o una cortina improvisada, porque una farola o un LED puede dejarte la cara iluminada toda la noche), <strong>silencio</strong> (tapones de espuma; si el ruido es de fuera, una emisora hablando bajito o un sonido constante de radio tapa mejor que la nada) y <strong>frescura o abrigo</strong> según la época —si el problema es el frío o el calor, tienes las reglas completas en <a href="#blog/temperatura-sin-electricidad">cómo mantener la temperatura corporal sin electricidad</a>. Y una regla de oro: <strong>nunca duermas en el suelo desnudo</strong>; esterilla, cartón y manta por capas, como se explica en <a href="#blog/vestirse-por-capas-ropa-emergencia-frio">vestirse por capas</a>.</p>

<p>Si en casa hay que vigilar algo —un enfermo, el nivel del agua, el vecino del bajo— no dejes que lo haga siempre el mismo. Divide la noche en bloques y escríbelo en papel, no de memoria:</p>

<table>
<thead><tr><th>Bloque</th><th>Quién vela</th><th>Quién duerme</th></tr></thead>
<tbody>
<tr><td>22:00 - 01:00</td><td>Persona A</td><td>Persona B</td></tr>
<tr><td>01:00 - 04:00</td><td>Persona B</td><td>Persona A</td></tr>
<tr><td>04:00 - 07:00</td><td>Persona A</td><td>Persona B (o siesta de 30 min)</td></tr>
</tbody>
</table>

<p>El turno del que vela es corto a propósito: tres horas se sostienen, seis no. Y una última herramienta que funciona casi siempre: <strong>la libreta al lado de la cama</strong>. Antes de acostarte, escribe las tres o cuatro preocupaciones que te van a despertar y lo que puedes hacer con cada una mañana. Sacarlas del bucle mental y dejarlas en papel es la forma más barata de que el cerebro acepte soltarlas.</p>

<h2>3. Niños: la rutina calma más que cualquier explicación</h2>

<p>Un niño no necesita saber la verdad completa de un desastre: necesita saber <strong>qué va a pasar en su día</strong>. La presencia de un adulto que no grita y la rutina —agua, dientes, cuento, luz— hacen más que cualquier conversación. Tres reglas para esta noche:</p>

<ul>
<li><strong>Dile la verdad, pero corta y con plan.</strong> «No hay luz porque hay una avería muy grande. Estamos en casa, hay agua y comida, y papá y mamá están aquí. Mañana lo veremos con la linterna». Nada de detalles que impresionen y nada de promesas que no puedas cumplir («mañana vuelve la luz seguro» es una promesa; «mañana te lo digo en cuanto lo sepan» no lo es).</li>
<li><strong>Dale un trabajo.</strong> Lo que más baja el miedo infantil es tener una función: llevar la linterna, apuntar las horas, revisar las garrafas de agua, repartir las mantas. Es su manera de sentir que controla algo.</li>
<li><strong>Duerme a su lado si lo pide.</strong> Esta no es la noche para enseñar a dormir solo. El objeto de apego (manta, peluche, chupete, cuento) sale del armario y entra en la mochila de evacuación desde ya.</li>
</ul>

<p>Además: nada de noticias en bucle delante de ellos, y luz tenue en el pasillo toda la noche para que no se despierten en una oscuridad total que no reconocen. Si tras varios días el niño no come, no duerme o se muestra muy irritable, háblalo con tu pediatra. Tienes el detalle por edades en <a href="#blog/bebes-ninos-emergencia-checklist-edades">bebés y niños en una emergencia</a> y los materiales en el <a href="#kit/kit-bebe">kit bebé y lactancia</a>.</p>

<h2>4. Personas mayores, enfermos crónicos y quien vive solo</h2>

<p>Aquí la preparación va antes del desastre, no durante. La oscuridad desorienta a la persona mayor más rápido que el hambre: pierde la referencia del pasillo, se levanta de noche y se cae. Soluciones concretas:</p>

<ul>
<li><strong>Luces baliza en pasillo y baño.</strong> Cuatro pilas LED que se encienden solas cuestan menos de 15 euros y evitan la caída más habitual del apagón. Todo lo que necesita el <a href="#kit/kit-mayores">kit de persona mayor</a> está detallado en su ficha.</li>
<li><strong>Toalla en el borde de la cama y camino libre.</strong> Nada de sillas ni cajas entre la cama y la puerta: de noche y sin luz, se convierte en un obstáculo.</li>
<li><strong>Una llamada a la misma hora, todos los días.</strong> No es una charla: es un control de estado. Y siempre con una persona sustituta designada, porque quien llama también se pone enfermo. Es la base de lo que conté en <a href="#blog/vivir-solo-estar-preparado">vivir solo y estar preparado</a>.</li>
<li><strong>Avisar con presencia, no por WhatsApp.</strong> Si hay pérdida de audición, un mensaje no sirve: hay que tocar la puerta, y hacerlo hablando alto y de frente. Lo mismo vale para las alertas de móvil, que conviene tener explicadas antes.</li>
</ul>

<p>Con medicación crónica, la orden del día es mantener el horario y no improvisar dosis: pastillero y lista escrita, con los días marcados. Si hay insulinas o medicamentos que necesitan frío, revisa <a href="#blog/medicion-cronica-personas-dependientes">cómo asegurar 2-4 semanas sin farmacia</a> y consulta siempre con tu médico o farmacéutico para cualquier decisión sobre dosis o conservación. Y si la persona tiene deterioro cognitivo, no le discutas la realidad: redirige —agua, manta, mano, canción, foto—.</p>

<h2>5. El que sostiene también se cae</h2>

<p>En cada casa hay alguien que hace de centralita: llama, organiza, no duerme y a los tres días revienta. Si eres esa persona, esto es para ti.</p>

<ul>
<li><strong>Nadie vela dos noches seguidas.</strong> Escríbelo en la puerta de la nevera con las letras grandes, que es lo primero que se salta todo el mundo.</li>
<li><strong>Come y bebe aunque no tengas hambre.</strong> Cinco minutos de comida salada y un vaso de agua cada tres horas rinden más que un café corriendo.</li>
<li><strong>Nombra un sustituto en voz alta.</strong> «Si yo no puedo, llamas a Marta y ella sabe dónde está todo». Sobre todo, deja por escrito los teléfonos importantes en papel: la lista completa está en <a href="#blog/recursos-oficiales-emergencia">los recursos oficiales que deberías tener guardados</a>.</li>
<li><strong>Sal cinco minutos al día.</strong> Aire, calle, caminar. La OMS lo tiene documentado: la actividad física reduce los síntomas de ansiedad y depresión y mejora el sueño, y eso vale doble cuando todo está patas arriba.</li>
</ul>

<p>Y ponle límite honesto a tu papel: no tienes que arreglar a nadie. Acompañar, resolver lo práctico y pasar el relevo ya es todo lo que se puede hacer en un primer día. Si tú o alguien de tu casa lleváis varios días sin dormir ni comer, si la tristeza se instala o aparecen ideas de no seguir viviendo, eso no se gestiona con fuerza de voluntad: llama al <strong>024</strong>, la línea de atención a la conducta suicida del Ministerio de Sanidad, gratuita y disponible las 24 horas, o al <strong>112</strong> si la urgencia es inmediata. En cualquier duda clínica, consúltalo con tu médico o tu farmacéutico.</p>

<h2>6. Tu kit de descanso y cabeza: diez objetos y un plan de siete días</h2>

<p>Ninguno de estos objetos es caro y todos se usan en casa cualquier noche mala, no solo en un desastre. Mete lo pequeño en una bolsa de tela dentro del <a href="#kit/kit-basico-72h">kit básico de 72 horas</a> y deja lo grande en el dormitorio.</p>

<table>
<thead><tr><th>Objeto</th><th>Para qué sirve de verdad</th><th>Precio orientativo</th></tr></thead>
<tbody>
<tr><td>Tapones de espuma (5 pares)</td><td>Dormir con una emisora, un generador o una calle en alerta</td><td>3-6 €</td></tr>
<tr><td>Antifaz de tela</td><td>Oscuridad real cuando hay farolas, velas o un LED encendido</td><td>5-8 €</td></tr>
<tr><td>Frontal con modo rojo</td><td>Moverte de noche sin despertar a nadie y sin romperte el sueño</td><td>10-15 €</td></tr>
<tr><td>Reloj despertador a pilas</td><td>Saber la hora sin encender el móvil a las 4 de la mañana</td><td>8-12 €</td></tr>
<tr><td>Radio a pilas o de manivela</td><td>Información oficial sin red ni batería, y sonido constante para dormir</td><td>15-25 €</td></tr>
<tr><td>Libreta pequeña y bolígrafo</td><td>Vaciar el bucle de preocupaciones antes de acostarte y apuntar teléfonos</td><td>2-4 €</td></tr>
<tr><td>Baraja de cartas o libro de bolsillo</td><td>Dos horas de actividad tranquila sin pantallas, con niños incluidos</td><td>5-10 €</td></tr>
<tr><td>Manta ligera extra</td><td>Dormir abrigado sin sudar: capas, no una manta pesada</td><td>10-15 €</td></tr>
<tr><td>Botella de agua de 1,5 litros</td><td>Tener agua al lado evita levantarse en la oscuridad y beber menos</td><td>1 €</td></tr>
<tr><td>Bolsa de aseo mínima y toallitas</td><td>Lavarse la cara y los dientes devuelve la sensación de normalidad</td><td>4-6 €</td></tr>
</tbody>
</table>

<p>Y este es el <strong>plan de siete días</strong> para tener todo esto resuelto antes de que haga falta, a quince minutos por día:</p>

<ul>
<li><strong>Día 1.</strong> Escribe en una hoja los teléfonos clave (112, 024, médico, colegio, dos vecinos, dos familiares) y el punto de encuentro familiar. Una copia en papel en la cartera y otra pegada dentro del armario de la entrada.</li>
<li><strong>Día 2.</strong> Monta la mesa de mando: radio, linterna, cargador, agua, papel, bolígrafo. Una sola mesa, siempre la misma.</li>
<li><strong>Día 3.</strong> Compra tapones, antifaz y reloj a pilas. Van al cajón de la mesilla, no al trastero.</li>
<li><strong>Día 4.</strong> Prepara la «cena sin luz»: latas, frutos secos, fruta y agua accesibles, y una bandeja con lo necesario (abrelatas, cuchara, servilletas) para no abrir armarios a oscuras.</li>
<li><strong>Día 5.</strong> Prueba una noche de dos horas sin luz eléctrica en casa: linternas, velas bien seguras, sin pantallas. Descubrirás lo que falta antes de necesitarlo.</li>
<li><strong>Día 6.</strong> Explica el plan a los niños y dáles una tarea concreta (linterna, lista de agua). Diez minutos bastan.</li>
<li><strong>Día 7.</strong> Llama a la persona de tu familia que vive sola y acordad la hora de la llamada diaria. Y dile a un vecino a quién avisar si no te ve.</li>
</ul>

<p>Con esto tienes cubierto lo que ninguna linterna arregla: dormir, comer, no perder la cabeza y saber a quién llamar. Si quieres repartir el trabajo por escenarios, empieza por <a href="#blog/como-montar-tu-kit-72h">montar tu kit de 72 horas</a> y por las primeras decisiones de <a href="#blog/apagon-lecciones-28a">un apagón</a>; y si esta noche ya estás en mitad del lío, lo urgente está en <a href="#kit/kit-hogar">kit hogar o confinamiento</a>.</p>
"""

ENTRADA = {
    "slug": "salud-mental-y-sueno-en-una-emergencia",
    "titulo": "Salud mental y sueño en una emergencia: cómo sostener la cabeza (y a los tuyos) cuando todo se desordena",
    "fecha": "2026-09-24",
    "lectura": "13 min",
    "resumen": "Dormir, comer y calmarse no son la parte blanda del plan: son las decisiones que se toman cuando llevas dos noches sin dormir. Gu\u00eda pr\u00e1ctica con el marco de primera ayuda psicol\u00f3gica de la OMS, turnos de noche, higiene del sue\u00f1o, c\u00f3mo hablar con ni\u00f1os y mayores, y un kit de descanso de diez objetos.",
    "autor": "David Antizar",
    "fuente": [
        {"nombre": "OMS / OPS \u2014 Primera ayuda psicol\u00f3gica: gu\u00eda para trabajadores de campo (mirar, escuchar, conectar)", "url": "https://www.paho.org/es/node/44399"},
        {"nombre": "OMS \u2014 Salud mental (nota descriptiva)", "url": "https://www.who.int/es/news-room/fact-sheets/detail/mental-health-strengthening-our-response"},
        {"nombre": "OMS \u2014 Actividad f\u00edsica (nota descriptiva: reduce los s\u00edntomas de ansiedad y depresi\u00f3n)", "url": "https://www.who.int/es/news-room/fact-sheets/detail/physical-activity"},
        {"nombre": "Ministerio de Sanidad \u2014 024, l\u00ednea de atenci\u00f3n a la conducta suicida", "url": "https://www.sanidad.gob.es/linea024/home.htm"},
        {"nombre": "Comisi\u00f3n Europea \u2014 Estrategia de la Uni\u00f3n de la Preparaci\u00f3n (m\u00ednimo 72 horas de autonom\u00eda)", "url": "https://commission.europa.eu/topics/preparedness_es"},
        {"nombre": "Protecci\u00f3n Civil \u2014 Recomendaciones generales por riesgo", "url": "https://www.proteccioncivil.es/gestion-riesgos/recomendaciones"},
        {"nombre": "Protecci\u00f3n Civil \u2014 Red de Alerta Nacional y alertas a m\u00f3viles (ES-Alert)", "url": "https://www.proteccioncivil.es/coordinacion/redes/ran/public-warning-system"}
    ],
    "cuerpo": CUERPO.strip(),
    "kits_relacionados": ["kit-hogar", "kit-basico-72h", "kit-mayores", "kit-bebe"],
    "etiquetas": ["salud mental", "sue\u00f1o", "descanso", "familia", "ni\u00f1os", "mayores", "preparacion", "escenarios"]
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
blog["meta"]["nota_editor"] = (f"{HOY}: nueva entrada 'salud-mental-y-sueno-en-una-emergencia' (editor nocturno) "
                               "\u2014 dormir, estr\u00e9s y primera ayuda psicol\u00f3gica; 7 fuentes oficiales verificadas "
                               "(OMS/OPS, Sanidad 024, Comisi\u00f3n Europea, Protecci\u00f3n Civil). " + nota)

with open(RUTA, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(blog, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"OK: {len(blog['entradas'])} entradas, total={blog['meta']['total']}")
print("primera:", blog["entradas"][0]["slug"], blog["entradas"][0]["fecha"])
