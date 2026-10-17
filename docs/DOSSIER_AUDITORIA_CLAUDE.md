# 📋 DOSSIER DE AUDITORÍA TÉCNICA INDEPENDIENTE — PROYECTO SLOCAST 1.0 / SLÖNE OS
> **Objetivo:** Presentar este informe a Claude (Claude Desktop / claude.ai) para obtener un segundo punto de vista arquitectónico, crítico e independiente, sin sesgos comerciales ni complacencia.

---

## 1. CONTEXTO Y MISIÓN DEL PROYECTO
- **Nombre:** SLÖNE Sovereign OS / Slocast 1.0.
- **Objetivo:** Sistema de salón privado para streaming local en red doméstica (`192.168.1.0/24`) y control de Smart TV (Xiaomi Mi TV con Android 11 vía ADB LAN).
- **Filosofía:** Zero-Trust, cero telemetría externa, supresión de anuncios y optimización de latencia en eventos deportivos.
- **Hardware anfitrión:** Portátil ThinkPad X390 (Intel Core i7-8665U, 8 GB RAM, Fedora 44 Linux, KDE Plasma 6).

---

## 2. COMPONENTES IMPLEMENTADOS ACTUALMENTE
1. **Daemon TV Hub (`scripts/servidor_tv_hub.py`):**
   - Servidor local en Python escuchando en puerto `8765`.
   - Sirve catálogo JSON de canales, portal web PWA y endpoints para lanzar comandos ADB hacia la TV.
2. **SLÖNE TV Launcher Nativo (`platforms/android/slone-tv-launcher`):**
   - App para Android TV desarrollada en Kotlin con Jetpack Compose for TV.
   - Paquete: `com.slone.launcher` (Actividad: `com.example.slnelauncher.MainActivity`).
   - Función actual: Pantalla de inicio con botones de acceso rápido que lanzan mediante Intents las apps instaladas en la TV (SmartTube, TiviMate, 3Cat, Netflix).
3. **Portal Web Flagship (`app/web_portal/launcher/index.html`):**
   - Interfaz web con cuadrícula Multiview (HLS/mpegts), carruseles y selectores de audio.
4. **Script de Control (`scripts/gestionar_tv_launcher.zsh`):**
   - Automatización en ZSH para compilar con Gradle, desplegar por ADB a `192.168.1.135:5555` y alternar entre el launcher habitual de Google TV y SLÖNE OS.

---

## 3. LIMITACIONES Y PUNTOS DÉBILES REALES (SIN MAQUILLAR)
1. **Infraestructura frágil:**
   - La batería del ThinkPad está agotada/bloqueada (0 segundos de autonomía). Si se corta el cable de corriente, el servidor central cae al instante.
   - El portátil está limitado a 8 GB de RAM física, lo que exige estricto control de memoria si se transcodifica vídeo.
2. **El launcher de TV es hoy un lanzador de accesos directos:**
   - No reproduce el vídeo dentro de la propia app de Android TV todavía; delega la reproducción abriendo TiviMate o SmartTube.
3. **Dependencia de la red local:**
   - Toda la orquestación depende de que el router asigne las IPs fijas (`192.168.1.145` para el PC y `192.168.1.135` para la TV) y de que el puerto 5555 de ADB no se cierre en reposo.

---

## 4. PREGUNTAS CLAVE PARA EL ARQUITECTO AUDITOR (CLAUDE)
Por favor, analiza este proyecto con mirada crítica de CTO senior:
1. **Arquitectura:** ¿Tiene sentido mantener la arquitectura dual (Launcher Kotlin nativo en TV + Servidor Python en ThinkPad), o sería más limpio y mantenible unificarlo en una sola PWA / app nativa directa?
2. **Riesgos y Estabilidad:** ¿Qué cuellos de botella ves a corto plazo en un ThinkPad de 8 GB sirviendo vídeo a la red local?
3. **Próximo Paso Crítico:** Dejando a un lado la interfaz visual, ¿cuál debería ser la siguiente prioridad técnica obligatoria para que el sistema sea verdaderamente robusto y no una maqueta frágil?
