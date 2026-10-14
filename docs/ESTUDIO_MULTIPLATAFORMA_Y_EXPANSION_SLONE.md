# SLÖNE™ — ESTUDIO MULTIPLATAFORMA Y HOJA DE RUTA DE EXPANSIÓN GLOBAL
## Plan de Despliegue Universal: Xiaomi TV, Android TV, Fire TV, Apple TV, webOS, Tizen y PC

---

## 1. Integración en Xiaomi TV (Android TV / Google TV)

Tu Xiaomi TV opera con el sistema operativo **Android TV / Google TV**. La integración se realiza de inmediato a través de tres vías optimizadas:

### Vía 1: Servidor Multimedia LAN Nativo (Disponible hoy mismo)
- Tu ThinkPad X390 tiene la IP local: `192.168.1.145`.
- El motor de SLÖNE sirve la lista maestra y los flujos en el puerto `8765`.
- **En la Xiaomi TV**:
  - **Opción Navegador (Sin instalar nada)**: Abre el navegador de la tele (Chrome, TV Bro o Puffin TV) e introduce:
    ```
    http://192.168.1.145:8765
    ```
    Tendrás acceso inmediato a la interfaz completa PWA de SLÖNE con reproductor y control de mando.
  - **Opción Reproductor Nativo TV (TiviMate / IPTV Smarters / VLC)**:
    En cualquier reproductor de la tienda de la tele, añade la lista M3U:
    ```
    http://192.168.1.145:8765/playlist.m3u
    ```
    La tele sintonizará los 430 canales oficiales HD con aceleración gráfica directa.

### Vía 2: Google Cast Directo desde el ThinkPad
- Al pulsar el botón **"📺 Proyectar en Xiaomi TV"** en la interfaz de SLÖNE, el motor transmite el canal activo con el audio de radio deportiva sincronizado directamente a la pantalla del salón a través del protocolo Cast v2.

### Vía 3: Instalación de APK Nativo en Xiaomi TV (Sideloading)
1. Instala la app gratuita **"Send Files to TV"** desde la Google Play Store de tu Xiaomi TV y en tu móvil.
2. Envía el archivo `.apk` de SLÖNE desde el ordenador o móvil a la tele.
3. Abre un explorador de archivos en la TV (como *File Commander*) y pulsa sobre el APK para instalarlo en 10 segundos.

---

## 2. Matriz de Plataformas: Estado Actual y Qué Podemos Añadir

| Plataforma | Estado Actual | Qué Añadimos para Liderar el Mercado |
|---|---|---|
| **Linux (Fedora, RHEL, Steam Deck)** | Binario nativo compilado ELF 64-bit (`dist/bin/slone`) y RPM oficial (`dist/rpms/`). | Paquete universal **AppImage** (1 clic sin dependencias) y paquete **Flatpak** para la tienda Flathub y Steam Deck. |
| **Android TV & Xiaomi TV** | Soporte Google Cast, Web PWA LAN y pipeline de empaquetado AAB. | Interfaz **Leanback nativa** diseñada para mando a distancia (D-Pad), control de canales con cruceta y decodificación por hardware MediaCodec. |
| **Amazon Fire TV** | Compatible con el APK de Android TV (Fire OS es Android). | Código numérico de descarga rápida para la app oficial **Downloader** de Amazon (instalar tecleando 5 números en el mando). |
| **Samsung Smart TV (Tizen)** | Web PWA accesible por navegador. | Paquete nativo `.wgt` (Tizen Web Application) empaquetado con Tizen Studio para instalación directa en televisores Samsung. |
| **LG Smart TV (webOS)** | Web PWA accesible por navegador. | Paquete nativo `.ipk` (webOS Web App) mediante webOS Open Source Edition SDK. |
| **Apple (macOS, iOS, Apple TV)** | Flujos HLS compatibles en `app/slocast.py`. | App nativa en Swift/SwiftUI empaquetada para TestFlight y la App Store, con soporte de audio espacial y Siri Remote. |
| **Windows 11 / 10** | Script lanzador `platforms/windows/iniciar_slone.bat`. | Instalador `.exe` e `.msi` firmado digitalmente con Inno Setup y aceleración DirectX / Direct3D 11. |

---

## 3. Nuevas Utilidades y Mejoras Estratégicas para Incorporar

1. **Sincronizador Multidispositivo Cloud (Sync Instantáneo)**:
   - Los favoritos, el orden de canales y el decalaje de audio guardados en tu ThinkPad se sincronizan en milisegundos con la Xiaomi TV y el móvil.
2. **Modo Estadio Multiview 4X en Pantallas Grandes**:
   - En una Xiaomi TV de 55" o 65", ver 4 partidos a la vez en 1080p simultáneo con solo cambiar el audio activo con el mando a distancia es la función más deseada por los aficionados al deporte.
3. **Grabación Inteligente en la Nube / Local (DVR Cloud-Ready)**:
   - Grabación programada de carreras de Fórmula 1, MotoGP o partidos nocturnos directamente en disco local o en Google Cloud Storage a coste cero mediante los créditos de startup.
