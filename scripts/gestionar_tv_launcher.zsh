#!/usr/bin/env zsh
# ==============================================================================
# SLÖNE TV SUITE - Gestión, Compilación y Despliegue de SLÖNELauncher Android TV
# ==============================================================================
set -e

DIR_PROYECTO="$(cd "$(dirname "$0")/.." && pwd)"
DIR_ANDROID="$DIR_PROYECTO/platforms/android/slone-tv-launcher"
DIR_DIST="$DIR_PROYECTO/dist"
TV_IP="192.168.1.135:5555"
PKG_NAME="com.slone.launcher"
ACT_NAME="com.slone.launcher.MainActivity"
HABITUAL_PKG="com.google.android.apps.tv.launcherx"
HABITUAL_ACT="com.google.android.apps.tv.launcherx.home.HomeActivity"

conectar() {
    echo "📡 Conectando a Xiaomi TV ($TV_IP)..."
    adb connect "$TV_IP" >/dev/null 2>&1 || true
}

case "$1" in
    build|compilar)
        echo "🔨 Compilando SLÖNELauncher Nativo (Compose for TV)..."
        cd "$DIR_ANDROID"
        ./gradlew assembleDebug
        mkdir -p "$DIR_DIST"
        cp "$DIR_ANDROID/app/build/outputs/apk/debug/app-debug.apk" "$DIR_DIST/slone-tv-launcher-debug.apk"
        echo "✅ Compilación completada con éxito."
        echo "📦 Binario generado: $DIR_DIST/slone-tv-launcher-debug.apk"
        ;;
    deploy|instalar)
        conectar
        APK="$DIR_DIST/slone-tv-launcher-debug.apk"
        if [[ ! -f "$APK" ]]; then
            APK="$DIR_ANDROID/app/build/outputs/apk/debug/app-debug.apk"
        fi
        if [[ ! -f "$APK" ]]; then
            echo "❌ No se encontró el APK. Ejecuta primero: ./gestionar_tv_launcher.zsh build"
            exit 1
        fi
        echo "📲 Instalando $APK en Xiaomi TV..."
        adb -s "$TV_IP" install -r "$APK"
        echo "✅ SLÖNELauncher instalado correctamente."
        ;;
    start|slone)
        conectar
        echo "👑 Activando SLÖNELauncher en pantalla de TV..."
        adb -s "$TV_IP" shell cmd package enable "$PKG_NAME" >/dev/null 2>&1 || true
        adb -s "$TV_IP" shell cmd package set-home-activity "$PKG_NAME/$ACT_NAME" >/dev/null 2>&1 || true
        adb -s "$TV_IP" shell am start -n "$PKG_NAME/$ACT_NAME"
        echo "✅ SLÖNELauncher activo."
        ;;
    normal|xiaomi)
        conectar
        echo "🔄 Restaurando interfaz Xiaomi habitual (Google TV)..."
        adb -s "$TV_IP" shell cmd package enable "$HABITUAL_PKG" >/dev/null 2>&1 || true
        adb -s "$TV_IP" shell cmd package set-home-activity "$HABITUAL_PKG/$HABITUAL_ACT" >/dev/null 2>&1 || true
        adb -s "$TV_IP" shell am start -n "$HABITUAL_PKG/$HABITUAL_ACT"
        echo "✅ Xiaomi TV en su estado habitual."
        ;;
    captura|screenshot)
        conectar
        DEST="$DIR_PROYECTO/docs/captura_tv_$(date +%Y%m%d_%H%M%S).png"
        adb -s "$TV_IP" shell screencap -p /sdcard/captura_tv_temp.png
        adb -s "$TV_IP" pull /sdcard/captura_tv_temp.png "$DEST" >/dev/null 2>&1
        adb -s "$TV_IP" shell rm -f /sdcard/captura_tv_temp.png
        echo "📸 Captura guardada en: $DEST"
        ;;
    status)
        conectar
        echo "📺 Enfoque actual en pantalla TV:"
        adb -s "$TV_IP" shell dumpsys window | grep -E "mCurrentFocus|mFocusedApp"
        ;;
    *)
        echo "Uso: $0 [build | deploy | slone | normal | status | captura]"
        echo "  build   -> Compila el APK nativo con Gradle"
        echo "  deploy  -> Instala el APK compilado en la Xiaomi TV"
        echo "  slone   -> Lanza SLÖNELauncher como Home"
        echo "  normal  -> Vuelve al launcher habitual de Xiaomi"
        echo "  status  -> Muestra la actividad en foco"
        echo "  captura -> Toma captura de la TV y la guarda en docs/"
        ;;
esac
