# -*- coding: utf-8 -*-
"""La web no puede prometer «la mayor rebaja» si el algoritmo no la elige."""
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


class TestTextoOferta(unittest.TestCase):
    def test_sin_promesas_de_mayor_rebaja(self):
        js = (RAIZ / "js" / "ui.js").read_text(encoding="utf-8")
        prohibidas = [
            r"mayor rebaja",
            r"lo que más baja",
            r"el que más ha bajado",
            r"la mayor rebaja de hoy",
        ]
        for patron in prohibidas:
            self.assertIsNone(re.search(patron, js, re.I), patron)

    def test_etiqueta_y_criterio_honesto(self):
        js = (RAIZ / "js" / "ui.js").read_text(encoding="utf-8")
        self.assertIn("Selección de hoy", js)
        self.assertIn("No es necesariamente el mayor porcentaje", js)


if __name__ == "__main__":
    unittest.main()
