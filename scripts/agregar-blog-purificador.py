#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — añadir la entrada de blog 'mejor-purificador-agua-emergencia'.

Comparativa (Cluster C del mapa de keywords: «mejor purificador de agua
emergencia», pendiente P2). Añade la entrada si no existe y la reemplaza si
ya existe (re-ejecutable), manteniendo el orden por fecha descendente y
meta.total / meta.ultima_revision.

Los ASIN de los productos están VERIFICADOS hoy (ficha amazon.es/dp/ con
buybox activo, comprobado con la misma rutina de scripts/buscar-amazon.py).
Las pastillas potabilizadoras llevan enlace de búsqueda: sin ficha
verificada, no se inventa un /dp/.
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUTA = RAIZ / "data" / "blog.json"
HOY = "2026-10-09"
SLUG = "mejor-purificador-agua-emergencia"
TAG = "ntizar-21"


def dp(asin):
    return f"https://www.amazon.es/dp/{asin}?tag={TAG}"


def busq(texto):
    return ("https://www.amazon.es/s?k=" + texto.replace(" ", "+") +
            f"&tag={TAG}")


AMZ = ' target="_blank" rel="sponsored nofollow noopener"'

CUERPO = """
<p>Después de la DANA, varios municipios se quedaron días sin agua potable mientras en las tiendas se agotaban las garrafas. Y en un apagón invernal el problema no es solo la luz: en tres días una vivienda llega a las <strong>72 horas de autonomía</strong> que recomienda la <strong>Estrategia de Preparación de la Unión Europea</strong>, y decides si bebes de la llave, del río o de la botella. Ahí entra el <strong>purificador de agua de emergencia</strong>: no es para sobrevivir en la selva, es para que cualquier agua turbia se pueda beber sin acabar en urgencias.</p>

<p>Comparo siete opciones reales de Amazon España —filtros personales, filtros de gravedad para casa, botella con filtro y pastillas— con su precio, su uso ideal y, sobre todo, con lo que cada una <em>no</em> hace. En agua de emergencia el error no se nota hoy: se nota a las 36 horas.</p>

<h2>Qué exige la normativa española y qué no resuelve un filtro</h2>

<p>En España el agua de grifo está regulada por el <strong>Real Decreto 3/2023</strong>, que fija los criterios técnico-sanitarios y el control de calidad: si sale del grifo, es apta. El problema aparece cuando se corta el suministro o cuando sube la turbidez tras un temporal. Ahí manda <strong>Protección Civil</strong>: agua para tres días y, ante dudas sobre la calidad, hervir o desinfectar. Su guía del Plan Familiar de Emergencias incluye expresamente «pastillas potabilizadoras de agua» y «agua (para 3 días)».</p>

<p>Y aquí viene la parte que casi nadie explica al comprar:</p>

<ul>
<li><strong>Los filtros de membrana (0,1-0,2 micras, según fabricante) retiran bacterias, parásitos y la mayor parte de los microplásticos.</strong> No retiran virus, que son mucho más pequeños, ni disolventes, pesticidos ni hidrocarburos.</li>
<li><strong>Las pastillas de cloro o de dióxido de cloro sí cubren virus</strong>, pero dejan sabor y necesitan un tiempo de contacto (minutos) antes de beber, y tampoco eliminan turbidez ni productos químicos.</li>
<li><strong>Hervir es lo más seguro y lo más tosco:</strong> mata todo lo vivo, pero no quita tierra, no quita metal pesado y consume gas o pilas justo cuando no las tienes.</li>
<li><strong>Ningún método arregla agua con productos químicos</strong> (una fuga, un vertido, gasóleo en la ría). Esa agua no se potabiliza: se descarta.</li>
</ul>

<p>La conclusión: <strong>un filtro solo nunca basta</strong>. El combo real es filtro + pastillas + posibilidad de hervir. Y no olvides la reserva —los tres litros por persona y día—, montada paso a paso en <a href="/blog/agua-cuanta-y-como/">cuánta agua necesitas y cómo guardarla</a>.</p>

<h2>Comparativa: los siete purificadores de agua para emergencia</h2>

<table>
<thead><tr><th>Producto</th><th>Tipo</th><th>Precio orientativo</th><th>Ideal para</th></tr></thead>
<tbody>
<tr><td><a href="{lifestraw}"{AMZ}>LifeStraw filtro personal</a></td><td>Pajita / filtro personal</td><td>26,95 €</td><td>Mochila, rutas y «el que no tiene nada»</td></tr>
<tr><td><a href="{peak}"{AMZ}>LifeStraw Peak Series Solo</a></td><td>Filtro personal compacto</td><td>33,34 €</td><td>Uso recurrente, más caudal que una pajita básica</td></tr>
<tr><td><a href="{membarato}"{AMZ}>Membrane Solutions 0,1 µm</a></td><td>Filtro de bombeo/pajita</td><td>18,99 €</td><td>Presupuesto ajustado (el más barato)</td></tr>
<tr><td><a href="{waterflow}"{AMZ}>Waterflow 3 fases</a></td><td>Filtro con carbón</td><td>24,97 €</td><td>Mejor relación calidad-precio</td></tr>
<tr><td><a href="{gravedad}"{AMZ}>Waterdrop con bolsa de gravedad</a></td><td>Filtro de gravedad</td><td>27,00 €</td><td>Casa: llenar, colgar y servir a varios</td></tr>
<tr><td><a href="{ws02}"{AMZ}>Membrane Solutions WS02</a></td><td>Filtro extraíble de mayor caudal</td><td>52,99 €</td><td>Autocaravana, casa de campo, equipo familiar</td></tr>
<tr><td><a href="{botella}"{AMZ}>LifeStraw Go con botella</a></td><td>Botella con filtro integrado</td><td>67,48 €</td><td>Un solo objeto que ya va lleno en la mochila</td></tr>
<tr><td><a href="{pastillas}"{AMZ}>Pastillas potabilizadoras</a></td><td>Desinfección química</td><td>9-25 €</td><td>Cubrir virus, que ningún filtro de esta lista caza</td></tr>
</tbody>
</table>

<p>Precios verificados hoy en la ficha de Amazon.es: cambian a diario, tómalos como orden de magnitud. Los enlaces van directos a la ficha con nuestro identificador de afiliado.</p>

<h2>Ganador por categoría (según el escenario que te toque)</h2>

<ul>
<li><strong>Mejor para la mochila de evacuación: el <a href="{lifestraw}"{AMZ}>LifeStraw</a>.</strong> Cabe en un bolsillo, no necesita recambios y funciona sin aprender nada: es el que compras si solo compras uno.</li>
<li><strong>Mejor para casa: el <a href="{gravedad}"{AMZ}>filtro de gravedad con bolsa</a>.</strong> La llenas, la cuelgas y goterea sobre un recipiente: da de beber a varios sin agacharse a un charco. El más cómodo con niños y con mayores.</li>
<li><strong>Mejor presupuesto: el <a href="{membarato}"{AMZ}>Membrane Solutions de 18,99 €</a>.</strong> Cumple sin gastar más que una caja de conservas.</li>
<li><strong>Mejor relación calidad-precio: el <a href="{waterflow}"{AMZ}>Waterflow de 3 fases</a>.</strong> Con carbón activo mejora olor y sabor: el agua de río o de aljibe, sin carbón, se bebe mal y acaba tirándose.</li>
<li><strong>Mejor complemento obligatorio: las <a href="{pastillas}"{AMZ}>pastillas potabilizadoras</a>.</strong> Baratas, ligeras y de fecha larga: lo único de esta lista que cubre virus. Sin ellas, el filtro solo deja un falso «agua segura».</li>
</ul>

<h2>Tres usos reales en un hogar español</h2>

<ul>
<li><strong>Tras una DANA o una inundación.</strong> Sale turbia o con aviso de hervir: filtro para beber y cloro para las superficies. El orden de limpieza está en <a href="/blog/volver-a-casa-tras-inundacion/">volver a casa después de una inundación</a>.</li>
<li><strong>Apagón de varios días.</strong> La cisterna y el termo siguen llenos, pero la bomba no funciona. Rellenar bidones de la bañera y filtrarlos es más rápido que subir garrafas. El guion completo está en <a href="/kit/kit-apagon/">el kit de apagón</a>.</li>
<li><strong>Agua de campo o de ruta.</strong> Río, manantial o depósito de autocaravana: el mismo filtro sirve el fin de semana. Que es justo lo que falta en la mayoría de kits: equipo que nunca se estrena.</li>
</ul>

<h2>Los cinco errores que dejan el agua igual que antes</h2>

<ol>
<li><strong>Filtrar agua muy turbia directamente.</strong> La tierra tapa el membrana y lo deja sin caudal en minutos. Primero se decanta o se prefiltra con un paño limpio, y después se filtra.</li>
<li><strong>Usar el filtro para agua con químicos</strong> (gasóleo, disolvente, aljibe tratado con productos de jardinería). Nada de esta lista lo retira: se descarta el agua.</li>
<li><strong>Comprar pastillas y no mirar la caducidad.</strong> Las pastillas pierden potencia; guárdalas secas, en su tarro cerrado, y apunta la fecha en el tarro con rotulador. Igual que con los <a href="/blog/alimentos-emergencia-caducidad-rotacion/">alimentos de la despensa</a>: lo caducado no es reserva.</li>
<li><strong>Filtrar y beber sin dejar el tiempo de contacto</strong> si además usas pastillas: con agua fría hacen falta varios minutos. Apúntalo en la etiqueta del bidón, para que no lo decida el que tiene más sed.</li>
<li><strong>No probarlo antes.</strong> Un equipo que nunca se ha usado se usa mal. Filtra un vaso de agua en casa y mira cuánto tarda: en el apagón ya sabrás lo que hace.</li>
</ol>

<h2>Qué comprar hoy (y qué dejar preparado)</h2>

<p>Lista mínima y barata: un <a href="{waterflow}"{AMZ}>filtro de tres fases</a> para la casa, un <a href="{lifestraw}"{AMZ}>filtro personal</a> por quien salga de casa, una tira de <a href="{pastillas}"{AMZ}>pastillas potabilizadoras</a> y una olla con tapa para hervir. Con eso cubres bacterias, virus y la vía de emergencia sin electricidad. El conjunto encaja en el <a href="/kit/kit-basico-72h/">kit básico de 72 horas</a> y, si vives en zona de riada, en el <a href="/kit/kit-dana/">kit de DANA e inundación</a>.</p>

<p>Y una idea que ahorra dinero: <strong>la reserva de agua sigue siendo lo primero</strong>. Un purificador no sustituye a los bidones, los amplía. Regla de los tres litros por persona y día, envases y rotación en <a href="/blog/almacenar-agua-comida-casa/">cómo almacenar agua y comida en casa</a>.</p>
"""

