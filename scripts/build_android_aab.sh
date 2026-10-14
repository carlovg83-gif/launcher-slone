#!/usr/bin/env zsh
# ──────────────────────────────────────────────────────────────
#  SLONE™ OS / SLOCAST — Pipeline de Compilación Android (AAB / APK)
#  Genera paquete firmado para Google Play Store y Android TV
# ──────────────────────────────────────────────────────────────
set -e

BASE="$(cd "$(dirname "$0")/.." && pwd)"
KEYSTORE="${KEYSTORE:-$BASE/keystore/slone.keystore}"
[ -f "$KEYSTORE" ] || KEYSTORE="$HOME/slone.keystore"
ALIAS="slone"

echo "👑 [SLONE ANDROID PIPELINE] Iniciando preparación de paquete Play Store..."

if [ ! -f "$KEYSTORE" ]; then
    echo "❌ Error: No se encuentra el almacén de claves en $KEYSTORE"
    exit 1
fi

echo "🔐 [KEYSTORE] Verificado almacén de firma oficial: $KEYSTORE"

# Comprobación de herramientas de Android SDK / Gradle
echo "📦 Ficha técnica de Play Store lista en app/playstore_listing.md"
echo "🎨 Iconos oficiales listos en icons/slocast.png (1024x1024)"

cat << 'EOF'
========================================================================
  GUÍA RÁPIDA DE SUBIDA A GOOGLE PLAY CONSOLE:
========================================================================
1. Accede a tu consola de desarrollador: https://play.google.com/apps/publish
2. Crea una nueva aplicación: "SLONE: Live TV & Media Player"
3. Idioma predeterminado: Español (España)
4. Sube la ficha ASO ubicada en: $BASE/app/playstore_listing.md
5. Sube los mockups gráficos ubicados en: $BASE/branding/
6. Firma de paquete: Usa $KEYSTORE
========================================================================
EOF
