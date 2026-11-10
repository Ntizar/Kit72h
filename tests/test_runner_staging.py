# -*- coding: utf-8 -*-
"""El runner solo commitea salidas declaradas; nunca `git add -A`."""
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
import cron_git


class TestDeclaracion(unittest.TestCase):
    def test_scripts_del_cron_tienen_paths(self):
        for nombre in ("noticias.py", "instrumentar-analitica.py",
                       "kit72h-analiticas.py", "generar-seo.py", "prerender.py"):
            self.assertIsNotNone(cron_git.paths_for(nombre), nombre)
            self.assertTrue(cron_git.paths_for(nombre))

    def test_desconocido_no_se_commitea(self):
        self.assertIsNone(cron_git.paths_for("script_nuevo.py"))
        self.assertIsNone(cron_git.paths_for("/tmp/otro.py"))


class TestStagingReal(unittest.TestCase):
    def test_solo_entran_las_salidas_declaradas(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            (repo / "data").mkdir()
            (repo / "data" / "noticias.json").write_text("{}", encoding="utf-8")
            (repo / "data" / "alertas-es.json").write_text("{}", encoding="utf-8")
            (repo / "secreto.txt").write_text("cambio ajeno", encoding="utf-8")

            paths = cron_git.existentes(repo, cron_git.paths_for("noticias.py"))
            subprocess.run(["git", "add", "--"] + paths, cwd=repo, check=True)
            staged = subprocess.check_output(
                ["git", "diff", "--cached", "--name-only"], cwd=repo, text=True).splitlines()
            self.assertEqual(sorted(staged), ["data/alertas-es.json", "data/noticias.json"])
            self.assertNotIn("secreto.txt", staged)


if __name__ == "__main__":
    unittest.main()
