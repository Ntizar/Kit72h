#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — añadir la entrada de blog 'mejor-estufa-sin-luz-apagon'.

Comparativa (Cluster C del mapa de keywords: «mejor estufa sin luz», pendiente).
Añade la entrada si no existe y la reemplaza si ya existe (re-ejecutable),
manteniendo el orden por fecha descendente y meta.total / meta.ultima_revision.
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUTA = RAIZ / "data" / "blog.json"
HOY = "2026-10-08"
SLUG = "mejor-estufa-sin-luz-apagon"

CUERPO = """
<p>En abril el apagón duró unas horas con dieciocho grados. En enero, el mismo corte a las tres de la mañana es otro asunto: sin calefacción una vivienda pierde grados en pocas horas, y el <strong>Plan Nacional de actuaciones preventivas por bajas temperaturas</strong> del Ministerio de Sanidad lo dice sin rodeos: el frío no solo provoca hipotermia, también «favorece los accidentes de tráfico y las caídas por placas de hielo, o los incendios e intoxicaciones por monóxido de carbono a partir de estufas de gas, braseros, etc.». Esa frase resume este artículo: elegir la <strong>mejor estufa para cuando se va la luz</strong> es cuestión de no convertir la sala de estar en un problema médico.</p>

<p>Comparo los cinco tipos que se compran en España —butano, pellets, eléctrica, catalítica y la opción sin estufa— con su coste por hora y con lo que necesitan para funcionar cuando la red está caída.</p>

<h2>Cuánto calor necesitas (y por qué calentar la casa entera es una trampa)</h2>

<p>Una estufa de 4.000 W no calienta un piso: calienta su habitación. La estrategia de un apagón es <strong>reducir el volumen</strong> —habitación pequeña, puerta cerrada, gente junta—. Regla orientativa para una estancia cerrada de 15-20 m²:</p>

<ul>
<li><strong>Bien aislada</strong> (paredes gruesas, ventana doble): bastan <strong>700-1.000 W</strong>.</li>
<li><strong>Mal aislada o con techos altos</strong>: pide <strong>1.500-2.000 W</strong>.</li>
<li>Por encima de 2.500-3.000 W en 15 m² es dinero quemado y más riesgo.</li>
</ul>

<p>Y una idea que pesa más que los vatios: <strong>la calefacción no sustituye a la ropa</strong>. Funciona ropa por capas + comida caliente + estufa baja; el desglose está en <a href="/blog/vestirse-por-capas-ropa-emergencia-frio/">vestirse por capas en una emergencia</a> y el plan de noche en <a href="/blog/temperatura-sin-electricidad/">cómo mantener la temperatura corporal sin electricidad</a>.</p>

<h2>Comparativa: los cinco tipos de estufa sin luz</h2>

<table>
<thead><tr><th>Tipo</th><th>Potencia / consumo</th><th>Coste orientativo por hora</th><th>¿Funciona sin red?</th></tr></thead>
<tbody>
<tr><td><strong>Estufa de butano con corte por falta de oxígeno</strong></td><td>4.200 W · bombona de 12,5 kg ≈ 30-40 h</td><td>0,40-0,50 €</td><td><strong>Sí</strong> ✅</td></tr>
<tr><td>Estufa de pellets</td><td>6-8 kW · 1,2-1,6 kg de pellets/h</td><td>0,70-0,95 €</td><td>Sí, pero necesita enchufe para agitador y ventilador</td></tr>
<tr><td>Calefactor eléctrico (convector o split)</td><td>2.000 W · 0,15-0,18 €/kWh</td><td>0,30-0,36 €</td><td><strong>No</strong> ❌ (solo con luz o generador)</td></tr>
<tr><td>Estufa catalítica de butano (sin llama)</td><td>2.400-3.000 W · bombona más pequeña</td><td>0,30-0,45 €</td><td>Sí ✅</td></tr>
<tr><td>Sin estufa: capas + peto eléctrico + manta de supervivencia</td><td>0 W de consumo</td><td>0 €</td><td><strong>Siempre</strong> ✅</td></tr>
</tbody>
</table>

<p>Precios orientativos para España: bombona de 12,5 kg a 15-18 €, pellet de palé a 0,45-0,60 €/kg y luz a 0,15-0,18 €/kWh. Sirven para comparar, no para firmar un contrato.</p>

<h2>Ganador por categoría</h2>

<ul>
<li><strong>Mejor para un apagón real: la estufa de butano con corte de oxígeno.</strong> No depende de nadie, calienta en minutos y una bombona aguanta varias noches: <a href="https://www.amazon.es/dp/B01M1NCHK8?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">4.200 W con corte automático por falta de oxígeno</a> (unos 84 €). El corte evita que la estufa se apague y siga quemando en una habitación cerrada.</li>
<li><strong>Mejor para una casa entera: pellets</strong>, si ya tienes la estufa y el palé. Calienta una planta entera y sale barato por hora, pero casi todas necesitan <strong>enchufe</strong> para el agitador, el ventilador y el encendido: sin luz, no arrancan.</li>
<li><strong>Mejor combo cocina + calor: el <a href="https://www.amazon.es/dp/B0CRN5KNCT?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">hornillo de butano portátil</a></strong> (20-45 €). No es una estufa, pero calienta agua y comida sin encender la cocina de casa: en tres días de corte amortiza su precio con la primera olla.</li>
<li><strong>Mejor presupuesto: la opción sin estufa.</strong> Una <a href="https://www.amazon.es/dp/B0CYDF32J3?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">manta térmica de supervivencia</a> (3-8 €), un <a href="https://www.amazon.es/s?k=peto+electrico+reutilizable&tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">peto eléctrico reutilizable</a> cuando vuelva la luz y un saco de abrigo aguantan la noche: menos que una bombona, y no puede fallar.</li>
</ul>

<p>¿Y la <strong>estufa catalítica</strong>? Es la versión más limpia del butano: quema sin llama visible y da un calor más suave, más agradable en una habitación pequeña. Vale la pena si quien pasa el día allí es una persona mayor o un niño; para un kit económico, el dinero está mejor en butano y detector de CO.</p>

<h2>El error grave: comprar una estufa eléctrica para el apagón</h2>

<p>Es el fallo más común: un convector de 2.000 W es barato, silencioso y no genera monóxido, por eso se vende tanto. El problema es que <strong>en un apagón no hay tensión</strong> y la estufa eléctrica se vuelve mueble. Para que funcione haría falta un generador de 1.500-2.000 W; lo que aguantan de verdad las baterías está en <a href="/blog/mejor-powerbank-emergencia-capacidad/">mejor powerbank para el apagón</a> y en <a href="/blog/generador-solar-emergencia-72h/">generador solar de emergencia</a>.</p>

<p>Dato del contexto español: según el <strong>Panel de Hogares de la CNMC</strong>, el 43,2 % de los hogares tiene contratada una potencia de entre 4 y 6 kW y gastó una media de 47,8 € al mes en electricidad. Con dos convector de 2.000 W enchufados ya estás en el límite de esa potencia; en un corte eso no es un problema de factura: es que no hay corriente que consumir.</p>

<h2>Monóxido de carbono: las cuatro reglas que salvan la noche</h2>

<p>El CO no huele, no pica y no avisa: los síntomas iniciales (dolor de cabeza, mareo, náuseas) se confunden con un resfriado, y los casos se concentran <strong>de octubre a marzo</strong>, justo cuando se encienden las estufas. Las recomendaciones oficiales son idénticas en todas las administraciones:</p>

<ul>
<li><strong>Ventilar dos veces al día, 15 minutos cada vez</strong>, aunque haga frío. Es la indicación literal del Plan de frío del Ministerio de Sanidad.</li>
<li><strong>Apagar las estufas eléctricas y de gas durante la noche.</strong> También del Plan de frío: dormir con la estufa encendida es la decisión que más se lamenta.</li>
<li><strong>No usar hornillos de camping, barbacoas, braseros ni el horno de la cocina</strong> dentro de la vivienda, y <strong>no tapar las rejillas</strong> de ventilación. Es la recomendación de los servicios 112 y de Protección Civil.</li>
<li><strong>Detector de monóxido a pilas en la pared</strong>, a un metro de la cama y lejos del techo. Cuesta entre 15 y 35 €: <a href="https://www.amazon.es/dp/B0D66LK5NP?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">ver detectores de CO</a>. Ninguna estufa de este artículo está completa sin él.</li>
</ul>

<h2>Checklist antes del primer frío</h2>

<ul>
<li>Estufa de butano con corte de oxígeno y <strong>dos bombonas de repuesto</strong>: la segunda se acaba siempre la primera noche.</li>
<li>Detector de CO con pilas nuevas y fecha de sustitución anotada.</li>
<li><a href="https://www.amazon.es/dp/B07PDRY2T2?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Cinta y plástico para sellar ventanas</a>: una habitación mal sellada pide el doble de potencia.</li>
<li>Mantas, <a href="https://www.amazon.es/dp/B0H37438Y1?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">saco de abrigo</a> y ropa térmica; <a href="https://www.amazon.es/dp/B0FZTLMXW9?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">encendedores y cerillas largas</a> fuera del alcance de los niños.</li>
<li>Comida y agua que no necesiten fuego: <a href="/blog/comer-sin-luz-menus-3-dias/">menús de tres días sin cocina</a>.</li>
</ul>

<p>Si el corte se alarga, la estufa es solo una pieza: la lista completa está en el <a href="/kit/kit-frio/">kit de frío e invierno</a> y en el <a href="/kit/kit-apagon/">kit apagón</a>.</p>
"""

