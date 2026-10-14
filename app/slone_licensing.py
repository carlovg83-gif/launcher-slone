#!/usr/bin/env python3
"""
SLONE™ MONETIZATION & SOVEREIGN LICENSING ENGINE v2.0
══════════════════════════════════════════════════════════════════════════
• Modelos de Licencia: FREE (Gratis con patrocinio) vs PREMIUM_VIP (Sovereign).
• Precios 'In-Crescendo' (Pase de 1 día con mayor precio unitario; tarifa anual óptima).
• Motor Ad-Blocker integrado: bloqueo total de trackers y anuncios en Premium.
• Claves de licencia criptográficas firmadas por HMAC-SHA256.
• Modo Maestro para desbloqueo automático del usuario propietario.
"""

import os
import sys
import json
import time
import hmac
import hashlib
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QLineEdit, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

# La criptografía de licencias vive en un módulo puro y auditable (sin GUI),
# para poder probarla de forma aislada y rotar el secreto sin tocar el código.
try:
    from slone_license_core import (
        LICENSE_SECRET, DURATION_DAYS,
        generate_license_key as core_generate_key,
        verify_key as core_verify_key,
    )
except ImportError:  # al importar como paquete: app.slone_licensing
    from app.slone_license_core import (
        LICENSE_SECRET, DURATION_DAYS,
        generate_license_key as core_generate_key,
        verify_key as core_verify_key,
    )

CONFIG_DIR = Path.home() / ".config/slocast"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
LICENSE_FILE = CONFIG_DIR / "license.json"

TIER_FREE = "FREE"
TIER_PREMIUM = "PREMIUM_VIP"

PRICING_PLANS = [
    {
        "id": "sports_month",
        "name": "⚽ Passion Sports Mensual",
        "price_eur": 3.99,
        "period": "1 mes (Digital)",
        "equiv_monthly": "3,99 €/mes",
        "badge": "INICIAL",
        "desc": "4K 60FPS, Audio-Sync radio dual, 2 pantallas y cupón 50% de descuento en la tienda de Merch."
    },
    {
        "id": "sports_year",
        "name": "🎁 Passion Sports Anual",
        "price_eur": 39.99,
        "period": "1 año (Con Regalo)",
        "equiv_monthly": "3,33 €/mes",
        "badge": "AHORRO 2 MESES",
        "desc": "Todo un año completo + Llavero de aluminio grabado a láser o pack vinilos de autor."
    },
    {
        "id": "quad_month",
        "name": "🔥 Quad-Stadium Pro Mensual",
        "price_eur": 7.99,
        "period": "1 mes (Digital)",
        "equiv_monthly": "7,99 €/mes",
        "badge": "PRO DIGITAL",
        "desc": "Multiview Stadium 4X, Turbo Shield Anti-cortes, 5 pantallas y cupón 50% de descuento en la tienda."
    },
    {
        "id": "quad_year",
        "name": "📦 Quad-Stadium Pro Anual (Best Seller)",
        "price_eur": 59.99,
        "period": "1 año (Welcome Pack)",
        "equiv_monthly": "4,99 €/mes",
        "badge": "MÁS ELEGIDO 80%",
        "desc": "1 año completo + Welcome Pack Pro (USB 128GB grabado láser + Llavero metálico + Carnet físico)."
    },
    {
        "id": "royale",
        "name": "👑 Royale Founders Pass",
        "price_eur": 149.00,
        "period": "Vitalicio (Lifetime)",
        "equiv_monthly": "0 €/mes perpetuo",
        "badge": "500 PLAZAS",
        "desc": "Acceso vitalicio, canal privado CEO, Royale Founder Box (Gorra/Camiseta, Carnet acero, USB 256GB)."
    },
    # Compatibilidad con claves legacy
    {"id": "day", "name": "⚡ Pase Flash", "price_eur": 1.99, "period": "1 día", "equiv_monthly": "1,99 €", "badge": "LEGACY", "desc": "Pase diario"},
    {"id": "week", "name": "🏁 Pase Semanal", "price_eur": 4.99, "period": "7 días", "equiv_monthly": "4,99 €", "badge": "LEGACY", "desc": "Pase semanal"},
    {"id": "month", "name": "👑 Suscripción Mensual Legacy", "price_eur": 9.99, "period": "1 mes", "equiv_monthly": "9,99 €", "badge": "LEGACY", "desc": "Pase mensual"},
    {"id": "year", "name": "💎 Pase Anual Legacy", "price_eur": 39.99, "period": "1 año", "equiv_monthly": "3,33 €", "badge": "LEGACY", "desc": "Pase anual"},
    {"id": "lifetime", "name": "🏆 Licencia Vitalicia Legacy", "price_eur": 79.99, "period": "Pago único", "equiv_monthly": "0 €", "badge": "LEGACY", "desc": "Vitalicio legacy"}
]

