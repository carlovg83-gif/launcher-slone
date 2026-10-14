#!/usr/bin/env zsh
# ──────────────────────────────────────────────────────────────
#  SLONE™ OS / SLOCAST — Pipeline de Publicación en GitHub
#  Uso: zsh scripts/publicar_github.sh "Mensaje del Release"
# ──────────────────────────────────────────────────────────────
set -e

SCRIPT_DIR="${0:A:h}"
BASE="${SCRIPT_DIR:h}"
cd "$BASE"

TAG="v7.5-sovereign"
MSG="${1:-Release SLONE OS v7.5 Sovereign Edition}"

echo "👑 [SLONE GITHUB PIPELINE] Iniciando empaquetado y control de versiones..."

# 1. Inicializar git si no está inicializado
if [ ! -d ".git" ]; then
    git init
    git branch -M main
    git config user.name "slone"
    git config user.email "slone@slone.global"
fi

# 2. Crear .gitignore estricto para no subir JAMAS datos privados, pedidos ni secretos
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.bak*
.DS_Store
*.log
.system_generated/
# Secretos y claves de infraestructura
config/*.env
config/secrets.env
config/slone_control.json
config/security.log
# Datos de clientes y pedidos privados (RGPD)
data/*.json
data/orders.json
# Bóveda y claves criptográficas
keystore/
*.keystore
*.key
*.pem
*.sig
# Paquetes y compilados binarios masivos
dist/*.zip
dist/*.tar.gz
dist/*.rpm
EOF

# 3. Añadir ficheros y crear commit
git add -A
git commit -m "$MSG" || echo "No hay cambios pendientes de commit."

# 4. Crear etiqueta de versión
git tag -f -a "$TAG" -m "SLONE OS v7.5 - Zero-Freeze, Multi-Audio, VPN Shield & Biometric Enclave"

echo "✅ [SLONE GITHUB] Repositorio local preparado y firmado con el tag $TAG."
echo ""
echo "🚀 Para publicar en tu cuenta remota de GitHub ejecuta:"
echo "   git remote add origin https://github.com/TU_USUARIO/slocast.git"
echo "   git push -u origin main --tags"
echo "   gh release create $TAG --title 'SLONE OS v7.5 Sovereign' --notes-file README.md"
