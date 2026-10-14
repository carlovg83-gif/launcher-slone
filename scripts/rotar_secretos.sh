#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
#  SLONE™ — Rotación de secretos de producción
#  Genera secretos criptográficamente fuertes y los guarda en config/secrets.env
#  (permisos 600, ignorado por Git). Ni la app ni el backend llevan secretos
#  en claro en el código: ambos leen estas variables de entorno.
# ════════════════════════════════════════════════════════════════════════════
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/config/secrets.env"

gen() { openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n'; }

LIC="SLONE_LIC_$(gen)"
WHK="SLONE_WHK_$(gen)"
ADM="$(gen)"

umask 077
cat > "$OUT" <<EOF
# Generado por scripts/rotar_secretos.sh el $(date -Iseconds)
# NO subir a Git (config/*.env está ignorado). Permisos 600.
export SLONE_LICENSE_SECRET="$LIC"
export SLONE_WEBHOOK_SECRET="$WHK"
export SLONE_ADMIN_TOKEN="$ADM"
EOF
chmod 600 "$OUT"

echo "✅ Secretos rotados en $OUT (permisos 600)"
echo
echo "Actívalos en esta sesión:"
echo "  source $OUT"
echo
echo "Arranca el backend con ellos:"
echo "  source $OUT && make backend"
echo
echo "⚠️  La app (SLOCAST) y el backend DEBEN usar el MISMO SLONE_LICENSE_SECRET;"
echo "    si no, las claves emitidas dejarán de validarse."
echo "    Para la app, expórtalo en tu sesión gráfica (p. ej. en ~/.profile):"
echo "      export SLONE_LICENSE_SECRET=...   (mismo valor que aquí)"
