#!/usr/bin/env python3
"""Kit72h — añadir/actualizar la entrada de blog 'mejor-detector-monoxido-carbono'.

Re-ejecutable: si la entrada ya existe la REEMPLAZA (no falla), mantiene el
orden por fecha descendente y recalcula meta.total / meta.ultima_revision.

Sustituye a agregar-blog-mental.py, cuya entrada (salud-mental-y-sueno-en-una-
emergencia) ya estaba publicada → «La entrada ya existe». Fila nueva del mapa
de keywords: «mejor detector de monóxido de carbono» (Cluster C, comparativa de
compra — conversión): el CO ya se recomienda en kit-apagon y kit-hogar pero
ninguna página lo compara.
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUTA = RAIZ / "data" / "blog.json"
HOY = "2026-10-16"
SLUG = "mejor-detector-monoxido-carbono"

CUERPO = """
<p>Baja el frío, enciendes la estufa, cierras la habitación para que el calor no se escape y te quedas dormido. Ese escenario —casero, cotidiano, de cualquier invierno en España— es el que más veces termina en urgencias: el monóxido de carbono es incoloro, inodoro e insípido, no te avisa y el cuerpo tampoco. El <strong>detector de CO</strong> es el aparato más barato de toda la casa que decide si te despiertas a tiempo. Cuesta menos que una cena y no necesita instalación, ni electricidad, ni app.</p>

<p>Los números están en los informes oficiales: según el <strong>Programa de Tóxico-vigilancia</strong> del Ministerio de Sanidad, el monóxido es el tóxico más frecuente en los servicios de urgencias de España, con <strong>entre 5.000 y 10.000 intoxicaciones al año y una media de 125 muertes anuales</strong>. Y el <strong>Plan Nacional de actuaciones preventivas por bajas temperaturas 2025-2026</strong> recuerda cada invierno que el frío trae calefacciones, braseros y grupos electrógenos: el riesgo sube justo cuando más te encierras dentro.</p>

<h2>1. Qué exige la norma: la tabla que decide si avisa a tiempo</h2>

<p>En España se vende de todo, desde detectores de 15 € hasta aparatos de 80 €, y el diferencial no es la marca: es si cumplen la norma europea <strong>UNE-EN 50291-1:2018</strong> (ratificada por AENOR en febrero de 2021), que fija los métodos de ensayo y los requisitos de funcionamiento de los detectores de CO domésticos. Un aparato conforme debe alarmar con estos plazos:</p>

<table>
<thead><tr><th>Concentración de CO</th><th>Cuándo debe sonar la alarma</th></tr></thead>
<tbody>
<tr><td>30 ppm</td><td>No antes de 120 minutos (y sí dentro de ese plazo)</td></tr>
<tr><td>50 ppm</td><td>Entre 60 y 90 minutos</td></tr>
<tr><td>100 ppm</td><td>Entre 10 y 40 minutos</td></tr>
<tr><td>300 ppm</td><td>En menos de 3 minutos</td></tr>
</tbody>
</table>

<p>Dos lecturas. Primera: la norma no vigila niveles bajos de fondo, sino que <strong>avisa antes de que el daño sea grande</strong> — por eso no salta con la chimenea abierta una tarde, pero sí si el generador lleva media hora en el garaje. Segunda: una vez que salta, <strong>la alarma no se calma hasta bajar de 50 ppm</strong>: que «se apague solo» no significa que el aire esté limpio. Para la colocación vale la <strong>EN 50292</strong> (selección e instalación): cada estancia con posible fuente de combustión y cada dormitorio. La parte eléctrica del mismo riesgo está en <a href="/blog/seguridad-pasiva-hogar-incendios-electricos/">seguridad pasiva contra incendios e incendios eléctricos</a>.</p>

<h2>2. Los seis tipos, comparados</h2>

<p>Precios orientativos en Amazon España para detectores con sensor electroquímico conforme a EN 50291. Cada enlace abre la búsqueda del tipo: ves el precio del día, no el de cuando se escribió esto.</p>

