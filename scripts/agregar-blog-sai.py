#!/usr/bin/env python3
"""Kit72h — añadir/actualizar la entrada de blog 'mejor-sai-ups-casa-apagon'.

Re-ejecutable: si la entrada ya existe la REEMPLAZA (no falla), mantiene el
orden por fecha descendente y recalcula meta.total / meta.ultima_revision.

Sustituye a agregar-blog-mental.py, cuya entrada (salud-mental-y-sueno-en-una-
emergencia) ya estaba publicada → «La entrada ya existe». Fila nueva del mapa
de keywords: «mejor SAI / UPS para casa y router» (Cluster C, comparativa de
compra — conversión): el SAI del router ya se recomienda en kit-apagon y
kit-electricidad, pero ninguna página del sitio explica VA, autonomía ni
compara tipos.
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUTA = RAIZ / "data" / "blog.json"
HOY = "2026-10-18"
SLUG = "mejor-sai-ups-casa-apagon"

CUERPO = """
<p>Son las 12:33 de un martes y se va la luz del router. Ocho segundos, vuelve la corriente y ya está — hasta que a la tercera semana el portátil se reinicia solo o el módem se cae cada vez que salta un diferencial. Ese es el trabajo del <strong>SAI (sistema de alimentación ininterrumpida)</strong>: aguantar los segundos que la red no da y proteger la casa cuando la luz vuelve.</p>

<p>El dato que ordena este artículo es de Red Eléctrica: en 2025 el sistema peninsular registró <strong>12 interrupciones de suministro, un 29 % menos que en 2024, con un Tiempo de Interrupción Medio de 0,25 minutos</strong>, muy lejos de los 15 minutos del artículo 26.2 del Real Decreto 1955/2000. La red española es excelente en promedio, pero el promedio no te consuela cuando el corte te toca a ti: aquí va qué SAI te hace falta y cuántos VA necesitas.</p>

<h2>1. Qué hace un SAI (y las tres cosas que no hace)</h2>

<p>Un SAI es una batería con un inversor y un conmutador: cuando la red baja de tensión, desaparece o sube de golpe, <strong>conmuta a baterías en milisegundos</strong> y sigue dando corriente — el router ni se entera. Filtra además los picos que llegan justo al volver la luz.</p>

<ul>
<li><strong>Sí alimenta:</strong> router, ONT, portátil, tele, cargadores, luces LED, detector de monóxido: de 15 a 300 W.</li>
<li><strong>No alimenta:</strong> nevera, horno, vitro, lavadora o calefacción: más de 1.000 W con arranque todavía mayor, que un SAI de 1.000 VA no mueve ni un segundo. Para eso hay <a href="/blog/generador-vs-power-station-comparativa/">generador o power station</a>.</li>
<li><strong>No es un estabilizador:</strong> corrige la tensión pero no da ni un segundo de batería. Si se va la luz, se apaga contigo.</li>
<li><strong>No es un generador:</strong> no crea energía, la guarda. Su autonomía se mide en minutos.</li>
</ul>

<h2>2. Los seis tipos, comparados</h2>

<p>Precios orientativos en Amazon España: cada enlace abre la búsqueda del tipo, así que ves el precio del día, no el de cuando se escribió esto.</p>

<table>
<thead><tr><th>Tipo</th><th>Cuándo compensa</th><th>Precio orientativo</th></tr></thead>
<tbody>
<tr><td><a href="https://www.amazon.es/s?k=mini+ups+dc+router+ont&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Mini-UPS de CC para router y ONT ↗</a></td><td>Solo comunicación: lo más barato y lo que más horas da</td><td>30-60 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=sai+ups+650va+line+interactive&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">SAI offline de 400-650 VA ↗</a></td><td>Primer PC de sobremesa o tele + router</td><td>45-80 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=sai+ups+1500va+line+interactive+avr&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Line-interactive de 1.000-1.500 VA con AVR ↗</a></td><td>Ordenador de trabajo con monitor y periféricos</td><td>70-140 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=sai+online+doble+conversion+1500va&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Online de doble conversión ↗</a></td><td>Equipo que no puede permitirse ni una microinterrupción</td><td>200-500 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=sai+ups+con+bateria+externa&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">SAI con baterías externas ampliables ↗</a></td><td>Quieres horas, no minutos: autonomía ampliable a mano</td><td>150-400 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=sai+ups+3000va+casa+completa&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">SAI de 2.000-3.000 VA ↗</a></td><td>Varios equipos a la vez y cuadro eléctrico pequeño</td><td>180-350 €</td></tr>
</tbody>
</table>

<p>La diferencia entre la primera y la última no es la marca: es cuánta batería llevas dentro. Un detalle que decide la compra: la <strong>onda de salida</strong> — para router y tele sirve cualquier modelo, pero para fuentes de alimentación (portátiles, audio) lo ideal es <strong>onda sinusoidal pura</strong>, porque hay SAI baratos con senoide aplanada que los cargadores rechazan con un pitido.</p>

