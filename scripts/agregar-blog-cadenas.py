#!/usr/bin/env python3
"""Kit72h — añadir/actualizar la entrada de blog 'mejores-cadenas-para-la-nieve'.

Re-ejecutable: si la entrada ya existe la REEMPLAZA (no falla), mantiene el
orden por fecha descendente y recalcula meta.total / meta.ultima_revision.

Sustituye a agregar-blog-mental.py (entrada ya publicada → «La entrada ya
existe»). El mapa de keywords no tiene filas `pendiente`, así que el editor
nocturno toma la fila de Cluster C (60 % comparativas/deals) que falta por
cubrir: «mejores cadenas para la nieve» — estacional (invierno, DGT), alta
intención de compra, y ninguna página del sitio compara cadenas, calcetines
ni neumáticos de invierno. Fuentes: DGT (3 páginas), BOE y AEMET, verificadas
por HTTP 200 en la noche del 2026-10-20.
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUTA = RAIZ / "data" / "blog.json"
HOY = "2026-10-20"
SLUG = "mejores-cadenas-para-la-nieve"

CUERPO = """
<p>Cada invierno pasa lo mismo: llega el aviso de nieve, la sierra se llena y los conductores que solo bajan a la gasolinera descubren que no tienen cadenas, que no saben ponerlas o que las que compraron hace tres años ya no valen para el coche actual. Elegir bien evita quedarse tirado en un puerto con visibilidad escasa —y también llegar tarde a donde ibas—, y no es caro: entre una cadena y otra hay veinte o treinta euros.</p>

<p>La norma española es sencilla y conviene repetirla: <strong>no hay fechas fijas</strong>. La obligación de llevar cadenas (o neumáticos de invierno que los sustituyan) la marca la señalización de cada tramo y el estado de la vía que informa la DGT, no un calendario. Antes de salir, lo oficial es consultar el estado del tráfico en dgt.es o mapamovilidad.dgt.es, llamar al <strong>011</strong> o escuchar los boletines de radio; y si hay aviso de AEMET para la zona, mejor posponer el plan. Lo demás —qué comprar, cómo ponerlas y cómo guardarlas— está en esta comparativa.</p>

<h2>1. Qué exige la DGT, en cuatro puntos</h2>

<ul>
<li><strong>La señal manda, no el calendario.</strong> Donde está puesta la señal de obligación de cadenas no se continúa sin ellas (ni sin otro dispositivo autorizado). El catálogo oficial de señales se actualizó con el Real Decreto 465/2025, así que en algunos mapas y manuales aparecen códigos distintos para la misma señal: fíjate en el panel del tramo, no en la letra de la norma.</li>
<li><strong>Los neumáticos de invierno solo sustituyen a las cadenas si están marcados.</strong> La DGT admite circular sin cadenas —cuando la señal lo exige— con neumáticos marcados con el símbolo de la montaña de tres picos (3PMSF); la marca M+S sola no vale para sustituir. Están pensados para temperaturas por debajo de unos 7 °C.</li>
<li><strong>Velocidades y colocación:</strong> máximo 30 km/h con cadenas metálicas y 50 km/h con las de tela; siempre en el <strong>eje motriz</strong> (las dos ruedas de ese eje) y, si el coche es a las cuatro ruedas, delante.</li>
<li><strong>Conducir con cadenas no es conducir igual:</strong> nada de acelerones ni frenazos bruscos, y sobre calzada sin nieve la frenada es más larga — quítalas en cuanto termine el tramo.</li>
</ul>

<h2>2. Los cinco tipos comparados</h2>

<p>Precios orientativos en Amazon España. Cada enlace abre la búsqueda del tipo, así que ves el precio del día, no el de cuando se escribió esto. Y antes de pagar, mira la talla de tus neumáticos (algo como 205/55 R16, en el flanco del neumático o en la puerta del conductor): una cadena que no es tu medida no es una cadena, es un peso en el maletero.</p>

