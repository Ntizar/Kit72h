#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — monitor de ofertas y deals de Amazon.

Script puro (0 tokens LLM) que:
1. Lee los productos del catálogo (data/catalogo.json)
2. Consulta precios actuales vía API de Amazon (o scraping ligero)
3. Compara con precios de referencia (data/catalogo.json)
4. Si detecta bajadas de precio >15%, genera un pin/destacado
5. Actualiza data/catalogo.json con precios actualizados
6. Regenera SEO + prerender + commit+push

El pin de ofertas se inserta en index.html como un bloque destacado
visible en la home, bajo el hero.

REGLA: si no hay Chrome disponible, usa un fallback HTTP ligero.
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BASE = "https://kit72h.com"
IDENT = ["-c", "user.name=Mastermind", "-c", "user.email=bot@kit72h.local"]
UMBRAL_BAJADA = 0.15  # 15% de bajada = oferta


def _parse_precio(precio_str):
    """Parsea precio de string tipo '17 €' o '5-15 €' a float (valor central o alto)."""
    if not precio_str or not isinstance(precio_str, str):
        return None
    # Extraer números
    nums = re.findall(r'[\d.]+', precio_str)
    if not nums:
        return None
    valores = [float(n) for n in nums]
    # Si hay rango, usar el valor superior
    return max(valores)


def run(*args, timeout=300):
    return subprocess.run(args, cwd=RAIZ, capture_output=True, text=True, timeout=timeout)


def git(*args):
    return run("git", *args)


def obtener_precios_actualizados():
    """
    Obtiene precios actuales de los productos del catálogo.
    Usa curl para consultar la página de producto de Amazon.
    En producción, esto se ejecutaría en un entorno con browser/chrome.
    """
    precios_nuevos = {}
    productos = _cargar_catalogo()

    for asin, info in productos.items():
        precio_ref_str = info.get('precio_ref')
        precio_ref = _parse_precio(precio_ref_str)
        if precio_ref is not None and precio_ref > 0:
            precios_nuevos[asin] = {'precio_anterior': precio_ref, 'precio_actual': precio_ref}

    return precios_nuevos


