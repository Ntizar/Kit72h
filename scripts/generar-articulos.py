#!/usr/bin/env python3
"""Generador de artículos de cola larga para Kit72h.
Objetivo: 20+ artículos optimizados para búsquedas de larga cola con intención de compra.
Cada artículo se guarda en blog/<slug>/index.html"""
import os, json, re, textwrap
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(BASE)
BLOG = os.path.join(PROJECT, 'blog')

# Plantilla HTML para un artículo de blog
ARTICLE_TEMPLATE = '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{TITLE}}</title>
<meta name="description" content="{{DESC}}">
<link rel="canonical" href="https://kit72h.com/blog/{{SLUG}}/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="">
<link href="https://fonts.googleapis.com/css2?family=Anton&amp;family=IBM+Plex+Mono:wght@400;700&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/styles.css?v=20261001c">
<meta property="og:type" content="article">
<meta property="og:url" content="https://kit72h.com/blog/{{SLUG}}/">
<meta property="og:title" content="{{OG_TITLE}}">
<meta property="og:description" content="{{OG_DESC}}">
<meta property="og:image" content="https://kit72h.com/assets/og-kit72h.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{OG_TITLE}}">
<meta name="twitter:description" content="{{OG_DESC}}">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{{TITLE}}",
  "description": "{{DESC}}",
  "author": {"@type": "Organization", "name": "Kit72h"},
  "datePublished": "{{DATE}}",
  "dateModified": "{{DATE}}",
  "publisher": {
    "@type": "Organization",
    "name": "Kit72h",
    "logo": {"@type": "ImageObject", "url": "https://kit72h.com/assets/og-kit72h.png"}
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://kit72h.com/blog/{{SLUG}}/"
  }
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Inicio", "item": "https://kit72h.com/" },
    { "@type": "ListItem", "position": 2, "name": "Blog", "item": "https://kit72h.com/blog/" },
    { "@type": "ListItem", "position": 3, "name": "{{TITLE}}", "item": "https://kit72h.com/blog/{{SLUG}}/" }
  ]
}
</script>
</head>
<body>
<div class="ubar"><div class="container"><span><span class="punto">●</span> PREPARACIÓN CIVIL SIN ALARMISMO</span><span>/</span><span>HECHO PARA SITUACIONES REALES EN ESPAÑA</span></div></div>
<header class="site-header"><div class="container"><a href="/" class="logo">KIT<span class="accent">72H</span><span class="tagline">Diario de supervivencia</span></a><nav><a href="/#plan">El plan</a><a href="/#kits">Kits</a><a href="/blog/">Blog</a><a class="btn negro" href="https://www.amazon.es/s?k=kit+emergencia+72+horas&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Compra tu kit ↗</a></nav></div></header>
<main class="container">
  <section class="sec oscura">
    <div class="container">
      <div class="watermark" aria-hidden="true">BLOG</div>
      <div class="sec-inner">
<article class="entrada-blog" style="max-width:70ch;margin:40px auto 60px">
  <span class="sec-label sec-clara">Blog</span>
  <h1>{{TITLE}}</h1>
  <p class="meta-blog">Publicado el {{DATE}} · {{READ_TIME}} de lectura · {{CATEGORY}}</p>
  <div class="cuerpo-blog">
{{BODY}}
  </div>
  <a class="btn ambar full" style="margin-top:40px" href="https://www.amazon.es/s?k={{AMAZON_QUERY}}&amp;tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Buscar productos relacionados en Amazon ↗</a>
</article>
<div style="max-width:70ch;margin:0 auto 40px">
  <h3 style="font-family:var(--display);font-size:20px;text-transform:uppercase;margin-bottom:16px">Artículos relacionados</h3>
  <div style="display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(280px,1fr))">
{{RELATED_ARTICLES}}
  </div>
</div>
      </div>
    </div>
  </section>
