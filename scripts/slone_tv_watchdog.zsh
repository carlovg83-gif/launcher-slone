#!/usr/bin/env zsh
# ══════════════════════════════════════════════════════════════════════════
# SLÖNE™ SOVEREIGN TV WATCHDOG & DAEMON MONITOR
# ══════════════════════════════════════════════════════════════════════════
# Monitoriza la conexión ADB con la Xiaomi TV y el servidor Hub local
# ══════════════════════════════════════════════════════════════════════════

SCRIPT_DIR="${0:A:h}"
BASE_DIR="${SCRIPT_DIR:h}"
ADB_BIN="/home/slone/.local/bin/adb"
TV_IP="192.168.1.135:5555"
PORT=8765

echo "🛡️ [SLÖNE WATCHDOG] Iniciando monitorización soberana..."

# 1. Verificar proceso de servidor_tv_hub.py
if ! pgrep -f "servidor_tv_hub.py" >/dev/null 2>&1; then
    echo "⚠️ [WATCHDOG] Servidor TV Hub caído. Relanzando en segundo plano..."
    nohup python3 "$BASE_DIR/scripts/servidor_tv_hub.py" >/dev/null 2>&1 &
    sleep 2
    echo "✅ [WATCHDOG] Servidor TV Hub relanzado."
else
    echo "✅ [WATCHDOG] Servidor TV Hub activo en puerto $PORT."
fi

# 2. Verificar enlace ADB con Xiaomi TV
if ! "$ADB_BIN" devices | grep -q "$TV_IP.*device"; then
    echo "⚠️ [WATCHDOG] Xiaomi TV desconectada. Reintentando conexión ADB..."
    "$ADB_BIN" connect "$TV_IP" >/dev/null 2>&1
    sleep 1
fi

if "$ADB_BIN" devices | grep -q "$TV_IP.*device"; then
    echo "✅ [WATCHDOG] Xiaomi TV conectada y autenticada ($TV_IP)."
else
    echo "❌ [WATCHDOG] No se pudo establecer conexión con Xiaomi TV en $TV_IP."
fi
