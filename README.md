# 👑 SLÖNE™ SOVEREIGN OS · FLAGSHIP SMART TV & MEDIA ENGINE

> **Plataforma Integral de Entretenimiento Soberano para Xiaomi TV, Android TV, Linux y Web.**
> Ecosistema multimedia de ultra-lujo con conmutación de audio en caliente, baja latencia, navegador privado y soporte para **Stitch Design System**.

---

## ⚡ Novedades Flagship (SLÖNE TV OS)

- **`SLÖNE TV Launcher OS`** (`app/web_portal/launcher/index.html`): Sistema operativo de salón de serie optimizado para Xiaomi TV, PatchWall y Fire TV con navegación por cruceta (D-Pad).
- **`SLÖNE Shield Web Browser™`**: Motor de búsqueda y navegación privada integrado estilo **Brave / Firefox** con bloqueo de rastreadores, adblock DNS y accesos rápidos deportivos (Flashscore, SPORT, Mundo Deportivo).
- **`SLÖNE Tube™`**: Módulo de YouTube 4K integrado 100% libre de publicidad con SponsorBlock y lanzamiento directo en la app nativa **SmartTube 4K**.
- **`Multiview Stadium™ 4X`**: Cuadrícula de 4 emisiones en directo simultáneas con cambio instantáneo entre modo 4X y 1X Pantalla Completa.
- **`FanAudio™ Culer Matrix`**: Matriz de selección de comentaristas (RAC1 Joan Maria Pou, Catalunya Ràdio, Ambiente de Estadio Puro sin narradores, SER, COPE, Marca) con decalaje milimétrico ajustable.
- **`Ecosystem Dock`**: Lanzamiento nativo vía ADB de Google Play Store, SmartTube, TiviMate VIP, Aptoide TV, Netflix, Prime Video, 3Cat / TV3, RTVE Play, atresplayer y Ajustes de TV.
- **`Stitch Integration Ready`**: Especificación [`stitch.json`](stitch.json) y [`DESIGN_SYSTEM.md`](DESIGN_SYSTEM.md) para sincronización con herramientas de diseño UI.


---

## 📁 Estructura

```
SLOCAST/
├── app/                     ← NÚCLEO FUNCIONAL (idéntico al original)
│   ├── slocast.py           · App principal (menú lateral, 7 páginas)
│   ├── slone_auth.py        · Autenticación biométrica (fprintd)
│   ├── slone_epg.py         · Motor EPG (guía XMLTV: descarga, parseo, ahora/siguiente)
│   ├── xtream_parser.py     · Cliente Xtream Codes + parser M3U Plus
│   ├── slone_meta.py        · Motor de metadatos IA (API DeepSeek)
│   ├── README.md, SECURITY.md, playstore_listing.md
│   ├── assets/              · logo.png, slone_logo.png, synq_logo.png
│   ├── web_portal/          · index.html (PWA), manifest.json, assets/ (4 img)
│   └── __pycache__/         · bytecode compilado
├── docs/
│   ├── implementation_plan.md / walkthrough.md   · contexto del proyecto
│   ├── *.metadata.json
│   └── antigravity_historial/                    · logs/mensajes/tareas de Antigravity
├── branding/                · logos y mockups de marca (+ user_uploaded/)
├── launchers/               · integración de escritorio
│   ├── slocast.desktop, slone.desktop
│   ├── bin/slocast, bin/slone
│   └── instalar_en_sistema.sh                    · instalador opcional (NO ejecutado)
├── icons/                   · slocast.png, slone.png (1024×1024)
├── config/
│   ├── SLOCaststaterc       · estado de KDE (archivos recientes)
│   └── slo_webcast/config.json
├── backups/                 · historial slocast.py.bak + .bak_v4 … .bak_v9
├── legacy/                  · versiones/prototipos anteriores
│   ├── slo_app.py           · "SLO Cast v5.0" (WebEngine)
│   ├── slone_player/main.py · prototipo GTK4/GStreamer
│   ├── desbloquear_slone.py · desbloqueo biométrico PAM
│   └── slone_prompt.txt     · guía/prompt original (texto)
├── keystore/
│   └── slone.keystore       · keystore de firma (binario)
└── INFORME_PRUEBAS.md       · resultado de todas las pruebas
```

