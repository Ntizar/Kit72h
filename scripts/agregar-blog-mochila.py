#!/usr/bin/env python3
"""Kit72h — añadir/actualizar la entrada de blog 'mejor-mochila-emergencia-evacuacion'.

Re-ejecutable: si la entrada ya existe la REEMPLAZA (no falla), mantiene el
orden por fecha descendente y recalcula meta.total / meta.ultima_revision.

Sustituye a agregar-blog-mental.py (entrada ya publicada → «La entrada ya
existe»). El mapa de keywords no tiene filas `pendiente`: todas están cubiertas
o hechas, así que el editor nocturno toma la fila de Cluster C (60 %
comparativas/deals) que falta por cubrir: «mejor mochila de emergencia /
evacuación» — el kit de evacuación ya está montado en /kit/kit-evacuacion/, pero
ninguna página del sitio compara mochilas por litros, peso ni uso real.
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUTA = RAIZ / "data" / "blog.json"
HOY = "2026-10-19"
SLUG = "mejor-mochila-emergencia-evacuacion"

CUERPO = """
<p>A las 23:40 llega la orden: el agua entra por la calle de abajo o el humo se ve desde el pueblo de al lado. Tienes minutos, no horas. Esa es la única razón de ser de la <strong>mochila de evacuación</strong>: preparada de antemano, en el mismo sitio desde hace semanas, lista para coger de un tirón mientras el resto de la casa se levanta.</p>

<p>El marco oficial es europeo: la <strong>Estrategia de la Unión de la Preparación</strong> pide directrices para que la población sea autosuficiente como mínimo <strong>72 horas</strong> mientras llega la ayuda, y Cruz Roja Española lo baja a lo práctico: una mochila fácil de llevar, de peso razonable y accesible, cuyo contenido se revisa periódicamente. De qué llenarla lo ves en <a href="/kit/kit-evacuacion/">el kit de evacuación</a>; aquí va la pregunta que más se deja a medias —<strong>qué mochila comprar</strong>—, con seis tipos comparados por litros, precio y uso real.</p>

<h2>1. Cuatro decisiones antes de mirar precios</h2>

<ul>
<li><strong>Capacidad por horas, no por ganas.</strong> 18-25 litros para 24 horas o para la oficina; 30-40 litros para dos o tres días con abrigo, agua y comida; 45-60 litros solo si hay que salir con lo de varias personas. La referencia de 72 horas empuja a un adulto que va a andar hacia los <strong>35-45 litros</strong>.</li>
<li><strong>Peso cargado: entre el 10 % y el 15 % de tu peso corporal.</strong> Es la misma regla que se aplica a las mochilas escolares: 70 kg → 7-10 kg en la espalda. Más que eso, a los veinte minutos vas más lento que el que lleva menos, y en una evacuación el tiempo es exactamente lo que no sobra.</li>
<li><strong>Sistema de espalda que reparta.</strong> Tirantes anchos y acolchados, panel que respire y, por encima de todo, <strong>cinturón de cadera</strong>: una mochila sin cinturón cargada a más de 10 kg convierte la zona lumbar en el punto débil. Lo pesado pegado a la espalda y a la altura de los hombros; lo blando y voluminoso, al fondo; lo que necesites de camino (agua, linterna, documentación), a mano.</li>
<li><strong>Agua y luz fuera, no dentro.</strong> Bolsillo exterior o malla para la botella y anclaje para la linterna: pararte a destapar la mochila en mitad de un pasillo lleno de gente no es lo mismo que beber andando.</li>
</ul>

<h2>2. Los seis tipos comparados</h2>

<p>Precios orientativos en Amazon España. Cada enlace abre la búsqueda del tipo, así que ves el precio del día, no el de cuando se escribió esto.</p>