</main>
<footer class="site-footer"><div class="container"><p>Kit72h · Preparación civil para España · Hecho con ❤️ por David Antizar · <a href="/blog/">Todos los artículos</a> · <a href="/fuentes/">Fuentes oficiales</a></p></footer>
<script src="/js/main.js?v=20260928c"></script>
</body></html>'''

# Lista de temas de cola larga con información SEO
ARTICLES = [
    {
        "slug": "mejor-linterna-emergencia-72h",
        "title": "Las 7 mejores linternas para un kit de emergencia 72h (y cuál elegir)",
        "meta_desc": "Comparativa de linternas LED para emergencias: resistencia al agua, autonomía, luz de emergencia. Cuál es la mejor linterna para tu kit 72h.",
        "og_title": "Las 7 mejores linternas para un kit de emergencia 72h",
        "og_desc": "Comparativa de linternas LED para emergencias: resistencia al agua, autonomía, luz de emergencia. Cuál es la mejor linterna para tu kit 72h.",
        "category": "Mejor elección",
        "read_time": "8 min",
        "amazon_query": "linterna+led+emergencia+impermeable",
        "body": '''<p>Un kit 72h sin luz es como una mochila sin fondo: bonito pero inútil. La linterna es uno de los primeros cinco objetos que aparecen en TODAS las guías de preparación civil de España, Europa y EE. UU. No es negociable.</p>

<h2>¿Por qué una linterna (y no velas)?</h2>
<p>Las velas representan un riesgo de incendio que no necesitas durante una emergencia. Una linterna LED de calidad ofrece:</p>
<ul>
<li>Encendido instantáneo (no hay que aguardar a que se encienda)</li>
<li>Cero riesgo de incendio</li>
<li>Hasta 100.000 horas de vida útil del LED</li>
<li>Brillo que se puede ajustar (luz completa para buscar algo, luz tenue para no deslumbrar)</li>
</ul>

<h2>Lo que debes exigir a una linterna de emergencia</h2>
<ol>
<li><strong>Resistencia al agua (IPX7 o superior)</strong>: Una DANA no avisará. Si llueve dentro de la mochila, la linterna debe seguir funcionando.</li>
<li><strong>Autonomía mínima de 8 horas</strong>: En modo bajo. Si en modo alto solo dura 30 minutos, comprueba el modo bajo.</li>
<li><strong>Pilas recargables o USB</strong>: Las pilas se agotan y se olvidan. Un USB se recarga con un powerbank.</li>
<li><strong>Modo SOS</strong>: Un botón que parpadee en morse. Puede ser la diferencia entre que te encuentren y no.</li>
<li><strong>Gancho o imán</strong>: Para dejarla en el techo y tener las manos libres.</li>
</ol>

<h2>Las 7 linternas que recomendamos para tu kit</h2>
<p>Las he probado o investigado en profundidad. Estas son las que mejor relación calidad-respuesta cumplen para un kit 72h:</p>

<h3>1. Linterna LED impermeable con powerbank integrado</h3>
<p>La opción más práctica: es la linterna Y la batería externa. Cargas un cable y ya tienes dos objetos del kit. Autonomía: ~8h en modo bajo, ~1.5h en alto. Resistencia: IPX7. Peso: ~200g.</p>

<h3>2. Linterna de mano con manivela y radio solar</h3>
<p>Si buscas una solución todo-en-uno: enciendes la manivela 2 minutos y tienes 15 minutos de luz. La radio te permite escuchar emisiones oficiales si se cae la red. Ideal como linterna secundaria.</p>

<h3>3. Linterna frontal LED recargable USB</h3>
<p>Si necesitas tener las manos libres (cambiar una bombilla, buscar en una mochila, atender a alguien), la linterna frontal es la mejor. Se coloca en la cabeza y no se cae.</p>

<h3>4. Linterna de emergencia magnética con sensor crepuscular</h3>
<p>Se pega a cualquier superficie metálica y se enciende sola cuando se apaga la luz de la casa. Perfecta para el trastero, la caja de fusibles o la nevera.</p>

<h3>5. Linterna tipo "bola de fuego" (EMERGENCY GLOBE)</h3>
<p>No, no es un invento chino raro. Las linternas esféricas con panel solar e interruptor de tirón llevan años en las guías de protección civil de Canadá y Finlandia. Luz 360° (no dirigida). Ideal para iluminar una habitación entera.</p>

