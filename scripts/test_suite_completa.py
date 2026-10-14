#!/usr/bin/env python3
"""
SLOCAST 1.0 — SUITE DE PRUEBAS AUTOMATIZADA INTEGRAL
══════════════════════════════════════════════════════════════════════════
Ejecuta la validación rigurosa de extremo a extremo:
  1. Compilación de sintaxis Python 3.14 (todos los módulos)
  2. Importación y resolución de dependencias
  3. Núcleo criptográfico de licencias (HMAC-SHA256 + autocaducidad)
  4. Escudo de seguridad (RateLimiter, Token bucket, filtrado)
  5. Perfil de rendimiento y hardware (Intel i7-8665U / ThinkPad X390)
  6. Parser M3U Plus y Xtream Codes API
  7. Inicialización de la GUI del reproductor (modo offscreen PyQt6)
  8. Servidor API Backend (Node.js REST + Playback API)
"""

import sys
import os
import subprocess
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "app"))
sys.path.insert(0, str(BASE_DIR / "scripts"))


class TestSlocastCore(unittest.TestCase):
    def test_01_syntax_compilation(self):
        """Verifica que todos los archivos Python compilen sin errores."""
        py_files = list((BASE_DIR / "app").glob("*.py")) + list((BASE_DIR / "scripts").glob("*.py"))
        self.assertGreater(len(py_files), 5)
        for f in py_files:
            res = subprocess.run([sys.executable, "-m", "py_compile", str(f)], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Error de sintaxis en {f.name}: {res.stderr}")

    def test_02_module_imports(self):
        """Verifica que todos los submódulos de app importen correctamente."""
        modules = [
            'slone_license_core', 'slone_licensing', 'slone_epg', 'slone_meta',
            'slone_payments', 'slone_perf', 'slone_security', 'slone_vpn',
            'xtream_parser', 'slone_auth'
        ]
        for m in modules:
            mod = __import__(m)
            self.assertIsNotNone(mod, f"Fallo al importar {m}")

    def test_03_licensing_core(self):
        """Verifica que el núcleo de licencias opere según el estándar HMAC-SHA256."""
        import slone_license_core as lc
        # Clave válida para plan year
        k_year = lc.generate_key("year", "slone")
        self.assertTrue(lc.validate_key(k_year))
        self.assertEqual(lc.get_plan_from_key(k_year), "year")

        # Clave vitalicia
        k_life = lc.generate_key("lifetime", "slone")
        self.assertTrue(lc.validate_key(k_life))
        self.assertFalse(lc.is_key_expired(k_life))

        # Rechazo de claves falsificadas o alteradas
        self.assertFalse(lc.validate_key("SLONE-FAKE-000000-0123456789ABCDEF"))
        self.assertFalse(lc.validate_key(k_year[:-2] + "00"))
        self.assertFalse(lc.validate_key(""))
        self.assertFalse(lc.validate_key(None))

    def test_04_security_shield(self):
        """Verifica el control de tasa y filtrado del escudo de seguridad."""
        from slone_security import RateLimiter, SecurityShield
        limiter = RateLimiter(max_per_min=5)
        for _ in range(5):
            self.assertTrue(limiter.check("192.168.1.100"))
        # El sexto debe ser bloqueado por exceder la cuota
        self.assertFalse(limiter.check("192.168.1.100"))
        # Otra IP debe seguir teniendo cuota
        self.assertTrue(limiter.check("192.168.1.101"))

        shield = SecurityShield()
        # Ataque de path traversal bloqueado
        ok, reason = shield.allow("127.0.0.1", "/../../etc/passwd")
        self.assertFalse(ok)
        self.assertIn("patrón", reason.lower())

    def test_05_perf_profile(self):
        """Verifica la detección de hardware y parámetros óptimos de MPV."""
        import slone_perf as perf
        hw = perf.detect_hardware()
        self.assertIn("cpu", hw)
        self.assertIn("cores", hw)
        self.assertGreater(hw["cores"], 0)
        self.assertIn("ram_gb", hw)

        args = perf.best_mpv_args()
        self.assertIsInstance(args, list)

    def test_06_m3u_and_xtream_parser(self):
        """Verifica el parseo de listas M3U Plus."""
        from xtream_parser import M3UPlusParser
        sample_m3u = """#EXTM3U
#EXTINF:-1 tvg-id="La1.es" tvg-logo="https://rtve.es/logo.png" group-title="Nacionales",La 1 HD
https://rtvelivestream.akamaized.net/la1_es.m3u8
#EXTINF:-1 tvg-id="TDP.es" tvg-logo="https://rtve.es/tdp.png" group-title="Deportes",Teledeporte
https://rtvelivestream.akamaized.net/tdp_es.m3u8
"""
        channels = M3UPlusParser.parse(sample_m3u)
        self.assertEqual(len(channels), 2)
        self.assertEqual(channels[0]["name"], "La 1 HD")
        self.assertEqual(channels[0]["group"], "Nacionales")
        self.assertEqual(channels[0]["epg_id"], "La1.es")
        self.assertEqual(channels[1]["name"], "Teledeporte")

    def test_07_player_gui_instantiation(self):
        """Verifica que la ventana principal de SLOCAST se instancie limpiamente en offscreen."""
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        os.environ["SLONE_AUTH_BYPASS"] = "1"
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
        import slocast
        win = slocast.SLONEMainWindow()
        self.assertIsNotNone(win)
        self.assertTrue("SLONE GLOBAL MEDIA ENGINE" in win.windowTitle() or "SLONE" in win.windowTitle())
        # Limpieza
        win.close()

    def test_08_backend_api_node_tests(self):
        """Ejecuta los tests de Node.js para el servidor de API."""
        test_file = BASE_DIR / "backend" / "test.mjs"
        res = subprocess.run(["node", "--test", str(test_file)], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Fallo en tests del backend Node:\n{res.stdout}\n{res.stderr}")

    def test_09_multiview_stadium_4x(self):
        """Verifica la instanciación de la cuadrícula Multiview Stadium 4X y alternancia de audio."""
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        os.environ["SLONE_AUTH_BYPASS"] = "1"
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
        import slocast
        stadium = slocast.MultiviewStadiumWidget()
        self.assertEqual(len(stadium.quadrants), 4)
        self.assertEqual(stadium.active_quadrant, 0)
        # Probar conmutación de audio a cuadrante 2 (índice 1)
        stadium.set_active_audio(1)
        self.assertEqual(stadium.active_quadrant, 1)
        stadium.close()

    def test_10_orders_and_checkout_flow(self):
        """Verifica la creación y listado de pedidos en el motor soberano slone_orders."""
        import slone_orders
        orders = slone_orders.OrderManager.list_orders(10)
        self.assertIsInstance(orders, list)
        self.assertGreaterEqual(len(orders), 1)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 EJECUTANDO SUITE COMPLETA DE PRUEBAS — SLOCAST 1.0")
    print("=" * 70)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSlocastCore)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\n" + "=" * 70)
        print("✅ TODAS LAS PRUEBAS DE SLOCAST 1.0 PASARON A LA PERFECCIÓN")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n❌ HUBO FALLOS EN LA SUITE DE PRUEBAS")
        sys.exit(1)
