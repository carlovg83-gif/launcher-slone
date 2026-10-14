#!/usr/bin/env python3
"""
SLONE™ BIOMETRIC ENCLAVE & ZERO-TRUST GATEWAY
Control de acceso mediante fprintd (sensor de huellas). Portable y no bloqueante:
si el sensor o la huella no están disponibles, el llamador puede decidir continuar.
"""

import os
import sys
import shutil
import getpass
import subprocess
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap

# Usuario actual (portable): no depende de un nombre fijo.
CURRENT_USER = os.environ.get("USER") or getpass.getuser()

# Rutas de icono portables.
_ICON_CANDIDATES = [
    os.path.expanduser("~/.local/share/icons/slone.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "slone.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_portal", "assets", "slone.png"),
]


def _find_icon():
    for p in _ICON_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def secure_folder_permissions(*a, **k):
    """Compatibilidad: no-op (reservado para endurecimiento de permisos)."""
    pass


def biometric_available(username=None) -> bool:
    """True si fprintd está instalado y el usuario tiene al menos una huella registrada."""
    username = username or CURRENT_USER
    try:
        if not shutil.which("fprintd-verify") or not shutil.which("fprintd-list"):
            return False
        res = subprocess.run(
            ["fprintd-list", username],
            capture_output=True, text=True, timeout=8
        )
        out = (res.stdout or "") + (res.stderr or "")
        # fprintd-list imprime líneas tipo " - #0: right-index-finger"
        return "Fingerprints for user" in out and "#0" in out
    except Exception:
        return False


def backup_password_enabled() -> bool:
    """True si la directiva maestra permite la contraseña de respaldo."""
    try:
        import json
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "config", "slone_control.json")
        with open(path, encoding="utf-8") as f:
            directive = json.load(f).get("directiva_maestra", {})
        return bool(directive.get("contrasena_respaldo_activa", True))
    except Exception:
        return True


def master_username() -> str:
    """Usuario maestro definido en la directiva (o el usuario actual)."""
    try:
        import json
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "config", "slone_control.json")
        with open(path, encoding="utf-8") as f:
            directive = json.load(f).get("directiva_maestra", {})
        return directive.get("usuario_maestro") or CURRENT_USER
    except Exception:
        return CURRENT_USER


_PAM_CANDIDATES = ("slone", "password-auth", "system-auth", "su", "login")


def _pam_config_is_safe(service, _seen=None):
    """True si el servicio PAM no invoca el sensor de huellas (pam_fprintd).

    Sigue recursivamente las directivas 'include'/'substack' para no quedarnos
    esperando una huella en segundo plano al verificar la contraseña.
    """
    _seen = _seen if _seen is not None else set()
    if service in _seen:
        return True
    _seen.add(service)
    path = os.path.join("/etc/pam.d", service)
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except OSError:
        return False  # el servicio no existe -> no es candidato válido
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "pam_fprintd" in line:
            return False
        parts = line.split()
        if parts and parts[0].lstrip("-") in ("auth", "account", "password", "session"):
            for i, tok in enumerate(parts):
                if tok in ("include", "substack") and i + 1 < len(parts):
                    if not _pam_config_is_safe(parts[i + 1], _seen):
                        return False
    return True


def verify_backup_password(username=None, password=None) -> bool:
    """Verifica la contraseña del sistema con PAM (respaldo de la huella).

    Solo usa servicios PAM que NO invocan el sensor de huellas, para no
    bloquearse esperando una huella mientras el usuario escribe su contraseña.
    """
    username = username or CURRENT_USER
    if not password:
        return False
    try:
        import pam
    except ImportError:
        print("[SLONE SECURITY] python-pam no instalado; no hay respaldo por contraseña.")
        return False
    safe_services = [s for s in _PAM_CANDIDATES if _pam_config_is_safe(s)]
    if not safe_services:
        # Último recurso (puede tardar si el stack integra huella).
        safe_services = ["password-auth", "su"]
    for service in safe_services:
        try:
            if pam.pam().authenticate(username, password, service=service):
                return True
        except Exception:
            continue
    return False