ENTRADA = {
    "slug": SLUG,
    "titulo": "Mejor purificador de agua para emergencias (2026): 7 filtros comparados",
    "fecha": HOY,
    "lectura": "8 min",
    "resumen": "Mejor purificador de agua para emergencias: 7 filtros comparados por precio y uso, qué elimina cada método y los 5 errores que dejan el agua igual.",
    "autor": "Redacción Kit72h",
    "fuente": [
        {"nombre": "BOE — Real Decreto 3/2023: criterios técnico-sanitarios del agua de consumo",
         "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2023-628"},
        {"nombre": "Ministerio de Sanidad — Legislación sobre aguas de consumo humano",
         "url": "https://www.sanidad.gob.es/areas/sanidadAmbiental/calidadAguas/aguasConsumoHumano/legislacion/home.htm"},
        {"nombre": "Protección Civil — Recomendaciones generales por riesgo",
         "url": "https://www.proteccioncivil.es/gestion-riesgos/recomendaciones"},
        {"nombre": "Protección Civil — Plan Familiar de Emergencias (agua para 3 días y pastillas potabilizadoras)",
         "url": "https://www.proteccioncivil.es/catalogo/guiastecnicas/mujer-reduccion-desastres/presentaciones/p12.pdf"},
        {"nombre": "Comisión Europea — Estrategia de la Unión de la Preparación (72 horas de autonomía)",
         "url": "https://commission.europa.eu/topics/preparedness_es"},
        {"nombre": "OMS — Directrices sobre la calidad del agua potable",
         "url": "https://www.who.int/publications/i/item/9789241548151"},
    ],
    "cuerpo": None,  # se rellena abajo
    "kits_relacionados": ["kit-basico-72h", "kit-dana", "kit-apagon"],
    "etiquetas": ["agua", "potabilizador", "purificador", "comparativas",
                  "apagon", "dana", "preparacion"],
}

