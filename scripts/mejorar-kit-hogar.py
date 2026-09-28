# -*- coding: utf-8 -*-
"""Editor nocturno 2026-09-28 — amplia el kit-hogar (SOLO anade)."""
import json, io, os

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "kits.json")
with io.open(RUTA, encoding="utf-8") as f:
    kits = json.load(f)

kit = None
for k in kits["kits"]:
    if k.get("slug") == "kit-hogar":
        kit = k
        break
assert kit is not None, "kit-hogar no encontrado"

BUSQ = "https://www.amazon.es/s?k=%s&tag=nti0c8-21"

# --- 1. Nuevos productos en "Cocina sin electricidad" ---
cocina = [s for s in kit["secciones"] if s["titulo"] == "Cocina sin electricidad"][0]
cocina["items"].append({
    "producto": "Detector de monóxido de carbono a pilas",
    "afiliado": BUSQ % "detector monoxido carbono pilas",
    "descripcion": "Este kit recomienda un hornillo de butano dentro de casa: el CO no se huele, no se ve y mata mientras duermes. Ponlo a la altura de la respiración, en la cocina o donde cocines, y nunca lo apagues para ahorrar pilas.",
    "precio_aprox": "15-30 €",
    "prioridad": "esencial",
    "es_busqueda": True
})

# --- 2. Seccion nueva: luz, energia y comunicacion ---
kit["secciones"].append({
    "titulo": "Luz, energía y comunicación",
    "intro": "Un kit de confinamiento sin luz ni radio depende de un móvil que se queda sin batería a las pocas horas. Estos tres aparatos son los que mantienen la casa informada y a la vista cuando no hay red eléctrica.",
    "items": [
        {
            "producto": "Linterna LED a pilas o de dinamo",
            "afiliado": BUSQ % "linterna LED pilas dinamo",
            "descripcion": "Sin luz no encuentras nada y acabas usando el móvil como linterna, que es justo lo que necesitas para llamar. Guarda pilas de repuesto del mismo tamaño, fuera de los aparatos.",
            "precio_aprox": "8-25 €",
            "prioridad": "esencial",
            "es_busqueda": True
        },
        {
            "producto": "Radio FM/AM a pilas o de dinamo",
            "afiliado": BUSQ % "radio fm am pilas dinamo",
            "descripcion": "Cuando cae la red móvil, la radio sigue emitiendo avisos oficiales sin internet ni batería del móvil. Sintoniza las emisoras locales antes de guardarla y prueba la recepción donde la vayas a usar.",
            "precio_aprox": "15-35 €",
            "prioridad": "esencial",
            "es_busqueda": True
        },
        {
            "producto": "Batería externa (powerbank) de 10.000-20.000 mAh",
            "afiliado": BUSQ % "powerbank 20000 mah",
            "descripcion": "Con el móvil al 20% te quedan dos llamadas. Un powerbank cargado da varias cargas completas y alimenta la radio o el ventilador por USB. Recárgalo cada seis meses aunque no lo uses.",
            "precio_aprox": "15-35 €",
            "prioridad": "esencial",
            "es_busqueda": True
        }
    ]
})

# --- 3. Guia: consejos nuevos ---
kit["guia"]["antes"] += [
    "Prueba radio, linterna y hornillo una vez al trimestre y ten pilas de repuesto del mismo tamaño: un kit con pilas agotadas no es un kit",
    "Carga el powerbank y revisa caducidades cada seis meses, el mismo día que cambies la hora: así no se te olvida nunca"
]
kit["guia"]["durante"] += [
    "Si enciendes hornillo de butano, vela o brasero, hazlo con ventilación y con el detector de CO puesto: dentro de casa la combustión consume oxígeno y el monóxido no avisa",
    "Móvil en modo ahorro y con datos apagados; llama cuando tengas cobertura y reserva el powerbank para la radio y la linterna"
]
kit["guia"]["despues"] += [
    "Repón pilas, agua y comida consumida el mismo día, no la semana siguiente: la próxima emergencia no avisa",
    "Apunta lo que echaste de menos durante esos días: esa lista, y no otra, es tu compra para el kit"
]

# --- 4. Errores nuevos ---
kit["errores"] += [
    "Usar el móvil como linterna: la luz más cara es la que te deja sin batería para llamar",
    "Guardar las pilas dentro de la radio o la linterna: se sulfatan y te arruinan el aparato justo cuando lo necesitas. Guárdalas aparte, en su envase"
]

# --- 5. Coste recalculado (se anaden ~53-125 EUR de luz, radio, bateria y detector) ---
kit["coste_total"] = "210-420 € (2 personas, 7-10 días, con hornillo, luz, radio, powerbank y detector de CO)"

# --- 6. Metadatos de revision ---
nota = ("2026-09-28 — EDITOR NOCTURNO: kit-hogar ampliado con 4 productos reales que faltaban. "
        "Hueco detectado: un kit de confinamiento no tenía ninguna fuente de luz, radio ni energía. "
        "Seccion nueva «Luz, energía y comunicación» con linterna LED a pilas/dinamo, radio FM/AM a pilas o dinamo "
        "(la guia ya pedia escuchar la radio oficial dos veces al día sin que existiera el aparato) y powerbank de 10.000-20.000 mAh. "
        "Anadido a «Cocina sin electricidad» un detector de monóxido de carbono a pilas: el kit recomienda hornillo de butano dentro de casa "
        "y no había ninguna protección frente al CO. Los 4 apuntan a busqueda de Amazon (es_busqueda: true): no se inventan fichas /dp/. "
        "4 consejos nuevos en la guia (antes: prueba trimestral y pilas de repuesto, powerbank con cambio de hora; durante: ventilacion con combustion y modo ahorro; "
        "despues: reponer el mismo dia y apuntar lo que faltó) y 2 errores nuevos (movil como linterna; pilas guardadas dentro de los aparatos). "
        "coste_total recalculado. paraQuien, paraQuien_no y resumen revisados: siguen exactos, sin cambios.")
kits["meta"]["nota_revision"] = nota + " // " + kits["meta"].get("nota_revision", "")
kits["meta"]["ultima_revision"] = "2026-09-28"
kits["meta"]["revision"] = int(kits["meta"].get("revision", 1)) + 1

with io.open(RUTA, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(kits, f, ensure_ascii=False, indent=2)
print("OK kit-hogar:", len(kit["secciones"]), "secciones,",
      sum(len(s["items"]) for s in kit["secciones"]), "productos")