<table>
<thead><tr><th>Tipo</th><th>Cuándo compensa</th><th>Precio orientativo</th></tr></thead>
<tbody>
<tr><td><a href="https://www.amazon.es/s?k=detector+de+monoxido+de+carbono+pilas&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Básico a pilas con alarma acústica ↗</a></td><td>Primera compra, vivienda alquilada, dormitorio</td><td>20-30 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=detector+co+con+pantalla&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Con pantalla de concentración (ppm) ↗</a></td><td>Casa con estufa, leña, chimenea o butano</td><td>30-45 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=detector+monoxido+carbono+bateria+10+anos&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Batería sellada de 10 años ↗</a></td><td>Dormitorio y pasillo: se coloca y se olvida</td><td>30-50 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=detector+humo+y+monoxido+carbono&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Combinado humo + CO ↗</a></td><td>Un solo aparato para los dos riesgos del apagón</td><td>40-70 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=detector+monoxido+carbono+alarma+sonora+fuerte&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Con aviso al móvil o interconectado ↗</a></td><td>Casa grande, varios pisos, ausencias</td><td>50-90 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=detector+monoxido+carbono+caravana+autocaravana&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Para autocaravana, caravana o velero ↗</a></td><td>Uso en movimiento, pilas y rango de temperatura amplio</td><td>30-60 €</td></tr>
</tbody>
</table>

<h2>3. Ganadores por categoría</h2>

<ul>
<li><strong>Mejor relación calidad-precio:</strong> el básico a pilas con sensor electroquímico. Si solo compras uno, es este: <a href="https://www.amazon.es/s?k=detector+de+monoxido+de+carbono+pilas&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">ver detectores de CO a pilas ↗</a>.</li>
<li><strong>Mejor para el dormitorio:</strong> batería sellada de 10 años, sin cambios de pila y con piloto de fin de vida: <a href="https://www.amazon.es/s?k=detector+monoxido+carbono+bateria+10+anos&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">ver modelos con batería de larga duración ↗</a>.</li>
<li><strong>Mejor con estufa o leña:</strong> con pantalla de ppm, para ver si la concentración sube antes de que suene: <a href="https://www.amazon.es/s?k=detector+co+con+pantalla&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">ver detectores con pantalla ↗</a>.</li>
<li><strong>Mejor casa con apagón previsto:</strong> combinado humo + CO: en un apagón conviven velas, estufas y generador, y el humo y el CO llegan juntos: <a href="https://www.amazon.es/s?k=detector+humo+y+monoxido+carbono&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">ver detectores combinados ↗</a>. Cuidado con la confusión de siempre: <strong>un detector de humo no detecta monóxido ni al revés</strong>.</li>
<li><strong>Mejor autocaravana o furgón:</strong> modelo específico para vehículos, con alimentación a pilas: <a href="https://www.amazon.es/s?k=detector+monoxido+carbono+caravana+autocaravana&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">ver detectores para caravana ↗</a>.</li>
</ul>

<p>Si el presupuesto es muy justo, la prioridad no es el detector: es <strong>ventilar y no calentar con combustión dentro de casa</strong>. Con eso y una linterna bien elegida ya vas cubierto — la selección está en <a href="/blog/mejor-estufa-sin-luz-apagon/">mejor estufa sin luz</a> y en <a href="/blog/temperatura-sin-electricidad/">mantener la temperatura sin electricidad</a>.</p>

<h2>4. Dónde ponerlo (y dónde nunca)</h2>

<ul>
<li><strong>Sí:</strong> en cada dormitorio, en el pasillo que los da y en la estancia donde quemes algo (cocina abierta, chimenea, taller). Sigue el fabricante: casi todos marcan 1-3 metros de la fuente, a techo o pared alta y lejos de corrientes de aire.</li>
<li><strong>No:</strong> dentro de un armario, detrás de una cortina, encima de la campana extractora ni junto a la ventana: ahí el aire llega tarde o se renueva demasiado rápido y mide mal.</li>
<li><strong>Garaje:</strong> el detector doméstico no sirve para el coche encendido: ahí hacen falta modelos de mayor rango y, mejor aún, no dejar el motor en marcha en un espacio cerrado.</li>
<li><strong>Mantenimiento:</strong> prueba mensual con el botón, quita el polvo cada seis meses (lo recomienda la <a href="https://www.comunidad.madrid/seguridad-emergencias-asem-112/instala-detectores-humo-tu-hogar" target="_blank" rel="noopener">Comunidad de Madrid</a>) y sustitúyelo al final de su vida útil, de 5 a 10 años según modelo: el propio aparato avisa.</li>
</ul>

<h2>5. Cinco errores que anulan el detector</h2>

<ul>
<li><strong>Confiar en el olfato.</strong> El CO no huele nada: cuando lo notas es que ya llevas rato respirándolo.</li>
<li><strong>Calentar con el horno de gas.</strong> Sanidad lo dice literal: nunca se usa la cocina ni el horno para calentar una casa.</li>
<li><strong>Generador, motosierra o caldera dentro de casa o en el garaje.</strong> Los motores de combustión en un espacio cerrado son la fuente clásica de intoxicación colectiva.</li>
<li><strong>Estufa encendida de noche con la habitación cerrada.</strong> Ventilar es la medida más barata: mejor perder algo de calor que no tener aire.</li>
<li><strong>Un detector para toda la casa.</strong> El aire no viaja entre plantas ni entre puertas cerradas: uno por planta como mínimo y uno en cada dormitorio.</li>
</ul>