<table>
<thead><tr><th>Tipo</th><th>Cuándo compensa</th><th>Límite</th><th>Precio orientativo</th></tr></thead>
<tbody>
<tr><td><a href="https://www.amazon.es/s?k=cadenas+nieve+coche&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Cadenas metálicas de eslabón ↗</a></td><td>La referencia: válidas en cualquier tramo con señal, duran años</td><td>30 km/h</td><td>30-80 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=cadenas+nieve+enganche+rapido&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Cadenas con sujeción rápida (tensor) ↗</a></td><td>Se ponen en la mitad de tiempo y con las manos frías: mismas normas, montaje más cómodo</td><td>30 km/h</td><td>50-130 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=calcetines+nieve+coche&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Calcetines textiles ↗</a></td><td>Se ponen en un minuto y sin mancharse; valen donde la vía admite dispositivos textiles</td><td>50 km/h</td><td>20-55 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=neumatico+invierno+3pmsf&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Neumáticos de invierno 3PMSF ↗</a></td><td>Zona nevada o salidas de fin de semana cada semana: sustituyen a las cadenas donde la señal lo exige</td><td>Según neumático</td><td>60-120 € por rueda</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=neumatico+all+season&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Neumáticos todo tiempo (all-season) ↗</a></td><td>Sin cambio de temporada; en nieve repetida rinden menos que un invierno de verdad</td><td>Según neumático</td><td>70-140 € por rueda</td></tr>
</tbody>
</table>

<h2>3. Ganadores por caso</h2>

<ul>
<li><strong>La mayoría de conductores (una salida a la sierra de vez en cuando):</strong> cadenas metálicas <strong>de tu talla</strong>, las básicas bien ajustadas. Es lo que todas las vías aceptan y lo más barato que funciona de verdad.</li>
<li><strong>Vives en zona nevada o bajas varios fines de semana seguidos:</strong> neumáticos de invierno 3PMSF. Con ellos cumples donde la señal exige cadenas, y no llevas el resto del año con un juego de cadenas ocupando el maletero.</li>
<li><strong>Manos frías, prisa o quien nunca las ha puesto:</strong> calcetines textiles en los tramos que admiten tejido (son los más rápidos de poner) — y si no sabes si tu ruta los admite, metálicas.</li>
<li><strong>Todo terreno y caminos sin asfaltar:</strong> metálicas con tensor, siempre; guantes y frontal en la misma bolsa que ellas.</li>
<li><strong>Presupuesto ajustado:</strong> mejor una cadena básica de tu talla que una «barata» de otra medida. El año siguiente le sumas los guantes y la linterna.</li>
</ul>

<h2>4. Cómo ponerlas, según la propia DGT</h2>

<ul>
<li><strong>Parar en un sitio seguro</strong>, fuera de la calzada y sin cuesta: mejor subir el coche a un aparcamiento ancho que ponerte en un arcén con poca visibilidad.</li>
<li><strong>Eje motriz:</strong> delante si el coche es a las cuatro ruedas; atrás si es tracción trasera. Las dos ruedas de ese eje, nunca «una de cada lado».</li>
<li><strong>Montaje:</strong> aro rígido por detrás de la rueda, centrado, anillo exterior, tensor y el sobrante enganchado para que no golpee el paso de rueda.</li>
<li><strong>Marcha suave</strong>, sin acelerones ni frenazos, y al terminar el tramo de nieve se quitan: sobre asfalto limpio estorban y desgastan.</li>
<li><strong>Al guardar:</strong> lavarlas y secarlas. La sal de la carretera las corroe por dentro, y una cadena oxidada se rompe justo cuando más la necesitas.</li>
</ul>

<h2>5. Los cinco errores que más se repiten</h2>

<ul>
<li><strong>No probarlas antes.</strong> El primer montaje en un aparcamiento con las manos templadas son dos minutos; en un puerto con nieve y sin guantes, veinte. Hazlo una vez en casa.</li>
<li><strong>Comprar por precio sin mirar la talla.</strong> La cadena más barata que no abrocha en tus ruedas no es una ganga: es un viaje a la gasolinera para no salir del aparcamiento.</li>
<li><strong>Llevar calcetines a un tramo que solo admite metálicas.</strong> Si el panel lo especifica o tu ruta habitual lo exige, metálicas: son las que valen en todos los casos.</li>
<li><strong>Guardarlas mojadas o con elásticos rotos.</strong> Revisión de dos minutos al terminar la temporada: limpias, secas y en una bolsa sin agujeros.</li>
<li><strong>Fiarse solo del GPS.</strong> El estado de la vía se consulta en dgt.es y mapamovilidad.dgt.es, en el 011 y en los boletines de radio; si hay restricción o aviso de AEMET, se pospone el viaje, no se fuerza.</li>
</ul>

