#!/usr/bin/env python3
"""Kit72h — añadir/actualizar la entrada de blog 'nevada-en-casa-que-necesito'.

Re-ejecutable: si la entrada ya existe la REEMPLAZA (no falla), mantiene el
orden por fecha descendente y recalcula meta.total / meta.ultima_revision.
Fila del mapa de keywords: «nevada hogar qué necesito» (Cluster B, P3,
estacional — se publica 45-60 días antes del pico de nieve).
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUTA = RAIZ / "data" / "blog.json"
HOY = "2026-10-13"
SLUG = "nevada-en-casa-que-necesito"

CUERPO = """
<p>Cuando la AEMET pinta el mapa de avisos de naranja, el problema no es la nieve de postal: son los días que vienen detrás. Carreteras cortadas, la luz que no vuelve, la calefacción parada y el súper con las estanterías vacías. La borrasca <strong>Filomena</strong> (enero de 2021) sigue siendo la referencia en España: la propia <a href="https://www.aemet.es/es/conocermas/borrascas/2020-2021/estudios_e_impactos/filomena" target="_blank" rel="noopener">AEMET la describe como un episodio de carácter excepcional</a>, con nieve acumulada de hasta 50 cm en Madrid capital y temperaturas mínimas de -26,5 °C. En muchas casas lo que falló no fue que nevara: fue que nadie se había preparado para tres días sin comprar.</p>

<p>Esta es la lista de <strong>qué necesito en casa cuando avisan nevada</strong>, en orden y con el porqué. Si solo haces una cosa, haz la primera.</p>

<h2>1. Mira el aviso oficial, no el grupo de WhatsApp</h2>

<p>Todo empieza en el <a href="https://www.aemet.es/es/eltiempo/prediccion/avisos" target="_blank" rel="noopener">mapa de avisos de la AEMET</a>: amarillo (ten cuidado), naranja (riesgo importante) y rojo (riesgo extremo, con implicaciones para tu seguridad). Complementa con las <a href="https://www.proteccioncivil.es/gestion-riesgos/recomendaciones" target="_blank" rel="noopener">recomendaciones de Protección Civil</a> y con el 112 si hay una emergencia real.</p>

<p>Y antes de mover el coche, la DGT lo repite en cada aviso invernal: <strong>consulta la previsión meteorológica y el estado de vialidad de las carreteras</strong> antes de salir, y ten cadenas o neumáticos de invierno a mano. Trafico puede restringir la circulación a los vehículos que no lleven ese equipamiento y llegar a cortar carreteras de forma preventiva. La regla práctica: <strong>si el desplazamiento no es imprescindible, no se hace</strong>.</p>

<h2>2. Calefacción: lo que calienta y lo que mata</h2>

<p>Cuando se va la luz, lo que mata en invierno no es el frío sino el <strong>monóxido de carbono</strong>: inodoro, invisible y producido por cualquier combustión mal ventilada. Es la primera norma de la lista:</p>

<ul>
<li><strong>Un generador jamás dentro de casa</strong>, ni en el garaje, ni en el portal, ni pegado a una ventana. Por qué, en la <a href="/blog/generador-vs-power-station-comparativa/">comparativa de generador frente a power station</a>: en un piso, la power station es la única opción.</li>
<li><strong>Estufa de gas o de combustión: solo con la habitación ventilada</strong> y nunca mientras duermes. Una <a href="https://www.amazon.es/dp/B01M1NCHK8?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">estufa de gas butano</a> resuelve un salón, no una casa cerrada toda la noche.</li>
<li><strong>Detector de monóxido a pilas en cada planta y cerca de los dormitorios.</strong> Cuesta menos que una cena y es lo único que te avisa antes de que sea tarde: <a href="https://www.amazon.es/dp/B0D66LK5NP?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">detector de CO a pilas</a>.</li>
<li><strong>Abrigar la casa, no solo a la gente:</strong> tapar la ventana por la noche con una cortina o manta, cerrar las habitaciones que no se usen y vestir por capas en casa. El detalle está en <a href="/blog/temperatura-sin-electricidad/">mantener la temperatura corporal sin electricidad</a> y en <a href="/blog/vestirse-por-capas-ropa-emergencia-frio/">vestirse por capas</a>.</li>
</ul>

<p>Lo específico del frío está en el <a href="/kit/kit-frio/">kit de frío y nevadas</a>.</p>

<h2>3. Agua y comida: tres días sin poder comprar</h2>

