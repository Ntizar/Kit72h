#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — añadir la entrada de blog 'mejores-conservas-larga-duracion'.

Comparativa (Cluster C del mapa de keywords: «mejores conservas larga duración»,
pendiente P2). Re-ejecutable: si la entrada ya existe, la reemplaza.

ASIN verificados hoy (2026-10-10) con fetch directo de amazon.es: HTTP 200 +
buybox activo. Sin precios exactos en la web (política de afiliados): solo
cualificaciones propias.
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUTA = RAIZ / "data" / "blog.json"
HOY = "2026-10-10"
SLUG = "mejores-conservas-larga-duracion"
TAG = "ntizar-21"


def dp(asin):
    return "https://www.amazon.es/dp/%s?tag=%s" % (asin, TAG)


AMZ = ' target="_blank" rel="sponsored nofollow noopener"'

CUERPO = """
<p>Se va la luz a las 21:40 y lo primero que haces es abrir la nevera para mirar cuánto queda. A las doce horas el congelador ya está tibio y, a las treinta y seis, la pregunta ya no es qué apetece sino <strong>qué se puede comer todavía</strong>. Ahí vale más una conserva bien elegida que cualquier gadget: comida que aguanta meses o años sin frío, sin luz y sin que tú hagas nada.</p>

<p>Ese es el criterio oficial: la <strong>Estrategia de Preparación de la Unión Europea</strong> pide <strong>72 horas de autonomía</strong> por hogar y <strong>Protección Civil</strong> recomienda alimentos no perecederos y agua para tres días. En España no falta comida, falta plan: el <strong>Informe del Desperdicio Alimentario en España 2024 (MAPA)</strong> cifra en <strong>1.125 millones de kilos o litros</strong> lo que tiramos al año, con el <strong>97,5 %</strong> dentro de los hogares y unos 24 kilos por persona. Compramos comida que acaba en la basura mientras la reserva de emergencia no existe.</p>

<p>Comparo <strong>nueve conservas de larga duración</strong> que se encuentran en cualquier supermercado o en Amazon España: cuánto aguantan cerradas, para qué sirve de verdad cada una y su punto débil.</p>

<h2>Consumo preferente no es caducidad: la fecha que decide si tiras o no</h2>

<p>La <strong>AESAN</strong> dedica una campaña entera a separar ambos conceptos y el <strong>Reglamento (UE) 1169/2011</strong> los regula. Confundirlos es la principal causa de tirar una reserva todavía buena:</p>

<ul>
<li><strong>Fecha de consumo preferente</strong> — conservas, legumbres, arroz, pasta, harina, aceite, miel. Indica hasta cuándo el alimento conserva su calidad. <strong>Pasada esa fecha sigue siendo seguro</strong>: puede perder textura o sabor, pero no se tira por la fecha sola.</li>
<li><strong>Fecha de caducidad</strong> — carne y pescado frescos, ciertos lácteos, platos preparados. Esa no se estira: no se consume después de la fecha.</li>
<li><strong>En un apagón la nevera es lo primero que se pierde.</strong> Lo fresco y lo de caducidad cae en 24-48 horas; la conserva es lo último en salir del plan.</li>
</ul>

<p>Truco: rotula la fecha de cada bote al guardarlo, ten el abrelatas en el mismo cajón y aplica la regla <strong>FIFO</strong> —lo que entra, delante; lo que ya está, se come primero—. Así la reserva se renueva con tu compra normal en vez de caducar en un armario.</p>

<h2>Las nueve mejores conservas de larga duración, comparadas</h2>

<p>Duraciones <strong>orientativas para envases cerrados</strong> en sitio seco, fresco y oscuro: quien fija la duración real es la fecha impresa en el envase.</p>

<table>
<thead><tr><th>Producto</th><th>Duración orientativa</th><th>Ideal para</th></tr></thead>
<tbody>
<tr><td><a href="{mre}"{AMZ}>MRE-9, ración de emergencia 24 × 500 g</a></td><td>20 años cerrada (caducidad declarada en la ficha)</td><td>El cajón que solo se toca en una emergencia real: plato completo sin cocina</td></tr>
<tr><td><a href="{trek}"{AMZ}>TREK'N EAT macarrones con queso, liofilizado 140 g</a></td><td>3 a 4 años (vida útil del fabricante)</td><td>Comida caliente sin nevera y con peso mínimo: se prepara con agua caliente</td></tr>
<tr><td><a href="{lenteja}"{AMZ}>Luengo lenteja cocida en frasco, 570 g</a></td><td>2 a 3 años sin abrir</td><td>Plato de verdad sin fuego: ya cocinada, se come fría con pan</td></tr>
<tr><td><a href="{atun}"{AMZ}>Calvo atún claro en aceite de oliva, 8 × 65 g</a></td><td>2 a 4 años sin abrir</td><td>Proteínas diarias que además se rotan en la compra de siempre</td></tr>
<tr><td><a href="{sardina}"{AMZ}>Calvo sardinas en aceite de oliva, 120 g</a></td><td>2 a 4 años sin abrir</td><td>Cena sin abrir nada más: solo abrelatas, sin agua y sin fuego</td></tr>
<tr><td><a href="{melon}"{AMZ}>Mitades de melocotón en almíbar extra, 480 g</a></td><td>1 a 2 años sin abrir</td><td>Azúcar rápido y moral alta, sobre todo para niños con poca hambre</td></tr>
<tr><td><a href="{frutos}"{AMZ}>Mezcla de frutos secos naturales, 1 kg</a></td><td>6 a 12 meses sin abrir (la grasa se rancía con calor)</td><td>Calorías ligeras: sin agua, sin fuego y sin nada</td></tr>
<tr><td><a href="{miel}"{AMZ}>Miel de mil flores cruda, 1 kg</a></td><td>Años: no se echa a perder (cristalizar no la estropea)</td><td>Energía, endulzar el café y labios y garganta agrietados</td></tr>
<tr><td><a href="{leche}"{AMZ}>Leche entera UHT en brik, 6 × 1 L</a></td><td>Meses sin abrir (fecha en el brik)</td><td>La más usada y la que más rápido caduca: se compra para rotar</td></tr>
</tbody>
</table>

<p>Enlaces directos a la ficha de cada producto con nuestro identificador de afiliado. Sin precios en la página: cambian a diario y aquí damos criterio, no etiqueta.</p>

<h2>Ganador por categoría</h2>

<ul>
<li><strong>Para el cajón de 20 años: la <a href="{mre}"{AMZ}>ración MRE-9</a>.</strong> Única de la lista con caducidad declarada de dos décadas: se compra una vez y no se toca hasta que hace falta.</li>
<li><strong>Para la despensa que se usa todos los días: <a href="{atun}"{AMZ}>atún</a> y <a href="{sardina}"{AMZ}>sardinas</a>.</strong> Rinden en la emergencia y rinden en marzo: la mejor reserva es la que se come antes de caducar.</li>
<li><strong>Para comer sin fuego ni agua: <a href="{sardina}"{AMZ}>sardinas</a> con <a href="{frutos}"{AMZ}>frutos secos</a>.</strong> Si el plan depende de encender algo, no es un plan.</li>
<li><strong>Para espacio y peso: la <a href="{trek}"{AMZ}>ración liofilizada</a>.</strong> 140 g por plato: cabe en la mochila de evacuación y no pesa en el armario.</li>
<li><strong>Para la cocina sin nevera: el <a href="{lenteja}"{AMZ}>frasco de legumbres</a>.</strong> Ya cocinadas, sin gas ni remojo, frías o templadas.</li>
</ul>

<h2>Seis reglas de guardado que se deciden antes del apagón</h2>

<ol>
<li><strong>Seco, fresco y oscuro.</strong> Nunca sobre el suelo del garaje ni junto a la caldera: la humedad abolla las latas y el calor rancía la grasa del pescado y de los frutos secos.</li>
<li><strong>Fuera del sol.</strong> Una lata a la luz todo un verano sabe a cartón.</li>
<li><strong>Envase dañado, fuera.</strong> Abollada, hinchada, con óxido o con la tapa saltada se tira sin discutir, aunque la fecha sea buena.</li>
<li><strong>Abierto, nevera y a consumo.</strong> Con ambiente cálido, horas; nunca un bote abierto «para mañana» en la encimera.</li>
<li><strong>Abrelatas manual en el mismo cajón.</strong> Sin luz no hay enchufe y sin abrelatas no hay cena: es el objeto más barato del kit.</li>
<li><strong>Prueba previa.</strong> Una noche sin luz usando lo que ya tienes guardado enseña más que cualquier lista: descubrirás que falta el abrelatas, no el atún.</li>
</ol>

<h2>Cinco errores que dejan la despensa igual que el primer día</h2>

<ol>
<li><strong>Comprar «comida de emergencia» especial.</strong> Lo que no comes en tu vida normal tampoco lo comerás en una emergencia, y además caduca antes: la reserva se monta con lo que ya comes.</li>
<li><strong>Guardarlo en el trastero o el garaje.</strong> Un verano español en un trastero es el peor enemigo de una conserva.</li>
<li><strong>No mirar fechas al hacer la compra.</strong> Dos latas idénticas, dos fechas distintas: llévate la que llegue más lejos y anótala en el cajón.</li>
<li><strong>Cocinar solo si hay luz.</strong> Si todo el plan necesita la vitro, en un apagón no hay plan: mezcla productos listos con productos que solo necesitan agua caliente.</li>
<li><strong>No saber cuánto hay.</strong> Un inventario en la puerta de la nevera, con fechas, evita vaciar el armario entero «por si acaso».</li>
</ol>

<p>Con esto cubres el flanco que ninguna linterna arregla. El montaje completo está en <a href="/blog/almacenar-agua-comida-casa/">cómo almacenar agua y comida en casa</a> y en la <a href="/blog/alimentos-emergencia-caducidad-rotacion/">rotación de alimentos por fecha</a>; los menús sin luz, en <a href="/blog/comer-sin-luz-menus-3-dias/">comer sin luz: menús para 3 días</a>; y qué hacer con lo que se estropea al cortarse el frío, en <a href="/blog/conservar-comida-sin-nevera-ni-frio/">conservar comida sin nevera</a>. El conjunto encaja en el <a href="/kit/kit-basico-72h/">kit básico de 72 horas</a> y en el <a href="/kit/kit-hogar/">kit de hogar o confinamiento</a>.</p>
"""