---

## 🗺️ Rutas de origen de cada archivo

| En `SLOCAST/` | Ruta original |
|---|---|
| `app/*` | `~/.gemini/antigravity/scratch/slocast/` |
| `docs/implementation_plan.md`, `walkthrough.md` | `~/.gemini/antigravity/brain/5bba4fad-…/` |
| `docs/antigravity_historial/` | `~/.gemini/antigravity/brain/5bba4fad-…/.system_generated/` |
| `branding/*.jpg`, `branding/user_uploaded/` | `~/.gemini/antigravity/brain/5bba4fad-…/` |
| `launchers/*.desktop` | `~/.local/share/applications/` |
| `launchers/bin/*` | `~/.local/bin/` |
| `icons/*` | `~/.local/share/icons/` |
| `config/SLOCaststaterc` | `~/.local/state/SLOCaststaterc` |
| `config/slo_webcast/config.json` | `~/.config/slo_webcast/config.json` |
| `legacy/slo_app.py` | `~/slo_app.py` |
| `legacy/slone_player/main.py` | `~/slone_player/main.py` |
| `legacy/desbloquear_slone.py` | `~/Descargas/desbloquear_slone.py` |
| `legacy/slone_prompt.txt` | `~/slone` |
| `keystore/slone.keystore` | `~/slone.keystore` |

---

## ▶️ Cómo se ejecuta la app

El lanzador de sistema (`~/.local/bin/slocast` y `~/.local/bin/slone`) ejecuta:

```bash
python3 ~/.gemini/antigravity/scratch/slocast/slocast.py
```

> ✅ **Rutas portables.** El código ya **no** usa rutas absolutas a Antigravity ni a
> `$HOME`: el portal web, los assets, el icono y el socket IPC se resuelven
> relativos a `__file__` y al directorio temporal del sistema
> (`tempfile.gettempdir()`). La app funciona desde cualquier carpeta.

**Instalación opcional** (apuntando a esta carpeta consolidada): ejecuta manualmente
`bash launchers/instalar_en_sistema.sh`. No se ha ejecutado.

---

## 🧩 Dependencias (todas presentes en el sistema)

| Dependencia | Estado |
|---|---|
| Python 3.14.7 | ✅ |
| PyQt6 6.11 · PyQt6-WebEngine · PyQt6-sip | ✅ |
| PyChromecast 14.0.10 · zeroconf | ✅ |
| python-pam · requests | ✅ |
| `mpv` (binario, motor de vídeo) | ✅ `/usr/bin/mpv` |
| `python-vlc` (motor VLC alternativo) | ✅ `pip install --user python-vlc` |
| `fprintd-verify` (huella dactilar) | ✅ `/usr/bin/fprintd-verify` |
| `vlc`, `ffmpeg` (alternativas) | ✅ |
| PyGObject 3.56 (prototipo GTK4 en `legacy/`) | ✅ |
| EPG / Xtream / DeepSeek (módulos internos) | ✅ solo stdlib (`urllib`, `gzip`, `xml.etree`) |

---

## ✅ Estado

Ver **[INFORME_PRUEBAS.md](INFORME_PRUEBAS.md)**: integridad **TODO_OK**,
compilación 5/5, import headless OK, smoke test del relay OK.

---
## 🔓 Desbloqueo / Acceso (si la huella no te reconoce)

El enclave biométrico admite **tres formas de entrar**:

1. **Huella dactilar** (`fprintd-verify`).
2. **Contraseña de respaldo** — botón **«Usar contraseña»** en el diálogo de
   acceso. Verifica tu **contraseña del sistema** por PAM. Se controla con
   `directiva_maestra.contrasena_respaldo_activa` (por defecto `true`).
   Si la huella falla, el diálogo **ya no se cierra**: puedes pulsar
   **«Reintentar huella»** o entrar con **«Usar contraseña»**.
