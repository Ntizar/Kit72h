# -*- coding: utf-8 -*-
"""Editor nocturno 2026-09-26 — mejora del kit-apagon (indice 2 del encargo).

Anade 4 productos reales que faltaban, 1 seccion nueva de seguridad, 7 consejos
nuevos en la guia y actualiza coste_total. No borra nada.
"""
import json, re, io, os

RUTA = os.path.join('data', 'kits.json')
with io.open(RUTA, encoding='utf-8', newline='') as f:
    data = json.load(f)

kits = data['kits']
kit = [k for k in kits if k['slug'] == 'kit-apagon'][0]

TAG = '&tag=nti0c8-21'
S = 'https://www.amazon.es/s?k='
PRE = 'https://www.amazon.es/s?k='

# --- 1. Seccion nueva: seguridad durante el corte (CO + extintor) -----------
nueva_seccion = {
    "titulo": "Seguridad durante el corte",
    "intro": "Un apagón cambia cómo cocinas y cómo te alumbras, y eso trae dos riesgos que no se ven: el monóxido de carbono y el fuego. Son dos compras pequeñas que no se usan casi nunca y que, el día que hacen falta, son las únicas que importan.",
    "items": [
        {
            "producto": "Detector de monóxido de carbono (CO) a pilas con alarma",
            "afiliado": PRE + 'detector+de+monoxido+de+carbono+co+a+pilas+con+alarma' + TAG,
            "descripcion": "El CO no se huele, no se ve y no irrita: da sueño, dolor de cabeza y, si sigues en la habitación, mata mientras duermes. En un apagón se encienden velas, hornillos y braseros, y ahí es donde aparece. Ponlo a la altura de la cabeza, fuera del baño y cerca de la zona donde cocinas, y dale al botón de test cada cambio de hora. Regla que no se negocia: braseros, barbacoas, generadores y hornillos nunca en una habitación cerrada ni en el garaje.",
            "precio_aprox": "15-35 €",
            "prioridad": "esencial",
            "busqueda": "detector de monoxido de carbono co a pilas con alarma",
            "es_busqueda": True,
        },
        {
            "producto": "Extintor de polvo ABC de 1-2 kg con soporte",
            "afiliado": PRE + 'extintor+de+polvo+abc+1+kg+con+soporte+pared' + TAG,
            "descripcion": "Velas sobre la mesa, hornillo en el suelo y regletas sobrecargadas: cuando se cocina con llama de forma improvisada, el fuego es cuestión de minutos. Uno pequeño en la cocina y, si tienes garaje o cuadro eléctrico en el recibidor, otro al lado. Revisa el manómetro (aguja en verde), gíralo de vez en cuando para que el polvo no se apelmace y ponlo donde lo alcances sin escalar. Un extintor de 2 kg se vacía en unos 10-15 segundos: úsalo solo si el fuego es todavía pequeño y tienes la salida a tu espalda; si no, sal y llama al 112.",
            "precio_aprox": "25-45 €",
            "prioridad": "recomendado",
            "busqueda": "extintor de polvo abc 1 kg con soporte pared",
            "es_busqueda": True,
        },
    ],
}

# --- 2. Acumuladores de frio -> Cocina sin electricidad --------------------
acumuladores = {
    "producto": "Acumuladores de frío (bloques de gel congelables) para nevera y congelador",
    "afiliado": PRE + 'acumulador+de+frio+bloques+de+gel+congelables+nevera' + TAG,
    "descripcion": "Tenlos congelados desde antes: el día del corte pasan a la nevera, pegados a lo más delicado (carne, pescado, lácteos, embutido), y alargan las horas de frío sin que tengas que abrir la puerta para comprobar nada. Truco gratis equivalente: dos botellas de agua congeladas. Y lo que ya se ha descongelado no se vuelve a congelar: se cocina o se tira.",
    "precio_aprox": "10-20 €",
    "prioridad": "recomendado",
    "busqueda": "acumulador de frio bloques de gel congelables nevera",
    "es_busqueda": True,
}

# --- 3. SAI pequeno -> Dinero y comunicacion -------------------------------
sai = {
    "producto": "SAI / UPS pequeño (600-900 VA) para router y ONT",
    "afiliado": PRE + 'sai+ups+600va+router+ont+bateria' + TAG,
    "descripcion": "Un SAI de 600-900 VA mantiene en pie el router y la ONT el rato que aguante su batería (normalmente minutos, no horas) y, de regalo, protege el equipo de la sobretensión cuando vuelve la luz. Conecta solo el router: si le cuelgas también el ordenador o la tele, la batería se agota enseguida. No es un generador: no alimenta nevera, calefacción ni lavadora.",
    "precio_aprox": "60-110 €",
    "prioridad": "recomendado",
    "busqueda": "sai ups 600va router ont bateria",
    "es_busqueda": True,
}

