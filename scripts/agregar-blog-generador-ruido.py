#!/usr/bin/env python3
"""Kit72h — añadir/actualizar la entrada de blog 'generador-ruido-normativa-comunidad'.

Re-ejecutable: si la entrada ya existe la REEMPLAZA (no falla), mantiene el
orden por fecha descendente y recalcula meta.total / meta.ultima_revision.
Fila del mapa de keywords: «generator ruido normativa comunidad» (Cluster E,
P3, intención info → guía con bloque de compra).
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUTA = RAIZ / "data" / "blog.json"
HOY = "2026-10-14"
SLUG = "generador-ruido-normativa-comunidad"

BOE_RUIDO = "https://www.boe.es/buscar/act.php?id=BOE-A-2003-20976"
BOE_RD1367 = "https://www.boe.es/buscar/act.php?id=BOE-A-2007-18397"
BOE_RD212 = "https://www.boe.es/buscar/act.php?id=BOE-A-2002-4099"
BOE_DIR14 = "https://www.boe.es/buscar/doc.php?id=DOUE-L-2000-81213"
BOE_LPH = "https://www.boe.es/buscar/act.php?id=BOE-A-1960-10906"

CUERPO = """
<p>Un apagón de dos días, el generador que compraste «por si acaso» y, a las 23:40, un golpe en la puerta: el vecino no puede dormir. La respuesta a «¿y esto es legal?» no está en ningún foro: está en la <strong>Ley 37/2003 del Ruido</strong>, en la ordenanza de tu ayuntamiento y en la Ley de Propiedad Horizontal.</p>

<h2>1. La ley estatal: dónde empieza lo doméstico y dónde deja de serlo</h2>

<p>La <a href="{BOE_RUIDO}" target="_blank" rel="noopener">Ley 37/2003, de 17 de noviembre, del Ruido</a> es la norma de cabecera, y su artículo 2.2.a) da la clave: quedan fuera de su ámbito «las actividades domésticas o los comportamientos de los vecinos, cuando la contaminación acústica producida por aquéllos se mantenga dentro de límites tolerables de conformidad con las ordenanzas municipales y los usos locales».</p>

<p>Traducción: <strong>encender tu generador es una actividad doméstica… hasta que deja de serlo</strong>. En cuanto excedes lo que tu ayuntamiento considera tolerable, entras en el régimen sancionador: el artículo 28.5 permite a las ordenanzas locales tipificar como infracción «el ruido producido por las actividades domésticas o los vecinos».</p>

<table>
<thead><tr><th>Gravedad</th><th>Multa</th><th>Cuándo aplica (resumen)</th></tr></thead>
<tbody>
<tr><td>Leve</td><td>Hasta 600 €</td><td>Incumplir la ley sin encajar en los supuestos graves</td></tr>
<tr><td>Grave</td><td>601 – 12.000 €</td><td>Superar los valores límite aplicables, sin daño grave</td></tr>
<tr><td>Muy grave</td><td>12.001 – 300.000 €</td><td>Superarlos con daño o riesgo grave para la salud</td></tr>
</tbody>
</table>

<h2>2. Los números del RD 1367/2007: cuántos dB se toleran de noche</h2>

<p>El <a href="{BOE_RD1367}" target="_blank" rel="noopener">Real Decreto 1367/2007</a> fija los objetivos de calidad en su anexo II. Para un <strong>sector de suelo residencial</strong> en áreas urbanizadas existentes (tabla A): <strong>65 dB de día, 65 de tarde y 55 de noche</strong>. Dentro de la vivienda (tabla B), que es lo que se mide en el dormitorio del vecino: <strong>45/45/35 en las estancias y 40/40/30 en los dormitorios</strong>.</p>

<p>Los periodos los marca cada ciudad; la <a href="https://www.bocm.es/boletin/CM_Orden_BOCM/2011/03/14/BOCM-20110314-56.PDF" target="_blank" rel="noopener">Ordenanza de la Comunidad de Madrid</a> divide el día en diurno (7:00–19:00), vespertino (19:00–23:00) y nocturno (23:00–7:00). Entre los 65 de día y los 55 de noche hay <strong>10 decibelios, que el oído percibe como el doble de ruido</strong>: lo que a las once es una molestia, a la una es un motivo de denuncia.</p>

<h2>3. Tu generador ya trae los dB en la etiqueta</h2>

<p>Los grupos electrógenos no se escapan: la <a href="{BOE_DIR14}" target="_blank" rel="noopener">Directiva 2000/14/CE</a>, transpuesta en España por el <a href="{BOE_RD212}" target="_blank" rel="noopener">Real Decreto 212/2002</a> (BOE-A-2002-4099), obliga a declarar el nivel de potencia acústica garantizada de los grupos electrógenos de menos de 400 kW. Ese dato va en la etiqueta y en la ficha técnica. Valores típicos, medidos a 7 metros —la distancia estándar de las fichas—:</p>