3. **Acceso de emergencia** (recuperación si el sensor no responde). Desde una
   terminal:

   ```bash
   # Opción A: variable de entorno
   SLONE_AUTH_BYPASS=1 slocast

   # Opción B: argumento
   slocast --no-auth
   ```

   O desactiva del todo el enclave en `config/slone_control.json`:
   `"enclave_biometrico_activo": false`.

> La contraseña de respaldo se valida con el servicio PAM **`password-auth`**
> (solo `pam_unix`, **sin sensor de huellas**), así que **no espera a la huella**
> mientras escribes. Para máxima portabilidad puedes instalar un servicio PAM
> dedicado (opcional, requiere sudo): `bash scripts/install_pam_service.sh`.

---



## 🛡️ Seguridad & Rendimiento (control total)

### Escudo SLONE (anti‑intrusión, integrado en la app)
El módulo `app/slone_security.py` protege el relay de vídeo (8765) y el webhook
de pagos (8766):

- **Bind seguro por defecto**: el relay escucha solo en `127.0.0.1`. El acceso
  desde la red (para **Chromecast/TV** o el **mando móvil**) es *opt‑in* desde
  *Ajustes Pro → «Permitir acceso LAN»*.
- **Escudo activo**: rate‑limit por IP (120 peticiones/min), bloqueo de
  *path‑traversal* y patrones de inyección, bloqueo de *user‑agents* de
  escáneres (sqlmap, nikto, nmap…) y de métodos no permitidos.
- **Baneo automático**: una IP hostil queda bloqueada 15 min tras 5 abusos.
  Todo se registra en `config/security.log` (botón *«📜 Registro de bloqueos»*).
- **Token LAN**: las rutas sensibles (`/remote`, `/api/cmd`) exigen
  `?token=…` cuando el acceso LAN está activo. Genera/rota el token desde
  *Ajustes Pro → «🔑 Ver/Rotar token LAN»*.

### Webhooks de pago endurecidos
`app/slone_payments.py` ahora **verifica de verdad la firma HMAC** de cada
webhook (antes se calculaba y se ignoraba), aplica *rate‑limit* y limita el
cuerpo a 1 MB. El puerto de escucha es configurable (`pasarela_pagos.webhook_bind`).

### Perfil de máximo rendimiento
El módulo `app/slone_perf.py` detecta tu hardware (CPU, núcleos, RAM, GPU) y
aplica los mejores ajustes de reproducción: **decodificación por hardware**
(`hwdec=auto-safe`), hilos de decodificación, búfer/timeshift óptimos y
desentrelazado automático (50 fps en deportes). Se aplica a **MPV** y **VLC**.
Actívalo/re‑aplícalo en *Ajustes Pro → «🚀 Aplicar perfil máximo rendimiento»*
(ya viene activado por defecto en `config/slone_control.json`).

### Endurecimiento del sistema operativo (opcional, root)
`bash scripts/slone_hardening.sh` — pone el gobernador de CPU en *performance*,
activa **fail2ban** y, con `--firewall`, aplica política de entrada estricta
(DROP) permitiendo solo el acceso LAN al puerto 8765. Ejecuta con `sudo`.

---

## 🆕 Novedades (sesión actual)

1. **Rutas portables** — Eliminadas todas las rutas absolutas (`/home/slone/…`,
   `/tmp/…`) en `slocast.py` y `slone_auth.py`. Todo se resuelve con `__file__`
   y `tempfile`.
2. **Biometría restaurada y conmutable** — `slone_auth.py` recupera el enclave
   completo (diálogo + `fprintd`). Se activa/desactiva desde
   `config/slone_control.json` (`directiva_maestra.enclave_biometrico_activo`).
   Si no hay sensor/huella, la app arranca igual (no bloquea).
3. **Motor de reproducción dual** — MPV (por defecto) y VLC/libvlc, seleccionable
   en **Ajustes Pro**. Requiere `python-vlc` para el motor VLC.
4. **Fuentes públicas de IPTV** — Botón «➕ Añadir M3U» (página de Canales y
   Ajustes) para cargar por URL/archivo y presets de **iptv-org**. Soporte de URLs
   M3U en el cargador asíncrono y memorización de la última fuente.
