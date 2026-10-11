#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — añadir la entrada de blog 'baliza-v16-obligatoria-2026'.

Fila «señalización V16 obligatoria 2026» del mapa de keywords (Cluster D,
P2, estacional «V16: ya»): guía normativa + checklist de compra con enlaces
de afiliado. Re-ejecutable: si la entrada ya existe, la reemplaza.

Fuentes oficiales verificadas hoy (2026-10-11): nota de prensa de la DGT
(25-11-2025), listado oficial de dispositivos V-16 certificados, nota de la
AEPD sobre la baliza conectada y BOE (RGCV art. 130.3 / RD 159-2021).
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUTA = RAIZ / "data" / "blog.json"
HOY = "2026-10-11"
SLUG = "baliza-v16-obligatoria-2026"
TAG = "ntizar-21"


def dp(asin):
    return "https://www.amazon.es/dp/%s?tag=%s" % (asin, TAG)


AMZ = ' target="_blank" rel="sponsored nofollow noopener"'

CUERPO = """
<p>El 1 de enero de 2026 ya pasó y con él una costumbre de veintiséis años: <strong>los triángulos dejan de ser un medio válido para señalar un coche parado en carretera</strong>. Desde esa fecha el único dispositivo legal es la baliza luminosa V-16 conectada, y quien siga confiando en los triángulos del maletero va fuera de norma — la infracción es leve y se paga con 80 €.</p>

<p>No es un capricho tecnológico: la DGT cifra en <strong>unas 25 las personas que mueren cada año atropelladas en carretera después de haber bajado de su vehículo</strong>, muchas mientras colocaban precisamente los triángulos. Con la V-16 no sales del coche: se enciende desde dentro y, además de la luz, envía la posición del vehículo al resto de conductores. Aquí ves qué exige la norma, cómo funciona, dónde se coloca, la multa, los bulos y qué mirar antes de comprar.</p>

<h2>Qué exige la norma desde el 1 de enero de 2026</h2>

<p>La obligación está en el <strong>anexo XII del Reglamento General de Vehículos</strong> y entró en vigor el 1 de enero de 2026: desde esa fecha la V-16 conectada es «el único medio legal de señalización de vehículos inmovilizados», según la DGT.</p>

<ul>
<li><strong>Obligatoria para</strong> turismos, furgonetas, autobuses, vehículos mixtos, camiones y conjuntos no especiales. En motocicletas no es obligatoria, pero la DGT considera su uso «muy aconsejable».</li>
<li><strong>Los triángulos</strong> pueden seguir en la dotación, pero ya no sirven para señalizar una avería en carretera.</li>
<li><strong>En el extranjero</strong> vale en los países firmantes de la Convención de Viena (Portugal, Francia, Alemania, Italia…), que aceptan el dispositivo del país de matriculación.</li>
<li><strong>Y un apunte de actualidad:</strong> desde el 1 de octubre de 2026 las motos llevan además chaleco reflectante de alta visibilidad en su dotación obligatoria (RD 518/2026). La baliza no sustituye al chaleco.</li>
</ul>

<h2>Por qué se cambió: la cuenta que nadie quería hacer</h2>

<p>Señalizar con triángulo obliga a caminar <strong>mínimo 100 metros por la calzada</strong> con el tráfico pasando a tu lado; Reino Unido llegó a prohibirlos en vías de alta capacidad por ese motivo. La V-16 ataca los dos frentes: se activa sin salir del habitáculo y suma a la luz física una <em>visibilidad virtual</em> — la ubicación del vehículo parado aparece en navegadores, aplicaciones de movilidad y paneles de mensaje variable, para que quien circula frene antes de verte.</p>

<h2>Cómo funciona: sin móvil, sin app y sin cuota</h2>

<ul>
<li><strong>Autónoma:</strong> chip GPS y tarjeta SIM integrados y no extraíbles. Sin teléfono, sin aplicaciones, sin emparejamientos: se enciende y ya está.</li>
<li><strong>Conectividad incluida en el precio</strong>, con un mínimo de 12 años garantizado por norma y sin recargo de las operadoras.</li>
<li><strong>Al activarse</strong> envía la ubicación exacta a la plataforma DGT 3.0, que la reparte a navegadores, apps y paneles. Sin red de datos, la luz sigue funcionando.</li>
<li><strong>No llama al 112</strong> ni a tu aseguradora: solo señala y envía posición. La llamada la haces tú.</li>
<li><strong>Después activa</strong> el artículo 130.3 del Reglamento General de Circulación: si el vehículo no puede reanudar la marcha y hay sitio seguro fuera, se sale <strong>por el lado contrario al tráfico</strong>; si no es seguro, se permanece en el habitáculo con cinturón abrochado.</li>
</ul>

<table>
<thead><tr><th></th><th>Baliza V-16 conectada</th><th>Triángulo</th></tr></thead>
<tbody>
<tr><td>Estado desde 1/1/2026</td><td><strong>Único medio legal</strong></td><td>No sirve para señalizar</td></tr>
<tr><td>Colocación</td><td>Desde dentro, en la parte más alta</td><td>A pie, 100 m por la calzada</td></tr>
<tr><td>Aviso al resto</td><td>Luz + posición en DGT 3.0</td><td>Solo la luz reflejada</td></tr>
<tr><td>Riesgo para quien señala</td><td>Salta del coche solo si es seguro</td><td>Expuesto a la circulación</td></tr>
<tr><td>Precio orientativo</td><td>8-25 €</td><td>—</td></tr>
</tbody>
</table>

<h2>Dónde se guarda y cómo se coloca</h2>

<p>Tres reglas de la DGT que se olvidan siempre: se <strong>guarda cargada en la guantera</strong> o en otro lugar accesible del vehículo — no en el maletero cerrado ni en casa —; se <strong>enciende y coloca desde el interior</strong>, en la parte más alta del vehículo; y en autobuses o camiones, donde el techo no está al alcance, en la puerta del conductor. Actívala una vez en casa para comprobar que funciona y saber dónde va el día que haga falta.</p>

<h2>Antes de comprar: homologación sí o sí</h2>

<p>Hay <strong>más de doscientos modelos</strong> en el mercado y la DGT es tajante: solo vale el que aparece en su listado oficial de dispositivos certificados, todos certificados por <strong>IDIADA o LCOE</strong>, con el laboratorio y el número de certificado <strong>grabados en la tulipa</strong>.</p>

<ul>
<li><strong>Comprueba la lista de la DGT antes de pagar</strong>, no las fotos del anuncio: es la única comprobación que te ahorra la sorpresa.</li>
<li><strong>Desconfía de la suscripción:</strong> si te piden cuota mensual para «que se conecte», no es el modelo que pide la norma.</li>
<li><strong>Sin registrarte con tus datos:</strong> ni app ni alta a tu nombre; al comprar no se asocia la baliza a ninguna persona ni matrícula.</li>
<li><strong>Dónde comprarla:</strong> <a href="{baliza}"{AMZ}>baliza V-16 conectada homologada</a> (la del <a href="/kit/kit-coche/">kit de coche</a>), <a href="{buscar}"{AMZ}>comparar modelos de baliza V-16 homologada</a> o, si todavía no lo tienes, <a href="{chaleco}"{AMZ}>chaleco reflectante</a>.</li>
</ul>

<h2>La multa: infracción leve y 80 €</h2>

<p>No llevar la baliza V-16 es una <strong>infracción leve sancionada con 80 €</strong>, la misma cantidad que se aplicaba antes a quien circulaba sin triángulos. Es la parte fácil: el coste real de ir sin ella es estar a pie en un arcén de noche esperando a que alguien te vea. Por eso el <a href="/kit/kit-coche/">kit de coche</a> la marca como imprescindible: cuesta como dos cenas y se compra una vez.</p>

<h2>Tres bulos que circulan por redes</h2>

<ol>
<li><strong>«Rastrea tus movimientos».</strong> Solo transmite cuando está activada, y lo que envía es la ubicación más un identificador técnico del propio dispositivo: la AEPD confirma que no hay registro que vincule la baliza con la identidad de quien la usa, ni con la matrícula, y la norma prohíbe funcionalidades adicionales.</li>
<li><strong>«Hay que registrarla con el DNI o instalar una app».</strong> Falso: no necesita aplicación, ni teléfono, ni datos personales al comprarla.</li>
<li><strong>«Llama sola al 112».</strong> También falso. Si hay heridos o la situación es grave, llamas tú al 112 y, si procede, a la asistencia de tu aseguradora.</li>
</ol>

<h2>Checklist de diez minutos para esta semana</h2>

<ol>
<li>Comprueba que tu baliza figura en el <strong>listado oficial de la DGT</strong> y que el número de certificado está grabado en la tulipa.</li>
<li><strong>Cárgala y déjala en la guantera</strong>; pruébala una vez y vuelve a guardarla cargada.</li>
<li>Ten el <strong>chaleco a mano</strong> — no debajo de la maleta en el maletero — y el móvil cargado.</li>
<li>Acordad en casa <strong>quién sale y por qué lado</strong>, o si simplemente os quedáis dentro con el cinturón abrochado.</li>
<li>Revisa el resto del kit del coche: botiquín, linterna, agua y <a href="/blog/mejor-powerbank-emergencia-capacidad/">powerbank</a>, lo que mantiene viva esa llamada al 112.</li>
</ol>

<p>La baliza resuelve la señalización, no el resto del escenario. El contexto está en las <a href="/blog/apagon-lecciones-28a/">lecciones del apagón del 28 de abril</a> y la lista completa de lo obligatorio y lo conveniente en el <a href="/blog/coche-kit-emergencia-2026/">kit de coche para 2026</a>. La base — agua, luz y comida para 72 horas — sigue en el <a href="/kit/kit-basico-72h/">kit básico de 72 horas</a>.</p>
"""

