#!/usr/bin/env python3
"""Kit72h — añadir/actualizar la entrada de blog 'mejor-extintor-domestico'.

Re-ejecutable: si la entrada ya existe la REEMPLAZA (no falla), mantiene el
orden por fecha descendente y recalcula meta.total / meta.ultima_revision.

Sustituye a agregar-blog-mental.py, cuya entrada (salud-mental-y-sueno-en-una-
emergencia) ya estaba publicada → «La entrada ya existe». Fila nueva del mapa
de keywords: «mejor extintor doméstico» (Cluster C, comparativa de compra —
conversión): el kit incendio y el kit hogar ya recomiendan un extintor, pero
ninguna página del sitio compara tipos ni explica clases de fuego.
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUTA = RAIZ / "data" / "blog.json"
HOY = "2026-10-17"
SLUG = "mejor-extintor-domestico"

CUERPO = """
<p>Se quema la sartén, salta la regleta o una vela cae sobre la cortina: entre el fuego de un plato y tener que salir corriendo hay muy poco margen, y en España ese margen se pierde todos los días. <strong>En 2024 murieron 234 personas en incendios y explosiones en España, 172 de ellas dentro de viviendas</strong>, y entre las probables causas encabezan las eléctricas, con el <strong>41,9 %</strong>. Son las cifras del Estudio de víctimas de incendios de la Fundación MAPFRE y la APTB (Asociación Profesional de Técnicos de Bomberos), que desde 2010 recoge los datos de bomberos y de los institutos de medicina forense.</p>

<p>El extintor es la respuesta barata: <strong>entre 25 y 60 €</strong> para el fuego que empieza mientras tú estás en casa. La norma obliga a instalarlos y mantenerlos en edificios y locales —el RIPCI, Real Decreto 513/2017, es el reglamento de referencia—, pero en el interior de una vivienda particular no hay obligación legal. Aquí decides qué tipo apaga qué, con seis comparados y dónde colgarlo.</p>

<h2>1. Primero decide esto: qué clase de fuego tienes</h2>

<p>En la etiqueta de cualquier extintor aparece una letra: es lo único que importa al comprar. La norma UNE-EN 3-7 fija las clases y los «hogares tipo» que el aparato tiene que apagar:</p>

<table>
<thead><tr><th>Clase</th><th>Qué arde</th><th>Dónde la encuentras en casa</th></tr></thead>
<tbody>
<tr><td>A</td><td>Sólidos: madera, papel, tela, cartón</td><td>Sofá, cortina, armario, papelera</td></tr>
<tr><td>B</td><td>Líquidos: gasolina, disolventes, aceite</td><td>Taller, garaje, bombonas</td></tr>
<tr><td>C</td><td>Gases combustibles</td><td>Butano, gas de la cocina</td></tr>
<tr><td>D</td><td>Metales (uso industrial)</td><td>Casi nunca en una vivienda</td></tr>
<tr><td>F</td><td>Grasas y aceites de cocina calientes</td><td>Sartén y freidora: el más frecuente en casa</td></tr>
</tbody>
</table>

<p>La traducción práctica: <strong>el polvo ABC cubre A, B y C</strong>, casi todo lo que arde en un piso. Lo que <strong>no cubre bien es la sartén (clase F)</strong>: el aceite se apaga por fuera y vuelve a prender en cuanto lo muevas. Para cocinar, extintor de clase F (espuma o agua con aditivo) o, mejor y más rápido, <strong>tapa la sartén con su tapa o con una manta antifuego</strong>. Echar agua es la forma clásica de quemarse: vaporiza y arrastra el aceite encendido por toda la cocina.</p>

<h2>2. Los seis tipos, comparados</h2>

<p>Precios orientativos en Amazon España para extintores con marcado CE; cada enlace abre la búsqueda del tipo, así que ves el precio del día, no el de cuando se escribió esto.</p>

<table>
<thead><tr><th>Tipo</th><th>Cuándo compensa</th><th>Precio orientativo</th></tr></thead>
<tbody>
<tr><td><a href="https://www.amazon.es/s?k=extintor+de+polvo+abc+2+kg&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Polvo ABC de 1-2 kg ↗</a></td><td>Primera compra: mochila, recibidor, despensa</td><td>20-35 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=extintor+de+polvo+abc+6+kg&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Polvo ABC de 6 kg ↗</a></td><td>Casa completa, garaje o comunidad</td><td>40-70 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=extintor+co2+2+kg&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">CO₂ de 2 kg ↗</a></td><td>Cuadro eléctrico o taller: no deja residuo</td><td>40-65 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=extintor+de+espuma+clase+f+cocina&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Espuma clase F (6 L) ↗</a></td><td>Cocina: el único para aceite caliente</td><td>35-60 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=extintor+acuoso+domestico&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Agua con aditivo / acuoso ↗</a></td><td>Cocina y salón: eficaz y poco sucio</td><td>30-55 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=manta+antifuego+extintor+aerosol&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Manta antifuego o aerosol ↗</a></td><td>Sobre la vitro y en el coche: corta el fuego pronto</td><td>10-25 €</td></tr>
</tbody>
</table>

