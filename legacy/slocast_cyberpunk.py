import sys
import os
import random
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QSlider, QListWidget, QListWidgetItem,
                               QStyle, QFileDialog, QMessageBox, QFrame)
from PySide6.QtCore import Qt, QUrl, QTimer, QSize
from PySide6.QtGui import QIcon, QFont, QPalette, QColor, QLinearGradient, QBrush, QPainter
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

class CyberpunkStyle:
    NEON_GREEN = "#39FF14"
    YELLOW = "#FFD700"
    DARK_BG = "#0D0D0D"
    DARKER_BG = "#050505"

class PlayerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SLOCAST - Cyberpunk Player")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {CyberpunkStyle.DARK_BG};
            }}
            QLabel {{
                color: {CyberpunkStyle.NEON_GREEN};
                font-family: 'Courier New', monospace;
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {CyberpunkStyle.DARKER_BG};
                color: {CyberpunkStyle.NEON_GREEN};
                border: 2px solid {CyberpunkStyle.NEON_GREEN};
                border-radius: 10px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {CyberpunkStyle.NEON_GREEN};
                color: {CyberpunkStyle.DARK_BG};
            }}
            QPushButton:pressed {{
                background-color: {CyberpunkStyle.YELLOW};
                border-color: {CyberpunkStyle.YELLOW};
                color: {CyberpunkStyle.DARK_BG};
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {CyberpunkStyle.NEON_GREEN};
                height: 8px;
                background: {CyberpunkStyle.DARKER_BG};
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {CyberpunkStyle.YELLOW};
                border: 1px solid {CyberpunkStyle.NEON_GREEN};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            QListWidget {{
                background-color: {CyberpunkStyle.DARKER_BG};
                color: {CyberpunkStyle.NEON_GREEN};
                border: 2px solid {CyberpunkStyle.NEON_GREEN};
                border-radius: 10px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
            }}
            QListWidget::item:selected {{
                background-color: {CyberpunkStyle.YELLOW};
                color: {CyberpunkStyle.DARK_BG};
            }}
            QFrame {{
                background-color: {CyberpunkStyle.DARKER_BG};
                border: 2px solid {CyberpunkStyle.NEON_GREEN};
                border-radius: 10px;
            }}
        """)
        
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        self.is_playing = False
        self.current_playlist_index = -1
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        title_label = QLabel("SLOCAST")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"font-size: 48px; color: {CyberpunkStyle.NEON_GREEN}; letter-spacing: 8px;")
        main_layout.addWidget(title_label)
        
        subtitle = QLabel(">> CYBERPUNK AUDIO INTERFACE <<")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"font-size: 16px; color: {CyberpunkStyle.YELLOW};")
        main_layout.addWidget(subtitle)
        
        # Área de visualización (simulada)
        visual_frame = QFrame()
        visual_frame.setFixedHeight(200)
        visual_layout = QVBoxLayout(visual_frame)
        self.visual_label = QLabel("\n    ┌─────────────────────────────────────┐\n    │   ██████╗ ██╗   ██╗ █████╗ ██╗     │\n    │  ██╔════╝ ██║   ██║██╔══██╗██║     │\n    │  ██║  ███╗██║   ██║███████║██║     │\n    │  ██║   ██║██║   ██║██╔══██║██║     │\n    │  ╚██████╔╝╚██████╔╝██║  ██║███████╗│\n    │   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝│\n    └─────────────────────────────────────┘")
        self.visual_label.setAlignment(Qt.AlignCenter)
        self.visual_label.setStyleSheet(f"font-family: 'Courier New', monospace; font-size: 12px; color: {CyberpunkStyle.NEON_GREEN};")
        visual_layout.addWidget(self.visual_label)
        main_layout.addWidget(visual_frame)
        
        # Lista de reproducción
        self.playlist_widget = QListWidget()
        self.playlist_widget.setMinimumHeight(150)
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected)
        main_layout.addWidget(self.playlist_widget)
        
        # Botones de control
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)
        
        self.btn_add = QPushButton("➕ AÑADIR")
        self.btn_add.clicked.connect(self.add_files)
        
        self.btn_prev = QPushButton("⏮ ANTERIOR")
        self.btn_prev.clicked.connect(self.prev_track)
        
        self.btn_play = QPushButton("▶ REPRODUCIR")
        self.btn_play.clicked.connect(self.toggle_play)
        
        self.btn_next = QPushButton("SIGUIENTE ⏭")
        self.btn_next.clicked.connect(self.next_track)
        
        self.btn_stop = QPushButton("⏹ DETENER")
        self.btn_stop.clicked.connect(self.stop)
        
        for btn in [self.btn_add, self.btn_prev, self.btn_play, self.btn_next, self.btn_stop]:
            btn.setMinimumHeight(50)
            control_layout.addWidget(btn)
        
        main_layout.addLayout(control_layout)
        
        # Barra de progreso
        progress_layout = QHBoxLayout()
        self.time_label = QLabel("00:00")
        self.time_label.setStyleSheet(f"color: {CyberpunkStyle.YELLOW}; font-size: 14px;")
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.sliderMoved.connect(self.seek)
        self.duration_label = QLabel("00:00")
        self.duration_label.setStyleSheet(f"color: {CyberpunkStyle.YELLOW}; font-size: 14px;")
        
        progress_layout.addWidget(self.time_label)
        progress_layout.addWidget(self.progress_slider)
        progress_layout.addWidget(self.duration_label)
        main_layout.addLayout(progress_layout)
        
        # Control de volumen
        volume_layout = QHBoxLayout()
        vol_label = QLabel("VOLUMEN")
        vol_label.setStyleSheet(f"color: {CyberpunkStyle.NEON_GREEN}; font-size: 14px;")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.change_volume)
        self.audio_output.setVolume(0.7)
        volume_layout.addWidget(vol_label)
        volume_layout.addWidget(self.volume_slider)
        main_layout.addLayout(volume_layout)
        
        # Estado
        self.status_label = QLabel("SISTEMA LISTO")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"color: {CyberpunkStyle.YELLOW}; font-size: 14px;")
        main_layout.addWidget(self.status_label)
        
        # Conectar señales del reproductor
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.playbackStateChanged.connect(self.update_playback_state)
        self.media_player.mediaStatusChanged.connect(self.handle_media_status)
        
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar archivos de audio", "", "Audio (*.mp3 *.wav *.ogg *.flac *.m4a)")
        for file in files:
            item = QListWidgetItem(os.path.basename(file))
            item.setData(Qt.UserRole, file)
            self.playlist_widget.addItem(item)
        self.status_label.setText(f"{len(files)} ARCHIVOS AÑADIDOS")
    
    def play_selected(self, item):
        self.current_playlist_index = self.playlist_widget.row(item)
        self.play_current()
    
    def play_current(self):
        if self.current_playlist_index < 0 or self.current_playlist_index >= self.playlist_widget.count():
            return
        item = self.playlist_widget.item(self.current_playlist_index)
        file_path = item.data(Qt.UserRole)
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        self.media_player.play()
        self.status_label.setText(f"REPRODUCIENDO: {item.text()}")
        self.is_playing = True
        self.btn_play.setText("⏸ PAUSAR")
    
    def toggle_play(self):
        if self.media_player.source().isEmpty():
            if self.playlist_widget.count() > 0:
                self.current_playlist_index = 0
                self.play_current()
            return
        if self.is_playing:
            self.media_player.pause()
            self.is_playing = False
            self.btn_play.setText("▶ REPRODUCIR")
        else:
            self.media_player.play()
            self.is_playing = True
            self.btn_play.setText("⏸ PAUSAR")
    
    def stop(self):
        self.media_player.stop()
        self.is_playing = False
        self.btn_play.setText("▶ REPRODUCIR")
        self.status_label.setText("DETENIDO")
    
    def prev_track(self):
        if self.playlist_widget.count() == 0:
            return
        self.current_playlist_index = (self.current_playlist_index - 1) % self.playlist_widget.count()
        self.play_current()
    
    def next_track(self):
        if self.playlist_widget.count() == 0:
            return
        self.current_playlist_index = (self.current_playlist_index + 1) % self.playlist_widget.count()
        self.play_current()
    
    def seek(self, position):
        self.media_player.setPosition(position)
    
    def change_volume(self, value):
        self.audio_output.setVolume(value / 100.0)
    
    def update_position(self, position):
        if not self.progress_slider.isSliderDown():
            self.progress_slider.setValue(position)
        self.time_label.setText(self.format_time(position))
    
    def update_duration(self, duration):
        self.progress_slider.setRange(0, duration)
        self.duration_label.setText(self.format_time(duration))
    
    def update_playback_state(self, state):
        if state == QMediaPlayer.PlayingState:
            self.is_playing = True
            self.btn_play.setText("⏸ PAUSAR")
        elif state == QMediaPlayer.PausedState:
            self.is_playing = False
            self.btn_play.setText("▶ REPRODUCIR")
        elif state == QMediaPlayer.StoppedState:
            self.is_playing = False
            self.btn_play.setText("▶ REPRODUCIR")
    
    def handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.next_track()
    
    @staticmethod
    def format_time(ms):
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(CyberpunkStyle.DARK_BG))
    palette.setColor(QPalette.WindowText, QColor(CyberpunkStyle.NEON_GREEN))
    palette.setColor(QPalette.Base, QColor(CyberpunkStyle.DARKER_BG))
    palette.setColor(QPalette.Text, QColor(CyberpunkStyle.NEON_GREEN))
    app.setPalette(palette)
    
    window = PlayerWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
