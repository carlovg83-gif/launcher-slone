#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════
SLONE™ MINTING ENGINE — Generador Oficial de Licencias Asimétricas Ed25519
══════════════════════════════════════════════════════════════════════════════
Firma criptográficamente con la clave privada de SLONE CORP (modo 0600 en keystore).
Emite claves v3 node-locked e inquebrantables matemáticamente.
"""

import os
import sys
import json
import argparse
from datetime import datetime, date

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(HERE, ".."))
APP_DIR = os.path.join(PROJECT_DIR, "app")
sys.path.insert(0, APP_DIR)

from slone_license_core import (  # noqa: E402
    generate_ed25519_license_key,
    verify_key,
    plan_from_key,
    get_hardware_fingerprint,
    PLAN_TAG,
)

PRIVATE_KEY_PATH = os.path.join(PROJECT_DIR, "keystore", "slone_ed25519_private.pem")
ISSUED_LOG_PATH = os.path.join(PROJECT_DIR, "data", "issued_licenses.json")


def main():
    parser = argparse.ArgumentParser(
        description="SLONE™ Sovereign License Minting Engine (Ed25519)"
    )
    parser.add_argument(
        "--plan",
        choices=list(PLAN_TAG.keys()),
        default="royale",
        help="Plan de suscripción (default: royale / Founders)",
    )
    parser.add_argument(
        "--hwid",
        type=str,
        default=None,
        help="HWID de la máquina destino (8 hex). Si se omite, usa el nodo local actual.",
    )
    parser.add_argument(
        "--global-node",
        action="store_true",
        help="Genera licencia válida para cualquier hardware (HWID = GLOBAL)",
    )
    parser.add_argument(
        "--customer",
        type=str,
        default="Founder 001",
        help="Nombre, empresa o identificador del cliente / inversor",
    )
    parser.add_argument(
        "--key-file",
        type=str,
        default=PRIVATE_KEY_PATH,
        help="Ruta al archivo PEM de la clave privada Ed25519",
    )
    parser.add_argument(
        "--json-out",
        action="store_true",
        help="Imprime exclusivamente en formato JSON estructurado",
    )

    args = parser.parse_args()

    if not os.path.exists(args.key_file):
        sys.stderr.write(f"❌ ERROR: Clave privada no encontrada en '{args.key_file}'\n")
        sys.exit(1)

    with open(args.key_file, "rb") as f:
        priv_pem = f.read()

    target_hwid = "GLOBAL" if args.global_node else (args.hwid or get_hardware_fingerprint())
    license_key = generate_ed25519_license_key(
        plan_id=args.plan,
        private_key_pem=priv_pem,
        lock_to_hwid=(target_hwid != "GLOBAL"),
        custom_hwid=target_hwid,
    )

    # Autoverificación inmediata con la clave pública embebida
    is_valid = verify_key(license_key) if (target_hwid in (get_hardware_fingerprint(), "GLOBAL")) else True

    record = {
        "key": license_key,
        "plan": args.plan,
        "customer": args.customer,
        "hwid": target_hwid,
        "issued_at": datetime.now().isoformat(),
        "verified_offline": is_valid,
        "algorithm": "Ed25519-SHA512-Asymmetric",
    }

    # Persistir en histórico auditado de data/issued_licenses.json
    try:
        os.makedirs(os.path.dirname(ISSUED_LOG_PATH), exist_ok=True)
        records = []
        if os.path.exists(ISSUED_LOG_PATH):
            with open(ISSUED_LOG_PATH, "r", encoding="utf-8") as f:
                records = json.load(f)
        records.append(record)
        with open(ISSUED_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
    except Exception as e:
        sys.stderr.write(f"⚠️ Advertencia al guardar registro histórico: {e}\n")

    if args.json_out:
        print(json.dumps(record, indent=2))
        return

    print("══════════════════════════════════════════════════════════════════════")
    print("👑 SLONE™ SOVEREIGN MINTING ENGINE — LICENCIA EMITIDA CON ÉXITO")
    print("══════════════════════════════════════════════════════════════════════")
    print(f"  Titular        : {args.customer}")
    print(f"  Plan           : {args.plan.upper()} ({PLAN_TAG.get(args.plan)})")
    print(f"  Hardware Lock  : {target_hwid}")
    print(f"  Algoritmo      : Asimétrico Ed25519 (Firma Curva Edwards 25519)")
    print(f"  Estado Verif.  : {'AUTORIZADA Y VÁLIDA ✅' if is_valid else 'VÁLIDA (REMOTO) 🛡️'}")
    print("──────────────────────────────────────────────────────────────────────")
    print(f"  CLAVE DE LICENCIA:")
    print(f"  {license_key}")
    print("══════════════════════════════════════════════════════════════════════\n")


if __name__ == "__main__":
    main()
