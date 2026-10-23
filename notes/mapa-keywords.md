# Mapa de keywords Kit72h — la brújula de la «fuente de verdad»

> Objetivo: que quien busque CUALQUIER frase relacionada con preparación de emergencias
> en España aterrice en kit72h.com. Cada keyword tiene: intención, página destino
> (existente o a crear) y prioridad. Los crons LLM (comparador/editor) consultan este
> fichero y trabajan la fila con prioridad más alta sin cubrir.

## Cómo se usa
1. El cron LLM lee la tabla de abajo, elige la primera fila con `Estado: pendiente`
   (o mejorable) y con prioridad P1 > P2 > P3.
2. Trabaja la página destino (crear en blog/ o mejorar kit/ existente).
3. Al terminar: marca la fila `Estado: hecha (fecha)` y commit.

## Clusters (grupos de intención de búsqueda)

### Cluster A — «kit de emergencia» (núcleo, alta intención de compra)
| Keyword | Volumen ES | Intención | Destino | Estado | Prioridad |
|---|---|---|---|---|---|
| kit de emergencia 72 horas | alto | compra | / (home) | ✅ cubierto | P1 |
| qué llevar en un kit de emergencia | alto | info→compra | /kit/kit-basico/ | ✅ cubierto | P1 |
| lista kit emergencia hogar | media | compra | /kit/kit-hogar/ | ✅ cubierto | P1 |
| kit supervivencia completo | media | compra | /kit/kit-kit-profesional/ | ✅ cubierto | P1 |
| maleta emergencia evacuación | media | compra | /kit/kit-evacuacion/ | ✅ cubierto | P1 |
| kit emergencia bebé familia | media | compra | blog pendiente | ✅ hecha (2026-10-10) | P2 |
| kit emergencia mascotas perro gato | media | compra | /kit/kit-mascotas/ | ✅ cubierto | P2 |

### Cluster B — escenarios (DANA, apagón, terremoto...) — donde España busca
| Keyword | Volumen ES | Intención | Destino | Estado | Prioridad |
|---|---|---|---|---|---|
| qué hacer en un apagón general | alto | info | /kit/kit-apagon/ | ✅ cubierto | P1 |
| kit apagón qué comprar | media | compra | /kit/kit-apagon/ | ✅ cubierto | P1 |
| DANA preparación casa kit | alto (estacional) | info→compra | /kit/kit-dana/ | ✅ cubierto | P1 |
| kit inundación imprescindibles | media | compra | /kit/kit-dana/ | ✅ cubierto | P1 |
| terremoto qué hacer España | media | info | /kit/kit-terremoto/ | ✅ cubierto | P1 |
| kit incendio casa | media | compra | /kit/kit-incendio/ | ✅ cubierto | P1 |
| ola de calor qué hacer | alto (estacional) | info | /kit/kit-calor/ | ✅ cubierto | P1 |
| nevada hogar qúe necesito | baja (estacional) | info→compra | /blog/nevada-en-casa-que-necesito/ | ✅ hecha (2026-10-13) | P3 |

### Cluster C — comparativas «mejor X» (máxima conversión)
| Keyword | Volumen ES | Intención | Destino | Estado | Prioridad |
|---|---|---|---|---|---|
| mejor linterna emergencia | media | compra | /blog/mejor-linterna-emergencia-72h/ | ✅ cubierto | P1 |
| mejor powerbank apagón | media | compra | /blog/mejor-powerbank-emergencia-capacidad/ | ✅ cubierto | P1 |
| mejor radio manivela | baja | compra | /blog/mejor-radio-emergencia-manivela-solar/ | ✅ cubierto | P2 |
| mejor botiquín doméstico | media | compra | /blog/botiquin-emergencia-lista-completa/ | ✅ cubierto | P1 |
| mejor purificador de agua emergencia | baja | compra | /blog/mejor-purificador-agua-emergencia/ | ✅ hecha (2026-10-09) | P2 |
| mejores conservas larga duración | media | compra | /blog/mejores-conservas-larga-duracion/ | ✅ hecha (2026-10-10) | P2 |
| mejor estufa sin luz | media | compra | /blog/mejor-estufa-sin-luz-apagon/ | ✅ hecha (2026-10-08) | P2 |
| mejor Starlink España precio | media | compra | /blog/mejor-starlink-espana-precio/ (+ banner home) | ✅ hecha (2026-10-15) | P2 |
| comparativa generador vs power station | baja | compra | /blog/generador-vs-power-station-comparativa/ | ✅ hecha (2026-10-12) | P3 |
| mejor detector de monóxido de carbono | media | compra | /blog/mejor-detector-monoxido-carbono/ | ✅ hecha (2026-10-16) | P2 |
| mejor extintor doméstico | media | compra | /blog/mejor-extintor-domestico/ (+ kit-incendio) | ✅ hecha (2026-10-17) | P2 |
| mejor SAI UPS para casa y router apagón | media | compra | /blog/mejor-sai-ups-casa-apagon/ (+ kit-apagon) | ✅ hecha (2026-10-18) | P2 |
| mejor mochila de emergencia y evacuación | media | compra | /blog/mejor-mochila-emergencia-evacuacion/ (+ /kit/kit-evacuacion/) | ✅ hecha (2026-10-19) | P2 |
| mejores cadenas para la nieve | media (estacional nov-mar) | compra | /blog/mejores-cadenas-para-la-nieve/ (+ /kit/kit-coche/) | ✅ hecha (2026-10-20) | P2 |