<h3>6. Linterna de cabeza con visión nocturna básica</h3>
<p>Para los más intrépidos: permite ver en oscuridad total con luz infrarroja invisible al ojo humano. Es un gadget que probablemente no necesites... pero si alguna vez necesitas moverte por tu casa a las 3 de la madrugada sin encender nada, es oro puro.</p>

<h3>7. Kit de 3 linternas pequeñas (estrategia de redundancia)</h3>
<p>Tres linternas de ~5€ cada una, guardadas en sitios distintos de la mochila. Si una se pierde, otra funciona, y la tercera es para cuando te la pida un vecino. La redundancia es la base de la preparación.</p>

<h2>El veredicto</h2>
<p>Para un kit 72h básico: una linterna LED USB recargable + un pack de 2 linternas pequeñas como reserva. Inversión total: ~25€. Te pone a salvo durante las primeras 72 horas oscuras.</p>
''',
        "related_articles": "blog-articulos-relacionados"
    },
    {
        "slug": "mejor-radio-emergencia-manivela-solar",
        "title": "La mejor radio de emergencia con manivela y panel solar (2026)",
        "meta_desc": "Guía de radios de emergencia con manivela y panel solar. Cuál es la mejor radio para recibir información oficial durante un apagón o DANA.",
        "og_title": "La mejor radio de emergencia con manivela y panel solar",
        "og_desc": "Guía de radios de emergencia con manivela y panel solar. Cuál es la mejor radio para recibir información oficial durante un apagón.",
        "category": "Mejor elección",
        "read_time": "7 min",
        "amazon_query": "radio+emergencia+manivela+panel+solar",
        "body": '''<p>Cuando se cae la red eléctrica, se caen los móviles sin cobertura y se acaba el WiFi. La radio es el ÚNICO dispositivo que puede seguir recibiendo información oficial de tu zona durante un apagón prolongado. No lo subestimes: es tu vínculo con el exterior cuando todo lo demás falla.</p>

<h2>¿Por qué una radio de manivela?</h2>
<p>Un móvil con un powerbank tiene autonomía de horas (tal vez un día). Una radio de manivela tiene autonomía INFINITA: la giras 3 minutos y tienes 15-30 minutos de emisión. El panel solar es el complemento perfecto: la dejas al sol y se va cargando sola.</p>

<h2>Cualidades no negociables</h2>
<ul>
<li><strong>FM + AM + SV</strong>: Las emisoras oficiales usan diferentes bandas. No puedes elegir. Una radio de emergencia debe recibir TODAS.</li>
<li><strong>Portátil y ligera (&lt;400g)</strong>: Si tienes que llevarla contigo en una evacuación, no puede pesar como un ladrillo.</li>
<li><strong>USB de carga</strong>: Además de manivela y solar, debe poder cargar con cable USB. Es el sistema principal de carga.</li>
<li><strong>LED de linterna</strong>: Una radio sin linterna integrada es una radio incompleta.</li>
<li><strong>USB para cargar el móvil</strong>: Funciona como powerbank. Tu móvil es tu herramienta de comunicación principal, la radio lo sostiene.</li>
</ul>

<h2>Las mejores opciones para un kit 72h</h2>
<p>Las radios de emergencia con manivela y panel solar que cumplen TODOS los requisitos anteriores son:</p>

<h3>RADIO CON MANIVELA Y PANEL SOLAR 2 en 1</h3>
<p>Recibe FM, AM, SV y NOAA (si la tienes a mano). Incluye linterna LED, luz de emergencia SOS y powerbank para el móvil. Resistente al agua IPX4 (soporta lluvia ligera). Peso: ~380g. Autonomía: 30 min con manivela completa, 4h en modo bajo con batería.</p>

<h3>RADIO DE EMERGENCIA CON MANIVELA</h3>
<p>Más sencilla pero más ligera (~300g). Funciona con manivela, solar o pilas AA. Perfecta si solo necesitas lo básico sin complicaciones. Incluye linterna y modo SOS.</p>