ENTRADA = {
    "slug": SLUG,
    "titulo": "Baliza V16 obligatoria 2026: norma, multa de 80 € y cómo elegirla",
    "fecha": HOY,
    "lectura": "6 min",
    "resumen": ("Desde el 1 de enero de 2026 la baliza V16 conectada es el único medio "
                "legal para señalizar un coche parado: qué exige la DGT y cómo elegirla "
                "homologada."),
    "autor": "Redacción Kit72h",
    "fuente": [
        {"nombre": "DGT — Nota de prensa: la baliza V-16, único medio legal desde el 1/1/2026",
         "url": "https://www.dgt.es/comunicacion/notas-de-prensa/20251125-dgt-recuerda-la-obligacion-de-disponer-de-la-baliza-v-16-para-senalizar-averias-y-accidentes-en-carretera/"},
        {"nombre": "DGT — Dispositivos de preseñalización V-16: marcas y modelos certificados",
         "url": "https://www.dgt.es/muevete-con-seguridad/tecnologia-e-innovacion-en-carretera/Dispositivos-de-presenalizacion-V16/"},
        {"nombre": "AEPD — Nota informativa sobre la baliza V-16 conectada (datos y privacidad)",
         "url": "https://www.aepd.es/prensa-y-comunicacion/notas-de-prensa/nota-informativa-sobre-baliza-v16-conectada"},
        {"nombre": "BOE — Real Decreto 1428/2003, Reglamento General de Circulación (art. 130.3)",
         "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2003-21851"},
        {"nombre": "BOE — Real Decreto 159/2021, servicios de auxilio en vías públicas",
         "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2021-4194"},
    ],
    "cuerpo": None,
    "kits_relacionados": ["kit-coche", "kit-basico-72h", "kit-apagon"],
    "etiquetas": ["coche", "v16", "baliza", "senalizacion", "dgt", "normativa",
                  "preparacion", "comparativas"],
}

ENTRADA["cuerpo"] = CUERPO.strip().format(
    baliza=dp("B0FHBDDBNT"),
    buscar="https://www.amazon.es/s?k=baliza+v16+homologada&tag=%s" % TAG,
    chaleco=dp("B0CWDNN3MY"),
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
                                   "— baliza V-16 obligatoria desde el 1/1/2026: anexo XII "
                                   "del RGVI, 25 atropellos/año, multa leve de 80 €, "
                                   "homologación IDIADA/LCOE, 3 bulos y checklist; "
                                   "5 fuentes oficiales (DGT, AEPD, BOE). " + nota)

with open(RUTA, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(blog, f, ensure_ascii=False, indent=2)
    f.write("\n")

palabras = len(re.sub(r"<[^>]+>", " ", ENTRADA["cuerpo"]).split())
print("OK: %d entradas, total=%d" % (len(entradas), blog["meta"]["total"]))
print("palabras: %d | resumen: %d caracteres | titulo: %d caracteres"
      % (palabras, len(ENTRADA["resumen"]), len(ENTRADA["titulo"])))
print("primera:", entradas[0]["slug"], entradas[0]["fecha"])
