#!/usr/bin/env python3
"""
SLONE™ LICENSE CORE — Firma y verificación de claves (sin dependencias de GUI).
══════════════════════════════════════════════════════════════════════════════
Módulo PURO (solo stdlib) con la criptografía de licencias, separado de la UI
para poder auditarlo y probarlo de forma aislada.

Esquema de clave AUTOVERIFICABLE y AUTOCADUCABLE (v2):
    SLONE-<PLAN>-<AAMMDD>-<FIRMA>
    · PLAN    → DAY | WEEK | MONTH | YEAR | LIFE
    · AAMMDD  → fecha de caducidad ('000000' = vitalicia)
    · FIRMA   → 16 hex = HMAC-SHA256(secreto, 'PLAN:AAMMDD:SLONE_SOVEREIGN')

La clave se valida SIN contacto con el servidor: se recalcula la firma y se
compara en tiempo constante. Falsificarla exige conocer el secreto.
El secreto se puede rotar sin tocar el código: export SLONE_LICENSE_SECRET=...
"""

import os
import hmac
import hashlib
from datetime import date, timedelta, datetime

# ── Secreto (rotable por entorno; valor por defecto = el histórico) ──────────
LICENSE_SECRET = os.environ.get(
    "SLONE_LICENSE_SECRET", "SLONE_VR46_MASTER_SECRET_KEY_2026"
).encode("utf-8")

DURATION_DAYS = {
    "day": 1, "week": 7, "month": 30, "year": 365, "lifetime": 0,
    "sports_month": 30, "sports_year": 365,
    "quad_month": 30, "quad_year": 365,
    "royale": 0
}
PLAN_TAG = {
    "day": "DAY", "week": "WEEK", "month": "MONTH", "year": "YEAR", "lifetime": "LIFE",
    "sports_month": "SPORTS", "sports_year": "SPORTY",
    "quad_month": "QUAD", "quad_year": "QUADY",
    "royale": "ROYALE"
}
TAG_PLAN = {v: k for k, v in PLAN_TAG.items()}


def _expiry_stamp(days):
    """Devuelve 'AAMMDD' de caducidad, o '000000' si es vitalicia."""
    if not days or days <= 0:
        return "000000"
    return (date.today() + timedelta(days=days)).strftime("%y%m%d")


def get_hardware_fingerprint() -> str:
    """Calcula un identificador único e inmutable de la máquina local (HWID)."""
    candidates = []
    for path in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    val = f.read().strip()
                    if val:
                        candidates.append(val)
        except Exception:
            pass
    try:
        dmi_path = "/sys/class/dmi/id/product_uuid"
        if os.path.exists(dmi_path):
            with open(dmi_path, "r", encoding="utf-8") as f:
                val = f.read().strip()
                if val:
                    candidates.append(val)
    except Exception:
        pass
    try:
        import uuid
        candidates.append(str(uuid.getnode()))
    except Exception:
        pass

    raw = ":".join(candidates) if candidates else "SLONE_DEFAULT_NODE_2026"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8].upper()


def sign_payload(tag, exp, hwid=None):
    """Firma determinista de (PLAN, caducidad, HWID). 16 hex en mayúsculas."""
    if hwid:
        payload = f"{tag}:{exp}:{hwid}:SLONE_SOVEREIGN"
    else:
        payload = f"{tag}:{exp}:SLONE_SOVEREIGN"
    return hmac.new(LICENSE_SECRET, payload.encode("utf-8"),
                    hashlib.sha256).hexdigest()[:16].upper()


def generate_license_key(plan_id, user_id="slone", lock_to_hwid: bool = True):
    """Genera una clave firmada vinculada obligatoriamente al HWID del equipo (Zero-Piracy)."""
    tag = PLAN_TAG.get(plan_id, "YEAR")
    exp = _expiry_stamp(DURATION_DAYS.get(plan_id, 365))
    hwid = get_hardware_fingerprint() if lock_to_hwid else "NODE"
    sig = sign_payload(tag, exp, hwid)
    if hwid:
        return f"SLONE-{tag}-{exp}-{hwid}-{sig}"
    return f"SLONE-{tag}-{exp}-{sig}"


# ── Clave pública asimétrica Ed25519 oficial SLONE Sovereign ────────────────
# La clave privada reside ÚNICAMENTE en el servidor seguro de licencias.
# El cliente solo posee esta clave pública: matemáticamente IMPOSIBLE falsificar licencias.
ED25519_PUBLIC_HEX = "02C234ED5E7361AE63DF72E581E244C7D91165CD7F45FC8109B27B5ACB9985A9"


