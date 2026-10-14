#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
#  SLONE™ Hardening — Endurecimiento del sistema operativo
#  • Gobernador de CPU → performance (máximo rendimiento)
#  • fail2ban para bloquear fuerza bruta
#  • Firewall estricto de entrada (opcional con --firewall)
#  Uso:  sudo bash scripts/slone_hardening.sh [--firewall]
# ──────────────────────────────────────────────────────────────
set -uo pipefail

APPLY_FIREWALL=0
[[ "${1:-}" == "--firewall" ]] && APPLY_FIREWALL=1

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Este script necesita root. Ejecuta:  sudo bash scripts/slone_hardening.sh ${1:-}"
  exit 1
fi

echo "🛡️  SLONE™ Hardening — control total del sistema"
echo

# 1) Gobernador de CPU → performance (máximo rendimiento sostenido)
GOV_DIR="/sys/devices/system/cpu/cpu0/cpufreq"
if [[ -f "$GOV_DIR/scaling_available_governors" ]] && grep -q performance "$GOV_DIR/scaling_available_governors"; then
  for g in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance > "$g" 2>/dev/null || true
  done
  echo "✅ Gobernador CPU → performance (todos los núcleos)."
else
  echo "ℹ️  El gobernador 'performance' no está disponible; se mantiene el actual."
fi

# 2) fail2ban — bloqueo automático de fuerza bruta (SSH y servicios)
if command -v fail2ban-client >/dev/null 2>&1; then
  systemctl enable --now fail2ban >/dev/null 2>&1 && echo "✅ fail2ban activado."
else
  echo "ℹ️  fail2ban no instalado (opcional): sudo dnf install fail2ban  ó  sudo apt install fail2ban"
fi

# 3) Firewall — política estricta de entrada
LAN_IP="$(ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K[0-9.]+' | head -1)"
SUBNET="$(echo "$LAN_IP" | awk -F. '{print $1"."$2"."$3".0/24"}')"
[[ -z "$SUBNET" ]] && SUBNET="192.168.0.0/24"

if command -v firewall-cmd >/dev/null 2>&1; then
  if [[ "$APPLY_FIREWALL" == "1" ]]; then
    firewall-cmd --set-default-zone=drop >/dev/null
    firewall-cmd --permanent --zone=drop \
      --add-rich-rule="rule family=\"ipv4\" source address=\"${SUBNET}\" port port=\"8765\" protocol=\"tcp\" accept" >/dev/null
    firewall-cmd --reload >/dev/null
    echo "✅ firewalld: entrada DROP + puerto 8765 permitido desde ${SUBNET}."
  else
    echo "ℹ️  firewalld detectado. Para blindar la entrada: añade --firewall"
  fi
elif command -v ufw >/dev/null 2>&1; then
  if [[ "$APPLY_FIREWALL" == "1" ]]; then
    ufw --force reset >/dev/null
    ufw default deny incoming >/dev/null
    ufw default allow outgoing >/dev/null
    ufw allow from "$SUBNET" to any port 8765 proto tcp >/dev/null
    ufw --force enable >/dev/null
    echo "✅ ufw: entrada denegada + 8765 permitido desde ${SUBNET}."
  else
    echo "ℹ️  ufw detectado. Para blindar la entrada: añade --firewall"
  fi
else
  echo "ℹ️  No se detectó firewalld ni ufw."
fi

echo
echo "🎯 SLONE™ Hardening completado. El escudo integrado de la app (Ajustes Pro) ya"
echo "   bloquea escaneos, aplica rate-limit y registra intrusiones en los puertos"
echo "   8765 (relay de vídeo) y 8766 (webhooks de pago)."