<p>Una nevada corta carreteras y retrasa el reparto, así que se calcula <strong> como mínimo 3 litros de agua por persona y día</strong> (beber, higiene y cocinar): la cifra y el cómo guardarla están en <a href="/blog/agua-cuanta-y-como/">cuánta agua guardar por persona</a>. Compra comida que se pueda comer <strong>sin gas y sin cocinar</strong>: conservas, legumbres de bote, frutos secos, pan de molde, café y un <strong>abrelatas</strong> (si olvidas el manual, un cuchillo y una olla no bastan).</p>

<p>Y en cuanto se va la luz, el orden es: <strong>consume primero lo fresco</strong> (carne, pescado, lácteos), después lo congelado. La nevera aguanta horas, no días; el calendario completo está en <a href="/blog/conservar-comida-sin-nevera-ni-frio/">conservar comida sin nevera</a>, y si vives solo o quieres margen extra, en <a href="/blog/nevera-portatil-emergencia-72h/">nevera portátil para emergencias</a>.</p>

<h2>4. Luz, información y baterías</h2>

<p>Los sustos de una nevada son de madrugada, en un pasillo oscuro. Equipo que los resuelve, con precios orientativos:</p>

<table>
<thead><tr><th>Objeto</th><th>Para qué sirve de verdad</th><th>Precio orientativo</th></tr></thead>
<tbody>
<tr><td><a href="https://www.amazon.es/dp/B0FB3WSWJ1?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Linterna frontal con pilas</a></td><td>Manos libres para subir al desván, bajar al trastero o ayudar al vecino</td><td>8-15 €</td></tr>
<tr><td><a href="https://www.amazon.es/dp/B094D3JGLT?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Surtido de pilas AA/AAA</a></td><td>Linternas, radios y detectores; con fecha de caducidad anotada</td><td>10-20 €</td></tr>
<tr><td><a href="https://www.amazon.es/dp/B0GWN9FJC7?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Radio a pilas o de dinamo</a></td><td>Información oficial sin red ni batería: la radio es la primera fuente cuando cae la luz</td><td>15-35 €</td></tr>
<tr><td><a href="https://www.amazon.es/dp/B0DFLHZQ18?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Powerbank de 20.000 mAh</a></td><td>Tres o cuatro recargas de móvil: avisar y recibir avisos</td><td>25-50 €</td></tr>
<tr><td><a href="https://www.amazon.es/dp/B0D9JMS8H2?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Panel solar plegable</a></td><td>Alargar la batería varios días; con cielo cubierto produce poco, no lo cuentes como red principal</td><td>40-80 €</td></tr>
<tr><td><a href="https://www.amazon.es/dp/B0BJPVQXP6?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Velas con portavelas estable</a></td><td>Refuerzo puntual, siempre sobre superficie resistente y lejos de cortinas</td><td>5-12 €</td></tr>
</tbody>
</table>

<p>Las comparativas completas están en <a href="/blog/mejor-linterna-emergencia-72h/">mejor linterna de emergencia</a>, <a href="/blog/mejor-powerbank-emergencia-capacidad/">mejor powerbank</a> y <a href="/blog/mejor-radio-emergencia-manivela-solar/">mejor radio de manivela y solar</a>; cuántos vatios necesitas de verdad, en <a href="/blog/panel-solar-portatil-72h-emergencia/">panel solar portátil</a>.</p>

<h2>5. El coche: cadenas, neumáticos y sentido común</h2>

<p>La DGT lo repite cada invierno: llevar <strong>cadenas o neumáticos de invierno o de todo tiempo</strong> si vas a circular por zonas con aviso de nevada, consultar la vialidad antes de salir y dejar libre el carril izquierdo para los quitanieves. Si te cogió la nieve en la carretera: no abandones el vehículo, reduce la marcha y avisa al 112.</p>

<p>El material va en el maletero <strong>antes</strong> de que anuncien el temporal: <a href="https://www.amazon.es/dp/B0CSDX8LR8?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">cadenas para nieve</a>, un <a href="https://www.amazon.es/dp/B0CJDWWGNG?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">par de guantes impermeables</a> (montar cadenas con las manos heladas es imposible) y una manta térmica. La lista entera del vehículo está en el <a href="/kit/kit-coche/">kit de coche</a>.</p>

<h2>6. Vecinos, mayores y quien vive solo</h2>