### Cluster D — normativa y autoridad (Google premia a quien la cita)
| Keyword | Volumen ES | Intención | Destino | Estado | Prioridad |
|---|---|---|---|---|---|
| kit 72 horas recomendación UE | media | info | /kit/kit-basico/ (fuente UE) | ✅ cubierto | P1 |
| qué recomienda Protección Civil kit emergencia | media | info | /fuentes/ + kit-basico | ✅ cubierto | P1 |
| autosuficiencia 72 horas directiva europea | baja | info | /kit/kit-basico/ | ✅ cubierto | P2 |
| alerta DGT kit coche obligatorio | media | info | /kit/kit-coche/ | ✅ hecha (2026-10-16) | P1 |
| señalización V16 obligatoria 2026 | alta (estacional) | info | /blog/baliza-v16-obligatoria-2026/ (+ /kit/kit-coche/) | ✅ hecha (2026-10-11) | P2 |

### Cluster E — dudas prácticas (long tail, FAQ + rich results)
| Keyword | Volumen ES | Intención | Destino | Estado | Prioridad |
|---|---|---|---|---|---|
| cuánta agua guardar por persona | media | info | /blog/agua-cuanta-y-como/ | ✅ cubierto | P2 |
| alimentos no perecederos lista | media | info | /blog/alimentos-emergencia-caducidad-rotacion/ | ✅ cubierto | P2 |
| caducidad de los alimentos almacenados | baja | info | mismo post | ✅ cubierto | P3 |
| cómo guardar agua correctamente | media | info | mismo post | ✅ cubierto | P2 |
| generator ruido normativa comunidad | baja | info | /blog/generador-ruido-normativa-comunidad/ | ✅ hecha (2026-10-14) | P3 |

### Cluster F — TICKET ALTO (una venta pesa 20-100× más que la cola larga)

> Con el 3% de comisión de Amazon: un generador de 800 € deja ~24 €; un powerbank de 30 € deja 0,90 €.
> El consejero pondera estas keywords ×1,25 además de su prioridad. Fuente del dato: panel de
> afiliados 30 días = 10 pedidos y 6,98 € → 0,70 €/pedido. El problema no es el clic, es el carrito.

| Keyword | Volumen ES | Intención | Destino | Estado | Prioridad |
|---|---|---|---|---|---|
| mejor generador eléctrico portátil inverter | alto | compra | blog pendiente | ✅ hecha (2026-10-23) | P1 |
| mejor power station para apagones en casa | media | compra | blog pendiente | pendiente | P1 |
| mejor kit solar portátil para casa | media | compra | blog pendiente | pendiente | P1 |
| mejor deshumidificador para inundaciones y humedad | media (estacional) | compra | blog pendiente | pendiente | P2 |
| mejor bomba de achique para inundación | media (estacional) | compra | blog pendiente | pendiente | P2 |
| mejor arrancador de batería para coche | media | compra | blog pendiente | pendiente | P2 |
| mejor estufa de gas butano para apagón | media (estacional) | compra | blog pendiente | pendiente | P2 |
| mejor walkie talkie PMR446 largo alcance | media | compra | blog pendiente | pendiente | P2 |

## Reglas de contenido (para los crons)
- Cada página nueva CITa fuente oficial con enlace (DG ECHO, Protección Civil, DGT, AEMET, 112).
- SIEMPRE tag afiliado `ntizar-21`.
- Enlaces internos: mínimo 3 por artículo hacia kits/otros posts con texto ancla descriptivo.
- Estacionales: crear 45-60 días ANTES del pico (DANA: sep; calor: may; nieve: nov; V16: ya).
- Nunca repetir título de página existente (canonical cannibalización).
- **Ticket alto primero**: una comparativa de ticket alto vale 20-100× más que una guía de cola larga.
  Cada una necesita ≥3 enlaces de producto con `tag=ntizar-21` (ficha `/dp/` SOLO si el ASIN está
  verificado en `data/catalogo.json`; si no, búsqueda `/s?k=` — **nunca inventar un ASIN**), tabla
  comparativa real y enlace a la ficha de kit que la use (`/kit/kit-apagon/`, `/kit/kit-dana/`…).
