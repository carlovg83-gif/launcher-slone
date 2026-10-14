#!/usr/bin/env zsh
# ══════════════════════════════════════════════════════════════════════════
# SLONE™ GLOBAL MEDIA ENGINE · GENERADOR DE PAQUETE DE DISTRIBUCIÓN
# ══════════════════════════════════════════════════════════════════════════
# Empaqueta el ecosistema SLONE completo para grabarlo en los Pendrives USB
# de los Welcome Packs (128GB / 256GB) o para distribución directa a clientes.
# ══════════════════════════════════════════════════════════════════════════

set -e

PROJECT_DIR="/home/slone/slocast 1.0"
DIST_DIR="${PROJECT_DIR}/dist"
USB_DIR="${DIST_DIR}/SLONE_USB_WELCOME_PACK"
ARCHIVE="${DIST_DIR}/slone_global_media_engine_fedora_linux.tar.gz"

echo "\n👑 [SLONE CORP] Iniciando empaquetado de distribución oficial..."

# 1. Crear directorio de salida limpio
rm -rf "${USB_DIR}"
mkdir -p "${USB_DIR}"

# 2. Copiar componentes esenciales del ecosistema
echo "📦 Copiando motor de aplicación y arquitectura de software..."
cp -r "${PROJECT_DIR}/app" "${USB_DIR}/"
cp -r "${PROJECT_DIR}/bin" "${USB_DIR}/"
cp -r "${PROJECT_DIR}/config" "${USB_DIR}/"
cp -r "${PROJECT_DIR}/docs" "${USB_DIR}/"
cp -r "${PROJECT_DIR}/icons" "${USB_DIR}/"
cp -r "${PROJECT_DIR}/playlists" "${USB_DIR}/"
cp -r "${PROJECT_DIR}/branding" "${USB_DIR}/"
cp "${PROJECT_DIR}/slone.desktop" "${USB_DIR}/"
cp "${PROJECT_DIR}/install.sh" "${USB_DIR}/"
chmod +x "${USB_DIR}/install.sh" "${USB_DIR}/bin/slone"

# 3. Limpiar cachés y temporales del paquete
find "${USB_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${USB_DIR}" -type f -name "*.pyc" -delete 2>/dev/null || true
find "${USB_DIR}" -type f -name "*.bak*" -delete 2>/dev/null || true

# 4. Crear carta de bienvenida del CEO para el socio del Welcome Pack
cat << 'EOF' > "${USB_DIR}/BIENVENIDO_A_SLONE.txt"
══════════════════════════════════════════════════════════════════════════
👑 SLONE GLOBAL MEDIA ENGINE · WELCOME PACK OFICIAL DE AUTOR
══════════════════════════════════════════════════════════════════════════
¡Enhorabuena y bienvenido a la élite del software multimedia soberano!

Tienes en tus manos el Pendrive Oficial SLONE Grabado a Láser, parte 
de tu Welcome Pack oficial. Este soporte contiene el instalador original 
de SLONE Global Media Engine de máxima fidelidad y rendimiento.

CÓMO INSTALAR EN TU SISTEMA (FEDORA / UBUNTU / DEBIAN / ARCH LINUX):
1. Abre tu terminal en esta carpeta.
2. Ejecuta simplemente:
   zsh install.sh
   (o bien: bash install.sh si tu distribución no dispone de ZSH por defecto).
3. ¡Listo! Escribe 'slone' en cualquier consola o pulsa la tecla Super/Windows
   en tu escritorio para iniciar la experiencia.

CARACTERÍSTICAS EXCLUSIVAS DE TU VERSIÓN:
• SLONE Multiview Stadium™ 4X: 4 partidos en directo conmutando audio con 1, 2, 3, 4.
• Dynamic Audio-Sync & Radio Layer™: Radios deportivas sin retraso.
• TDT Oficial Abierta y Hub Musical YouTube integrado.
• Temas dinámicos de club: Signature Neón, FC Barcelona, Girona FC, etc.

Sede Central: Girona Tech Hub (Catalunya, España)
Director Ejecutivo y Fundador: slone (CEO)
══════════════════════════════════════════════════════════════════════════
EOF

# 5. Generar archivo comprimido de alta velocidad
echo "🗜️  Comprimiendo archivo tar.gz oficial..."
tar -czf "${ARCHIVE}" -C "${DIST_DIR}" "SLONE_USB_WELCOME_PACK"

echo "\n======================================================================="
echo "✅ ¡PAQUETE DE DISTRIBUCIÓN GENERADO CON ÉXITO!"
echo "======================================================================="
echo "📁 Carpeta lista para Pendrive: ${USB_DIR}"
echo "📦 Archivo tar.gz distribuible: ${ARCHIVE}"
echo "💾 Tamaño del paquete: $(du -sh "${ARCHIVE}" | awk '{print $1}')"
echo "=======================================================================\n"
