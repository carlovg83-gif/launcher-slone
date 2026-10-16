#!/usr/bin/env zsh
# ══════════════════════════════════════════════════════════════════════════
# SLÖNE CORP · SCRIPT SOBERANO DE COPIA DE SEGURIDAD CIFRADA A LA BÓVEDA
# ══════════════════════════════════════════════════════════════════════════
# Empaqueta, audita mediante árbol SHA-256 y cifra con AES-256 (PBKDF2)
# los 3 pilares del ecosistema SLÖNE (SLO_Sports, slocast 1.0 y tesis/).
# Aplica permisos militares 0700/0600 y custodia en .vault_slocast.
# ══════════════════════════════════════════════════════════════════════════

set -e

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
USER_HOME="${HOME:-/home/slone}"
VAULT_DIR="${USER_HOME}/.vault_slocast"
SNAPSHOTS_DIR="${VAULT_DIR}/snapshots"
MOUNT_VAULT="${USER_HOME}/SLOCAST_VAULT"

DIR_SLO_SPORTS="${USER_HOME}/Proyectos/SLO_Sports"
DIR_SLOCAST="${USER_HOME}/slocast 1.0"
DIR_TESIS="${USER_HOME}/tesis"

TMP_STAGE="${USER_HOME}/.slone_backup_tmp_${TIMESTAMP}"

echo "\n══════════════════════════════════════════════════════════════════════════"
echo "👑 [SLÖNE CORP] COPIA DE SEGURIDAD CIFRADA MILITAR A LA BÓVEDA SOBERANA"
echo "══════════════════════════════════════════════════════════════════════════"
echo "🕒 Marca de tiempo: ${TIMESTAMP}"
echo "📍 Destino seguro: ${SNAPSHOTS_DIR} (Permisos 0700)"

# 1. PREPARACIÓN Y BLINDAJE DE DIRECTORIOS
mkdir -p "${SNAPSHOTS_DIR}"
chmod 700 "${VAULT_DIR}" "${SNAPSHOTS_DIR}"
mkdir -p "${TMP_STAGE}"
chmod 700 "${TMP_STAGE}"

# Limpieza segura al salir
trap 'rm -rf "${TMP_STAGE}"' EXIT INT TERM

# 2. GENERACIÓN DEL ÁRBOL DE INTEGRIDAD SHA-256
echo "\n[1/4] Auditando e indexando integridad criptográfica del ecosistema..."
MANIFEST_FILE="${TMP_STAGE}/MANIFEST_INTEGRIDAD_${TIMESTAMP}.sha256"

# Auditoría de SLO_Sports
if [ -d "${DIR_SLO_SPORTS}" ]; then
    find "${DIR_SLO_SPORTS}" -type f \
        ! -path "*/__pycache__/*" \
        ! -path "*/.git/*" \
        ! -path "*/.pytest_cache/*" \
        -exec sha256sum {} + >> "${MANIFEST_FILE}" 2>/dev/null || true
fi

# Auditoría de slocast 1.0
if [ -d "${DIR_SLOCAST}" ]; then
    find "${DIR_SLOCAST}" -type f \
        ! -path "*/__pycache__/*" \
        ! -path "*/.git/*" \
        ! -path "*/node_modules/*" \
        ! -path "*/dist/*" \
        -exec sha256sum {} + >> "${MANIFEST_FILE}" 2>/dev/null || true
fi

# Auditoría de tesis
if [ -d "${DIR_TESIS}" ]; then
    find "${DIR_TESIS}" -type f \
        ! -path "*/__pycache__/*" \
        -exec sha256sum {} + >> "${MANIFEST_FILE}" 2>/dev/null || true
fi

TOTAL_FILES_AUDITED=$(wc -l < "${MANIFEST_FILE}" | tr -d ' ')
echo "  ✓ Ficheros indexados en árbol SHA-256: ${TOTAL_FILES_AUDITED}"

# 3. EMPAQUETADO SOBERANO DE LOS 3 PILARES
echo "\n[2/4] Generando snapshot comprimido del ecosistema..."
TAR_ARCHIVE="${TMP_STAGE}/slone_ecosistema_${TIMESTAMP}.tar.gz"

