#!/usr/bin/env zsh
# ══════════════════════════════════════════════════════════════════════════
# SLONE™ CLOUDFLARE PAGES 1-CLICK DEPLOYER
# ══════════════════════════════════════════════════════════════════════════
# Despliega la web del Drop 01 en la red global CDN de Cloudflare con SSL gratis.
# ══════════════════════════════════════════════════════════════════════════

set -e

PROJECT_DIR="/home/slone/slocast 1.0"
WEB_DIR="${PROJECT_DIR}/dist/slone_web_produccion"

echo "\n👑 [SLONE CORP] Desplegando Drop 01 en Cloudflare Pages..."

if [ ! -d "${WEB_DIR}" ]; then
    echo "⚙️ Directorio web no encontrado. Generando distribución web..."
    "${PROJECT_DIR}/scripts/preparar_despliegue_web.zsh"
fi

# Comprobar si el usuario tiene sesión activa o token
if ! npx -y wrangler whoami >/dev/null 2>&1; then
    echo "⚠️ Sesión de Cloudflare no detectada en este terminal."
    echo "👉 Abriendo autenticación segura en Firefox (solo 1 clic)..."
    npx -y wrangler login
fi

echo "🚀 Subiendo assets a Cloudflare Pages (Proyecto: slone-media)..."
npx -y wrangler pages deploy "${WEB_DIR}" --project-name slone-media --branch main

echo "\n======================================================================="
echo "✅ ¡WEB SLONE DROP 01 DESPLEGADA GLOBALMENTE EN CLOUDFLARE PAGES!"
echo "======================================================================="
echo "🌐 URL pública: https://slone-media.pages.dev"
echo "🛡️  SSL gratuito y CDN Edge con latencia <10ms en todo el planeta."
echo "=======================================================================\n"