<h2>6. El kit del maletero, en seis objetos</h2>

<p>Además de las cadenas de tu talla: guantes de trabajo (los de invierno se empapan), una linterna con pilas de repuesto, una toalla vieja para las manos y el barro, agua y algo de comer por si te quedas tirado un par de horas, y la manta o el abrigo extra para los pasajeros. Todo eso vive en el <a href="/kit/kit-coche/">kit de coche</a> junto a la baliza V-16, el chaleco y el botiquín; el reparto completo está en <a href="/blog/coche-kit-emergencia-2026/">qué llevar en el coche de emergencia</a>. Y si el aviso llega con la casa sin preparar, lo básico para pasar la nevada sin luz lo tienes en <a href="/blog/nevada-en-casa-que-necesito/">nevada en casa: qué necesitas</a>; el abrigo, paso a paso, en <a href="/blog/vestirse-por-capas-ropa-emergencia-frio/">vestirse por capas</a>.</p>
"""

ENTRADA = {
    "slug": SLUG,
    "titulo": "Mejores cadenas para la nieve 2026: 5 opciones comparadas y cuándo son obligatorias",
    "fecha": HOY,
    "lectura": "7 min",
    "resumen": "Metálicas, calcetines o neumáticos de invierno: 5 opciones comparadas por precio y uso, con lo que exige la DGT y los errores que más se repiten.",
    "autor": "Redacción Kit72h",
    "fuente": [
        {"nombre": "DGT — Recomendaciones de tráfico (información antes de salir, 011, elementos imprescindibles)",
         "url": "https://www.dgt.es/conoce-el-estado-del-trafico/recomendaciones-de-trafico"},
        {"nombre": "DGT — Con frío, ¡no patine! (cadenas metálicas o de tela, límites de velocidad, neumáticos 3PMSF)",
         "url": "https://revista.dgt.es/es/reportajes/2023/12DICIEMBRE/SUP_INVIERNO/1219-N268-INVIERNO-nieve_hielo.shtml"},
        {"nombre": "DGT — Cómo colocar correctamente las cadenas (eje motriz, montaje, lavado y secado)",
         "url": "https://revista.dgt.es/es/sabia-que/dudas/2015/0205poner-cadenas.shtml"},
        {"nombre": "BOE — Real Decreto 465/2025, de 10 de junio, de señalización de tráfico (catálogo oficial de señales)",
         "url": "https://www.boe.es/eli/es/rd/2025/06/10/465"},
        {"nombre": "AEMET — Avisos meteorológicos (estado y avisos por zona antes de salir)",
         "url": "https://www.aemet.es/es/eltiempo/prediccion/avisos"},
    ],
    "cuerpo": CUERPO.strip(),
    "kits_relacionados": ["kit-coche", "kit-frio", "kit-basico-72h"],
    "etiquetas": ["cadenas para la nieve", "conducción en invierno", "comparativa",
                  "kit de coche", "DGT", "neumáticos de invierno"],
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
assert 'rel="sponsored nofollow noopener"' in cuerpo, "sin rel sponsored"
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
        "comparativa estacional de cadenas para la nieve: cinco tipos (metálicas, "
        "tensor rápido, calcetines, 3PMSF y all-season) con límites de velocidad y "
        "ganadores por caso; norma DGT (la señal manda, no el calendario; 3PMSF "
        "sustituyen a cadenas; 30/50 km/h; eje motriz) y 5 errores frecuentes; "
        "5 fuentes oficiales verificadas (DGT ×3, BOE RD 465/2025, AEMET avisos). " + nota)

with open(RUTA, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(blog, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"OK: {len(blog['entradas'])} entradas, total={blog['meta']['total']}")
print(f"cuerpo={palabras} palabras | resumen={len(ENTRADA['resumen'])} car. | "
      f"internos={len(internos)} | amazon={len(re.findall('amazon.es', cuerpo))}")
print("primera:", blog["entradas"][0]["slug"], blog["entradas"][0]["fecha"])
