#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test-auditar-tags.py — el auditor tiene que FALLAR cuando hay que fallar.

Un verificador que nunca se pone rojo no verifica nada. Este test siembra
enlaces malos a propósito y exige que cada regla salte, además de comprobar que
el parseo HTML no inventa errores con apóstrofos, paréntesis ni parámetros
`&amp;` (los tres falsos positivos que ya aparecieron en producción).

    python3 scripts/test-auditar-tags.py
"""
import importlib.util
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("auditar_tags", RAIZ / "scripts" / "auditar-tags.py")
at = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(at)

REGISTRO = {
    "tags": {
        "aaa-21": {"mercado": "es", "roles": ["home"]},
        "bbb-21": {"mercado": "es", "roles": ["kits"]},
        "ccc-21": {"mercado": "intl",
                   "dominios": ["www.amazon.com", "www.amazon.co.uk", "www.amazon.de"],
                   "roles": ["home", "kits", "blog"]},
    },
    "mercadospendientes": ["it"],
}


def codigos(urls, zona="es-home"):
    return [h["codigo"] for h in at.analizar(REGISTRO, urls, "test", zona)]


class TestReglas(unittest.TestCase):
    def test_tag_correcto_no_da_nada(self):
        self.assertEqual(codigos(["https://www.amazon.es/s?k=agua&tag=aaa-21"]), [])

    def test_tag_de_otro_mercado_es_error(self):
        # E2: el fallo que dejó 2.646 enlaces a cero
        self.assertIn("E2", codigos(["https://www.amazon.de/s?k=wasser&tag=aaa-21"]))

    def test_tag_desconocido_es_error(self):
        self.assertIn("E1", codigos(["https://www.amazon.es/dp/B0X?tag=inventado-21"]))

    def test_sin_tag_en_mercado_con_tag_es_error(self):
        self.assertIn("E3", codigos(["https://www.amazon.es/s?k=agua"]))

    def test_sin_tag_en_mercado_pendiente_es_aviso(self):
        self.assertEqual(codigos(["https://www.amazon.it/s?k=kit"]), ["W1"])

    # --- tag internacional / OneLink (onamz…) ---
    def test_tag_intl_vale_en_tiendas_extranjeras(self):
        self.assertEqual(codigos(["https://www.amazon.de/s?k=wasser&tag=ccc-21"]), [])
        self.assertEqual(codigos(["https://www.amazon.co.uk/s?k=water&tag=ccc-21"]), [])

    def test_tag_intl_no_vale_en_amazon_es(self):
        # amazon.es tiene programa propio: el tag OneLink ahí no acredita
        self.assertIn("E2", codigos(["https://www.amazon.es/s?k=agua&tag=ccc-21"]))

    def test_tienda_extranjera_sin_tag_pese_a_haber_intl_es_error(self):
        self.assertIn("E3", codigos(["https://www.amazon.de/s?k=wasser"]))

    def test_tag_vacio_es_error(self):
        self.assertIn("E4", codigos(["https://www.amazon.es/s?k=agua&tag="]))

    def test_dos_tags_distintos_es_error(self):
        self.assertIn("E4", codigos(["https://www.amazon.es/dp/B0X?tag=aaa-21&tag=bbb-21"]))

    def test_imagen_y_ayuda_no_cuentan(self):
        self.assertEqual(codigos(["https://m.media-amazon.com/images/I/x.jpg",
                                  "https://www.amazon.es/gp/help/customer/display.html"]), [])

    def test_rol_de_seccion_mal_es_aviso(self):
        # aaa-21 es de portada; usarlo en una ficha de kit es sospechoso, no roto
        self.assertEqual(codigos(["https://www.amazon.es/dp/B0X?tag=aaa-21"], zona="es-kit"), ["W2"])


class TestParseo(unittest.TestCase):
    """El parseo no puede truncar la URL ni inventar enlaces."""

    def test_apostrofo_en_el_href_no_trunca(self):
        html = ('<a href="https://www.amazon.co.uk/s?k=Trek\'n%20Eat&amp;tag=bbb-21" '
                'target="_blank">ver</a>')
        enlaces = at.enlaces_de_html(html)
        self.assertEqual(len(enlaces), 1)
        self.assertIn("tag=bbb-21", enlaces[0])
        self.assertNotIn("&amp;", enlaces[0])          # entidad decodificada

    def test_parentesis_sin_codificar_se_respeta(self):
        html = '<a href="https://www.amazon.fr/s?k=kit%20d\'urgence%20(72%20h)&tag=aaa-21">x</a>'
        self.assertIn("tag=aaa-21", at.enlaces_de_html(html)[0])

    def test_tres_formas_de_tag(self):
        self.assertEqual(at.tags_de("https://www.amazon.es/dp/B0X?tag=aaa-21"), ["aaa-21"])
        self.assertEqual(at.tags_de("https://www.amazon.es/dp/B0X?x=1&amp;tag=aaa-21"), ["aaa-21"])
        self.assertEqual(at.tags_de("https://www.amazon.es/dp/B0X?x=1&tag=aaa-21"), ["aaa-21"])

    def test_mercado_del_host(self):
        self.assertEqual(at.mercado_del_host("www.amazon.es"), "es")
        self.assertEqual(at.mercado_del_host("www.amazon.co.uk"), "uk")
        self.assertEqual(at.mercado_del_host("www.amazon.com"), "us")
        self.assertEqual(at.mercado_del_host("www.amazon.com.be"), "be")


class TestRegistro(unittest.TestCase):
    """El registro y data/mercados.json no pueden contradecirse."""

    def test_registro_real_es_coherente(self):
        reg = at.cargar_registro()
        hallazgos = at.auditar_registro(reg)
        errores = [h for h in hallazgos if h["nivel"] == "ERROR"]
        self.assertEqual(errores, [], f"mercados.json contradice el registro: {errores}")

    def test_mercado_con_tag_ajeno_falla(self):
        reg = {"tags": {"aaa-21": {"mercado": "es", "roles": ["home"]}}, "mercadospendientes": []}
        mercados = {"mercados": [{"id": "de", "activo": True,
                                  "amazon": {"dominio": "www.amazon.de", "tag": "aaa-21"}}]}
        ruta = RAIZ / "data" / "mercados.json"
        original = ruta.read_text(encoding="utf-8")
        try:
            import json
            ruta.write_text(json.dumps(mercados), encoding="utf-8")
            errores = [h for h in at.auditar_registro(reg) if h["nivel"] == "ERROR"]
            self.assertTrue(errores, "un tag de .es en .de tiene que dar E6")
        finally:
            ruta.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main(verbosity=2)
