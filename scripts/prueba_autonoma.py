#!/usr/bin/env python3
"""
Prueba Autónoma y Generador de Capturas de SLOCAST 1.0 (SLONE OS / TiviMate)
Ejecuta la aplicación de forma desatendida, carga la lista real del usuario,
sintoniza el canal de fútbol con el búfer anti-cortes de 5s, despliega el
Drawer lateral de ajustes integrado en la misma ventana (sin ventanas externas)
y genera capturas de alta resolución para el usuario.
"""

import sys
import os
import time
from pathlib import Path

# Usar backend offscreen para captura limpia sin interferir con el escritorio del usuario
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer

# Añadir directorio de la app
APP_DIR = Path(__file__).resolve().parent.parent / "app"
sys.path.insert(0, str(APP_DIR))

import slocast

OUT_DIR = Path("/home/slone/.gemini/antigravity/brain/b7290ecc-a035-4dae-846a-78c02a4174b1/capturas")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SLOCAST_AUTOTEST")
    
    print("[AUTOTEST] Iniciando SLOCAST 1.0 (SLONE OS) de forma autónoma...")
    win = slocast.SLONEMainWindow()
    win.resize(1360, 850)
    win.show()

    # Cargar lista de serie
    playlist_path = str(slocast.DEFAULT_SERIE_M3U)
    print(f"[AUTOTEST] Cargando lista IPTV de serie: {playlist_path}")
    loader = slocast.M3ULoaderThread(playlist_path)

    def on_loaded(channels, countries_map, raw):
        print(f"[AUTOTEST] Lista indexada: {len(channels)} canales en {len(win.groups_order)} grupos.")
        win._on_channels_loaded(channels, countries_map, raw)
        
        # 1. Sintonizar el canal de fútbol estrella M+ LALIGA TV FHD
        target_ch = None
        for ch in win.all_channels:
            if "M+ LALIGA TV FHD" in ch.get("name", "") and "HEVC" not in ch.get("name", ""):
                target_ch = ch
                break
        if not target_ch:
            target_ch = win.all_channels[0]

        print(f"[AUTOTEST] Sintonizando canal: {target_ch.get('name')}")
        win._tune(target_ch)

        app.processEvents()
        time.sleep(0.5)
        app.processEvents()

        # Captura 1: Ventana principal con nuevo banner OSD estilo TiviMate
        pix_main = win.grab()
        path_main = OUT_DIR / "01_ventana_principal_tivimate.png"
        pix_main.save(str(path_main))
        print(f"[AUTOTEST] Captura 1 guardada: {path_main}")

        # Captura 2: Filtrado por grupo "ES - DEPORTES"
        win._select_group_by_name("ES - DEPORTES")
        app.processEvents()
        pix_deportes = win.grab()
        path_deportes = OUT_DIR / "02_grupo_es_deportes.png"
        pix_deportes.save(str(path_deportes))
        print(f"[AUTOTEST] Captura 2 guardada (Grupo ES - DEPORTES): {path_deportes}")

        # Captura 3: Drawer Lateral de Ajustes desplegado en la misma ventana (Sección Lista)
        win.toggle_settings_drawer(True)
        # Buscar el QTabWidget dentro del drawer
        drawer_tabs = win.settings_drawer.findChild(slocast.QTabWidget)
        if drawer_tabs:
            drawer_tabs.setCurrentIndex(0)
        app.processEvents()
        time.sleep(0.3)
        app.processEvents()

        pix_drawer_1 = win.grab()
        path_drawer_1 = OUT_DIR / "03_drawer_lateral_lista.png"
        pix_drawer_1.save(str(path_drawer_1))
        print(f"[AUTOTEST] Captura 3 guardada (Drawer Lateral - Lista): {path_drawer_1}")

        # Captura 4: Drawer Lateral - Sección Motor & Anti-Cortes
        if drawer_tabs:
            drawer_tabs.setCurrentIndex(1)
        app.processEvents()
        pix_drawer_2 = win.grab()
        path_drawer_2 = OUT_DIR / "04_drawer_motor_anticortes.png"
        pix_drawer_2.save(str(path_drawer_2))
        print(f"[AUTOTEST] Captura 4 guardada (Drawer Lateral - Motor & Anti-Cortes): {path_drawer_2}")

        # Captura 5: Drawer Lateral - Sección Audio & Comentarios de Radio
        if drawer_tabs:
            drawer_tabs.setCurrentIndex(2)
        app.processEvents()
        pix_drawer_3 = win.grab()
        path_drawer_3 = OUT_DIR / "05_drawer_multiaudio_catala_radios.png"
        pix_drawer_3.save(str(path_drawer_3))
        print(f"[AUTOTEST] Captura 5 guardada (Drawer Lateral - Multi-Audio & Radios): {path_drawer_3}")

        # Captura 6: Drawer Lateral - Sección Apariencia (Logo & Tipografía)
        if drawer_tabs:
            drawer_tabs.setCurrentIndex(3)
        app.processEvents()
        pix_drawer_4 = win.grab()
        path_drawer_4 = OUT_DIR / "06_drawer_apariencia_logo_tipografia.png"
        pix_drawer_4.save(str(path_drawer_4))
        print(f"[AUTOTEST] Captura 6 guardada (Drawer Lateral - Apariencia & Tipografía): {path_drawer_4}")

        win.mpv.stop()
        print("[AUTOTEST] Todas las pruebas y capturas de TiviMate se han generado con éxito.")
        app.quit()

    loader.channels_ready.connect(on_loaded)
    loader.start()
    app.exec()

if __name__ == "__main__":
    main()