<table>
<thead><tr><th>Tipo</th><th>Litros</th><th>Cuándo compensa</th><th>Precio orientativo</th></tr></thead>
<tbody>
<tr><td><a href="https://www.amazon.es/s?k=mochila+trekking+45l&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Mochila de trekking de 40-50 L ↗</a></td><td>40-50</td><td>El adulto que va a andar: la mejor capacidad por kilo, cinturón de cadera de serie</td><td>35-90 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=mochila+tactica+40l&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Mochila táctica MOLLE de 35-45 L ↗</a></td><td>35-45</td><td>Kit fijo y organizado: anclas externas para fundas, botiquín o frontales</td><td>30-75 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=mochila+evacuacion+emergencia+72h&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Mochila de evacuación ya montada ↗</a></td><td>30-40</td><td>Llega montada, pero controlas menos el contenido: hay que revisarla igual</td><td>50-120 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=mochila+25l+impermeable&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Mochila de día de 18-25 L ↗</a></td><td>18-25</td><td>24 horas, oficina, coche y ruta corta: lo más barata y lo que más se usa también a diario</td><td>18-45 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=mochila+infantil+emergencia&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Mochila infantil de 15-20 L ↗</a></td><td>15-20</td><td>Cada niño la suya, con su ropa y su juego: cargar a los mayores solo con lo suyo ya es bastante</td><td>15-35 €</td></tr>
<tr><td><a href="https://www.amazon.es/s?k=mochila+con+ruedas+capota&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Mochila con ruedas o carrito ↗</a></td><td>40-80</td><td>Personas mayores, movilidad reducida o carga pesada (agua, garrafas): se rueda, no se carga</td><td>40-110 €</td></tr>
</tbody>
</table>

<h2>3. Ganadores por caso</h2>

<ul>
<li><strong>Evacuación andando a pie (DANA, incendio, orden de salir):</strong> trekking de 40-50 L con cinturón de cadera. Es la que aguanta el peso sin castigarte: <a href="https://www.amazon.es/s?k=mochila+trekking+45l&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">mochilas de trekking de 45 L ↗</a>.</li>
<li><strong>Kit preparado para coger y marchar:</strong> táctica de 35-45 L con anclas externas, si te organizas por bolsillos: <a href="https://www.amazon.es/s?k=mochila+tactica+40l&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">mochilas tácticas MOLLE ↗</a>. Útil sobre todo si la guardas ya montada en el armario de la entrada.</li>
<li><strong>Casa con mayores o problemas de espalda:</strong> la de ruedas, sin discusión. Mejor empujar que arrastrar a una persona con una mochila de 12 kg.</li>
<li><strong>Familia con niños:</strong> una mochila grande de adultos <strong>más</strong> una pequeña por niño. <a href="/blog/bebes-ninos-emergencia-checklist-edades/">Bebés y niños en una emergencia</a> marca qué lleva cada edad.</li>
<li><strong>Oficina, coche y ruta de un día:</strong> la de 18-25 L, la única que vas a usar de verdad el resto del año: <a href="https://www.amazon.es/s?k=mochila+25l+impermeable&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">mochilas de día impermeables ↗</a>.</li>
<li><strong>Si llevas mascotas:</strong> la de la familia más una bolsa aparte con agua, correa, documentación veterinaria y pienso: <a href="/blog/mascotas-plan-emergencia/">plan de emergencia con perros y gatos</a>.</li>
</ul>

<h2>4. Qué va dentro: el reparto en cinco huecos</h2>

<p>La mochila es el envoltorio; el contenido, media lista del kit. Lo que no puede faltar en ninguno de los seis tipos:</p>

<table>
<thead><tr><th>Hueco</th><th>Qué lleva</th><th>Referencia</th></tr></thead>
<tbody>
<tr><td>Documentación</td><td>Copias en bolsa estanca: DNI, tarjeta sanitaria, pólizas, contactos en papel</td><td><a href="/blog/carpeta-de-emergencia-documentos/">carpeta de emergencia</a></td></tr>
<tr><td>Agua y comida</td><td>1,5-3 L por persona y barritas, frutos secos o conservas que no necesiten cocina</td><td><a href="/blog/agua-cuanta-y-como/">cuánta agua necesitas</a></td></tr>
<tr><td>Luz y batería</td><td>Linterna frontal, pilas de repuesto y powerbank cargado</td><td><a href="/blog/mejor-linterna-emergencia-72h/">mejor linterna</a> · <a href="/blog/mejor-powerbank-emergencia-capacidad/">mejor powerbank</a></td></tr>
<tr><td>Salud y abrigo</td><td>Botiquín, medicación crónica de 5-7 días y ropa por capas</td><td><a href="/blog/vestirse-por-capas-ropa-emergencia-frio/">vestirse por capas</a></td></tr>
<tr><td>Lo que decide</td><td>Móvil cargado, radio a pilas y el plan familiar escrito (punto de encuentro y a quién llamar)</td><td><a href="/blog/plan-familiar-de-emergencia/">plan familiar de emergencia</a></td></tr>
</tbody>
</table>

<p>Si aún no tienes montada la base, el orden es el de siempre: primero <a href="/blog/como-montar-tu-kit-72h/">montar tu kit de 72 horas</a>, después elegir la mochila que lo lleve. Al revés sale más caro.</p>