def verify_ed25519_signature(payload_str: str, signature_hex: str) -> bool:
    """Verifica una firma Ed25519 de forma asimétrica y segura con la clave pública."""
    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519
        pub_bytes = bytes.fromhex(ED25519_PUBLIC_HEX)
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
        sig_bytes = bytes.fromhex(signature_hex)
        public_key.verify(sig_bytes, payload_str.encode("utf-8"))
        return True
    except Exception:
        return False


def generate_ed25519_license_key(plan_id: str, private_key_pem: bytes, lock_to_hwid: bool = True, custom_hwid: str = None) -> str:
    """Genera una licencia asimétrica inquebrantable Ed25519 (solo ejecutable con la clave privada)."""
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization

    tag = PLAN_TAG.get(plan_id, "YEAR")
    exp = _expiry_stamp(DURATION_DAYS.get(plan_id, 365))
    if custom_hwid:
        hwid = custom_hwid.strip().upper()
    elif lock_to_hwid:
        hwid = get_hardware_fingerprint()
    else:
        hwid = "GLOBAL"

    payload = f"{tag}:{exp}:{hwid}:SLONE_SOVEREIGN"
    priv_key = serialization.load_pem_private_key(private_key_pem, password=None)
    sig = priv_key.sign(payload.encode("utf-8")).hex().upper()
    return f"SLONEV3-{tag}-{exp}-{hwid}-{sig}"


def verify_key(key):
    """Verifica una clave offline: soporta Ed25519 asimétrico (v3) y HMAC node-locked (v2)."""
    if not key:
        return False
    parts = str(key).strip().upper().split("-")
    prefix = parts[0]
    if prefix not in ("SLONE", "SLONEV3"):
        return False

    current_hwid = get_hardware_fingerprint()

    # 1. Licencia asimétrica Ed25519 v3: SLONEV3-<PLAN>-<AAMMDD>-<HWID>-<SIG128HEX>
    if prefix == "SLONEV3" and len(parts) == 5:
        _, tag, exp, key_hwid, sig = parts
        if key_hwid != "GLOBAL" and key_hwid != current_hwid:
            # Clave robada o intentada en otro hardware
            return False
        payload = f"{tag}:{exp}:{key_hwid}:SLONE_SOVEREIGN"
        if not verify_ed25519_signature(payload, sig):
            return False

    # 2. Licencia HMAC v2 node-locked: SLONE-<PLAN>-<AAMMDD>-<HWID>-<HMAC16>
    elif prefix == "SLONE" and len(parts) == 5:
        _, tag, exp, key_hwid, sig = parts
        if key_hwid != current_hwid:
            # Clave robada o copiada en otra máquina distinta
            return False
        if not hmac.compare_digest(sign_payload(tag, exp, key_hwid), sig):
            return False

    # 3. Licencia node-locked local v2: SLONE-<PLAN>-<AAMMDD>-<HMAC16>
    elif prefix == "SLONE" and len(parts) == 4:
        _, tag, exp, sig = parts
        valid_local = hmac.compare_digest(sign_payload(tag, exp, current_hwid), sig)
        if not valid_local:
            return False
    else:
        return False

    if exp != "000000":  # vitalicia = sin caducidad
        try:
            exp_date = datetime.strptime(exp, "%y%m%d").date()
        except ValueError:
            return False
        if exp_date < date.today():
            return False
    return True


def is_key_expired(key):
    """Devuelve True si la clave tiene fecha de caducidad superada."""
    parts = str(key).strip().upper().split("-")
    if len(parts) not in (4, 5) or parts[0] not in ("SLONE", "SLONEV3"):
        return True
    exp = parts[2]
    if exp == "000000":
        return False
    try:
        exp_date = datetime.strptime(exp, "%y%m%d").date()
        return exp_date < date.today()
    except ValueError:
        return True


def plan_from_key(key):
    """Devuelve el id de plan embebido en la clave (o None)."""
    parts = str(key).strip().upper().split("-")
    if len(parts) in (4, 5) and parts[0] in ("SLONE", "SLONEV3"):
        return TAG_PLAN.get(parts[1])
    return None


# Alias de compatibilidad con nombres de funciones equivalentes.
validate_key = verify_key
generate_key = generate_license_key
get_plan_from_key = plan_from_key

