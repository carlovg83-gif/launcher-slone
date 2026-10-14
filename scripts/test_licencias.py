#!/usr/bin/env python3
"""
Pruebas del núcleo de licencias SLONE (sin GUI, sin dependencias externas).
Ejecutar:  python3 scripts/test_licencias.py
"""
import os
import sys
import hmac
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "app"))

from slone_license_core import (  # noqa: E402
    generate_license_key, verify_key, sign_payload, plan_from_key,
    LICENSE_SECRET,
)

failures = []


def check(name, cond):
    print(("  ✅ " if cond else "  ❌ ") + name)
    if not cond:
        failures.append(name)


print("SLONE — pruebas del núcleo de licencias\n")

check("formato y validez de una clave del plan 'year'", verify_key(generate_license_key("year")))
check("clave vitalicia válida y sin caducidad", verify_key(generate_license_key("lifetime")))
check("el plan se puede leer de la clave", plan_from_key(generate_license_key("month")) == "month")

# ── Rechazos (anti-falsificación) ────────────────────────────────────────────
check("rechaza 'SLONE-AAAA-BBBB-CCCC' (no firmada)", not verify_key("SLONE-AAAA-BBBB-CCCC"))
check("rechaza firma manipulada", not verify_key("SLONE-YEAR-991231-DEADBEEFDEADBEEF"))
check("rechaza cadena vacía y None", not verify_key("") and not verify_key(None))

# Clave bien firmada pero con fecha de caducidad en el pasado.
expired = "SLONE-YEAR-200101-" + sign_payload("YEAR", "200101")
check("rechaza clave CADUCADA (bien firmada)", not verify_key(expired))

# ── Coherencia de la firma con HMAC-SHA256 ──────────────────────────────────
k = generate_license_key("year")
_, tag, exp, sig = k.split("-")
expected = hmac.new(LICENSE_SECRET, f"{tag}:{exp}:SLONE_SOVEREIGN".encode(),
                    hashlib.sha256).hexdigest()[:16].upper()
check("firma = HMAC-SHA256(secreto, 'PLAN:FECHA:SLONE_SOVEREIGN')", sig == expected)

# ── Pruebas de Criptografía Asimétrica Ed25519 (v3) ──────────────────────────
priv_path = os.path.join(HERE, "..", "keystore", "slone_ed25519_private.pem")
if os.path.exists(priv_path):
    with open(priv_path, "rb") as f:
        priv_pem = f.read()
    from slone_license_core import generate_ed25519_license_key, get_hardware_fingerprint

    hwid = get_hardware_fingerprint()
    k_v3 = generate_ed25519_license_key("royale", priv_pem, lock_to_hwid=True)
    check("formato y validez de clave Ed25519 v3 (ROYALE)", verify_key(k_v3))
    check("el plan de clave v3 se extrae correctamente", plan_from_key(k_v3) == "royale")

    # Clave v3 vinculada a otro HWID debe fallar
    k_v3_alien = generate_ed25519_license_key("royale", priv_pem, lock_to_hwid=True, custom_hwid="DEADBEEF")
    check("rechaza clave v3 vinculada a HWID ajeno (anti-robo)", not verify_key(k_v3_alien))

    # Clave v3 con firma falsificada debe fallar
    fake_sig = "A" * 128
    k_v3_tampered = f"SLONEV3-ROYALE-000000-{hwid}-{fake_sig}"
    check("rechaza clave v3 con firma Ed25519 manipulada", not verify_key(k_v3_tampered))

    # Clave global (no atada a HWID)
    k_v3_global = generate_ed25519_license_key("year", priv_pem, lock_to_hwid=False)
    check("clave v3 GLOBAL válida en cualquier nodo", verify_key(k_v3_global))

print()
if failures:
    print(f"FALLOS ({len(failures)}): " + ", ".join(failures))
    sys.exit(1)
print("TODO OK ✅")

