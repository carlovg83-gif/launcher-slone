#!/usr/bin/env python3
"""
SLONE OS v7.0 — Global Luxury Media & Broadcast Ecosystem
══════════════════════════════════════════════════════════════════════════
• Marca Global SLONE: Pure Black (#000000) + Amarillo Neón Flúor (#E3FF00).
• Selector Multi-Audio Real: Cambia en directo entre Español, Català, Radio o V.O.
• Cero-Cortes Anti-Freeze Watchdog: Búfer de resiliencia con paquetes de sincronización.
• Latencia Ultra-Baja: Retransmisión al mismo segundo que la señal satélite original.
• Ordenación Internacional Estandarizada: 🇪🇸 España, 🇬🇧 UK, 🇺🇸 USA, 🇫🇷 Francia, etc.
• Web Remote Móvil (http://IP:8765/remote): Mando a distancia táctil para el sofá.
• Control Directo Xiaomi TV (SLÖNE) con 1 clic en red local.
"""

import sys
import os
import time
import socket
import queue
import re
import threading
import json
import urllib.request
import urllib.parse
import tempfile
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QLineEdit, QListWidget,
    QSplitter, QMessageBox, QListWidgetItem, QButtonGroup, QSlider,
    QFileDialog, QFrame, QSizePolicy, QComboBox, QMenu,
    QDialog, QFormLayout, QDialogButtonBox, QCheckBox,
    QMenuBar, QTabWidget, QSpinBox, QDoubleSpinBox, QStatusBar,
    QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QThread, QTimer, QProcess, QProcessEnvironment, QSize
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QPixmap, QIcon, QAction, QColor, QCursor

try:
    import pychromecast
    HAS_CHROMECAST = True
except ImportError:
    HAS_CHROMECAST = False

# ──────────────────────────────────────────────────────────────
#  FASE 0 · INCRUSTACIÓN FIABLE DEL VÍDEO (KDE/Wayland a prueba de fallos)
#  ──────────────────────────────────────────────────────────────
#  Los motores mpv (--wid) y libvlc (set_xwindow) SOLO incrustan el vídeo
#  en ventanas X11. En Wayland nativo winId() devuelve un surface no-X11 y
#  el reproductor abre su PROPIA ventana externa (el clásico "doble player").
#  Forzamos aquí el backend XCB (XWayland) ANTES de crear QApplication, de
#  modo que el binario funcione igual lanzado desde el .desktop que a mano.
#  Respeta un QT_QPA_PLATFORM fijado explícitamente por el usuario.
def _xwayland_available() -> bool:
    """¿Hay un servidor X disponible (XWayland) al que engancharnos?"""
    if os.environ.get("DISPLAY"):
        return True
    for n in range(4):
        if os.path.exists(f"/tmp/.X11-unix/X{n}"):
            return True
    return False


if not os.environ.get("QT_QPA_PLATFORM"):
    _on_wayland = (
        os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
        or bool(os.environ.get("WAYLAND_DISPLAY"))
    )
    if _on_wayland and _xwayland_available():
        os.environ["QT_QPA_PLATFORM"] = "xcb"
        print("[SLONE ENGINE] Wayland detectado → backend XCB/XWayland para incrustar el vídeo.")
    elif _on_wayland and not _xwayland_available():
        print("[SLONE ENGINE] Wayland sin XWayland: el vídeo puede abrirse en ventana externa.")

# ──────────────────────────────────────────────────────────────
#  RUTAS PORTABLES — no dependen del nombre de usuario ni de $HOME
# ──────────────────────────────────────────────────────────────
APP_DIR = Path(__file__).resolve().parent          #  .../SLOCAST/app
PROJECT_DIR = APP_DIR.parent                        #  .../SLOCAST
WEB_PORTAL_DIR = APP_DIR / "web_portal"
CONFIG_DIR = PROJECT_DIR / "config"
STATE_CONFIG_PATH = CONFIG_DIR / "slo_webcast" / "config.json"   # last_m3u / engine
CONTROL_CONFIG_PATH = CONFIG_DIR / "slone_control.json"          # directiva maestra

# MPV IPC en el directorio temporal del sistema con aislamiento por PID
MPV_IPC_SOCKET = str(Path(tempfile.gettempdir()) / f"slone_mpv_{os.getpid()}.sock")

# Icono oficial: primer candidato existente (home del usuario actual o assets de la app)
ICON_CANDIDATES = [
    Path.home() / ".local" / "share" / "icons" / "slone.png",
    APP_DIR / "assets" / "slone.png",
    WEB_PORTAL_DIR / "assets" / "slone.png",
]


def find_icon() -> Path | None:
    """Devuelve la primera ruta de icono existente, o None."""
    for p in ICON_CANDIDATES:
        try:
            if p.exists():
                return p
        except Exception:
            continue
    return None


def load_json_config(path, default=None):
    """Lee un JSON sin lanzar excepciones (devuelve {} o el default)."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {} if default is None else default


def save_json_config(path, data) -> bool:
    """Escribe un JSON creando el directorio si hace falta. Nunca lanza."""
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception:
        return False


def get_app_setting(key: str, default=None):
    """Ajuste persistente de la app (config/slo_webcast/config.json)."""
    return load_json_config(STATE_CONFIG_PATH, {}).get(key, default)


def set_app_setting(key: str, value):
    """Guarda un ajuste persistente de la app."""
    data = load_json_config(STATE_CONFIG_PATH, {})
    data[key] = value
    return save_json_config(STATE_CONFIG_PATH, data)


def get_control_directive() -> dict:
    """Directiva maestra de SLONE OS (config/slone_control.json → directiva_maestra)."""
    return load_json_config(CONTROL_CONFIG_PATH, {}).get("directiva_maestra", {})


# Fuentes públicas libres de iptv-org (playlists M3U sin clave)
IPTV_ORG_SOURCES = {
    "🇪🇸 España": "https://iptv-org.github.io/iptv/countries/es.m3u",
    "⚽ Deportes": "https://iptv-org.github.io/iptv/categories/sports.m3u",
    "🎬 Cine": "https://iptv-org.github.io/iptv/categories/movies.m3u",
    "📰 Noticias": "https://iptv-org.github.io/iptv/categories/news.m3u",
    "🎵 Música": "https://iptv-org.github.io/iptv/categories/music.m3u",
    "🧒 Infantil": "https://iptv-org.github.io/iptv/categories/kids.m3u",
    "🌐 Global (todas)": "https://iptv-org.github.io/iptv/index.m3u",
}


DEFAULT_SERIE_M3U = Path.home() / "Descargas" / "TV-76173252_playlist.m3u"


def resolve_default_playlist() -> Path | None:
    """Primera lista M3U existente: config persistida → Descargas (de serie) → playlists/ del proyecto."""
    candidates = []
    last = get_app_setting("last_m3u")
    if last and not str(last).lower().startswith(("http://", "https://")):
        cand_p = Path(str(last)).expanduser()
        if cand_p.exists():
            candidates.append(cand_p)
    candidates.append(DEFAULT_SERIE_M3U)
    candidates.append(PROJECT_DIR / "playlists" / "tv.m3u")
    for p in candidates:
        try:
            if p.exists():
                return p
        except Exception:
            continue
    return None


# Motor de vídeo alternativo (VLC/libvlc). Detección opcional y silenciosa.
try:
    import vlc as _vlc_probe  # noqa: F401
    VLC_AVAILABLE = True
except Exception:
    VLC_AVAILABLE = False

# Motor EPG (guía de programación XMLTV)
try:
    from slone_epg import EpgManager, EPG_PRESETS
    EPG_AVAILABLE = True
except Exception:
    EPG_AVAILABLE = False
    EPG_PRESETS = {}

# Motor Xtream Codes
try:
    from xtream_parser import XtreamClient
    XTREAM_AVAILABLE = True
except Exception:
    XTREAM_AVAILABLE = False
    XtreamClient = None

# Motor de metadatos IA (DeepSeek)
try:
    from slone_meta import DeepSeekClient, DeepSeekError
    AI_AVAILABLE = True
except Exception:
    AI_AVAILABLE = False
    DeepSeekClient = None

    class DeepSeekError(Exception):
        pass

# Escudo de seguridad anti-intrusión (rate-limit, anti-hackers, bind seguro)
try:
    from slone_security import SHIELD
except Exception:
    SHIELD = None

# Perfil de máximo rendimiento integrado (hardware + MPV/VLC)
try:
    from slone_perf import (
        apply_performance_profile,
        best_mpv_args,
        best_vlc_options,
        detect_hardware,
        load_profile as load_perf_profile,
        profile_active,
        summary_text as perf_summary,
    )
    PERF_AVAILABLE = True
except Exception:
    PERF_AVAILABLE = False


# ──────────────────────────────────────────────────────────────
#  PALETAS Y TEMAS POR EQUIPO Y ESTILO (SLONE THEMES)
# ──────────────────────────────────────────────────────────────
SLONE_THEMES = {
    "obsidian": {
        "name": "👑 SLONE Signature (Negro & Neón)",
        "accent": "#E3FF00",
        "hover": "#F0FF4D",
        "bg": "#000000"
    },
    "blaugrana": {
        "name": "🔵🔴 FC Barcelona (Blaugrana & Oro)",
        "accent": "#EDBB00",
        "hover": "#FFD700",
        "bg": "#060A14"
    },
    "girona": {
        "name": "🔴⚪ Girona FC (Vermell-i-Blanc)",
        "accent": "#FF2A2A",
        "hover": "#FF5555",
        "bg": "#0E0707"
    },
    "madrid": {
        "name": "⚪🟡 Real Madrid / Clásico (Blanco & Oro)",
        "accent": "#D4AF37",
        "hover": "#E5C158",
        "bg": "#09090C"
    },
    "betis": {
        "name": "🟢⚪ Real Betis (Verdiblanco)",
        "accent": "#00D66C",
        "hover": "#26E885",
        "bg": "#060C08"
    },
    "racing": {
        "name": "🔴⚫ Ferrari / Racing (Rojo Competición)",
        "accent": "#FF2800",
        "hover": "#FF4500",
        "bg": "#080808"
    },
    "cyberpunk": {
        "name": "🟣🔵 Cyberpunk Neon (Cyan & Magenta)",
        "accent": "#00F0FF",
        "hover": "#33F3FF",
        "bg": "#0A0714"
    }
}

def get_slone_stylesheet(theme_key: str = "obsidian") -> str:
    """Genera la hoja de estilos dinámica sustituyendo los colores del tema seleccionado."""
    t = SLONE_THEMES.get(theme_key, SLONE_THEMES["obsidian"])
    acc = t["accent"]
    hov = t["hover"]
    return STYLE_SLONE.replace("#E3FF00", acc).replace("#F0FF4D", hov)

# ──────────────────────────────────────────────────────────────
#  ESTILO SLONE GLOBAL LUXURY (Negro #000000 + Neón VR46 #E3FF00)
# ──────────────────────────────────────────────────────────────
STYLE_SLONE = """
QMainWindow, QWidget {
    background-color: #000000;
    color: #FFFFFF;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 13px;
}

/* ── HEADER SUPERIOR SLONE ── */
#TopHeader {
    background-color: #000000;
    border-bottom: 2px solid #E3FF00;
    min-height: 52px;
    max-height: 52px;
    padding: 0 14px;
}
#MenuCornerTab {
    background-color: #E3FF00;
    color: #000000;
    font-weight: 900;
    font-size: 13px;
    padding: 7px 18px;
    border-radius: 8px;
    border: 1px solid #E3FF00;
    letter-spacing: 0.5px;
}
#MenuCornerTab:hover {
    background-color: #F0FF4D;
}
#CastCornerTab {
    background-color: #00E676;
    color: #000000;
    font-weight: 900;
    font-size: 13px;
    padding: 7px 18px;
    border-radius: 8px;
    border: 1px solid #00E676;
    letter-spacing: 0.5px;
}
#CastCornerTab:hover {
    background-color: #69F0AE;
}
#PlayerMiniBar {
    background-color: #000000;
    border-bottom: 1px solid #14171F;
    min-height: 28px;
    max-height: 28px;
    padding: 0 8px;
}
#PlayerSettingsTab {
    background-color: #0E1015;
    color: #E3FF00;
    font-weight: 900;
    font-size: 11px;
    border: 1px solid #E3FF00;
    border-radius: 6px;
    padding: 3px 12px;
}
#PlayerSettingsTab:hover {
    background-color: #E3FF00;
    color: #000000;
}
#BrandTitle {
    color: #E3FF00;
    font-size: 15px;
    font-weight: 900;
    letter-spacing: 1px;
}
#PlayerBottomBar {
    background-color: #000000;
    min-height: 30px;
    max-height: 30px;
}
#GoogleCastBtn {
    background-color: transparent;
    border: 1px solid #1E232E;
    border-radius: 6px;
    padding: 3px 8px;
    min-width: 34px;
    min-height: 24px;
}
#GoogleCastBtn:hover {
    background-color: #1A202C;
    border-color: #E3FF00;
}
#BrandAccent {
    color: #E3FF00;
}
#TopNavBtn {
    background-color: transparent;
    color: #A0A0A0;
    border: none;
    border-radius: 6px;
    padding: 7px 12px;
    font-size: 12px;
    font-weight: 800;
    margin: 0 1px;
}
#TopNavBtn:hover {
    background-color: #16181F;
    color: #FFFFFF;
}
#TopNavBtn:checked {
    background-color: #E3FF00;
    color: #000000;
    font-weight: 900;
}
#SearchBox {
    background-color: #080808;
    color: #FFFFFF;
    border: 1px solid #222222;
    border-radius: 16px;
    padding: 6px 14px;
    font-size: 12px;
    min-width: 170px;
    max-width: 250px;
}
#SearchBox:focus {
    border: 1px solid #E3FF00;
    background-color: #0D0D0D;
}
#CastHeaderBtn {
    background-color: #E3FF00;
    color: #000000;
    font-weight: 900;
    font-size: 11px;
    padding: 6px 14px;
    border-radius: 16px;
    border: none;
    letter-spacing: 0.5px;
}
#CastHeaderBtn:hover {
    background-color: #F0FF4D;
}

/* ── MENÚ LATERAL Y COMPONENTES LEGACY ── */
#SidebarWidget {
    background-color: #000000;
    border-right: 1px solid #141414;
    min-width: 0px;
    max-width: 0px;
}
#NavBtn {
    color: #E3FF00;
    background: transparent;
    text-align: left;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 800;
    border: none;
    border-radius: 6px;
}

/* ── PANEL DE CANALES Y FILTROS ── */
#ChannelPanel {
    background-color: #000000;
}
#CountryCombo {
    background-color: #0A0B0E;
    color: #E3FF00;
    border: 1px solid #252833;
    border-radius: 12px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 800;
}
#CountryCombo:focus {
    border-color: #E3FF00;
}
#CountryCombo QAbstractItemView {
    background-color: #0A0B0E;
    color: #FFFFFF;
    selection-background-color: #E3FF00;
    selection-color: #000000;
}
#CategoryChip {
    background-color: #0A0B0E;
    color: #888888;
    border: 1px solid #20222A;
    border-radius: 10px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 700;
}
#CategoryChip:hover {
    color: #E3FF00;
    border-color: #383D4A;
}
#CategoryChip:checked {
    background-color: #E3FF00;
    color: #000000;
    border-color: #E3FF00;
    font-weight: 900;
}

/* ── LISTA DE CANALES ── */
QListWidget {
    background-color: #050608;
    color: #E6E6E6;
    border: 1px solid #15171F;
    border-radius: 8px;
    outline: none;
    font-size: 13px;
}
QListWidget::item {
    padding: 7px 10px;
    border-bottom: 1px solid #0F1014;
    border-radius: 5px;
    margin: 1px 3px;
    color: #E2E8F0;
    font-weight: 600;
}
QListWidget::item:selected {
    background-color: #1A202C;
    color: #E3FF00;
    font-weight: 800;
    border-left: 3px solid #E3FF00;
}
QListWidget::item:hover {
    background-color: #0F1117;
    color: #FFFFFF;
}

#MainSplitter::handle {
    background-color: #12141A;
    width: 2px;
}
#MainSplitter::handle:hover {
    background-color: #E3FF00;
}

/* ── BARRA DE CONTROL INFERIOR (SLONE DOCK) ── */
#BottomDock {
    background-color: #000000;
    border-top: 1px solid #141414;
    min-height: 56px;
    max-height: 56px;
    padding: 0 16px;
}
#CtlBtn {
    background-color: #0D0D0D;
    color: #E3FF00;
    border: 1px solid #222222;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 800;
    min-width: 44px;
}
#CtlBtn:hover {
    background-color: #1A1A1A;
    border-color: #E3FF00;
}
#AudioDropdownBtn {
    background-color: #0D0D0D;
    color: #E3FF00;
    border: 1px solid #E3FF00;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 800;
}
#AudioDropdownBtn:hover {
    background-color: #E3FF00;
    color: #000000;
}
#BtnNeon {
    background-color: #E3FF00;
    color: #000000;
    font-weight: 900;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
}
#BtnNeon:hover {
    background-color: #F0FF4D;
}
#BtnDark {
    background-color: #0A0A0A;
    color: #E3FF00;
    font-weight: 800;
    border: 1px solid #222222;
    border-radius: 6px;
    padding: 8px 14px;
}
#BtnDark:hover {
    background-color: #141414;
    border-color: #E3FF00;
}

QSlider::groove:horizontal {
    height: 4px;
    background: #1C1C1C;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #E3FF00;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: #E3FF00;
    border-radius: 2px;
}

#CardItem {
    background-color: #070707;
    border: 1px solid #141414;
    border-radius: 8px;
    padding: 18px;
}

/* ── BARRA DE MENÚS SUPERIOR Y MENÚS DESPLEGABLES ── */
QMenuBar {
    background-color: #000000;
    color: #FFFFFF;
    border-bottom: 1px solid #1A1A1A;
    font-size: 13px;
    font-weight: 700;
    padding: 2px 6px;
}
QMenuBar::item {
    background: transparent;
    padding: 6px 12px;
    border-radius: 4px;
    margin-right: 2px;
}
QMenuBar::item:selected {
    background: #141414;
    color: #E3FF00;
}
QMenuBar::item:pressed {
    background: #222222;
    color: #E3FF00;
}
QMenu {
    background-color: #0A0A0A;
    color: #FFFFFF;
    border: 1px solid #282828;
    border-radius: 6px;
    padding: 6px 0;
    font-size: 13px;
}
QMenu::item {
    padding: 7px 28px 7px 20px;
}
QMenu::item:selected {
    background-color: #E3FF00;
    color: #000000;
    font-weight: 800;
}
QMenu::item:disabled {
    color: #555555;
}
QMenu::separator {
    height: 1px;
    background: #1F1F1F;
    margin: 5px 8px;
}

/* ── PESTAÑAS Y DIÁLOGOS DE PREFERENCIAS ── */
QDialog {
    background-color: #000000;
    color: #FFFFFF;
}
QTabWidget::pane {
    border: 1px solid #222222;
    background: #050505;
    border-radius: 6px;
    padding: 8px;
}
QTabBar::tab {
    background: #0D0D0D;
    color: #888888;
    padding: 8px 18px;
    border: 1px solid #1F1F1F;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 4px;
    font-weight: 700;
}
QTabBar::tab:selected {
    background: #050505;
    color: #E3FF00;
    border-top: 2px solid #E3FF00;
}
QTabBar::tab:hover:!selected {
    color: #FFFFFF;
    background: #141414;
}
QSpinBox, QDoubleSpinBox {
    background-color: #0A0A0A;
    color: #FFFFFF;
    border: 1px solid #282828;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 13px;
}
QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #E3FF00;
}
QStatusBar {
    background-color: #000000;
    color: #888888;
    border-top: 1px solid #141414;
    font-size: 12px;
}

/* ── DRAWER LATERAL DE AJUSTES SLONE PRO (INTEGRADO EN LA VENTANA) ── */
#SettingsDrawer {
    background-color: #0B0C10;
    border-left: 2px solid #E3FF00;
    min-width: 390px;
    max-width: 420px;
}
#DrawerHeader {
    background-color: #070709;
    border-bottom: 1px solid #1C1E24;
    padding: 10px 14px;
}
#DrawerTitle {
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 900;
    letter-spacing: 0.5px;
}
#DrawerCloseBtn {
    background: transparent;
    color: #888888;
    font-size: 15px;
    font-weight: 900;
    border: none;
    padding: 2px 6px;
    border-radius: 4px;
}
#DrawerCloseBtn:hover {
    color: #E3FF00;
    background: #14161D;
}
#DrawerSectionTitle {
    color: #E3FF00;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 8px;
    margin-bottom: 4px;
}
#DrawerCard {
    background-color: #101217;
    border: 1px solid #1D212A;
    border-radius: 6px;
    padding: 10px;
}

/* ── DRAWER PRINCIPAL SLONE (ESQUINA IZQUIERDA) ── */
#SloneDrawer, #TiviMateDrawer {
    background-color: #07080B;
    border-right: 2px solid #E3FF00;
    min-width: 320px;
    max-width: 320px;
}
#DrawerSectionHeader {
    color: #E3FF00;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 1px;
    padding: 10px 6px 4px 6px;
    border-bottom: 1px solid #1A1D26;
    text-transform: uppercase;
}
#DrawerNavBtn {
    background-color: #0D0F14;
    color: #E2E8F0;
    font-size: 13px;
    font-weight: 700;
    text-align: left;
    padding: 10px 14px;
    border: 1px solid #1A1D26;
    border-radius: 8px;
}
#DrawerNavBtn:hover {
    background-color: #1A202C;
    color: #E3FF00;
    border-color: #E3FF00;
}
#DrawerFooter {
    color: #64748B;
    font-size: 11px;
    font-weight: 700;
    padding: 8px 0;
    border-top: 1px solid #14171F;
}

