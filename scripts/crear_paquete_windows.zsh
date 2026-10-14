#!/usr/bin/env zsh
# ══════════════════════════════════════════════════════════════════════════
# SLONE™ WINDOWS 10 / 11 PORTABLE PACKAGING PIPELINE
# ══════════════════════════════════════════════════════════════════════════
# Empaqueta la versión portátil para sistemas Microsoft Windows (x64)
# ══════════════════════════════════════════════════════════════════════════

set -e

PROJECT_DIR="/home/slone/slocast 1.0"
DIST_DIR="${PROJECT_DIR}/dist"
WIN_STAGE="${DIST_DIR}/SLONE_WINDOWS_PORTABLE"
ZIP_OUT="${DIST_DIR}/slone_windows_x64_portable.zip"

echo "\n👑 [SLONE CORP] Iniciando empaquetado portátil para Windows 10/11..."

rm -rf "${WIN_STAGE}"
mkdir -p "${WIN_STAGE}"

# Copiar aplicación y configuraciones
cp -r "${PROJECT_DIR}/app" "${WIN_STAGE}/"
cp -r "${PROJECT_DIR}/config" "${WIN_STAGE}/"
cp -r "${PROJECT_DIR}/branding" "${WIN_STAGE}/"
cp -r "${PROJECT_DIR}/docs" "${WIN_STAGE}/"
cp -r "${PROJECT_DIR}/icons" "${WIN_STAGE}/"
cp -r "${PROJECT_DIR}/playlists" "${WIN_STAGE}/"

# Copiar lanzador bat
cp "${PROJECT_DIR}/platforms/windows/iniciar_slone.bat" "${WIN_STAGE}/Iniciar_SLONE.bat"

# Limpieza de temporales y cachés
find "${WIN_STAGE}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${WIN_STAGE}" -type f -name "*.pyc" -delete 2>/dev/null || true
find "${WIN_STAGE}" -type f -name "*.bak*" -delete 2>/dev/null || true

# Crear archivo LEEME para Windows
cat << 'EOF' > "${WIN_STAGE}/LEEME_WINDOWS.txt"
══════════════════════════════════════════════════════════════════════════
👑 SLONE GLOBAL MEDIA ENGINE · EDICIÓN MICROSOFT WINDOWS 10 / 11
══════════════════════════════════════════════════════════════════════════
Sede Central: Girona Tech Hub (Catalunya, España)

INSTRUCCIONES DE EJECUCIÓN EN WINDOWS:
1. Asegúrate de tener Python 3 instalado (desde https://www.python.org/downloads/
   marcando la casilla "Add Python to PATH" durante la instalación).
2. Haz doble clic en "Iniciar_SLONE.bat".
3. El script configurará las librerías gráficas automáticamente e iniciará
   el motor multimedia con aceleración gráfica completa.

CARACTERÍSTICAS INCLUIDAS:
• Multiview Stadium™ 4X: Cuadrícula para seguir 4 deportes a la vez [F4].
• Audio-Sync: Radios deportivas en directo sin retraso.
• TDT abierta oficial y hub de música integrado.
══════════════════════════════════════════════════════════════════════════
EOF

# Comprimir a zip
rm -f "${ZIP_OUT}"
(cd "${DIST_DIR}" && zip -qr "${ZIP_OUT}" "SLONE_WINDOWS_PORTABLE")

echo "\n======================================================================="
echo "✅ ¡PAQUETE PORTÁTIL PARA MICROSOFT WINDOWS GENERADO CON ÉXITO!"
echo "======================================================================="
echo "📦 Archivo ZIP listo: ${ZIP_OUT}"
echo "💾 Tamaño del paquete: $(du -sh "${ZIP_OUT}" | awk '{print $1}')"
echo "=======================================================================\n"
