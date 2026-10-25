#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — añadir la entrada de blog 'mejor-deshumidificador-inundaciones-humedad'.

Comparativa (Cluster C del mapa de keywords: «mejor deshumidificador inundaciones»,
pendiente, estacional: media). Añade la entrada si no existe y la reemplaza si ya
existe (re-ejecutable), manteniendo el orden por fecha descendente y meta.total /
meta.ultima_revision.
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUTA = RAIZ / "data" / "blog.json"
HOY = "2026-10-25"
SLUG = "mejor-deshumidificador-inundaciones-humedad"

CUERPO = """<p>La humedad oculta es la que más destruye después de una inundación o de una temporada de lluvia. No necesitas que entre el agua en casa para que los muros, la ropa o los muebles de aglomérado se echen a perder: con un 70% de humedad relativa basta para que aparezcan los primeros mohos, y a partir de 75% el hongo Stachybotrys —el de las toxinas— empieza a proliferar. En España, el INMET lo tiene claro: la humedad relativa ideal en interiores oscila entre el 40 y el 60%. Supera el 65% y empiezan los problemas.</p>

<p>El deshumidificador es la herramienta que controla esa humedad cuando no hay calefacción suficiente para secar las paredes o cuando la lluvia ha dejado una capa de agua que no llega a secar con un trapo. Y en un escenario de apagón post-inundación, cuando la red falla y no puedes encender el ventilador del coche para ventilar el salón, es la diferencia entre recuperar las cosas o enterrarlas.</p>

<p>Comparo los tres tipos disponibles en España —compresor, desecante y membrana— con su consumo, su capacidad real y su utilidad en emergencia.</p>

<h2>Cuatro tipos, un objetivo: el 50% de humedad</h2>

<table>
<thead><tr><th>Tipo</th><th>¿Cómo funciona?</th><th>Capacidad (L/día)</th><th>Consumo</th><th>¿Sirve en frío?</th></tr></thead>
<tbody>
<tr><td><strong>Compresor (el más efectivo)</strong></td><td>Enfría el aire para condensar la humedad como un frigorífico al revés</td><td>10-50 L/día</td><td>200-400 W</td><td>Sí, pero pierde eficiencia por debajo de 15 °C</td></tr>
<tr><td><strong>Desecante (sales o silicato)</strong></td><td>Absorbe el agua en un material higroscópico que se recalienta para secarlo</td><td>5-25 L/día</td><td>200-500 W</td><td><strong>Sí, funciona bien a cualquier temperatura</strong> ✅</td></tr>
<tr><td><strong>Membrana (peltier)</strong></td><td>Termoeléctrico mini: como el deshumidificador de coche</td><td>1-5 L/día</td><td>30-70 W</td><td>Sí, pero capacidad muy limitada</td></tr>
<tr><td><strong>Sin deshumidificador: ventilación cruzada + bórax</strong></td><td>Abrir ventanas (si no llueve), sacos de sílice o bórax</td><td>Variable</td><td>0 W</td><td><strong>Sí</strong> ✅ (solo si el exterior está más seco)</td></tr>
</tbody>
</table>

<p>Precios orientativos para España: compresor de 20 L/día entre 150-300 €, desecante entre 100-200 €, y peltier entre 30-60 €. Los de compresor rinden más pero consumen más: si el apagón se alarga, un compresor de 300 W sobre un generador pequeño puede vaciar el depósito de combustible antes que la estufa.</p>

<h2>Ganador por categoría</h2>

<p><strong>Mayor capacidad:</strong> el compresor de 30-50 L/día. Ideal para un sótano inundado o un piso tras la DANA. Marcas como De'Longhi, Pro Breeze o Mila ofrecen modelos de 20-30 L/día a precio razonable. <a href="https://www.amazon.es/s?k=deshumidificador+compresor+30l&tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Ver deshumidificadores compresor en Amazon</a>.</p>

<p><strong>Mejor para frío:</strong> el desecante de sal. A 5 °C sigue sacando 10 L/día mientras el compresor baja a 3-4 L. Si vives en zonas de montaña o inviernos duros, es la opción más fiable cuando no hay calefacción. <a href="https://www.amazon.es/s?k=deshumidificador+desecante+sal&tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Ver deshumidificadores desecantes en Amazon</a>.</p>

<p><strong>Mejor relación tamaño/rendimiento:</strong> el peltier de 3-5 L para armarios o cuartos pequeños. No sirve para un salón inundado, pero es suficiente para evitar que el armario se llenen de moho tras una temporada de lluvia intensa. <a href="https://www.amazon.es/s?k=deshumidificador+electrico+pequeno&tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Ver deshumidificadores pequeños en Amazon</a>.</p>

<p><strong>Gratis:</strong> la ventilación cruzada con bórax (cristato de bórax, no bórax puro). Un saquito de bórax en cada armario absorbe 1-2 L/día de forma pasiva. No es un deshumidificador, pero en un apagón es la opción que no necesita enchufe. El bórax se compra en ferreterías por 2-5 € el kilo y no caduca.</p>

<h2>Cuándo comprarlo y cómo usarlo</h2>

<p>Hay dos momentos para un deshumidificador en una emergencia:</p>

<ol>
<li><strong>Prevención (antes):</strong> si vives en zona de lluvia frecuente o piso bajo, tener un compresor de 10-15 L/día en el trastero o debajo de la cocina es como tener un paraguas cerrado que no estorba. Conéctalo en temporada de lluvia y mantén la humedad entre 45-55%. El consumo es bajo: un compresor de 15 L gasta unas 250 W-h/día ≈ 0,04 €/día.</li>
<li><strong>Recuperación (después de inundación):</strong> tras la DANA o una riada, los muros mojados tardan semanas en secar solos. Un compresor de 20-30 L secará una vivienda de 70 m² en 3-5 días si se mantiene cerrado (ventanas cerradas, puerta de la habitación sellada con plástico). Sin él, puede tardar 2-3 semanas y aparecer moho en 48-72 h.</li>
</ol>

<p><strong>Regla de los tres días:</strong> si después de una inundación no puedes secar la vivienda en 72 horas, necesitarás un deshumidificador de capacidad media o alta (20+ L/día). Los materiales de aglomerado (MDF, aglomerado) que se mojan y no se secan a tiempo se hinchan y pierden estructura para siempre: una mesa de MDF que se moja no vuelve a ser igual aunque se seque.</p>

<h2>Errores frecuentes</h2>

<ul>
<li><strong>Dejar las ventanas abiertas:</strong> un deshumidificador no funciona si el exterior está más húmedo. En una tormenta o justo después, el aire exterior puede tener 95% de humedad; abrir la ventana es como echar leña al fuego. Cierra todo y deja que la máquina trabaje.</li>
<li><strong>Comprar un peltier para un salón:</strong> el peltier de 3 L solo sirve para un cajón o un armario pequeño. Si la superficie a secar supera 30 m², pide un compresor de al menos 15 L/día.</li>
<li><strong>No vaciar el depósito:</strong> un compresor de 20 L en un piso muy húmedo puede llenarse en 6-8 horas. Si se llena y no lo vacías, la máquina se para y la humedad sube de golpe. Ponle un drenaje continuo o recuerda vaciarlo cada 4-6 horas.</li>
<li><strong>Creer que ventila:</strong> un deshumidificador no renueva el aire: solo lo seca. Si hay moho visible, necesitas limpieza con lejía diluida (1 parte de lejía por 10 de agua) antes de secar. El deshumidificador evita que vuelva a aparecer, pero no elimina lo que ya crece.</li>
</ul>

<h2>Kit de deshumedecimiento básico</h2>

<ul>
<li><strong>Deshumidificador de compresor 20 L/día:</strong> <a href="https://www.amazon.es/s?k=deshumidificador+compresor+20l+recogida+agua&tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Ver modelos en Amazon</a> — el caballo de batalla, para un piso normal de 70-90 m².</li>
<li><strong>Sacos de bórax o sílice:</strong> para armarios y zonas pequeñas donde no llega el compresor. <a href="https://www.amazon.es/s?k=saquitos+deshumidificantes+armario&tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Ver sacos deshumidificantes en Amazon</a>.</li>
<li><strong>Higrómetro digital:</strong> para medir la humedad real, no adivinarla. Unos 8-12 € y se cuelga en la pared. <a href="https://www.amazon.es/s?k=higrometro+digital+pare&tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Ver higrómetros digitales en Amazon</a>.</li>
<li><strong>Lejía concentrada:</strong> para limpiar moho visible antes de secar. 1 parte de lejía por 10 de agua. <a href="https://www.amazon.es/s?k=lejia+concentrada+limpieza&tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Ver lejía concentrada en Amazon</a>.</li>
<li><strong>Plástico de burbujas o film industrial:</strong> para sellar puertas y ventanas durante el secado. <a href="https://www.amazon.es/s?k=plastico+burbujas+gran+formato&tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Ver plástico de burbujas en Amazon</a>.</li>
</ul>

<p>La humedad es la razón número uno por la que los seguros rechazan claims post-inundación: si el moho lleva más de 30 días creciendo, se considera «deterioro progresivo» y no «daño repentino». Por eso, actuar en las primeras 72 horas no es una sugerencia, es una obligación contractual.</p>

<p>Para la lista completa de productos tras una inundación, consulta el <a href="/kit/kit-dana/">kit DANA e inundación</a> y el <a href="/kit/kit-hogar/">kit de hogar</a>.</p>"""

