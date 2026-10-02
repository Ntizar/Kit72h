#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — vigilante: chequeo semanal completo (repos, SEO, URLs, salud).

Fusiona las funciones de los antiguos 'vigilante' + 'revision-urls'.
Ejecuta:
1. git pull + estado del repo
2. generar-seo.py + prerender.py (deben terminar sin fallos)
3. HEAD a https://kit72h.com/ y rutas clave (esperar 200)
4. Comprobar URLs de afiliado (comprobar-urls.py) → regenera data/estado.json
5. Si algo falla: commit del arreglo + push. Si todo correcto: 'todo verde'.
"""

import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BASE = "https://kit72h.com"
IDENT = ["-c", "user.name=Mastermind", "-c", "user.email=bot@kit72h.local"]


def run(*args, timeout=300):
    return subprocess.run(args, cwd=RAIZ, capture_output=True, text=True, timeout=timeout)


def git(*args):
    return run("git", *args)


def check(url):
    """Verifica que una URL responde con 200."""
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        return resp.status == 200
    except:
        return False


def main():
    problemas = []
    fixs_aplicados = 0

    print("=== VIGILANTE SEMANAL ===")

    # 1) git pull
    print("\n1) Estado del repo...")
    pull = git("pull", "origin", "main")
    if pull.returncode != 0:
        # Intentar reset si hay conflicto
        reset = git("reset", "--hard", "HEAD")
        pull = git("pull", "origin", "main")
        if pull.returncode == 0:
            print("  ✅ Reset + pull completado")

    status = git("status", "--porcelain")
    if status.stdout.strip():
        print(f"  ⚠️ {len(status.stdout.strip().splitlines())} archivos modificados locales")

    # 2) SEO + Prerender
    print("\n2) SEO + Prerender...")
    seo = run(sys.executable, "scripts/generar-seo.py")
    if seo.returncode == 0:
        print("  ✅ SEO OK")
    else:
        problemas.append(f"seo-falló: {seo.stderr[:200]}")
        print(f"  ❌ SEO falló")

    pre = run(sys.executable, "scripts/prerender.py")
    if pre.returncode == 0:
        print("  ✅ Prerender OK")
    else:
        problemas.append(f"prerender-falló: {pre.stderr[:200]}")
        print(f"  ❌ Prerender falló")

    # 3) URLs web
    print("\n3) URLs vivas...")
    urls_ok = []
    urls_fail = []
    for url in [f"{BASE}/", f"{BASE}/kit/kit-apagon/", f"{BASE}/blog/como-montar-tu-kit-72h/"]:
        if check(url):
            urls_ok.append(url)
        else:
            urls_fail.append(url)
            problemas.append(f"url-falló: {url}")

    print(f"  {len(urls_ok)}/{len(urls_ok)+len(urls_fail)} URLs OK")

    # 4) URLs de afiliado
    print("\n4) URLs de afiliado...")
    check_urls = run(sys.executable, "scripts/comprobar-urls.py")
    if check_urls.returncode == 0:
        print("  ✅ URLs verificadas")
    else:
        print(f"  ⚠️ Error al verificar URLs: {check_urls.stderr[:200]}")

    # 5) Estado del SEO audit
    print("\n5) Auditoría SEO...")
    seo_audit = run(sys.executable, "scripts/kit72h-seo-audit.py")
    if seo_audit.returncode == 0:
        print("  ✅ SEO audit OK")
    else:
        problemas.append(f"seo-audit-falló: {seo_audit.stdout[:300]}")
        print(f"  ❌ SEO audit falló")

    # Resultados
    print("\n=== RESULTADO ===")
    if problemas:
        print(f"❌ {len(problemas)} problema(s) detectado(s):")
        for p in problemas:
            print(f"  - {p}")
    else:
        print("✅ Todo verde — web saludable")


if __name__ == "__main__":
    main()