<table>
<thead><tr><th>Tipo de equipo</th><th>Ruido a 7 m</th><th>Para qué sirve en casa</th></tr></thead>
<tbody>
<tr><td>Inverter insonorizado (maleta)</td><td>48 – 60 dB(A)</td><td>La opción silenciosa: luces, nevera, router</td></tr>
<tr><td>Open-frame portátil (barato)</td><td>70 – 80 dB(A)</td><td>El más ruidoso: suena como una aspiradora</td></tr>
<tr><td>Grupo instalado (standby)</td><td>60 – 75 dB(A)</td><td>Vivienda unifamiliar con plazo del vecino</td></tr>
<tr><td><a href="/blog/generador-vs-power-station-comparativa/">Power station</a> (batería)</td><td>~30 dB(A)</td><td>Solo ventilador: cero ruido y cero humos</td></tr>
</tbody>
</table>

<p>Dos reglas de la física explican casi todos los conflictos: <strong>cada +10 dB se percibe como el doble de ruido</strong> y <strong>el sonido cae unos 6 dB cada vez que doblas la distancia</strong>. Un open-frame de 72 dB a 7 metros suena como 66 a 14 y 60 a 28: alejar el equipo del patio del vecino vale más que cualquier barrera.</p>

<h2>4. La ordenanza municipal: el texto que de verdad te multa</h2>

<p>La ley estatal da el marco, pero la multa la pinta tu ayuntamiento. Busca «ordenanza contaminación acústica» más tu municipio: ahí están los decibelios por zona, los horarios y las sanciones. Como muestra, la <a href="https://www.sevilla.org/ayuntamiento/unidad-organica/servicio-de-apoyo-juridico/ordenanzas-del-municipio-de-sevilla/o-contra-la-contaminacion-acustica-ruidos-y-vibraciones.pdf" target="_blank" rel="noopener">Ordenanza de Sevilla</a>: «Los grupos electrógenos y los transformadores deberán instalarse de forma que queden convenientemente aislados contra ruido y vibraciones».</p>

<p>Fíjate en <em>aislados</em>: no dice «silenciosos», dice aislados contra ruido <strong>y vibraciones</strong>. Las vibraciones viajan por la estructura del edificio y despiertan al vecino aunque el aire esté callado.</p>

<h2>5. La comunidad de vecinos: la vía rápida no es la multa</h2>

<p>Si el ruido viene de un vecino —o lo provocas tú—, el camino más corto es la <a href="{BOE_LPH}" target="_blank" rel="noopener">Ley de Propiedad Horizontal</a>. Su artículo 7 prohíbe desarrollar en la vivienda actividades que contravengan las disposiciones generales sobre <strong>actividades molestas, insalubres, nocivas, peligrosas o ilícitas</strong>:</p>

<ul>
<li><strong>Requerimiento del presidente</strong>, a iniciativa propia o de cualquier propietario, con apercibimiento de acciones judiciales.</li>
<li><strong>Acción de cesación</strong> si persiste y la Junta lo autoriza: el juez puede acordar de forma cautelar la cesación inmediata, «bajo apercibimiento de incurrir en delito de desobediencia».</li>
<li><strong>Sentencia</strong> que, además de la cesación y la indemnización, puede privar del uso de la vivienda por un tiempo <strong>no superior a tres años</strong>.</li>
</ul>

<p>Un generador mal colocado puede costarte la multa, la indemnización y, en el peor caso, el uso de tu propia vivienda.</p>

<h2>6. Cómo usarlo sin dormir con la sanción encima</h2>

<ul>
<li><strong>Nunca dentro, ni en el garaje, ni en el trastero del portal.</strong> El monóxido mata antes que la multa; un <a href="https://www.amazon.es/dp/B0D66LK5NP?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">detector de CO a pilas</a> por planta es la medida más barata del kit.</li>
<li><strong>Alejar y orientar.</strong> Los 6 dB por distancia doblada trabajan a tu favor; orienta el escape hacia fuera y nunca contra un muro que refleje el sonido.</li>
<li><strong>Base antivibración.</strong> Una alfombrilla de goma corta el camino de vibración hacia la estructura —lo exige la ordenanza de Sevilla—: <a href="https://www.amazon.es/s?k=alfombrillas+antivibracion+generador&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">alfombrillas antivibración</a>.</li>
<li><strong>Horario.</strong> De 23:00 a 7:00 el objetivo baja de 65 a 55 dB: es cuando la misma molestia se convierte en expediente.</li>
<li><strong>Modo eco y carga real.</strong> Las fichas declaran el ruido a cuarto de carga; con el equipo al tope de vatios sube. Para luces y cargadores, un <a href="https://www.amazon.es/s?k=generador+inverter+silencioso&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">generador inverter silencioso</a> rinde igual con la mitad de ruido.</li>
<li><strong>Si vives en piso, no compres motor.</strong> Una <a href="https://www.amazon.es/s?k=power+station+portatil&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">power station</a> da corriente sin ruido, sin humo y sin discusión con la comunidad.</li>
</ul>

<h2>7. Los errores que más salen caros</h2>