<h2>6. Si suena la alarma: cuatro pasos</h2>

<ol>
<li><strong>Sal de la estancia con todos</strong> — sin «mirar de qué es», sin apagar nada y sin volver a entrar a buscar a nadie.</li>
<li><strong>Airea desde fuera</strong> y no se vuelve hasta que los servicios de emergencias lo autoricen.</li>
<li><strong>Llama al 112 desde el exterior</strong>: personas afectadas, síntomas y qué fuente de combustión estaba en marcha.</li>
<li><strong>Revisa la fuente con un profesional</strong> antes de volver a encenderla: una caldera o chimenea mal sellada repetirá el episodio.</li>
</ol>

<p>Y el aviso que más se ignora: <strong>dolor de cabeza, mareo, náuseas y confusión que ceden al salir de casa</strong> son el cuadro típico. Si despiertas de madrugada con la cabeza como un tambor con la calefacción puesta, sal.</p>

<p>El detector es el primer euro del kit de invierno: junto a él van radio, luz y abrigo en <a href="/kit/kit-hogar/">kit hogar o confinamiento</a>, seguridad eléctrica en <a href="/kit/kit-electricidad/">kit de electricidad</a> y frío en <a href="/kit/kit-frio/">kit de frío y nevada</a>. Si aún no has montado nada, empieza por <a href="/blog/como-montar-tu-kit-72h/">cómo montar tu kit de 72 horas</a>: te lleva media tarde.</p>
"""

ENTRADA = {
    "slug": SLUG,
    "titulo": "Mejor detector de monóxido de carbono: 6 tipos comparados (2026)",
    "fecha": HOY,
    "lectura": "8 min",
    "resumen": "Cómo elegir detector de CO: los umbrales de la norma UNE-EN 50291, 6 tipos comparados con precio, dónde colocarlo y qué hacer si suena la alarma.",
    "autor": "Redacción Kit72h",
    "fuente": [
        {"nombre": "Ministerio de Sanidad — Plan Nacional de actuaciones preventivas por bajas temperaturas 2025-2026 (PDF)",
         "url": "https://www.sanidad.gob.es/areas/sanidadAmbiental/riesgosAmbientales/frioExtremo/publicaciones/docs/Plan_Frio_25-26.pdf"},
        {"nombre": "Programa de Tóxico-vigilancia del Ministerio de Sanidad (vía Dirección General de Salud Pública de Murcia): 5.000-10.000 intoxicaciones y media de 125 muertes al año",
         "url": "https://www.murciasalud.es/-/sanidad-aconseja-precaucion-en-el-uso-de-braseros-estufas-o-calderas-para-evitar-accidentes-potencialmente-graves"},
        {"nombre": "AENOR — UNE-EN 50291-1:2018, detectores de monóxido de carbono en locales de uso doméstico",
         "url": "https://tienda.aenor.com/p/norma-une-en-50291-1-2018-ac-2021-01-n0065182"},
        {"nombre": "Protección Civil — Recomendaciones generales por riesgo",
         "url": "https://www.proteccioncivil.es/gestion-riesgos/recomendaciones"},
        {"nombre": "Comunidad de Madrid (ASEM 112) — Detectores domésticos: ubicación y mantenimiento",
         "url": "https://www.comunidad.madrid/seguridad-emergencias-asem-112/instala-detectores-humo-tu-hogar"},
    ],
    "cuerpo": CUERPO.strip(),
    "kits_relacionados": ["kit-hogar", "kit-apagon", "kit-electricidad", "kit-frio", "kit-incendio"],
    "etiquetas": ["monóxido de carbono", "detector CO", "seguridad en casa", "calefacción",
                  "invierno", "comparativa", "prevención", "apagón"],
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
        "comparativa detector de monóxido de carbono: 6 tipos con precio, umbrales "
        "de la norma UNE-EN 50291 (30/50/100/300 ppm), colocación, 5 errores y "
        "protocolo de alarma; 5 fuentes oficiales (Ministerio de Sanidad, "
        "Tóxico-vigilancia, AENOR, Protección Civil, Comunidad de Madrid). " + nota)

with open(RUTA, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(blog, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"OK: {len(blog['entradas'])} entradas, total={blog['meta']['total']}")
print(f"cuerpo={palabras} palabras | resumen={len(ENTRADA['resumen'])} car. | "
      f"internos={len(internos)} | amazon={len(re.findall(r'amazon.es', cuerpo))}")
print("primera:", blog["entradas"][0]["slug"], blog["entradas"][0]["fecha"])
