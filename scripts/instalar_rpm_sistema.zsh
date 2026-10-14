#!/usr/bin/env zsh
# ══════════════════════════════════════════════════════════════════════════
# SLONE™ INSTALADOR DEL PAQUETE RPM EN EL SISTEMA
# ══════════════════════════════════════════════════════════════════════════
# Instala el paquete RPM nativo x86_64 a nivel global en Fedora 44
# ══════════════════════════════════════════════════════════════════════════

set -e

PROJECT_DIR="/home/slone/slocast 1.0"
RPM_FILE="${PROJECT_DIR}/dist/rpms/slone-1.0.0-1.fc44.x86_64.rpm"

if [ ! -f "${RPM_FILE}" ]; then
    echo "❌ Archivo RPM no encontrado en ${RPM_FILE}"
    echo "Ejecuta primero: ${PROJECT_DIR}/scripts/crear_rpm_fedora.zsh"
    exit 1
fi

echo "\n👑 [SLONE CORP] Instalando SLONE 1.0.0 en /usr/bin/slone con dnf..."
echo "👆 Pon el dedo en el sensor de huellas si te lo solicita sudo:\n"

sudo dnf reinstall -y "${RPM_FILE}" 2>/dev/null || sudo dnf install -y "${RPM_FILE}"

echo "\n======================================================================="
echo "✅ ¡SLONE INSTALADO OFICIALMENTE EN EL SISTEMA A NIVEL GLOBAL!"
echo "======================================================================="
echo "📦 Paquete: ${RPM_FILE##*/}"
echo "🚀 Binario global: /usr/bin/slone"
echo "=======================================================================\n"