for sec in kit['secciones']:
    if sec['titulo'] == 'Cocina sin electricidad':
        sec['items'].append(acumuladores)
    if sec['titulo'] == 'Dinero y comunicación':
        sec['items'].append(sai)

# insertar la seccion nueva despues de "Cocina sin electricidad"
idx = [i for i, s in enumerate(kit['secciones']) if s['titulo'] == 'Cocina sin electricidad'][0]
kit['secciones'].insert(idx + 1, nueva_seccion)

# --- 4. Guia: 7 consejos nuevos -------------------------------------------
kit['guia']['antes'] += [
    "Deja dos botellas de agua congeladas o bloques de gel dentro del congelador: el día del corte pasan a la nevera y te dan horas de frío sin abrir la puerta.",
    "Prueba hoy el detector de CO con su botón de test y mira que la aguja del extintor esté en verde. En un apagón no hay momento para descubrir que no funcionan.",
]
kit['guia']['durante'] += [
    "Ningún aparato de combustión en habitación cerrada: nada de braseros, barbacoas, generadores ni hornillos de gas dentro de casa o del garaje. Si enciendes el hornillo, ventilación cruzada (una ventana y otra abertura) y detector de CO a la vista.",
    "Ordena la nevera por descongelación: leche, carne, pescado y embutido primero; congelado y conservas al final. Lo que ya se descongeló, se cocina o se tira: no se recongela.",
    "Con SAI, apaga el ordenador y deja solo el router: ganas wifi mientras aguante la batería y evitas el pico de tensión al volver la luz.",
]
kit['guia']['despues'] += [
    "Antes de dormir, deja ventilada la habitación donde hayas usado llama y comprueba de nuevo el detector de CO y el extintor.",
    "Repón lo que gastaste: pilas, velas, gel congelable y lo que hayas abierto de la despensa. El siguiente corte no avisa.",
]

# --- 5. coste_total recalculado -------------------------------------------
def rango(precio):
    nums = [int(n) for n in re.findall(r'\d+', precio.replace('.', ''))]
    nums = [n for n in nums if n >= 1]
    if not nums:
        return (0, 0)
    if len(nums) == 1:
        return (nums[0], nums[0])
    return (nums[0], nums[1])

mins = maxs = 0
for sec in kit['secciones']:
    for it in sec['items']:
        a, b = rango(it.get('precio_aprox', ''))
        mins += a
        maxs += b
kit['coste_total'] = "%d-%d € según prioridades (además del kit básico)" % (mins, maxs)

# --- 6. meta ---------------------------------------------------------------
data['meta']['ultima_revision'] = '2026-09-26'
data['meta']['revision'] = data['meta'].get('revision', 1) + 1
nota = (" // 2026-09-26 — EDITOR NOCTURNO: kit-apagon ampliado con 4 productos reales que faltaban y una sección nueva "
        "«Seguridad durante el corte» (detector de monóxido de carbono a pilas + extintor de polvo ABC), acumuladores de frío "
        "congelables en «Cocina sin electricidad» y un SAI/UPS de 600-900 VA para router y ONT en «Dinero y comunicación». "
        "Los 4 apuntan a búsqueda de Amazon (es_busqueda: true): no se inventan fichas /dp/. 7 consejos nuevos en la guía "
        "(antes: gel congelado y test del detector/extintor; durante: cero combustión en recintos cerrados, orden de descongelación "
        "de la nevera y apagar todo menos el router; después: ventilar la estancia y reponer pilas, velas y gel). coste_total "
        "recalculado. paraQuien, paraQuien_no y errores revisados: siguen exactos, sin cambios.")
data['meta']['nota_revision'] = nota + data['meta'].get('nota_revision', '')

salida = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
with io.open(RUTA, 'w', encoding='utf-8', newline='') as f:
    f.write(salida.replace('\n', '\r\n'))

print('OK. coste_total =', kit['coste_total'])
print('secciones:', [s['titulo'] for s in kit['secciones']])
for s in kit['secciones']:
    print('  ', s['titulo'], '->', len(s['items']), 'items')
print('guia:', {k: len(v) for k, v in kit['guia'].items()})
