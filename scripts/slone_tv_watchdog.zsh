#!/usr/bin/env zsh
# ══════════════════════════════════════════════════════════════════════════
# SLÖNE TV WATCHDOG & LAUNCHER GUARDIAN DAEMON
# ══════════════════════════════════════════════════════════════════════════
# 1. Supervisa conexión ADB y el servidor hub local
# 2. Intercepta el botón HOME de Xiaomi para mantener siempre SLÖNE en pantalla
# ══════════════════════════════════════════════════════════════════════════

SCRIPT_DIR="${0:A:h}"
BASE_DIR="${SCRIPT_DIR:h}"
ADB_BIN="/home/slone/.local/bin/adb"
TV_IP="192.168.1.135:5555"
PORT=8765

check_health() {
    # 1. Verificar proceso de servidor_tv_hub.py
    if ! pgrep -f "servidor_tv_hub.py" >/dev/null 2>&1; then
        echo "[$(date +'%H:%M:%S')] ⚠️ [WATCHDOG] Servidor TV Hub caído. Relanzando en segundo plano..."
        nohup python3 "$BASE_DIR/scripts/servidor_tv_hub.py" >/dev/null 2>&1 &
        sleep 2
        echo "[$(date +'%H:%M:%S')] ✅ [WATCHDOG] Servidor TV Hub relanzado."
    fi

    # 2. Verificar enlace ADB con Xiaomi TV
    if ! "$ADB_BIN" devices | grep -q "$TV_IP.*device"; then
        "$ADB_BIN" connect "$TV_IP" >/dev/null 2>&1
        sleep 1
    fi
}

enforce_slone_home() {
    local focused=$("$ADB_BIN" -s "$TV_IP" shell "dumpsys window | grep mCurrentFocus" 2>/dev/null)
    # Si la pantalla actual es el escritorio con publicidad de Xiaomi / Google TV
    if [[ "$focused" =~ "com.google.android.apps.tv.launcherx" ]]; then
        "$ADB_BIN" -s "$TV_IP" shell am start -n com.phlox.tvwebbrowser/.activity.main.MainActivity -a android.intent.action.VIEW -d "http://192.168.1.145:$PORT/launcher/" >/dev/null 2>&1
    fi
}

echo "🛡️ [SLÖNE WATCHDOG] Iniciando guardián de escritorio y monitor en segundo plano..."
check_health

if [[ "$1" == "--daemon" || "$1" == "-d" ]]; then
    cycle=0
    while true; do
        sleep 1.5
        enforce_slone_home
        ((cycle++))
        if (( cycle >= 20 )); then
            check_health >/dev/null 2>&1
            cycle=0
        fi
    done
fi
