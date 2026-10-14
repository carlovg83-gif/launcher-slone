#!/usr/bin/env zsh
# ==============================================================================
# SLONE GLOBAL MEDIA ENGINE · INSTALADOR AUTOMÁTICO EN 1-CLIC
# Sistema: Fedora 44 Linux · KDE Plasma 6 · Shell ZSH
# ==============================================================================

set -e

SLONE_ROOT="/home/slone/slocast 1.0"
ICON_SRC="${SLONE_ROOT}/app/assets/slone_logo.png"
DESKTOP_SRC="${SLONE_ROOT}/slone.desktop"
BIN_SRC="${SLONE_ROOT}/bin/slone"

echo "👑 Iniciando instalación de SLONE Global Media Engine..."

# 1. Crear directorios de usuario
mkdir -p "${HOME}/.local/bin"
mkdir -p "${HOME}/.local/share/applications"
mkdir -p "${HOME}/.local/share/icons/hicolor/256x256/apps"

# 2. Instalar enlace simbólico del binario en PATH
echo "⚡ Instalando comando 'slone' en ~/.local/bin/slone..."
ln -sf "${BIN_SRC}" "${HOME}/.local/bin/slone"
chmod +x "${BIN_SRC}"

# 3. Instalar icono del sistema
if [[ -f "${ICON_SRC}" ]]; then
    echo "🎨 Instalando icono oficial SLONE en el tema de KDE..."
    cp -f "${ICON_SRC}" "${HOME}/.local/share/icons/hicolor/256x256/apps/slone.png"
fi

# 4. Instalar acceso directo .desktop
echo "🖥️  Configurando lanzador para KDE Plasma 6..."
cp -f "${DESKTOP_SRC}" "${HOME}/.local/share/applications/slone.desktop"
chmod +x "${HOME}/.local/share/applications/slone.desktop"

# 5. Actualizar base de datos de aplicaciones de escritorio
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${HOME}/.local/share/applications" >/dev/null 2>&1 || true
fi

echo "======================================================================="
echo "✅ ¡SLONE GLOBAL MEDIA ENGINE INSTALADO CON ÉXITO EN TU SISTEMA!"
echo "======================================================================="
echo "• Desde Konsole / ZSH: escribe simplemente 'slone'"
echo "• Desde KDE Plasma: pulsa tecla Meta/Super y busca 'SLONE'"
echo "• Ubicación del proyecto: ${SLONE_ROOT}"
echo "======================================================================="
