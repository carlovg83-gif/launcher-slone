#!/usr/bin/env python3
"""
SLONE™ SECURITY SHIELD — Control total y blindaje anti-intrusión.
══════════════════════════════════════════════════════════════════════════
• Escudo maestro conmutable (config/slone_control.json → 'seguridad').
• Bind a 127.0.0.1 por defecto; el acceso LAN es opt-in con token.
• Rate-limit por IP, bloqueo de patrones de ataque, user-agents y métodos.
• Baneo automático tras abusos reiterados y registro en config/security.log.
No requiere dependencias externas ni privilegios de root.
"""

import json
import time
import secrets
import threading
import urllib.parse
from collections import defaultdict, deque
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_DIR / "config" / "slone_control.json"
LOG_PATH = PROJECT_DIR / "config" / "security.log"

DEFAULT_POLICY = {
    "escudo_activo": True,
    "permitir_lan": False,          # por seguridad: solo 127.0.0.1 hasta activarlo
    "requiere_token_lan": True,
    "max_peticiones_por_min": 120,
    "bloquear_tras_abusos": 5,
    "minutos_de_bloqueo": 15,
}

# Fragmentos típicos de explotación / path-traversal / inyección.
SUSPICIOUS = ("..", "//", "\\", "%2e", "%2f", "%5c", "\x00", "%00",
              "etc/passwd", "etc/shadow", "<script", "union select", "select%20",
              "cmd.exe", "/bin/sh", "/bin/bash")
# User-agents de escáneres y herramientas de ataque habituales.
BAD_AGENTS = ("sqlmap", "nikto", "nmap", "masscan", "zgrab", "nuclei",
              "hydra", "dirbuster", "gobuster", "wpscan", "burpsuite")


def check_environment_integrity() -> tuple:
    """Detecta inyección de memoria, LD_PRELOAD o procesos de depuración activos."""
    import os
    if os.environ.get("LD_PRELOAD"):
        return False, "Inyección de librerías LD_PRELOAD detectada"
    status_path = Path("/proc/self/status")
    if status_path.exists():
        try:
            for line in status_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("TracerPid:"):
                    tracer = int(line.split(":")[1].strip())
                    if tracer != 0:
                        return False, f"Proceso bajo depuración hostil (TracerPid={tracer})"
        except Exception:
            pass
    return True, "ok"


def load_policy() -> dict:
    try:
        pol = json.loads(CONFIG_PATH.read_text(encoding="utf-8")).get("seguridad", {})
    except Exception:
        pol = {}
    merged = dict(DEFAULT_POLICY)
    merged.update({k: v for k, v in pol.items() if v is not None})
    return merged


def save_policy(updates: dict) -> bool:
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8")) if CONFIG_PATH.exists() else {}
    except Exception:
        data = {}
    sec = data.get("seguridad", {}) or {}
    sec.update(updates)
    data["seguridad"] = sec
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception:
        return False


def is_local_ip(ip: str) -> bool:
    return ip in ("127.0.0.1", "::1", "localhost")


def _log(line: str):
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {line}\n")
    except Exception:
        pass


class RateLimiter:
    """Token-bucket simple por IP (ventana de 60 s)."""
    def __init__(self, max_per_min: int):
        self.max_per_min = max(1, int(max_per_min))
        self._hits = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, ip: str) -> bool:
        now = time.time()
        with self._lock:
            dq = self._hits[ip]
            while dq and now - dq[0] > 60:
                dq.popleft()
            if len(dq) >= self.max_per_min:
                return False
            dq.append(now)
            return True


