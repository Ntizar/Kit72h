#!/usr/bin/env python3
"""Ensayo del corte por agotamiento en el buscador de kit72h (sin red, sin tocar produccion).

Tres comprobaciones:
  1) unitaria de las funciones puras (registrar_intento / n_agotado)
  2) transicion en un arbol de juguete: con 3 items a n=3 salen de la rotacion y el conteo baja
  3) valvula humana: --reabrir los devuelve
Uso: python3 scripts/verificar-buscador.py   (0 = todo bien; no toca produccion)
"""
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

REAL = pathlib.Path(__file__).resolve().parents[1]      # el repo donde vive este arnes
T = pathlib.Path(tempfile.mkdtemp(prefix="k72-ensayo-"))  # TMPDIR (aqui, el scratch de Hermes)
PY = sys.executable


def carga_modulo(ruta):
    spec = importlib.util.spec_from_file_location("ba", ruta)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    fallos = []

    # ---------- 1) unitaria de la logica pura ----------
    m = carga_modulo(REAL / "scripts" / "buscar-amazon.py")
    import datetime
    hoy = datetime.date(2026, 10, 12)
    ints = {}
    seq = [m.registrar_intento("k|x", ints, hoy) for _ in range(3)]
    print("1) registrar_intento 3 noches ->", seq, "| guardado:", json.dumps(ints["k|x"], ensure_ascii=False))
    if seq != [1, 2, 3]:
        fallos.append("el contador no suma 1,2,3")
    if ints["k|x"].get("primera") != ints["k|x"].get("ultima"):
        fallos.append("primera/ultima mal")
    casos = [(m.n_agotado("k|x", ints, 3), True, "n=3 con tope 3 -> agotado"),
             (m.n_agotado("k|x", ints, 0), False, "tope 0 -> nunca agotado"),
             (m.n_agotado("k|y", ints, 3), False, "sin intentos -> no agotado")]
    for got, esp, txt in casos:
        print("   ", "ok " if got == esp else "MAL", txt, "->", got)
        if got != esp:
            fallos.append(txt)

    # ---------- arbol de juguete ----------
    if T.exists():
        shutil.rmtree(T)
    (T / "scripts").mkdir(parents=True)
    (T / "data").mkdir(parents=True)
    for f in ("kits.json", "propuestas-fichas.json", "buscador-log.json"):
        shutil.copy(REAL / "data" / f, T / "data" / f)
    shutil.copy(REAL / "scripts" / "buscar-amazon.py", T / "scripts" / "buscar-amazon.py")

    def corre(*args):
        r = subprocess.run([PY, str(T / "scripts" / "buscar-amazon.py"), *args],
                           capture_output=True, text=True, timeout=180)
        return r.returncode, r.stdout + r.stderr

    def resumen(salida):
        for ln in salida.splitlines():
            if ln.startswith("Pendientes:"):
                d = dict(x.strip().split(": ")[0:2] for x in ln.split("|")) if False else None
                return ln
        return "(sin linea de cabecera)"

    # estado inicial: nadie agotado
    rc, out = corre("--simular")
    cab0 = [l for l in out.splitlines() if l.startswith("Pendientes:")]
    print("\n2) sin intentos:", rc, cab0[0] if cab0 else out[:200])
    if rc != 0 or not cab0 or "agotados: 0" not in cab0[0]:
        fallos.append("el ensayo inicial no da agotados: 0")

    # doctoro el log: los 3 primeros pendientes con 3 noches a cuestas
    kits = json.loads((T / "data" / "kits.json").read_text(encoding="utf-8"))
    log = json.loads((T / "data" / "buscador-log.json").read_text(encoding="utf-8"))
    log["intentos"] = {}
    props = json.loads((T / "data" / "propuestas-fichas.json").read_text(encoding="utf-8"))
    resueltos = set(log.get("resueltos") or [])
    claves = []
    for kit in kits["kits"]:
        for s in kit["secciones"]:
            for i in s["items"]:
                prod, url = i.get("producto", ""), i.get("afiliado") or ""
                if not (("amazon.es/s?" in url) or not url or i.get("es_busqueda")):
                    continue
                if m.coletilla_no_compra(prod):
                    continue
                c = f"{kit['slug']}|{prod}"
                # mismas condiciones que el script para estar en `pendientes`
                if (props.get(c) or {}).get("url") or prod in resueltos:
                    continue
                claves.append(c)
    assert len(claves) >= 6, "el árbol de juguete necesita al menos 6 pendientes reales (%d)" % len(claves)
    for c in claves[:3]:
        log["intentos"][c] = {"n": 3, "primera": "2026-10-01", "ultima": "2026-10-11"}
    (T / "data" / "buscador-log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print("   doctorados 3 items con n=3:", [c[:48] for c in claves[:3]])

    rc, out = corre("--simular")
    cab1 = [l for l in out.splitlines() if l.startswith("Pendientes:")]
    print("   con 3 agotados:", cab1[0] if cab1 else out[:200])
    pend_antes = int(cab0[0].split("Pendientes: ")[1].split(" ")[0])
    pend_ahora = int(cab1[0].split("Pendientes: ")[1].split(" ")[0]) if cab1 else -1
    if "agotados: 3" not in (cab1[0] if cab1 else ""):
        fallos.append("no cuenta 3 agotados")
    if pend_ahora != pend_antes - 3:
        fallos.append(f"los pendientes no bajan 3 ({pend_antes} -> {pend_ahora})")
    for c in claves[:3]:
        if any(c[:20] in l for l in out.splitlines() if "intentos=" in l):
            fallos.append("un agotado sigue entrando en el lote: " + c[:40])

    # ---------- 3) valvula humana ----------
    trozo = claves[0].split("|")[1][:18]
    rc, out = corre("--reabrir", trozo)
    print("3) --reabrir '%s':" % trozo, rc, out.strip().splitlines()[-1][:120])
    rc, out = corre("--simular")
    cab2 = [l for l in out.splitlines() if l.startswith("Pendientes:")]
    print("   tras reabrir:", cab2[0] if cab2 else out[:200])
    if "agotados: 2" not in (cab2[0] if cab2 else ""):
        fallos.append("--reabrir no devolvio el item a la rotacion")

    # ---------- produccion intacta ----------
    r = subprocess.run(["git", "status", "--porcelain"], cwd=REAL, capture_output=True, text=True)
    sucio = [l for l in r.stdout.splitlines() if not l.endswith("scripts/buscar-amazon.py")]
    print("\nproduccion: solo el script tocado ->", "si" if not sucio else "NO: " + str(sucio))

    shutil.rmtree(T, ignore_errors=True)        # el arbol de juguete no se queda por ahi
    print()
    print("FALLOS: " + " | ".join(fallos) if fallos else "ENSAYO OK: contador, corte por agotado y --reabrir funcionan")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
