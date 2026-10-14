#!/usr/bin/env bash
# Instala el servicio PAM dedicado de SLONE (contraseña de respaldo sin huella).
# Uso:  bash scripts/install_pam_service.sh
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)/config/pam.d/slone"

if [ ! -f "$SRC" ]; then
  echo "No encuentro $SRC" >&2
  exit 1
fi

sudo install -m 0644 "$SRC" /etc/pam.d/slone
echo "✔ Instalado /etc/pam.d/slone (verificación por contraseña, sin sensor de huellas)."
echo "  SLOCAST ya puede usar la contraseña de respaldo sin esperar la huella."
