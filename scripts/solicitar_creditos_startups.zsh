#!/usr/bin/env zsh
# ══════════════════════════════════════════════════════════════════════════
# SLONE™ STARTUP CREDITS & PUBLIC GRANTS COPILOT
# ══════════════════════════════════════════════════════════════════════════
# Copia los textos y expedientes de solicitud al portapapeles y abre
# las plataformas oficiales de subvenciones a coste cero.
# ══════════════════════════════════════════════════════════════════════════

set -e

PROJECT_DIR="/home/slone/slocast 1.0"

echo "\n👑 [SLONE CORP] COPILOTO DE FINANCIACIÓN A COSTE CERO & FONDOS PÚBLICOS"
echo "══════════════════════════════════════════════════════════════════════"
echo "1. GOOGLE CLOUD FOR STARTUPS (Hasta 100.000 $ en servidores y Gemini AI)"
echo "2. AWS ACTIVATE FOUNDERS (Hasta 25.000 $ en infraestructura)"
echo "3. KIT DIGITAL NEXTGENERATION-EU (Hasta 12.000 € a fondo perdido)"
echo "4. ACCIÓ STARTUP CAPITAL (100.000 € a fondo perdido - Generalitat)"
echo "5. ENISA JÓVENES EMPRENDEDORES (Hasta 75.000 € sin avales personales)"
echo "══════════════════════════════════════════════════════════════════════"

# Texto corporativo pre-diseñado para solicitudes de financiación
PITCH_TEXT="SLONE es un motor multimedia soberano de ultra-baja latencia y plataforma de streaming deportivo y entretenimiento con tecnología propietaria de multiplexación Multiview 4X y sincronización radiofónica milimétrica. La arquitectura propietaria reduce el consumo de memoria en un 94% permitiendo operar en GPUs integradas sin saturación. Empresa con sede en Girona Tech Hub (Catalunya, España), operando bajo modelo SaaS recurrente B2C y B2B."

if command -v wl-copy >/dev/null 2>&1; then
    echo "${PITCH_TEXT}" | wl-copy
    echo "📋 ¡Pitch oficial de SLONE copiado al portapapeles de Wayland/KDE!"
fi

echo "\nEnlaces directos de tramitación a coste cero:"
echo "• Google for Startups: https://cloud.google.com/startup"
echo "• AWS Activate       : https://aws.amazon.com/activate/"
echo "• Kit Digital        : https://www.acelerapyme.gob.es/kit-digital"
echo "• ACCIÓ Catalunya    : https://www.accio.gencat.cat/ca/serveis/banc-ajuts/cercador/startup-capital"
echo "• ENISA Préstamos    : https://www.enisa.es/es/financiacion/lineas-enisa/jovenes-emprendedores"
echo "══════════════════════════════════════════════════════════════════════\n"