class LicenseManager:
    def __init__(self):
        self.tier = TIER_PREMIUM  # Por defecto activo en entorno maestro
        self.license_key = ""
        self.expires_at = None
        self.plan_id = "lifetime"
        self._load_license()

    def _load_license(self):
        # Validación criptográfica estricta: nunca confiar en la variable USER del sistema
        if LICENSE_FILE.exists():
            try:
                data = json.loads(LICENSE_FILE.read_text(encoding="utf-8"))
                key = data.get("key", "")
                if self.validate_key(key):
                    self.tier = data.get("tier", TIER_FREE)
                    self.plan_id = data.get("plan_id", "month")
                    self.expires_at = data.get("expires_at")
                    # Comprobar expiración
                    if self.expires_at and time.time() > self.expires_at:
                        self.tier = TIER_FREE
                else:
                    self.tier = TIER_FREE
            except Exception:
                self.tier = TIER_FREE
        else:
            self.tier = TIER_FREE

    def save_license(self, key: str, tier: str, plan_id: str,
                     duration_days: int = 365, user_id: str = "slone"):
        self.license_key = key
        self.tier = tier
        self.plan_id = plan_id
        self.expires_at = time.time() + (duration_days * 86400) if duration_days > 0 else None

        data = {
            "key": key,
            "tier": tier,
            "plan_id": plan_id,
            "user_id": user_id,
            "expires_at": self.expires_at,
            "activated_at": time.time()
        }
        LICENSE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def is_premium(self) -> bool:
        if self.expires_at and time.time() > self.expires_at:
            self.tier = TIER_FREE
            return False
        return self.tier == TIER_PREMIUM

    def generate_license_key(self, plan_id: str, user_id: str = "slone") -> str:
        # Clave AUTOVERIFICABLE y AUTOCADUCABLE: SLONE-<PLAN>-<FECHA>-<FIRMA>
        return core_generate_key(plan_id, user_id)

    def validate_key(self, key: str) -> bool:
        # Verificación criptográfica REAL: recalcula la firma HMAC y comprueba
        # caducidad. Rechaza cualquier clave falsificada.
        return core_verify_key(key)

    def set_free_tier(self):
        self.tier = TIER_FREE
        self.plan_id = "free"
        if LICENSE_FILE.exists():
            LICENSE_FILE.unlink(missing_ok=True)

    def set_premium_tier(self, plan_id: str = "lifetime"):
        key = self.generate_license_key(plan_id)
        duration = DURATION_DAYS.get(plan_id, 365)
        self.save_license(key, TIER_PREMIUM, plan_id, duration)


