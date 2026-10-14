#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
#  SLONE VAULT · Lanzador cómodo de la Bóveda Soberana
#  Uso:  slone_vault.sh <init|unlock|lock|status|recover|twofa|tpm|add|migrate|restore|doctor|help> [...]
#  Ej.:  slone_vault.sh unlock          → huella + contraseña + 2FA
#        slone_vault.sh lock            → cierra la bóveda
#        slone_vault.sh add ~/Documentos/secreto.pdf
#        slone_vault.sh migrate --dry-run   → simula la migración a la bóveda
# ──────────────────────────────────────────────────────────────
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${SLONE_PYTHON:-python3}"

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "⛔ No encuentro '$PY'. Instala Python 3 o define SLONE_PYTHON." >&2
  exit 1
fi

exec "$PY" "$DIR/scripts/slone_vault.py" "$@"
