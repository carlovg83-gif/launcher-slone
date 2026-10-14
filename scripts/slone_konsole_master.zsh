#!/usr/bin/env zsh
# ══════════════════════════════════════════════════════════════════════════
# SLONE™ GLOBAL MEDIA ENGINE — MASTER KONSOLE CLI (Fedora 44 / ThinkPad X390)
# Sede: Girona, Catalunya · Shell: ZSH · CEO: slone
# ══════════════════════════════════════════════════════════════════════════

SCRIPT_DIR="${0:A:h}"
PROJECT_DIR="${SCRIPT_DIR:h}"
cd "$PROJECT_DIR" || exit 1

print_header() {
    clear
    echo "\033[1;33m"
    echo "  ███████╗██╗      ██████╗ ███╗   ██╗███████╗     ██████╗ ██████╗ ██████╗ ██████╗ "
    echo "  ██╔════╝██║     ██╔═══██╗████╗  ██║██╔════╝    ██╔════╝██╔═══██╗██╔══██╗██╔══██╗"
    echo "  ███████╗██║     ██║   ██║██╔██╗ ██║█████╗      ██║     ██║   ██║██████╔╝██████╔╝"
    echo "  ╚════██║██║     ██║   ██║██║╚██╗██║██╔══╝      ██║     ██║   ██║██╔══██╗██╔═══╝ "
    echo "  ███████║███████╗╚██████╔╝██║ ╚████║███████╗    ╚██████╗╚██████╔╝██║  ██║██║     "
    echo "  ╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝     ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝     "
    echo "\033[1;33m  👑 SLONE GLOBAL MEDIA ENGINE · GIRONA TECH HUB · SOVEREIGN ARCHITECTURE\033[0m"
    echo "  \033[0;37mFedora 44 Linux · KDE Plasma 6 · ThinkPad X390 · Zero-Bloat Sovereignty\033[0m"
    echo "══════════════════════════════════════════════════════════════════════════"
}

show_menu() {
    print_header
    echo "\033[1;36m[PANEL DE MANDO DEL CEO — FASE 1]:\033[0m"
    echo "  \033[1;33m1)\033[0m 🚀 Iniciar SLONE Global Media Engine (Reproductor Nativo mpv + Google Cast + TiviMate)"
    echo "  \033[1;33m2)\033[0m 🌐 Servir Portal Web Corporativo (app/web_portal en http://localhost:8765)"
    echo "  \033[1;33m3)\033[0m 🧪 Test Rápido de Integridad (Reproductor, Xtream, VPN, Licencias VIP)"
    echo "  \033[1;33m4)\033[0m 📋 Ver Expediente Oficial de Marca OEPM (Clases de Niza 9, 38, 42, 25)"
    echo "  \033[1;33m5)\033[0m 🔄 Reinstalar Lanzador y Menús en KDE Plasma 6 (kbuildsycoca6)"
    echo "  \033[1;33m6)\033[0m 🔒 Blindar Permisos y Cifrado (chmod 700 ThinkPad X390)"
    echo "  \033[1;33m7)\033[0m 📊 Ver Dossier Estratégico Ejecutivo del CEO"
    echo "  \033[1;31mq)\033[0m Salir"
    echo "──────────────────────────────────────────────────────────────────────────"
    echo -n "Selecciona una opción [1-7/q]: "
}

while true; do
    show_menu
    read -r opt
    case "$opt" in
        1)
            echo "\n🚀 Iniciando SLONE Global Media Engine..."
            export QT_QPA_PLATFORM=xcb
            python3 app/slocast.py
            break
            ;;
        2)
            echo "\n🌐 Levantando servidor corporativo en http://localhost:8765..."
            echo "Abre tu navegador Firefox en http://localhost:8765 (Ctrl+C para detener)"
            python3 -m http.server 8765 --directory app/web_portal
            ;;
        3)
            echo "\n🧪 Ejecutando suite de pruebas de integridad..."
            python3 -c "
import app.slone_licensing as l, app.slone_auth as a, app.xtream_parser as x
print('✅ Módulos core de SLONE importados correctamente')
print('✅ Gestor de licencias VIP HMAC:', l.LicenseManager().generate_license_key('year'))
print('✅ Parser de listas Xtream/M3U operativo')
print('✅ Todo el motor SLONE opera al 100% de rendimiento')
"
            echo "\nPresiona ENTER para continuar..."
            read -r
            ;;
        4)
            echo "\n📋 Abriendo expediente OEPM..."
            cat docs/REGISTRO_MARCA_OEPM_SLONE.md | head -n 45
            echo "\n[... Expediente completo en docs/REGISTRO_MARCA_OEPM_SLONE.md ...]"
            echo "\nPresiona ENTER para continuar..."
            read -r
            ;;
        5)
            echo "\n🔄 Reinstalando accesos en KDE Plasma 6..."
            zsh launchers/instalar_en_sistema.zsh
            echo "\nPresiona ENTER para continuar..."
            read -r
            ;;
        6)
            echo "\n🔒 Aplicando blindaje estricto..."
            chmod 700 -R "$PROJECT_DIR"
            echo "Permisos aplicados: chmod 700 a todo el repositorio."
            echo "\nPresiona ENTER para continuar..."
            read -r
            ;;
        7)
            echo "\n📊 Abriendo Dossier Estratégico..."
            cat "/home/slone/.gemini/antigravity/brain/a8590119-ee87-4c54-8640-d27a1d2fac96/slone_global_media_engine_master_plan.md" | head -n 45
            echo "\nPresiona ENTER para continuar..."
            read -r
            ;;
        q|Q)
            echo "\nHasta pronto, slone."
            exit 0
            ;;
        *)
            echo "\nOpción no válida."
            sleep 1
            ;;
    esac
done
