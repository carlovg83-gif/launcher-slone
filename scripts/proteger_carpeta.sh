#!/usr/bin/env zsh
# ──────────────────────────────────────────────────────────────
#  SLONE™ OS — Bloqueo y Blindaje de Permisos de Carpeta
#  Restringe el acceso exclusivamente al usuario 'slone'
# ──────────────────────────────────────────────────────────────
set -e

SCRIPT_DIR="${0:A:h}"
DIR="${1:-${SCRIPT_DIR:h}}"

echo "🔒 [SLONE SECURITY] Aplicando blindaje estricto de permisos en $DIR..."

# Solo el usuario propietario tiene lectura, escritura y ejecución
chmod 700 "$DIR"
find "$DIR" -type d -exec chmod 700 {} +
find "$DIR" -type f \( -name "*.sh" -o -name "*.zsh" -o -name "*.py" \) -exec chmod 700 {} +
find "$DIR" -type f ! -name "*.sh" ! -name "*.zsh" ! -name "*.py" -exec chmod 600 {} +

echo "✅ [SLONE SECURITY] Carpeta blindada. Ningún otro usuario del sistema puede acceder."
