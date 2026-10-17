# 👑 CLAUDE.md · PROTOCOLO DE DESARROLLO SLÖNE SOVEREIGN OS

Este archivo define las directrices maestras de arquitectura, desarrollo y seguridad para **Claude Code** y asistentes de IA que operen en este repositorio.

> 📡 **COORDINACIÓN INTER-ASISTENTES (Single Source of Truth)**:
> Este proyecto mantiene su estado vivo, red y hardware sincronizados en [`PROJECT_STATE.md`](file:///home/slone/slocast%201.0/PROJECT_STATE.md).
> **OBLIGATORIO**: Lee `PROJECT_STATE.md` al iniciar para conocer la IP activa, estado de ADB y servicios. Al finalizar cualquier cambio o solución técnica, actualiza `PROJECT_STATE.md` para que los demás asistentes (Antigravity, Gemini, Claude Desktop) continúen sin pérdida de contexto.

---

## 🏛️ Identidad y Filosofía Universal de SLÖNE
- **Ecosistema**: SLÖNE™ Sovereign Media Engine & TV OS.
- **Misión Universal**: Eliminar la publicidad invasiva, el rastreo y el bloatware en el salón. Diseñado para TODOS los usuarios y compatible con CUALQUIER pantalla (Android TV, Google TV, Fire TV, webOS, Tizen, PC y móviles vía PWA). Inspirado en la soberanía y limpieza de herramientas como Brave, SmartTube y SponsorBlock.
- **Sin sesgos**: Proyecto global y abierto. Ni marcas exclusivas (no solo Xiaomi), ni clubes deportivos específicos, ni limitaciones territoriales.
- **Entorno de Desarrollo y Pruebas**: Fedora 44 Linux · ThinkPad X390 · Banco de pruebas local en `192.168.1.135:5555`.

---

## ⚙️ Reglas de Arquitectura y Ejecución
1. **Lenguaje y Tono**: Todo en Castellano de España (`es_ES`). Tono ejecutivo, directo, técnico y de alta eficiencia.
2. **Shell**: Exclusivamente ZSH. No utilizar sintaxis específica de Bash ni hacer referencia a `.bashrc`.
3. **Seguridad en Ficheros**: Antes de sobrescribir archivos existentes de configuración, crear copia `.bak` (`cp archivo archivo.bak`).
4. **Integridad de Datos**: Prohibido borrar bases de datos, pedidos de clientes o listas M3U maestras.
5. **Secretos y Seguridad**: Nunca commitear `.env`, claves criptográficas en `keystore/`, pedidos de clientes o credenciales privadas de IPTV (protegidos en `.gitignore`).

---

## 🧩 Componentes del Repositorio

- **`app/web_portal/launcher/index.html`**: Interfaz Universal Web/PWA para Smart TV, PC y móviles:
  - *SLÖNE Shield Browser*: Acceso privado y bloqueador de rastreadores estilo Brave Shields.
  - *SLÖNE Tube*: Reproducción de vídeo sin publicidad con salto automático de patrocinios (SponsorBlock).
  - *Multiview 4X*: Multiventana de hasta 4 señales simultáneas HLS de baja latencia.
  - *FanAudio Universal*: Sincronización milimétrica de pistas de audio externas y radios sobre emisiones en directo con control de decalaje (+/- ms).
  - *Universal Dock*: Accesos directos a apps nativas en televisores conectados.
  - *Carruseles Globales*: Canales organizados por categorías universales (Deportes Internacionales, Motor, Cine, Series, Noticias y TDT).
- **`scripts/servidor_tv_hub.py`**: Servidor daemon autónomo de alta velocidad (puerto 8765):
  - Sirve el launcher PWA, el catálogo de canales en JSON (`/api/tv/ceo_catalog`), listas M3U, control remoto ADB de apps (`/api/tv/launch`, `/api/tv/open_url`, `/api/tv/open_smarttube`).
- **`platforms/android/slone-tv-launcher`**: Motor nativo Android TV (Kotlin + Jetpack Compose for TV):
  - Navegación universal por control remoto físico (D-Pad para cualquier mando de TV).
  - Tema Obsidian & Golden Sovereignty (`#D4AF37`) con foco dinámico de 4dp.
  - Compatible con Android TV, Google TV, Fire TV Stick, Sony, TCL, Philips, Xiaomi y TV Boxes genéricos.
- **`dist/slone-tv-launcher-debug.apk`**: Binario compilado listo para instalar en cualquier televisor.
- **`scripts/gestionar_tv_launcher.zsh`**: Script para compilar, instalar vía ADB y conmutar el launcher en dispositivos de prueba (`./scripts/gestionar_tv_launcher.zsh build | deploy | slone | normal`).
- **`stitch.json` & `DESIGN_SYSTEM.md`**: Manifiesto y especificación de tokens para Google Stitch y herramientas de diseño UI.
- **`app/slocast.py`**: Aplicación de escritorio nativa PyQt6 con reproductor dual MPV IPC y VLC.

---

## 🧪 Comandos de Prueba y Validación

```zsh
# 1. Validar sintaxis Python en todo el repositorio
python3 -m py_compile app/*.py scripts/*.py

# 2. Ejecutar la suite completa de pruebas unitarias y de integración (10 tests)
python3 scripts/test_suite_completa.py

# 3. Validar el núcleo de licencias y criptografía Ed25519
python3 scripts/test_licencias.py

# 4. Validar el backend Node.js
node --check backend/server.js && node --test backend/test.mjs

# 5. Comprobar estado del servidor TV Hub
curl -s http://127.0.0.1:8765/api/status
```

© 2026 SLÖNE ENTERPRISES LLC. TODOS LOS DERECHOS RESERVADOS.