ENTRADA = {
    "slug": SLUG,
    "titulo": "Mejor deshumidificador para inundaciones y humedad: 4 tipos comparados",
    "fecha": HOY,
    "lectura": "7 min",
    "resumen": "Compresor, desecante o peltier: qué deshumidificador sirve tras una inundación o lluvia intensa, cuánto gasta cada tipo y la regla de los 3 días.",
    "autor": "Redacción Kit72h",
    "fuente": [
        {"nombre": "INMET — Indicadores de tiempo en España: humedad relativa",
         "url": "https://www.aemet.es/es/eltiempo/observacion/indicadoresmetereologicos"},
        {"nombre": "OMS — Guidelines for indoor relative humidity",
         "url": "https://www.who.int/publications/m/item/9789289042012"},
        {"nombre": "Protección Civil — Recomendaciones post-inundación",
         "url": "https://www.proteccioncivil.es/gestion-riesgos/recomendaciones"},
        {"nombre": "Ministerio de Sanidad — Calidad del aire interior: humedad y moho",
         "url": "https://www.sanidad.gob.es/areas/sanidadAmbiental/calidadAire/documents/guias_calidad_aire_interior.htm"}
    ],
    "cuerpo": CUERPO.strip(),
    "kits_relacionados": ["kit-dana", "kit-hogar", "kit-basico-72h"],
    "etiquetas": ["inundación", "humedad", "comparativas", "DANA", "productos", "preparacion"]
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
                                   " comparativa de 4 tipos de deshumidificador (compresor, desecante, peltier, sin máquina), "
                                   "ganador por categoría, regla de 3 días post-inundación; 4 fuentes oficiales "
                                   "(INMET, OMS, Protección Civil, Sanidad). " + nota)

with open(RUTA, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(blog, f, ensure_ascii=False, indent=2)
    f.write("\n")

palabras = len(re.sub(r"<[^>]+>", " ", ENTRADA["cuerpo"]).split())
print(f"OK: {len(entradas)} entradas, total={blog['meta']['total']}")
print(f"palabras: {palabras} | resumen: {len(ENTRADA['resumen'])} caracteres")
print("primera:", entradas[0]["slug"], entradas[0]["fecha"])