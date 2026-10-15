# 👑 CLAUDE.md · PROTOCOLO DE DESARROLLO SLÖNE SOVEREIGN OS

Este archivo define las directrices maestras de arquitectura, desarrollo y seguridad para **Claude Code** y asistentes de IA que operen en este repositorio.

---

## 🏛️ Identidad y Filosofía de SLÖNE
- **Ecosistema**: SLÖNE™ Sovereign Media Engine & TV OS.
- **Misión**: Sistema operativo de salón de ultra-lujo, hiperdeportivo y sigilo cibernético (*cyber-stealth*), diseñado para eliminar por completo la latencia en transmisiones deportivas en directo, suprimir publicidad invasiva y otorgar soberanía total al usuario.
- **Entorno de Producción**: Fedora 44 Linux · KDE Plasma 6 · ZSH · Xiaomi Mi TV (Android 11 / PatchWall vía ADB LAN en `192.168.1.135:5555`).

---

## ⚙️ Reglas de Arquitectura y Ejecución
1. **Lenguaje y Tono**: Todo en Castellano de España (`es_ES`). Tono ejecutivo, directo, técnico y de alta eficiencia.
2. **Shell**: Exclusivamente ZSH. No utilizar sintaxis específica de Bash ni hacer referencia a `.bashrc`.
3. **Seguridad en Ficheros**: Antes de sobrescribir archivos existentes de configuración, crear copia `.bak` (`cp archivo archivo.bak`).
4. **Integridad de Datos**: Prohibido borrar bases de datos, pedidos de clientes o listas M3U maestras.
5. **Secretos y Seguridad**: Nunca commitear `.env`, claves criptográficas en `keystore/`, pedidos de clientes o credenciales privadas de IPTV (protegidos en `.gitignore`).

---

## 🧩 Componentes del Repositorio

- **`app/web_portal/launcher/index.html`**: Interfaz Flagship del Home Launcher para Xiaomi TV y Smart TV:
  - *SLÖNE Shield Web Browser™*: Buscador privado estilo Brave Shields / Firefox Focus.
  - *SLÖNE Tube™*: YouTube 4K sin publicidad con SponsorBlock y lanzamiento en SmartTube.
  - *Multiview Stadium™ 4X*: 4 señales simultáneas HLS de ultra-baja latencia.
  - *FanAudio™ Culer Matrix*: Sincronización milimétrica de RAC1 (Joan Maria Pou), CatRàdio y Sonido Estadio sin narradores con control de decalaje.
  - *Ecosystem Dock*: Accesos directos a apps nativas de Android TV vía puente ADB.
  - *Carruseles del CEO*: 39.737 canales clasificados en Fútbol, Champions, DAZN, Motor, TDT y Cine.
- **`scripts/servidor_tv_hub.py`**: Servidor daemon autónomo de alta velocidad (puerto 8765):
  - Sirve el launcher PWA, el catálogo de canales en JSON (`/api/tv/ceo_catalog`), listas M3U, control remoto ADB de apps (`/api/tv/launch`, `/api/tv/open_url`, `/api/tv/open_smarttube`).
- **`platforms/android/slone-tv-launcher`**: Motor nativo Android TV (Kotlin + Jetpack Compose for TV):
  - Navegación por hardware D-Pad (control remoto físico de Xiaomi TV).
  - Tema Obsidian & Golden Sovereignty (`#D4AF37`) con foco dinámico de 4dp.
  - Lanzamiento nativo Leanback de SmartTube, TiviMate, 3Cat, Netflix, Prime Video, etc.
- **`dist/slone-tv-launcher-debug.apk`**: Binario compilado listo para instalar.
- **`scripts/gestionar_tv_launcher.zsh`**: Script para compilar, instalar vía ADB y conmutar el launcher de la Xiaomi TV (`./scripts/gestionar_tv_launcher.zsh build | deploy | slone | normal`).
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
