# -*- coding: utf-8 -*-
"""Regresión del contrato de la cola de publicación (auditoría 2026-11-10)."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SCRIPTS = RAIZ / "scripts"


def cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pub = cargar("kit72h_publicar_mod", SCRIPTS / "kit72h-publicar.py")


class TestDecisiones(unittest.TestCase):
    def test_sin_marca_publica(self):
        self.assertEqual(pub.decidir({"slug": "x"}, {}, {}), "publicar")

    def test_marca_antigua_es_conflicto(self):
        self.assertEqual(
            pub.decidir({"slug": "x"}, {"formato": "antiguo"}, {"cuerpo": "<p>hola</p>"}),
            "conflicto",
        )

    def test_hash_distinto_es_conflicto(self):
        marca = {"hash_sha256": pub.hash_cuerpo("<p>viejo</p>")}
        self.assertEqual(
            pub.decidir({"slug": "x"}, marca, {"cuerpo": "<p>nuevo</p>"}),
            "conflicto",
        )

    def test_hash_igual_permite_archivar(self):
        cuerpo = "<p>contenido publicado</p>"
        marca = {"hash_sha256": pub.hash_cuerpo(cuerpo)}
        self.assertEqual(
            pub.decidir({"slug": "x"}, marca, {"cuerpo": cuerpo}),
            "archivar_verificado",
        )


class TestGateEditorial(unittest.TestCase):
    def _entrada(self, palabras=900, fuentes=2, mejora=False):
        return {
            "slug": "prueba",
            "titulo": "Prueba",
            "cuerpo": "<p>" + ("palabra " * palabras) + "</p>",
            "fuente": [{"nombre": "A", "url": f"https://example.com/{i}"}
                       for i in range(fuentes)],
            "_mejora": mejora,
        }

    def test_entrada_valida_pasa(self):
        self.assertEqual(pub.validar_entrada(self._entrada()), [])

    def test_stub_sin_fuentes_no_pasa(self):
        faltas = pub.validar_entrada(self._entrada(palabras=20, fuentes=0))
        self.assertTrue(any("palabras" in f for f in faltas))
        self.assertTrue(any("fuentes" in f for f in faltas))

    def test_revamp_exige_1200(self):
        faltas = pub.validar_entrada(self._entrada(palabras=1000, mejora=True))
        self.assertTrue(any("1200" in f for f in faltas))


class TestRestaurarCola(unittest.TestCase):
    def test_si_falla_el_commit_vuelve_a_la_cola(self):
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            entrada = raiz / "_entrada.json"
            destino = raiz / "publicados" / "2026-11-10-x.json"
            destino.parent.mkdir()
            destino.write_text('{"slug":"x"}', encoding="utf-8")
            original = pub.ENTRADA
            pub.ENTRADA = entrada
            try:
                pub.restaurar_cola(destino)
            finally:
                pub.ENTRADA = original
            self.assertEqual(json.loads(entrada.read_text(encoding="utf-8"))["slug"], "x")


class TestArchivo(unittest.TestCase):
    def test_archivar_conserva_cuerpo(self):
        with tempfile.TemporaryDirectory() as td:
            plan = Path(td)
            entrada = plan / "_entrada.json"
            datos = {"slug": "montana", "cuerpo": "<p>no perder esto</p>"}
            entrada.write_text(json.dumps(datos), encoding="utf-8")
            destino = pub.archivar(entrada, plan, datetime(2026, 11, 10, tzinfo=timezone.utc))
            self.assertFalse(entrada.exists())
            self.assertTrue(destino.exists())
            self.assertEqual(json.loads(destino.read_text(encoding="utf-8")), datos)
            self.assertIn("2026-11-10-montana.json", destino.name)


class TestRutasStaging(unittest.TestCase):
    def test_entrada_archivada_no_rompe_el_add(self):
        """El fallo real: _entrada.json untracked desaparece y git add aborta."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "data").mkdir()
            (raiz / "data" / "blog.json").write_text("{}", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=raiz, check=True)
            original = pub.REPO
            pub.REPO = raiz
            try:
                validas = pub.rutas_validas(
                    ["data/blog.json", "notes/plan-crecimiento/_entrada.json"]
                )
            finally:
                pub.REPO = original
            self.assertEqual(validas, ["data/blog.json"])


class TestConflictoNoBorra(unittest.TestCase):
    def test_main_devuelve_2_y_conserva_entrada(self):
        """Reproduce el fallo real: marca vieja sin hash + revamp en cola."""
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            plan = repo / "notes" / "plan-crecimiento"
            plan.mkdir(parents=True)
            entrada = plan / "_entrada.json"
            entrada.write_text(json.dumps({"slug": "revamp", "cuerpo": "<article>nuevo</article>"}),
                               encoding="utf-8")
            (plan / ".publicado-revamp").write_text("publicado\n", encoding="utf-8")
            env = dict(os.environ, KIT72H_REPO=str(repo))
            r = subprocess.run([sys.executable, str(SCRIPTS / "kit72h-publicar.py")],
                               capture_output=True, text=True, env=env, timeout=30)
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            self.assertIn("CONFLICTO", r.stdout)
            self.assertTrue(entrada.exists(), "la entrada NUNCA se borra ante un conflicto")


if __name__ == "__main__":
    unittest.main()
