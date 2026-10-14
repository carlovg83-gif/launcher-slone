#!/usr/bin/env zsh
# ══════════════════════════════════════════════════════════════════════════
# SLONE™ FEDORA 44 RPM PACKAGING PIPELINE
# ══════════════════════════════════════════════════════════════════════════
# Genera el paquete oficial .rpm para Fedora Linux y Red Hat Enterprise
# Compatible al 100% con 'sudo dnf install ./slone-1.0.0-1.fc44.noarch.rpm'
# ══════════════════════════════════════════════════════════════════════════

set -e

PROJECT_DIR="/home/slone/slocast 1.0"
# Usar ruta sin espacios para evitar conflictos en rpmbuild
BUILD_DIR="${HOME}/.cache/slone_rpmbuild"
RPMS_OUT="${PROJECT_DIR}/dist/rpms"

echo "\n👑 [SLONE CORP] Iniciando empaquetado nativo RPM para Fedora 44..."

# 1. Crear estructura de trabajo rpmbuild
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
mkdir -p "${RPMS_OUT}"

VERSION="1.0.0"
PKG_NAME="slone"
TAR_NAME="${PKG_NAME}-${VERSION}"
STAGE_DIR="${BUILD_DIR}/${TAR_NAME}"

# 2. Asegurar existencia de binario nativo compilado
if [ ! -f "${PROJECT_DIR}/dist/bin/slone" ]; then
    echo "⚙️ Binario nativo no encontrado. Ejecutando compilación previa..."
    "${PROJECT_DIR}/scripts/compilar_binario_nativo.zsh"
fi

# 3. Preparar el árbol de fuentes para el tarball
echo "📦 Preparando árbol de distribución v${VERSION}..."
mkdir -p "${STAGE_DIR}"
mkdir -p "${STAGE_DIR}/bin"
cp "${PROJECT_DIR}/dist/bin/slone" "${STAGE_DIR}/bin/slone"
cp -r "${PROJECT_DIR}/branding" "${STAGE_DIR}/"
cp -r "${PROJECT_DIR}/docs" "${STAGE_DIR}/"
cp -r "${PROJECT_DIR}/icons" "${STAGE_DIR}/"
cp -r "${PROJECT_DIR}/playlists" "${STAGE_DIR}/"
cp "${PROJECT_DIR}/slone.desktop" "${STAGE_DIR}/"

# Crear tarball fuente
tar -czf "${BUILD_DIR}/SOURCES/${TAR_NAME}.tar.gz" -C "${BUILD_DIR}" "${TAR_NAME}"
rm -rf "${STAGE_DIR}"

# 4. Escribir el archivo SPEC de RPM
cat << 'EOF' > "${BUILD_DIR}/SPECS/slone.spec"
%global debug_package %{nil}

Name:           slone
Version:        1.0.0
Release:        1%{?dist}
Summary:        SLONE Sovereign Global Media Engine
License:        Proprietary
URL:            https://slone.tech
Source0:        %{name}-%{version}.tar.gz
BuildArch:      x86_64

Requires:       mpv >= 0.35
Requires:       zsh

%description
SLONE Global Media Engine es el motor multimedia y reproductor de alta fidelidad
soberano con tolerancia Zero-Freeze, soporte Multi-Audio real, sincronización
de radio deportiva sin retardo y cuadrícula deportiva Multiview Stadium 4X.
Compilado en binario nativo protegido x86_64.
Sede Central: Girona Tech Hub (Catalunya, España).

%prep
%setup -q

%install
rm -rf "%{buildroot}"
mkdir -p "%{buildroot}/usr/share/slone"
mkdir -p "%{buildroot}/usr/bin"
mkdir -p "%{buildroot}/usr/share/applications"
mkdir -p "%{buildroot}/usr/share/icons/hicolor/512x512/apps"

# Copiar recursos a /usr/share/slone
cp -r branding docs icons playlists "%{buildroot}/usr/share/slone/"

# Instalar binario nativo protegido
cp bin/slone "%{buildroot}/usr/bin/slone"
chmod 755 "%{buildroot}/usr/bin/slone"

# Acceso directo oficial de escritorio
cat << 'INNER_EOF' > "%{buildroot}/usr/share/applications/slone.desktop"
[Desktop Entry]
Name=SLONE
GenericName=Global Media Engine
Comment=Sovereign Ultra-High-Fidelity Media & Sports Broadcast Player
Exec=/usr/bin/slone %U
Icon=slone
Terminal=false
Type=Application
Categories=AudioVideo;Player;TV;Video;
Keywords=slone;iptv;streaming;stadium;multiview;radio;cast;
StartupNotify=true
StartupWMClass=slone
INNER_EOF

# Icono oficial de alta resolución
cp icons/slone.png "%{buildroot}/usr/share/icons/hicolor/512x512/apps/slone.png"

%files
/usr/share/slone
/usr/bin/slone
/usr/share/applications/slone.desktop
/usr/share/icons/hicolor/512x512/apps/slone.png

%changelog
* Wed Oct 14 2026 slone CEO <ceo@slone.es> - 1.0.0-1
- Lanzamiento inicial oficial de SLONE Global Media Engine con Multiview Stadium 4X.
EOF

# 4. Ejecutar compilación de paquete RPM
echo "🔨 Compilando binario RPM con rpmbuild..."
rpmbuild -ba \
    --define "_topdir ${BUILD_DIR}" \
    --define "dist .fc44" \
    "${BUILD_DIR}/SPECS/slone.spec"

# 5. Mover los paquetes generados a dist/rpms
cp "${BUILD_DIR}"/RPMS/*/*.rpm "${RPMS_OUT}/"
rm -rf "${BUILD_DIR}"
GENERATED_RPM=$(ls "${RPMS_OUT}"/slone-1.0.0-1.fc44.x86_64.rpm | head -n 1)

echo "\n======================================================================="
echo "✅ ¡PAQUETE RPM PARA FEDORA 44 GENERADO CON ÉXITO!"
echo "======================================================================="
echo "📦 Archivo RPM listo: ${GENERATED_RPM}"
echo "💾 Tamaño del paquete: $(du -sh "${GENERATED_RPM}" | awk '{print $1}')"
echo "💡 Para instalar en cualquier Fedora / Red Hat:"
echo "   sudo dnf install ./${GENERATED_RPM##*/}"
echo "=======================================================================\n"
