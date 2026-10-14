#!/usr/bin/env zsh
# ══════════════════════════════════════════════════════════════════════════
# SLÖNE™ XIAOMI TV & LAN STREAMING BRIDGE
# ══════════════════════════════════════════════════════════════════════════
# Inicia y monitoriza el servidor local de SLÖNE para Smart TVs y Xiaomi TV
# ══════════════════════════════════════════════════════════════════════════

set -e

PROJECT_DIR="/home/slone/slocast 1.0"
IP_LOCAL=$(ip -4 addr show wlp0s20f3 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' || echo "127.0.0.1")
PUERTO=8765

echo "\n👑 [SLÖNE TV CONNECT] Inicializando Pasarela Multimedia para Xiaomi TV..."
echo "📡 Dirección IP de tu ThinkPad: ${IP_LOCAL}"
echo "🔌 Puerto de servicio:          ${PUERTO}"
echo "══════════════════════════════════════════════════════════════════════════"
echo "📺 CÓMO REPRODUCIR SLÖNE EN TU XIAOMI TV EN 3 PASOS:"
echo "══════════════════════════════════════════════════════════════════════════"
echo "1️⃣  OPCIÓN A (Navegador Web de la Xiaomi TV - Chrome / Puffin / TV Bro):"
echo "    👉 Abre el navegador en la tele y entra en: http://${IP_LOCAL}:${PUERTO}"
echo ""
echo "2️⃣  OPCIÓN B (En TiviMate, IPTV Smarters o VLC de la Xiaomi TV):"
echo "    👉 Añade la Lista M3U: http://${IP_LOCAL}:${PUERTO}/playlist.m3u"
echo ""
echo "3️⃣  OPCIÓN C (Proyección directa por Google Cast):"
echo "    👉 Con SLÖNE abierto en tu ThinkPad, pulsa '📺 Proyectar en Xiaomi TV'."
echo "══════════════════════════════════════════════════════════════════════════\n"

# Comprobar si el servidor SLÖNE ya está corriendo en segundo plano
if ss -tuln | grep -q ":${PUERTO} "; then
    echo "✅ El servidor SLÖNE ya está ACTIVO y transmitiendo en el puerto ${PUERTO}."
else
    echo "🚀 Arrancando pasarela multimedia de SLÖNE..."
    nohup python3 "${PROJECT_DIR}/scripts/servidor_tv_hub.py" > /dev/null 2>&1 &
    sleep 1
fi

echo "🟢 Servidor listo para recibir a tu Xiaomi TV.\n"
