#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — publicador de la entrada encolada por el consejero.

Lo ejecuta el cron `kit72h-publicador` (modo script, --no-agent) en el VM. Lee
`notes/plan-crecimiento/_entrada.json` (que escribe el consejero LLM a las
07:30) y la publica: upsert en blog.json, materializa el directorio, regenera
home+SEO, hornea con Playwright y pasa el gate. Si el gate falla NO commitea.

Contrato de cola (auditoría 2026-11-10):
- Una marca `.publicado-<slug>` NUNCA autoriza a borrar una entrada nueva.
- Solo se archiva una entrada cuando la marca contiene el SHA-256 del cuerpo
  realmente publicado y ese hash coincide con `data/blog.json`.
- Un conflicto deja la entrada intacta y sale con código 2 (visible al cron).
- Cola vacía sale con 0 y una línea explícita; nunca finge silencio.

Salida: recibo con slug, palabras, commit, push y URL.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("ARNES_EXENTO", "1")  # cron que empuja a main por diseño
REPO = Path(os.environ.get("KIT72H_REPO", Path(__file__).resolve().parents[1])).resolve()
PLAN = REPO / "notes" / "plan-crecimiento"
ENTRADA = PLAN / "_entrada.json"

IDENT = ["-c", "user.name=Mastermind", "-c", "user.email=bot@kit72h.local"]
# SOLO estos paths: nunca `git add -A` (arrastraría cambios ajenos del árbol).
PATHS = ["data/blog.json", "blog", "kit", "fuentes", "zona", "index.html",
         "noticias", "sitemap.xml", "feed.xml", "llms.txt", "llms-full.txt",
         "notes/mapa-keywords.md"]


def git(*args, timeout=300):
    return subprocess.run(["git", "-C", str(REPO)] + list(args),
                          capture_output=True, text=True, timeout=timeout)


def palabras_html(cuerpo: str) -> int:
    return len(re.sub(r"<[^>]+>", " ", cuerpo or "").split())


def hash_cuerpo(cuerpo: str) -> str:
    """Huella estable del HTML publicado (normaliza solo extremos)."""
    return hashlib.sha256((cuerpo or "").strip().encode("utf-8")).hexdigest()


def validar_entrada(entrada: dict) -> list[str]:
    """Gate editorial mínimo antes de encolar: cuerpo real y fuentes citadas.

    No sustituye la revisión humana de afirmaciones delicadas, pero impide que
    una entrada vacía, un stub o un texto sin fuentes llegue a producción.
    """
    faltas: list[str] = []
    if not (entrada.get("titulo") or "").strip():
        faltas.append("falta título")
    if not (entrada.get("slug") or "").strip():
        faltas.append("falta slug")
    cuerpo = entrada.get("cuerpo") or ""
    minimo = 1200 if entrada.get("_mejora") else 800
    if palabras_html(cuerpo) < minimo:
        faltas.append(f"cuerpo de {palabras_html(cuerpo)} palabras; mínimo {minimo}")
    fuentes = entrada.get("fuente") or entrada.get("fuentes") or []
    urls = [f.get("url", "") for f in fuentes if isinstance(f, dict)]
    validas = [u for u in urls if re.match(r"^https?://", u)]
    if len(validas) < 2:
        faltas.append("menos de 2 fuentes oficiales con URL")
    return faltas


