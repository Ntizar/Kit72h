# -*- coding: utf-8 -*-
"""Identidad de producto en el buscador: ni accesorios ni unidades que no casan."""
import importlib.util
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("buscador", RAIZ / "scripts" / "buscar-amazon.py")
buscador = importlib.util.module_from_spec(spec)
spec.loader.exec_module(buscador)


class TestIdentidadProducto(unittest.TestCase):
    def test_silbato_con_unidad_y_plural(self):
        self.assertTrue(buscador.titulo_compatible(
            "Silbato de emergencia 120dB",
            "Pack de 4 Silbatos de Emergencia Naranja 120 dB",
        ))

    def test_funda_no_sustituye_al_producto(self):
        self.assertFalse(buscador.titulo_compatible(
            "Silbato de emergencia 120dB",
            "Funda para silbato de emergencia 120 dB",
        ))

    def test_sin_la_unidad_no_vale(self):
        self.assertFalse(buscador.titulo_compatible(
            "Silbato de emergencia 120dB",
            "4 piezas Silbato de emergencia de rescate",
        ))

    def test_candidato_sin_stock_se_descarta(self):
        resultados = [{
            "asin": "B000000001", "precio": 10, "disponible": False,
            "titulo": "Silbato de emergencia 120 dB",
        }]
        self.assertIsNone(buscador.elegir_candidato("Silbato de emergencia 120dB", resultados, 5, 20))


if __name__ == "__main__":
    unittest.main()