/* ── BANNER OSD SLONE (SUPERIOR DEL REPRODUCTOR) ── */
#SloneBanner, #TiviMateBanner {
    background-color: #07080A;
    border-bottom: 1px solid #1C1E26;
    border-radius: 4px;
    min-height: 32px;
    max-height: 34px;
    padding: 2px 8px;
}
#OsdBadgeLive {
    background-color: #E50914;
    color: #FFFFFF;
    font-size: 10px;
    font-weight: 900;
    border-radius: 3px;
    padding: 2px 6px;
    letter-spacing: 0.5px;
}
#OsdBadgeFhd {
    background-color: #142814;
    color: #9FE870;
    border: 1px solid #2B552B;
    font-size: 10px;
    font-weight: 800;
    border-radius: 3px;
    padding: 2px 6px;
}
#OsdBadgeAudio {
    background-color: #162030;
    color: #64B5F6;
    border: 1px solid #283955;
    font-size: 10px;
    font-weight: 800;
    border-radius: 3px;
    padding: 2px 6px;
}
#OsdBadgeBuffer {
    background-color: #26220E;
    color: #E3FF00;
    border: 1px solid #574F1A;
    font-size: 10px;
    font-weight: 800;
    border-radius: 3px;
    padding: 2px 6px;
}
"""

def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

UA_IPTV = "IPTVSmartersPro"
# MPV_IPC_SOCKET se define en el bloque "RUTAS PORTABLES" (tempfile del sistema).

# Paquete de relleno MPEG-TS (NULL packet 188 bytes con PID 0x1FFF)
NULL_TS_PACKET = b"\x47\x1f\xff\x10" + (b"\xff" * 184)
NULL_TS_BURST = NULL_TS_PACKET * 32  # Relleno de seguridad durante microcortes

# ──────────────────────────────────────────────────────────────
#  BROADCAST HUB — ANTI-FREEZE & WATCHDOG RESILIENTE
# ──────────────────────────────────────────────────────────────
class BroadcastHub:
    def __init__(self):
        self.lock = threading.Lock()
        self.current_url: str | None = None
        self.channel_name: str = "Sin canal"
        self.clients: set[queue.Queue] = set()
        self.worker_thread: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.raw_playlist: str = ""
        self.app_window = None

    def register_client(self) -> queue.Queue:
        q = queue.Queue(maxsize=160)
        with self.lock:
            self.clients.add(q)
            if self.current_url and not (self.worker_thread and self.worker_thread.is_alive()):
                self.stop_event.clear()
                self.worker_thread = threading.Thread(target=self._upstream_resilient_worker, args=(self.current_url,), daemon=True)
                self.worker_thread.start()
        return q

    def unregister_client(self, q: queue.Queue):
        with self.lock:
            self.clients.discard(q)
            if not self.clients:
                self.stop_event.set()

    def set_channel(self, url: str, name: str = ""):
        with self.lock:
            self.current_url = url
            self.channel_name = name or "Canal IPTV"
            self.stop_event.set()

        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=0.4)

        with self.lock:
            # Conectar upstream únicamente si hay clientes escuchando activamente en LAN/Relay
            if self.clients and self.current_url:
                self.stop_event.clear()
                self.worker_thread = threading.Thread(target=self._upstream_resilient_worker, args=(url,), daemon=True)
                self.worker_thread.start()

    def _upstream_resilient_worker(self, url: str):
        """Lector continuo con watchdog anti-cortes: jamás corta los sockets locales."""
        headers = {"User-Agent": UA_IPTV, "Accept": "*/*", "Connection": "keep-alive"}
        while not self.stop_event.is_set():
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=8) as resp:
                    while not self.stop_event.is_set():
                        chunk = resp.read(32768)
                        if not chunk:
                            break  # Microcorte del proveedor -> reconectar de inmediato sin desconectar clientes
                        self._broadcast(chunk)
            except Exception:
                # Durante la reconexión, inyectar paquetes NULL TS para mantener vivo el decodificador de Xiaomi TV y PC
                if not self.stop_event.is_set():
                    self._broadcast(NULL_TS_BURST)
                    time.sleep(0.15)  # Reintento instantáneo en 150 ms

    def _broadcast(self, chunk: bytes):
        with self.lock:
            dead = []
            for q in list(self.clients):
                try:
                    if q.full():
                        try: q.get_nowait()
                        except Exception: pass
                    q.put_nowait(chunk)
                except Exception:
                    dead.append(q)
            for d in dead:
                self.clients.discard(d)

HUB = BroadcastHub()

# ──────────────────────────────────────────────────────────────
#  SERVIDOR RELAY HTTP + WEB REMOTE MÓVIL (Puerto 8765)
# ──────────────────────────────────────────────────────────────
class RelayHTTPHandler(BaseHTTPRequestHandler):
    def _security_guard(self) -> bool:
        """Aplica el escudo SLONE. Devuelve True si la petición puede continuar."""
        if SHIELD is None:
            return True
        ip = self.client_address[0]
        ua = self.headers.get("User-Agent", "")
        query = urllib.parse.urlparse(self.path).query
        token = urllib.parse.parse_qs(query).get("token", [None])[0]
        # Rutas de medios y listas LAN (SLONE TV Connect, Cast, AirRelay, VLC) no exigen token:
        # el control remoto (/remote, /api/cmd) sí lo exige si la directiva lo requiere.
        sensitive = not (
            self.path.startswith("/stream")
            or self.path.startswith("/assets/")
            or self.path.startswith("/playlist")
            or self.path.startswith("/slone_tv")
            or self.path.startswith("/airrelay")
            or self.path.startswith("/tivimate")
            or self.path.startswith("/get.php")
            or self.path.startswith("/epg")
            or self.path.startswith("/xmltv")
            or self.path.startswith("/api/checkout")
            or self.path.startswith("/api/orders")
        )
        ok, reason = SHIELD.allow(ip, self.path, method="GET", user_agent=ua,
                                  token=token, sensitive=sensitive)
        if not ok:
            try:
                self.send_response(403)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"403 — Bloqueado por SLONE Shield: {reason}".encode("utf-8"))
            except Exception:
                pass
            return False
        return True

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_POST(self):
        if not self._security_guard():
            return
        p = self.path
        if p.startswith("/api/v1/control") or p.startswith("/api/cmd"):
            length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(length) if length > 0 else b"{}"
            self._handle_api_control_post(body_bytes)
        elif p == "/api/checkout":
            length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(length) if length > 0 else b"{}"
            self._handle_checkout_post(body_bytes)
        else:
            self.send_error(404)

    def do_GET(self):
        if not self._security_guard():
            return
        p = self.path
        if p == "/stream":
            self._serve_stream()
        elif p.startswith("/playlist") or p.startswith("/slone_tv") or p.startswith("/airrelay") or p.startswith("/tivimate") or p.startswith("/get.php"):
            self._serve_playlist()
        elif p == "/" or p == "/portal" or p == "/index.html":
            self._serve_portal()
        elif p == "/manifest.json":
            self._serve_manifest()
        elif p.startswith("/assets/"):
            self._serve_asset(p)
        elif p in ("/sw.js", "/privacy.html", "/terms.html"):
            self._serve_portal_file(p.lstrip("/"))
        elif p.startswith("/remote"):
            self._serve_web_remote()
        elif p.startswith("/api/v1/status") or p == "/api/status":
            self._serve_status()
        elif p.startswith("/api/v1/channels"):
            self._serve_channels_api()
        elif p == "/api/orders":
            self._serve_orders_api()
        elif p.startswith("/api/cmd") or p.startswith("/api/v1/control"):
            self._handle_remote_cmd(p)
        else:
            self.send_error(404)

    def _serve_manifest(self):
        mf_path = WEB_PORTAL_DIR / "manifest.json"
        if mf_path.exists():
            content = mf_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/manifest+json")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404)

    def _serve_portal(self):
        portal_path = WEB_PORTAL_DIR / "index.html"
        if portal_path.exists():
            content = portal_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self._serve_web_remote()

    def _serve_portal_file(self, name):
        """Sirve archivos estáticos concretos del portal (sw.js, privacy.html, terms.html)."""
        try:
            path = (WEB_PORTAL_DIR / name).resolve()
            if WEB_PORTAL_DIR.resolve() not in path.parents:
                self.send_error(404)
                return
        except Exception:
            self.send_error(404)
            return
        ctype = {
            ".html": "text/html; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/manifest+json",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".svg": "image/svg+xml",
        }.get(path.suffix.lower(), "application/octet-stream")
        if path.exists():
            content = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404)

    def _serve_asset(self, path):
        rel = path.replace("/assets/", "", 1).split("?")[0]
        assets_root = (WEB_PORTAL_DIR / "assets").resolve()
        asset_file = (assets_root / rel).resolve()
        # Seguridad: impedir path traversal fuera del directorio /assets
        if assets_root not in asset_file.parents and asset_file != assets_root:
            self.send_error(403)
            return
        if asset_file.is_file():
            mime = "application/octet-stream"
            if asset_file.suffix in (".jpg", ".jpeg"): mime = "image/jpeg"
            elif asset_file.suffix == ".png": mime = "image/png"
            elif asset_file.suffix == ".svg": mime = "image/svg+xml"
            elif asset_file.suffix == ".css": mime = "text/css"
            elif asset_file.suffix == ".js": mime = "application/javascript"
            content = asset_file.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "max-age=86400")
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404)

    def _serve_web_remote(self):
        ip = get_local_ip()
        ch = HUB.channel_name
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>SLONE Remote</title>
  <style>
    * {{ box-sizing: border-box; touch-action: manipulation; }}
    body {{ background: #000; color: #FFF; font-family: -apple-system, sans-serif; text-align: center; margin: 0; padding: 20px; }}
    h1 {{ color: #E3FF00; font-size: 28px; font-weight: 900; margin: 10px 0 2px 0; letter-spacing: 1.5px; }}
    .sub {{ color: #888; font-size: 13px; margin-bottom: 18px; }}
    .card {{ background: #090909; border: 1px solid #1F1F1F; border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
    .channel {{ color: #E3FF00; font-size: 17px; font-weight: 800; word-break: break-word; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 16px 0; }}
    .btn {{ background: #111; color: #E3FF00; border: 2px solid #222; border-radius: 12px; padding: 18px 8px; font-size: 15px; font-weight: 800; cursor: pointer; }}
    .btn:active {{ background: #E3FF00; color: #000; }}
    .btn-main {{ background: #E3FF00; color: #000; grid-column: span 2; font-size: 18px; border: none; }}
    .btn-audio {{ background: #1C1C1C; color: #E3FF00; border: 2px solid #E3FF00; grid-column: span 2; }}
    .btn-cast {{ background: #00E676; color: #000; grid-column: span 2; font-size: 16px; border: none; }}
  </style>
</head>
<body>
  <h1>👑 SLONE<span style="color:#FFF">.OS</span></h1>
  <div class="sub">Mando a Distancia Móvil VR46</div>
  <div class="card">
    <div style="color:#666; font-size: 11px; text-transform:uppercase;">Canal en Directo</div>
    <div class="channel" id="cur_ch">{ch}</div>
  </div>
  <div class="grid">
    <button class="btn btn-main" onclick="send('toggle')">⏯ Play / Pausa</button>
    <button class="btn btn-audio" onclick="send('cycle_audio')">🎙 Cambiar Audio (Català / Radio / TV)</button>
    <button class="btn" onclick="send('prev')">⏮ Canal Anterior</button>
    <button class="btn" onclick="send('next')">⏭ Siguiente Canal</button>
    <button class="btn" onclick="send('vol_up')">🔊 Volumen +</button>
    <button class="btn" onclick="send('vol_down')">🔉 Volumen -</button>
    <button class="btn" onclick="send('mute')">🔇 Silencio</button>
    <button class="btn" onclick="send('fullscreen')">⛶ Pantalla Completa</button>
    <button class="btn btn-cast" onclick="send('cast_tv')">📺 Proyectar en Xiaomi TV</button>
  </div>
  <div style="color:#555; font-size:12px; margin-top:20px;">ThinkPad X390 ({ip}:8765)</div>
  <script>
    function send(act) {{
      fetch('/api/cmd?action=' + act)
        .then(r => r.json())
        .then(d => {{ if(d.channel) document.getElementById('cur_ch').innerText = d.channel; }});
    }}
  </script>
</body>
</html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def _serve_status(self):
        win = HUB.app_window
        st = {
            "status": "ok",
            "service": "slocast-player-engine",
            "channel": HUB.channel_name,
            "is_playing": win.mpv.is_playing() if win else False,
            "volume": win.slider_vol.value() if win else 85,
            "muted": win._muted if win else False,
            "engine": win.mpv._engine_name() if win else "mpv",
            "total_channels": len(win.all_channels) if (win and hasattr(win, "all_channels")) else 0,
            "stream_url": HUB.current_url or ""
        }
        data = json.dumps(st, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_channels_api(self):
        win = HUB.app_window
        chs = []
        if win and hasattr(win, "all_channels"):
            for i, c in enumerate(win.all_channels[:500]):
                chs.append({
                    "id": i,
                    "name": c.get("name", ""),
                    "group": c.get("group", "General"),
                    "logo": c.get("logo", ""),
                    "url": c.get("url", "")
                })
        data = json.dumps({"status": "ok", "count": len(chs), "channels": chs}, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _dispatch_action(self, action: str, val=None):
        win = HUB.app_window
        if win:
            if action in ("toggle", "play_pause"): win._toggle_playback()
            elif action == "play":
                if not win.mpv.is_playing() and getattr(win, "current_channel", None):
                    win._tune(win.current_channel)
            elif action == "pause":
                if win.mpv.is_playing(): win.mpv.toggle_pause()
            elif action == "next": win._next_channel()
            elif action == "prev": win._prev_channel()
            elif action == "cycle_audio": win.mpv.cycle_audio()
            elif action == "set_volume" and val is not None:
                win.slider_vol.setValue(max(0, min(100, int(val))))
            elif action == "vol_up": win.slider_vol.setValue(min(100, win.slider_vol.value() + 8))
            elif action == "vol_down": win.slider_vol.setValue(max(0, win.slider_vol.value() - 8))
            elif action == "mute": win._toggle_mute()
            elif action == "fullscreen": win._toggle_fullscreen()
            elif action == "cast_tv": win._cast_to_xiaomi_tv()
            elif action == "select_channel" and val is not None:
                if hasattr(win, "all_channels"):
                    if isinstance(val, int) and 0 <= val < len(win.all_channels):
                        win._tune(win.all_channels[val])
                    elif isinstance(val, str):
                        for ch in win.all_channels:
                            if ch.get("name", "").lower() == val.lower():
                                win._tune(ch)
                                break

    def _handle_api_control_post(self, body_bytes: bytes):
        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            body = {}
        action = body.get("action") or body.get("cmd") or "toggle"
        val = body.get("value")
        self._dispatch_action(action, val)

        win = HUB.app_window
        resp = {
            "status": "ok",
            "action": action,
            "channel": HUB.channel_name,
            "volume": win.slider_vol.value() if win else 85,
            "muted": win._muted if win else False,
            "is_playing": win.mpv.is_playing() if win else False
        }
        data = json.dumps(resp, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _handle_checkout_post(self, body_bytes: bytes):
        try:
            data = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            data = {}
        plan_id = data.get("plan_id", "quad_year")
        email = data.get("email", "socio@slone.tv")

        # Cero emisión gratuita en cliente: derivar a pasarela bancaria segura oficial
        try:
            from slone_payments import PaymentGateway
            gw = PaymentGateway()
            checkout_url = gw.get_checkout_url(plan_id, email)
            resp = {
                "status": "redirect",
                "checkout_url": checkout_url,
                "message": "Redirigiendo a pasarela bancaria segura..."
            }
        except Exception as e:
            resp = {"status": "error", "message": f"Pasarela de cobro no disponible: {e}"}

        out = json.dumps(resp, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def _serve_orders_api(self):
        # Blindaje anti-exfiltración web: denegar acceso a cualquier origen web externo (CORS cerrado)
        origin = self.headers.get("Origin", "")
        client_ip = self.client_address[0] if self.client_address else ""
        if client_ip not in ("127.0.0.1", "::1", "localhost") or (origin and "localhost" not in origin and "127.0.0.1" not in origin):
            self.send_response(403)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(b'{"status": "error", "message": "Acceso restringido por SLONE Security Shield (RGPD)"}')
            return

        try:
            from slone_orders import OrderManager
            orders = OrderManager.list_orders(50)
            out = json.dumps({"status": "success", "orders": orders}, indent=2, ensure_ascii=False).encode("utf-8")
        except Exception as e:
            out = json.dumps({"status": "error", "message": str(e)}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def _handle_remote_cmd(self, path: str):
        params = urllib.parse.parse_qs(path.split("?", 1)[1]) if "?" in path else {}
        action = params.get("action", params.get("cmd", [""]))[0]
        val = params.get("value", [None])[0]
        self._dispatch_action(action, val)

        win = HUB.app_window
        resp = {
            "status": "ok",
            "action": action,
            "channel": HUB.channel_name,
            "volume": win.slider_vol.value() if win else 85,
            "muted": win._muted if win else False,
            "is_playing": win.mpv.is_playing() if win else False
        }
        data = json.dumps(resp, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_playlist(self):
        content = HUB.raw_playlist
        if not content:
            last_m3u = get_app_setting("last_m3u", str(DEFAULT_SERIE_M3U))
            if last_m3u and Path(last_m3u).exists():
                try:
                    content = Path(last_m3u).read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    pass
        if not content:
            self.send_error(404, "Lista M3U no disponible en el servidor")
            return
        data = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/vnd.apple.mpegurl; charset=utf-8")
        self.send_header("Content-Disposition", 'attachment; filename="slocast_playlist.m3u"')
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def _serve_stream(self):
        if not HUB.current_url:
            self.send_error(503, "Sin canal seleccionado")
            return
        cq = HUB.register_client()
        try:
            self.send_response(200)
            self.send_header("Content-Type", "video/mp2t")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            while True:
                try:
                    chunk = cq.get(timeout=2.0)
                    self.wfile.write(chunk)
                except queue.Empty:
                    # Mantener el cliente conectado mientras haya emisor activo
                    if not (HUB.worker_thread and HUB.worker_thread.is_alive()):
                        break
                    continue
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            HUB.unregister_client(cq)

    def log_message(self, *args): pass


class RelayServer:
    PORT = 8765
    def __init__(self):
        self._srv: ThreadingHTTPServer | None = None
        self.is_running = False

    @property
    def bind_host(self) -> str:
        """127.0.0.1 (seguro por defecto) o 0.0.0.0 si el escudo permite LAN."""
        if SHIELD is not None:
            return SHIELD.bind_host
        return "0.0.0.0"

    def start(self) -> bool:
        if self.is_running: return True
        try:
            self._srv = ThreadingHTTPServer((self.bind_host, self.PORT), RelayHTTPHandler)
            threading.Thread(target=self._srv.serve_forever, daemon=True).start()
            self.is_running = True
            return True
        except OSError:
            return False

    def stop(self):
        if self._srv:
            self._srv.shutdown()
            self.is_running = False

    @property
    def stream_url(self) -> str:
        return f"http://{get_local_ip()}:{self.PORT}/stream"

    @property
    def loopback_url(self) -> str:
        return f"http://127.0.0.1:{self.PORT}/stream"

    @property
    def remote_url(self) -> str:
        host = "127.0.0.1" if self.bind_host in ("127.0.0.1", "localhost") else get_local_ip()
        tok = ""
        if SHIELD is not None:
            try:
                tok = f"?token={SHIELD.token()}"
            except Exception:
                tok = ""
        return f"http://{host}:{self.PORT}/remote{tok}"

# ──────────────────────────────────────────────────────────────
#  CONTROLADOR XIAOMI TV (SLÖNE)
# ──────────────────────────────────────────────────────────────
class XiaomiCastController(QThread):
    cast_status = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()
        self.cast_device = None
        self.is_connected = False
        self._target_url = ""
        self._target_title = ""
        self._action = "idle"

    def connect_and_play(self, url: str, title: str):
        self._target_url = url
        self._target_title = title
        self._action = "play"
        if not self.isRunning():
            self.start()

    def stop_cast(self):
        self._action = "stop"
        if not self.isRunning():
            self.start()

    def run(self):
        if not HAS_CHROMECAST:
            self.cast_status.emit("pychromecast no disponible", False)
            return
        try:
            if self._action == "play":
                cast_name = str(get_app_setting("cast_name", "SLÖNE") or "SLÖNE")
                self.cast_status.emit(f"Conectando con {cast_name}…", False)
                casts, browser = pychromecast.get_listed_chromecasts(friendly_names=[cast_name])
                if not casts:
                    chromecasts, browser = pychromecast.get_chromecasts()
                    casts = [c for c in chromecasts if "xiaomi" in c.model_name.lower() or "mitv" in c.model_name.lower()]

                if not casts:
                    self.cast_status.emit("Xiaomi TV no detectada", False)
                    pychromecast.discovery.stop_discovery(browser)
                    return

                cast = casts[0]
                cast.wait()
                mc = cast.media_controller
                mc.play_media(self._target_url, "video/mp2t", title=f"SLONE: {self._target_title}")
                mc.block_until_active(timeout=5)
                self.cast_device = cast
                self.is_connected = True
                self.cast_status.emit(f"Transmitiendo en Xiaomi TV: {self._target_title}", True)
                pychromecast.discovery.stop_discovery(browser)
            elif self._action == "stop":
                if self.cast_device:
                    try: self.cast_device.media_controller.stop()
                    except Exception: pass
                self.is_connected = False
                self.cast_status.emit("Transmisión en TV detenida", False)
        except Exception as e:
            self.cast_status.emit(f"Error Cast: {str(e)[:30]}", False)

# ──────────────────────────────────────────────────────────────
#  MOTOR SLONE ULTRA ENGINE (INC. XCB + MULTI-AUDIO + CERO CORTES)
# ──────────────────────────────────────────────────────────────
# Emisoras y comentarios en directo de España para Multi-Audio deportivo
SLONE_MULTI_AUDIO_RADIOS = [
    {"id": "radio_rac1", "title": "🔴 Català · RAC1 (Directe Esports)", "url": "https://playerservices.streamtheworld.com/api/livestream-redirect/RAC_1.mp3"},
    {"id": "radio_catradio", "title": "🔴 Català · Catalunya Ràdio", "url": "https://shoutcast.ccma.cat/ccma/catalunyaradio.mp3"},
    {"id": "radio_ser", "title": "🔴 Cadena SER · Carrusel Deportivo", "url": "https://23543.live.streamtheworld.com/CADENASER.mp3"},
    {"id": "radio_cope", "title": "🔴 COPE · Tiempo de Juego", "url": "https://flucast09-h-cloud.flumotion.com/cope/net1.mp3"},
    {"id": "radio_marca", "title": "🔴 Radio Marca · El Marcador", "url": "https://playerservices.streamtheworld.com/api/livestream-redirect/RADIOMARCA_NACIONAL.mp3"},
    {"id": "radio_ondacero", "title": "🔴 Onda Cero · Radioestadio", "url": "https://icecast-streaming.nice264.com/ondacero"},
    {"id": "radio_los40", "title": "🎵 Los 40 Principales (Música Directa)", "url": "https://21253.live.streamtheworld.com/LOS40.mp3"},
    {"id": "radio_rockfm", "title": "🎸 Rock FM (Música Directa)", "url": "https://flucast06-b-cloud.flumotion.com/cope/rockfm.mp3"},
    {"id": "radio_ibiza", "title": "🌴 Ibiza Global Radio (Chill & House)", "url": "https://listenssl.ibizaglobalradio.com:8024/ibizaglobalradio.mp3"},
    {"id": "radio_flaix", "title": "⚡ Flaix FM (Dance & Hits)", "url": "https://flaixfm.streaming-pro-v2.com:8000/flaixfm.mp3"},
]

class MPVWidget(QWidget):
    double_clicked = pyqtSignal()
    audio_tracks_updated = pyqtSignal(list)

    def __init__(self, parent=None, ipc_socket: str = "", is_stadium: bool = False):
        super().__init__(parent)
        self.setObjectName("VideoViewport")
        self.setMinimumSize(320, 200)
        self.ipc_socket = ipc_socket or MPV_IPC_SOCKET
        self.is_stadium = is_stadium
        self._proc: QProcess | None = None
        self._vol = 100
        self._muted = False
        self.current_tracks: list = []
        self._active_radio: str | None = None
        self._current_stream_url: str = ""
        self._buffer_secs: int = int(get_app_setting("buffer_secs", 5) or 5)
        # Motor VLC/libvlc (opcional)
        self._vlc_instance = None
        self._vlc_player = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.placeholder = QLabel("👑  SLONE ULTRA ENGINE — DIRECTO DE ALTA FIDELIDAD\n\nSelecciona un canal para reproducir en directo\n[Espacio: Pausa | A: Cambiar Idioma / Radio | F: Pantalla Completa]", self)
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("color: #E3FF00; font-size: 14px; font-weight: 800; background: #000000;")
        lay.addWidget(self.placeholder)

        # Polling periódico de pistas de audio tras abrir canal
        self.track_poll_timer = QTimer(self)
        self.track_poll_timer.setInterval(1200)
        self.track_poll_timer.timeout.connect(self._query_audio_tracks)

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)

    def _engine_name(self) -> str:
        """Motor activo: 'mpv' o 'vlc' (con fallback a mpv si VLC no está disponible)."""
        eng = str(get_app_setting("engine", "mpv") or "mpv").lower()
        if eng == "vlc" and not VLC_AVAILABLE:
            return "mpv"
        return eng

    def _ensure_native_window(self):
        """Materializa una superficie X11 real para incrustar el vídeo DENTRO
        del widget (evita la ventana externa del reproductor en Wayland)."""
        try:
            self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
            self.setAttribute(Qt.WidgetAttribute.WA_DontCreateNativeAncestors, True)
            self.winId()  # fuerza la creación de la ventana nativa
        except Exception as e:
            print(f"[SLONE ENGINE] Aviso preparando superficie nativa: {e}")

    def play(self, stream_url: str):
        self.stop()
        self.placeholder.hide()
        self._current_stream_url = stream_url
        self._active_radio = None
        if self._engine_name() == "vlc":
            self._play_vlc(stream_url)
        else:
            self._play_mpv(stream_url)

    def _play_mpv(self, stream_url: str):
        if os.path.exists(self.ipc_socket):
            try: os.remove(self.ipc_socket)
            except Exception: pass

        self._ensure_native_window()
        wid = str(int(self.winId()))
        args = [
            f"--wid={wid}",
            "--vo=gpu",
            "--gpu-context=x11",
            "--title=SLONE ULTRA PLAYER",
            "--force-window=no",
            "--no-terminal",
            "--no-input-default-bindings",
            "--input-vo-keyboard=no",
            "--input-cursor=no",
            "--no-osc",
            f"--input-ipc-server={self.ipc_socket}",
            "--cache=yes",
            f"--cache-secs={self._buffer_secs if not self.is_stadium else 2}",
            f"--demuxer-max-bytes={'32M' if self.is_stadium else '384M'}",
            f"--demuxer-max-back-bytes={'16M' if self.is_stadium else '128M'}",
            f"--demuxer-readahead-secs={self._buffer_secs if not self.is_stadium else 2}",
            "--correct-pts=yes",
            "--video-sync=audio",
            "--stream-buffer-size=2M",
            "--network-timeout=15",
            "--stream-lavf-o=reconnect=1,reconnect_streamed=1,reconnect_delay_max=5",
            "--hr-seek=yes",
            "--deinterlace=auto",
            # Audio nativo PipeWire estéreo para ThinkPad X390
            "--ao=pipewire,pulse,alsa",
            "--audio-device=auto",
            "--audio-channels=stereo",
            "--audio-pitch-correction=yes",
            "--aid=auto",
            "--alang=es,spa,cat,ca,en,eng",
            f"--volume={self._vol}",
            "--mute=no" if not self._muted else "--mute=yes",
            f"--user-agent={UA_IPTV}",
            f"--http-header-fields=User-Agent: {UA_IPTV}",
            "--no-ytdl",
            "--no-sub",
        ]
        # Perfil de máximo rendimiento: decodificación HW y búfer óptimos.
        if PERF_AVAILABLE:
            try:
                args.extend(best_mpv_args())
            except Exception:
                pass
        args.append(stream_url)

        self._proc = QProcess(self)
        env = QProcessEnvironment.systemEnvironment()
        env.remove("WAYLAND_DISPLAY")
        env.insert("QT_QPA_PLATFORM", "xcb")
        uid = os.getuid()
        runtime_dir = f"/run/user/{uid}"
        if not env.contains("XDG_RUNTIME_DIR") and os.path.exists(runtime_dir):
            env.insert("XDG_RUNTIME_DIR", runtime_dir)
        if not env.contains("PULSE_SERVER") and os.path.exists(f"{runtime_dir}/pulse/native"):
            env.insert("PULSE_SERVER", f"unix:{runtime_dir}/pulse/native")
        if not env.contains("PIPEWIRE_RUNTIME_DIR") and os.path.exists(runtime_dir):
            env.insert("PIPEWIRE_RUNTIME_DIR", runtime_dir)
        self._proc.setProcessEnvironment(env)
        self._proc.finished.connect(self._safe_show_placeholder)
        self._proc.start("mpv", args)
        self.track_poll_timer.start()

    def _safe_show_placeholder(self):
        try:
            if hasattr(self, "placeholder") and self.placeholder:
                self.placeholder.show()
        except Exception:
            pass

    def _play_vlc(self, stream_url: str):
        """Reproduce con libvlc embebido en el widget Qt (reemplazo del motor MPV)."""
        try:
            import vlc
            if self._vlc_instance is None:
                self._vlc_instance = vlc.Instance("--no-video-title-show")
            self._vlc_player = self._vlc_instance.media_player_new()
            # Enlaza la superficie del widget (X11 / XWayland)
            self._ensure_native_window()
            self._vlc_player.set_xwindow(int(self.winId()))
            media = self._vlc_instance.media_new(stream_url)
            media.add_option(f":http-user-agent={UA_IPTV}")
            media.add_option(":network-caching=5000")
            if PERF_AVAILABLE:
                try:
                    for opt in best_vlc_options():
                        media.add_option(opt)
                except Exception:
                    pass
            self._vlc_player.set_media(media)
            self._vlc_player.audio_set_volume(self._vol)
            self._vlc_player.audio_set_mute(self._muted)
            self._vlc_player.play()
            self.track_poll_timer.start()
        except Exception as e:
            print(f"[SLONE ENGINE] VLC no disponible ({e}); conmutando a SLONE nativo.")
            self._play_mpv(stream_url)

    def stop(self):
        self.track_poll_timer.stop()
        if getattr(self, "_vlc_player", None) is not None:
            try:
                self._vlc_player.stop()
                self._vlc_player.release()
            except Exception:
                pass
            self._vlc_player = None
        if self._proc:
            self._ipc_command(["quit"])
            self._proc.waitForFinished(200)
            self._proc.kill()
            self._proc = None
        self._safe_show_placeholder()

    def toggle_pause(self):
        if self._engine_name() == "vlc" and self._vlc_player is not None:
            try:
                self._vlc_player.pause()
                return
            except Exception:
                pass
        self._ipc_command(["cycle", "pause"])

    def cycle_audio(self):
        """Alternar a la siguiente pista de audio (Español, Català, Radio SER, COPE, etc.)."""
        if not self.current_tracks:
            self._ipc_command(["cycle", "audio"])
            QTimer.singleShot(400, self._query_audio_tracks)
            return
        curr_idx = 0
        for i, t in enumerate(self.current_tracks):
            if t.get("selected"):
                curr_idx = i
                break
        next_idx = (curr_idx + 1) % len(self.current_tracks)
        next_track = self.current_tracks[next_idx]
        self.set_audio_option(next_track)

    def set_audio_option(self, track_info: dict):
        """Aplica una opción de audio concreta (pista de TV o comentario de radio sincronizada)."""
        t_type = track_info.get("type", "stream")
        title = track_info.get("title", "")
        if t_type == "stream":
            self._active_radio = None
            mpv_id = track_info.get("mpv_id", 1)
            self._ipc_command(["set_property", "aid", mpv_id])
            self._ipc_command(["show-text", f"SLONE Audio: {title}", 2500])
        elif t_type == "radio":
            self._active_radio = track_info.get("id")
            url = track_info.get("url")
            self._ipc_command(["audio-add", url, "select", title])
            self._ipc_command(["show-text", f"SLONE Multi-Audio: {title}", 3000])

        QTimer.singleShot(400, self._query_audio_tracks)

    def set_audio_delay(self, secs: float) -> float:
        """Ajusta el retardo milimétrico de audio para sincronizar radio sobre vídeo."""
        self._audio_delay = round(float(secs), 2)
        self._ipc_command(["set_property", "audio-delay", str(self._audio_delay)])
        sign = "+" if self._audio_delay > 0 else ""
        self._ipc_command(["show-text", f"SLONE Audio-Sync: {sign}{self._audio_delay}s", 1500])
        return self._audio_delay

    def adjust_audio_delay(self, delta: float) -> float:
        """Incrementa o decrementa el retardo de audio en pasos de delta segundos."""
        cur = getattr(self, "_audio_delay", 0.0)
        return self.set_audio_delay(cur + delta)

    def set_buffer_secs(self, secs: int):
        self._buffer_secs = max(1, min(30, int(secs)))
        set_app_setting("buffer_secs", self._buffer_secs)

    def seek_relative(self, seconds: int):
        if self._engine_name() == "vlc" and self._vlc_player is not None:
            try:
                t = self._vlc_player.get_time()
                if t and t > 0:
                    self._vlc_player.set_time(t + seconds * 1000)
                return
            except Exception:
                pass
        self._ipc_command(["seek", str(seconds), "relative"])

    def set_volume(self, val: int):
        self._vol = max(0, min(100, int(val)))
        if self._muted:
            self._muted = False
            self._ipc_command(["set_property", "mute", "no"])
            if self._engine_name() == "vlc" and self._vlc_player is not None:
                try: self._vlc_player.audio_set_mute(False)
                except Exception: pass
        if self._engine_name() == "vlc" and self._vlc_player is not None:
            try:
                self._vlc_player.audio_set_volume(self._vol)
                return
            except Exception:
                pass
        self._ipc_command(["set_property", "volume", self._vol])

    def toggle_mute(self) -> bool:
        self._muted = not self._muted
        val_str = "yes" if self._muted else "no"
        if self._engine_name() == "vlc" and self._vlc_player is not None:
            try:
                self._vlc_player.audio_set_mute(self._muted)
                return self._muted
            except Exception:
                pass
        self._ipc_command(["set_property", "mute", val_str])
        return self._muted

    def unmute(self):
        self._muted = False
        if self._engine_name() == "vlc" and self._vlc_player is not None:
            try: self._vlc_player.audio_set_mute(False)
            except Exception: pass
        self._ipc_command(["set_property", "mute", "no"])

    def mute(self):
        self._muted = True
        if self._engine_name() == "vlc" and self._vlc_player is not None:
            try: self._vlc_player.audio_set_mute(True)
            except Exception: pass
        self._ipc_command(["set_property", "mute", "yes"])

    def is_playing(self) -> bool:
        if self._engine_name() == "vlc" and self._vlc_player is not None:
            try:
                return bool(self._vlc_player.is_playing())
            except Exception:
                return False
        return self._proc is not None and self._proc.state() == QProcess.ProcessState.Running

    def _ipc_command(self, cmd_list: list) -> dict | None:
        if not os.path.exists(self.ipc_socket):
            return None
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(0.4)
            s.connect(self.ipc_socket)
            payload = json.dumps({"command": cmd_list}).encode() + b"\n"
            s.sendall(payload)
            resp = s.recv(4096)
            s.close()
            return json.loads(resp.decode(errors="ignore"))
        except Exception:
            return None

    def _query_audio_tracks(self):
        """Consulta pistas nativas y las fusiona con el catálogo Multi-Audio de SLONE."""
        if self._engine_name() == "vlc":
            return
        res = self._ipc_command(["get_property", "track-list"])
        tracks = []
        if res and "data" in res:
            for t in res["data"]:
                if t.get("type") == "audio":
                    tid = t.get("id", 1)
                    title = t.get("title") or t.get("lang") or f"Pista {tid}"
                    lang = t.get("lang", "")
                    selected = t.get("selected", False)

                    # Embellecer nombres (Català, Español, etc.)
                    if lang.lower() in ("cat", "ca"): title = f"Català (Audio {tid})"
                    elif lang.lower() in ("spa", "es"): title = f"Español TV (Audio {tid})"
                    elif lang.lower() in ("eng", "en"): title = f"English (Audio {tid})"
                    else: title = f"Audio {tid} ({title})"
                    tracks.append({
                        "id": f"stream_{tid}",
                        "mpv_id": tid,
                        "title": title,
                        "selected": selected and (self._active_radio is None),
                        "type": "stream"
                    })

        if not tracks:
            tracks.append({
                "id": "stream_1",
                "mpv_id": 1,
                "title": "Español (Sonido TV Directo)",
                "selected": (self._active_radio is None),
                "type": "stream"
            })

        # Añadir emisoras sincronizadas de Multi-Audio SLONE
        for r in SLONE_MULTI_AUDIO_RADIOS:
            is_sel = (self._active_radio == r["id"])
            tracks.append({
                "id": r["id"],
                "url": r["url"],
                "title": r["title"],
                "selected": is_sel,
                "type": "radio"
            })

        self.current_tracks = tracks
        self.audio_tracks_updated.emit(tracks)

# ──────────────────────────────────────────────────────────────
#  SLONE MULTIVIEW STADIUM™ 4X (CUADRÍCULA MULTI-DEPORTE 2X2)
# ──────────────────────────────────────────────────────────────
class MultiviewStadiumWidget(QWidget):
    """
    SLONE MULTIVIEW STADIUM™ 4X
    Cuadrícula 2x2 para seguir 4 partidos o señales en directo simultáneas.
    Permite alternar el canal de audio instantáneamente con las teclas 1, 2, 3 o 4.
    """
    quadrant_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StadiumWidget")
        self.active_quadrant = 0
        self.accent_color = "#E3FF00"
        self.quadrants: list = []

        grid = QGridLayout(self)
        grid.setContentsMargins(4, 4, 4, 4)
        grid.setSpacing(6)

        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for i in range(4):
            q_box = QWidget()
            q_box.setObjectName(f"StadiumQuad_{i}")
            ql = QVBoxLayout(q_box)
            ql.setContentsMargins(3, 3, 3, 3)
            ql.setSpacing(2)

            bar = QWidget()
            bar.setFixedHeight(26)
            bhl = QHBoxLayout(bar)
            bhl.setContentsMargins(6, 1, 6, 1)
            bhl.setSpacing(6)

            lbl_title = QLabel(f"[{i+1}] SEÑAL {i+1} — Sin señal")
            lbl_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #FFFFFF;")

            btn_audio = QPushButton(f"🔊 AUDIO {i+1}" if i == 0 else "🔇 MUTE")
            btn_audio.setObjectName("BtnNeon" if i == 0 else "BtnDark")
            btn_audio.setFixedHeight(20)
            btn_audio.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_audio.clicked.connect(lambda checked, idx=i: self.set_active_audio(idx))

            bhl.addWidget(lbl_title, 1)
            bhl.addWidget(btn_audio)
            ql.addWidget(bar)

            # Instancia MPV dedicada con su socket IPC único y búfer optimizado (32M)
            sock = str(Path(tempfile.gettempdir()) / f"slone_stadium_{os.getpid()}_{i}.sock")
            player = MPVWidget(self, ipc_socket=sock, is_stadium=True)
            player.placeholder.setText(f"🏟️ SEÑAL {i+1}\n\nSelecciona un canal para este cuadrante\n[Tecla {i+1}: Activar Audio]")
            ql.addWidget(player, 1)

            grid.addWidget(q_box, positions[i][0], positions[i][1])

            self.quadrants.append({
                "index": i,
                "box": q_box,
                "bar": bar,
                "lbl_title": lbl_title,
                "btn_audio": btn_audio,
                "player": player,
                "channel": None
            })

        self.update_visual_state(self.accent_color)

    def set_active_audio(self, index: int):
        if not (0 <= index < 4):
            return
        self.active_quadrant = index
        for i, q in enumerate(self.quadrants):
            if i == index:
                q["player"].unmute()
                q["btn_audio"].setText(f"🔊 AUDIO {i+1}")
                q["btn_audio"].setObjectName("BtnNeon")
            else:
                q["player"].mute()
                q["btn_audio"].setText("🔇 MUTE")
                q["btn_audio"].setObjectName("BtnDark")
            q["btn_audio"].style().unpolish(q["btn_audio"])
            q["btn_audio"].style().polish(q["btn_audio"])
        self.update_visual_state(self.accent_color)
        self.quadrant_selected.emit(index)

    def update_visual_state(self, accent_color: str = "#E3FF00"):
        self.accent_color = accent_color
        for i, q in enumerate(self.quadrants):
            is_act = (i == self.active_quadrant)
            border_color = accent_color if is_act else "#1D212A"
            border_w = "2px" if is_act else "1px"
            q["box"].setStyleSheet(f"""
                QWidget#StadiumQuad_{i} {{
                    border: {border_w} solid {border_color};
                    border-radius: 6px;
                    background-color: #060709;
                }}
            """)

    def play_channel_in_quadrant(self, index: int, channel: dict):
        if not (0 <= index < 4):
            return
        q = self.quadrants[index]
        q["channel"] = channel
        name = channel.get("name", f"Canal {index+1}")
        url = channel.get("url", "")
        q["lbl_title"].setText(f"[{index+1}] {name}")
        if url:
            q["player"].play(url)
            if index != self.active_quadrant:
                q["player"].mute()

    def stop_all(self):
        for q in self.quadrants:
            q["player"].stop()


# ──────────────────────────────────────────────────────────────
#  CARGADOR ASÍNCRONO M3U CON INDEXACIÓN POR PAÍSES
# ──────────────────────────────────────────────────────────────
class M3ULoaderThread(QThread):
    channels_ready = pyqtSignal(list, dict, str)

    def __init__(self, source: str = "", content: str = ""):
        super().__init__()
        self.source = source
        self.content = content

    def run(self):
        try:
            if self.content:
                content = self.content
            elif (self.source or "").strip().lower().startswith(("http://", "https://")):
                req = urllib.request.Request((self.source or "").strip(), headers={"User-Agent": UA_IPTV})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    content = resp.read().decode("utf-8", errors="ignore")
            else:
                content = Path(os.path.expanduser(self.source)).read_text(encoding="utf-8", errors="ignore")
            channels = []
            countries_map = {
                "🇪🇸 España": [],
                "🇬🇧 Reino Unido": [],
                "🇺🇸 Estados Unidos": [],
                "🇫🇷 Francia": [],
                "🇮🇹 Italia": [],
                "🇩🇪 Alemania": [],
                "🇵🇹 Portugal": [],
                "🌎 Latinoamérica": [],
                "🌐 Otros": []
            }
            cur_name = "Canal"
            cur_group = "Otros"
            cur_logo = ""
            cur_epg = ""

            for line in content.splitlines():
                line = line.strip()
                if line.startswith("#EXTINF:"):
                    parts = line.split(",", 1)
                    cur_name = parts[1].strip() if len(parts) > 1 else "Canal"
                    cur_group = "Otros"
                    cur_logo = ""
                    cur_epg = ""
                    g_m = re.search(r'group-title="([^"]*)"', line)
                    if g_m and g_m.group(1).strip(): cur_group = g_m.group(1).strip()
                    l_m = re.search(r'tvg-logo="([^"]*)"', line)
                    if l_m: cur_logo = l_m.group(1).strip()
                    e_m = re.search(r'tvg-id="([^"]*)"', line)
                    if e_m: cur_epg = e_m.group(1).strip()
                elif line and not line.startswith("#"):
                    item = {"name": cur_name, "url": line, "group": cur_group,
                            "logo": cur_logo, "epg_id": cur_epg}
                    channels.append(item)

                    # Clasificación por país estructurada
                    g_up = (cur_group + " " + cur_name).upper()
                    g_norm = g_up.replace(" ", "")  # tolera "ES |", "ES -", etc.

                    def _hit(keys):
                        return any(k in g_up or k in g_norm for k in keys)

                    if _hit(["ES-", "ES|", "[ES]", "ES:", "SPAIN", "ESPAÑA", "MOVISTAR", "LALIGA"]):
                        countries_map["🇪🇸 España"].append(item)
                    elif _hit(["UK-", "UK|", "[UK]", "ENGLAND", "UK:", "UNITEDKINGDOM"]):
                        countries_map["🇬🇧 Reino Unido"].append(item)
                    elif _hit(["US-", "USA", "US|", "[US]", "US:", "UNITEDSTATES"]):
                        countries_map["🇺🇸 Estados Unidos"].append(item)
                    elif _hit(["FR-", "FRANCE", "FR|", "[FR]", "FR:"]):
                        countries_map["🇫🇷 Francia"].append(item)
                    elif _hit(["IT-", "ITALY", "IT|", "[IT]", "IT:"]):
                        countries_map["🇮🇹 Italia"].append(item)
                    elif _hit(["DE-", "GERMAN", "DE|", "[DE]", "DE:"]):
                        countries_map["🇩🇪 Alemania"].append(item)
                    elif _hit(["PT-", "PORTUGAL", "PT|", "[PT]", "PT:"]):
                        countries_map["🇵🇹 Portugal"].append(item)
                    elif _hit(["AR-", "MX-", "MX|", "CO-", "CL-", "LATINO", "LATAM", "[MX]", "[AR]"]):
                        countries_map["🌎 Latinoamérica"].append(item)
                    else:
                        countries_map["🌐 Otros"].append(item)

                    cur_name = "Canal"
                    cur_group = "Otros"
                    cur_logo = ""
                    cur_epg = ""

            self.channels_ready.emit(channels, countries_map, content)
        except Exception:
            pass


class XtreamLoaderThread(QThread):
    """Descarga canales Live + VOD de un panel Xtream Codes y los exporta a M3U."""
    m3u_ready = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, host: str, username: str, password: str):
        super().__init__()
        self.host = host
        self.username = username
        self.password = password

    def run(self):
        try:
            if not XTREAM_AVAILABLE or XtreamClient is None:
                self.error.emit("Módulo Xtream no disponible (falta xtream_parser.py).")
                return
            cli = XtreamClient(self.host, self.username, self.password)
            if not cli.authenticate():
                self.error.emit("Credenciales Xtream rechazadas (host/usuario/contraseña).")
                return
            cats = {str(c.get("id")): c.get("category_name", "Xtream Live")
                    for c in cli.get_live_categories()}
            lines = ["#EXTM3U"]
            n_live = 0
            for s in cli.get_live_streams():
                url = s.get("url", "")
                if not url:
                    continue
                name = (s.get("name") or "Canal").replace(",", " ").strip()
                group = cats.get(str(s.get("category_id", "")), "Xtream Live")
                logo = s.get("logo", "") or ""
                epg = s.get("epg_id", "") or ""
                lines.append(f'#EXTINF:-1 tvg-id="{epg}" tvg-logo="{logo}" group-title="{group}",{name}')
                lines.append(url)
                n_live += 1
            n_vod = 0
            for m in cli.get_vod_streams():
                sid = m.get("stream_id")
                if not sid:
                    continue
                ext = m.get("container_extension", "mp4")
                url = f"{cli.base_url}/movie/{cli.username}/{cli.password}/{sid}.{ext}"
                name = (m.get("name") or "Película").replace(",", " ").strip()
                logo = m.get("stream_icon", "") or ""
                lines.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="🎬 VOD",{name}')
                lines.append(url)
                n_vod += 1
            if n_live + n_vod == 0:
                self.error.emit("El panel respondió pero no devolvió canales.")
                return
            self.m3u_ready.emit("\n".join(lines))
        except Exception as e:
            self.error.emit(str(e))


class EpgLoaderThread(QThread):
    """Descarga y parsea guías XMLTV en segundo plano."""
    epg_ready = pyqtSignal(int)

    def __init__(self, manager, urls: list):
        super().__init__()
        self.manager = manager
        self.urls = urls

    def run(self):
        try:
            count = self.manager.load_urls(self.urls)
        except Exception:
            count = 0
        self.epg_ready.emit(count)


class DeepSeekThread(QThread):
    """Consulta a la API DeepSeek (metadatos o ping) sin bloquear la interfaz."""
    meta_ready = pyqtSignal(dict)
    ping_ok = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, client, title: str = "", kind: str = "película", mode: str = "meta"):
        super().__init__()
        self.client = client
        self.title = title
        self.kind = kind
        self.mode = mode

    def run(self):
        try:
            if self.mode == "ping":
                self.ping_ok.emit(self.client.ping())
            else:
                self.meta_ready.emit(self.client.describe_title(self.title, self.kind))
        except Exception as e:
            self.error.emit(str(e))


# ──────────────────────────────────────────────────────────────
#  VENTANA PRINCIPAL SLONE OS
# ──────────────────────────────────────────────────────────────
class SLONEMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SLONE GLOBAL MEDIA ENGINE")
        self.resize(1360, 850)
        self.cur_theme = str(get_app_setting("ui_theme", "obsidian") or "obsidian")
        self.setStyleSheet(get_slone_stylesheet(self.cur_theme))

        # Icono oficial de la marca
        icon_path = find_icon()
        if icon_path:
            self.setWindowIcon(QIcon(str(icon_path)))

        self.all_channels: list = []
        self.countries_map: dict = {}
        self.groups_order: list = []
        self.groups_map: dict = {}
        self.recent_channels: list = []
        self.bookmarked_channels: list = []
        self.current_channel: dict | None = None
        self.selected_group: str = "ALL"
        self.order_mode: str = str(get_app_setting("order_mode", "original") or "original")
        self.channel_limit_per_page: int = int(get_app_setting("channel_limit", 500) or 500)
        self.selected_country: str = "🇪🇸 España"
        self.selected_subcategory: str = "Todos"

        # Hub & Relay
        self.relay = RelayServer()
        self.relay.start()
        HUB.app_window = self

        # Controlador Xiaomi TV
        self.cast_ctl = XiaomiCastController()
        self.cast_ctl.cast_status.connect(self._on_cast_status)

        # Reproductor MPV con soporte multi-audio y modo Multiview Stadium 4X
        self.mpv = MPVWidget(self)
        self.mpv.double_clicked.connect(self._toggle_fullscreen)
        self.mpv.audio_tracks_updated.connect(self._on_audio_tracks_detected)
        self.stadium_mode = False
        self.stadium_widget = None

        # Motores EPG (guía) y Xtream Codes
        self.epg = EpgManager() if EPG_AVAILABLE else None
        self.epg_thread = None
        self.xtream_thread = None
        self.ai_thread = None
        self._epg_autoloaded = False

        # Búsqueda con debounce
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._execute_search)

        self._build_ui()
        self._setup_shortcuts()
        self._check_autoload()

    def _build_ui(self):
        # Barra de menús nativa completa (oculta para mantener interfaz limpia y soberana SLONE)
        self._build_menu_bar()
        self.menuBar().hide()

        root = QWidget()
        self.setCentralWidget(root)
        vl = QVBoxLayout(root)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)

        # 1. Header superior limpio con pestaña de menú en la esquina
        self.top_header = self._build_top_header()
        vl.addWidget(self.top_header)

        # 2. Cuerpo: Drawer Lateral SLONE + Stack de páginas + Drawer de Ajustes
        body = QWidget()
        hl = QHBoxLayout(body)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(0)

        # Drawer Lateral de Menú Principal SLONE (esquina izquierda, oculto por defecto)
        self.slone_drawer = self._build_slone_drawer()
        self.tivimate_drawer = self.slone_drawer  # Alias compatibilidad interna
        self.slone_drawer.hide()
        hl.addWidget(self.slone_drawer)

        self.stack = QStackedWidget()
        self.stack.currentChanged.connect(self._on_stack_changed)
        self.stack.addWidget(self._page_channels())    # 0: Canales IPTV (sloTV)
        self.stack.addWidget(self._page_favorites())   # 1: Favoritos (sloFAVS)
        self.stack.addWidget(self._page_recents())     # 2: Recientes
        self.stack.addWidget(self._page_remote())      # 3: Mando Web Móvil (sloREMOTE)
        self.stack.addWidget(self._page_cast())        # 4: Transmitir a TV (sloCAST)
        self.stack.addWidget(self._page_files())       # 5: Vídeo Local (sloFILES)
        self.stack.addWidget(self._page_settings())    # 6: Ajustes Pro (sloSETTINGS)
        self.stack.addWidget(self._page_music())       # 7: Música & Radios (sloMUSIC)
        self.stack.addWidget(self._page_dj())          # 8: Cabina DJ & Producción (sloDJ)

        hl.addWidget(self.stack, 1)

        # Drawer Lateral de Ajustes SLONE Pro (derecha)
        self.settings_drawer = self._build_settings_drawer()
        self.settings_drawer.hide()
        hl.addWidget(self.settings_drawer)

        vl.addWidget(body, 1)

        # 3. Barra inferior de control (oculta para máxima visibilidad de vídeo y canales)
        self.bottom_dock = self._build_bottom_dock()
        self.bottom_dock.hide()
        vl.addWidget(self.bottom_dock)

    def _on_stack_changed(self, idx: int):
        """Mantiene sincronizados los botones de navegación superior si existen."""
        if hasattr(self, "nav_group"):
            btn = self.nav_group.button(idx)
            if btn:
                btn.setChecked(True)

    def _toggle_slone_drawer(self):
        """Muestra u oculta el cajón lateral de menú principal SLONE."""
        drawer = getattr(self, "slone_drawer", getattr(self, "tivimate_drawer", None))
        if not drawer:
            return
        is_visible = drawer.isVisible()
        if is_visible:
            drawer.hide()
            if hasattr(self, "btn_menu_tab"):
                self.btn_menu_tab.setText("☰  MENÚ")
        else:
            drawer.show()
            if hasattr(self, "btn_menu_tab"):
                self.btn_menu_tab.setText("✕  CERRAR")

    def _toggle_tivimate_drawer(self):
        """Alias de compatibilidad."""
        self._toggle_slone_drawer()

    def _build_slone_drawer(self) -> QWidget:
        """Cajón de navegación principal unificado SLONE."""
        drawer = QWidget()
        drawer.setObjectName("SloneDrawer")
        drawer.setFixedWidth(320)
        vl = QVBoxLayout(drawer)
        vl.setContentsMargins(12, 12, 12, 12)
        vl.setSpacing(10)

        # Cabecera del Cajón
        head = QWidget()
        head.setObjectName("DrawerHeader")
        hl_head = QHBoxLayout(head)
        hl_head.setContentsMargins(4, 0, 4, 8)
        title = QLabel("👑 MENÚ PRINCIPAL SLONE")
        title.setObjectName("DrawerTitle")
        hl_head.addWidget(title)
        hl_head.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setObjectName("DrawerCloseBtn")
        btn_close.setToolTip("Cerrar menú [Esc / M]")
        btn_close.clicked.connect(self._toggle_slone_drawer)
        hl_head.addWidget(btn_close)
        vl.addWidget(head)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        sl = QVBoxLayout(scroll_content)
        sl.setContentsMargins(0, 0, 6, 0)
        sl.setSpacing(8)

        def make_section(title_text: str):
            lbl = QLabel(title_text)
            lbl.setObjectName("DrawerSectionHeader")
            sl.addWidget(lbl)

        def make_btn(icon_text: str, label_text: str, callback, tooltip: str = ""):
            btn = QPushButton(f" {icon_text}   {label_text}")
            btn.setObjectName("DrawerNavBtn")
            if tooltip:
                btn.setToolTip(tooltip)
            btn.clicked.connect(lambda: (callback(), self._toggle_slone_drawer()))
            sl.addWidget(btn)
            return btn

        # ── 1. TELEVISIÓN & CANALES ──
        make_section("📺 TELEVISIÓN & STADIUM")
        make_btn("📺", "sloTV — Canales en Directo", lambda: self.stack.setCurrentIndex(0), "Lista de canales principal")
        make_btn("🏟️", "sloSTADIUM™ — Multiview 4X [F4]", self.toggle_stadium_mode, "Seguir 4 partidos o señales en directo a la vez")
        make_btn("★", "sloFAVS — Canales Favoritos", lambda: self.stack.setCurrentIndex(1), "Ver favoritos guardados")
        make_btn("🕒", "Historial / Recientes", lambda: self.stack.setCurrentIndex(2), "Ver canales recientes")
        make_btn("📁", "sloFILES — Vídeo Local / Archivos", lambda: self.stack.setCurrentIndex(5), "Reproducir archivos de disco")
        make_btn("📑", "Filtrar Grupos de Canales", self._show_filter_menu, "Seleccionar grupo de canales")
        make_btn("◀", "Ocultar / Mostrar Canales [C]", self._toggle_channel_panel, "Alternar visualización de la lista")

        # ── 2. MÚSICA & AUDIO PROFESIONAL ──
        make_section("🎧 MÚSICA & PRODUCCIÓN DJ")
        make_btn("📻", "sloMUSIC — Radios & Streams en Directo", lambda: self.stack.setCurrentIndex(7), "Emisoras de alta calidad, YouTube y podcasts")
        make_btn("🎧", "sloDJ™ — Cabina de Mezclas Pro", lambda: self.stack.setCurrentIndex(8), "Estudio profesional de DJ con doble plato y ecualizador")
        make_btn("🇪🇸", "TDT Abierta España & Catalunya", self._load_tdt_spain, "Cargar canales oficiales de TDT sin antena")
        make_btn("🎨", "Color de tu Equipo (Temas UI)", self._open_theme_selector, "Cambiar colores de la pantalla según tu club")

        # ── 3. CONECTIVIDAD & DISPOSITIVOS ──
        make_section("📡 CONECTIVIDAD & SMART TV")
        make_btn("📡", "sloCAST™ — Envío a Smart TV [E]", self._show_tv_connect_dialog, "Transmitir emisión a Smart TV / Proyector")
        self.btn_top_cast = make_btn("📺", "sloCAST™ — Smart TV (DLNA/LAN)", self._cast_to_xiaomi_tv, "Enviar emisión a la TV")
        self.btn_top_tivimate = QPushButton()
        make_btn("📱", "sloREMOTE™ — Mando a Distancia Web", lambda: self.stack.setCurrentIndex(3), "Control remoto móvil")

        # ── 4. GESTIÓN DE LISTAS ──
        make_section("📂 LISTAS DE REPRODUCCIÓN")
        make_btn("➕", "Añadir / Cambiar Lista M3U", self._show_source_menu, "Cargar archivo, URL o Xtream")
        make_btn("🔄", "Recargar Lista de Canales", self._check_autoload, "Actualizar canales [F5]")
        make_btn("💾", "Exportar Lista M3U", self._export_playlist_dialog, "Guardar lista actual a archivo")

        # ── 5. SISTEMA Y AJUSTES ──
        make_section("⚙ SISTEMA Y AJUSTES")
        make_btn("⚙", "sloSETTINGS — Ajustes Pro & Audio [O]", lambda: self.toggle_settings_drawer(True), "Configurar reproductor y audio")
        make_btn("🩺", "Diagnóstico de Emisión", self._diagnose_current_stream, "Analizar salud del stream actual")
        make_btn("ℹ️", "Ayuda & Atajos de Teclado", self._show_shortcuts_dialog, "Guía de atajos de teclado")

        sl.addStretch()
        scroll.setWidget(scroll_content)
        vl.addWidget(scroll, 1)

        # Footer con estado de red
        footer = QLabel("🌐 192.168.1.145:8765 · ThinkPad X390")
        footer.setObjectName("DrawerFooter")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.addWidget(footer)

        return drawer

    def _show_filter_menu(self):
        """Muestra menú rápido para seleccionar grupo IPTV sin saturar la pantalla principal."""
        menu = QMenu(self)
        menu.setTitle("📑 Grupos IPTV")
        for i in range(self.group_combo.count()):
            txt = self.group_combo.itemText(i)
            act = menu.addAction(txt)
            act.triggered.connect(lambda _checked=False, idx=i: self.group_combo.setCurrentIndex(idx))
        if hasattr(self, "btn_menu_tab") and self.btn_menu_tab.isVisible():
            pos = self.btn_menu_tab.mapToGlobal(self.btn_menu_tab.rect().bottomLeft())
        else:
            pos = QCursor.pos()
        menu.exec(pos)

    def apply_theme(self, theme_key: str):
        """Aplica la paleta de colores del tema seleccionado en caliente."""
        if theme_key not in SLONE_THEMES:
            theme_key = "obsidian"
        self.cur_theme = theme_key
        set_app_setting("ui_theme", theme_key)
        css = get_slone_stylesheet(theme_key)
        self.setStyleSheet(css)
        t = SLONE_THEMES[theme_key]
        if hasattr(self, "brand_label"):
            self.brand_label.setStyleSheet(f"color: {t['accent']}; font-weight: 900; font-size: 14px; letter-spacing: 1px;")
        if hasattr(self, "btn_menu_tab"):
            self.btn_menu_tab.setStyleSheet(f"background-color: {t['accent']}; color: #000000; font-weight: 900; border-radius: 8px;")
        if hasattr(self, "mpv") and hasattr(self.mpv, "_ipc_command"):
            self.mpv._ipc_command(["show-text", f"SLONE Tema: {t['name']}", 2000])
        if hasattr(self, "stadium_widget") and self.stadium_widget is not None:
            self.stadium_widget.update_visual_state(t["accent"])

    def _load_tdt_spain(self):
        """Carga la lista maestra de canales abiertos oficiales y radios deportivas de SLONE."""
        master_path = PROJECT_DIR / "playlists" / "slone_sovereign_master.m3u8"
        tdt_path = PROJECT_DIR / "playlists" / "tdt_spain.m3u"
        target = master_path if master_path.exists() else tdt_path
        if target.exists():
            self._load_source(str(target))
            if hasattr(self, "osd_channel_label"):
                self.osd_channel_label.setText("📺 SLONE Sovereign Master (430 Canales & Radios)")
        else:
            self._load_source("https://www.tdtchannels.com/lists/tv.m3u8")

    def _open_direct_media_dialog(self):
        """Diálogo interactivo para reproducir música de YouTube, stream web o podcast."""
        dlg = QDialog(self)
        dlg.setWindowTitle("🎵 SLONE · Música Directa, YouTube o Web Stream")
        dlg.resize(540, 240)
        dlg.setStyleSheet("""
            QDialog { background-color: #0A0B10; color: #FFFFFF; font-family: sans-serif; }
            QLabel { color: #E0E0E0; font-size: 13px; }
            QLineEdit { background-color: #141724; color: #E3FF00; border: 1px solid #252A3D; border-radius: 6px; padding: 8px 12px; font-size: 13px; font-weight: bold; }
            QPushButton { background-color: #1A1E2E; color: #FFFFFF; border: 1px solid #333A50; border-radius: 6px; padding: 7px 14px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background-color: #262D45; border-color: #E3FF00; color: #E3FF00; }
        """)
        vl = QVBoxLayout(dlg)
        vl.setContentsMargins(20, 20, 20, 20)
        vl.setSpacing(12)
        
        lbl = QLabel("🎵 Reproducir Música Directa, YouTube o Podcast")
        lbl.setStyleSheet("font-size: 15px; font-weight: 900; color: #E3FF00;")
        vl.addWidget(lbl)
        
        desc = QLabel("Pega cualquier enlace de YouTube (vídeo o playlist), stream de audio web o podcast:")
        desc.setStyleSheet("color: #8E92A4; font-size: 11px;")
        vl.addWidget(desc)
        
        txt = QLineEdit()
        txt.setPlaceholderText("https://www.youtube.com/watch?v=... o https://stream.mp3...")
        vl.addWidget(txt)
        
        hl_btns = QHBoxLayout()
        btn_yt_music = QPushButton("📻 Los 40")
        btn_yt_music.clicked.connect(lambda: txt.setText("https://21253.live.streamtheworld.com/LOS40.mp3"))
        btn_rock = QPushButton("🎸 Rock FM")
        btn_rock.clicked.connect(lambda: txt.setText("https://flucast06-b-cloud.flumotion.com/cope/rockfm.mp3"))
        btn_chill = QPushButton("🌴 Ibiza Chill")
        btn_chill.clicked.connect(lambda: txt.setText("https://listenssl.ibizaglobalradio.com:8024/ibizaglobalradio.mp3"))
        hl_btns.addWidget(btn_yt_music)
        hl_btns.addWidget(btn_rock)
        hl_btns.addWidget(btn_chill)
        vl.addLayout(hl_btns)
        
        btn_play = QPushButton("▶ REPRODUCIR DIRECTAMENTE")
        btn_play.setStyleSheet("background-color: #E3FF00; color: #000000; font-weight: 900; padding: 10px;")
        def do_play():
            url = txt.text().strip()
            if url:
                dlg.accept()
                self._play_direct_url(url)
        btn_play.clicked.connect(do_play)
        vl.addWidget(btn_play)
        dlg.exec()

    def _play_direct_url(self, url: str):
        self.mpv.play_url(url)
        if hasattr(self, "osd_channel_label"):
            self.osd_channel_label.setText(f"🎵 Emisión Directa: {url[:45]}...")

    def _open_theme_selector(self):
        """Muestra un menú rápido para cambiar el tema/color del equipo."""
        menu = QMenu(self)
        menu.setTitle("🎨 Colores de tu Equipo")
        for k, t in SLONE_THEMES.items():
            act = menu.addAction(f"{t['name']}")
            act.triggered.connect(lambda checked, tk=k: self.apply_theme(tk))
        pos = QCursor.pos()
        menu.exec(pos)

    # ── HEADER SUPERIOR LIMPIO CON PESTAÑA EN LA ESQUINA ───────────
    def _build_top_header(self) -> QWidget:
        h = QWidget()
        h.setObjectName("TopHeader")
        hl = QHBoxLayout(h)
        hl.setContentsMargins(10, 0, 14, 0)
        hl.setSpacing(10)

        # Pestaña en la esquina para todos los menús de SLONE
        self.btn_menu_tab = QPushButton("☰  MENÚ")
        self.btn_menu_tab.setObjectName("MenuCornerTab")
        self.btn_menu_tab.setToolTip("Abrir menú principal SLONE [M / F1]")
        self.btn_menu_tab.clicked.connect(self._toggle_slone_drawer)
        hl.addWidget(self.btn_menu_tab)

        # Logo e icono oficial
        logo_label = QLabel()
        self.header_logo_label = logo_label
        logo_path = find_icon()
        if logo_path:
            pix = QPixmap(str(logo_path)).scaled(26, 26, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pix)
        hl.addWidget(logo_label)

        brand = QLabel("👑  SLONE ENGINE")
        brand.setObjectName("BrandTitle")
        brand.setStyleSheet("color: #E3FF00; font-weight: 900; font-size: 14px; letter-spacing: 1px;")
        self.brand_label = brand
        hl.addWidget(brand)

        # Barra rápida de navegación directa slo*
        self.nav_container = QWidget()
        nav_hl = QHBoxLayout(self.nav_container)
        nav_hl.setContentsMargins(8, 0, 8, 0)
        nav_hl.setSpacing(4)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        nav_items = [
            ("📺 sloTV", 0, "Canales de televisión en directo [sloTV]"),
            ("🏟️ sloSTADIUM", -1, "Multiview Stadium™ 4X en directo [F4]"),
            ("📻 sloMUSIC", 7, "Radios oficiales, música directa y YouTube [sloMUSIC]"),
            ("🎧 sloDJ", 8, "Cabina profesional de mezclas y producción DJ [sloDJ]"),
            ("📡 sloCAST", 4, "Transmisión directa a Smart TV y DLNA [sloCAST]"),
            ("📱 sloREMOTE", 3, "Mando a distancia web para el móvil [sloREMOTE]"),
        ]

        for text, idx, tip in nav_items:
            b = QPushButton(text)
            b.setCheckable(True)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.setToolTip(tip)
            b.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #A0A5B5;
                    border: 1px solid transparent;
                    border-radius: 6px;
                    padding: 5px 9px;
                    font-size: 11px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    color: #FFFFFF;
                    background-color: #171A24;
                    border: 1px solid #282C3D;
                }
                QPushButton:checked {
                    color: #000000;
                    background-color: #E3FF00;
                    font-weight: 900;
                }
            """)
            if idx == 0:
                b.setChecked(True)

            def make_handler(index=idx):
                if index == -1:
                    return self.toggle_stadium_mode
                else:
                    return lambda: self._on_nav_clicked(index)

            b.clicked.connect(make_handler(idx))
            if idx >= 0:
                self.nav_group.addButton(b, idx)
            nav_hl.addWidget(b)

        hl.addWidget(self.nav_container)
        hl.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchBox")
        self.search_input.setPlaceholderText("🔍 Buscar canal...")
        self.search_input.textChanged.connect(lambda: self.search_timer.start(250))
        hl.addWidget(self.search_input)

        btn_fs = QPushButton("⛶")
        btn_fs.setObjectName("CtlBtn")
        btn_fs.setToolTip("Pantalla Completa [F / F11]")
        btn_fs.clicked.connect(self._toggle_fullscreen)
        hl.addWidget(btn_fs)

        return h

    def _build_sidebar(self) -> QWidget:
        """Compatibilidad: el menú lateral ha sido integrado en el cajón principal SLONE."""
        return QWidget()

    # ── PÁGINA 0: CANALES IPTV CON PANEL DEDICADO Y REPRODUCTOR ───
    def _page_channels(self) -> QWidget:
        w = QWidget()
        self.page_channels_widget = w
        self.page_channels_layout = QVBoxLayout(w)
        self.page_channels_layout.setContentsMargins(8, 6, 8, 6)
        self.page_channels_layout.setSpacing(0)

        # Splitter principal: Panel de Canales (Izquierda) | Reproductor (Derecha)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setObjectName("MainSplitter")

        # ── COLUMNA IZQUIERDA: LISTA Y FILTROS DE CANALES ──
        self.channel_panel = QWidget()
        self.channel_panel.setObjectName("ChannelPanel")
        cp_layout = QVBoxLayout(self.channel_panel)
        cp_layout.setContentsMargins(4, 4, 6, 4)
        cp_layout.setSpacing(6)

        # Contenedor de filtros y grupos (oculto de la pantalla principal para máxima limpieza de lista)
        self.filter_panel = QWidget()
        self.filter_panel.setObjectName("FilterPanel")
        fp_layout = QVBoxLayout(self.filter_panel)
        fp_layout.setContentsMargins(0, 0, 0, 0)
        fp_layout.setSpacing(4)

        # Fila 1: Selector de Grupo IPTV + Botón Ocultar + Conteo de canales
        filter_row1 = QHBoxLayout()
        filter_row1.setSpacing(6)

        self.group_combo = QComboBox()
        self.group_combo.setObjectName("CountryCombo")
        self.group_combo.addItem("⭐ Todos los canales (De serie)", "ALL")
        self.group_combo.currentIndexChanged.connect(self._on_group_changed)
        filter_row1.addWidget(self.group_combo, 1)

        self.btn_toggle_channels = QPushButton("◀ Ocultar")
        self.btn_toggle_channels.setObjectName("BtnDark")
        self.btn_toggle_channels.setToolTip("Ocultar o mostrar lista de canales para expandir el vídeo [C / Tab]")
        self.btn_toggle_channels.clicked.connect(self._toggle_channel_panel)
        filter_row1.addWidget(self.btn_toggle_channels)

        self.btn_add_source = QPushButton("➕ M3U")
        self.btn_add_source.hide()

        self.lbl_channel_count = QLabel("0 canales")
        self.lbl_channel_count.setStyleSheet("color: #E3FF00; font-weight: 900; font-size: 11px;")
        filter_row1.addWidget(self.lbl_channel_count)
        fp_layout.addLayout(filter_row1)

        # Fila 2: Chips de categorías rápidas
        filter_row2 = QHBoxLayout()
        filter_row2.setSpacing(4)
        self.subcat_group = QButtonGroup(self)
        self.subcat_group.setExclusive(True)

        subcategories = ["Todos", "⚽ Fútbol", "🎬 Cine", "📰 TDT", "★ Favoritos"]
        for idx, sub_text in enumerate(subcategories):
            btn = QPushButton(sub_text)
            btn.setObjectName("CategoryChip")
            btn.setCheckable(True)
            if idx == 0:
                btn.setChecked(True)
            filter_row2.addWidget(btn)
            self.subcat_group.addButton(btn, idx)

        self.subcat_group.idClicked.connect(self._on_subcategory_chip_clicked)
        fp_layout.addLayout(filter_row2)

        self.filter_panel.hide() # Oculto por defecto de la pantalla principal
        cp_layout.addWidget(self.filter_panel)

        # Modo de ordenación (en memoria para sincronización bidireccional con menús nativos)
        self.order_combo = QComboBox()
        self.order_combo.setObjectName("CountryCombo")
        self.order_combo.addItem("De serie (Original IPTV)", "original")
        self.order_combo.addItem("Alfabético (A → Z)", "alpha")
        self.order_combo.addItem("SLOCAST Inteligente", "slocast")
        idx_ord = self.order_combo.findData(self.order_mode)
        if idx_ord >= 0:
            self.order_combo.setCurrentIndex(idx_ord)
        self.order_combo.currentIndexChanged.connect(self._on_order_combo_changed)
        self.order_combo.hide()

        # Widget lista de canales con ancho garantizado para ver el nombre completo
        self.channel_list = QListWidget()
        self.channel_list.setObjectName("ChannelList")
        self.channel_list.setMinimumWidth(380)
        self.channel_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.channel_list.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.channel_list.setUniformItemSizes(True)
        self.channel_list.itemClicked.connect(self._on_channel_clicked)
        self.channel_list.itemDoubleClicked.connect(self._on_channel_double_clicked)
        cp_layout.addWidget(self.channel_list, 1)

        self.channel_panel.setMinimumWidth(380)

        # ── COLUMNA DERECHA: REPRODUCTOR DE VÍDEO ──
        self.player_container = QWidget()
        self.player_layout = QVBoxLayout(self.player_container)
        self.player_layout.setContentsMargins(6, 4, 4, 4)
        self.player_layout.setSpacing(4)

        self.slone_banner = self._build_slone_banner()
        self.tivimate_banner = self.slone_banner  # Alias compatibilidad
        self.player_layout.addWidget(self.slone_banner)

        # Contenedor conmutador: Reproductor Individual vs Multiview Stadium 4X
        self.player_stack = QStackedWidget()
        self.player_stack.addWidget(self.mpv)  # Índice 0: Pantalla única
        self.stadium_widget = MultiviewStadiumWidget(self)
        self.stadium_widget.quadrant_selected.connect(self._on_stadium_quadrant_selected)
        self.player_stack.addWidget(self.stadium_widget)  # Índice 1: Cuadrícula 4X
        self.player_layout.addWidget(self.player_stack, 1)

        # Barra inferior minimalista: botón Multiview Stadium + botón SLONE Cast
        player_bottom_bar = QWidget()
        player_bottom_bar.setObjectName("PlayerBottomBar")
        pb_layout = QHBoxLayout(player_bottom_bar)
        pb_layout.setContentsMargins(0, 2, 6, 2)
        pb_layout.setSpacing(8)

        self.btn_stadium_bottom = QPushButton("🏟️ Multiview Stadium 4X [F4]")
        self.btn_stadium_bottom.setObjectName("BtnNeon")
        self.btn_stadium_bottom.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_stadium_bottom.setToolTip("Conmutar a cuadrícula 4X para seguir 4 deportes a la vez [F4]")
        self.btn_stadium_bottom.clicked.connect(self.toggle_stadium_mode)
        pb_layout.addWidget(self.btn_stadium_bottom)
        pb_layout.addStretch()
        self.btn_google_cast = QPushButton()
        self.btn_google_cast.setObjectName("GoogleCastBtn")
        self.btn_google_cast.setToolTip("SLONE Cast · Transmitir emisión a Smart TV [E]")
        cast_icon_path = APP_DIR / "assets" / "slone_cast.svg"
        if not cast_icon_path.exists():
            cast_icon_path = APP_DIR / "assets" / "google_cast.svg"
        if cast_icon_path.exists():
            self.btn_google_cast.setIcon(QIcon(str(cast_icon_path)))
            self.btn_google_cast.setIconSize(QSize(22, 22))
        else:
            self.btn_google_cast.setText("⎚")
        self.btn_google_cast.clicked.connect(self._show_tv_connect_dialog)
        pb_layout.addWidget(self.btn_google_cast)
        self.player_layout.addWidget(player_bottom_bar)

        self.main_splitter.addWidget(self.channel_panel)
        self.main_splitter.addWidget(self.player_container)
        self.main_splitter.setCollapsible(0, True)
        self.main_splitter.setCollapsible(1, False)
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setSizes([400, 960])

        self.page_channels_layout.addWidget(self.main_splitter, 1)
        return w

    # ── PÁGINA 1: FAVORITOS ────────────────────────────────────────
    def _page_favorites(self) -> QWidget:
        w = QWidget()
        vl = QVBoxLayout(w)
        vl.setContentsMargins(24, 20, 24, 20)
        ttl = QLabel("★  Canales Favoritos")
        ttl.setStyleSheet("font-size: 18px; font-weight: 900; color: #E3FF00;")
        vl.addWidget(ttl)
        self.fav_list = QListWidget()
        self.fav_list.itemDoubleClicked.connect(self._on_channel_double_clicked)
        vl.addWidget(self.fav_list, 1)
        return w

    # ── PÁGINA 2: RECIENTES ────────────────────────────────────────
    def _page_recents(self) -> QWidget:
        w = QWidget()
        vl = QVBoxLayout(w)
        vl.setContentsMargins(24, 20, 24, 20)
        ttl = QLabel("🕒  Canales Vistos Recientemente")
        ttl.setStyleSheet("font-size: 18px; font-weight: 900; color: #E3FF00;")
        vl.addWidget(ttl)
        self.recents_list = QListWidget()
        self.recents_list.itemDoubleClicked.connect(self._on_channel_double_clicked)
        vl.addWidget(self.recents_list, 1)
        return w

    # ── PÁGINA 3: MANDO WEB MÓVIL (SOFÁ) ──────────────────────────
    def _page_remote(self) -> QWidget:
        w = QWidget()
        vl = QVBoxLayout(w)
        vl.setContentsMargins(28, 24, 28, 24)
        vl.setSpacing(14)

        ttl = QLabel("📱  Mando a Distancia en tu Teléfono Móvil")
        ttl.setStyleSheet("font-size: 18px; font-weight: 900; color: #E3FF00;")
        vl.addWidget(ttl)

        box = QWidget(); box.setObjectName("CardItem")
        bl = QVBoxLayout(box)
        bl.setSpacing(10)
        bl.addWidget(QLabel("👑 <b>Controla SLONE desde el sofá con cualquier smartphone</b>"))
        bl.addWidget(QLabel("Abre esta dirección en el navegador de tu móvil o tablet (conectado a tu WiFi):"))

        row = QHBoxLayout()
        txt_url = QLineEdit()
        txt_url.setReadOnly(True)
        txt_url.setText(self.relay.remote_url)
        txt_url.setStyleSheet("background: #000; color: #E3FF00; font-family: monospace; font-size: 15px; border: 1px solid #E3FF00; padding: 10px;")
        btn_c = QPushButton("📋 Copiar")
        btn_c.setObjectName("BtnNeon")
        btn_c.clicked.connect(lambda: (QApplication.clipboard().setText(self.relay.remote_url), QMessageBox.information(self, "Copiado", f"Enlace copiado:\n{self.relay.remote_url}")))
        row.addWidget(txt_url)
        row.addWidget(btn_c)
        bl.addLayout(row)

        desc = QLabel("El mando móvil incluye: <b>Pausar/Reanudar</b>, <b>Cambio de audio (Català/Radio/TV)</b>, <b>Cambio de canal</b> y <b>Proyección directa a Xiaomi TV</b>.")
        desc.setStyleSheet("color: #888; font-size: 12px; margin-top: 6px;")
        bl.addWidget(desc)
        vl.addWidget(box)

        vl.addStretch()
        return w

    # ── PÁGINA 4: TRANSMITIR A XIAOMI TV & RELAY ──────────────────
    def _page_cast(self) -> QWidget:
        w = QWidget()
        vl = QVBoxLayout(w)
        vl.setContentsMargins(28, 24, 28, 24)
        vl.setSpacing(16)

        ttl = QLabel("📡  Transmisión a Xiaomi TV & Red Doméstica")
        ttl.setStyleSheet("font-size: 18px; font-weight: 900; color: #E3FF00;")
        vl.addWidget(ttl)

        card_tv = QWidget(); card_tv.setObjectName("CardItem")
        ctl = QVBoxLayout(card_tv)
        ctl.setSpacing(10)
        ctl.addWidget(QLabel(f"👑 <b>{get_app_setting('cast_name', 'SLÖNE')} — Chromecast en {get_app_setting('cast_ip', '192.168.1.135')}:8009</b>"))
        ctl.addWidget(QLabel("Proyecta directamente el canal actual a la tele sin cortes ni multiconexión."))

        btn_row = QHBoxLayout()
        btn_cast_now = QPushButton("📺  Proyectar Canal en Xiaomi TV")
        btn_cast_now.setObjectName("BtnNeon")
        btn_cast_now.clicked.connect(self._cast_to_xiaomi_tv)

        btn_stop_tv = QPushButton("⏹  Detener TV")
        btn_stop_tv.setObjectName("BtnDark")
        btn_stop_tv.setFixedWidth(120)
        btn_stop_tv.clicked.connect(self.cast_ctl.stop_cast)

        btn_row.addWidget(btn_cast_now)
        btn_row.addWidget(btn_stop_tv)
        ctl.addLayout(btn_row)
        vl.addWidget(card_tv)

        card_relay = QWidget(); card_relay.setObjectName("CardItem")
        crl = QVBoxLayout(card_relay)
        crl.setSpacing(10)
        crl.addWidget(QLabel("🔗 <b>Enlace Relay para VLC y Smart TV</b>"))
        crl.addWidget(QLabel(f"<code>{self.relay.stream_url}</code>"))
        vl.addWidget(card_relay)

        vl.addStretch()
        return w

    # ── PÁGINA 5: VÍDEOS LOCALES ──────────────────────────────────
    def _page_files(self) -> QWidget:
        w = QWidget()
        vl = QVBoxLayout(w)
        vl.setContentsMargins(28, 24, 28, 24)
        vl.setSpacing(14)
        ttl = QLabel("📁  Reproducción de Vídeo Local")
        ttl.setStyleSheet("font-size: 18px; font-weight: 900; color: #E3FF00;")
        desc = QLabel("Abre cualquier archivo (MP4, MKV, TS). Se reproducirá en SLONE y se enviará al Hub Relay para tu TV.")
        desc.setStyleSheet("color: #888;")
        btn_open = QPushButton("🎬  Seleccionar Vídeo del Ordenador...")
        btn_open.setObjectName("BtnNeon")
        btn_open.setFixedWidth(280)
        btn_open.clicked.connect(self._open_local_video)

        self.lbl_local_file = QLabel("Ningún archivo abierto")
        self.lbl_local_file.setStyleSheet("color: #666;")

        vl.addWidget(ttl)
        vl.addWidget(desc)
        vl.addWidget(btn_open)
        vl.addWidget(self.lbl_local_file)
        vl.addStretch()
        return w

    # ── PÁGINA 6: AJUSTES PRO ─────────────────────────────────────
    def _page_settings(self) -> QWidget:
        w = QWidget()
        vl = QVBoxLayout(w)
        vl.setContentsMargins(28, 24, 28, 24)
        vl.setSpacing(14)

        ttl = QLabel("⚙  Ajustes y Parámetros de SLONE OS")
        ttl.setStyleSheet("font-size: 18px; font-weight: 900; color: #E3FF00;")
        vl.addWidget(ttl)

        box = QWidget(); box.setObjectName("CardItem")
        bl = QVBoxLayout(box)
        bl.setSpacing(10)
        bl.addWidget(QLabel(f"<b>• Motor Multimedia:</b> SLONE ULTRA ENGINE con IPC socket nativo ({MPV_IPC_SOCKET})"))
        bl.addWidget(QLabel("<b>• Modo Cero-Latencia:</b> Búfer adaptativo anti-cortes (5s recomendados para fútbol)"))
        bl.addWidget(QLabel("<b>• Anti-Freeze Watchdog:</b> Auto-reconexión TCP y sincronización continua video-sync=audio"))
        bl.addWidget(QLabel("<b>• Selector de Audio:</b> Soporte Multi-Audio (Català RAC1, CatRàdio, SER, COPE, Radio Marca y TV)"))
        bl.addWidget(QLabel(f"<b>• Dispositivo Cast:</b> {get_app_setting('cast_name', 'SLÖNE')} ({get_app_setting('cast_ip', '192.168.1.135')} · Puerto 8009)"))
        bl.addWidget(QLabel("<b>• Puerto Relay Local:</b> 8765"))
        vl.addWidget(box)

        # Selector de motor de reproducción (SLONE / VLC)
        eng_row = QHBoxLayout()
        eng_lbl = QLabel("<b>Motor de reproducción:</b>")
        eng_row.addWidget(eng_lbl)
        self.engine_combo = QComboBox()
        self.engine_combo.addItem("SLONE ULTRA ENGINE (IPC nativo · Alta fidelidad · Recomendado)", "mpv")
        if VLC_AVAILABLE:
            self.engine_combo.addItem("VLC (libvlc · máxima compatibilidad)", "vlc")
        else:
            self.engine_combo.addItem("VLC (no disponible: falta python-vlc)", "vlc_disabled")
        cur = str(get_app_setting("engine", "mpv") or "mpv").lower()
        idx = self.engine_combo.findData(cur)
        if idx >= 0:
            self.engine_combo.setCurrentIndex(idx)
        self.engine_combo.currentIndexChanged.connect(self._on_engine_changed)
        eng_row.addWidget(self.engine_combo)
        eng_row.addStretch()
        vl.addLayout(eng_row)

        # Estado del enclave biométrico
        try:
            from slone_auth import biometric_available
            bio = biometric_available()
        except Exception:
            bio = False
        vl.addWidget(QLabel(f"<b>Biometría (fprintd):</b> {'✅ disponible' if bio else '⚠ no disponible'} "
                            f"· <b>Directiva:</b> {'activada' if get_control_directive().get('enclave_biometrico_activo', True) else 'desactivada'}"))

        btn_row = QHBoxLayout()
        btn_reload = QPushButton("🔄  Recargar Lista M3U")
        btn_reload.setObjectName("BtnDark")
        btn_reload.setFixedWidth(200)
        btn_reload.clicked.connect(self._check_autoload)
        btn_row.addWidget(btn_reload)

        btn_add = QPushButton("➕  Añadir fuente M3U")
        btn_add.setObjectName("BtnDark")
        btn_add.setFixedWidth(200)
        btn_add.clicked.connect(self._show_source_menu_settings)
        btn_row.addWidget(btn_add)
        btn_row.addStretch()
        vl.addLayout(btn_row)

        # EPG + Xtream Codes
        src2 = QHBoxLayout()
        btn_epg = QPushButton("📺  Configurar EPG")
        btn_epg.setObjectName("BtnDark")
        btn_epg.setFixedWidth(200)
        btn_epg.clicked.connect(self._show_epg_menu)
        src2.addWidget(btn_epg)
        btn_xtream = QPushButton("🛰  Xtream Codes…")
        btn_xtream.setObjectName("BtnDark")
        btn_xtream.setFixedWidth(200)
        btn_xtream.clicked.connect(self._prompt_xtream)
        src2.addWidget(btn_xtream)
        src2.addStretch()
        vl.addLayout(src2)

        # Metadatos IA (DeepSeek)
        ai_box = QWidget()
        ai_box.setObjectName("CardItem")
        al = QFormLayout(ai_box)
        self.ai_key = QLineEdit()
        self.ai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.ai_key.setPlaceholderText("sk-… (o define $DEEPSEEK_API_KEY / config/deepseek.env)")
        self.ai_key.textChanged.connect(self._refresh_ai_status)
        cfg_ai = get_app_setting("deepseek", {}) or {}
        self.ai_key.setText(cfg_ai.get("api_key", ""))
        btn_reveal = QPushButton("👁")
        btn_reveal.setObjectName("BtnDark")
        btn_reveal.setFixedWidth(40)
        btn_reveal.setCheckable(True)
        btn_reveal.setToolTip("Mostrar / ocultar la clave")
        btn_reveal.toggled.connect(
            lambda on: self.ai_key.setEchoMode(
                QLineEdit.EchoMode.Normal if on else QLineEdit.EchoMode.Password))
        key_row = QHBoxLayout()
        key_row.setContentsMargins(0, 0, 0, 0)
        key_row.addWidget(self.ai_key)
        key_row.addWidget(btn_reveal)
        key_box = QWidget()
        key_box.setLayout(key_row)
        self.ai_model = QComboBox()
        self.ai_model.setEditable(True)  # permite escribir modelos nuevos
        for m in ("deepseek-flash", "deepseek-v4-pro", "deepseek-v4-flash"):
            self.ai_model.addItem(m)
        mi = self.ai_model.findText(cfg_ai.get("model", "deepseek-flash"))
        if mi >= 0:
            self.ai_model.setCurrentIndex(mi)
        al.addRow("DeepSeek API key:", key_box)
        al.addRow("Modelo IA:", self.ai_model)
        ai_btns = QHBoxLayout()
        b_save = QPushButton("💾  Guardar IA")
        b_save.setObjectName("BtnDark")
        b_save.clicked.connect(self._save_ai_config)
        b_test = QPushButton("🧪  Probar conexión")
        b_test.setObjectName("BtnDark")
        b_test.clicked.connect(self._test_ai)
        b_rich = QPushButton("✨  Analizar canal actual")
        b_rich.setObjectName("BtnNeon")
        b_rich.clicked.connect(self._enrich_current_ai)
        ai_btns.addWidget(b_save)
        ai_btns.addWidget(b_test)
        ai_btns.addWidget(b_rich)
        al.addRow(ai_btns)
        self.lbl_ai_status = QLabel(self._ai_status_text())
        self.lbl_ai_status.setStyleSheet("color: #9FE870;")
        al.addRow(self.lbl_ai_status)
        vl.addWidget(ai_box)

        # ── SEGURIDAD & RENDIMIENTO (control total) ───────────────
        sec_box = QWidget()
        sec_box.setObjectName("CardItem")
        sl = QVBoxLayout(sec_box)
        sl.addWidget(QLabel("<b>🔒 Escudo de Seguridad SLONE</b>"))
        self.chk_shield = QCheckBox("Escudo activo (rate-limit, anti-hackers, log de intrusiones)")
        self.chk_shield.setChecked(bool(self._shield_cfg("escudo_activo", True)))
        self.chk_shield.stateChanged.connect(self._save_security)
        sl.addWidget(self.chk_shield)
        self.chk_lan = QCheckBox("Permitir acceso LAN (necesario para Cast/TV y mando móvil)")
        self.chk_lan.setChecked(bool(self._shield_cfg("permitir_lan", False)))
        self.chk_lan.stateChanged.connect(self._save_security)
        sl.addWidget(self.chk_lan)
        self.lbl_sec = QLabel(self._security_status_text())
        self.lbl_sec.setStyleSheet("color: #9FE870;")
        sl.addWidget(self.lbl_sec)
        sec_btns = QHBoxLayout()
        b_tok = QPushButton("🔑  Ver/Rotar token LAN")
        b_tok.setObjectName("BtnDark")
        b_tok.clicked.connect(self._rotate_lan_token)
        b_log = QPushButton("📜  Registro de bloqueos")
        b_log.setObjectName("BtnDark")
        b_log.clicked.connect(self._show_security_log)
        sec_btns.addWidget(b_tok)
        sec_btns.addWidget(b_log)
        sec_btns.addStretch()
        sl.addLayout(sec_btns)

        sl.addWidget(QLabel("<b>🚀 Perfil de máximo rendimiento</b>"))
        self.lbl_perf = QLabel(self._perf_status_text())
        self.lbl_perf.setStyleSheet("color: #E3FF00;")
        self.lbl_perf.setWordWrap(True)
        sl.addWidget(self.lbl_perf)
        b_perf = QPushButton("🚀  Aplicar perfil máximo rendimiento")
        b_perf.setObjectName("BtnNeon")
        b_perf.clicked.connect(self._apply_perf_profile)
        sl.addWidget(b_perf)
        vl.addWidget(sec_box)

        vl.addStretch()
        return w

    # ── PÁGINA 7: sloMUSIC™ (RADIOS, YOUTUBE & STREAMING) ─────────
    def _page_music(self) -> QWidget:
        w = QWidget()
        w.setObjectName("PageSloMusic")
        vl = QVBoxLayout(w)
        vl.setContentsMargins(24, 20, 24, 20)
        vl.setSpacing(14)

        # Cabecera
        head = QWidget()
        hl = QHBoxLayout(head)
        hl.setContentsMargins(0, 0, 0, 0)
        ttl = QLabel("📻  sloMUSIC™ — RADIOS EN DIRECTO & AUDIO STREAMING")
        ttl.setStyleSheet("font-size: 17px; font-weight: 900; color: #E3FF00; letter-spacing: 1px;")
        hl.addWidget(ttl)
        hl.addStretch()
        btn_open_dj = QPushButton("🎧 Abrir Cabina sloDJ™")
        btn_open_dj.setObjectName("BtnNeon")
        btn_open_dj.clicked.connect(lambda: self.stack.setCurrentIndex(8))
        hl.addWidget(btn_open_dj)
        vl.addWidget(head)

        # Barra de Entrada Directa (YouTube, Streams, Podcasts)
        box_input = QWidget()
        box_input.setObjectName("CardItem")
        bil = QVBoxLayout(box_input)
        bil.setSpacing(8)
        lbl_in = QLabel("<b>🎵 Reproductor de audio directo / Enlaces de YouTube / Podcasts:</b>")
        bil.addWidget(lbl_in)

        row_in = QHBoxLayout()
        txt_url = QLineEdit()
        txt_url.setPlaceholderText("https://www.youtube.com/watch?v=... o https://stream.mp3...")
        row_in.addWidget(txt_url, 1)

        btn_play_direct = QPushButton("▶ Reproducir")
        btn_play_direct.setObjectName("BtnNeon")
        btn_play_direct.clicked.connect(lambda: self._play_direct_url(txt_url.text().strip()) if txt_url.text().strip() else None)
        row_in.addWidget(btn_play_direct)

        btn_to_deck_a = QPushButton("🎧 Deck A (sloDJ)")
        btn_to_deck_a.setObjectName("BtnDark")
        btn_to_deck_a.clicked.connect(lambda: self._load_into_dj_deck("A", txt_url.text().strip(), "Audio Web") if txt_url.text().strip() else None)
        row_in.addWidget(btn_to_deck_a)

        btn_to_deck_b = QPushButton("🎧 Deck B (sloDJ)")
        btn_to_deck_b.setObjectName("BtnDark")
        btn_to_deck_b.clicked.connect(lambda: self._load_into_dj_deck("B", txt_url.text().strip(), "Audio Web") if txt_url.text().strip() else None)
        row_in.addWidget(btn_to_deck_b)

        bil.addLayout(row_in)
        vl.addWidget(box_input)

        # Parrilla de Emisoras Oficiales de Alta Calidad
        lbl_grid = QLabel("<b>📻 Emisoras de Radio Oficiales y Canales Musicales:</b>")
        vl.addWidget(lbl_grid)

        stations = [
            ("🇪🇸 Los 40 Principales", "Top Éxitos Pop & Urban", "https://21253.live.streamtheworld.com/LOS40.mp3", "#E3FF00"),
            ("🎸 Rock FM", "Clásicos del Rock Internacional", "https://flucast06-b-cloud.flumotion.com/cope/rockfm.mp3", "#FF4444"),
            ("🌴 Ibiza Global Radio", "Electronic, Deep House & Sunset", "https://listenssl.ibizaglobalradio.com:8024/ibizaglobalradio.mp3", "#00F0FF"),
            ("🎧 Flaix FM", "Dance & Urban Hits Catalunya", "https://en-directe.flaixfm.cat/flaixfm.mp3", "#FF8800"),
            ("💋 Kiss FM", "Lo Mejor de los 80, 90 y 2000s", "https://kissfm.kissfmradio.cires21.com/kissfm.mp3", "#FF2277"),
            ("🎶 Cadena 100", "Las 100 mejores canciones pop", "https://flucast06-b-cloud.flumotion.com/cope/cadena100.mp3", "#33CC66"),
            ("🔵 iCat CCMA", "Música emergente y tendencias", "https://directes-radio-cat.ccma.cat/live-origin/icat-mp3", "#00A8FF"),
            ("📻 Radio 3 RNE", "Indie, Electrónica y Vanguardia", "https://rtveaudio-live.rtve.es/rne_r3_main.mp3", "#A855F7"),
        ]

        grid = QGridLayout()
        grid.setSpacing(10)
        for i, (name, desc, url, col) in enumerate(stations):
            card = QWidget()
            card.setObjectName("CardItem")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(12, 10, 12, 10)
            cl.setSpacing(6)

            st_title = QLabel(name)
            st_title.setStyleSheet(f"font-size: 13px; font-weight: 900; color: {col};")
            cl.addWidget(st_title)

            st_desc = QLabel(desc)
            st_desc.setStyleSheet("color: #8E92A4; font-size: 11px;")
            cl.addWidget(st_desc)

            btns_row = QHBoxLayout()
            b_play = QPushButton("▶ Sonar")
            b_play.setObjectName("BtnNeon")
            b_play.clicked.connect(lambda chk=False, u=url, n=name: self._play_music_station(u, n))
            btns_row.addWidget(b_play)

            b_deck = QPushButton("🎧 Deck A")
            b_deck.setObjectName("BtnDark")
            b_deck.setToolTip("Cargar en Deck A de sloDJ")
            b_deck.clicked.connect(lambda chk=False, u=url, n=name: self._load_into_dj_deck("A", u, n))
            btns_row.addWidget(b_deck)

            b_deck2 = QPushButton("🎧 Deck B")
            b_deck2.setObjectName("BtnDark")
            b_deck2.setToolTip("Cargar en Deck B de sloDJ")
            b_deck2.clicked.connect(lambda chk=False, u=url, n=name: self._load_into_dj_deck("B", u, n))
            btns_row.addWidget(b_deck2)

            cl.addLayout(btns_row)
            row = i // 2
            col_pos = i % 2
            grid.addWidget(card, row, col_pos)

        vl.addLayout(grid)
        vl.addStretch()
        return w

    def _play_music_station(self, url: str, name: str):
        """Reproduce una emisora de radio o stream en el motor de audio."""
        self._play_direct_url(url)
        if hasattr(self, "osd_channel_label"):
            self.osd_channel_label.setText(f"📻 {name}")
        if hasattr(self, "mpv") and hasattr(self.mpv, "_ipc_command"):
            self.mpv._ipc_command(["show-text", f"📻 sloMUSIC: {name}", 3000])

    def _load_into_dj_deck(self, deck_id: str, url: str, name: str = ""):
        """Carga una pista o stream directamente en el plato especificado de sloDJ."""
        self.stack.setCurrentIndex(8)
        if hasattr(self, "dj_studio") and self.dj_studio is not None:
            if deck_id.upper() == "A":
                self.dj_studio.deck_a.load_file(url)
            else:
                self.dj_studio.deck_b.load_file(url)
            if hasattr(self, "mpv") and hasattr(self.mpv, "_ipc_command"):
                self.mpv._ipc_command(["show-text", f"🎧 Pista cargada en sloDJ Deck {deck_id}: {name or url[:25]}", 2500])

    # ── PÁGINA 8: sloDJ™ (CABINA DE MEZCLAS PROFESIONAL) ───────────
    def _page_dj(self) -> QWidget:
        """Página 8: Cabina de DJ y Producción sloDJ™"""
        try:
            try:
                from slone_dj import SloDJStudioWidget
            except ImportError:
                from app.slone_dj import SloDJStudioWidget
            self.dj_studio = SloDJStudioWidget(self)
            return self.dj_studio
        except Exception as e:
            fallback = QWidget()
            vl = QVBoxLayout(fallback)
            vl.addWidget(QLabel(f"⚠ Error inicializando sloDJ: {e}"))
            return fallback

    # ── SEGURIDAD & RENDIMIENTO — manejadores ────────────────────
    def _shield_cfg(self, key, default=None):
        try:
            from slone_security import load_policy
            return load_policy().get(key, default)
        except Exception:
            return default

    def _security_status_text(self) -> str:
        if SHIELD is None:
            return "⚠ Escudo no disponible"
        s = SHIELD.stats()
        return (f"Estado: {'ACTIVO' if s['escudo_activo'] else 'inactivo'} · "
                f"Bind: {s['bind']} · Bloqueos: {s['bloqueos_totales']} · "
                f"IPs baneadas: {s['ips_baneadas']} · Límite: {s['max_peticiones_por_min']}/min")

    def _save_security(self, *_):
        try:
            from slone_security import save_policy, SHIELD as SEC
            save_policy({
                "escudo_activo": self.chk_shield.isChecked(),
                "permitir_lan": self.chk_lan.isChecked(),
            })
            if SEC is not None:
                SEC.reload()
        except Exception as e:
            QMessageBox.warning(self, "Seguridad", f"No se pudo guardar: {e}")
        # Reinicia el relay para aplicar el nuevo modo de bind (LAN ↔ local)
        try:
            if getattr(self, "relay", None) is not None:
                self.relay.stop()
                self.relay.start()
        except Exception:
            pass
        self.lbl_sec.setText(self._security_status_text())

    def _rotate_lan_token(self):
        if SHIELD is None:
            QMessageBox.warning(self, "Seguridad", "Escudo no disponible.")
            return
        tok = SHIELD.rotate_token()
        QApplication.clipboard().setText(tok)
        QMessageBox.information(
            self, "Token LAN",
            f"Nuevo token generado y copiado al portapapeles:\n\n{tok}\n\n"
            "Úsalo en el mando móvil así:\n  .../remote?token=" + tok)

    def _show_security_log(self):
        try:
            from slone_security import LOG_PATH
            p = Path(LOG_PATH)
            lines = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
        except Exception:
            lines = []
        tail = "\n".join(lines[-30:]) or "Sin eventos registrados."
        QMessageBox.information(self, "SLONE Shield — Registro de bloqueos", tail)

    def _perf_status_text(self) -> str:
        if not PERF_AVAILABLE:
            return "⚠ Módulo de rendimiento no disponible"
        try:
            return perf_summary()
        except Exception:
            return "Perfil de rendimiento listo."

    def _apply_perf_profile(self):
        if not PERF_AVAILABLE:
            QMessageBox.warning(self, "Rendimiento", "Módulo de rendimiento no disponible.")
            return
        ok = False
        try:
            ok = apply_performance_profile()
        except Exception as e:
            QMessageBox.warning(self, "Rendimiento", f"Error: {e}")
            return
        if ok:
            try:
                hw = detect_hardware()
            except Exception:
                hw = {"cpu": "n/d", "cores": 0, "ram_gb": 0, "gpu": "n/d", "governor": "n/d"}
            QMessageBox.information(
                self, "Perfil máximo rendimiento",
                "✅ Perfil aplicado y guardado.\n\n"
                f"CPU: {hw.get('cpu')}\nNúcleos: {hw.get('cores')} · RAM: {hw.get('ram_gb')} GB\n"
                f"GPU: {hw.get('gpu')}\nGobernador CPU: {hw.get('governor') or 'n/d'}\n\n"
                "Se aplicará al reproducir el próximo canal.\n"
                "Potencia extra del SO (root):  bash scripts/slone_hardening.sh")
        else:
            QMessageBox.warning(self, "Rendimiento", "No se pudo guardar el perfil.")
        self.lbl_perf.setText(self._perf_status_text())

    def _on_engine_changed(self, idx: int):
        data = self.engine_combo.itemData(idx)
        if data == "vlc_disabled":
            QMessageBox.information(
                self, "Motor VLC",
                "python-vlc no está instalado.\n\nInstálalo con:\n    pip install --user python-vlc"
            )
            cur = str(get_app_setting("engine", "mpv") or "mpv")
            i = self.engine_combo.findData(cur)
            if i >= 0:
                self.engine_combo.setCurrentIndex(i)
            return
        set_app_setting("engine", data)
        self.lbl_channel_title.setText(f"Motor activo: {data.upper()}")

    def _show_source_menu_settings(self):
        menu = QMenu(self)
        act_custom = menu.addAction("🔗  URL o archivo M3U/M3U8…")
        act_custom.triggered.connect(self._prompt_add_source)
        menu.addSeparator()
        for label, url in IPTV_ORG_SOURCES.items():
            act = menu.addAction(f"📡  iptv-org · {label}")
            act.triggered.connect(lambda _checked=False, u=url: self._load_iptv_org(u))
        menu.addSeparator()
        act_xt = menu.addAction("🛰  Conectar panel Xtream Codes…")
        act_xt.triggered.connect(self._prompt_xtream)
        menu.addSeparator()
        act_tv = menu.addAction("📡 SLONE TV Connect™ (Sincronizar con Smart TV)…")
        act_tv.triggered.connect(self._show_tv_connect_dialog)
        menu.exec(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))

    # ── BARRA INFERIOR DE REPRODUCCIÓN (SLONE DOCK) ───────────────
    def _build_bottom_dock(self) -> QWidget:
        b = QWidget()
        b.setObjectName("BottomDock")
        hl = QHBoxLayout(b)
        hl.setContentsMargins(14, 0, 14, 0)
        hl.setSpacing(10)

        self.btn_pp = QPushButton("▶")
        self.btn_pp.setObjectName("CtlBtn")
        self.btn_pp.clicked.connect(self._toggle_playback)

        self.btn_rewind = QPushButton("⏪ -10s")
        self.btn_rewind.setObjectName("CtlBtn")
        self.btn_rewind.setToolTip("Timeshift: Rebobinar 10 segundos")
        self.btn_rewind.clicked.connect(lambda: self.mpv.seek_relative(-10))

        self.btn_forward = QPushButton("+10s ⏩")
        self.btn_forward.setObjectName("CtlBtn")
        self.btn_forward.setToolTip("Timeshift: Avanzar 10 segundos")
        self.btn_forward.clicked.connect(lambda: self.mpv.seek_relative(10))

        # Selector interactivo de audio desplegable (Català / Español / Radio)
        self.btn_audio_select = QPushButton("🎙 Audio: Auto")
        self.btn_audio_select.setObjectName("AudioDropdownBtn")
        self.btn_audio_select.setToolTip("Pistas de audio disponibles (Català, Español, Radio)")
        self.btn_audio_select.clicked.connect(self._show_audio_menu)

        self.btn_bookmark = QPushButton("★")
        self.btn_bookmark.setObjectName("CtlBtn")
        self.btn_bookmark.setToolTip("Guardar en Favoritos")
        self.btn_bookmark.clicked.connect(self._bookmark_current)

        # Bloque central: Canal activo y guía de programación EPG integrada
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(4, 4, 4, 4)
        info_layout.setSpacing(1)

        self.lbl_channel_title = QLabel("Sin canal seleccionado")
        self.lbl_channel_title.setStyleSheet("color: #E3FF00; font-weight: 800; font-size: 13px;")

        self.lbl_epg = QLabel("")
        self.lbl_epg.setStyleSheet("color: #9FE870; font-size: 11px;")

        info_layout.addWidget(self.lbl_channel_title)
        info_layout.addWidget(self.lbl_epg)
        info_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.btn_mute = QPushButton("🔊")
        self.btn_mute.setObjectName("CtlBtn")
        self.btn_mute.setFixedWidth(36)
        self.btn_mute.setToolTip("Silenciar / Activar sonido [M]")
        self.btn_mute.clicked.connect(self._toggle_mute)

        self.slider_vol = QSlider(Qt.Orientation.Horizontal)
        self.slider_vol.setRange(0, 100)
        self.slider_vol.setValue(100)
        self.slider_vol.setFixedWidth(100)
        self.slider_vol.setToolTip("Volumen [Flechas Arriba/Abajo]")
        self.slider_vol.valueChanged.connect(self._on_volume_changed)

        for w in (self.btn_pp, self.btn_rewind, self.btn_forward, self.btn_audio_select, self.btn_bookmark,
                  info_widget, self.btn_mute, self.slider_vol):
            hl.addWidget(w)

        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._poll_ui)
        self.poll_timer.start(1000)

        self.epg_timer = QTimer(self)
        self.epg_timer.timeout.connect(self._refresh_epg_label)
        self.epg_timer.start(60000)
        return b

    # ── ATAJOS DE TECLADO ─────────────────────────────────────────
    def _setup_shortcuts(self):
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self._toggle_playback)
        QShortcut(QKeySequence(Qt.Key.Key_F), self, self._toggle_fullscreen)
        QShortcut(QKeySequence(Qt.Key.Key_F11), self, self._toggle_fullscreen)
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self._exit_fullscreen)
        QShortcut(QKeySequence(Qt.Key.Key_C), self, self._toggle_channel_panel)
        QShortcut(QKeySequence(Qt.Key.Key_Tab), self, self._toggle_channel_panel)
        QShortcut(QKeySequence(Qt.Key.Key_M), self, self._toggle_mute)
        QShortcut(QKeySequence(Qt.Key.Key_A), self, self.mpv.cycle_audio)
        QShortcut(QKeySequence(Qt.Key.Key_Up), self, lambda: self._step_volume(5))
        QShortcut(QKeySequence(Qt.Key.Key_Down), self, lambda: self._step_volume(-5))
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, self._next_channel)
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, self._prev_channel)
        QShortcut(QKeySequence(Qt.Key.Key_BracketLeft), self, lambda: self.mpv.adjust_audio_delay(-0.1))
        QShortcut(QKeySequence(Qt.Key.Key_BracketRight), self, lambda: self.mpv.adjust_audio_delay(+0.1))
        QShortcut(QKeySequence("Ctrl+0"), self, lambda: self.mpv.set_audio_delay(0.0))
        QShortcut(QKeySequence("Ctrl+U"), self, self._open_direct_media_dialog)
        # Multiview Stadium 4X (F4 conmuta cuadrícula y 1, 2, 3, 4 alternan canal de audio)
        QShortcut(QKeySequence(Qt.Key.Key_F4), self, self.toggle_stadium_mode)
        QShortcut(QKeySequence("1"), self, lambda: self._on_key_quad(0))
        QShortcut(QKeySequence("2"), self, lambda: self._on_key_quad(1))
        QShortcut(QKeySequence("3"), self, lambda: self._on_key_quad(2))
        QShortcut(QKeySequence("4"), self, lambda: self._on_key_quad(3))

    # ── MULTI-AUDIO EN DIRECTO (CATALÀ, ESPAÑOL, RADIOS DEPORTIVAS) ─
    def _show_audio_menu(self):
        """Despliega menú interactivo con todas las pistas de audio detectadas y radios sincronizadas."""
        menu = QMenu(self)
        menu.setStyleSheet("background-color: #0A0A0A; color: #FFFFFF; font-weight: bold; border: 1px solid #E3FF00;")

        if not self.mpv.current_tracks:
            self.mpv._query_audio_tracks()

        if not self.mpv.current_tracks:
            act_cycle = menu.addAction("🎙 Alternar audio siguiente [Tecla A]")
            act_cycle.triggered.connect(self.mpv.cycle_audio)
        else:
            for t in self.mpv.current_tracks:
                prefix = "✓ " if t.get("selected") else "   "
                act = menu.addAction(f"{prefix}{t['title']}")
                act.triggered.connect(lambda checked, t_info=t: (
                    self.mpv.set_audio_option(t_info),
                    self.btn_audio_select.setText(f"🎙 {t_info['title'][:14]}")
                ))
            menu.addSeparator()
            act_drawer = menu.addAction("⚙ Ajustes de audio y búfer en panel lateral...")
            act_drawer.triggered.connect(lambda: self.toggle_settings_drawer(True))

        menu.exec(self.btn_audio_select.mapToGlobal(self.btn_audio_select.rect().bottomLeft()))

    def _on_audio_tracks_detected(self, tracks: list):
        self._refresh_drawer_audio_list(tracks)
        for t in tracks:
            if t.get("selected"):
                self.btn_audio_select.setText(f"🎙 {t['title'][:14]}")
                if hasattr(self, "osd_badge_audio"):
                    self.osd_badge_audio.setText(f"AUDIO: {t['title'][:12]}")
                break

    # ── LÓGICA DE CANALES Y FILTRADO POR PAÍS ─────────────────────
    def _check_autoload(self):
        last = get_app_setting("last_m3u")
        if last and str(last).lower().startswith(("http://", "https://")):
            self.lbl_channel_count.setText("Indexando...")
            self.loader = M3ULoaderThread(str(last))
            self.loader.channels_ready.connect(self._on_channels_loaded)
            self.loader.start()
            return

        default_file = resolve_default_playlist()
        if default_file:
            self.lbl_channel_count.setText("Indexando...")
            self.loader = M3ULoaderThread(str(default_file))
            self.loader.channels_ready.connect(self._on_channels_loaded)
            self.loader.start()

    def _load_source(self, source: str):
        """Carga una lista M3U desde URL o archivo y la recuerda en config."""
        source = (source or "").strip()
        if not source:
            return
        if not source.lower().startswith(("http://", "https://")):
            source = os.path.expanduser(source)
        set_app_setting("last_m3u", source)
        self.lbl_channel_count.setText("Indexando...")
        self.loader = M3ULoaderThread(source)
        self.loader.channels_ready.connect(self._on_channels_loaded)
        self.loader.start()

    def _prompt_add_source(self):
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(
            self, "Añadir lista M3U",
            "Pega una URL M3U/M3U8 o una ruta de archivo local:\n"
            "Ej.: https://iptv-org.github.io/iptv/countries/es.m3u"
        )
        if ok and text.strip():
            self._load_source(text.strip())

    def _load_iptv_org(self, url: str):
        self._load_source(url)

    def _show_source_menu(self):
        menu = QMenu(self)
        act_custom = menu.addAction("🔗  URL o archivo M3U/M3U8…")
        act_custom.triggered.connect(self._prompt_add_source)
        menu.addSeparator()
        for label, url in IPTV_ORG_SOURCES.items():
            act = menu.addAction(f"📡  iptv-org · {label}")
            act.triggered.connect(lambda _checked=False, u=url: self._load_iptv_org(u))
        menu.addSeparator()
        act_xt = menu.addAction("🛰  Conectar panel Xtream Codes…")
        act_xt.triggered.connect(self._prompt_xtream)
        menu.addSeparator()
        if hasattr(self, "btn_menu_tab") and self.btn_menu_tab.isVisible():
            pos = self.btn_menu_tab.mapToGlobal(self.btn_menu_tab.rect().bottomLeft())
        elif hasattr(self, "btn_add_source") and self.btn_add_source.isVisible():
            pos = self.btn_add_source.mapToGlobal(self.btn_add_source.rect().bottomLeft())
        else:
            pos = QCursor.pos()
        menu.exec(pos)

    # ── EPG: GUÍA DE PROGRAMACIÓN ─────────────────────────────────
    def _load_epg(self, urls: list):
        if not EPG_AVAILABLE or self.epg is None:
            QMessageBox.information(self, "EPG", "Módulo EPG no disponible.")
            return
        urls = [u for u in (urls or []) if u]
        if not urls:
            return
        try:
            self.lbl_epg.setText("📺 EPG: descargando guía…")
        except Exception:
            pass
        self.epg_thread = EpgLoaderThread(self.epg, urls)
        self.epg_thread.epg_ready.connect(self._on_epg_ready)
        self.epg_thread.start()
        set_app_setting("epg_urls", urls)

    def _on_epg_ready(self, n: int):
        if n:
            self.lbl_epg.setText(f"📺 EPG: {n} programas cargados")
        else:
            self.lbl_epg.setText("📺 EPG: no se pudo descargar la guía")
        self._update_epg_for_channel()

    def _show_epg_menu(self):
        btn = self.sender()
        menu = QMenu(self)
        act_custom = menu.addAction("🔗  URL XMLTV personalizada…")
        act_custom.triggered.connect(self._prompt_epg_custom)
        menu.addSeparator()
        for label, url in EPG_PRESETS.items():
            act = menu.addAction(f"📺  EPG · {label}")
            act.triggered.connect(lambda _c=False, u=url: self._load_epg([u]))
        if hasattr(btn, "mapToGlobal"):
            menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))

    def _prompt_epg_custom(self):
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(
            self, "EPG personalizado",
            "URL de la guía XMLTV (.xml o .xml.gz):\n"
            "Ej.: https://epgshare01.online/epgshare01/epg_ripper_ES1.xml.gz"
        )
        if ok and text.strip():
            self._load_epg([text.strip()])

    def _update_epg_for_channel(self):
        if self.epg is None or not self.epg.has_data() or not self.current_channel:
            return
        ch = self.current_channel
        cur, nxt = self.epg.now_next(ch.get("epg_id", "") or "", ch.get("name", ""))

        def fmt(p):
            try:
                st = p["start"].astimezone().strftime("%H:%M")
                sp = (p["stop"] or p["start"]).astimezone().strftime("%H:%M")
                return f"{st}–{sp} {p.get('title', '')}"
            except Exception:
                return p.get("title", "")

        parts = []
        if cur:
            parts.append(f"📺 Ahora: {fmt(cur)}")
        if nxt:
            parts.append(f"▶ Siguiente: {fmt(nxt)}")
        self.lbl_epg.setText(("   ·   ".join(parts) or "📺 EPG: sin programación para este canal")[:320])

    def _refresh_epg_label(self):
        if self.epg is not None and self.epg.has_data():
            self._update_epg_for_channel()

    # ── XTREAM CODES ──────────────────────────────────────────────
    def _prompt_xtream(self):
        if not XTREAM_AVAILABLE:
            QMessageBox.information(self, "Xtream", "Módulo Xtream no disponible (falta xtream_parser.py).")
            return
        saved = get_app_setting("xtream", {}) or {}
        dlg = QDialog(self)
        dlg.setWindowTitle("🛰 Conectar panel Xtream Codes")
        form = QFormLayout(dlg)
        host = QLineEdit(saved.get("host", ""))
        host.setPlaceholderText("http://servidor:8080")
        user = QLineEdit(saved.get("user", ""))
        pwd = QLineEdit(saved.get("pass", ""))
        pwd.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Host (URL):", host)
        form.addRow("Usuario:", user)
        form.addRow("Contraseña:", pwd)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(dlg.accept)
        bb.rejected.connect(dlg.reject)
        form.addRow(bb)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            h, u, p = host.text().strip(), user.text().strip(), pwd.text().strip()
            if not (h and u and p):
                QMessageBox.warning(self, "Xtream", "Completa host, usuario y contraseña.")
                return
            set_app_setting("xtream", {"host": h, "user": u, "pass": p})
            self._load_xtream(h, u, p)

    def _load_xtream(self, host, user, pwd):
        self.lbl_channel_count.setText("🛰 Conectando a Xtream…")
        self.xtream_thread = XtreamLoaderThread(host, user, pwd)
        self.xtream_thread.m3u_ready.connect(self._on_xtream_m3u)
        self.xtream_thread.error.connect(self._on_xtream_error)
        self.xtream_thread.start()

    def _on_xtream_m3u(self, txt: str):
        self.lbl_channel_count.setText("Indexando Xtream…")
        self.loader = M3ULoaderThread(content=txt)
        self.loader.channels_ready.connect(self._on_channels_loaded)
        self.loader.start()

    def _on_xtream_error(self, msg: str):
        self.lbl_channel_count.setText("0 canales")
        QMessageBox.warning(self, "Xtream", f"No se pudo cargar el panel Xtream:\n{msg}")

    # ── METADATOS IA (DEEPSEEK) ───────────────────────────────────
    def _ai_client(self):
        if not AI_AVAILABLE:
            return None
        cfg = get_app_setting("deepseek", {}) or {}
        return DeepSeekClient(cfg.get("api_key", ""), cfg.get("model", "deepseek-flash"))

    def _ai_status_text(self) -> str:
        if not AI_AVAILABLE:
            return "IA: módulo no disponible ❌"
        try:
            has = DeepSeekClient(self.ai_key.text().strip()).available()
        except Exception:
            has = False
        return "IA: clave lista ✅" if has else "IA: añade tu clave de DeepSeek ⚠️"

    def _refresh_ai_status(self):
        if hasattr(self, "lbl_ai_status"):
            self.lbl_ai_status.setText(self._ai_status_text())

    def _harden_config_perms(self):
        """Restringe los permisos del archivo de config (contiene la clave)."""
        try:
            os.chmod(STATE_CONFIG_PATH, 0o600)
        except Exception:
            pass

    def _enrich_current_ai(self):
        client = self._ai_client()
        if client is None:
            QMessageBox.information(self, "IA", "Módulo IA no disponible.")
            return
        if not client.available():
            QMessageBox.information(self, "IA", "Configura tu API key de DeepSeek en «Ajustes Pro».")
            return
        ch = self.current_channel
        if not ch:
            QMessageBox.information(self, "IA", "Selecciona un canal o película primero.")
            return
        title = ch.get("name", "")
        kind = "película" if "VOD" in (ch.get("group", "") or "").upper() else "canal de televisión"
        self.lbl_channel_title.setText(f"✨ Analizando «{title}» con IA…")
        self.ai_thread = DeepSeekThread(client, title, kind)
        self.ai_thread.meta_ready.connect(self._on_ai_meta)
        self.ai_thread.error.connect(self._on_ai_error)
        self.ai_thread.start()

    def _on_ai_meta(self, meta: dict):
        if not meta:
            QMessageBox.information(self, "IA DeepSeek", "Sin resultados.")
            return
        rows = []
        if meta.get("titulo"): rows.append(f"<b>{meta['titulo']}</b>")
        if meta.get("anio"): rows.append(f"<b>Año:</b> {meta['anio']}")
        if meta.get("genero"): rows.append(f"<b>Género:</b> {meta['genero']}")
        if meta.get("sinopsis"): rows.append(f"<br>{meta['sinopsis']}")
        QMessageBox.information(self, "✨ IA DeepSeek", "<br>".join(rows) or "(vacío)")

    def _on_ai_error(self, msg: str):
        QMessageBox.warning(self, "IA DeepSeek", f"Error: {msg}")

    def _save_ai_config(self):
        key = self.ai_key.text().strip()
        set_app_setting("deepseek", {
            "api_key": key,
            "model": self.ai_model.currentText().strip() or "deepseek-flash",
        })
        self._harden_config_perms()
        if key:
            self.lbl_ai_status.setText("IA: configuración guardada ✅")
        else:
            self._refresh_ai_status()

    def _test_ai(self):
        if not AI_AVAILABLE:
            QMessageBox.information(self, "IA", "Módulo IA no disponible.")
            return
        client = DeepSeekClient(self.ai_key.text().strip(), self.ai_model.currentText())
        if not client.available():
            QMessageBox.warning(self, "IA",
                "Introduce una API key de DeepSeek (o define $DEEPSEEK_API_KEY / config/deepseek.env).")
            return
        self.lbl_ai_status.setText("IA: probando conexión…")
        self.ai_thread = DeepSeekThread(client, mode="ping")
        self.ai_thread.ping_ok.connect(lambda t: self.lbl_ai_status.setText("IA: conexión OK ✅"))
        self.ai_thread.error.connect(lambda e: self.lbl_ai_status.setText(f"IA: error → {e}"))
        self.ai_thread.start()

    def _on_channels_loaded(self, channels: list, countries_map: dict, raw: str):
        self.all_channels = channels
        self.countries_map = countries_map
        HUB.raw_playlist = raw

        # Indexar grupos exactos en el orden original de serie en el M3U
        self.groups_order = []
        self.groups_map = {}
        for ch in channels:
            g = ch.get("group") or "Otros"
            if g not in self.groups_map:
                self.groups_map[g] = []
                self.groups_order.append(g)
            self.groups_map[g].append(ch)

        # Actualizar selector de grupos
        if hasattr(self, "group_combo"):
            self.group_combo.blockSignals(True)
            self.group_combo.clear()
            self.group_combo.addItem("⭐ DE SERIE: Toda la lista (Orden IPTV)", "ALL")
            for g in self.groups_order:
                count_g = len(self.groups_map[g])
                self.group_combo.addItem(f"{g}  ({count_g})", g)
            self.group_combo.blockSignals(False)

        # Actualizar submenú dinámico de grupos en la barra de menús
        if hasattr(self, "menu_grupos_dinamicos"):
            self.menu_grupos_dinamicos.clear()
            act_all = self.menu_grupos_dinamicos.addAction("⭐ De serie: Toda la lista")
            act_all.triggered.connect(lambda: self._select_group_by_name("ALL"))
            self.menu_grupos_dinamicos.addSeparator()
            for g in self.groups_order[:30]:
                count_g = len(self.groups_map[g])
                act_g = self.menu_grupos_dinamicos.addAction(f"{g}  ({count_g})")
                act_g.triggered.connect(lambda _c=False, grp=g: self._select_group_by_name(grp))

        self._apply_current_filter()

        # Auto-carga de la EPG guardada (una sola vez por sesión)
        if not self._epg_autoloaded and self.epg is not None:
            urls = get_app_setting("epg_urls", []) or []
            if urls:
                self._epg_autoloaded = True
                self._load_epg(urls)

    def _select_group_by_name(self, group_name: str):
        if hasattr(self, "group_combo"):
            idx = self.group_combo.findData(group_name)
            if idx >= 0:
                self.group_combo.setCurrentIndex(idx)
        self.selected_group = group_name
        self._apply_current_filter()

    def _on_group_changed(self, idx: int):
        self.selected_group = self.group_combo.currentData() or "ALL"
        self._apply_current_filter()

    def _on_order_combo_changed(self, idx: int):
        mode = self.order_combo.currentData()
        if mode:
            self._set_order_mode(mode)

    def _on_country_changed(self, country: str):
        self.selected_country = country
        self._apply_current_filter()

    def _on_subcategory_chip_clicked(self, chip_id: int):
        subcategories = ["Todos", "⚽ Fútbol & Deportes", "🎬 Cine & Series", "📰 TDT & General", "★ Favoritos"]
        self.selected_subcategory = subcategories[chip_id]
        self._apply_current_filter()

    def _apply_current_filter(self):
        # 1. Base según grupo IPTV seleccionado
        if not hasattr(self, "selected_group") or self.selected_group == "ALL":
            base = self.all_channels
        else:
            base = self.groups_map.get(self.selected_group, [])

        # 2. Filtrar por subcategoría / chip rápido
        sub = self.selected_subcategory
        if sub == "Todos":
            matching = base
        elif sub == "★ Favoritos":
            matching = [c for c in base if c in self.bookmarked_channels]
        elif "Fútbol" in sub or "Deportes" in sub:
            matching = [
                c for c in base
                if any(k in (c["name"] + c.get("group", "")).upper() for k in ["FUTBOL", "DEPORTES", "DAZN", "LALIGA", "CHAMPIONS", "MOTOGP", "F1", "SPORT", "EPL"])
            ]
        elif "Cine" in sub or "Series" in sub:
            matching = [
                c for c in base
                if any(k in (c["name"] + c.get("group", "")).upper() for k in ["CINE", "PELICULAS", "SERIES", "ESTRENOS", "MOVIES", "HBO", "NETFLIX", "CINEMA", "VOD"])
            ]
        elif "TDT" in sub or "General" in sub:
            matching = [
                c for c in base
                if any(k in (c["name"] + c.get("group", "")).upper() for k in ["TDT", "NOTICIAS", "NEWS", "INFO", "GENERAL", "24H"])
            ]
        else:
            matching = base

        self.lbl_channel_count.setText(f"{len(matching)} canales")
        self._populate_list(matching, offset=0)

    def _populate_list(self, channels: list, offset: int = 0):
        self.channel_list.setUpdatesEnabled(False)
        if offset == 0:
            self.channel_list.clear()

        # Respetar el modo de ordenación
        if self.order_mode == "alpha":
            ordered = sorted(channels, key=lambda c: (c.get("name") or "").upper())
        elif self.order_mode == "slocast":
            try:
                ordered = sorted(channels, key=_slocast_sort_key)
            except Exception:
                ordered = list(channels)
        else:
            # "original" (De serie): respeta el orden exacto del proveedor IPTV
            ordered = list(channels)

        limit = self.channel_limit_per_page
        chunk = ordered[offset : offset + limit]
        current_cat = None

        show_headers = bool(get_app_setting("show_group_headers", True))
        for ch in chunk:
            cat = ch.get("group") or "Otros"
            if show_headers and cat != current_cat and self.order_mode == "original":
                header = QListWidgetItem(f"── {cat} ──")
                header.setForeground(QColor("#E3FF00"))
                f = header.font()
                f.setBold(True)
                header.setFont(f)
                header.setFlags(Qt.ItemFlag.NoItemFlags)
                self.channel_list.addItem(header)
                current_cat = cat

            name = (ch.get("name") or "Canal").strip()
            item = QListWidgetItem(name)
            item.setToolTip(f"{name}\n📁 {cat}")
            item.setData(Qt.ItemDataRole.UserRole, ch)
            self.channel_list.addItem(item)

        remaining = len(ordered) - (offset + len(chunk))
        if remaining > 0:
            load_qty = min(limit, remaining)
            more_item = QListWidgetItem(f"⬇️ Cargar siguientes {load_qty} canales... [{offset + len(chunk)}/{len(ordered)}]")
            more_item.setForeground(QColor("#E3FF00"))
            f = more_item.font()
            f.setBold(True)
            more_item.setFont(f)
            more_item.setData(Qt.ItemDataRole.UserRole, {
                "_action": "load_more",
                "channels": channels,
                "offset": offset + len(chunk)
            })
            self.channel_list.addItem(more_item)

        self.channel_list.setUpdatesEnabled(True)

    def _execute_search(self):
        q = self.search_input.text().strip().lower()
        if not q:
            self._apply_current_filter()
            return
        matches = [c for c in self.all_channels if q in c["name"].lower() or q in c.get("group", "").lower()]
        self.lbl_channel_count.setText(f"{len(matches)} / {len(self.all_channels)}")
        self._populate_list(matches, offset=0)

    def _on_channel_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(data, dict):
            if data.get("_action") == "load_more":
                row = self.channel_list.row(item)
                self.channel_list.takeItem(row)
                self._populate_list(data["channels"], offset=data["offset"])
            else:
                self._tune(data)

    def _on_channel_double_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(data, dict):
            if data.get("_action") == "load_more":
                # Eliminar el botón "Cargar más" y añadir la siguiente página
                row = self.channel_list.row(item)
                self.channel_list.takeItem(row)
                self._populate_list(data["channels"], offset=data["offset"])
            else:
                self._tune(data)

    def _tune(self, ch: dict):
        self.current_channel = ch
        name = ch.get("name", "Canal")
        url = ch.get("url", "")
        if not url:
            return

        self.stack.setCurrentIndex(0)
        HUB.set_channel(url, name)

        # Si el modo Stadium 4X está activo, sintonizar en el cuadrante seleccionado
        if getattr(self, "stadium_mode", False) and hasattr(self, "stadium_widget") and self.stadium_widget is not None:
            act_idx = self.stadium_widget.active_quadrant
            self.stadium_widget.play_channel_in_quadrant(act_idx, ch)
            if hasattr(self, "osd_channel_label"):
                self.osd_channel_label.setText(f"🏟️ Señal [{act_idx+1}]: {name}")
            return

        # Restablecer estado de audio (desmutear y volumen óptimo garantizado)
        self.mpv._muted = False
        if hasattr(self, "btn_mute"):
            self.btn_mute.setText("🔊")
            self.btn_mute.setStyleSheet("")

        # Reproducción directa ultra-rápida y fiable con MPV/VLC (evita demuxing erróneo en relay)
        pb_mode = get_app_setting("playback_mode", "direct")
        if pb_mode == "relay":
            self.mpv.play(self.relay.loopback_url)
        else:
            self.mpv.play(url)

        self.lbl_channel_title.setText(f"📺 {name}")
        self.btn_audio_select.setText("🎙 Audio: Auto")
        if hasattr(self, "osd_channel_label"):
            self.osd_channel_label.setText(f"{name}")
        if hasattr(self, "osd_badge_buffer"):
            self.osd_badge_buffer.setText(f"ANTI-CORTES {self.mpv._buffer_secs}s")
        self._update_epg_for_channel()

        if ch not in self.recent_channels:
            self.recent_channels.insert(0, ch)
            self.recents_list.clear()
            for r in self.recent_channels[:50]:
                it = QListWidgetItem(f"🕒 {r['name']}")
                it.setData(Qt.ItemDataRole.UserRole, r)
                self.recents_list.addItem(it)

        if self.cast_ctl.is_connected:
            self.cast_ctl.connect_and_play(self.relay.stream_url, name)

    def _next_channel(self):
        row = self.channel_list.currentRow()
        if row + 1 < self.channel_list.count():
            item = self.channel_list.item(row + 1)
            self.channel_list.setCurrentRow(row + 1)
            self._on_channel_double_clicked(item)

    def _prev_channel(self):
        row = self.channel_list.currentRow()
        if row - 1 >= 0:
            item = self.channel_list.item(row - 1)
            self.channel_list.setCurrentRow(row - 1)
            self._on_channel_double_clicked(item)

    # ── BARRA DE MENÚS NATIVA Y AJUSTES INTEGRADOS ────────────────
    def _build_menu_bar(self):
        mb = self.menuBar()
        mb.setObjectName("AppMenuBar")

        # 1. Menú Lista IPTV
        menu_lista = mb.addMenu("📁 Lista IPTV")

        act_serie = menu_lista.addAction("⚡ Cargar lista de serie (TV-76173252)")
        act_serie.triggered.connect(self._load_serie_playlist)

        act_open_file = menu_lista.addAction("📂 Abrir archivo local M3U / M3U8… (Ctrl+O)")
        act_open_file.setShortcut(QKeySequence("Ctrl+O"))
        act_open_file.triggered.connect(self._open_local_file_dialog)

        act_open_url = menu_lista.addAction("🌐 Cargar desde URL web… (Ctrl+U)")
        act_open_url.setShortcut(QKeySequence("Ctrl+U"))
        act_open_url.triggered.connect(self._prompt_add_source)

        act_xtream = menu_lista.addAction("🛰 Servidor Xtream Codes… (Ctrl+X)")
        act_xtream.setShortcut(QKeySequence("Ctrl+X"))
        act_xtream.triggered.connect(self._prompt_xtream)

        act_reload = menu_lista.addAction("🔄 Recargar lista actual (F5)")
        act_reload.setShortcut(QKeySequence("F5"))
        act_reload.triggered.connect(self._check_autoload)

        menu_lista.addSeparator()
        act_export = menu_lista.addAction("💾 Exportar lista actual a archivo…")
        act_export.triggered.connect(self._export_playlist_dialog)

        act_tivimate = menu_lista.addAction("📡 SLONE TV Connect™ (Sincronizar con Smart TV)…")
        act_tivimate.triggered.connect(self._show_tv_connect_dialog)

        menu_lista.addSeparator()
        act_quit = menu_lista.addAction("❌ Salir de SLOCAST (Ctrl+Q)")
        act_quit.setShortcut(QKeySequence("Ctrl+Q"))
        act_quit.triggered.connect(self.close)

        # 2. Menú Canales y Grupos
        menu_canales = mb.addMenu("📺 Canales y Grupos")

        self.menu_grupos_dinamicos = menu_canales.addMenu("📑 Grupos IPTV (De serie)")
        act_def_grp = self.menu_grupos_dinamicos.addAction("⭐ De serie: Toda la lista")
        act_def_grp.triggered.connect(lambda: self._select_group_by_name("ALL"))

        menu_orden = menu_canales.addMenu("🔀 Modo de visualización / Orden")
        self.act_order_serie = menu_orden.addAction("⭐ De serie (Original IPTV - Sin alterar)")
        self.act_order_serie.setCheckable(True)
        self.act_order_serie.setChecked(self.order_mode == "original")
        self.act_order_serie.triggered.connect(lambda: self._set_order_mode("original"))

        self.act_order_alpha = menu_orden.addAction("🔤 Alfabético (A → Z)")
        self.act_order_alpha.setCheckable(True)
        self.act_order_alpha.setChecked(self.order_mode == "alpha")
        self.act_order_alpha.triggered.connect(lambda: self._set_order_mode("alpha"))

        self.act_order_slocast = menu_orden.addAction("🧠 SLOCAST Inteligente")
        self.act_order_slocast.setCheckable(True)
        self.act_order_slocast.setChecked(self.order_mode == "slocast")
        self.act_order_slocast.triggered.connect(lambda: self._set_order_mode("slocast"))

        menu_canales.addSeparator()
        act_search = menu_canales.addAction("🔍 Buscar canal… (Ctrl+F)")
        act_search.setShortcut(QKeySequence("Ctrl+F"))
        act_search.triggered.connect(lambda: (self.stack.setCurrentIndex(0), self.search_input.setFocus(), self.search_input.selectAll()))

        act_favs = menu_canales.addAction("★ Ver Canales Favoritos (Ctrl+D)")
        act_favs.setShortcut(QKeySequence("Ctrl+D"))
        act_favs.triggered.connect(lambda: self.stack.setCurrentIndex(1))

        act_recents = menu_canales.addAction("🕒 Ver Canales Recientes (Ctrl+H)")
        act_recents.setShortcut(QKeySequence("Ctrl+H"))
        act_recents.triggered.connect(lambda: self.stack.setCurrentIndex(2))

        act_clear_rec = menu_canales.addAction("🧹 Limpiar historial de recientes")
        act_clear_rec.triggered.connect(self._clear_recent_channels)

        # 3. Menú Motor y Reproductor
        menu_motor = mb.addMenu("⚡ Motor y Reproductor")

        menu_sel_motor = menu_motor.addMenu("🎬 Motor de reproducción")
        self.act_motor_mpv = menu_sel_motor.addAction("MPV Player (IPC nativo · Recomendado)")
        self.act_motor_mpv.setCheckable(True)
        cur_eng = str(get_app_setting("engine", "mpv") or "mpv").lower()
        self.act_motor_mpv.setChecked(cur_eng == "mpv")
        self.act_motor_mpv.triggered.connect(lambda: self._set_engine("mpv"))

        self.act_motor_vlc = menu_sel_motor.addAction("VLC Player (libvlc)" if VLC_AVAILABLE else "VLC Player (no disponible)")
        self.act_motor_vlc.setCheckable(True)
        self.act_motor_vlc.setChecked(cur_eng == "vlc")
        self.act_motor_vlc.setEnabled(VLC_AVAILABLE)
        self.act_motor_vlc.triggered.connect(lambda: self._set_engine("vlc"))

        menu_gpu = menu_motor.addMenu("🚀 Aceleración por Hardware (Intel GPU)")
        act_gpu_auto = menu_gpu.addAction("Automática segura (vaapi/auto-safe)")
        act_gpu_auto.triggered.connect(lambda: (set_app_setting("hwdec", "auto-safe"), QMessageBox.information(self, "Aceleración GPU", "Aceleración automática segura seleccionada.")))
        act_gpu_vaapi = menu_gpu.addAction("Forzar VAAPI (Intel i7-8665U UHD 620)")
        act_gpu_vaapi.triggered.connect(lambda: (set_app_setting("hwdec", "vaapi"), QMessageBox.information(self, "Aceleración GPU", "VAAPI forzado para gráficos integrados Intel.")))
        act_gpu_off = menu_gpu.addAction("Desactivada (Software)")
        act_gpu_off.triggered.connect(lambda: (set_app_setting("hwdec", "no"), QMessageBox.information(self, "Aceleración GPU", "Aceleración por hardware desactivada.")))

        menu_buf = menu_motor.addMenu("⏱ Búfer de streaming (Caché)")
        act_b05 = menu_buf.addAction("0.5 s (Ultra-bajo · Directo satélite)")
        act_b05.triggered.connect(lambda: self._set_buffer_secs(0.5))
        act_b15 = menu_buf.addAction("1.5 s (Estándar · Recomendado)")
        act_b15.triggered.connect(lambda: self._set_buffer_secs(1.5))
        act_b40 = menu_buf.addAction("4.0 s (Alto · Anti-cortes)")
        act_b40.triggered.connect(lambda: self._set_buffer_secs(4.0))

        menu_motor.addSeparator()
        act_fs = menu_motor.addAction("⛶ Pantalla completa (F11 / F)")
        act_fs.setShortcut(QKeySequence("F11"))
        act_fs.triggered.connect(self._toggle_fullscreen)

        act_playpause = menu_motor.addAction("⏯ Reproducir / Pausar (Espacio)")
        act_playpause.triggered.connect(self._toggle_playback)

        act_next_ch = menu_motor.addAction("⏭ Siguiente canal (N)")
        act_next_ch.triggered.connect(self._next_channel)

        act_prev_ch = menu_motor.addAction("⏮ Canal anterior (P)")
        act_prev_ch.triggered.connect(self._prev_channel)

        act_stop = menu_motor.addAction("🛑 Detener reproducción (S)")
        act_stop.triggered.connect(self.mpv.stop)

        # 4. Menú Audio y Pistas
        menu_audio = mb.addMenu("🎙 Audio y Pistas")
        act_cycle_audio = menu_audio.addAction("🔄 Conmutar siguiente pista de audio (A / Ctrl+A)")
        act_cycle_audio.setShortcut(QKeySequence("Ctrl+A"))
        act_cycle_audio.triggered.connect(self.mpv.cycle_audio)

        menu_audio.addSeparator()
        act_vol_up = menu_audio.addAction("🔊 Subir volumen (+)")
        act_vol_up.triggered.connect(lambda: self.slider_vol.setValue(min(100, self.slider_vol.value() + 5)))
        act_vol_down = menu_audio.addAction("🔉 Bajar volumen (-)")
        act_vol_down.triggered.connect(lambda: self.slider_vol.setValue(max(0, self.slider_vol.value() - 5)))
        act_mute = menu_audio.addAction("🔇 Silenciar / Desactivar silencio (M)")
        act_mute.triggered.connect(self._toggle_mute)

        # 5. Menú Ajustes y Preferencias
        menu_ajustes = mb.addMenu("⚙ Ajustes y Preferencias")
        act_pref = menu_ajustes.addAction("🛠 Preferencias completas… (Ctrl+,)")
        act_pref.setShortcut(QKeySequence("Ctrl+,"))
        act_pref.triggered.connect(self._open_preferences_dialog)

        menu_ajustes.addSeparator()
        act_remote = menu_ajustes.addAction("📱 Mando a distancia web (Móvil)…")
        act_remote.triggered.connect(lambda: self.stack.setCurrentIndex(3))

        act_cast = menu_ajustes.addAction("📺 Proyectar en Xiaomi TV…")
        act_cast.triggered.connect(self._cast_to_xiaomi_tv)

        act_perf = menu_ajustes.addAction("💻 Panel de rendimiento ThinkPad X390…")
        act_perf.triggered.connect(self._show_performance_dialog)

        # 6. Menú Ayuda
        menu_ayuda = mb.addMenu("ℹ️ Ayuda")
        act_diag = menu_ayuda.addAction("🩺 Diagnóstico del stream actual…")
        act_diag.triggered.connect(self._diagnose_current_stream)

        act_shortcuts = menu_ayuda.addAction("⌨ Atajos de teclado…")
        act_shortcuts.triggered.connect(self._show_shortcuts_dialog)

        menu_ayuda.addSeparator()
        act_about = menu_ayuda.addAction("👑 Acerca de SLOCAST 1.0 (SLONE OS)")
        act_about.triggered.connect(self._show_about_dialog)

    # ── MÉTODOS DE SOPORTE PARA MENÚS Y PREFERENCIAS ─────────────
    def _load_serie_playlist(self):
        if DEFAULT_SERIE_M3U.exists():
            self._load_source(str(DEFAULT_SERIE_M3U))
            QMessageBox.information(self, "Lista de serie", f"Cargando lista IPTV de serie:\n{DEFAULT_SERIE_M3U}")
        else:
            QMessageBox.warning(self, "Lista de serie no encontrada", f"No se encontró el archivo en:\n{DEFAULT_SERIE_M3U}")

    def _open_local_file_dialog(self):
        fn, _ = QFileDialog.getOpenFileName(
            self, "Abrir lista M3U", str(Path.home() / "Descargas"),
            "Playlists M3U (*.m3u *.m3u8);;Todos los archivos (*)"
        )
        if fn:
            self._load_source(fn)

    def _export_playlist_dialog(self):
        if not self.all_channels:
            QMessageBox.warning(self, "Exportar", "No hay canales cargados para exportar.")
            return
        fn, _ = QFileDialog.getSaveFileName(
            self, "Exportar lista actual", str(Path.home() / "Descargas" / "slocast_export.m3u"),
            "Lista M3U (*.m3u)"
        )
        if fn:
            try:
                lines = ["#EXTM3U\n"]
                for c in self.all_channels:
                    lines.append(f'#EXTINF:-1 group-title="{c.get("group","")}",{c.get("name","Canal")}\n{c.get("url","")}\n')
                Path(fn).write_text("".join(lines), encoding="utf-8")
                QMessageBox.information(self, "Exportado", f"Lista guardada correctamente ({len(self.all_channels)} canales) en:\n{fn}")
            except Exception as e:
                QMessageBox.warning(self, "Error al exportar", str(e))

    def _set_order_mode(self, mode: str):
        self.order_mode = mode
        set_app_setting("order_mode", mode)
        if hasattr(self, "order_combo"):
            i = self.order_combo.findData(mode)
            if i >= 0:
                self.order_combo.blockSignals(True)
                self.order_combo.setCurrentIndex(i)
                self.order_combo.blockSignals(False)
        if hasattr(self, "act_order_serie"):
            self.act_order_serie.setChecked(mode == "original")
            self.act_order_alpha.setChecked(mode == "alpha")
            self.act_order_slocast.setChecked(mode == "slocast")
        self._apply_current_filter()

    def _set_engine(self, eng: str):
        if eng == "vlc" and not VLC_AVAILABLE:
            QMessageBox.warning(self, "VLC", "python-vlc no está instalado en el sistema.")
            return
        set_app_setting("engine", eng)
        if hasattr(self, "act_motor_mpv"):
            self.act_motor_mpv.setChecked(eng == "mpv")
            self.act_motor_vlc.setChecked(eng == "vlc")
        self.lbl_channel_title.setText(f"Motor activo: {eng.upper()}")

    def _set_buffer_secs(self, secs: float):
        set_app_setting("cache_secs", secs)
        QMessageBox.information(self, "Búfer actualizado", f"Búfer de streaming fijado a {secs} segundos.")

    def _clear_recent_channels(self):
        self.recent_channels.clear()
        self.recents_list.clear()
        QMessageBox.information(self, "Historial", "Historial de canales recientes limpiado.")

    def toggle_settings_drawer(self, show: bool | None = None):
        """Despliega u oculta el panel lateral de ajustes integrado SLONE PRO."""
        if not hasattr(self, "settings_drawer"):
            return
        if show is None:
            show = self.settings_drawer.isHidden()
        if show:
            self.settings_drawer.show()
            if hasattr(self, "nav_group") and self.nav_group.button(6):
                self.nav_group.button(6).setChecked(True)
            if hasattr(self, "drawer_txt_m3u"):
                cur_m3u = get_app_setting("last_m3u", str(DEFAULT_SERIE_M3U))
                self.drawer_txt_m3u.setText(str(cur_m3u))
            if hasattr(self, "mpv"):
                self._refresh_drawer_audio_list(self.mpv.current_tracks)
        else:
            self.settings_drawer.hide()
            if hasattr(self, "nav_group") and self.nav_group.button(self.stack.currentIndex()):
                self.nav_group.button(self.stack.currentIndex()).setChecked(True)

    def _open_preferences_dialog(self):
        """Abre las preferencias en el panel lateral integrado dentro de la misma ventana (sin popups ni pestañas externas)."""
        self.toggle_settings_drawer(True)

    def _on_nav_clicked(self, page_idx: int):
        """Maneja la navegación principal unificada superior."""
        if page_idx == 6:
            self.toggle_settings_drawer()
        else:
            if hasattr(self, "settings_drawer") and not self.settings_drawer.isHidden():
                self.settings_drawer.hide()
            self.stack.setCurrentIndex(page_idx)

    def _build_slone_banner(self) -> QWidget:
        """Pestaña minimalista sobre el reproductor con el logo SLONE para abrir ajustes."""
        bar = QWidget()
        bar.setObjectName("PlayerMiniBar")
        bar.setFixedHeight(28)
        hl = QHBoxLayout(bar)
        hl.setContentsMargins(6, 2, 6, 2)
        hl.setSpacing(6)

        # Nombre sutil del canal actual
        self.osd_channel_label = QLabel("👑 SLONE — Selecciona un canal")
        self.osd_channel_label.setStyleSheet("color: #888888; font-weight: 700; font-size: 11px;")
        hl.addWidget(self.osd_channel_label, 1)

        # Elementos de compatibilidad en memoria
        self.osd_badge_res = QLabel()
        self.osd_badge_audio = QLabel()
        self.osd_badge_buffer = QLabel()
        self.btn_banner_toggle_list = QPushButton()
        self.btn_banner_fs = QPushButton()

        # Botón directo para conmutar Multiview Stadium 4X
        self.btn_banner_stadium = QPushButton("🏟️ STADIUM 4X")
        self.btn_banner_stadium.setObjectName("PlayerSettingsTab")
        self.btn_banner_stadium.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_banner_stadium.setToolTip("Conmutar modo Multiview Stadium 4X [F4]")
        self.btn_banner_stadium.clicked.connect(self.toggle_stadium_mode)
        hl.addWidget(self.btn_banner_stadium)

        # Pequeña pestaña con el símbolo de SLONE o logo para abrir los ajustes
        self.btn_player_settings = QPushButton("👑  AJUSTES")
        self.btn_player_settings.setObjectName("PlayerSettingsTab")
        self.btn_player_settings.setToolTip("Abrir ajustes de reproducción, pistas y emisión [O]")
        self.btn_player_settings.clicked.connect(lambda: self.toggle_settings_drawer())
        hl.addWidget(self.btn_player_settings)

        return bar

    def _build_tivimate_banner(self) -> QWidget:
        """Alias compatibilidad."""
        return self._build_slone_banner()

    def _build_settings_drawer(self) -> QWidget:
        """Panel lateral derecho de ajustes integrado SLONE PRO."""
        drawer = QWidget()
        drawer.setObjectName("SettingsDrawer")
        vl = QVBoxLayout(drawer)
        vl.setContentsMargins(14, 14, 14, 14)
        vl.setSpacing(10)

        # Cabecera del drawer
        head = QWidget()
        head.setObjectName("DrawerHeader")
        hl_head = QHBoxLayout(head)
        hl_head.setContentsMargins(0, 0, 0, 8)
        title = QLabel("⚙  AJUSTES SLONE PRO")
        title.setObjectName("DrawerTitle")
        hl_head.addWidget(title)
        hl_head.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setObjectName("DrawerCloseBtn")
        btn_close.setToolTip("Cerrar panel de ajustes")
        btn_close.clicked.connect(drawer.hide)
        hl_head.addWidget(btn_close)
        vl.addWidget(head)

        tabs = QTabWidget()
        tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #1D212A; }")

        # ── SECCIÓN 1: LISTA IPTV ──
        tab_m3u = QWidget()
        l_m3u = QVBoxLayout(tab_m3u)
        l_m3u.setSpacing(8)

        lbl_s1 = QLabel("LISTA IPTV ACTIVA")
        lbl_s1.setObjectName("DrawerSectionTitle")
        l_m3u.addWidget(lbl_s1)

        self.drawer_txt_m3u = QLineEdit()
        cur_m3u = get_app_setting("last_m3u", str(DEFAULT_SERIE_M3U))
        self.drawer_txt_m3u.setText(str(cur_m3u))
        self.drawer_txt_m3u.setPlaceholderText("Ruta / URL M3U...")
        l_m3u.addWidget(self.drawer_txt_m3u)

        row_m3u_btns = QHBoxLayout()
        btn_de_serie = QPushButton("⚡ De serie")
        btn_de_serie.setObjectName("BtnNeon")
        btn_de_serie.setToolTip("Restaurar lista original TV-76173252_playlist.m3u")
        btn_de_serie.clicked.connect(lambda: (
            self.drawer_txt_m3u.setText(str(DEFAULT_SERIE_M3U)),
            self._load_source(str(DEFAULT_SERIE_M3U))
        ))
        btn_browse = QPushButton("📂 Examinar…")
        btn_browse.setObjectName("BtnDark")
        btn_browse.clicked.connect(self._drawer_browse_m3u)
        row_m3u_btns.addWidget(btn_de_serie)
        row_m3u_btns.addWidget(btn_browse)
        l_m3u.addLayout(row_m3u_btns)

        btn_apply_m3u = QPushButton("🔄 Aplicar y Cargar Lista")
        btn_apply_m3u.setObjectName("BtnDark")
        btn_apply_m3u.clicked.connect(lambda: self._load_source(self.drawer_txt_m3u.text()))
        l_m3u.addWidget(btn_apply_m3u)
        l_m3u.addStretch()
        tabs.addTab(tab_m3u, "📺 Lista")

        # ── SECCIÓN 2: MOTOR & ANTI-CORTES ──
        tab_engine = QWidget()
        l_eng = QVBoxLayout(tab_engine)
        l_eng.setSpacing(8)

        lbl_s2 = QLabel("SINCRONIZACIÓN Y ANTI-CORTES")
        lbl_s2.setObjectName("DrawerSectionTitle")
        l_eng.addWidget(lbl_s2)

        lbl_buf = QLabel("Búfer anti-cortes de emisión deportiva:")
        lbl_buf.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        l_eng.addWidget(lbl_buf)

        self.drawer_buffer_combo = QComboBox()
        self.drawer_buffer_combo.setObjectName("CountryCombo")
        self.drawer_buffer_combo.addItem("3 segundos (Baja latencia)", 3)
        self.drawer_buffer_combo.addItem("5 segundos (⭐ Recomendado · Cero cortes)", 5)
        self.drawer_buffer_combo.addItem("8 segundos (Estabilidad alta)", 8)
        self.drawer_buffer_combo.addItem("12 segundos (Máxima protección)", 12)
        cur_buf = int(get_app_setting("buffer_secs", 5) or 5)
        idx_b = self.drawer_buffer_combo.findData(cur_buf)
        if idx_b >= 0: self.drawer_buffer_combo.setCurrentIndex(idx_b)
        self.drawer_buffer_combo.currentIndexChanged.connect(self._on_drawer_buffer_changed)
        l_eng.addWidget(self.drawer_buffer_combo)

        card_status = QWidget(); card_status.setObjectName("DrawerCard")
        cl = QVBoxLayout(card_status)
        cl.setSpacing(4)
        cl.addWidget(QLabel("<b>• Motor Multimedia:</b> SLONE ULTRA ENGINE"))
        cl.addWidget(QLabel("<b>• Modo Incrustado:</b> XCB Nativo (Sin ventanas externas)"))
        cl.addWidget(QLabel("<b>• Reconexión TCP:</b> Automática con ffmpeg"))
        cl.addWidget(QLabel("<b>• Sincronía:</b> video-sync=audio (Cero bucles)"))
        l_eng.addWidget(card_status)

        btn_resync = QPushButton("⚡ Resincronizar Canal Ahora")
        btn_resync.setObjectName("BtnNeon")
        btn_resync.clicked.connect(self._resync_signal)
        l_eng.addWidget(btn_resync)
        l_eng.addStretch()
        tabs.addTab(tab_engine, "⚡ Motor")

        # ── SECCIÓN 3: IDIOMAS & MULTI-AUDIO ──
        tab_audio = QWidget()
        l_aud = QVBoxLayout(tab_audio)
        l_aud.setSpacing(8)

        lbl_s3 = QLabel("SELECCIÓN DE IDIOMA Y COMENTARIOS")
        lbl_s3.setObjectName("DrawerSectionTitle")
        l_aud.addWidget(lbl_s3)

        self.drawer_audio_list = QListWidget()
        self.drawer_audio_list.setStyleSheet("background: #08090C; border: 1px solid #1D212A; border-radius: 6px;")
        self.drawer_audio_list.itemClicked.connect(self._on_drawer_audio_selected)
        l_aud.addWidget(self.drawer_audio_list, 1)

        btn_refresh_audio = QPushButton("🔄 Actualizar pistas de audio")
        btn_refresh_audio.setObjectName("BtnDark")
        btn_refresh_audio.clicked.connect(self.mpv._query_audio_tracks)
        l_aud.addWidget(btn_refresh_audio)

        lbl_sync = QLabel("Sincronización milimétrica Radio / TV (Audio Delay):")
        lbl_sync.setStyleSheet("color: #CCCCCC; font-size: 11px; margin-top: 6px;")
        l_aud.addWidget(lbl_sync)

        row_sync = QHBoxLayout()
        self.slider_sync = QSlider(Qt.Orientation.Horizontal)
        self.slider_sync.setRange(-50, 50)
        self.slider_sync.setValue(0)
        self.lbl_sync_val = QLabel("0.0s")
        self.lbl_sync_val.setStyleSheet("color: #E3FF00; font-weight: bold; min-width: 45px;")
        def on_sync_slider(val):
            secs = val / 10.0
            sign = "+" if secs > 0 else ""
            self.lbl_sync_val.setText(f"{sign}{secs:.1f}s")
            self.mpv.set_audio_delay(secs)
        self.slider_sync.valueChanged.connect(on_sync_slider)
        btn_reset_sync = QPushButton("↺ 0.0s")
        btn_reset_sync.setObjectName("BtnDark")
        btn_reset_sync.clicked.connect(lambda: (self.slider_sync.setValue(0), self.mpv.set_audio_delay(0.0)))
        row_sync.addWidget(self.slider_sync, 1)
        row_sync.addWidget(self.lbl_sync_val)
        row_sync.addWidget(btn_reset_sync)
        l_aud.addLayout(row_sync)
        tabs.addTab(tab_audio, "🎙 Audio")

        # ── SECCIÓN 4: APARIENCIA (LOGO Y TIPOGRAFÍA) ──
        tab_look = QWidget()
        l_look = QVBoxLayout(tab_look)
        l_look.setSpacing(8)

        lbl_s4 = QLabel("TIPOGRAFÍA, TEMAS & LOGO SLONE")
        lbl_s4.setObjectName("DrawerSectionTitle")
        l_look.addWidget(lbl_s4)

        l_look.addWidget(QLabel("Color de Pantalla / Equipo Favorito:"))
        self.drawer_theme_combo = QComboBox()
        self.drawer_theme_combo.setObjectName("CountryCombo")
        for k, t in SLONE_THEMES.items():
            self.drawer_theme_combo.addItem(t["name"], k)
        cur_t = getattr(self, "cur_theme", "obsidian")
        idx_t = self.drawer_theme_combo.findData(cur_t)
        if idx_t >= 0: self.drawer_theme_combo.setCurrentIndex(idx_t)
        self.drawer_theme_combo.currentIndexChanged.connect(lambda: self.apply_theme(self.drawer_theme_combo.currentData()))
        l_look.addWidget(self.drawer_theme_combo)

        l_look.addWidget(QLabel("Tipografía de la interfaz:"))
        self.drawer_font_combo = QComboBox()
        self.drawer_font_combo.setObjectName("CountryCombo")
        self.drawer_font_combo.addItem("Inter (Limpia & Minimalista SLONE)", "Inter")
        self.drawer_font_combo.addItem("Montserrat (Moderna & Geométrica)", "Montserrat")
        self.drawer_font_combo.addItem("Rajdhani (Tecnológica & Deportes)", "Rajdhani")
        self.drawer_font_combo.addItem("Segoe UI (Estándar OS)", "Segoe UI")
        cur_font = str(get_app_setting("ui_font", "Inter") or "Inter")
        idx_f = self.drawer_font_combo.findData(cur_font)
        if idx_f >= 0: self.drawer_font_combo.setCurrentIndex(idx_f)
        self.drawer_font_combo.currentIndexChanged.connect(self._on_drawer_font_changed)
        l_look.addWidget(self.drawer_font_combo)

        l_look.addWidget(QLabel("Estilo de Logotipo SLONE:"))
        self.drawer_logo_combo = QComboBox()
        self.drawer_logo_combo.setObjectName("CountryCombo")
        self.drawer_logo_combo.addItem("👑 Royal Crown (Corona Dorada)", "crown")
        self.drawer_logo_combo.addItem("⚡ Cyber Tech Hexagon", "tech")
        self.drawer_logo_combo.addItem("🌊 Wave Dynamic Minimal", "wave")
        self.drawer_logo_combo.addItem("✦ Neon Ultra Classic", "classic")
        cur_logo = str(get_app_setting("ui_logo", "crown") or "crown")
        idx_l = self.drawer_logo_combo.findData(cur_logo)
        if idx_l >= 0: self.drawer_logo_combo.setCurrentIndex(idx_l)
        self.drawer_logo_combo.currentIndexChanged.connect(self._on_drawer_logo_changed)
        l_look.addWidget(self.drawer_logo_combo)
        l_look.addStretch()
        tabs.addTab(tab_look, "🎨 Estilo")

        # ── SECCIÓN 5: RED & XIAOMI TV ──
        tab_net = QWidget()
        l_net = QVBoxLayout(tab_net)
        l_net.setSpacing(8)

        lbl_s5 = QLabel("TRANSMISIÓN Y RELAY")
        lbl_s5.setObjectName("DrawerSectionTitle")
        l_net.addWidget(lbl_s5)

        f_net = QFormLayout()
        self.drawer_txt_cast_ip = QLineEdit(str(get_app_setting("cast_ip", "192.168.1.135")))
        f_net.addRow("IP Xiaomi TV:", self.drawer_txt_cast_ip)
        self.drawer_txt_cast_name = QLineEdit(str(get_app_setting("cast_name", "SLÖNE")))
        f_net.addRow("Nombre Cast:", self.drawer_txt_cast_name)
        l_net.addLayout(f_net)

        btn_save_net = QPushButton("💾 Guardar Red")
        btn_save_net.setObjectName("BtnDark")
        btn_save_net.clicked.connect(self._drawer_save_net)
        l_net.addWidget(btn_save_net)

        btn_test_cast = QPushButton("📡 Probar conexión con TV")
        btn_test_cast.setObjectName("BtnNeon")
        btn_test_cast.clicked.connect(self._cast_to_xiaomi_tv)
        l_net.addWidget(btn_test_cast)
        l_net.addStretch()
        tabs.addTab(tab_net, "📡 Red")

        vl.addWidget(tabs, 1)
        return drawer

    def _on_drawer_buffer_changed(self, idx: int):
        secs = self.drawer_buffer_combo.currentData()
        if secs:
            set_app_setting("buffer_secs", secs)
            self.mpv.set_buffer_secs(secs)
            if hasattr(self, "osd_badge_buffer"):
                self.osd_badge_buffer.setText(f"ANTI-CORTES {secs}s")

    def _on_drawer_font_changed(self, idx: int):
        family = self.drawer_font_combo.currentData()
        if family:
            set_app_setting("ui_font", family)
            app = QApplication.instance()
            if app:
                f = app.font()
                f.setFamily(family)
                app.setFont(f)

    def _on_drawer_logo_changed(self, idx: int):
        logo_key = self.drawer_logo_combo.currentData()
        if logo_key:
            set_app_setting("ui_logo", logo_key)
            icons = {
                "crown": "👑 SLONE<span style='color:#E3FF00'>.OS</span>",
                "tech": "⚡ SLONE<span style='color:#00F0FF'>.PRO</span>",
                "wave": "🌊 SLONE<span style='color:#9FE870'>.STREAM</span>",
                "classic": "✦ SLONE<span style='color:#E3FF00'>.OS</span>",
            }
            if hasattr(self, "brand_label"):
                self.brand_label.setText(icons.get(logo_key, "👑 SLONE<span style='color:#E3FF00'>.OS</span>"))

    def _on_drawer_audio_selected(self, item: QListWidgetItem):
        track_info = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(track_info, dict):
            self.mpv.set_audio_option(track_info)
            self.btn_audio_select.setText(f"🎙 {track_info.get('title', '')[:14]}")

    def _refresh_drawer_audio_list(self, tracks: list):
        if not hasattr(self, "drawer_audio_list"):
            return
        self.drawer_audio_list.clear()
        for t in tracks:
            prefix = "✓ " if t.get("selected") else "   "
            item = QListWidgetItem(f"{prefix}{t['title']}")
            item.setData(Qt.ItemDataRole.UserRole, t)
            if t.get("selected"):
                item.setForeground(QColor("#E3FF00"))
            self.drawer_audio_list.addItem(item)

    def _drawer_browse_m3u(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar lista M3U", str(Path.home() / "Descargas"), "Playlists M3U (*.m3u *.m3u8);;Todos (*)")
        if fn:
            self.drawer_txt_m3u.setText(fn)

    def _drawer_save_net(self):
        ip = self.drawer_txt_cast_ip.text().strip()
        name = self.drawer_txt_cast_name.text().strip()
        if ip: set_app_setting("cast_ip", ip)
        if name: set_app_setting("cast_name", name)
        QMessageBox.information(self, "Red Guardada", f"Configuración de transmisión a {name} ({ip}) guardada con éxito.")

    def _resync_signal(self):
        """Reinicia la reproducción del canal actual para vaciar cualquier retardo y reconectar al segundo exacto."""
        if self.current_channel and self.current_channel.get("url"):
            name = self.current_channel.get("name", "")
            self.lbl_channel_title.setText(f"⚡ Resincronizando señal directa: {name}")
            self.mpv.play(self.current_channel["url"])
            if hasattr(self, "osd_badge_buffer"):
                self.osd_badge_buffer.setText(f"ANTI-CORTES {self.mpv._buffer_secs}s")

    def _diagnose_current_stream(self):
        if not self.current_channel:
            QMessageBox.information(self, "Diagnóstico de Stream", "Selecciona o reproduce un canal primero para analizar su señal.")
            return
        ch = self.current_channel
        name = ch.get("name", "Canal")
        url = ch.get("url", "")
        if not url:
            QMessageBox.warning(self, "Diagnóstico de Stream", "El canal no tiene URL válida.")
            return

        t0 = time.time()
        status_msg = []
        status_msg.append(f"<b>Canal:</b> {name}")
        status_msg.append(f"<b>URL:</b> {url}")

        try:
            req = urllib.request.Request(url, headers={"User-Agent": get_app_setting("user_agent", UA_IPTV), "Range": "bytes=0-1024"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                elapsed_ms = int((time.time() - t0) * 1000)
                code = resp.getcode()
                ctype = resp.headers.get("Content-Type", "desconocido")
                server = resp.headers.get("Server", "servidor IPTV")
                status_msg.append(f"<b>Estado HTTP:</b> <span style='color:#9FE870;'>{code} OK</span>")
                status_msg.append(f"<b>Latencia de conexión:</b> <span style='color:#E3FF00;'>{elapsed_ms} ms</span>")
                status_msg.append(f"<b>Tipo MIME:</b> {ctype}")
                status_msg.append(f"<b>Servidor remoto:</b> {server}")
                status_msg.append("<b>Diagnóstico:</b> <span style='color:#9FE870;'>✅ Señal en directo activa y respondiendo perfectamente.</span>")
        except Exception as e:
            elapsed_ms = int((time.time() - t0) * 1000)
            status_msg.append(f"<b>Estado de conexión:</b> <span style='color:#FF4D4D;'>Error tras {elapsed_ms} ms</span>")
            status_msg.append(f"<b>Detalle:</b> {e}")
            status_msg.append("<b>Diagnóstico:</b> <span style='color:#FF4D4D;'>⚠ El servidor no responde o ha rechazado la solicitud.</span>")

        QMessageBox.information(self, f"Diagnóstico — {name}", "<br>".join(status_msg))

    def _get_xtream_info(self) -> dict:
        """Extrae credenciales Xtream Codes desde la lista activa o la configuración."""
        info = {
            "server": "http://398607.solanaflix.com",
            "username": "TV-76173252",
            "password": "624816943106",
            "lan_m3u": f"http://{get_local_ip()}:8765/playlist.m3u",
            "direct_m3u": "http://398607.solanaflix.com/get.php?username=TV-76173252&password=624816943106&type=m3u_plus&output=ts",
            "direct_epg": "http://398607.solanaflix.com/xmltv.php?username=TV-76173252&password=624816943106"
        }
        sample_urls = []
        if getattr(self, "current_channel", None) and self.current_channel.get("url"):
            sample_urls.append(self.current_channel["url"])
        if hasattr(self, "all_channels") and self.all_channels:
            sample_urls.append(self.all_channels[0].get("url", ""))
        for u in sample_urls:
            m = re.search(r"https?://([^/:]+(?::\d+)?)/(?:live/)?([^/]+)/([^/]+)/", u)
            if m:
                proto = "https" if u.startswith("https") else "http"
                host = m.group(1)
                user = m.group(2)
                pwd = m.group(3)
                info["server"] = f"{proto}://{host}"
                info["username"] = user
                info["password"] = pwd
                info["direct_m3u"] = f"{proto}://{host}/get.php?username={user}&password={pwd}&type=m3u_plus&output=ts"
                info["direct_epg"] = f"{proto}://{host}/xmltv.php?username={user}&password={pwd}"
                break
        return info

    def _show_tv_connect_dialog(self):
        info = self._get_xtream_info()
        dlg = QDialog(self)
        dlg.setWindowTitle("👑 SLONE GLOBAL MEDIA ENGINE — Conexión Soberana Smart TV")
        dlg.resize(680, 520)
        dlg.setStyleSheet("""
            QDialog { background-color: #0D0D0D; color: #FFFFFF; font-family: sans-serif; }
            QLabel { color: #E0E0E0; font-size: 13px; }
            QLineEdit { background-color: #1A1A1A; color: #E3FF00; border: 1px solid #333333; border-radius: 6px; padding: 6px 10px; font-weight: bold; font-size: 13px; }
            QPushButton { background-color: #222222; color: #FFFFFF; border: 1px solid #444444; border-radius: 6px; padding: 6px 14px; font-weight: bold; }
            QPushButton:hover { background-color: #333333; border-color: #E3FF00; color: #E3FF00; }
            QTabWidget::pane { border: 1px solid #222222; background: #121212; border-radius: 8px; }
            QTabBar::tab { background: #181818; color: #888888; padding: 8px 16px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 4px; font-weight: bold; }
            QTabBar::tab:selected { background: #E3FF00; color: #000000; }
        """)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QLabel("📺 SLONE TV CONNECT™ — Sincronización Multipantalla Smart TV")
        header.setStyleSheet("color: #E3FF00; font-size: 17px; font-weight: 900;")
        layout.addWidget(header)

        sub = QLabel("Conecta tu Smart TV, Fire TV, Apple TV o dispositivo móvil al ecosistema SLONE para reproducir de forma independiente sin depender del PC.")
        sub.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        layout.addWidget(sub)

        tabs = QTabWidget()

        # Pestaña 1: Xtream Codes (Protocolo SLONE TV Connect)
        tab_xtream = QWidget()
        v_xt = QVBoxLayout(tab_xtream)
        v_xt.setContentsMargins(16, 16, 16, 16)
        v_xt.setSpacing(10)

        v_xt.addWidget(QLabel("<b>⭐ Método 1 (Recomendado): Protocolo SLONE Xtream API en Smart TV</b><br><span style='color:#888;'>Introduce las credenciales en tu app de Smart TV para decodificación nativa con logos y EPG.</span>"))

        def add_copy_row(lay, label_text, val_text):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(140)
            txt = QLineEdit(val_text)
            txt.setReadOnly(True)
            btn_cp = QPushButton("📋 Copiar")
            btn_cp.setFixedWidth(80)
            def do_cp():
                QApplication.clipboard().setText(val_text)
                btn_cp.setText("✓ Copiado")
                QTimer.singleShot(1500, lambda: btn_cp.setText("📋 Copiar"))
            btn_cp.clicked.connect(do_cp)
            row.addWidget(lbl)
            row.addWidget(txt, 1)
            row.addWidget(btn_cp)
            lay.addLayout(row)

        add_copy_row(v_xt, "Servidor (URL):", info["server"])
        add_copy_row(v_xt, "Nombre de Usuario:", info["username"])
        add_copy_row(v_xt, "Contraseña:", info["password"])
        add_copy_row(v_xt, "User-Agent:", "IPTVSmartersPro")

        pasos = QLabel("<b>Cómo configurarlo en tu Smart TV:</b><br>"
                       "1. En tu TV abre la aplicación de televisión IPTV → <i>Añadir lista</i>.<br>"
                       "2. Selecciona <b>Xtream Codes / Servidor</b>.<br>"
                       "3. Introduce el Servidor, Usuario y Contraseña que ves arriba y pulsa <i>Conectar</i>.")
        pasos.setStyleSheet("color: #BBBBBB; font-size: 11px; background: #181818; padding: 10px; border-radius: 6px; border: 1px solid #282828;")
        v_xt.addWidget(pasos)
        v_xt.addStretch()
        tabs.addTab(tab_xtream, "⭐ Xtream Codes (TV)")

        # Pestaña 2: M3U en Red Local (Servidor SLONE AirRelay)
        tab_lan = QWidget()
        v_lan = QVBoxLayout(tab_lan)
        v_lan.setContentsMargins(16, 16, 16, 16)
        v_lan.setSpacing(10)

        v_lan.addWidget(QLabel("<b>📡 Método 2: Servidor M3U SLONE AirRelay™ en Red Local</b><br><span style='color:#888;'>Tu ThinkPad X390 sirve la lista directamente a cualquier dispositivo conectado a tu red Wi-Fi.</span>"))

        add_copy_row(v_lan, "URL M3U Red Local:", info["lan_m3u"])
        add_copy_row(v_lan, "URL M3U Directa:", info["direct_m3u"])

        info_lan = QLabel("<b>Sincronización universal mediante URL M3U SLONE AirRelay™:</b><br>"
                          f"• En la app en tu Smart TV, móvil o proyector, elige <b>Añadir lista M3U</b> e introduce: <br>"
                          f"<code style='color:#E3FF00;'>{info['lan_m3u']}</code><br>"
                          "• El servidor local SLONE AirRelay está activo y accesible en tu red local.")
        info_lan.setStyleSheet("color: #BBBBBB; font-size: 11px; background: #181818; padding: 10px; border-radius: 6px; border: 1px solid #282828;")
        v_lan.addWidget(info_lan)
        v_lan.addStretch()
        tabs.addTab(tab_lan, "📡 M3U Red Local")

        # Pestaña 3: Independencia y Conexiones Simultáneas
        tab_info = QWidget()
        v_inf = QVBoxLayout(tab_info)
        v_inf.setContentsMargins(16, 16, 16, 16)
        v_inf.setSpacing(12)

        v_inf.addWidget(QLabel("<b style='color:#E3FF00;'>ℹ️ Independencia y Conexiones Simultáneas de tu Línea</b>"))
        
        box_indep = QLabel(
            "<b>1. Independencia total de control:</b><br>"
            "Con SLONE TV Connect™, tu Smart TV y tu PC con SLONE son <b>completamente independientes</b>:<br>"
            "• Puedes cambiar de canal en la TV sin que afecte a SLONE.<br>"
            "• Puedes pausar o cerrar SLONE en el PC y la TV sigue funcionando.<br><br>"
            "<b>2. Límite de conexiones simultáneas del proveedor:</b><br>"
            "• La cuenta actual de Solanaflix está contratada con <b>1 conexión activa (max_connections = 1)</b>.<br>"
            "• Esto significa que puedes alternar entre PC y TV cuando quieras, pero <b>no reproducir a la vez en ambos al mismo tiempo</b> (el servidor IPTV cortará una de las dos transmisiones).<br>"
            "• Si necesitas ver dos canales distintos al mismo tiempo en el PC y en la TV, solicita a tu proveedor IPTV una <b>segunda conexión simultánea (Multi-Room)</b>."
        )
        box_indep.setStyleSheet("color: #CCCCCC; font-size: 12px; line-height: 1.4; background: #181818; padding: 12px; border-radius: 6px; border: 1px solid #333333;")
        box_indep.setWordWrap(True)
        v_inf.addWidget(box_indep)
        v_inf.addStretch()
        tabs.addTab(tab_info, "ℹ️ Conexiones y Uso")

        layout.addWidget(tabs, 1)

        btn_close = QPushButton("Entendido / Cerrar")
        btn_close.setObjectName("BtnNeon")
        btn_close.clicked.connect(dlg.close)
        layout.addWidget(btn_close, 0, Qt.AlignmentFlag.AlignRight)

        self._tv_connect_dialog = dlg
        self._tivimate_dialog = dlg
        dlg.setModal(False)
        dlg.show()

    def _show_tivimate_share_dialog(self):
        """Alias de compatibilidad."""
        self._show_tv_connect_dialog()

    def _show_shortcuts_dialog(self):
        txt = """<h3>⌨ Atajos de Teclado de SLOCAST</h3>
<ul>
  <li><b>Espacio:</b> Reproducir / Pausar</li>
  <li><b>F / F11:</b> Pantalla Completa</li>
  <li><b>A / Ctrl+A:</b> Conmutar siguiente pista de audio (Español / Català / Radio)</li>
  <li><b>Flecha Derecha / N:</b> Siguiente canal</li>
  <li><b>Flecha Izquierda / P:</b> Canal anterior</li>
  <li><b>Flecha Arriba / +:</b> Subir volumen</li>
  <li><b>Flecha Abajo / -:</b> Bajar volumen</li>
  <li><b>M:</b> Silenciar / Desactivar silencio (Mute)</li>
  <li><b>Ctrl+F:</b> Buscar canal</li>
  <li><b>Ctrl+O:</b> Abrir archivo local M3U</li>
  <li><b>Ctrl+U:</b> Cargar lista desde URL web</li>
  <li><b>Ctrl+X:</b> Servidor Xtream Codes</li>
  <li><b>Ctrl+, :</b> Abrir Preferencias y Configuración</li>
  <li><b>F5:</b> Recargar lista actual</li>
  <li><b>Ctrl+Q:</b> Salir de la aplicación</li>
</ul>
"""
        QMessageBox.information(self, "Atajos de Teclado — SLOCAST", txt)

    def _show_about_dialog(self):
        txt = """<h2>👑 SLOCAST 1.0</h2>
<p><b>SLONE OS v7.0 — Global Luxury Media & Broadcast Ecosystem</b></p>
<p>Diseñado para ThinkPad X390 · Fedora 44 Linux (KDE Plasma 6).</p>
<hr>
<ul>
  <li><b>Motor de reproducción:</b> MPV con aceleración por hardware Intel VAAPI y latencia ultra-baja.</li>
  <li><b>Soporte Multi-Audio:</b> Català, Español, Radio y V.O. en un clic.</li>
  <li><b>Mando a distancia táctil:</b> Acceso web móvil local (puerto 8765).</li>
  <li><b>Proyección Xiaomi TV:</b> Protocolo Google Cast en LAN doméstica.</li>
  <li><b>Lista IPTV de serie:</b> Respeta al 100% el orden y categorización del proveedor.</li>
</ul>
<p style='color:#E3FF00;'><i>Desarrollado para el máximo disfrute y eficiencia.</i></p>
"""
        QMessageBox.information(self, "Acerca de SLOCAST 1.0", txt)

    def _show_performance_dialog(self):
        self._apply_perf_profile()

    def _toggle_playback(self):
        if self.mpv.is_playing():
            self.mpv.toggle_pause()
        elif self.current_channel:
            self._tune(self.current_channel)

    def _toggle_mute(self):
        m = self.mpv.toggle_mute()
        if m:
            self.btn_mute.setText("🔇")
            self.btn_mute.setStyleSheet("color: #FF4444; border-color: #FF4444;")
        else:
            self.btn_mute.setText("🔊")
            self.btn_mute.setStyleSheet("")

    def _on_volume_changed(self, val: int):
        self.mpv.set_volume(val)
        if not self.mpv._muted:
            self.btn_mute.setText("🔊")
            self.btn_mute.setStyleSheet("")

    def _step_volume(self, delta: int):
        new_val = max(0, min(100, self.slider_vol.value() + delta))
        self.slider_vol.setValue(new_val)

    def _bookmark_current(self):
        if self.current_channel and self.current_channel not in self.bookmarked_channels:
            self.bookmarked_channels.append(self.current_channel)
            it = QListWidgetItem(f"★ {self.current_channel['name']}")
            it.setData(Qt.ItemDataRole.UserRole, self.current_channel)
            self.fav_list.addItem(it)
            QMessageBox.information(self, "Favoritos", f"Añadido a Favoritos:\n{self.current_channel['name']}")

    def _cast_to_xiaomi_tv(self):
        if not HUB.current_url:
            QMessageBox.information(self, "Cast TV", "Selecciona un canal en la lista primero para iniciar la emisión.")
            return
        self.cast_ctl.connect_and_play(self.relay.stream_url, HUB.channel_name)

    def _on_cast_status(self, msg: str, active: bool):
        if active:
            self.btn_top_cast.setText("📡  Emitiendo en Xiaomi TV")
            self.btn_top_cast.setStyleSheet("background-color: #00E676; color: #000; font-weight: 900;")
        else:
            self.btn_top_cast.setText("📡  Transmitir a Xiaomi TV (SLÖNE)")
            self.btn_top_cast.setStyleSheet("")

    def _open_local_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir archivo de vídeo", str(Path.home()),
            "Vídeo (*.mp4 *.mkv *.ts *.avi *.mov *.m4v);;Todos los archivos (*)"
        )
        if path:
            self.lbl_local_file.setText(path)
            fake_ch = {"name": Path(path).name, "url": f"file://{path}", "group": "Vídeo Local"}
            self._tune(fake_ch)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self._exit_fullscreen()
        else:
            self._enter_fullscreen()

    def _enter_fullscreen(self):
        # Garantizar que estamos en la vista de streaming
        self.stack.setCurrentIndex(0)
        # Ocultar todos los paneles y barras ajenos al vídeo
        if hasattr(self, "channel_panel") and self.channel_panel:
            self.channel_panel.hide()
        if hasattr(self, "top_header") and self.top_header:
            self.top_header.hide()
        if hasattr(self, "bottom_dock") and self.bottom_dock:
            self.bottom_dock.hide()
        if hasattr(self, "tivimate_banner") and self.tivimate_banner:
            self.tivimate_banner.hide()
        if hasattr(self, "settings_drawer") and self.settings_drawer:
            self.settings_drawer.hide()
        if self.menuBar():
            self.menuBar().hide()
        if hasattr(self, "page_channels_layout") and self.page_channels_layout:
            self.page_channels_layout.setContentsMargins(0, 0, 0, 0)
        if hasattr(self, "player_layout") and self.player_layout:
            self.player_layout.setContentsMargins(0, 0, 0, 0)
            self.player_layout.setSpacing(0)
        self.showFullScreen()

    def _exit_fullscreen(self):
        self.showNormal()
        if self.menuBar():
            self.menuBar().hide()
        if hasattr(self, "top_header") and self.top_header:
            self.top_header.show()
        if hasattr(self, "bottom_dock") and self.bottom_dock:
            self.bottom_dock.hide()
        if hasattr(self, "tivimate_banner") and self.tivimate_banner:
            self.tivimate_banner.show()
        if hasattr(self, "page_channels_layout") and self.page_channels_layout:
            self.page_channels_layout.setContentsMargins(8, 6, 8, 6)
        if hasattr(self, "player_layout") and self.player_layout:
            self.player_layout.setContentsMargins(6, 4, 4, 4)
            self.player_layout.setSpacing(4)
        if hasattr(self, "channel_panel") and self.channel_panel:
            if not getattr(self, "_channels_hidden_by_user", False):
                self.channel_panel.show()

    def toggle_stadium_mode(self):
        """Conmuta entre reproducción individual estándar y cuadrícula Multiview Stadium™ 4X."""
        if not hasattr(self, "stadium_widget") or self.stadium_widget is None:
            return

        self.stadium_mode = not getattr(self, "stadium_mode", False)
        t = SLONE_THEMES.get(getattr(self, "cur_theme", "obsidian"), SLONE_THEMES["obsidian"])

        if self.stadium_mode:
            self.player_stack.setCurrentIndex(1)
            self.stadium_widget.update_visual_state(t["accent"])
            if hasattr(self, "btn_banner_stadium"):
                self.btn_banner_stadium.setText("✖ SALIR STADIUM [F4]")
                self.btn_banner_stadium.setStyleSheet(f"background-color: {t['accent']}; color: #000000; font-weight: 900;")
            if hasattr(self, "btn_stadium_bottom"):
                self.btn_stadium_bottom.setText("✖ Salir de Stadium 4X [F4]")

            cur_ch = getattr(self, "current_channel", None)
            self.mpv.stop()

            if cur_ch:
                self.stadium_widget.play_channel_in_quadrant(0, cur_ch)
            elif self.all_channels:
                self.stadium_widget.play_channel_in_quadrant(0, self.all_channels[0])

            sports_ch = [c for c in self.all_channels if any(k in (c["name"] + c.get("group", "")).upper() for k in ["DEPORTE", "FÚTBOL", "LALIGA", "DAZN", "SPORT", "TDP", "TELEDEPORTE", "TV3"])]
            candidates = sports_ch if len(sports_ch) >= 4 else self.all_channels
            for i in range(1, 4):
                if i < len(candidates):
                    self.stadium_widget.play_channel_in_quadrant(i, candidates[i])

            if hasattr(self, "osd_channel_label"):
                self.osd_channel_label.setText("🏟️ MULTIVIEW STADIUM™ 4X — Teclas 1, 2, 3, 4 para alternar audio")
        else:
            active_idx = self.stadium_widget.active_quadrant
            active_quad_ch = self.stadium_widget.quadrants[active_idx].get("channel")
            self.stadium_widget.stop_all()

            self.player_stack.setCurrentIndex(0)
            if hasattr(self, "btn_banner_stadium"):
                self.btn_banner_stadium.setText("🏟️ STADIUM 4X")
                self.btn_banner_stadium.setStyleSheet("")
            if hasattr(self, "btn_stadium_bottom"):
                self.btn_stadium_bottom.setText("🏟️ Multiview Stadium 4X [F4]")

            if active_quad_ch:
                self._tune(active_quad_ch)
            elif getattr(self, "current_channel", None):
                self._tune(self.current_channel)

    def _on_stadium_quadrant_selected(self, idx: int):
        q = self.stadium_widget.quadrants[idx]
        ch_name = q.get("channel", {}).get("name", f"Señal {idx+1}") if q.get("channel") else f"Señal {idx+1} (vacía)"
        if hasattr(self, "osd_channel_label"):
            self.osd_channel_label.setText(f"🏟️ Audio asignado a Señal [{idx+1}]: {ch_name}")

    def _on_key_quad(self, idx: int):
        if getattr(self, "stadium_mode", False) and hasattr(self, "stadium_widget") and self.stadium_widget is not None:
            if hasattr(self, "search_input") and self.search_input.hasFocus():
                return
            self.stadium_widget.set_active_audio(idx)

    def _toggle_channel_panel(self):
        if not hasattr(self, "channel_panel") or not self.channel_panel:
            return
        is_hidden = self.channel_panel.isHidden()
        if is_hidden:
            self.channel_panel.show()
            self._channels_hidden_by_user = False
            if hasattr(self, "btn_toggle_channels"):
                self.btn_toggle_channels.setText("◀ Ocultar")
            if hasattr(self, "btn_banner_toggle_list"):
                self.btn_banner_toggle_list.setText("📺 Canales")
        else:
            self.channel_panel.hide()
            self._channels_hidden_by_user = True
            if hasattr(self, "btn_toggle_channels"):
                self.btn_toggle_channels.setText("▶ Canales")
            if hasattr(self, "btn_banner_toggle_list"):
                self.btn_banner_toggle_list.setText("📺 Mostrar canales")

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Escape:
            if hasattr(self, "tivimate_drawer") and self.tivimate_drawer.isVisible():
                self._toggle_tivimate_drawer()
                event.accept()
                return
            if hasattr(self, "settings_drawer") and self.settings_drawer.isVisible():
                self.settings_drawer.hide()
                event.accept()
                return
            if self.isFullScreen():
                self._exit_fullscreen()
                event.accept()
                return
        elif key in (Qt.Key.Key_M, Qt.Key.Key_F1):
            self._toggle_tivimate_drawer()
            event.accept()
            return
        elif key == Qt.Key.Key_E:
            self._show_tivimate_share_dialog()
            event.accept()
            return
        elif key == Qt.Key.Key_O:
            self.toggle_settings_drawer()
            event.accept()
            return
        elif key in (Qt.Key.Key_F, Qt.Key.Key_F11):
            self._toggle_fullscreen()
            event.accept()
            return
        elif key in (Qt.Key.Key_C, Qt.Key.Key_Tab):
            self._toggle_channel_panel()
            event.accept()
            return
        super().keyPressEvent(event)

    def _poll_ui(self):
        if self.mpv.is_playing():
            self.btn_pp.setText("⏸")
        else:
            self.btn_pp.setText("▶")

    def closeEvent(self, event):
        self.mpv.stop()
        self.relay.stop()
        super().closeEvent(event)

# ──────────────────────────────────────────────────────────────
#  PUNTO DE ENTRADA SLONE OS (ENCLAVE BIOMÉTRICO THINKPAD X390)
# ──────────────────────────────────────────────────────────────
# === SLOCAST CATEGORIZACION DEPORTIVA v2 - POR COMPETICION ===

SLOCAST_CATEGORY_ORDER = [
    "\U0001f525 EN DIRECTO HOY",
    "\u26bd LALIGA EA SPORTS",
    "\u26bd LALIGA HYPERMOTION",
    "\u26bd CHAMPIONS LEAGUE",
    "\u26bd EUROPA LEAGUE",
    "\u26bd SELECCIONES",
    "\u26bd COPA DEL REY",
    "\u26bd PREMIER LEAGUE",
    "\u26bd SERIE A / CALCIO",
    "\u26bd BUNDESLIGA",
    "\u26bd LIGUE 1",
    "\u26bd OTRAS LIGAS FUTBOL",
    "\U0001f3cd\ufe0f MOTOGP",
    "\U0001f3ce\ufe0f F1",
    "\U0001f94a UFC / MMA / BOXEO",
    "\U0001f3c0 NBA",
    "\U0001f3c0 LIGA ACB / EUROLIGA",
    "\U0001f3be TENIS",
    "\U0001f4fa DEPORTES ESPA\u00d1A",
    "\U0001f4fa TV GENERAL ESPA\u00d1A",
    "\U0001f310 INTERNACIONAL",
    "\U0001f4c1 OTROS",
]

PROVIDER_WEIGHT = [
    ("MOVISTAR", 0), ("M+", 1), ("DAZN", 2),
    ("TDT", 3), ("TELEDEPORTE", 4), ("TDP", 5),
    ("GOL", 6), ("EUROSPORT", 7), ("ESPN", 8), ("FOX", 9),
]

def _slocast_provider_weight(ch):
    name = (ch.get("name") or "").upper()
    for prov, w in PROVIDER_WEIGHT:
        if prov in name:
            return w
    return 99

def _slocast_categorize(ch):
    name = (ch.get("name") or "").upper()
    group = (ch.get("group") or "").upper()
    txt = name + " " + group

    if any(k in txt for k in ["EN DIRECTO", "DIRECTO HOY", "STREAMING HOY", "LIVE EVENT"]):
        return "\U0001f525 EN DIRECTO HOY"
    if any(k in txt for k in ["LALIGA EA", "LA LIGA EA", "LALIGA SPORTS"]):
        return "\u26bd LALIGA EA SPORTS"
    if any(k in txt for k in ["HYPERMOTION", "SMARTBANK", "LALIGA 2", "SEGUNDA DIVISION"]):
        return "\u26bd LALIGA HYPERMOTION"
    if any(k in txt for k in ["COPA DEL REY", "COPA REY"]):
        return "\u26bd COPA DEL REY"
    if any(k in txt for k in ["CHAMPIONS", "UCL", "LIGA DE CAMPEONES"]):
        return "\u26bd CHAMPIONS LEAGUE"
    if any(k in txt for k in ["EUROPA LEAGUE", "UEL", "CONFERENCE LEAGUE"]):
        return "\u26bd EUROPA LEAGUE"
    if any(k in txt for k in ["SELECCION", "NATIONS", "EUROCOPA", "MUNDIAL", "WORLD CUP"]):
        return "\u26bd SELECCIONES"
    if any(k in txt for k in ["PREMIER LEAGUE", "PREMIER"]):
        return "\u26bd PREMIER LEAGUE"
    if any(k in txt for k in ["SERIE A", "CALCIO", "JUVENTUS", "NAPOLI", "AS ROMA", "LAZIO"]):
        return "\u26bd SERIE A / CALCIO"
    if any(k in txt for k in ["BUNDESLIGA", "BAYERN", "DORTMUND"]):
        return "\u26bd BUNDESLIGA"
    if any(k in txt for k in ["LIGUE 1", "PSG", "MARSELLA"]):
        return "\u26bd LIGUE 1"
    if any(k in txt for k in ["LALIGA", "LA LIGA", "LIGA TV", "M+ LALIGA"]):
        return "\u26bd LALIGA EA SPORTS"
    if any(k in txt for k in ["FUTBOL", "F\u00daTBOL", "SOCCER", "FOOTBALL"]):
        return "\u26bd OTRAS LIGAS FUTBOL"
    if any(k in txt for k in ["MOTOGP", "MOTO GP", "MOTO2", "MOTO3"]):
        return "\U0001f3cd\ufe0f MOTOGP"
    if any(k in txt for k in ["F1", "FORMULA 1", "FORMULA1", "GRAN PREMIO"]):
        return "\U0001f3ce\ufe0f F1"
    if any(k in txt for k in ["UFC", "MMA", "BOXEO", "FIGHT", "VELADA"]):
        return "\U0001f94a UFC / MMA / BOXEO"
    if "NBA" in txt:
        return "\U0001f3c0 NBA"
    if any(k in txt for k in ["ACB", "LIGA ENDESA", "EUROLIGA", "BALONCESTO"]):
        return "\U0001f3c0 LIGA ACB / EUROLIGA"
    if any(k in txt for k in ["TENIS", "ATP", "WTA", "WIMBLEDON", "ROLAND GARROS", "US OPEN"]):
        return "\U0001f3be TENIS"

    is_spain = any(k in txt for k in [
        "ESPA\u00d1A", "SPAIN", "ES -", "ES|", "[ES]", "ES:",
        "MOVISTAR", "M+", "DAZN", "LALIGA",
    ])
    if is_spain:
        if any(k in txt for k in ["DEPORTES", "EUROSPORT", "GOLF", "TELEDEPORTE", "TDP"]):
            return "\U0001f4fa DEPORTES ESPA\u00d1A"
        return "\U0001f4fa TV GENERAL ESPA\u00d1A"
    if not txt.strip():
        return "\U0001f4c1 OTROS"
    return "\U0001f310 INTERNACIONAL"

def _slocast_sort_key(ch):
    cat = _slocast_categorize(ch)
    try:
        idx = SLOCAST_CATEGORY_ORDER.index(cat)
    except ValueError:
        idx = 999
    return (idx, _slocast_provider_weight(ch), (ch.get("name") or "").upper())

def _biometric_gate() -> bool:
    """Devuelve True si el acceso está permitido.

    - Acceso de emergencia por env/flag (recuperación si el sensor falla).
    - Si la directiva maestra lo desactiva → permite.
    - Si el sensor/huella no están disponibles → permite (no bloquea).
    - Si está activo y disponible → exige huella o contraseña de respaldo.
    """
    directive = get_control_directive()
    if not directive.get("enclave_biometrico_activo", True):
        print("[SLONE SECURITY] Enclave biométrico desactivado en la directiva maestra.")
        return True
    try:
        from slone_auth import biometric_available, require_biometric_auth
    except Exception as e:
        print(f"[SLONE SECURITY WARNING] Módulo biométrico no disponible: {e}")
        return True
    if not biometric_available():
        print("[SLONE SECURITY] Sensor de huellas no disponible: arrancando sin bloqueo.")
        return True
    try:
        return require_biometric_auth()
    except Exception as e:
        print(f"[SLONE SECURITY WARNING] Fallo al iniciar enclave biométrico: {e}")
        return True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("SLONE")

    # Guardián de Acceso Biométrico Nativo (según directiva maestra, no bloqueante si no hay sensor)
    if not _biometric_gate():
        print("\n[SLONE SECURITY] Acceso denegado: Huella dactilar no autenticada.")
        sys.exit(13)

    win = SLONEMainWindow()
    win.show()
    sys.exit(app.exec())