ENTRADA["cuerpo"] = CUERPO.strip().format(
    lifestraw=dp("B006QF3TW4"),
    peak=dp("B0C62WZ2WY"),
    membarato=dp("B073R8F3HP"),
    waterflow=dp("B0F3D422BK"),
    gravedad=dp("B086QNLBB4"),
    ws02=dp("B08MQMC8PL"),
    botella=dp("B0BY39KS2D"),
    pastillas=busq("pastillas potabilizadoras de agua"),
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
                                   "— comparativa de 7 purificadores de agua verificados "
                                   "y ganador por categoría, qué elimina cada método "
                                   "(filtro/pastillas/hervido) y 5 errores; 6 fuentes "
                                   "oficiales (BOE RD 3/2023, Sanidad, Protección Civil, "
                                   "Comisión Europea, OMS). " + nota)

with open(RUTA, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(blog, f, ensure_ascii=False, indent=2)
    f.write("\n")

palabras = len(re.sub(r"<[^>]+>", " ", ENTRADA["cuerpo"]).split())
print(f"OK: {len(entradas)} entradas, total={blog['meta']['total']}")
print(f"palabras: {palabras} | resumen: {len(ENTRADA['resumen'])} caracteres")
print("primera:", entradas[0]["slug"], entradas[0]["fecha"])
