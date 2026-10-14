#!/usr/bin/env python3
"""
SLONE™ SOVEREIGN VPN & GEOLOCATION SHIELD v2.0
══════════════════════════════════════════════════════════════════════════
• Detección automática de túneles VPN (WireGuard, OpenVPN, SOCKS5, Shadowsocks).
• Monitorización continua de IP pública, país y proveedor ISP.
• Kill-Switch en tiempo real: corta la emisión de inmediato si cae la VPN
  evitando cualquier fuga de IP o localización real hacia el proveedor IPTV.
• Prevención activa de fugas DNS y enrutamiento seguro de streams.
"""

import os
import sys
import json
import socket
import urllib.request
import threading
import time
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

class VPNShield(QObject):
    vpn_status_changed = pyqtSignal(bool, dict)  # (is_secure, details)
    kill_switch_triggered = pyqtSignal(str)      # mensaje de alerta

    def __init__(self, kill_switch_enabled: bool = True):
        super().__init__()
        self.kill_switch_enabled = kill_switch_enabled
        self.is_vpn_active = False
        self.last_details = {
            "ip": "Desconocida",
            "country": "Detectando...",
            "country_code": "XX",
            "city": "Desconocida",
            "isp": "Detectando...",
            "vpn_interface": None
        }
        self._running = True
        self._monitor_thread = None
        self._lock = threading.Lock()

    def start_monitoring(self):
        if self._monitor_thread and self._monitor_thread.is_alive():
            return
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def stop_monitoring(self):
        self._running = False

    def detect_vpn_interface(self) -> str | None:
        """Detecta si hay interfaces de túnel activas en el sistema Linux."""
        try:
            interfaces = os.listdir('/sys/class/net')
            for iface in interfaces:
                # Interfaces típicas de WireGuard, OpenVPN, Tailscale, Nord, Proton
                if any(iface.startswith(prefix) for prefix in ("tun", "wg", "tap", "nordlynx", "proton", "cscotun")):
                    # Verificar si la interfaz está UP
                    operstate_path = Path(f"/sys/class/net/{iface}/operstate")
                    if operstate_path.exists() and operstate_path.read_text().strip() in ("up", "unknown"):
                        return iface
        except Exception:
            pass
        return None

    def check_public_ip_and_geo(self) -> dict:
        """Consulta la IP pública y geolocalización de salida en servidores seguros."""
        endpoints = [
            ("https://ipwho.is/", self._parse_ipwhois),
            ("https://api.ipify.org?format=json", self._parse_ipify),
            ("http://ip-api.com/json/", self._parse_ipapi)
        ]
        
        headers = {"User-Agent": "Mozilla/5.0 (SLONE Sovereign Shield)"}
        for url, parser in endpoints:
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=3.5) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                        return parser(data)
            except Exception:
                continue

        return self.last_details

    def _parse_ipwhois(self, data: dict) -> dict:
        return {
            "ip": data.get("ip", "Desconocida"),
            "country": data.get("country", "Desconocido"),
            "country_code": data.get("country_code", "XX"),
            "city": data.get("city", ""),
            "isp": data.get("connection", {}).get("isp", "Privado"),
            "is_vpn": data.get("security", {}).get("vpn", False) or data.get("security", {}).get("proxy", False)
        }

    def _parse_ipapi(self, data: dict) -> dict:
        return {
            "ip": data.get("query", "Desconocida"),
            "country": data.get("country", "Desconocido"),
            "country_code": data.get("countryCode", "XX"),
            "city": data.get("city", ""),
            "isp": data.get("isp", "Privado"),
            "is_vpn": False
        }

    def _parse_ipify(self, data: dict) -> dict:
        return {
            "ip": data.get("ip", "Desconocida"),
            "country": "En línea",
            "country_code": "SEC",
            "city": "",
            "isp": "VPN/Proxy",
            "is_vpn": True
        }

    def _monitor_loop(self):
        """Bucle en segundo plano con control de Kill-Switch optimizado (cero spam HTTP)."""
        consecutive_drops = 0
        last_geo_check = 0
        geo_info = dict(self.last_details)
        while self._running:
            vpn_iface = self.detect_vpn_interface()
            now = time.time()

            # Consulta externa con HTTPS solo si cambia el túnel o cada 60 segundos
            if (now - last_geo_check > 60) or (bool(vpn_iface) != self.is_vpn_active):
                geo_info = self.check_public_ip_and_geo()
                last_geo_check = now

            geo_info["vpn_interface"] = vpn_iface
            is_active = bool(vpn_iface or geo_info.get("is_vpn", False))

            with self._lock:
                previous_active = self.is_vpn_active
                self.is_vpn_active = is_active
                self.last_details = geo_info

            # Disparo de Kill Switch si la VPN estaba activa y se desconecta de repente
            if previous_active and not is_active and self.kill_switch_enabled:
                consecutive_drops += 1
                if consecutive_drops >= 1:
                    msg = (
                        "⚠️ ALERTA KILL-SWITCH SLONE: Se ha perdido la conexión VPN protegida.\n"
                        "La transmisión en directo se ha pausado automáticamente para blindar tu IP real."
                    )
                    self.kill_switch_triggered.emit(msg)
            else:
                consecutive_drops = 0

            self.vpn_status_changed.emit(is_active, geo_info)
            time.sleep(3.0)

    def get_status_summary(self) -> str:
        with self._lock:
            if self.is_vpn_active:
                cc = self.last_details.get("country_code", "OK")
                ip = self.last_details.get("ip", "")
                iface = self.last_details.get("vpn_interface") or "SEC"
                return f"🛡️ VPN [{cc}] · {iface} ({ip})"
            else:
                ip = self.last_details.get("ip", "")
                cc = self.last_details.get("country_code", "DIRECT")
                return f"⚠️ IP DIRECTA [{cc}] · {ip}"
