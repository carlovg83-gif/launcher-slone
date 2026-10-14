# 📡 PLAN MAESTRO DE ARQUITECTURA: API UNIFICADA Y MOTOR DE REPRODUCCIÓN SLOCAST 1.0
══════════════════════════════════════════════════════════════════════════
> **Versión:** 1.0.0 Sovereign Edition  
> **Entorno:** Fedora 44 Linux · KDE Plasma 6 · ZSH · ThinkPad X390 (Intel Core i7-8665U / 16 GB RAM)  
> **Objetivo:** Arquitectura de referencia de alta disponibilidad para la API central y el reproductor multimedia ultra-resiliente.

---

## 1. Visión y Objetivos del Sistema

SLOCAST 1.0 es un ecosistema soberano de transmisión multimedia e IPTV de alto rendimiento diseñado para proporcionar:
1. **Cero Retardo y Cero Cortes:** Reproducción satelital en tiempo real con latencia inferior a 1 segundo y watchdog anti-congelamiento.
2. **Selector Multi-Audio en Vivo:** Conmutación sin interrupciones entre pistas de audio de televisión, radio satelital y versión original.
3. **API Desacoplada y Soberana:** Backend en Node.js puro sin dependencias externas, responsable del licenciamiento criptográfico HMAC-SHA256, telemetría, gestión de listas de canales y control remoto.
4. **Reproductor Nativo Optimizado para KDE Plasma 6:** Integración en Wayland/XWayland con aceleración por hardware (VA-API / Mesa Intel UHD 620).
5. **Control Ubicuo:** Mando a distancia PWA accesible desde cualquier smartphone o tablet en la red local y transmisión 1-clic a Xiaomi TV.

---

## 2. Arquitectura de la API (Backend Central)

