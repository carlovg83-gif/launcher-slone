#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
#  SLOCAST / SLONE — Instalador OPCIONAL en el sistema
#  Instala lanzadores e iconos en ~/.local apuntando a ESTA
#  carpeta consolidada. NO se ejecuta automáticamente.
#  Uso:  bash instalar_en_sistema.sh
# ──────────────────────────────────────────────────────────────
set -euo pipefail

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$BASE/app/slocast.py"

[ -f "$APP" ] || { echo "ERROR: no encuentro $APP"; exit 1; }

mkdir -p "$HOME/.local/bin" "$HOME/.local/share/applications" "$HOME/.local/share/icons"

# 1. Lanzadores de consola (slocast y slone)
cat > "$HOME/.local/bin/slocast" <<EOF
#!/usr/bin/env zsh
export QT_QPA_PLATFORM=xcb
exec python3 "$APP" "\$@"
EOF
ln -sf "$HOME/.local/bin/slocast" "$HOME/.local/bin/slone"
chmod +x "$HOME/.local/bin/slocast"

# 2. Iconos
cp -f "$BASE/icons/slocast.png" "$BASE/icons/slone.png" "$HOME/.local/share/icons/"

# 3. Entradas de menú (.desktop)
for n in slocast slone; do
  sed -e "s#^Exec=.*#Exec=$HOME/.local/bin/$n#" \
      -e "s#^Icon=.*#Icon=$HOME/.local/share/icons/$n.png#" \
      "$BASE/launchers/$n.desktop" > "$HOME/.local/share/applications/$n.desktop"
done

# 4. Refrescar cachés de menú (KDE / GNOME)
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$HOME/.local/share/applications" || true
command -v kbuildsycoca6 >/dev/null 2>&1 && kbuildsycoca6 --noincremental >/dev/null 2>&1 || true

echo "Instalado: slocast / slone  ->  $APP"
echo "Aviso: el portal web (web_portal) se sirve desde la ruta de Antigravity."
echo "       Para portabilidad total aplica el parche descrito en ../README.md"
