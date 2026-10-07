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
| kit emergencia bebé familia | media | compra | blog pendiente | pendiente | P2 |
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
| nevada hogar qúe necesito | baja (estacional) | info | /kit/kit-nieve/ | pendiente | P3 |

### Cluster C — comparativas «mejor X» (máxima conversión)
| Keyword | Volumen ES | Intención | Destino | Estado | Prioridad |
|---|---|---|---|---|---|
| mejor linterna emergencia | media | compra | /blog/mejor-linterna-emergencia-72h/ | ✅ cubierto | P1 |
| mejor powerbank apagón | media | compra | /blog/mejor-powerbank-emergencia-capacidad/ | ✅ cubierto | P1 |
| mejor radio manivela | baja | compra | /blog/mejor-radio-emergencia-manivela-solar/ | ✅ cubierto | P2 |
| mejor botiquín doméstico | media | compra | /blog/botiquin-emergencia-lista-completa/ | ✅ cubierto | P1 |
| mejor purificador de agua emergencia | baja | compra | blog pendiente | pendiente | P2 |
| mejores conservas larga duración | media | compra | blog pendiente | pendiente | P2 |
| mejor estufa sin luz | media | compra | blog pendiente | pendiente | P2 |
| mejor Starlink España precio | media | compra | banner Starlink home | parcial | P2 |
| comparativa generador vs power station | baja | compra | blog pendiente | pendiente | P3 |

### Cluster D — normativa y autoridad (Google premia a quien la cita)
| Keyword | Volumen ES | Intención | Destino | Estado | Prioridad |
|---|---|---|---|---|---|
| kit 72 horas recomendación UE | media | info | /kit/kit-basico/ (fuente UE) | ✅ cubierto | P1 |
| qué recomienda Protección Civil kit emergencia | media | info | /fuentes/ + kit-basico | ✅ cubierto | P1 |
| autosuficiencia 72 horas directiva europea | baja | info | /kit/kit-basico/ | ✅ cubierto | P2 |
| alerta DGT kit coche obligatorio | media | info | /kit/kit-coche/ | ✅ cubierto | P1 |
| señalización V16 obligatoria 2026 | alta (estacional) | info | /kit/kit-coche/ | parcial | P2 |

### Cluster E — dudas prácticas (long tail, FAQ + rich results)
| Keyword | Volumen ES | Intención | Destino | Estado | Prioridad |
|---|---|---|---|---|---|
| cuánta agua guardar por persona | media | info | /blog/agua-cuanta-y-como/ | ✅ cubierto | P2 |
| alimentos no perecederos lista | media | info | /blog/alimentos-emergencia-caducidad-rotacion/ | ✅ cubierto | P2 |
| caducidad de los alimentos almacenados | baja | info | mismo post | ✅ cubierto | P3 |
| cómo guardar agua correctamente | media | info | mismo post | ✅ cubierto | P2 |
| generator ruido normativa comunidad | baja | info | blog pendiente | pendiente | P3 |

## Reglas de contenido (para los crons)
- Cada página nueva CITa fuente oficial con enlace (DG ECHO, Protección Civil, DGT, AEMET, 112).
- SIEMPRE tag afiliado `ntizar-21`.
- Enlaces internos: mínimo 3 por artículo hacia kits/otros posts con texto ancla descriptivo.
- Estacionales: crear 45-60 días ANTES del pico (DANA: sep; calor: may; nieve: nov; V16: ya).
- Nunca repetir título de página existente (canonical cannibalización).