def leer_marca(marca: Path) -> dict:
    """Devuelve la marca. Las marcas antiguas ('publicado\\n') no prueban nada."""
    if not marca.exists():
        return {}
    try:
        datos = json.loads(marca.read_text(encoding="utf-8"))
        return datos if isinstance(datos, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {"formato": "antiguo"}


def entrada_blog(slug: str) -> dict:
    try:
        blog = json.loads((REPO / "data" / "blog.json").read_text(encoding="utf-8"))
        return next((e for e in blog.get("entradas", []) if e.get("slug") == slug), {})
    except (OSError, json.JSONDecodeError):
        return {}


def decidir(entrada: dict, marca: dict, publicado: dict) -> str:
    """`publicar`, `archivar_verificado` o `conflicto`.

    La marca solo vale si guarda el hash del cuerpo y coincide con la entrada
    actual de blog.json. Cualquier marca sin hash es un conflicto a revisar.
    """
    if not marca:
        return "publicar"
    esperado = marca.get("hash_sha256")
    actual = hash_cuerpo(publicado.get("cuerpo") or "") if publicado else ""
    if esperado and actual and esperado == actual:
        return "archivar_verificado"
    return "conflicto"


def archivar(entrada: Path, plan: Path, ahora: datetime) -> Path:
    """Mueve la cola a publicados/ sin destruir su contenido."""
    destino_dir = plan / "publicados"
    destino_dir.mkdir(parents=True, exist_ok=True)
    datos = json.loads(entrada.read_text(encoding="utf-8"))
    slug = datos.get("slug") or "entrada"
    destino = destino_dir / f"{ahora.date().isoformat()}-{slug}.json"
    if destino.exists():
        destino = destino_dir / (f"{ahora.strftime('%Y%m%dT%H%M%SZ')}-{slug}.json")
    shutil.move(str(entrada), str(destino))
    return destino


def rutas_validas(rutas: list[str]) -> list[str]:
    """Paths que `git add` puede aceptar: existentes o tracked-borrados."""
    return [
        ruta for ruta in dict.fromkeys(rutas)
        if (REPO / ruta).exists()
        or git("ls-files", "--error-unmatch", "--", ruta).returncode == 0
    ]


def publicar_cambios(mensaje: str, extra: tuple[str, ...] = ()) -> tuple[int, str]:
    """Commit y push de los paths del publicador. Devuelve (rc, sha)."""
    # `_entrada.json` puede no estar trackeada: tras archivarla su path ya no
    # existe y `git add` abortaría TODO el staging. Solo añadimos paths que
    # existan o que Git ya conozca (deleted tracked).
    validas = rutas_validas(list(PATHS) + list(extra))
    agregado = git("add", "--", *validas)
    if agregado.returncode != 0:
        print("❌ git add falló: " + (agregado.stderr or "").strip()[:200])
        return 1, ""
    if not git("status", "--porcelain").stdout.strip():
        return 0, ""
    commit = git(*IDENT, "commit", "-m", mensaje)
    if commit.returncode != 0:
        print("❌ commit falló: " + (commit.stderr or commit.stdout).strip()[:200])
        return 1, ""
    sha = git("rev-parse", "--short", "HEAD").stdout.strip()
    push = git("push", "-q", "origin", "HEAD:main")
    if push.returncode != 0:
        # Un cron hermano puede haber empujado mientras horneábamos.
        if git("pull", "--rebase", "-q", "origin", "main").returncode != 0:
            print("❌ rebase falló (conflicto): commit local conservado, revisar a mano")
            return 1, sha
        push = git("push", "-q", "origin", "HEAD:main")
        if push.returncode != 0:
            print("❌ push falló: " + (push.stderr or "").strip()[:200])
            return 1, sha
    return 0, sha


def main() -> int:
    if not ENTRADA.exists():
        print("publicador: cola vacía (no hay _entrada.json)")
        return 0
    try:
        entrada = json.loads(ENTRADA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as ex:
        print("publicador: _entrada.json ilegible (%s); se conserva" % ex)
        return 1
    slug = entrada.get("slug", "")
    if not slug:
        print("publicador: _entrada.json sin slug; se conserva")
        return 1

    marca_path = PLAN / (".publicado-" + slug)
    marca = leer_marca(marca_path)
    publicado = entrada_blog(slug)
    accion = decidir(entrada, marca, publicado)
    if accion == "conflicto":
        print("❌ CONFLICTO de cola: «%s» tiene marca .publicado pero el contenido "
              "no coincide con el hash publicado. Entrada CONSERVADA en %s. "
              "Revisar el borrador y retirar la marca a mano." % (slug, ENTRADA))
        return 2
    if accion == "archivar_verificado":
        destino = archivar(ENTRADA, PLAN, datetime.now(timezone.utc))
        rc, sha = publicar_cambios("consejero: archivar cola ya publicada «%s»" % slug,
                                   (str(ENTRADA.relative_to(REPO)), "notes/plan-crecimiento/publicados",
                                    str(marca_path.relative_to(REPO))))
        if rc == 0:
            print("publicador: «%s» ya estaba publicado con hash válido; cola archivada "
                  "en %s · commit %s" % (slug, destino.relative_to(REPO), sha or "sin cambios"))
        return rc

    faltas = validar_entrada(entrada)
    if faltas:
        print("❌ GATE EDITORIAL: «%s» no se publica; entrada CONSERVADA. %s"
              % (slug, "; ".join(faltas)))
        return 1

    sys.path.insert(0, str(REPO / "scripts"))
    import importlib
    consejero = importlib.import_module("kit72h-consejero")  # noqa

    rc = consejero.publicar(str(ENTRADA))
    if rc != 0:
        print("❌ Publicador: la publicación de «%s» FALLÓ (ver arriba). "
              "NO se commitea y la entrada se conserva." % slug)
        return 1

    ahora = datetime.now(timezone.utc)
    publicado = entrada_blog(slug)
    cuerpo = publicado.get("cuerpo") or ""
    if not cuerpo:
        print("❌ «%s» no aparece en data/blog.json tras publicar; entrada conservada" % slug)
        return 1
    marca_path.write_text(json.dumps({
        "slug": slug,
        "titulo": publicado.get("titulo", ""),
        "publicado_en": ahora.isoformat(timespec="seconds"),
        "palabras_html": palabras_html(cuerpo),
        "hash_sha256": hash_cuerpo(cuerpo),
        "url": "https://kit72h.com/blog/%s/" % slug,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    destino = archivar(ENTRADA, PLAN, ahora)
    rc, sha = publicar_cambios("consejero: publicar «%s» (blog)" % slug,
                               (str(ENTRADA.relative_to(REPO)), "notes/plan-crecimiento/publicados",
                                str(marca_path.relative_to(REPO))))
    if rc != 0:
        return rc

    ix = subprocess.run([sys.executable, "scripts/indexnow.py", "--desde-git", "HEAD~1"],
                        cwd=REPO, capture_output=True, text=True, timeout=90)
    nota_ix = (ix.stdout.strip().splitlines() or [""])[-1][:80]
    print("🚀 Publicado /blog/%s/ · %d palabras · commit %s · push ✔ · URL %s%s"
          % (slug, palabras_html(cuerpo), sha or "sin cambios",
             "https://kit72h.com/blog/%s/" % slug,
             (" · " + nota_ix) if nota_ix else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