<h2>5. Los cinco errores que más se repiten</h2>

<ul>
<li><strong>Sobrecargarla «por si acaso».</strong> Pasar del 15 % de tu peso corporal convierte una evacuación a pie en un traslado a urgencias: la mochila que no puedes cargar contigo no es tu mochila.</li>
<li><strong>Comprar la más barata sin probarla.</strong> Sin cinturón de cadera y con tirantes finos, la diferencia se nota al minuto cinco, no en la foto del producto.</li>
<li><strong>Que la mochila sea cosa de una sola persona.</strong> Si la guarda y la revisa solo un individuo, cuando ese alguien no está en casa la mochila deja de existir: el sitio y el contenido tienen que conocerlos todos.</li>
<li><strong>No revisarla nunca.</strong> Pilas agotadas, documentación caducada, ropa de verano en pleno invierno. Cruz Roja insiste en la revisión periódica: cada seis meses, diez minutos, con calendario.</li>
<li><strong>Olvidar lo que no cabe en la mochila.</strong> El coche, la ruta de salida, el agua de la casa y los documentos originales se preparan aparte; la mochila solo lleva lo imprescindible para moverte.</li>
</ul>

<h2>6. La prueba de los diez minutos</h2>

<p>El único test que vale: pon cronómetro, coge la mochila y sal a la calle cerrando la puerta. Diez minutos con la casa dormida es un buen objetivo. Si te faltó algo, apúntalo y cómpralo; si te sobraron cinco minutos, quita peso. Después, déjala en el mismo sitio —visible, etiquetada y al alcance de todos— y ensaya con la familia: quién la coge, quién recoge los documentos, quién avisa a los abuelos. Lo que se ensaya antes se hace después con la cabeza fría, y ahí se gana la emergencia.</p>
"""

ENTRADA = {
    "slug": SLUG,
    "titulo": "Mejor mochila de emergencia 2026: 6 mochilas de evacuación comparadas",
    "fecha": HOY,
    "lectura": "7 min",
    "resumen": "¿Qué mochila coges si hay que salir de casa en diez minutos? 6 tipos comparados por litros, peso y precio, ganadores por caso y qué va dentro (2026).",
    "autor": "Redacción Kit72h",
    "fuente": [
        {"nombre": "Comisión Europea — Estrategia de la Unión de la Preparación (autosuficiencia mínima de 72 horas)",
         "url": "https://commission.europa.eu/topics/preparedness_es"},
        {"nombre": "Cruz Roja Española — Preparación ante desastres (mochila de emergencia accesible y revisión periódica)",
         "url": "https://www2.cruzroja.es/preparacionantedesastres"},
        {"nombre": "Cruz Roja Española — Qué hacer si las autoridades ordenan evacuar tu casa",
         "url": "https://www2.cruzroja.es/web/ahora/-/todo-lo-que-debes-saber-si-las-autoridades-ordenan-evacuar-tu-casa"},
        {"nombre": "Protección Civil — Recomendaciones generales por riesgo",
         "url": "https://www.proteccioncivil.es/gestion-riesgos/recomendaciones"},
        {"nombre": "Protección Civil — Red de Alerta Nacional y alertas a móviles (ES-Alert)",
         "url": "https://www.proteccioncivil.es/coordinacion/redes/ran/public-warning-system"},
    ],
    "cuerpo": CUERPO.strip(),
    "kits_relacionados": ["kit-evacuacion", "kit-basico-72h", "kit-dana", "kit-hogar"],
    "etiquetas": ["mochila", "evacuación", "mochila de emergencia", "comparativa",
                  "preparación", "DANA", "autoprotección"],
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
        "comparativa de mochilas de emergencia/evacuación: seis tipos por litros y "
        "precio, reglas de capacidad y peso cargado (10-15 % del peso corporal), "
        "ganadores por caso, reparto del contenido en cinco huecos y 5 errores; "
        "5 fuentes oficiales (Comisión Europea 72 h, Cruz Roja preparación ante "
        "desastres y evacuación, Protección Civil recomendaciones y ES-Alert). " + nota)

with open(RUTA, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(blog, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"OK: {len(blog['entradas'])} entradas, total={blog['meta']['total']}")
print(f"cuerpo={palabras} palabras | resumen={len(ENTRADA['resumen'])} car. | "
      f"internos={len(internos)} | amazon={len(re.findall('amazon.es', cuerpo))}")
print("primera:", blog["entradas"][0]["slug"], blog["entradas"][0]["fecha"])
