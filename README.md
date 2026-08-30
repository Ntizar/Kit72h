# Kit72h

Kits de emergencia para 72 horas basados en recomendaciones oficiales de la Unión Europea y de Protección Civil.

## Qué es
Web estática con kits de emergencia por escenario: DANA, apagón, coche, hogar, montaña, ola de calor, evacuación y kit básico 72h. Cada kit incluye lista de productos con enlaces de afiliado de Amazon y guía antes/durante/después.

## Estructura
```
kit72h/
├── index.html              ← entry point
├── css/styles.css          ← estilos
├── js/
│   ├── state.js            ← carga de datos
│   ├── ui.js               ← render de vistas
│   └── main.js             ← orquestador
├── data/kits.json          ← kits + productos + fuentes
├── SPEC.md                 ← spec del proyecto
└── .github/workflows/pages.yml
```

## Cómo editar los kits
Todo el contenido vive en `data/kits.json`. Añade o edita un kit y el sitio lo muestra al instante (no hay build). Los enlaces de afiliado son placeholders `AMAZON-URL-*` hasta que se sustituyan por enlaces reales de Amazon Afiliados.

## Deploy
GitHub Pages vía `actions/deploy-pages@v4` (push a main despliega automáticamente).

## Créditos
Hecho con ❤️ por David Antizar
