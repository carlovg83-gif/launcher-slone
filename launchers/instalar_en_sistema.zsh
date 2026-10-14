#!/usr/bin/env zsh
# ──────────────────────────────────────────────────────────────
#  SLONE GLOBAL MEDIA ENGINE — Instalador Oficial en Fedora / KDE
#  Sede: Girona, Catalunya · Shell: ZSH
# ──────────────────────────────────────────────────────────────
set -eu

BASE="${0:A:h}/.."
APP="$BASE/app/slocast.py"

if [[ ! -f "$APP" ]]; then
  echo "[-] ERROR: No se encuentra el motor principal en $APP" >&2
  exit 1
fi

mkdir -p "$HOME/.local/bin" "$HOME/.local/share/applications" "$HOME/.local/share/icons"

rm -f "$HOME/.local/bin/slone" "$HOME/.local/bin/slocast"

# 1. Binario de consola 'slone' en ~/.local/bin
cat > "$HOME/.local/bin/slone" <<EOF
#!/usr/bin/env zsh
# SLONE GLOBAL MEDIA ENGINE · CLI Launcher
export QT_QPA_PLATFORM=xcb
exec python3 "$APP" "\$@"
EOF
chmod +x "$HOME/.local/bin/slone"

# Enlace de compatibilidad retroactiva 'slocast'
ln -sf "$HOME/.local/bin/slone" "$HOME/.local/bin/slocast"

# 2. Iconos del sistema
cp -f "$BASE/icons/slone.png" "$HOME/.local/share/icons/slone.png"
cp -f "$BASE/icons/slone.png" "$HOME/.local/share/icons/slocast.png"

# 3. Lanzador .desktop para KDE Plasma 6 / KRunner
sed -e "s#^Exec=.*#Exec=$HOME/.local/bin/slone#" \
    -e "s#^Icon=.*#Icon=$HOME/.local/share/icons/slone.png#" \
    "$BASE/launchers/slone.desktop" > "$HOME/.local/share/applications/slone.desktop"

# 4. Refrescar base de datos de escritorio de KDE Plasma 6
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
fi

if command -v kbuildsycoca6 >/dev/null 2>&1; then
  kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
fi

echo "[+] SLONE Global Media Engine instalado con éxito en el sistema."
echo "    - Binario CLI: ~/.local/bin/slone"
echo "    - Acceso directo KDE: Menú Aplicaciones / KRunner -> 'SLONE Global Media Engine'"