# ──────────────────────────────────────────────────────────────
#  DIÁLOGO DE MONETIZACIÓN Y SELECCIÓN DE PLANES VIP
# ──────────────────────────────────────────────────────────────
class UpgradeDialog(QDialog):
    plan_selected = pyqtSignal(str)

    def __init__(self, lic_mgr: LicenseManager, parent=None):
        super().__init__(parent)
        self.lic_mgr = lic_mgr
        self.setWindowTitle("SLONE Sovereign — Planes y Licencias VIP")
        self.resize(600, 680)
        self.setStyleSheet("""
            QDialog {
                background-color: #050505;
                border: 2px solid #E3FF00;
                border-radius: 14px;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            QRadioButton {
                color: #FFFFFF;
                font-weight: 800;
                font-size: 13px;
                padding: 10px;
                border: 1px solid #1C1C1C;
                border-radius: 8px;
                background-color: #0A0A0A;
                margin-bottom: 6px;
            }
            QRadioButton:hover {
                border-color: #444444;
                background-color: #111111;
            }
            QRadioButton:checked {
                border-color: #E3FF00;
                background-color: #141400;
                color: #E3FF00;
            }
            #BtnBuy {
                background-color: #E3FF00;
                color: #000000;
                font-weight: 900;
                font-size: 14px;
                border-radius: 8px;
                padding: 12px 24px;
                border: none;
            }
            #BtnBuy:hover {
                background-color: #F0FF4D;
            }
            #BtnMaster {
                background-color: #111116;
                color: #E3FF00;
                border: 1px solid #E3FF00;
                font-weight: 800;
                font-size: 12px;
                border-radius: 8px;
                padding: 10px 18px;
            }
            #BtnMaster:hover {
                background-color: #E3FF00;
                color: #000000;
            }
            #KeyInput {
                background-color: #0B0B0B;
                color: #E3FF00;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 8px 12px;
                font-family: monospace;
                font-size: 13px;
            }
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(12)

        # Header
        h_box = QVBoxLayout()
        t1 = QLabel("👑 SLONE<span style='color:#E3FF00'>.SOVEREIGN VIP</span>")
        t1.setTextFormat(Qt.TextFormat.RichText)
        t1.setStyleSheet("font-size: 22px; font-weight: 900; letter-spacing: 1px;")
        t2 = QLabel("Desbloquea Multi-Audio Satélite, Cero Cortes, Kill-Switch VPN y Ad-Blocker Total.")
        t2.setStyleSheet("color: #888888; font-size: 12px;")
        h_box.addWidget(t1)
        h_box.addWidget(t2)
        lay.addLayout(h_box)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #1A1A1A; max-height: 1px;")
        lay.addWidget(sep)

        # Selector de Planes
        self.radio_group = QButtonGroup(self)
        self.radios = {}

        for idx, plan in enumerate(PRICING_PLANS):
            r = QRadioButton(
                f"{plan['name']} — {plan['price_eur']:.2f} €  ({plan['equiv_monthly']})\n"
                f"  ▸ {plan['desc']}"
            )
            self.radios[plan['id']] = r
            self.radio_group.addButton(r, idx)
            lay.addWidget(r)
            if plan['id'] == "year":
                r.setChecked(True)

        # Activación por Código de Licencia
        key_box = QHBoxLayout()
        self.txt_key = QLineEdit()
        self.txt_key.setObjectName("KeyInput")
        self.txt_key.setPlaceholderText("Introduce tu clave (SLONE-XXXX-XXXX-...)")
        btn_activate = QPushButton("Activar Clave")
        btn_activate.setStyleSheet("background: #181818; color: #FFF; font-weight: 800; padding: 8px 16px; border-radius: 6px; border: 1px solid #333;")
        btn_activate.clicked.connect(self._activate_custom_key)
        key_box.addWidget(self.txt_key)
        key_box.addWidget(btn_activate)
        lay.addLayout(key_box)

        # Botones de Acción
        btn_row = QHBoxLayout()
        btn_free_test = QPushButton("Modo Gratis (Prueba)")
        btn_free_test.setStyleSheet("background: #0A0A0A; color: #888; border: 1px solid #222; padding: 10px; border-radius: 6px; font-weight: 700;")
        btn_free_test.clicked.connect(self._set_free)

        btn_master = QPushButton("🔑 Desbloqueo Maestro (slone)")
        btn_master.setObjectName("BtnMaster")
        btn_master.clicked.connect(self._set_master)

        btn_buy = QPushButton("⭐ Suscribirse / Activar")
        btn_buy.setObjectName("BtnBuy")
        btn_buy.clicked.connect(self._confirm_purchase)

        btn_row.addWidget(btn_free_test)
        btn_row.addWidget(btn_master)
        btn_row.addWidget(btn_buy)
        lay.addLayout(btn_row)

    def _confirm_purchase(self):
        selected_id = "year"
        for pid, r in self.radios.items():
            if r.isChecked():
                selected_id = pid
                break

        plan = next((p for p in PRICING_PLANS if p["id"] == selected_id), PRICING_PLANS[3])
        self.lic_mgr.set_premium_tier(selected_id)
        QMessageBox.information(
            self,
            "Suscripción Activada",
            f"¡Enhorabuena! Has activado {plan['name']}.\n"
            f"Tarifa: {plan['price_eur']:.2f} €.\n\n"
            f"Todas las funciones Premium VIP, VPN Shield y Ad-Blocker están ahora activas."
        )
        self.accept()

    def _activate_custom_key(self):
        key = self.txt_key.text().strip()
        if self.lic_mgr.validate_key(key):
            self.lic_mgr.save_license(key, TIER_PREMIUM, "custom_key", 365)
            QMessageBox.information(self, "Licencia Válida", "Licencia SLONE Sovereign activada con éxito.")
            self.accept()
        else:
            QMessageBox.warning(self, "Clave Inválida", "La clave introducida no tiene el formato correcto de SLONE OS.")

    def _set_free(self):
        self.lic_mgr.set_free_tier()
        QMessageBox.information(self, "Modo Free", "Has cambiado al plan Gratis (con anuncios y funciones estándar).")
        self.accept()

    def _set_master(self):
        try:
            from slone_auth import require_biometric_auth
            if not require_biometric_auth():
                QMessageBox.warning(self, "Acceso Denegado", "Autenticación biométrica o contraseña maestra requerida para desbloqueo.")
                return
        except Exception as e:
            QMessageBox.critical(self, "Error de Seguridad", f"No se pudo verificar el enclave de identidad: {e}")
            return

        self.lic_mgr.set_premium_tier("lifetime")
        QMessageBox.information(self, "Modo Maestro", "Identidad verificada por sensor biométrico: Acceso Maestro Soberano activado.")
        self.accept()