ENTRADA = {
    "slug": SLUG,
    "titulo": "Mejor estufa sin luz: 5 tipos comparados para sobrevivir a un apagón de invierno",
    "fecha": HOY,
    "lectura": "7 min",
    "resumen": "Butano, pellets o eléctrica: qué estufa funciona cuando se va la luz, cuánto cuesta cada hora y por qué la eléctrica no sirve en un apagón.",
    "autor": "Redacción Kit72h",
    "fuente": [
        {"nombre": "Ministerio de Sanidad — Plan Nacional de actuaciones preventivas por bajas temperaturas (ventilar 15 min, apagar estufas de noche)",
         "url": "https://www.sanidad.gob.es/areas/sanidadAmbiental/riesgosAmbientales/frioExtremo/publicaciones/docs/Plan_Frio_25-26.pdf"},
        {"nombre": "Ministerio de Sanidad — Frío extremo: impacto en salud (incendios e intoxicaciones por CO)",
         "url": "https://www.sanidad.gob.es/areas/sanidadAmbiental/riesgosAmbientales/frioExtremo/impactoSalud.htm"},
        {"nombre": "Protección Civil — Recomendaciones generales por riesgo",
         "url": "https://www.proteccioncivil.es/gestion-riesgos/recomendaciones"},
        {"nombre": "Emergencias 112 (Castilla y León) — Intoxicación por monóxido de carbono: casos de octubre a marzo",
         "url": "https://112.jcyl.es/web/es/consejos-recomendaciones/intoxicacion-monoxido-carbono.html"},
        {"nombre": "CNMC — Panel de Hogares: potencia contratada y gasto medio en electricidad",
         "url": "https://www.cnmc.es/prensa/panel-hogares-servicios-electricidad-gas-20241205"}
    ],
    "cuerpo": CUERPO.strip(),
    "kits_relacionados": ["kit-frio", "kit-apagon", "kit-basico-72h"],
    "etiquetas": ["frío", "apagón", "calefacción", "comparativas", "escenarios", "preparacion"]
}

