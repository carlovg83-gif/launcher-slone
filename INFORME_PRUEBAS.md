# Informe de pruebas y optimización — SLOCAST / SLONE OS v7.5

| Dato | Valor |
|---|---|
| Fecha | 03/10/2026 |
| Carpeta Principal | `/home/slone/Documentos/SLOCAST` |
| Núcleo | `app/slocast.py` (v7.5 Pro VR46 Edition) |
| Hardware de Referencia | ThinkPad X390 · Intel Core i7-8665U · 16 GB RAM · Intel UHD 620 |
| Sistema Operativo | Fedora 44 Linux · KDE Plasma 6 + SDDM · ZSH |
| Estado de Pruebas | ✅ **100% OK (Todas las pruebas superadas)** |

---

## 1. Problemas Detectados y Soluciones Aplicadas

### 🎯 A. Corrección Integral de Decalaje (A/V Sync y Latencia de Directo)
- **Causa raíz técnica:** 
  1. El perfil `--profile=low-latency` de MPV desactivaba el búfer de red provocando micro-caídas en streams HTTP IPTV, lo que desalineaba los sellos de tiempo PTS entre vídeo y audio.
  2. En `BroadcastHub`, el tamaño de paquete leído era de `32768` bytes (no múltiplo de los 188 bytes del estándar MPEG-TS), lo que provocaba que al descartar paquetes en la cola se corrompiera la cabecera TS y el decodificador de vídeo perdiera la sincronización con el audio.
  3. La cola de clientes (`queue.Queue`) tenía un tamaño de 160 bloques (~5.2 MB), acumulando hasta 8 segundos de desfase permanente respecto al directo.
  4. Falta de aceleración por hardware en MPV para el procesador Intel Core i7-8665U, provocando caídas de fotogramas en emisiones 1080p50/HEVC y retraso del vídeo frente al audio.
- **Solución implementada:**
  1. Configuración de parámetros avanzados en MPV: `--cache=yes`, `--cache-secs=3`, `--demuxer-readahead-secs=2`, `--stream-buffer-size=128k`, `--video-sync=audio`, `--autosync=30`, `--audio-pitch-correction=yes`, `--correct-pts=yes`, `--deinterlace=auto` y `--hwdec=auto-safe` (Intel VA-API nativo).
  2. Alineación matemática de bloques MPEG-TS: `CHUNK_TS_ALIGNED = 65424` (exactamente `188 * 348` bytes).
  3. Búfer ágil de 32 bloques en `BroadcastHub`, con vaciado automático de colas al cambiar de canal para eliminar residuos y asegurar inicio instantáneo en vivo.
  4. **Control dinámico de decalaje en directo:**
     - Botones en el dock inferior: `[-0.1s]`, `[+0.1s]`, `[⏱ 0.0s]` (menú interactivo de presets).
     - Atajos de teclado en tiempo real: `Z` (-0.1s), `X` (+0.1s), `[` (-0.5s), `]` (+0.5s), `0` (restablecer a 0.0s).
     - Indicador en vivo en el HUD superior (`⏱ SYNC: +0.20s`).
     - Control de decalaje desde el mando web móvil (`/remote` y `/api/cmd?action=decalaje_plus/minus/reset`).

---

### 📋 B. Errores del Menú y de la Interfaz Corregidos
1. **Menú contextual (clic derecho) implementado:**
   - En lista de canales, favoritos y recientes ahora es posible hacer clic derecho para:
     - ▶ Reproducir canal.
     - ★ Añadir / Quitar de Favoritos.
     - 📺 Transmitir a Xiaomi TV.
     - 📋 Copiar URL del stream.
     - 🗑 Eliminar de la lista.
2. **Sincronización del menú lateral (Drawer) y navegación:**
   - Al sintonizar un canal desde Favoritos o Recientes, el selector lateral ahora actualiza su estado activo a `📺 Canales IPTV` (`setChecked(True)`).
3. **Selector dinámico de Grupos IPTV por País:**
   - Añadido desplegable de grupos exactos de la lista (`ES - FUTBOL`, `ES - DAZN EVENTOS`, `ES - FORMULA 1`, etc.).
   - Añadido chip rápido dedicado para `🏎 Motor (VR46/F1)` con detección inteligente de MotoGP, Fórmula 1 y carreras.
4. **Actualización de HUD y reloj en tiempo real:**
   - El encabezado del reproductor (`lbl_hud_name`) ahora muestra el canal en reproducción en lugar de quedarse estático en "Selecciona un canal...".
   - El reloj digital del HUD (`lbl_hud_clock`) se actualiza cada segundo.
   - El pie del HUD (`lbl_epg_now`) muestra el canal y categoría actual.
5. **Persistencia automática:**
   - Favoritos y canales recientes se guardan y cargan automáticamente en `~/.config/slocast/state.json`.
6. **Alertas no intrusivas:**
   - Reemplazados los diálogos modales emergentes (`QMessageBox.information`) que bloqueaban la reproducción al marcar favoritos o copiar enlaces por avisos OSD en pantalla mediante MPV.
7. **Reproducción de vídeos locales:**
   - Los archivos locales (`file://` o rutas locales) se envían directamente al motor MPV nativo sin pasar por el relé HTTP ni inyección TS.

---

### 🚀 C. Portabilidad y Lanzadores del Sistema
- Eliminadas rutas absolutas codificadas en el servidor web hacia carpetas temporales (`PORTAL_DIR` e iconos ahora se resuelven dinámicamente).
- Actualizados los ejecutables `~/.local/bin/slocast` y `~/.local/bin/slone` apuntando a `/home/slone/Documentos/SLOCAST/app/slocast.py`.
- Actualizadas las cachés de aplicaciones de KDE Plasma 6 (`kbuildsycoca6` y `update-desktop-database`).

---

## 2. Resultados de las Pruebas Unitarias y de Integración

```
[TEST 1] Canales cargados: 39737
[TEST 2] Sintonizando: |ES| DAZN MOTOGP FHD
[TEST 2 OK] HUD, Dock y EPG actualizados con el nombre del canal.
[TEST 3 OK] Ajuste de decalaje en MPV, dock y HUD verificado.
[TEST 3 OK] Reset de decalaje a 0.0s verificado.
[TEST 4 OK] Persistencia de favoritos en state.json verificada.
[TEST 4 OK] Eliminación de favorito y guardado en state.json verificado.
[TEST 5 OK] Navegación siguiente/anterior canal con scroll verificado.
[TEST 6 OK] Reloj en tiempo real operativo.

>>> TODOS LOS TESTS DE INTEGRIDAD Y FUNCIONALIDAD HAN PASADO (100% OK) <<<
```

---

© 2026 SLONE ENTERPRISES LLC. Documentación y pruebas consolidadas para ThinkPad X390.