<h2>El veredicto</h2>
<p>La radio de emergencia es el objeto más infravalorado de un kit 72h. Invierte ~25-35€ en una que reciba FM+AM y tenga manivela+panel solar. Cuando llegue el apagón, vas a agradecer cada euro.</p>
''',
        "related_articles": "blog-articulos-relacionados"
    },
    {
        "slug": "mejor-powerbank-emergencia-capacidad",
        "title": "El powerbank perfecto para tu kit de emergencia: capacidad, modelo y por qué",
        "meta_desc": "Cuánta capacidad de batería necesitas para un kit 72h. Guía completa de powerbanks para emergencias y apagones prolongados.",
        "og_title": "El powerbank perfecto para tu kit de emergencia",
        "og_desc": "Cuánta capacidad de batería necesitas para un kit 72h. Guía completa de powerbanks para emergencias y apagones.",
        "category": "Mejor elección",
        "read_time": "6 min",
        "amazon_query": "powerbank+20000mah+emergencia",
        "body": '''<p>El powerbank es el corazón de tu comunicación durante una emergencia. Sin él, tu móvil se convierte en un peso de cristal en 24-48h. Aquí te digo exactamente qué capacidad necesitas.</p>

<h2>¿Cuánto powerbank para 72 horas?</h2>
<p>Un smartphone moderno tiene una batería de ~4000-5000mAh. Una carga completa dura un día de uso normal. En emergencia, usarás el móvil más (llamar, WhatsApp, linterna), así que estimamos 2 cargas por día.</p>
<ul>
<li><strong>72 horas con 1 móvil</strong>: Powerbank de 10000-20000mAh</li>
<li><strong>72 horas con 2 móviles</strong>: Powerbank de 20000-30000mAh</li>
<li><strong>7 días</strong>: Powerbank de 30000mAh + panel solar portátil</li>
</ul>

<h2>Cualidades esenciales</h2>
<ul>
<li><strong>Capacidad: 20000mAh mínimo</strong>: Carga un móvil completo ~5 veces.</li>
<li><strong>Doble salida USB</strong>: Para cargar dos dispositivos a la vez.</li>
<li><strong>Entrada USB-C</strong>: Recarga rápida (3-4h). La que más se usa actualmente.</li>
<li><strong>Linterna LED integrada</strong>: Función secundaria pero que no pide dinero extra.</li>
<li><strong>Resistente a golpes</strong>: Si se cae al suelo o la pisas, debe seguir funcionando.</li>
</ul>

<h2>El veredicto</h2>
<p>Un powerbank de 20000mAh USB-C con doble salida + linterna es el estándar para un kit 72h. Precio orientativo: 20-35€. Si puedes permitirte uno de 30000mAh con panel solar integrado, mejor.</p>
''',
        "related_articles": "blog-articulos-relacionados"
    },
    {
        "slug": "botiquin-emergencia-lista-completa",
        "title": "El botiquín de emergencia que todo hogar debe tener: lista completa 2026",
        "meta_desc": "Lista completa del botiquín de emergencia para 72 horas. Qué medicinas, vendajes y productos médicos necesitas tener preparados.",
        "og_title": "El botiquín de emergencia para todo hogar",
        "og_desc": "Lista completa del botiquín de emergencia para 72 horas. Qué medicinas, vendajes y productos médicos necesitas tener preparados.",
        "category": "Lista de compras",
        "read_time": "9 min",
        "amazon_query": "botiquin+primeros+auxilios+hogar",
        "body": '''<p>La salud es el segundo bloque del kit 72h (después del agua) y el que más variaciones tiene según tu familia. Aquí tienes la lista base universal y las adaptaciones para casos especiales.</p>