```
                       ┌────────────────────────────────────────┐
                       │        SLOCAST CLIENTES (UI/PWA)       │
                       └───────────────────┬────────────────────┘
                                           │ HTTP/REST + CORS
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      SLOCAST SOVEREIGN API SERVER (Puerto 8766)                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐│
│  │   SISTEMA Y TELEMETRÍA│  │  LICENCIAS Y PAGOS    │  │ REPRODUCCIÓN & STREAM ││
│  │   /health             │  │  /api/v1/plans        │  │ /api/v1/playback/ctrl ││
│  │   /api/v1/system/stat │  │  /api/v1/license/verif│  │ /api/v1/playback/stat ││
│  └───────────────────────┘  │  /api/v1/webhook/pay  │  │ /api/v1/stream/check  ││
│                             └───────────────────────┘  └───────────────────────┘│
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                           GESTIÓN DE CANALES Y EPG                        │  │
│  │   GET /api/v1/channels (filtros, categorías, búsqueda)                    │  │
│  │   POST /api/v1/channels/load (importación masiva M3U / Xtream)            │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │       SEGURIDAD: Rate Limiter Token-Bucket + Anti-Tamper HMAC-SHA256       │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Módulos de la API
1. **Núcleo Criptográfico de Licencias:**
   - Estructura: `SLONE-<PLAN>-<AAMMDD>-<FIRMA16>`.
   - Firma determinista HMAC-SHA256 derivada de `SLONE_LICENSE_SECRET`.
   - Autoverificación fuera de línea sin obligar a conexión permanente con servidores de terceros.
   - Autocaducidad con protección contra desfases horarios y falsificación.

2. **Control de Reproducción (Playback API):**
   - `GET /api/v1/playback/status`: Proporciona telemetría del canal activo, volumen (0-100), estado de mute, motor (`mpv`/`vlc`), pistas de audio disponibles y pista seleccionada.
   - `POST /api/v1/playback/control`: Ejecuta comandos de transporte (`play`, `pause`, `toggle`, `next`, `prev`, `set_volume`, `mute`, `select_channel`, `set_audio`).

3. **Catálogo de Canales y Validador de Streams:**
   - `GET /api/v1/channels`: Recupera el repertorio indexado con soporte para filtrado por categoría (`Nacionales`, `Deportes`, `Cine`, `Noticias`) y búsqueda por texto.
   - `POST /api/v1/stream/check`: Realiza sondeos HTTP HEAD no bloqueantes para medir latencia y validar la disponibilidad del stream antes de sintonizarlo.

---

## 3. Arquitectura del Reproductor Desktop (SLOCAST Engine)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       SLOCAST DESKTOP PLAYER (PyQt6)                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌────────────────────────────────────────┐ ┌────────────────────────────────┐  │
│  │           INTERFAZ DE USUARIO          │ │       SERVICIOS INTEGRADOS     │  │
│  │  • Estilo VR46 Soberano (#000 + #E3FF) │ │  • Biometría fprintd + PAM     │  │
│  │  • Selector de Canales por Categorías  │ │  • Escudo Anti-Intrusión SHIELD│  │
│  │  • Dock de Control y Sliders Fluidos   │ │  • Perfil Hardware Intel UHD620│  │
│  │  • Panel EPG Guía de Programas         │ │  • Servidor Relay HTTP :8765   │  │
│  └───────────────────┬────────────────────┘ └────────────────────────────────┘  │
│                      │                                                          │
│                      ▼                                                          │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                     MOTOR DE REPRODUCCIÓN MULTI-ENGINE                    │  │
│  │                                                                           │  │
│  │   ┌───────────────────────────────────┐ ┌─────────────────────────────┐   │  │
│  │   │      MPV ENGINE (Por defecto)     │ │     LIBVLC (Fallback)       │   │  │
│  │   │  • IPC Socket /tmp/slone_mpv.sock │ │  • libvlc embedded surface  │   │  │
│  │   │  • --profile=low-latency          │ │  • network-caching=1000     │   │  │
│  │   │  • --cache=yes (128 MB Demuxer)   │ │  • audio track switcher     │   │  │
│  │   │  • --hwdec=auto-safe (VA-API)     │ └─────────────────────────────┘   │  │
│  │   └───────────────────────────────────┘                                   │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Decisiones Clave de Ingeniería en Fedora 44 + KDE Plasma 6
- **Incrustación de Vídeo Robusta:** En Wayland nativo, incrustar procesos externos mediante `winId()` abre habitualmente una ventana externa separada. Para garantizar vídeo embebido impecable, la aplicación arranca forzando `QT_QPA_PLATFORM=xcb` para comunicarse mediante XWayland con `WA_NativeWindow`.
- **Buffer de Resiliencia Zero-Freeze:**
  - Búfer de demuxer de 128 MB con 64 MB de memoria hacia atrás (timeshift instantáneo).
  - `--cache-secs=1` y `--demuxer-readahead-secs=1` para mantener sincronización estricta con el directo satélite.
- **Selector de Audio Multi-Pista:**
  - Interroga el socket IPC de MPV periódicamente tras sintonizar para identificar pistas (`audio/es`, `audio/ca`, `audio/en`).
  - Permite conmutar con un solo clic o atajo de teclado sin recargar el flujo.

---

## 4. Estructura Organizada del Proyecto `slocast 1.0`

```text
/home/slone/slocast 1.0/
├── app/                        # Aplicación de escritorio y lógica central
│   ├── slocast.py              # Reproductor nativo insignia (PyQt6 + MPV/VLC)
│   ├── slone_license_core.py   # Criptografía pura de licencias HMAC-SHA256
│   ├── slone_licensing.py      # Capa de licenciamiento e interfaz de usuario
│   ├── slone_auth.py           # Guardián biométrico (fprintd + PAM)
│   ├── slone_security.py       # Escudo de seguridad (Rate limit, IP filter)
│   ├── slone_perf.py           # Detección de hardware y perfil ThinkPad X390
│   ├── slone_epg.py            # Motor de guía electrónica de programas XMLTV
│   ├── slone_meta.py           # Metadatos de películas y series (TMDB)
│   ├── slone_payments.py       # Pasarelas de pago y webhooks
│   ├── slone_vpn.py            # Selector y monitor de VPN/Proxy
│   ├── xtream_parser.py        # Parser para Xtream Codes y M3U Plus
│   ├── assets/                 # Iconos e imágenes del reproductor
│   └── web_portal/             # Portal PWA instalable (Service Worker + Manifest)
├── backend/                    # Servidor de API Unificado
│   ├── server.js               # Servidor Node.js puro (Licencias, Playback, Streams)
│   ├── test.mjs                # Suite de pruebas automatizadas del backend
│   ├── package.json            # Manifiesto de Node
│   └── data/                   # Almacén local persistente (licencias y canales)
├── config/                     # Configuración y secretos
│   ├── slone_control.json      # Directiva maestra del sistema
│   ├── secrets.env.example     # Plantilla de variables de entorno
│   └── pam.d/                  # Configuración de respaldo PAM
├── docs/                       # Documentación técnica y arquitectura
│   ├── PLAN_ARQUITECTURA_API_Y_PLAYER.md  # Este plan maestro
│   ├── SLOCAST_2.0.md          # Especificación de seguridad y bóveda
│   ├── BOVEDA.md               # Guía de cifrado soberano
│   └── PROJECT_STRUCTURE.md    # Estructura del repositorio
├── launchers/                  # Lanzadores para el sistema operativo
│   ├── bin/slocast             # Script ejecutable portable ZSH
│   ├── bin/slone               # Alias ejecutable ZSH
│   ├── slocast.desktop         # Acceso directo para el menú de KDE Plasma 6
│   └── instalar_en_sistema.sh  # Script de instalación en ~/.local
├── scripts/                    # Scripts de mantenimiento y pruebas
│   ├── test_suite_completa.py  # Suite de pruebas integral (Python + GUI + Node)
│   ├── test_licencias.py       # Pruebas unitarias de licencias
│   ├── slone_vault.py          # Bóveda soberana cifrada (gocryptfs)
│   ├── slone_vault.sh          # Wrapper shell para la bóveda
│   ├── slone_hardening.sh      # Endurecimiento del sistema operativo
│   ├── slone_konsole_master.zsh# CLI maestro para Konsole
│   └── rotar_secretos.sh       # Script de rotación de claves secretas
├── keystore/                   # Almacén de firmas y certificados
├── legacy/                     # Archivo histórico de versiones anteriores
└── Makefile                    # Orquestador del proyecto (make test, make app, etc.)
```

---

## 5. Protocolo de Ejecución y Validación

1. **Ejecución de la Suite Completa:**
   ```zsh
   cd "/home/slone/slocast 1.0"
   make test
   ```
2. **Iniciar el Servidor de API:**
   ```zsh
   make backend
   ```
3. **Iniciar el Reproductor Multimedia:**
   ```zsh
   make app
   ```
4. **Instalación en el Sistema (KDE Plasma 6):**
   ```zsh
   cd "/home/slone/slocast 1.0/launchers"
   bash instalar_en_sistema.sh
   ```