<ul>
<li><strong>Creer que lo doméstico está siempre permitido:</strong> la ley te excluye solo «dentro de límites tolerables» según tu ordenanza.</li>
<li><strong>Mirar solo los vatios en la tienda:</strong> si la ficha no trae dB(A) a 7 m, es un equipo que no quieres en un edificio.</li>
<li><strong>Instalarlo pegado a la medianera:</strong> ruido y vibración al mismo vecino, y la ordenanza lo cita expresamente.</li>
<li><strong>Olvidar el CO y el combustible:</strong> la seguridad está en la <a href="/kit/kit-apagon/">guía del kit de apagón</a> y las primeras decisiones en <a href="/blog/apagon-lecciones-28a/">qué nos enseñó un apagón</a>.</li>
</ul>

<h2>8. Por dónde empezar hoy</h2>

<p>Si no tienes generador, decide antes si lo necesitas de verdad: para un piso, la <a href="/blog/generador-vs-power-station-comparativa/">comparativa entre generador y power station</a> es contundente. Si ya lo tienes, saca la ficha técnica, anota los dB a 7 m, cuenta los metros hasta el patio del vecino y busca tu ordenanza municipal. Para calcular vatios antes de comprar: <a href="/blog/panel-solar-portatil-72h-emergencia/">panel solar portátil</a> y <a href="/blog/generador-solar-emergencia-72h/">generador solar de emergencia</a>.</p>

<p>El ruido no se resuelve con buena voluntad: se resuelve con decibelios, metros y horarios. Y qué debe aguantar tu casa sin luz está en el <a href="/kit/kit-electricidad/">kit de electricidad y respaldo</a>.</p>
""".format(BOE_RUIDO=BOE_RUIDO, BOE_RD1367=BOE_RD1367, BOE_RD212=BOE_RD212,
           BOE_DIR14=BOE_DIR14, BOE_LPH=BOE_LPH)

ENTRADA = {
    "slug": SLUG,
    "titulo": "Generador y ruido en la comunidad: cuántos dB te toleran (2026)",
    "fecha": HOY,
    "lectura": "7 min",
    "resumen": "Límites de dB según la Ley 37/2003, el RD 1367/2007 y tu ordenanza municipal: cómo usar el generador sin multa y sin vecinos enfadados.",
    "autor": "Redacción Kit72h",
    "fuente": [
        {"nombre": "BOE — Ley 37/2003, de 17 de noviembre, del Ruido (arts. 2.2.a, 28 y 29)",
         "url": BOE_RUIDO},
        {"nombre": "BOE — Real Decreto 1367/2007 (anexo II: objetivos de calidad 65/65/55 y 45/35)",
         "url": BOE_RD1367},
        {"nombre": "BOE — Real Decreto 212/2002, emisiones sonoras de máquinas de uso al aire libre",
         "url": BOE_RD212},
        {"nombre": "BOE — Directiva 2000/14/CE sobre emisiones sonoras de grupos electrógenos",
         "url": BOE_DIR14},
        {"nombre": "BOE — Ley 49/1960 de Propiedad Horizontal, artículo 7 (actividades molestas)",
         "url": BOE_LPH},
        {"nombre": "Ayuntamiento de Sevilla — Ordenanza contra la contaminación acústica (grupos electrógenos aislados)",
         "url": "https://www.sevilla.org/ayuntamiento/unidad-organica/servicio-de-apoyo-juridico/ordenanzas-del-municipio-de-sevilla/o-contra-la-contaminacion-acustica-ruidos-y-vibraciones.pdf"},
        {"nombre": "BOCM — Ordenanza de Protección contra la Contaminación Acústica (periodos horarios)",
         "url": "https://www.bocm.es/boletin/CM_Orden_BOCM/2011/03/14/BOCM-20110314-56.PDF"},
        {"nombre": "Protección Civil — Recomendaciones generales por riesgo",
         "url": "https://www.proteccioncivil.es/gestion-riesgos/recomendaciones"},
        {"nombre": "Comisión Europea — Estrategia de la Unión de la Preparación (mínimo 72 horas de autonomía)",
         "url": "https://commission.europa.eu/topics/preparedness_es"},
    ],
    "cuerpo": CUERPO.strip(),
    "kits_relacionados": ["kit-electricidad", "kit-apagon", "kit-basico-72h", "kit-hogar"],
    "etiquetas": ["generador", "ruido", "normativa", "comunidad de vecinos",
                  "apagón", "energía", "preparacion", "escenarios"]
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
        "ruido del generador y normativa de la comunidad: Ley 37/2003, RD 1367/2007, "
        "RD 212/2002/Directiva 2000/14/CE, LPH art. 7 y ordenanzas municipales "
        "(Sevilla y Madrid); 9 fuentes oficiales. " + nota)

with open(RUTA, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(blog, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"OK: {len(blog['entradas'])} entradas, total={blog['meta']['total']}")
print(f"cuerpo={palabras} palabras | resumen={len(ENTRADA['resumen'])} car. | "
      f"internos={len(internos)}")
print("primera:", blog["entradas"][0]["slug"], blog["entradas"][0]["fecha"])
