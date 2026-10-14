#!/usr/bin/env python3
"""
Autenticacion SLONE: huella dactilar primero, contrasena PAM si falla.
Dependencias: fprintd   python3-pam   python3-pyqt6
"""
import subprocess
import getpass
import sys


def desbloquear_slone(usuario=None):
    """
    Devuelve True si el usuario se autentica correctamente.
    Orden: 1) huella dactilar  2) dialogo Qt + PAM  3) terminal + PAM
    """
    if usuario is None:
        usuario = getpass.getuser()

    # ---- 1. HUELLA DACTILAR ----------------------------------------
    try:
        r = subprocess.run(
            ["fprintd-verify", usuario],
            capture_output=True,
            text=True,
            timeout=15,             # corregido: de 12 a 15 segundos
        )
        salida = r.stdout + r.stderr
        if "verify-match" in salida:
            return True
        # verify-no-match o timeout: cae al metodo siguiente
    except subprocess.TimeoutExpired:
        pass                        # sin respuesta -> pedir contrasena
    except FileNotFoundError:
        pass                        # fprintd-verify no instalado -> pedir contrasena

    # ---- 2. CONTRASENA: dialogo grafico Qt -------------------------
    pwd = None
    ok  = False

    try:
        from PyQt6.QtWidgets import QApplication, QInputDialog, QLineEdit
        # CORRECCION: QInputDialog necesita una QApplication activa
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)   # CORRECCION: sys importado arriba

        pwd, ok = QInputDialog.getText(
            None,
            "SLONE - Autenticacion",
            "Contrasena del sistema:",
            QLineEdit.EchoMode.Password,
        )
    except ImportError:
        # PyQt6 no instalado: pedir por terminal como fallback
        try:
            pwd = getpass.getpass("Contrasena del sistema: ")
            ok  = True
        except (EOFError, KeyboardInterrupt):
            return False

    if not (ok and pwd):
        return False

    # ---- 3. VERIFICAR CON PAM -------------------------------------
    try:
        import pam                          # CORRECCION: import dentro de funcion
        autenticador = pam.pam()
        # CORRECCION: service="su" en lugar de "login" (funciona sin privilegios root)
        return autenticador.authenticate(usuario, pwd, service="su")
    except ImportError:
        print("[ERROR] python3-pam no instalado.")
        print("Ejecuta: sudo dnf install -y python3-pam")
        return False


if __name__ == "__main__":
    resultado = desbloquear_slone()
    if resultado:
        print("Autenticacion correcta.")
    else:
        print("Autenticacion fallida.")