5. **Configuración central** — Lectura/escritura no destructiva de
   `config/slo_webcast/config.json` (última lista, motor) y
   `config/slone_control.json` (directiva maestra).
6. **EPG (guía de programación)** — Nuevo módulo `slone_epg.py` que descarga y
   parsea guías **XMLTV** (incluye `.xml.gz`), indexa por `tvg-id` y por nombre,
   y muestra *«Ahora / Siguiente»* bajo el reproductor. Presets públicos por país
   (**epgshare01**: ES/UK/FR/DE/IT/PT) y URL personalizada desde *Ajustes Pro*.
   La última guía se recuerda en `config/`.
7. **Xtream Codes** — Nuevo flujo en `xtream_parser.py`: *«🛰 Conectar panel
   Xtream Codes»* (host/usuario/contraseña) desde los menús de fuentes y desde
   Ajustes. Descarga canales **Live** + **VOD**, los exporta a M3U (con
   `tvg-id`/`tvg-logo`/`group-title`) y los integra en la misma clasificación por
   países/categorías. Credenciales guardadas en `config/`.
8. **Metadatos IA con DeepSeek** — Nuevo módulo `slone_meta.py` (cliente
   compatible con OpenAI: `https://api.deepseek.com/chat/completions`, modelos
   oficiales `deepseek-flash` y `deepseek-v4-pro`). El modo *razonamiento* se
   **desactiva** para metadatos (más rápido y barato) y se solicita **JSON
   estricto**. Botón *«✨ IA»* para enriquecer el canal/película actual
   (título, año, género, sinopsis) y *«🧪 Probar conexión»* en *Ajustes Pro*.
   **Solo falta pegar tu clave**: en *Ajustes Pro → DeepSeek API key* (botón
   👁 para verla, 💾 Guardar IA). Alternativas: variable `$DEEPSEEK_API_KEY`
   o copiar `config/deepseek.env.example` → `config/deepseek.env`. La clave se
   guarda con permisos `0600`. Consíguela en
   <https://platform.deepseek.com/api_keys>.
9. **Corrección de seguridad** — Bloqueado *path traversal* en `/assets/` del
   relay HTTP (ahora devuelve 403 fuera del directorio web). Los clientes del
   relay ya no se desconectan al cambiar de canal. El dispositivo de Cast es
   configurable (`cast_name`/`cast_ip` en `config/`).
10. **Acceso robusto (anti‑bloqueo)** — El enclave biométrico ahora incluye
    **contraseña de respaldo** (botón «Usar contraseña», validada por PAM
    `password-auth`, **sin esperar la huella**) y, si la huella no coincide, el
    diálogo **no se cierra**: puedes reintentar o usar la contraseña. Además hay
    **acceso de emergencia** con `SLONE_AUTH_BYPASS=1 slocast` o
    `slocast --no-auth`. Detalles en **🔓 Desbloqueo / Acceso**.
11. **Escudo de seguridad SLONE** — Nuevo módulo `app/slone_security.py`:
    bind a `127.0.0.1` por defecto, rate‑limit por IP, bloqueo de patrones de
    ataque y *user‑agents* de escáneres, baneo automático (15 min tras 5 abusos)
    y registro en `config/security.log`. Detectado dentro del relay HTTP.
    Detalles en **🛡️ Seguridad & Rendimiento**.
12. **Webhooks de pago verificados** — `app/slone_payments.py` valida la firma
    **HMAC** (antes se ignoraba), aplica rate‑limit y limita el cuerpo a 1 MB;
    bind seguro configurable.
13. **Perfil de máximo rendimiento** — Nuevo módulo `app/slone_perf.py`
    (detección de hardware + mejores flags de MPV/VLC), aplicable desde
    *Ajustes Pro*. Incluye `scripts/slone_hardening.sh` (gobernador CPU,
    fail2ban y firewall opcional).


---

© 2026 SLONE ENTERPRISES LLC. Documento de consolidación generado automáticamente.