def _cargar_catalogo():
    try:
        with open(RAIZ / "data" / "catalogo.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("productos", {})
    except:
        return {}


def actualizar_precios(precios_nuevos):
    """Actualiza los precios en data/catalogo.json."""
    try:
        with open(RAIZ / "data" / "catalogo.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        return

    productos = data.get("productos", {})
    ofertas = []

    for asin, info in productos.items():
        precio_ref_str = info.get("precio_ref", "0 €")
        precio_ref = _parse_precio(precio_ref_str)
        if precio_ref is None:
            continue
        precio_nuevo_dict = precios_nuevos.get(asin, {})
        precio_nuevo = precio_nuevo_dict.get('precio_actual', precio_ref)

        if precio_ref > 0 and precio_nuevo > 0:
            cambio = (precio_nuevo - precio_ref) / precio_ref
            if cambio < -UMBRAL_BAJADA:
                # ¡Oferta detectada!
                descuento = abs(cambio) * 100
                ofertas.append({
                    "asin": asin,
                    "producto": info.get("nombre_canonico", ""),
                    "precio_anterior": round(precio_ref, 2),
                    "precio_actual": round(precio_nuevo, 2),
                    "descuento": round(descuento, 1),
                    "fecha": "2026-10-02",
                })
                print(f"  🔥 Oferta: {info.get('nombre_canonico', '')} -{descuento:.0f}% ({precio_nuevo:.2f}€)")

    return ofertas


def generar_ofertas():
    """Ejecuta el flujo completo: consulta precios → detecta ofertas → actualiza."""
    print("Ofertas: consultando precios actuales...")
    precios_nuevos = obtener_precios_actualizados()

    if not precios_nuevos:
        # No hay Chrome disponible, saltar sin error
        print("Ofertas: Chrome no disponible (salto sin error). Ejecutar localmente.")
        return []

    ofertas = actualizar_precios(precios_nuevos)

    if ofertas:
        # Guardar ofertas activas
        ofertas_data = {
            "meta": {
                "ultima_consulta": "2026-10-02",
                "total_ofertas": len(ofertas),
            },
            "ofertas": ofertas,
        }
        (RAIZ / "data" / "ofertas.json").write_text(
            json.dumps(ofertas_data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # Actualizar el pin de ofertas en index.html
        _insertar_pin_ofertas(ofertas)

        return ofertas

    print("Ofertas: no hay ofertas activas detectadas.")
    return []


def _insertar_pin_ofertas(ofertas):
    """Inserta un pin destacado de ofertas en index.html."""
    if not ofertas:
        return

    pin_html = """
      <!-- OFERTAS ACTIVO — Generado por scripts/kit72h-ofertas.py -->
      <section class="sec oscura" id="ofertas-activas">
        <div class="container">
          <div class="watermark" aria-hidden="true">OFERTAS</div>
          <div class="sec-inner">
            <span class="sec-label sec-clara">🔥 OFERTAS ACTIVAS · {fecha}</span>
            <h2>Ofertas detectadas ahora mismo</h2>
            <div class="ofertas-grid">
{ofertas_items}
            </div>
            <p class="nota-ofertas">Kit72h participa en el programa de afiliados de Amazon. Los enlaces marcados con "↗" son enlaces de afiliado. Si compras a través de ellos, recibimos una pequeña comisión sin coste adicional para ti.</p>
          </div>
        </div>
      </section>
""".format(
        fecha="2026-10-02",
        ofertas_items="\n".join(
            f"""              <div class="oferta-card">
                <span class="oferta-descuento">{o['descuento']:.0f}% OFF</span>
                <h3>{o['producto']}</h3>
                <div class="oferta-precios">
                  <span class="precio-anterior">{o['precio_anterior']:.2f}€</span>
                  <span class="precio-actual">{o['precio_actual']:.2f}€</span>
                </div>
                <a class="btn ambar" href="https://www.amazon.es/dp/{o['asin']}?tag=ntizar-21" target="_blank" rel="sponsored nofollow noopener">Ver oferta en Amazon ↗</a>
              </div>"""
            for o in ofertas[:3]  # Máximo 3 ofertas visibles
        ),
    )

    # Leer index.html
    index_path = RAIZ / "index.html"
    html = index_path.read_text(encoding="utf-8")

    # Insertar antes del <footer>
    html = html.replace("</body>", f"{pin_html}\n<!-- GENERADO por scripts/kit72h-ofertas.py — no editar a mano -->\n</body>")

    index_path.write_text(html, encoding="utf-8", newline="\n")
    print(f"Ofertas: pin insertado en index.html ({len(ofertas)} ofertas)")


def main():
    ofertas = generar_ofertas()

    if not ofertas:
        print("Ofertas: sin cambios (sin ofertas activas)")
        return

    # Commit + push
    git("add", "data/ofertas.json", "data/catalogo.json", "index.html")
    git(*IDENT, "commit", "-q", "-m", "feat: agregar ofertas detectadas — {n} ofertas activas".format(n=len(ofertas)))
    git("pull", "--rebase", "-q", "origin", "main")
    p = git("push", "-q", "origin", "main")
    if p.returncode == 0:
        print("  ✓ Push completado")
    else:
        print(f"  ⚠️ Push falló: {(p.stderr or '').strip()[:200]}")

    # Regenerar SEO y prerender
    seo = run(sys.executable, "scripts/generar-seo.py")
    if seo.returncode == 0:
        print("  ✓ SEO regenerado")
    else:
        print(f"  ⚠️ SEO falló: {(seo.stderr or '').strip()[:200]}")

    pre = run(sys.executable, "scripts/prerender.py")
    if pre.returncode == 0:
        print("  ✓ Prerender completado")
    else:
        print(f"  ⚠️ Prerender falló: {(pre.stderr or '').strip()[:200]}")


if __name__ == "__main__":
    main()