ENTRADA = {
    "slug": SLUG,
    "titulo": "Mejores conservas de larga duración para emergencias (2026)",
    "fecha": HOY,
    "lectura": "7 min",
    "resumen": ("Mejores conservas de larga duración para emergencias: 9 productos comparados, "
                "qué fecha mirar en el envase y los 5 errores habituales de la despensa."),
    "autor": "Redacción Kit72h",
    "fuente": [
        {"nombre": "AESAN — Fecha de consumo preferente y fecha de caducidad (campaña)",
         "url": "https://www.aesan.gob.es/actualidad/campanyas-seguridad-alimentaria/fecha_consumo"},
        {"nombre": "EUR-Lex — Reglamento (UE) 1169/2011, art. 24 (indicaciones de duración)",
         "url": "https://eur-lex.europa.eu/eli/reg/2011/1169/oj"},
        {"nombre": "MAPA — Desperdicio alimentario en España 2024: 1.125 millones de kilos",
         "url": "https://www.mapa.gob.es/es/prensa/ultimas-noticias/detalle_noticias/el-desperdicio-alimentario-en-espa-a-se-ha-reducido-el-4-4---en-2024--hasta-los-1.125-millones-de-kilos/6b13413a-ce02-436a-820a-c1e0f8387cb5"},
        {"nombre": "Protección Civil — Recomendaciones generales por riesgo",
         "url": "https://www.proteccioncivil.es/gestion-riesgos/recomendaciones"},
        {"nombre": "Comisión Europea — Estrategia de la Unión de la Preparación (72 horas de autonomía)",
         "url": "https://commission.europa.eu/topics/preparedness_es"},
    ],
    "cuerpo": None,
    "kits_relacionados": ["kit-basico-72h", "kit-hogar", "kit-apagon"],
    "etiquetas": ["comida", "conservas", "larga duracion", "comparativas",
                  "despensa", "apagon", "preparacion"],
}