<h2>3. Ganadores por caso</h2>

<ul>
<li><strong>Un solo aparato para un piso:</strong> polvo ABC de 6 kg, el mismo que cuelga en las escaleras; si el presupuesto aprieta, el de 2 kg ya cubre el fuego incipiente: <a href="https://www.amazon.es/s?k=extintor+de+polvo+abc+2+kg&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">ver extintores de polvo ABC ↗</a>.</li>
<li><strong>Cocina con frecuencia:</strong> espuma clase F junto a la puerta, nunca encima de la vitro, más manta antifuego en el cajón de debajo: <a href="https://www.amazon.es/s?k=extintor+de+espuma+clase+f+cocina&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">ver extintores de clase F ↗</a>.</li>
<li><strong>Cuadro eléctrico o trastero:</strong> CO₂ de 2 kg, que deja el aparato y los cables utilizables después: <a href="https://www.amazon.es/s?k=extintor+co2+2+kg&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">ver extintores de CO₂ ↗</a>.</li>
<li><strong>Garaje o taller con combustible:</strong> polvo ABC de 6 kg en su soporte de pared y visible desde la entrada: <a href="https://www.amazon.es/s?k=extintor+de+polvo+abc+6+kg+soporte+pared&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">ver extintores de 6 kg ↗</a>.</li>
<li><strong>Maletero y caravana:</strong> manta antifuego o pequeño extintor, porque en una furgoneta lo que arde antes es la nevera y la ropa — el resto va en <a href="/kit/kit-coche/">kit de coche</a>: <a href="https://www.amazon.es/s?k=manta+antifuego+coche&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">ver mantas antifuego ↗</a>.</li>
</ul>

<p>Aviso honesto: un extintor de 2 kg se vacía en <strong>unos 10-15 segundos</strong> de chorro. Sirve para el fuego que acaba de empezar, no para una habitación en llamas. Si en dos pasadas no lo has cortado, es momento de salir.</p>

<h2>4. Dónde ponerlo (y la revisión de un minuto al mes)</h2>

<ul>
<li><strong>Cerca de la salida, nunca al otro lado del fuego.</strong> Regla de bomberos: no se atraviesa la estancia que arde para cogerlo. Visible, sin muebles delante y con señalización encima.</li>
<li><strong>Altura y sujeción.</strong> En su soporte, a la altura de la mano y lejos de calor, humedad y golpes. En el suelo o detrás de una puerta que se abre hacia él, el error clásico.</li>
<li><strong>Revisión mensual (60 segundos):</strong> aguja del manómetro <strong>en zona verde</strong>, precinto y pasador intactos, manguera sin grietas, cuerpo sin óxido. Y <strong>gíralo del revés un par de veces al año</strong> para que el polvo no se apelmace.</li>
<li><strong>Revisión formal:</strong> si cuelga en una instalación sujeta al RIPCI, el mantenimiento lo hace una empresa habilitada: revisión anual y prueba de presión cada cinco años. En vivienda particular no es obligatorio, pero conviene lo mismo: <strong>la vida útil ronda los 20 años desde la fabricación</strong> (Tecnifuego) y hay que sustituirlo antes si la aguja no vuelve al verde.</li>
<li><strong>En el apagón, doble check.</strong> Velas y generadores disparan el riesgo justo cuando nadie mira: repasa manómetro y vela antes de que anochezca. El detalle está en <a href="/kit/kit-apagon/">kit de apagón</a>.</li>
</ul>

<h2>5. Cinco errores que dejan el extintor inútil</h2>

<ul>
<li><strong>Agua en un fuego eléctrico.</strong> Primero se corta la luz si se puede y después se usa CO₂ o polvo con ensayo dieléctrico.</li>
<li><strong>Comprar por el color.</strong> Rojo no dice nada: mira la etiqueta con las letras A/B/C/F y la eficacia. Un aerosol no es un extintor de 6 kg.</li>
<li><strong>Taparlo con la lavadora o con cajas.</strong> El que lleva años en el trastero no existe.</li>
<li><strong>Exceso de confianza.</strong> El extintor es para el fuego de un plato. Si la llama toca el techo o hay humo denso, se cierra la puerta y se sale.</li>
<li><strong>Olvidar el resto del sistema.</strong> El extintor no avisa: para eso está el detector de humo, y para no encender fuego innecesario, la linterna. Todo eso está en <a href="/kit/kit-incendio/">kit de incendio</a> y en <a href="/blog/seguridad-pasiva-hogar-incendios-electricos/">seguridad pasiva contra incendios e incendios eléctricos</a>.</li>
</ul>

