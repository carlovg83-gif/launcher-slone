#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SLO Cast — Web Cast & IPTV Player v5.0 Final Edition
Entorno: Fedora Linux (KDE Plasma / ThinkPad)
Features: Dual Player Engine, Bypass SSL/User-Agent, Persistence, WebEngine
"""
import sys, os, json, ssl, subprocess, shutil
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QLineEdit, QListWidget,
    QFileDialog, QFrame, QSplitter, QMessageBox, QListWidgetItem,
    QButtonGroup, QComboBox
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QThread

CONFIG_DIR = Path.home() / ".config" / "slo_webcast"
CONFIG_FILE = CONFIG_DIR / "config.json"

def load_config():
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_config(data):
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

HAS_MULTIMEDIA = False
try:
    from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PyQt6.QtMultimediaWidgets import QVideoWidget
    HAS_MULTIMEDIA = True
except ImportError:
    pass

HAS_WEBENGINE = False
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    pass

DARK_STYLE = """
QMainWindow, QWidget { background: #121212; color: #E0E0E0; font-family: system-ui, sans-serif; }
#Sidebar { background: #181818; border-right: 1px solid #282828; min-width: 230px; max-width: 250px; }
#BrandTitle { color: #FFB300; font-size: 20px; font-weight: bold; padding: 20px 15px; }
QPushButton {
    color: #E0E0E0; background: transparent; text-align: left;
    padding: 12px 16px; font-size: 14px; border: none; border-radius: 6px; margin: 3px 10px;
}
QPushButton:hover { background: #2A2A2A; color: #FFFFFF; }
QPushButton:checked { background: #FFB300; color: #121212; font-weight: bold; }
QLineEdit, QComboBox {
    background: #242424; color: #FFFFFF; border: 1px solid #383838;
    border-radius: 6px; padding: 8px 12px; font-size: 14px;
}
QLineEdit:focus, QComboBox:focus { border: 1px solid #FFB300; }
QListWidget { background: #161616; color: #E0E0E0; border: 1px solid #282828; border-radius: 6px; }
QListWidget::item { padding: 12px; border-bottom: 1px solid #222222; }
QListWidget::item:hover { background: #222222; }
QListWidget::item:selected { background: #FFB300; color: #121212; font-weight: bold; }
QFrame#Header { background: #181818; border-bottom: 1px solid #282828; }
"""

class M3ULoader(QThread):
    loaded = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self, source: str):
        super().__init__()
        self.source = source

    def run(self):
        try:
            if self.source.startswith(("http://", "https://")):
                ctx = ssl._create_unverified_context()
                req = Request(self.source, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "*/*"
                })
                with urlopen(req, context=ctx, timeout=25) as resp:
                    raw_data = resp.read()
                    try:
                        content = raw_data.decode("utf-8")
                    except UnicodeDecodeError:
                        content = raw_data.decode("latin-1", errors="replace")
            else:
                path = Path(self.source)
                if not path.exists():
                    self.failed.emit(f"No existe el archivo local: {self.source}")
                    return
                try:
                    content = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    content = path.read_text(encoding="latin-1", errors="replace")
            
            channels = []
            cur_name = "Canal Sin Nombre"
            cur_group = "General"
            
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("#EXTINF:"):
                    if 'group-title="' in line:
                        try:
                            cur_group = line.split('group-title="')[1].split('"')[0]
                        except IndexingError:
                            cur_group = "General"
                    parts = line.split(",", 1)
                    cur_name = parts[1].strip() if len(parts) > 1 else "Canal Sin Nombre"
                elif line and not line.startswith("#"):
                    channels.append({"name": cur_name, "group": cur_group, "url": line})
                    cur_name = "Canal Sin Nombre"
            
            if not channels:
                self.failed.emit("El archivo se descargó pero no contiene entradas válidas de canales (#EXTINF).")
            else:
                self.loaded.emit(channels)
        except HTTPError as e:
            self.failed.emit(f"Error HTTP del Servidor IPTV ({e.code}): {e.reason}")
        except URLError as e:
            self.failed.emit(f"Error de red: {e.reason}")
        except Exception as e:
            self.failed.emit(f"Error procesando lista: {str(e)}")

class SLOCastApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SLO Cast — Web Cast & IPTV Player v5.0")
        self.resize(1200, 780)
        self.setStyleSheet(DARK_STYLE)

        self.config = load_config()
        self.channels_data = []

        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        s_lay = QVBoxLayout(sidebar)
        s_lay.setContentsMargins(0, 0, 0, 0)
        
        brand = QLabel(" 👑 SLO Cast")
        brand.setObjectName("BrandTitle")
        s_lay.addWidget(brand)

        self.btn_nav = QPushButton("🌐  Navegador Web")
        self.btn_iptv = QPushButton("📺  IPTV / Directo")
        self.btn_files = QPushButton("📁  Archivos Locales")
        self.btn_cast = QPushButton("📡  Transmitir a TV")
        
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        
        btns = [self.btn_nav, self.btn_iptv, self.btn_files, self.btn_cast]
        for i, b in enumerate(btns):
            b.setCheckable(True)
            s_lay.addWidget(b)
            self.group.addButton(b, i)

        s_lay.addStretch()
        lbl_ver = QLabel("v5.0 Final · Fedora Edition")
        lbl_ver.setStyleSheet("color: #666; font-size: 11px; padding: 15px;")
        s_lay.addWidget(lbl_ver)
        layout.addWidget(sidebar)

        # Reproductores
        if HAS_MULTIMEDIA:
            self.player = QMediaPlayer()
            self.audio = QAudioOutput()
            self.player.setAudioOutput(self.audio)
            self.video_widget = QVideoWidget()
            self.player.setVideoOutput(self.video_widget)
        else:
            self.video_widget = QLabel("⚠️ Módulo Multimedia no detectado")
            self.video_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pages = QStackedWidget()
        self.pages.addWidget(self._create_nav_page())
        self.pages.addWidget(self._create_iptv_page())
        self.pages.addWidget(self._create_files_page())
        self.pages.addWidget(self._create_cast_page())
        layout.addWidget(self.pages, 1)

        self.group.idClicked.connect(self.pages.setCurrentIndex)
        self.btn_iptv.setChecked(True)
        self.pages.setCurrentIndex(1)

        # Cargar lista previa guardada
        last_m3u = self.config.get("last_m3u", "")
        if last_m3u:
            self.m3u_input.setText(last_m3u)
            self.load_m3u()

    def _create_nav_page(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        
        header = QFrame()
        header.setObjectName("Header")
        hl = QHBoxLayout(header)
        
        self.btn_back = QPushButton("◄")
        self.btn_forward = QPushButton("►")
        self.btn_reload = QPushButton("🔄")
        for b in (self.btn_back, self.btn_forward, self.btn_reload):
            b.setFixedWidth(38)
            b.setStyleSheet("background: #2A2A2A; border-radius: 4px; text-align: center;")

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Introduce una dirección web (ej. https://duckduckgo.com)...")
        btn_go = QPushButton("Ir")
        btn_go.setStyleSheet("background: #FFB300; color: #121212; font-weight: bold; padding: 8px 18px;")

        hl.addWidget(self.btn_back)
        hl.addWidget(self.btn_forward)
        hl.addWidget(self.btn_reload)
        hl.addWidget(self.url_input, 1)
        hl.addWidget(btn_go)
        l.addWidget(header)

        if HAS_WEBENGINE:
            self.web = QWebEngineView()
            self.web.setUrl(QUrl("https://duckduckgo.com"))
            l.addWidget(self.web, 1)

            btn_go.clicked.connect(self._navigate)
            self.url_input.returnPressed.connect(self._navigate)
            self.btn_back.clicked.connect(self.web.back)
            self.btn_forward.clicked.connect(self.web.forward)
            self.btn_reload.clicked.connect(self.web.reload)
        else:
            lbl = QLabel("🌐 Motor WebQtEngine no disponible.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l.addWidget(lbl, 1)

        return w

    def _navigate(self):
        url = self.url_input.text().strip()
        if not url: return
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.web.setUrl(QUrl(url))

    def _create_iptv_page(self):
        w = QWidget()
        l = QVBoxLayout(w)
        
        top = QHBoxLayout()
        self.m3u_input = QLineEdit()
        self.m3u_input.setPlaceholderText("URL M3U/M3U8 o ruta de archivo...")
        
        btn_load = QPushButton("Cargar Lista")
        btn_load.setStyleSheet("background: #FFB300; color: #121212; font-weight: bold; padding: 8px 18px;")
        btn_load.clicked.connect(self.load_m3u)

        btn_browse = QPushButton("📁 Abrir M3U")
        btn_browse.setStyleSheet("background: #2A2A2A; padding: 8px 18px;")
        btn_browse.clicked.connect(self.browse_m3u_file)

        top.addWidget(self.m3u_input, 1)
        top.addWidget(btn_load)
        top.addWidget(btn_browse)
        l.addLayout(top)

        # Barra de Búsqueda y Filtro de Grupos
        filter_box = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar canal...")
        self.search_input.textChanged.connect(self.filter_channels)
        
        self.engine_mode = QComboBox()
        self.engine_mode.addItems(["Motor Integrado (Qt)", "Motor Externo (MPV / VLC)"])
        filter_box.addWidget(self.search_input, 1)
        filter_box.addWidget(self.engine_mode)
        l.addLayout(filter_box)

        splitter = QSplitter()
        self.channel_list = QListWidget()
        self.channel_list.itemDoubleClicked.connect(self.play_selected_channel)
        
        splitter.addWidget(self.channel_list)
        splitter.addWidget(self.video_widget)
        splitter.setSizes([340, 860])
        l.addWidget(splitter, 1)
        return w

    def _create_files_page(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_select = QPushButton("📁 Abrir Archivo de Vídeo Local")
        btn_select.setStyleSheet("background: #FFB300; color: #121212; font-weight: bold; padding: 15px 30px; font-size: 16px;")
        btn_select.clicked.connect(self.open_local_file)
        
        lbl_info = QLabel("Formatos soportados: .mp4, .mkv, .ts, .m3u8, .avi")
        lbl_info.setStyleSheet("color: #888; margin-top: 10px;")

        l.addWidget(btn_select)
        l.addWidget(lbl_info)
        return w

    def _create_cast_page(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl = QLabel("📡 Transmisión Local SLO Cast\nBuscando dispositivos Xiaomi TV / Chromecast en la red Wi-Fi...")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 16px; color: #AAA;")
        l.addWidget(lbl)
        return w

    def browse_m3u_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Lista M3U", "", "Listas M3U (*.m3u *.m3u8 *.txt)")
        if path:
            self.m3u_input.setText(path)
            self.load_m3u()

    def load_m3u(self):
        url = self.m3u_input.text().strip()
        if not url: return
        
        self.config["last_m3u"] = url
        save_config(self.config)

        self.loader = M3ULoader(url)
        self.loader.loaded.connect(self.on_m3u_loaded)
        self.loader.failed.connect(lambda err: QMessageBox.warning(self, "Error de Lista IPTV", f"{err}"))
        self.loader.start()

    def on_m3u_loaded(self, channels):
        self.channels_data = channels
        self.channel_list.clear()
        for ch in channels:
            item = QListWidgetItem(f"{ch['name']}  [{ch['group']}]")
            item.setData(Qt.ItemDataRole.UserRole, ch["url"])
            self.channel_list.addItem(item)

    def filter_channels(self, text):
        text = text.lower()
        for i in range(self.channel_list.count()):
            item = self.channel_list.item(i)
            item.setHidden(text not in item.text().lower())

    def play_selected_channel(self, item):
        url = item.data(Qt.ItemDataRole.UserRole)
        if not url: return

        if self.engine_mode.currentIndex() == 1:
            # Reproducción mediante motor de sistema mpv/vlc
            player_bin = shutil.which("mpv") or shutil.which("vlc")
            if player_bin:
                subprocess.Popen([player_bin, "--user-agent=VLC/3.0.18", url])
            else:
                QMessageBox.warning(self, "Error", "No se encontró el reproductor MPV ni VLC en el sistema.")
        else:
            if HAS_MULTIMEDIA:
                self.player.setSource(QUrl(url))
                self.player.play()

    def open_local_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Vídeo", "", "Archivos de Vídeo (*.mp4 *.mkv *.ts *.m3u8)")
        if path and HAS_MULTIMEDIA:
            self.player.setSource(QUrl.fromLocalFile(path))
            self.btn_iptv.setChecked(True)
            self.pages.setCurrentIndex(1)
            self.player.play()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SLOCastApp()
    win.show()
    sys.exit(app.exec())
