# 🏛️ SLÖNE SOVEREIGN OS · ESTADO VIVO DEL SISTEMA (PROJECT_STATE.md)
> **FUENTE ÚNICA DE VERDAD (Single Source of Truth) para todos los chats y asistentes de IA (Antigravity, Claude Code, Claude Desktop, Ollama).**
> *Cualquier asistente que interactúe con este ecosistema debe leer este archivo y [MASTER_ECOSISTEMA_SLONE.md](file:///home/slone/MASTER_ECOSISTEMA_SLONE.md) antes de comenzar y actualizarlo al completar cambios relevantes.*

---

## 🌍 1. FILOSOFÍA Y ALCANCE UNIVERSAL (REGLAS FUNDAMENTALES)
- **Misión Global**: Resolver un problema que afecta a millones de usuarios: la saturación de publicidad invasiva, el rastreo y la lentitud extrema de las interfaces de televisión y streaming actuales.
- **Solución SLÖNE**: Un ecosistema multimedia soberano, ultra-rápido, limpio y **completamente libre de anuncios** (inspirado en la filosofía de herramientas como Brave, SmartTube y SponsorBlock).
- **Universalidad Total**:
  - **Sin sesgos de marcas ni modelos**: Diseñado para cualquier televisor o dispositivo de salón (Google TV, Android TV, Fire TV Stick, Chromecast, Sony, TCL, Philips, Samsung Tizen, LG webOS) y cualquier navegador en PC o móvil.
  - **Sin sesgos geográficos ni temáticos**: Neutral, abierto a cualquier contenido, deporte, idioma o país. El usuario es el único soberano de lo que sintoniza.
- **Identidad Soberana (No IA Genérica)**:
  - La marca oficial emana exclusivamente de los trazos originales del fundador (artista/grafitero): tipografía caligráfica [`assets/ink_top_white.png`](file:///home/slone/slocast%201.0/app/web_portal/assets/ink_top_white.png) y el glifo de frecuencia continua [`assets/ink_mid_white.png`](file:///home/slone/slocast%201.0/app/web_portal/assets/ink_mid_white.png).
  - Prohibidos logotipos circulares genéricos con números "1".

---

## ⚡ 2. INFRAESTRUCTURA DE DESARROLLO Y BANCO DE PRUEBAS
- **Estación de Desarrollo**: ThinkPad X390 (Intel Core i7-8665U · Fedora 44 Linux · KDE Plasma 6 · ZSH).
  - Conectado en puerto USB-C 2 (Thunderbolt) firme, modo sobremesa permanente.
  - Red Fedora blindada: IPv6 desactivado; DNS Cloudflare (`1.1.1.1`) y Quad9 (`9.9.9.9`).
  - IP Local del ThinkPad: `192.168.1.145`.
  - Centinela de Hardware activo en `http://127.0.0.1:7331` (SSE streaming de temperatura, RAM, batería y LAN 192.168.1.0/24).
- **Dispositivo de Pruebas Físico**:
  - Televisor de pruebas en `192.168.1.135:5555` vía ADB LAN.
  - Ergonomía con mando a distancia físico (cruceta D-Pad y botón central).

---

## 📺 3. ARQUITECTURA TÉCNICA MULTIPLATAFORMA

1. **Motor Android TV Nativo (`platforms/android/slone-tv-launcher`)**:
   - Paquete: `com.slone.launcher` (Actividad: `com.example.slnelauncher.MainActivity`).
   - **Binario de Producción Firmado (Release)**: [`dist/slone-tv-launcher-v1.0.0-release.apk`](file:///home/slone/slocast%201.0/dist/slone-tv-launcher-v1.0.0-release.apk) (**5.8 MB**, R8, keystore RSA-2048 en `keystore/slone_release.keystore`).
   - Catálogo de Apps dinámico mediante `packageManager.queryIntentActivities` (`CATEGORY_LEANBACK_LAUNCHER`).
   - Reproductor nativo integrado con ExoPlayer Media3 (`PlayerScreen.kt`) para HLS/CMAF sin apps externas.
2. **Motor Web / PWA Universal (`app/web_portal/launcher/index.html`)**:
   - Funciona en cualquier navegador de Smart TV, PC o móvil.
   - Sincronizado automáticamente en GitHub Pages (`gh-pages`) mediante [`scripts/desplegar_ghpages.zsh`](file:///home/slone/slocast%201.0/scripts/desplegar_ghpages.zsh).
3. **Aplicación Nativa Linux Fedora Desktop (`/home/slone/slone_player`)**:
   - Stack: Python 3 + GTK4 + Libadwaita 1.0 + GStreamer 1.0 (`playbin`).
   - Aceleración por hardware VA-API verificada.
   - Arquitectura modular desacoplada: `src/core/playlist.py`, `src/services/player_service.py`, `src/ui/window.py`, `data/style.css`.
   - Pruebas unitarias al 100% en `tests/test_core.py`.
4. **Hub y Pasarela de Control LAN (`scripts/servidor_tv_hub.py`)**:
   - Activo en `http://0.0.0.0:8765`.
   - Lista M3U para reproductores externos en `/playlist.m3u`.
   - API de canales, lanzamiento ADB y proxy de streaming anti-bloqueo en `/api/`.
5. **Centinela Hardware ThinkPad X390 (`/home/slone/.gemini/antigravity/scratch/slone-sentinel`)**:
   - Activo en `http://127.0.0.1:7331`.
   - Monitorización continua de térmicas, RAM, batería y seguridad de red local.
6. **Estrategia y Modelo Económico Sostenible**:
   - Documento Maestro Integral: [`/home/slone/MASTER_ECOSISTEMA_SLONE.md`](file:///home/slone/MASTER_ECOSISTEMA_SLONE.md).
   - Campaña de Locutores Incógnito (Coste Cero): [`docs/CAMPANA_TALENTO_INCOGNITO.md`](file:///home/slone/slocast%201.0/docs/CAMPANA_TALENTO_INCOGNITO.md).
   - Modelo Freemium + SLÖNE Pass mensual / micro-pagos (eliminado el riesgo de suscripciones vitalicias a 9,99 €).

---

## 🔒 4. SEGURIDAD Y ZERO-TRUST (INQUEBRANTABLE)
- Cero telemetría externa. Ningún dato de visualización sale del dispositivo.
- Secretos, claves privadas y configuraciones sensibles en la Bóveda SLONE (`SLOCAST_VAULT/`), con permisos `700/600` e ignorados en Git.
- Almacén de claves de producción: [`keystore/slone_release.keystore`](file:///home/slone/slocast%201.0/keystore/slone_release.keystore) (RSA-2048, 10.000 días de validez, permisos `0600`).
- Copia `.bak` obligatoria antes de modificar cualquier fichero existente.
- Integridad Git 100% verificada (`git fsck --full` OK).

---

## 🚀 5. HOJA DE RUTA: HITOS COMPLETADOS
1. **Paso 1 (Autonomía de la App y Catálogo Dinámico Android TV)**: ✅ COMPLETADO.
2. **Paso 2 (Limpieza y Neutralidad de Interfaces)**: ✅ COMPLETADO.
3. **Paso 3 (Integración de Reproducción Nativa Media3 ExoPlayer)**: ✅ COMPLETADO.
4. **Paso 4 (Empaquetado Release 5.8 MB firmado & Despliegue en TV física)**: ✅ COMPLETADO.
5. **Paso 5 (Centinela Autónomo Hardware ThinkPad en :7331)**: ✅ COMPLETADO.
6. **Paso 6 (Player Nativo Linux GTK4 + GStreamer en slone_player)**: ✅ COMPLETADO.
7. **Paso 7 (Unificación de Chats y Dossier Maestro Definitivo)**: ✅ COMPLETADO.
8. **Paso 8 (Casilla Unificada Multi-Idioma, Guía EPG XMLTV en Vivo & PWA Offline)**: ✅ COMPLETADO.
   - Portal web `tv.html` desplegado en `:8765/tv.html` con Casilla de Audio Unificada (Castellano, V.O., Català, Radios deportivas sincronizadas con Web Audio API `delayNode`).
   - Doble lista maestra activa: `/playlist/sovereign.m3u8` (abierta legal) y `/playlist/private.m3u8` (79.475 canales con XMLTV EPG y timeshift 7d).
   - Motor EPG en vivo en `servidor_tv_hub.py` (`/api/epg`) con indexación inteligente tolerante a prefijos/sufijos y soporte de caché local (`cache/epg_tdt.xml.gz` + `cache/epg_es.xml.gz`).
   - PWA Service Worker actualizado a `slone-tv-v3` para carga offline instantánea sin almacenar fragmentos multimedia de vídeo.
   - Purga total de maquetas de hardware físico ficticio (`hardware.html` redirige transparentemente al software soberano).
