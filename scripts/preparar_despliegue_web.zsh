#!/usr/bin/env zsh
# ══════════════════════════════════════════════════════════════════════════
# SLONE™ GLOBAL WEB DEPLOYMENT PIPELINE (CLOUDFLARE / VERCEL / CDN)
# ══════════════════════════════════════════════════════════════════════════
# Genera el directorio optimizado de producción para la web pública y checkout
# ══════════════════════════════════════════════════════════════════════════

set -e

PROJECT_DIR="/home/slone/slocast 1.0"
DIST_DIR="${PROJECT_DIR}/dist"
WEB_OUT="${DIST_DIR}/slone_web_produccion"

echo "\n✦ [SLÖNE CORP] Preparando paquete de despliegue web para producción..."

rm -rf "${WEB_OUT}"
mkdir -p "${WEB_OUT}"

# Copiar archivos del portal web
cp "${PROJECT_DIR}/app/web_portal/index.html" "${WEB_OUT}/"
cp "${PROJECT_DIR}/app/web_portal/manifest.json" "${WEB_OUT}/"
cp "${PROJECT_DIR}/app/web_portal/sw.js" "${WEB_OUT}/"
cp "${PROJECT_DIR}/app/web_portal/privacy.html" "${WEB_OUT}/" 2>/dev/null || true
cp "${PROJECT_DIR}/app/web_portal/terms.html" "${WEB_OUT}/" 2>/dev/null || true
cp "${PROJECT_DIR}/app/web_portal/showroom.html" "${WEB_OUT}/" 2>/dev/null || true
cp -r "${PROJECT_DIR}/app/web_portal/assets" "${WEB_OUT}/"
cp -r "${PROJECT_DIR}/app/web_portal/launcher" "${WEB_OUT}/"

# Añadir _redirects y configuración para Cloudflare Pages y SPA
cat << 'EOF' > "${WEB_OUT}/_redirects"
/portal   /index.html   200
/checkout /index.html   200
/*        /index.html   200
EOF

cat << 'EOF' > "${WEB_OUT}/vercel.json"
{
  "version": 2,
  "rewrites": [
    { "source": "/portal", "destination": "/index.html" },
    { "source": "/(.*)", "destination": "/$1" }
  ]
}
EOF

# Archivo de instrucciones para el CEO
cat << 'EOF' > "${WEB_OUT}/COMO_PUBLICAR_EN_INTERNET.txt"
══════════════════════════════════════════════════════════════════════════
✦ SLÖNE CORP · GUÍA DE PUBLICACIÓN EN DOMINIO GLOBAL (0 € EN SERVIDORES)
══════════════════════════════════════════════════════════════════════════

MÉTODO 1 · CLOUDFLARE PAGES (RECOMENDADO · ULTRA-RÁPIDO Y GRATUITO):
1. Entra en https://dash.cloudflare.com/ (crea cuenta gratuita).
2. Ve a "Workers & Pages" → "Create application" → "Pages" → "Upload assets".
3. Arrastra esta carpeta completa ('slone_web_produccion').
4. ¡Tu web estará online inmediatamente en https://slone.pages.dev con SSL gratis!
5. En la sección "Custom domains" puedes vincular tu propio dominio: slone.tech o slone.es.

MÉTODO 2 · VERCEL:
1. Instala vercel en terminal: npm i -g vercel
2. Ejecuta 'vercel deploy' dentro de esta carpeta.
══════════════════════════════════════════════════════════════════════════
EOF

echo "======================================================================="
echo "✅ ¡PAQUETE DE DESPLIEGUE WEB GENERADO CON ÉXITO!"
echo "======================================================================="
echo "📁 Directorio listo para subir a la nube: ${WEB_OUT}"
echo "📄 Guía paso a paso: ${WEB_OUT}/COMO_PUBLICAR_EN_INTERNET.txt"
echo "=======================================================================\n"