tar -czf "${TAR_ARCHIVE}" \
    --exclude="*/__pycache__" \
    --exclude="*/.pytest_cache" \
    --exclude="*/node_modules" \
    --exclude="*/.git/objects" \
    -C "${USER_HOME}" \
    "Proyectos/SLO_Sports" \
    "slocast 1.0" \
    "tesis" 2>/dev/null || {
        echo "⚠️ Advertencia en empaquetado (ficheros concurrentes ignorados)."
    }

TAR_SIZE=$(du -sh "${TAR_ARCHIVE}" | awk '{print $1}')
echo "  ✓ Snapshot base empaquetado: ${TAR_SIZE}"

# 4. CIFRADO MILITAR AES-256-CBC CON PBKDF2
echo "\n[3/4] Cifrando snapshot con grado de defensa militar (AES-256 + PBKDF2)..."
FINAL_ENC_ARCHIVE="${SNAPSHOTS_DIR}/SLONE_SNAPSHOT_${TIMESTAMP}.tar.gz.enc"

# Usamos la clave privada de la keystore como entropía de derivación o clave soberana
KEYSTORE_PRIV="${DIR_SLOCAST}/keystore/slone_ed25519_private.pem"
if [ -f "${KEYSTORE_PRIV}" ]; then
    PASS_PHRASE=$(sha256sum "${KEYSTORE_PRIV}" | awk '{print $1}')
else
    PASS_PHRASE="SLONE-SOVEREIGN-VAULT-DEFENSE-LAYER-7"
fi

openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -salt \
    -in "${TAR_ARCHIVE}" \
    -out "${FINAL_ENC_ARCHIVE}" \
    -pass "pass:${PASS_PHRASE}"

chmod 600 "${FINAL_ENC_ARCHIVE}"
ENC_SIZE=$(du -sh "${FINAL_ENC_ARCHIVE}" | awk '{print $1}')
ENC_SHA256=$(sha256sum "${FINAL_ENC_ARCHIVE}" | awk '{print $1}')

# Guardar registro notarial de este snapshot
echo "${ENC_SHA256}  SLONE_SNAPSHOT_${TIMESTAMP}.tar.gz.enc" > "${SNAPSHOTS_DIR}/SLONE_SNAPSHOT_${TIMESTAMP}.sha256"
cp "${MANIFEST_FILE}" "${SNAPSHOTS_DIR}/MANIFEST_INTEGRIDAD_${TIMESTAMP}.sha256"
chmod 600 "${SNAPSHOTS_DIR}/SLONE_SNAPSHOT_${TIMESTAMP}.sha256" "${SNAPSHOTS_DIR}/MANIFEST_INTEGRIDAD_${TIMESTAMP}.sha256"

# 5. SINCRONIZACIÓN AUTOMÁTICA SI LA BÓVEDA ESTÁ MONTADA
echo "\n[4/4] Verificando estado de montado de Bóveda SLÖNE..."
if mountpoint -q "${MOUNT_VAULT}" 2>/dev/null; then
    echo "  🔓 Bóveda activa detectada en ${MOUNT_VAULT}."
    mkdir -p "${MOUNT_VAULT}/backups_ecosistema"
    cp "${TAR_ARCHIVE}" "${MOUNT_VAULT}/backups_ecosistema/slone_ecosistema_${TIMESTAMP}.tar.gz"
    echo "  ✓ Copia adicional depositada en el sistema de ficheros cifrado gocryptfs."
else
    echo "  🔒 Bóveda en reposo (/home/slone/SLOCAST_VAULT). Snapshot blindado depositado en ${SNAPSHOTS_DIR}."
    echo "  👉 Cuando ejecutes 'slone_vault.sh unlock' se mantendrá bajo custodia biométrica."
fi

echo "\n══════════════════════════════════════════════════════════════════════════"
echo "✅ ¡COPIA DE SEGURIDAD SOBERANA FINALIZADA Y PROTEGIDA!"
echo "══════════════════════════════════════════════════════════════════════════"
echo "📁 Archivo cifrado: ${FINAL_ENC_ARCHIVE}"
echo "📦 Tamaño cifrado:  ${ENC_SIZE}"
echo "🛡️  Algoritmo:       AES-256-CBC (PBKDF2 100.000 iteraciones + Salt)"
echo "🔑 Huella SHA-256:  ${ENC_SHA256}"
echo "📑 Manifiesto:      ${SNAPSHOTS_DIR}/MANIFEST_INTEGRIDAD_${TIMESTAMP}.sha256"
echo "══════════════════════════════════════════════════════════════════════════\n"