class SecurityShield:
    def __init__(self):
        self.policy = load_policy()
        self.limiter = RateLimiter(self.policy["max_peticiones_por_min"])
        self._bans = {}                 # ip -> ts de desbaneo
        self._abuse = defaultdict(int)
        self._recent = deque(maxlen=200)
        self._lock = threading.Lock()
        self._blocked_total = 0

    def reload(self):
        self.policy = load_policy()
        self.limiter = RateLimiter(self.policy["max_peticiones_por_min"])

    @property
    def active(self) -> bool:
        return bool(self.policy.get("escudo_activo", True))

    @property
    def bind_host(self) -> str:
        return "0.0.0.0" if self.policy.get("permitir_lan") else "127.0.0.1"

    def token(self) -> str:
        try:
            tok = json.loads(CONFIG_PATH.read_text(encoding="utf-8")).get("seguridad", {}).get("lan_token")
            if tok:
                return tok
        except Exception:
            pass
        return self.rotate_token()

    def rotate_token(self) -> str:
        tok = secrets.token_urlsafe(16)
        save_policy({"lan_token": tok})
        return tok

    def is_banned(self, ip: str) -> bool:
        with self._lock:
            until = self._bans.get(ip)
            if until is None:
                return False
            if time.time() >= until:
                self._bans.pop(ip, None)
                return False
            return True

    def _ban(self, ip: str, reason: str):
        minutes = int(self.policy.get("minutos_de_bloqueo", 15))
        with self._lock:
            self._bans[ip] = time.time() + minutes * 60
        _log(f"[BAN {minutes}m] {ip} :: {reason}")

    def _deny(self, ip: str, path: str, reason: str):
        with self._lock:
            self._abuse[ip] += 1
            self._blocked_total += 1
            self._recent.append((time.time(), ip, reason, path))
            abuse = self._abuse[ip]
        _log(f"[BLOQUEADO] {ip} :: {reason} :: {path}")
        if abuse >= int(self.policy.get("bloquear_tras_abusos", 5)):
            self._ban(ip, f"abusos reiterados ({abuse})")
        return False, reason

    def allow(self, ip: str, path: str, method: str = "GET",
              user_agent: str = "", token: str = None, sensitive: bool = True) -> tuple:
        """Devuelve (permitido, motivo). 'sensitive' exige token en acceso LAN."""
        if not self.active:
            return True, "escudo desactivado"
        if self.is_banned(ip):
            return self._deny(ip, path, "IP baneada por abusos")
        lan_ok = bool(self.policy.get("permitir_lan"))
        if not lan_ok and not is_local_ip(ip):
            return self._deny(ip, path, "acceso externo bloqueado (modo solo-local)")
        if sensitive and lan_ok and not is_local_ip(ip) and self.policy.get("requiere_token_lan"):
            if token != self.token():
                return self._deny(ip, path, "token LAN ausente o inválido")
        if method not in ("GET", "HEAD"):
            return self._deny(ip, path, f"método no permitido: {method}")
        # Decodificación recursiva contra ataques de doble encoding URL (%252e%252e -> %2e%2e -> ..)
        decoded = path or ""
        for _ in range(3):
            new_decoded = urllib.parse.unquote(decoded)
            if new_decoded == decoded:
                break
            decoded = new_decoded
        low = decoded.lower()
        if any(tok in low for tok in SUSPICIOUS):
            return self._deny(ip, path, "patrón de ataque o path-traversal en la ruta")
        ua = (user_agent or "").lower()
        if any(bad in ua for bad in BAD_AGENTS):
            return self._deny(ip, path, f"user-agent sospechoso: {user_agent[:40]}")
        if not self.limiter.check(ip):
            return self._deny(ip, path, "rate-limit excedido")
        return True, "ok"

    def stats(self) -> dict:
        with self._lock:
            return {
                "escudo_activo": self.active,
                "permitir_lan": bool(self.policy.get("permitir_lan")),
                "bind": self.bind_host,
                "ips_baneadas": len(self._bans),
                "bloqueos_totales": self._blocked_total,
                "max_peticiones_por_min": self.policy.get("max_peticiones_por_min"),
            }

    def recent_blocks(self, limit: int = 15):
        with self._lock:
            items = list(self._recent)[-limit:]
        return list(reversed(items))


# Instancia global compartida por el relay y el webhook.
SHIELD = SecurityShield()