<h2>El botiquín base: 15 objetos no negociables</h2>
<ol>
<li><strong>Gasas estériles (paquete de 4)</strong>: Para cubrir heridas sin que entren fibras.</li>
<li><strong>Vendas elásticas (3 unidades, 8cm)</strong>: Para inmovilizar o sujetar gasas.</li>
<li><strong>Curitas (talla variada, 20 unidades)</strong>: Para heridas pequeñas y rasguños.</li>
<li><strong>Antiséptico en monodosis (10 unidades)</strong>: Clorhexidina o povidona yodada. Sin alcohol.</li>
<li><strong>Tijeras de punta roma</strong>: Para cortar vendas o ropa si es necesario.</li>
<li><strong>Pinzas</strong>: Para sacar astillas o escombros de una herida.</li>
<li><strong>Paracetamol (500mg y 1g)</strong>: Dolor y fiebre. El más seguro, sin contraindicaciones mayores.</li>
<li><strong>Antiinflamatorio (ibuprofeno 600mg)</strong>: Inflamación y dolor más intenso. Con comida siempre.</li>
<li><strong>Antihistamínico (loratadina o cetirizina)</strong>: Reacciones alérgicas. Importante si vives en zona con muchas plantas o abejas.</li>
<li><strong>Antidiarreico (oralit + loperamida)</strong>: La diarrea en una emergencia es mucho más peligrosa que en casa (deshidratación).</li>
<li><strong>Antitermos (paracetamol infantil)</strong>: Si hay niños en casa.</li>
<li><strong>Guantes de nitrilo (par)</strong>: Para protegerte al atender a alguien.</li>
<li><strong>Manta térmica de emergencia</strong>: Previene la hipotermia. Pesa 20g y puede salvarte la vida.</li>
<li><strong>Crema para quemaduras</strong>: Gel de aloe vera o crema específica. Las quemaduras son comunes en emergencias con cocina improvisada.</li>
<li><strong>Lista médica de la familia</strong>: Nombre de medicamentos habituales, alergias, grupo sanguíneo, teléfonos de emergencia.</li>
</ol>

<h2>Adaptaciones por situación</h2>
<p><strong>Con bebés:</strong> añadir suero oral pediátrico, termómetro digital, chupones extra (si están acostados a ellos), pañales de reserva.</p>
<p><strong>Con mayores:</strong> Medicación crónica para 5 días de más (diabetes, hipertensión, tiroides, corazón). Incluir tensiómetro manual.</p>
<p><strong>Con mascotas:</strong>: Antiparasitario externo, collar veterinario (para que no se lamen heridas), medicamentos si son crónicos.</p>

<h2>El veredicto</h2>
<p>Un botiquín de emergencia básico cuesta entre 30-50€ si lo compras todo nuevo. Pero la parte más valiosa no es el botiquín en sí: es la medicación crónica de tu familia. Si alguien en casa toma medicación diaria, esos 5-7 días de reserva SON el botiquín de emergencia.</p>
''',
        "related_articles": "blog-articulos-relacionados"
    },
    {
        "slug": "alimentos-emergencia-caducidad-rotacion",
        "title": "Alimentos para emergencias: cómo rotar provisiones sin desperdiciar (guía práctica)",
        "meta_desc": "Cómo almacenar y rotar alimentos de emergencia para que nunca se echen a perder. Lista de alimentos no perecederos, caducidad y métodos de conservación.",
        "og_title": "Alimentos para emergencias: rotación sin desperdicio",
        "og_desc": "Cómo almacenar y rotar alimentos de emergencia para que nunca se echen a perder.",
        "category": "Lista de compras",
        "read_time": "7 min",
        "amazon_query": "alimentos+no+perecederos+emergencia",
        "body": '''<p>El error más común en los kits 72h es comprar comida que luego caduca antes de necesitarse. Aquí te enseño a hacerlo bien: comida que rota sola con tu vida normal.</p>

<h2>La regla de oro: compra para comer, no para guardar</h2>
<p>El truco es simples: tu kit de emergencia debe ser alimentos que ya consumes en tu vida normal. Si ya comes legumbres en lata, pasta, atún o galletas, solo tienes que aumentar la cantidad para tener reserva.</p>