<p>En un edificio la logística se resuelve entre todos: quién compra si alguien no puede salir y quién tiene llave del piso de la persona mayor. Una <strong>llamada a la misma hora cada día</strong> a quien vive solo no es cortesía, es control de estado: el guion está en <a href="/blog/vivir-solo-estar-preparado/">vivir solo y estar preparado</a>, los equipos en el <a href="/kit/kit-mayores/">kit de persona mayor</a> y los teléfonos que no pueden faltar en <a href="/blog/recursos-oficiales-emergencia/">recursos oficiales de emergencia</a>. Si hay medicación diaria, revisa la dosis de la semana y ten la receta al día: <a href="/blog/medicion-cronica-personas-dependientes/">medicación crónica sin farmacia</a>.</p>

<h2>7. Los cinco errores que se repiten en cada nevada</h2>

<ul>
<li><strong>Salir «a mirar»</strong> con la nieve cayendo. La carretera que «está bien» a las diez puede estar cortada a las doce.</li>
<li><strong>Encender el generador o la estufa en un espacio cerrado.</strong> Es el error que más hospitalizaciones causa en invierno.</li>
<li><strong>Comprar solo comida que hay que cocinar</strong> y descubrir a las 21:00 que no hay gas, agua ni abrelatas.</li>
<li><strong>Dejar los teléfonos y los papeles solo en el móvil.</strong> Sin luz y con la batería al 8 %, la lista de contactos no existe: imprimirla. La carpeta completa está en <a href="/blog/carpeta-de-emergencia-documentos/">carpeta de emergencia y documentos</a>.</li>
<li><strong>Esperar a que avise el vecino.</strong> Cuando el supermercado desborda, ya es tarde para comprar lo importante: pilas, pilas de repuesto, botiquín y medicación.</li>
</ul>

<h2>8. Por dónde empezar hoy</h2>

<p>Si vienes de cero, el <a href="/kit/kit-basico-72h/">kit básico de 72 horas</a> da la base común y encima va el equipo de frío y coche. El método para no dejarte nada está en <a href="/blog/como-montar-tu-kit-72h/">cómo montar tu kit de 72 horas</a> y las decisiones del primer momento, en <a href="/blog/apagon-lecciones-28a/">qué nos enseñó un apagón</a>.</p>

<p>La nevada avisa con días de antelación: úsalos, y cuando llegue solo tendrás que mirar por la ventana.</p>
"""

ENTRADA = {
    "slug": SLUG,
    "titulo": "Nevada en casa: 8 claves para aguantar los días sin luz (2026)",
    "fecha": HOY,
    "lectura": "7 min",
    "resumen": "Qué necesitas cuando avisan nevada: calefacción segura, agua, comida, "
               "luz, coche con cadenas y los errores que enseñó Filomena, con fuentes oficiales.",
    "autor": "Redacción Kit72h",
    "fuente": [
        {"nombre": "AEMET — Borrasca Filomena (episodio de carácter excepcional, nieve y mínimas)",
         "url": "https://www.aemet.es/es/conocermas/borrascas/2020-2021/estudios_e_impactos/filomena"},
        {"nombre": "AEMET — Mapa de avisos meteorológicos",
         "url": "https://www.aemet.es/es/eltiempo/prediccion/avisos"},
        {"nombre": "Protección Civil — Recomendaciones generales por riesgo",
         "url": "https://www.proteccioncivil.es/gestion-riesgos/recomendaciones"},
        {"nombre": "DGT — Hielo y nieve: conducción invernal",
         "url": "https://www.dgt.es/muevete-con-seguridad/conviertete-en-un-buen-conductor/conduccion-invernal/circular-con-hielo/index.html"},
        {"nombre": "Comisión Europea — Estrategia de la Unión de la Preparación (mínimo 72 horas de autonomía)",
         "url": "https://commission.europa.eu/topics/preparedness_es"},
    ],
    "cuerpo": CUERPO.strip(),
    "kits_relacionados": ["kit-frio", "kit-coche", "kit-basico-72h", "kit-mayores"],
    "etiquetas": ["nevada", "nieve", "invierno", "frío", "coche",
                  "preparacion", "escenarios"]
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
prefijo = f"{HOY}: entrada '{SLUG}' (editor nocturno) — nevada en casa: qué necesito; "
if prefijo not in nota:
    blog["meta"]["nota_editor"] = prefijo + (
        "5 fuentes oficiales (AEMET Filomena y avisos, Protección Civil, DGT conducción "
        "invernal, Comisión Europea 72 h). " + nota)

with open(RUTA, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(blog, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"OK: {len(blog['entradas'])} entradas, total={blog['meta']['total']}")
print(f"cuerpo={palabras} palabras | resumen={len(ENTRADA['resumen'])} car. | "
      f"internos={len(internos)}")
print("primera:", blog["entradas"][0]["slug"], blog["entradas"][0]["fecha"])
