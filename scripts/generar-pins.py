#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — Pinterest Pin Generator para atraer tráfico masivo.

Genera HTML estático de pins optimizados para Pinterest:
- Tarjetas visuales estilo Aurora 7 (1000x1500px, ratio 2:3)
- Cobertura de KITS y blog entries
- Cada pin enlazando a una página del sitio

Pinterest = fuente de tráfico orgánico masivo y de LARGA VIDA (meses/años).
"""

import json
import os
import re
import subprocess
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PINTOUT_DIR = RAIZ / "pintout"
PINTOUT_DIR.mkdir(exist_ok=True)
IDENT = ["-c", "user.name=Mastermind", "-c", "user.email=bot@kit72h.local"]


def run(*args, timeout=300):
    return subprocess.run(args, cwd=RAIZ, capture_output=True, text=True, timeout=timeout)


def git(*args):
    return run("git", *args)


COLORES = [
    ("#D14B27", "#F1EBDF"),
    ("#EFA02B", "#F1EBDF"),
    ("#26201A", "#F1EBDF"),
    ("#D14B27", "#FFFFFF"),
    ("#EFA02B", "#0E0C09"),
    ("#D14B27", "#0E0C09"),
]


def recortar(texto, max_len):
    """Recorta por palabra completa (nunca corta a mitad de palabra)."""
    texto = (texto or "").strip()
    if len(texto) <= max_len:
        return texto
    corte = texto[:max_len].rsplit(" ", 1)[0].rstrip(" ,;:.-")
    return (corte or texto[:max_len]) + "…"


def generate_pin_html(title, subtitle, color_idx=0, show_cta=True, url=""):
    bg, fg = COLORES[color_idx % len(COLORES)]
    title_safe = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    subtitle_safe = subtitle.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="pin-url" content="{url}">
<meta name="pin-ratio" content="2:3">
<title>Pin — Kit72h</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=IBM+Plex+Mono:wght@400;700&amp;display=swap');
body {{ margin: 0; display: flex; align-items: center; justify-content: center;
  width: 1000px; height: 1500px; background: {bg}; font-family: 'IBM Plex Mono', monospace; }}
.container {{ max-width: 800px; padding: 60px 40px; text-align: center; color: {fg}; }}
.logo {{ font-family: 'Anton', sans-serif; font-size: 42px; letter-spacing: 3px;
  margin-bottom: 40px; text-transform: uppercase; border-bottom: 4px solid {fg};
  display: inline-block; padding-bottom: 8px; }}
.logo .accent {{ color: #EFA02B; }}
.title {{ font-family: 'Anton', sans-serif; font-size: 52px; line-height: 1.15;
  text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px; color: {fg}; }}
.subtitle {{ font-size: 20px; line-height: 1.5; opacity: 0.8; margin-bottom: 40px;
  max-width: 600px; margin-left: auto; margin-right: auto; color: {fg}; }}
.divider {{ height: 2px; background: linear-gradient(90deg, transparent, {fg}, transparent);
  margin: 20px 0; }}
.cta {{ font-size: 18px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase;
  border: 2px solid {fg}; padding: 16px 32px; display: inline-block;
  opacity: 0.7; margin-top: 20px; }}
.pin-id {{ position: absolute; bottom: 30px; right: 40px; font-size: 13px;
  opacity: 0.75; letter-spacing: 2px; font-weight: 700; }}
.icon-row {{ display: flex; justify-content: center; gap: 20px; margin: 30px 0 10px;
  font-size: 32px; opacity: 0.5; }}
</style>
</head>
<body data-url="{url}">
<div class="container">
  <div class="logo">KIT<span class="accent">72H</span></div>
  <div class="title">{title_safe}</div>
  {f'<div class="subtitle">{subtitle_safe}</div>' if subtitle else ''}
  <div class="divider"></div>
  <div class="icon-row"><span>📋</span><span>🔥</span><span>⚡</span><span>💧</span><span>🏠</span></div>
  {f'<div class="cta">LEER EL KIT →</div>' if show_cta else ''}
</div>
<div class="pin-id">kit72h.com</div>
</body>
</html>'''


def generar_pins():
    kits_data = json.loads((RAIZ / "data" / "kits.json").read_text(encoding="utf-8"))
    blog_data = json.loads((RAIZ / "data" / "blog.json").read_text(encoding="utf-8"))
    existing = json.loads((RAIZ / "data" / "pins-generados.json").read_text(encoding="utf-8")) if (RAIZ / "data" / "pins-generados.json").exists() else {"pins": []}
    existing_slugs = {p["slug"] for p in existing.get("pins", [])}
    pins_created = []

    kit_emojis = {
        "kit-basico-72h": "🎒", "kit-dana": "🌊", "kit-apagon": "⚡",
        "kit-coche": "🚗", "kit-hogar": "🏠", "kit-montana": "🏔️",
        "kit-calor": "☀️", "kit-evacuacion": "🚨", "kit-bebe": "👶",
        "kit-mayores": "👴", "kit-mascotas": "🐾", "kit-frio": "❄️",
        "kit-terremoto": "💥", "kit-incendio": "🔥", "huerto-autosuficiencia": "🌱",
        "kit-30-dias": "📦", "kit-kit-profesional": "🏭",
        "kit-starlink": "📡", "kit-comunicacion": "📻",
    }

    for kit in kits_data.get("kits", []):
        slug = kit["slug"]
        if f"pin-kit-{slug}" in existing_slugs:
            continue
        emoji = kit_emojis.get(slug, "📋")
        titulo = recortar(f"{emoji} {kit['titulo']}", 60)
        resumen = recortar(re.sub(r'<[^>]+>', '', kit.get("resumen", "")).replace("&", ""), 90)
        url = f"https://kit72h.com/kit/{slug}/"
        pin_html = generate_pin_html(titulo, resumen, color_idx=kits_data["kits"].index(kit), url=url)
        pin_file = PINTOUT_DIR / f"pin-kit-{slug}.html"
        pin_file.write_text(pin_html, encoding="utf-8", newline="\n")
        pins_created.append({"slug": f"pin-kit-{slug}", "tipo": "kit", "titulo": kit["titulo"], "url": url, "emoji": emoji, "pin": pin_file.name})

    for i, entry in enumerate(blog_data.get("entradas", [])):
        slug = entry["slug"]
        if f"pin-blog-{slug}" in existing_slugs:
            continue
        titulo_full = entry.get("titulo", slug)
        if ":" in titulo_full:
            cabeza = titulo_full.split(":")[0].strip()
            if len(cabeza) >= 18:
                titulo_full = cabeza
        titulo = recortar(titulo_full, 60)
        resumen = recortar(entry.get("resumen", ""), 90)
        url = f"https://kit72h.com/blog/{slug}/"
        pin_html = generate_pin_html(titulo, resumen, color_idx=i + 20, url=url)
        pin_file = PINTOUT_DIR / f"pin-blog-{slug}.html"
        pin_file.write_text(pin_html, encoding="utf-8", newline="\n")
        pins_created.append({"slug": f"pin-blog-{slug}", "tipo": "blog", "titulo": entry.get("titulo", ""), "url": url, "emoji": "📖", "pin": pin_file.name})

    todos = existing.get("pins", []) + pins_created
    data_json = {
        "meta": {"ultima_generacion": date.today().isoformat(), "total": len(todos)},
        "pins": todos,
    }
    (RAIZ / "data" / "pins-generados.json").write_text(json.dumps(data_json, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Pins generados: {len(pins_created)} (índice total: {len(todos)})")
    for p in pins_created:
        print(f"  {p['emoji']} {p['tipo']}: {p['titulo'][:50]}")
    return pins_created


def encontrar_chromium():
    """Localiza un binario de Chromium/Chrome para renderizar los pins a PNG."""
    import glob
    import shutil

    candidatos = []
    for var in ("KIT72H_CHROME", "CHROME_PATH", "CHROMIUM_PATH"):
        ruta = os.environ.get(var)
        if ruta and Path(ruta).exists():
            candidatos.append(ruta)
    for exe in ("chromium", "chromium-browser", "google-chrome",
                "google-chrome-stable", "chrome", "msedge"):
        ruta = shutil.which(exe)
        if ruta:
            candidatos.append(ruta)
    local = os.environ.get("LOCALAPPDATA", "")
    patrones = [
        f"{local}/ms-playwright/chromium-*/chrome-win64/chrome.exe",
        f"{local}/ms-playwright/chromium-*/chrome-win/chrome.exe",
        str(Path.home() / ".cache/ms-playwright/chromium-*/chrome-linux/chrome"),
        str(Path.home() / ".cache/ms-playwright/chromium_headless_shell-*/chrome-linux/headless_shell"),
        str(Path.home() / "Library/Caches/ms-playwright/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium"),
        "/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome",
    ]
    for patron in patrones:
        candidatos.extend(sorted(glob.glob(patron), reverse=True))
    for c in candidatos:
        if c and Path(c).exists():
            return c
    return None


def renderizar_pins():
    """Renderiza cada pin HTML a PNG 1000x1500 listo para subir a Pinterest.

    Pinterest SOLO acepta imágenes: sin este paso los pins son inservibles.
    Se salta un pin si su PNG ya existe y es más reciente que el HTML.
    """
    chromium = encontrar_chromium()
    if not chromium:
        print("  ⚠️ Render: sin Chromium/Chrome disponible — solo HTML")
        return []

    indice_path = RAIZ / "data" / "pins-generados.json"
    indice = json.loads(indice_path.read_text(encoding="utf-8"))
    renderizados = []
    for pin in indice.get("pins", []):
        html = PINTOUT_DIR / pin["pin"]
        png = PINTOUT_DIR / (Path(pin["pin"]).stem + ".png")
        if not html.exists():
            continue
        if png.exists() and png.stat().st_mtime >= html.stat().st_mtime:
            pin["png"] = png.name
            continue
        try:
            run(
                chromium,
                "--headless=new", "--disable-gpu", "--no-sandbox",
                "--disable-dev-shm-usage", "--hide-scrollbars",
                "--force-device-scale-factor=1", "--window-size=1000,1500",
                "--virtual-time-budget=8000",
                f"--screenshot={png.as_posix()}",
                html.as_uri(),
                timeout=90,
            )
        except subprocess.TimeoutExpired:
            print(f"  ⚠️ timeout renderizando {png.name}")
            continue
        if png.exists() and png.stat().st_size > 5000:
            pin["png"] = png.name
            renderizados.append(png.name)
        else:
            print(f"  ⚠️ render vacío: {png.name}")
    indice.setdefault("meta", {})["png_total"] = sum(1 for p in indice["pins"] if p.get("png"))
    indice_path.write_text(json.dumps(indice, ensure_ascii=False, indent=2), encoding="utf-8")
    return renderizados


def main():
    pins = generar_pins()
    render = renderizar_pins()
    if render:
        print(f"PNG renderizados: {len(render)}")
    if not pins and not render:
        print("Pins: sin cambios")
        return
    git("add", "data/pins-generados.json", "pintout/")
    git(*IDENT, "commit", "-q", "-m", "feat: generar pins Pinterest para atraer tráfico")
    git("pull", "--rebase", "-q", "origin", "main")
    p = git("push", "-q", "origin", "main")
    if p.returncode == 0:
        print("  ✓ Push completado")
    else:
        print(f"  ⚠️ Push falló: {(p.stderr or '').strip()[:200]}")


if __name__ == "__main__":
    main()