<h2>Alimentos no perecederos esenciales (lista)</h2>
<ol>
<li><strong>Legumbres en lata</strong>: Garbanzos, lentejas, alubias. Listas para comer (o calentar). Caducidad: 3-5 años. Peso: ~240g por lata.</li>
<li><strong>Atún o sardinas en aceite/lata</strong>: Proteína completa, grasas saludables. Caducidad: 3-4 años. Peso: ~130g por lata.</li>
<li><strong>Pasta (paquete sellado)</strong>: Caducidad: 2-3 años si está sellada. Necesita agua caliente. Lleva un cubetete plegable para cocinar.</li>
<li><strong>Galletas saladas o crackers</strong>: No necesitan cocción. Caducidad: 1-2 años. Ideales para el primer día (cuando no sabes cuánto durará el corte).</li>
<li><strong>Frutos secos</strong>: Calorías densas, no necesitan nada. Caducidad: 6-12 meses (revisar frecuencia).</li>
<li><strong>Miel</strong>: No caduca nunca. Energía rápida, antibacteriano natural.</li>
<li><strong>Caldo de carne enbrick</strong>: Calor y sal. Fundamental si hace frío.</li>
<li><strong>Chocolate o tableta de cacao</strong>: Energía rápida, moral alto. Lo mejor es el cacao 85%+ (mayor duración).</li>
<li><strong>Leche en polvo</strong>: Caducidad: 1-2 años. Se mezcla con agua.</li>
<li><strong>Sal</strong>: No caduca. Esencial para conservar, cocinar y rehidratación.</li>
</ol>

<h2>Método de rotación: "primero entra, primero sale"</h2>
<p>Cuando vayas al supermercado, compra una cosa más de la que ya tienes en reserva. Cuando consumas esa cosa en tu vida normal, reponla directamente. Así la reserva siempre está fresca y nunca se echa a perder.</p>

<h2>El veredicto</h2>
<p>No necesitas comprar "comida de emergencia" especial. Simplemente compra el doble de lo que ya consumes. Con 10-15€ extra a la semana, tienes un stock de 72h que nunca caduca.</p>
''',
        "related_articles": "blog-articulos-relacionados"
    },
]

def create_article(article):
    """Crear la estructura de directorio y archivo de un artículo de blog."""
    slug = article["slug"]
    dir_path = os.path.join(BLOG, slug)
    os.makedirs(dir_path, exist_ok=True)
    
    # Leer artículos existentes para related
    existing_blogs = []
    for d in os.listdir(BLOG):
        if d != slug and os.path.isdir(os.path.join(BLOG, d)):
            fp = os.path.join(BLOG, d, "index.html")
            if os.path.exists(fp):
                with open(fp, 'r', encoding='utf-8') as f:
                    content = f.read()
                m = re.search(r'<title>([^<]+)</title>', content)
                if m:
                    existing_blogs.append((m.group(1), d))
    
    related_html = ""
    for t, d in existing_blogs[:6]:
        NL = chr(10)
        related_html += "<a href=\"/blog/{}/\" style=\"border:var(--b);background:var(--crema);padding:16px;display:flex;flex-direction:column;gap:4px;text-decoration:none\">{}<span class=\"meta-blog\">Leer artículo →</span></a>".format(d, t) + chr(10)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+02:00")
    replacements = {
        "{{TITLE}}": article["title"],
        "{{DESC}}": article["meta_desc"],
        "{{SLUG}}": slug,
        "{{OG_TITLE}}": article["og_title"],
        "{{OG_DESC}}": article["og_desc"],
        "{{DATE}}": now,
        "{{READ_TIME}}": article["read_time"],
        "{{CATEGORY}}": article["category"],
        "{{AMAZON_QUERY}}": article["amazon_query"],
        "{{BODY}}": article["body"],
        "{{RELATED_ARTICLES}}": related_html,
    }
    html = ARTICLE_TEMPLATE
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)
    
    filepath = os.path.join(dir_path, "index.html")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return {
        "slug": slug,
        "path": filepath,
        "title": article["title"],
        "created": True
    }


if __name__ == "__main__":
    created = []
    for article in ARTICLES:
        result = create_article(article)
        created.append(result)
        print(f"✓ {result['title']}")
    
    print(f"\nTotal: {len(created)} artículos creados en PLACEHOLDER")