<h2>6. Si se declara: cuatro pasos, en este orden</h2>

<ol>
<li><strong>Avisar:</strong> llama al <strong>112</strong> antes de tocar el extintor, con la dirección y qué arde. Un dato erróneo es peor que uno tarde.</li>
<li><strong>Proteger la salida:</strong> extintor en mano, vertical, manguera a la base del fuego y a un paso de la puerta.</li>
<li><strong>Una sola prueba:</strong> dos pasadas cortas. Si no baja, se suelta el extintor, se cierra la puerta detrás y se sale sin coger nada más.</li>
<li><strong>No volver jamás</strong> hasta que los bomberos lo autoricen, aunque «solo quede la ceniza»: el humo es lo que mata.</li>
</ol>

<p>Eso cierra el equipo del fuego. El resto de la casa —luz, agua, abrigo y documentos— se monta en la misma tarde con la <a href="/blog/botiquin-emergencia-que-llevar/">guía del botiquín</a> y con <a href="/blog/como-montar-tu-kit-72h/">cómo montar tu kit de 72 horas</a>; si solo preparas un rincón, que sea el de <a href="/kit/kit-hogar/">kit hogar o confinamiento</a>.</p>
"""

ENTRADA = {
    "slug": SLUG,
    "titulo": "Mejor extintor doméstico 2026: 6 tipos comparados y dónde colocarlo en casa",
    "fecha": HOY,
    "lectura": "8 min",
    "resumen": "Qué extintor para casa: polvo, CO₂, espuma o clase F. Seis tipos comparados con precio, dónde colocarlo y la revisión mensual de un minuto.",
    "autor": "Redacción Kit72h",
    "fuente": [
        {"nombre": "BOE — Real Decreto 513/2017 (RIPCI): instalaciones de protección contra incendios, texto consolidado",
         "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2017-6606"},
        {"nombre": "Fundación MAPFRE y APTB — Estudio de víctimas de incendios en España (234 muertos en 2024, 172 en viviendas, 41,9 % causas eléctricas)",
         "url": "https://www.fundacionmapfre.org/publicaciones/todas/estudio-victimas-incendios-en-espana/"},
        {"nombre": "Tecnifuego — análisis del Estudio de Víctimas de Incendios en España 2024",
         "url": "https://www.tecnifuego.org/comunicacion/analisis-del-informe-sobre-victimas-de-incendios-en-espana-en-2024-cifras-y-tendencias"},
        {"nombre": "eldiario.es — Extintor doméstico: seis preguntas (vida útil de 20 años, prueba de presión cada 5 años y revisión anual, según Tecnifuego)",
         "url": "https://www.eldiario.es/consumoclaro/elegir-extintor-domestico-preguntas-guia-basica-de-compra_1_10184377.html"},
        {"nombre": "INSST — NTP 28, Medios manuales de extinción (extintores portátiles: masa ≤ 20 kg, agentes y eficacia)",
         "url": "https://www.insst.es/documents/94886/195574/NTP+28+Medios+manuales+de+extinci%C3%B3n.pdf/63ecfb2a-67f2-4994-8a20-f499ffa2662c"},
        {"nombre": "Protección Civil — Recomendaciones generales por riesgo (medidas preventivas en el hogar)",
         "url": "https://www.proteccioncivil.es/gestion-riesgos/recomendaciones"},
    ],
    "cuerpo": CUERPO.strip(),
    "kits_relacionados": ["kit-incendio", "kit-hogar", "kit-apagon", "kit-coche"],
    "etiquetas": ["incendio", "extintor", "seguridad en casa", "cocina", "comparativa",
                  "prevención", "electricidad", "apagón"],
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
        "comparativa de extintores domésticos: clases de fuego A-F según UNE-EN 3-7, "
        "6 tipos con precio orientativo, ganadores por caso, colocación y revisión "
        "mensual, 5 errores y protocolo de 4 pasos; 6 fuentes (BOE RIPCI, Fundación "
        "MAPFRE/APTB, Tecnifuego, eldiario, INSST, Protección Civil). " + nota)

with open(RUTA, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(blog, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"OK: {len(blog['entradas'])} entradas, total={blog['meta']['total']}")
print(f"cuerpo={palabras} palabras | resumen={len(ENTRADA['resumen'])} car. | "
      f"internos={len(internos)} | amazon={len(re.findall(r'amazon.es', cuerpo))}")
print("primera:", blog["entradas"][0]["slug"], blog["entradas"][0]["fecha"])
