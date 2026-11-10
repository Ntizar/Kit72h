# -*- coding: utf-8 -*-
"""Regresión de precios: instantánea completa, sin arrastrar precios viejos."""
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("precios_mod", RAIZ / "scripts" / "precios-amazon.py")
precios = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(precios)


def dato(asin="A1", precio=100.0, antes=150.0, disponible=True, pct=33.3):
    return {
        "asin": asin, "titulo": f"Producto {asin}", "precio": precio,
        "precio_texto": f"{precio:.2f} €", "precio_antes": antes,
        "ahorro_pct": pct, "disponible": disponible, "imagen": None,
        "url": f"https://www.amazon.es/dp/{asin}?tag=ntizar-21",
    }


class Base(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.dir = Path(self.td.name)
        self.salida = self.dir / "precios.json"
        self.hist = self.dir / "precios-historico.json"
        self._orig = (precios.SALIDA, precios.HIST, precios.asins_de_kits,
                      precios.ama.cargar_env, precios.ama.items_por_asin)
        precios.SALIDA = self.salida
        precios.HIST = self.hist
        precios.ama.cargar_env = lambda: {"AMAZON_CREDENTIAL_ID": "x"}
        precios.asins_de_kits = lambda: {
            "A1": {"producto": "Uno", "kit": "kit1", "kit_titulo": "Kit 1",
                   "prioridad": "esencial", "precio_aprox": "100", "seccion": "s"},
            "B2": {"producto": "Dos", "kit": "kit1", "kit_titulo": "Kit 1",
                   "prioridad": "extra", "precio_aprox": "50", "seccion": "s"},
        }

    def tearDown(self):
        (precios.SALIDA, precios.HIST, precios.asins_de_kits,
         precios.ama.cargar_env, precios.ama.items_por_asin) = self._orig
        self.td.cleanup()


class TestAtomicidad(Base):
    def test_lote_fallido_no_escribe_y_conserva_json(self):
        previo = '{"meta":{"con_precio":99},"productos":{"VIEJO":{"precio":1}}}\n'
        self.salida.write_text(previo, encoding="utf-8")
        precios.ama.items_por_asin = lambda cfg, lote, pausa=0: {
            "ok": {"A1": dato("A1")}, "sin_datos": ["B2"],
            "lotes_fallidos": [["B2"]],
        }
        self.assertEqual(precios.refrescar(), 2)
        self.assertEqual(self.salida.read_text(encoding="utf-8"), previo)
        self.assertFalse((self.dir / "precios.json.tmp").exists())

    def test_asins_no_devueltos_no_heredan_precio(self):
        self.salida.write_text(json.dumps({"productos": {
            "A1": {"precio": 999, "precio_texto": "999 €"},
            "B2": {"precio": 888, "precio_texto": "888 €"},
        }}), encoding="utf-8")
        precios.ama.items_por_asin = lambda cfg, lote, pausa=0: {
            "ok": {"A1": dato("A1", 100)}, "sin_datos": ["B2"], "lotes_fallidos": [],
        }
        self.assertEqual(precios.refrescar(), 0)
        datos = json.loads(self.salida.read_text(encoding="utf-8"))
        self.assertEqual(set(datos["productos"]), {"A1"})
        self.assertEqual(datos["productos"]["A1"]["precio"], 100)
        self.assertEqual(datos["sin_precio"], {"B2": 0})
        self.assertEqual(datos["meta"]["con_precio"], 1)
        self.assertEqual(datos["meta"]["total_asins"], 2)

    def test_sin_ninguna_cotizacion_no_pisa_json(self):
        previo = '{"productos":{"VIEJO":{"precio":1}}}\n'
        self.salida.write_text(previo, encoding="utf-8")
        precios.ama.items_por_asin = lambda cfg, lote, pausa=0: {
            "ok": {}, "sin_datos": ["A1", "B2"], "lotes_fallidos": [],
        }
        self.assertEqual(precios.refrescar(), 2)
        self.assertEqual(self.salida.read_text(encoding="utf-8"), previo)


class TestSeleccion(Base):
    def test_oferta_solo_con_stock(self):
        productos = {
            "A1": dict(dato("A1", 100, 150, disponible=False), producto="Sin stock",
                       kit="k", kit_titulo="K", prioridad="esencial", fecha="2026-11-10"),
            "B2": dict(dato("B2", 50, 80, disponible=True, pct=37.5), producto="Con stock",
                       kit="k", kit_titulo="K", prioridad="extra", fecha="2026-11-10"),
        }
        salida = precios._volcar(productos, {}, 2, 0, 0,
                                 datetime(2026, 11, 10, tzinfo=timezone.utc),
                                 ["A1", "B2"], {}, persistir=False)
        self.assertIsNotNone(salida["oferta_dia"])
        self.assertEqual(salida["oferta_dia"]["asin"], "B2")
        self.assertNotIn("Sin stock", [x["producto"] for x in salida["ofertas"]])

    def test_criterio_declarado_no_promete_mayor_porcentaje(self):
        salida = precios._volcar({}, {}, 0, 0, 0,
                                 datetime(2026, 11, 10, tzinfo=timezone.utc),
                                 [], {}, persistir=False)
        criterio = salida["meta"]["criterio_oferta"].lower()
        self.assertIn("no es necesariamente el mayor", criterio)
        self.assertIn("stock", criterio)


class TestCompatibilidad(unittest.TestCase):
    def setUp(self):
        import sys
        sys.path.insert(0, str(RAIZ / "scripts"))
        import importlib
        self.b = importlib.import_module("buscar-amazon")

    def test_unidad_y_modelo_deben_coincidir(self):
        self.assertTrue(self.b.titulo_compatible(
            "Silbato de emergencia 120dB", "Silbato de emergencia para montaña 120 dB, naranja"))

    def test_rechaza_sin_unidad(self):
        self.assertFalse(self.b.titulo_compatible(
            "Silbato de emergencia 120dB", "Silbato de emergencia para montaña"))

    def test_rechaza_accesorio(self):
        self.assertFalse(self.b.titulo_compatible(
            "Silbato de emergencia 120dB", "Funda para silbato de emergencia 120 dB"))

    def test_candidato_exige_stock(self):
        resultados = [
            {"asin": "A", "titulo": "Silbato de emergencia 120 dB", "precio": 10,
             "disponible": False},
            {"asin": "B", "titulo": "Silbato de emergencia 120 dB", "precio": 11,
             "disponible": True},
        ]
        elegido = self.b.elegir_candidato("Silbato de emergencia 120dB", resultados, 5, 20)
        self.assertEqual(elegido["asin"], "B")


if __name__ == "__main__":
    unittest.main()