AUTH_STYLE = """
QDialog {
    background-color: #000000;
    border: 2px solid #E3FF00;
    border-radius: 18px;
}
QLabel {
    color: #FFFFFF;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
#HeaderTitle {
    color: #E3FF00;
    font-size: 20px;
    font-weight: 900;
    letter-spacing: 2px;
}
#SubTitle {
    color: #888890;
    font-size: 13px;
    font-weight: 500;
    margin-bottom: 8px;
}
#StatusLabel {
    color: #E3FF00;
    font-size: 14px;
    font-weight: 800;
    padding: 12px;
    background: #09090C;
    border: 1px solid #1E1E24;
    border-radius: 10px;
}
QPushButton {
    background-color: #121216;
    color: #888890;
    border: 1px solid #24242C;
    border-radius: 10px;
    padding: 10px 24px;
    font-size: 13px;
    font-weight: 700;
}
QPushButton:hover {
    background-color: #1A1A22;
    color: #FFFFFF;
}
QPushButton#CancelBtn:hover {
    border-color: #FF3344;
    color: #FF3344;
}
"""


class BiometricVerifyThread(QThread):
    verified = pyqtSignal(bool, str)
    status_update = pyqtSignal(str)

    def __init__(self, username=None):
        super().__init__()
        self.username = username or CURRENT_USER
        self.proc = None
        self._is_running = True

    def run(self):
        try:
            self.status_update.emit("Activando sensor de huellas...")
            self.proc = subprocess.Popen(
                ["fprintd-verify", self.username],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            matched = False
            message = "No verificado"

            for line in iter(self.proc.stdout.readline, ''):
                line_str = line.strip()
                if not line_str:
                    continue

                if "Scan finger on" in line_str or "verify-finger" in line_str or "Place your finger" in line_str:
                    self.status_update.emit("Coloca tu huella registrada en el sensor...")
                elif "verify-match" in line_str:
                    matched = True
                    message = "Huella dactilar autenticada correctamente"
                    self.status_update.emit(message)
                    break
                elif "verify-no-match" in line_str:
                    self.status_update.emit("Huella no coincide. Inténtalo de nuevo...")
                elif "verify-swipe-too-short" in line_str:
                    self.status_update.emit("Contacto demasiado breve. Mantén el dedo...")
                elif "verify-finger-not-present" in line_str or "verify-retry-scan" in line_str:
                    self.status_update.emit("Repite el contacto con el sensor...")
                elif "error" in line_str.lower():
                    self.status_update.emit(f"Aviso: {line_str}")

            self.proc.wait()
            self.verified.emit(matched, message)

        except Exception as e:
            self.verified.emit(False, str(e))

    def stop(self):
        self._is_running = False
        if self.proc:
            try:
                self.proc.terminate()
            except Exception:
                pass


class BiometricAuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._username = CURRENT_USER
        self._backup_enabled = backup_password_enabled()
        self.setWindowTitle("SLONE™ Enclave Biométrico")
        self.setFixedSize(460, 400)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setStyleSheet(AUTH_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(16)

        # Header con icono
        header_layout = QHBoxLayout()
        logo_lbl = QLabel()
        icon_path = _find_icon()
        if icon_path:
            pix = QPixmap(icon_path).scaled(44, 44, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(pix)
        header_layout.addWidget(logo_lbl)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_title = QLabel("SLONE™ SOVEREIGN ENCLAVE")
        lbl_title.setObjectName("HeaderTitle")
        lbl_sub = QLabel("Control de Acceso Biométrico")
        lbl_sub.setObjectName("SubTitle")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Divisor
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #1A1A22; max-height: 1px;")
        layout.addWidget(line)

        fingerprint_icon = QLabel("🖐️")
        fingerprint_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fingerprint_icon.setStyleSheet("font-size: 56px; margin: 10px 0;")
        layout.addWidget(fingerprint_icon)

        self.status_lbl = QLabel("Iniciando verificación de huella...")
        self.status_lbl.setObjectName("StatusLabel")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_lbl)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.retry_btn = QPushButton("Reintentar huella")
        self.retry_btn.clicked.connect(self._start_fingerprint)
        btn_layout.addWidget(self.retry_btn)
        self.pwd_btn = QPushButton("Usar contraseña")
        self.pwd_btn.clicked.connect(self._try_password)
        if self._backup_enabled:
            btn_layout.addWidget(self.pwd_btn)
        else:
            self.pwd_btn.hide()
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setObjectName("CancelBtn")
        self.cancel_btn.clicked.connect(self._on_cancel)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.auth_thread = None
        self._start_fingerprint()

    def _start_fingerprint(self):
        # Detén cualquier verificación previa y arranca una nueva
        if self.auth_thread is not None:
            try:
                self.auth_thread.stop()
            except Exception:
                pass
        self.retry_btn.setEnabled(False)
        self.setStyleSheet(AUTH_STYLE)
        self.status_lbl.setText("Coloca tu huella registrada en el sensor...")
        self.auth_thread = BiometricVerifyThread(self._username)
        self.auth_thread.status_update.connect(self._on_status)
        self.auth_thread.verified.connect(self._on_verified)
        self.auth_thread.start()

    def _on_status(self, text):
        self.status_lbl.setText(text)

    def _on_verified(self, success, message):
        if hasattr(self, "retry_btn"):
            self.retry_btn.setEnabled(True)
        if success:
            self.setStyleSheet(AUTH_STYLE + "QDialog { border: 2px solid #00E676; } #StatusLabel { color: #00E676; border-color: #00E676; }")
            self.status_lbl.setText("✓ ACCESO CONCEDIDO · BIOMETRÍA CONFIRMADA")
            QTimer.singleShot(600, self.accept)
        else:
            # No cerramos el diálogo: el usuario puede reintentar o usar contraseña.
            self.setStyleSheet(AUTH_STYLE + "QDialog { border: 2px solid #FF3344; } #StatusLabel { color: #FF3344; border-color: #FF3344; }")
            hint = " · usa «Usar contraseña»" if self._backup_enabled else " · vuelve a intentarlo"
            self.status_lbl.setText(f"✕ Huella no reconocida{hint}")

    def _try_password(self):
        from PyQt6.QtWidgets import QInputDialog, QLineEdit
        pwd, ok = QInputDialog.getText(
            self, "SLONE · Acceso de respaldo",
            f"Contraseña del sistema para «{self._username}»:",
            QLineEdit.EchoMode.Password,
        )
        if not (ok and pwd):
            return
        if verify_backup_password(self._username, pwd):
            self.setStyleSheet(AUTH_STYLE + "QDialog { border: 2px solid #00E676; } #StatusLabel { color: #00E676; border-color: #00E676; }")
            self.status_lbl.setText("✓ ACCESO CONCEDIDO · CONTRASEÑA VERIFICADA")
            QTimer.singleShot(600, self.accept)
        else:
            self.setStyleSheet(AUTH_STYLE + "QDialog { border: 2px solid #FF3344; } #StatusLabel { color: #FF3344; border-color: #FF3344; }")
            self.status_lbl.setText("✕ Contraseña incorrecta. Inténtalo de nuevo.")

    def _on_cancel(self):
        if self.auth_thread is not None:
            try:
                self.auth_thread.stop()
            except Exception:
                pass
        self.reject()

    def closeEvent(self, event):
        if self.auth_thread is not None:
            try:
                self.auth_thread.stop()
            except Exception:
                pass
        super().closeEvent(event)


def require_biometric_auth(username=None) -> bool:
    """Ejecuta la verificación (huella o contraseña de respaldo) por GUI.

    Retorna True si la identidad es válida.
    """
    dialog = BiometricAuthDialog()
    result = dialog.exec()
    return result == QDialog.DialogCode.Accepted