<h2>3. La cuenta de los VA: cuánto necesitas de verdad</h2>

<p>Los SAI se venden en <strong>VA (voltiamperios)</strong>, no en vatios, y ahí está la confusión de casi todas las compras. Como la relación entre ambos es el factor de potencia —entre 0,6 y 0,7 en un SAI doméstico—, cuenta que <strong>W ≈ VA × 0,6</strong>: un SAI de 1.000 VA mueve en torno a 600 W. La ficha técnica del modelo es la que manda.</p>

<table>
<thead><tr><th>Qué quieres alimentar</th><th>Consumo orientativo</th><th>SAI recomendado</th><th>Autonomía orientativa</th></tr></thead>
<tbody>
<tr><td>Router + ONT</td><td>15-30 W</td><td>Mini-UPS DC o SAI de 400-650 VA</td><td>2-4 h</td></tr>
<tr><td>Router, tele y cargadores</td><td>80-150 W</td><td>SAI de 650-1.000 VA</td><td>45-90 min</td></tr>
<tr><td>Portátil + monitor</td><td>60-120 W</td><td>SAI de 1.000-1.500 VA</td><td>1-2 h</td></tr>
<tr><td>PC de sobremesa con monitor</td><td>300-500 W</td><td>SAI de 1.500-2.000 VA (onda pura)</td><td>8-15 min</td></tr>
<tr><td>Nevera, horno o calefacción</td><td>1.000-3.000 W</td><td>Ninguno: power station o generador</td><td>—</td></tr>
</tbody>
</table>

<p>Las autonomías son horquillas calculadas sobre la batería de serie (12 V y 7 Ah ronda los 84 Wh) y el rendimiento real del inversor: sirven para comparar modelos, no para firmar, y se desploman si la dejas descargada o con calor. Traducción: <strong>lo que un SAI compra no es horas de casa encendida, es que la comunicación no se te caiga</strong> mientras decides qué hacer — y esa decisión está en <a href="/kit/kit-apagon/">el kit de apagón</a>.</p>

<h2>4. Ganadores por caso</h2>

<ul>
<li><strong>Router y ONT, lo primero de todo:</strong> mini-UPS de CC, el que más horas da por el precio. Si prefieres SAI convencional, el de <a href="https://www.amazon.es/dp/B07DPWBBDP?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">600-900 VA para router y ONT ↗</a> es el punto dulce: aguanta el rato que hace falta y protege además contra el pico de retorno.</li>
<li><strong>Teletrabajo con portátil:</strong> line-interactive de 1.000-1.500 VA con AVR: <a href="https://www.amazon.es/s?k=sai+ups+1500va+line+interactive+avr&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">ver SAIs line-interactive ↗</a>. El AVR mantiene la tensión sin gastar batería en los bajones de la tarde.</li>
<li><strong>PC de sobremesa que no puede reiniciarse:</strong> online de doble conversión, que alimenta siempre desde baterías: el del <a href="/kit/kit-electricidad/">kit de electricidad</a>.</li>
<li><strong>Casa donde ya se han ido las luces varias veces:</strong> SAI con baterías externas ampliables: <a href="https://www.amazon.es/s?k=sai+ups+con+bateria+externa&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">ver modelos ampliables ↗</a>. La única vía para pasar de minutos a horas.</li>
<li><strong>Si el objetivo es la casa entera:</strong> no es un SAI, es una <a href="https://www.amazon.es/s?k=estacion+de+energia+portatil&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">estación de energía portátil ↗</a> con <a href="/blog/panel-solar-portatil-72h-emergencia/">panel solar</a>: compara antes en <a href="/blog/generador-vs-power-station-comparativa/">generador frente a power station</a>.</li>
</ul>

<h2>5. Los cinco errores que más se repiten</h2>

<ul>
<li><strong>Comprar por VA sin mirar los vatios reales.</strong> Calcula qué enchufas con la tabla de arriba y solo después mira el precio.</li>
<li><strong>Cargarle la nevera.</strong> No solo no la moverá: dejará la batería muerta justo cuando la necesitas para el router.</li>
<li><strong>Olvidar la batería.</strong> Las de plomo duran 3-5 años; una vencida es un SAI que se apaga contigo. Aviso en el calendario cada dos años.</li>
<li><strong>Comprarlo y no probarlo.</strong> Desconecta la red un segundo: si el equipo se reinicia, o está mal conectado o el modelo no vale para esa carga.</li>
<li><strong>Confundirlo con un estabilizador o un generador.</strong> Si necesitas horas de nevera o calefacción, estás en el artículo equivocado: mira <a href="/blog/mejor-powerbank-emergencia-capacidad/">powerbanks</a> y <a href="/blog/generador-vs-power-station-comparativa/">estaciones de energía</a>.</li>
</ul>