ENTRADA["cuerpo"] = CUERPO.strip().format(
    mre=dp("B0CKJ1G7GD"),
    trek=dp("B0CJ2S3N7N"),
    lenteja=dp("B009PLRV2A"),
    atun=dp("B0D8L2KTHN"),
    sardina=dp("B0083D3UEE"),
    melon=dp("B00XA0SU5O"),
    frutos=dp("B0H9STC996"),
    miel=dp("B09NNL9Z4G"),
    leche=dp("B01LZIMTSC"),
    AMZ=AMZ,
)

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
                                   "— comparativa de 9 conservas de larga duración con "
                                   "ganador por categoría, consumo preferente vs caducidad "
                                   "(AESAN/1169-2011) y datos MAPA 2024; 5 fuentes oficiales. " + nota)

with open(RUTA, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(blog, f, ensure_ascii=False, indent=2)
    f.write("\n")

palabras = len(re.sub(r"<[^>]+>", " ", ENTRADA["cuerpo"]).split())
print("OK: %d entradas, total=%d" % (len(entradas), blog["meta"]["total"]))
print("palabras: %d | resumen: %d caracteres | titulo: %d caracteres"
      % (palabras, len(ENTRADA["resumen"]), len(ENTRADA["titulo"])))
print("primera:", entradas[0]["slug"], entradas[0]["fecha"])
