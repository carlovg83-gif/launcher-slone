# 👑 SLÖNE SOVEREIGN OS · DESIGN SYSTEM & STITCH INTEGRATION SPEC

Bienvenido al sistema de diseño oficial de **SLÖNE Sovereign OS** para Smart TVs, pantallas 4K y entornos multimedia de lujo.

---

## 🎨 Paleta de Color & Tokens de Diseño

| Token | Código Hex / RGBA | Uso Principal |
| :--- | :--- | :--- |
| `--accent` | `#E3FF00` | Dorado Cyber Neón (Insignias, foco activo, bordes seleccionados) |
| `--accent-glow` | `rgba(227, 255, 0, 0.35)` | Resplandor holográfico en tarjetas activas |
| `--cyan-shield` | `#00E5FF` | Cian Escudo de Privacidad (SLÖNE Shield Browser, Brave / Firefox) |
| `--tube-red` | `#FF334B` | Rojo SmartTube (SLÖNE Tube sin publicidad) |
| `--bg` | `#030407` | Obsidiana Profunda (Fondo espacial) |
| `--bg-card` | `rgba(11, 15, 25, 0.88)` | Cristal ahumado (Glassmorphism con blur de 20px) |
| `--bg-card-hover` | `rgba(22, 28, 46, 0.96)` | Cristal iluminado al enfocar con el mando |
| `--border` | `rgba(255, 255, 255, 0.09)` | Líneas de división de precisión militar |
| `--culer-blue` | `#004D98` | Azul Blaugrana (RAC1 Pou / CatRàdio) |
| `--culer-garnet` | `#A50044` | Grana Blaugrana |

---

## 🏗️ Arquitectura de Componentes del Launcher

1. **`SovereignHeader` (`#SovereignHeader`)**:
   - Cabecera fija translúcida con el escudo oficial SLÖNE.
   - Píldora de estado del CEO con catálogo de 39.737 canales.
   - Monitor de telemetría de la Xiaomi TV con indicador pulsante verde.
   - Reloj ejecutivo digital en tiempo real.

2. **`ShieldBrowserOmnibox` (`.shield-browser-bar`)**:
   - Barra omnibox interactiva inspirada en **Brave Shields** y **Firefox Focus**.
   - Escudos activos: Anti-rastreo, bloqueo total de publicidad y DNS privado.
   - Accesos directos: Brave Search, DuckDuckGo, Flashscore Directo, Diario SPORT, Mundo Deportivo, Marca y Wikipedia.

3. **`EcosystemDock` (`.dock-row`)**:
   - Dock de aplicaciones de fábrica: Google Play Store, SmartTube 4K, TiviMate VIP, Aptoide TV, Shield Web, Netflix, Prime Video, 3Cat / TV3, RTVE Play, atresplayer, Downloader y Ajustes de TV.
   - Control total vía mando a distancia (D-Pad TV).

4. **`SloneTubeSection` (`.tube-section`)**:
   - Reproductor y catálogo de YouTube 4K integrado y sin publicidad.
   - Pestañas dinámicas: Resúmenes Barça & Champions, F1 & MotoGP Highlights y Tertulias deportivas (Jijantes FC / Gerard Romero / El Chiringuito).
   - Botón de lanzamiento nativo a la aplicación SmartTube en la TV.

5. **`MultiviewStadium4X` (`.hero-stage`)**:
   - Cuadrícula de 4 señales simultáneas HLS de ultra-baja latencia.
   - Conmutación en caliente de pantalla activa y cambio rápido entre modo 4X y Pantalla Completa.

6. **`FanAudioMatrix` (`.fan-audio-bar`)**:
   - Matriz de audio para eliminar comentaristas sesgados: RAC1 (Joan Maria Pou), Catalunya Ràdio, Sonido Ambiente Puro de Estadio, Cadena SER, COPE y Radio Marca.
   - Controles de decalaje milimétrico (`-0.5s`, `-0.1s`, `+0.1s`, `+0.5s`) para sincronizar audio y vídeo con precisión satelital.

7. **`ChannelCarousel` (`.carousel-section`)**:
   - Carruseles categorizados con carátulas dinámicas para Fútbol, Champions, DAZN, Motor, TDT Generalistas y Cine.

---

## 📐 Puntos de Ruptura & Pantalla TV

- **Resolución Objetivo**: 1920 × 1080 (1080p FHD) y 3840 × 2160 (4K UHD).
- **Relación de Aspecto**: 16:9.
- **Interacción**: Diseñado para cruceta de mando a distancia (D-Pad), ratón de aire (air-mouse) y pantalla táctil.

© 2026 SLÖNE ENTERPRISES LLC. TODOS LOS DERECHOS RESERVADOS.