<h2>6. Norma, mantenimiento y cómo encaja en tu kit</h2>

<p>Para comprar con criterio basta con fijarse en que el modelo cumple la norma europea armonizada <strong>UNE-EN IEC 62040-1:2019</strong> (requisitos de seguridad de los SAI, vigente en España con enmiendas de 2021, 2023 y 2025): garantiza que el aparato es seguro al tocarlo, no que aguante horas.</p>

<p>Mantenimiento en tres líneas: <strong>prueba de carga cada seis meses</strong> (desconecta la red un minuto), <strong>ventilación</strong> (que el SAI respire, nunca en mueble cerrado) y <strong>sustitución de baterías</strong> antes de que el equipo se queje. Regla de oro: <strong>pruébalo un día normal, no durante el apagón</strong>.</p>

<p>En marzo de 2026 la CNMC publicó su informe de recomendaciones sobre el incidente del 28 de abril de 2025: mitiga los cambios bruscos de tensión y refuerza la inspección de los sistemas de protección. La red mejorará, pero proteger tu casa sigue siendo cosa tuya. La lista está en <a href="/kit/kit-apagon/">el kit de apagón</a> y en <a href="/blog/apagon-lecciones-28a/">las lecciones del 28 de abril</a>; si aún no tienes la base montada, empieza por <a href="/blog/como-montar-tu-kit-72h/">cómo montar tu kit de 72 horas</a>.</p>
"""

ENTRADA = {
    "slug": SLUG,
    "titulo": "Mejor SAI (UPS) para casa y router: 6 tipos por VA y vatios (2026)",
    "fecha": HOY,
    "lectura": "7 min",
    "resumen": "¿Cuánto aguanta tu router y PC en un apagón? 6 SAI comparados por VA y vatios, ganadores por caso y los 5 errores que más se repiten (2026).",
    "autor": "Redacción Kit72h",
    "fuente": [
        {"nombre": "Red Eléctrica — Energía no suministrada (ENS) y Tiempo de Interrupción Medio (TIM): 12 interrupciones y TIM de 0,25 min en 2025",
         "url": "https://www.sistemaelectrico-ree.es/es/informe-del-sistema-electrico/transporte/energia-no-suministrada-ens-y-tiempo-de-interrupcion-medio"},
        {"nombre": "CNMC — Informe de recomendaciones y propuestas sobre el incidente del 28 de abril de 2025 (marzo 2026)",
         "url": "https://www.cnmc.es/prensa/informe-incidente-electrico-20260319"},
        {"nombre": "UNE — UNE-EN IEC 62040-1:2019, Sistemas de alimentación ininterrumpida (SAI). Parte 1: Requisitos de seguridad",
         "url": "https://www.une.org/encuentra-tu-norma/busca-tu-norma/norma?c=N0062428"},
        {"nombre": "BOE — Real Decreto 1955/2000, artículo 26.2 (indicadores de calidad de suministro: 15 minutos de referencia)",
         "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2000-24019"},
        {"nombre": "La Moncloa — Informe no confidencial del Comité de análisis del 28 de abril de 2025",
         "url": "https://www.lamoncloa.gob.es/consejodeministros/resumenes/Documents/2025/Informe-no-confidencial-Comite-de-analisis-28A.pdf"},
        {"nombre": "Protección Civil — Recomendaciones generales por riesgo",
         "url": "https://www.proteccioncivil.es/gestion-riesgos/recomendaciones"},
    ],
    "cuerpo": CUERPO.strip(),
    "kits_relacionados": ["kit-apagon", "kit-electricidad", "kit-hogar", "kit-basico-72h"],
    "etiquetas": ["apagón", "SAI", "UPS", "electricidad", "router", "comparativa",
                  "comunicación", "protección de equipos"],
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
for m in re.findall(r'href="(https://www\.amazon\.es/[^"]+)"', cuerpo):
    assert "rel=\"sponsored nofollow noopener\"" in cuerpo, "sin rel sponsored"
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
        "comparativa de SAI/UPS domésticos: seis tipos, cuenta de VA vs vatios "
        "(W ≈ VA × 0,6), tabla de autonomía por caso, 5 errores y ganadores; "
        "6 fuentes oficiales (REE TIM/ENS 2025, CNMC informe 28-A, UNE-EN IEC "
        "62040-1:2019, BOE RD 1955/2000, La Moncloa Comité 28-A, Protección "
        "Civil). " + nota)

with open(RUTA, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(blog, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"OK: {len(blog['entradas'])} entradas, total={blog['meta']['total']}")
print(f"cuerpo={palabras} palabras | resumen={len(ENTRADA['resumen'])} car. | "
      f"internos={len(internos)} | amazon={len(re.findall('amazon.es', cuerpo))}")
print("primera:", blog["entradas"][0]["slug"], blog["entradas"][0]["fecha"])
