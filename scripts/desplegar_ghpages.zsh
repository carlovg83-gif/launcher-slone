#!/usr/bin/env zsh
# ==============================================================================
# SLÖNE WEB PWA - Publicación Automatizada en GitHub Pages (Rama gh-pages)
# ==============================================================================
set -e

DIR_PROYECTO="$(cd "$(dirname "$0")/.." && pwd)"
DIR_PWA="$DIR_PROYECTO/dist/slone-web-pwa"

echo "👑 [SLÖNE PWA] Sincronizando y preparando despliegue de PWA estática..."

# 1. Asegurar contenido de producción en dist/slone-web-pwa
mkdir -p "$DIR_PWA"
cp -r "$DIR_PROYECTO/app/web_portal/launcher/"* "$DIR_PWA/"
rm -f "$DIR_PWA/"*.bak*

# 2. Despliegue seguro mediante Git worktree temporal aislado
TMP_WORKTREE=$(mktemp -d /tmp/slone_ghpages_XXXXXX)
trap 'rm -rf "$TMP_WORKTREE"' EXIT INT TERM

cd "$DIR_PROYECTO"

if git show-ref --quiet refs/heads/gh-pages; then
    git worktree add -B gh-pages "$TMP_WORKTREE" gh-pages
else
    git worktree add -B gh-pages "$TMP_WORKTREE" HEAD
    cd "$TMP_WORKTREE"
    git rm -rf . >/dev/null 2>&1 || true
fi

cd "$TMP_WORKTREE"
git rm -rf . >/dev/null 2>&1 || true
cp -r "$DIR_PWA/"* .
touch .nojekyll

git add -A
if git diff --staged --quiet; then
    echo "ℹ️ No hay cambios pendientes en la PWA estática."
else
    git commit -m "deploy: actualización autónoma de SLÖNE Web PWA"
    echo "🚀 Publicando PWA en GitHub Pages (origin/gh-pages)..."
    git push -u origin gh-pages --force
    echo "✅ Despliegue de SLÖNE Web PWA completado en GitHub Pages."
fi

cd "$DIR_PROYECTO"
git worktree remove --force "$TMP_WORKTREE"
