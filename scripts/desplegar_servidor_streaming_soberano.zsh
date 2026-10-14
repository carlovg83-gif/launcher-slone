#!/usr/bin/env zsh
# ══════════════════════════════════════════════════════════════════════════
# SLÖNE™ STREAMING ENGINE DEPLOYMENT SCRIPT
# ══════════════════════════════════════════════════════════════════════════
# Despliega el servidor de streaming de ultra-baja latencia localmente
# o en instancias cloud (Google Cloud / Hetzner / AWS)
# ══════════════════════════════════════════════════════════════════════════

set -e

PROJECT_DIR="/home/slone/slocast 1.0"
STREAMING_DIR="${PROJECT_DIR}/backend/streaming"

echo "\n👑 [SLÖNE STREAMING] Inicializando Nodo de Streaming Soberano..."

if ! command -v podman &>/dev/null && ! command -v docker &>/dev/null; then
    echo "⚙️ Instalando Podman en Fedora mediante dnf..."
    sudo dnf install -y podman podman-compose
fi

CONTAINER_CMD="podman"
if command -v docker &>/dev/null; then
    CONTAINER_CMD="docker"
fi

echo "🚀 Iniciando contenedor MediaMTX con ${CONTAINER_CMD}..."
cd "${STREAMING_DIR}"

if command -v "${CONTAINER_CMD}-compose" &>/dev/null; then
    "${CONTAINER_CMD}-compose" up -d
else
    # Ejecución directa si no está instalado compose
    ${CONTAINER_CMD} run -d \
        --name slone-streaming-origin \
        --restart unless-stopped \
        -p 8554:8554 \
        -p 1935:1935 \
        -p 8888:8888 \
        -p 8889:8889 \
        -p 8889:8889/udp \
        -p 9997:9997 \
        -v "${STREAMING_DIR}/mediamtx.yml:/mediamtx.yml:ro" \
        bluenviron/mediamtx:latest-ffmpeg
fi

echo "\n======================================================================="
echo "✅ SERVIDOR DE STREAMING SOBERANO SLÖNE EN LÍNEA"
echo "======================================================================="
echo "📡 Protocolos activos:"
echo "   • LL-HLS (Low Latency HLS < 1s): http://localhost:8888/{canal}/"
echo "   • WebRTC (WHEP Cero Retardo):   http://localhost:8889/{canal}/"
echo "   • RTSP Ingesta Directa:          rtsp://localhost:8554/{canal}"
echo "   • REST API Control:              http://localhost:9997/v3/paths/list"
echo "=======================================================================\n"
