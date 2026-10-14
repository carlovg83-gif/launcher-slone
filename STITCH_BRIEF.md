# 👑 SLÖNE SOVEREIGN OS · MASTER DESIGN BRIEF FOR STITCH

## 1. Identidad de Marca y Filosofía (Brand DNA)
- **Nombre**: SLÖNE™ (Sovereign Technology & Luxury Media Engine).
- **Arquetipo**: Hiperdeportivo, sigilo cibernético (*cyber-stealth*), soberanía tecnológica y exclusividad de alta gama.
- **Atmósfera Visual**: Obsidiana espacial profunda (`#030407`), fibra de carbono y cristal ahumado translúcido (*glassmorphism* con desenfoque de 20px) con líneas de acento de alta precisión en **Dorado Cyber Neón (`#E3FF00`)** y **Cian Escudo de Privacidad (`#00E5FF`)**.
- **Entorno Objetivo**: Smart TV de salón (Xiaomi TV, Android TV, Google TV, PatchWall, Fire TV) a resoluciones 1080p FHD y 4K UHD (3840×2160), navegable con mando a distancia (D-Pad).

---

## 2. Mapa de Pantallas y Componentes a Diseñar en Stitch

### Pantalla 1: SLÖNE Sovereign Home Launcher (Pantalla Principal)
- **Cabecera Soberana**:
  - Emblema oficial SLÖNE con resplandor dorado.
  - Insignia de perfil: `👑 CEO MASTER · 39.737 CANALES ACTIVOS`.
  - Widget de telemetría de red y estado de seguridad en tiempo real: `XIAOMI MiTV · ESCUDO ACTIVO` con diodo pulsante verde.
  - Reloj digital ejecutivo de gran legibilidad.
- **SLÖNE Shield Web Browser™**:
  - Barra omnibox de navegación privada inspirada en **Brave Shields** y **Firefox Focus**.
  - Indicadores de escudo: *Anti-rastreo activo*, *Sin anuncios*, *DNS privado*.
  - Píldoras de accesos rápidos: Brave Search, DuckDuckGo, Flashscore Directo, Diario SPORT, Mundo Deportivo, Marca y Wikipedia.
- **SLÖNE Ecosystem Dock**:
  - Carrusel horizontal de accesos rápidos a aplicaciones nativas y tiendas de serie: Google Play Store, SmartTube 4K, TiviMate VIP, Aptoide TV, Shield Web, Netflix 4K, Prime Video, 3Cat / TV3, RTVE Play, atresplayer, Downloader y Ajustes de TV.
  - Estados interactivos: `default`, `hover`, `focused` (con borde neón y resplandor).
- **SLÖNE Tube™ (YouTube 4K Sin Publicidad)**:
  - Módulo integrado con carátulas de vídeo 16:9 de alta definición, etiquetas de duración y distintivo `SIN ANUNCIOS`.
  - Selector de categorías: *Resúmenes Barça & Champions*, *Motor F1 & MotoGP*, *Jijantes FC / Tertulias deportivas*.
- **Multiview Stadium™ 4X & 1X**:
  - Escenario heroico con cuadrícula de 4 señales en directo simultáneas.
  - Conmutador de audio individual por cuadrante (`🔊 AUDIO` vs `🔇 MUTE`).
  - Botones de acción rápida: *Cuadrícula 4X*, *1 Pantalla Completa*, *Intercambiar señales [1 ⇄ 2]*, *Maximizar*.
- **FanAudio™ Culer Matrix**:
  - Barra de sincronización de emisoras de radio para silenciar narradores de TV convencionales.
  - Botones para: *Audio Original TV*, *RAC1 (Joan Maria Pou · Culer)*, *Catalunya Ràdio*, *Sonido Ambiente Puro sin narradores*, *Cadena SER*, *Cadena COPE*, *Radio Marca*.
  - Panel de decalaje milimétrico (`-0.5s`, `-0.1s`, `0.0s`, `+0.1s`, `+0.5s`, `RESET`) con display digital de latencia.
- **Carruseles de Canales VIP del CEO (39.737 Canales)**:
  - Fila 1: *Fútbol & Champions League* (M+ LaLiga TV FHD, M+ Liga de Campeones, DAZN LaLiga, Copa del Rey, LaLiga TV Bar...).
  - Fila 2: *Motor, Fórmula 1 & MotoGP* (DAZN F1, DAZN MotoGP, F1TV Live, Eurosport 1 UHD 4K...).
  - Fila 3: *Televisión Generalista & Autonómicas* (La 1 UHD, Antena 3, Telecinco, Cuatro, laSexta, TV3 HD, Esport3...).
  - Fila 4: *Cine, Estrenos & Series* (M+ Estrenos, Taquillas, Canales Temáticos).

---

## 3. Tokens de Diseño (CSS / Stitch Specs)

```css
:root {
  --bg: #030407;
  --bg-card: rgba(11, 15, 25, 0.88);
  --bg-card-hover: rgba(22, 28, 46, 0.96);
  --border: rgba(255, 255, 255, 0.09);
  --border-accent: rgba(227, 255, 0, 0.4);
  --accent: #E3FF00;
  --accent-glow: rgba(227, 255, 0, 0.35);
  --cyan-shield: #00E5FF;
  --cyan-glow: rgba(0, 229, 255, 0.35);
  --tube-red: #FF334B;
  --text: #FFFFFF;
  --text-muted: #8E95AA;
}
```

---

## 4. Archivo Fuente de Referencia en el Repositorio
- Código HTML/CSS en producción: [`app/web_portal/launcher/index.html`](app/web_portal/launcher/index.html)
- Manifiesto JSON de componentes: [`stitch.json`](stitch.json)
- Especificación de tokens y componentes: [`DESIGN_SYSTEM.md`](DESIGN_SYSTEM.md)