blog = json.loads(RUTA.read_text(encoding="utf-8"))
entradas = [e for e in blog["entradas"] if e.get("slug") != SLUG]
entradas.append(ENTRADA)
entradas.sort(key=lambda e: (e["fecha"], e["slug"]), reverse=True)
blog["entradas"] = entradas
blog["meta"]["total"] = len(entradas)
blog["meta"]["ultima_revision"] = HOY
blog["meta"]["actualizado"] = blog["meta"].get("actualizado", HOY)
nota = blog["meta"].get("nota_editor", "")
if SLUG not in nota:
    blog["meta"]["nota_editor"] = (f"{HOY}: nueva entrada '{SLUG}' (editor nocturno) "
                                   "\u2014 comparativa de 5 tipos de estufa sin luz, ganador por categoría, "
                                   "coste por hora y reglas de monóxido de carbono; 5 fuentes oficiales "
                                   "(Sanidad, Protección Civil, 112, CNMC). " + nota)

with open(RUTA, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(blog, f, ensure_ascii=False, indent=2)
    f.write("\n")

palabras = len(re.sub(r"<[^>]+>", " ", ENTRADA["cuerpo"]).split())
print(f"OK: {len(entradas)} entradas, total={blog['meta']['total']}")
print(f"palabras: {palabras} | resumen: {len(ENTRADA['resumen'])} caracteres")
print("primera:", entradas[0]["slug"], entradas[0]["fecha"])
