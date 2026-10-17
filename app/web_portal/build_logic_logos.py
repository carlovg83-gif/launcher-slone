import os

brain_dir = "/home/slone/.gemini/antigravity/brain/ca19abdc-9859-4476-ab55-60c6b1483221"
web_dir = "/home/slone/slocast 1.0/app/web_portal"

# 1. ISOTIPO A: LA 'S' DE FRECUENCIA / ONDA ACÚSTICA (THE SOUNDWAVE S)
# Lógica: SLÖNE es audio en directo y retransmisión. 
# La 'S' se forma a partir de ondas de compresión de sonido (como las 3 ondas de Spotify, pero que aquí dibujan literalmente una S de titanio).
svg_soundwave_s = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="100%" height="100%">
  <defs>
    <linearGradient id="cyanBlue" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00F0FF"/>
      <stop offset="100%" stop-color="#0066FF"/>
    </linearGradient>
  </defs>
  <!-- FONDO NEGRO PURO OLED -->
  <rect width="300" height="300" rx="36" fill="#05070D"/>
  
  <!-- GUÍAS DE ONDAS CONCÉNTRICAS (ANATOMÍA DE SONIDO) -->
  <circle cx="150" cy="105" r="55" fill="none" stroke="rgba(0, 240, 255, 0.08)" stroke-width="1.5" stroke-dasharray="4 4"/>
  <circle cx="150" cy="195" r="55" fill="none" stroke="rgba(0, 240, 255, 0.08)" stroke-width="1.5" stroke-dasharray="4 4"/>

  <!-- LA 'S' DE SEÑAL DE AUDIO PURA: DOS ONDAS CURVAS QUE SE ENLAZAN -->
  <g fill="none" stroke="url(#cyanBlue)" stroke-width="18" stroke-linecap="round" stroke-linejoin="round">
    <!-- Onda superior (emisión canal izquierdo / vídeo) -->
    <path d="M 205 92 C 205 65, 175 52, 150 52 C 120 52, 95 70, 95 100 C 95 135, 140 145, 150 150 C 160 155, 205 165, 205 200 C 205 230, 180 248, 150 248 C 125 248, 95 235, 95 208"/>
  </g>
  
  <!-- LOS DOS NODOS DE SINCRONIZACIÓN (LA Ö DE SLÖNE / EMISORES ESTÉREO A CERO LATENCIA) -->
  <circle cx="128" cy="30" r="6" fill="#00F0FF"/>
  <circle cx="172" cy="30" r="6" fill="#00F0FF"/>
</svg>"""

# 2. ISOTIPO B: EL NODO CENTRAL / LA ANTENA RÚNICA SOBERANA
# Lógica: Como la 'T' de Tesla (rotor del motor) o Bluetooth (la runa del rey Harald).
# Es una antena de emisión directa al televisor, donde los frentes de onda forman la 'S'.
svg_antenna_s = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="100%" height="100%">
  <defs>
    <linearGradient id="whiteSilver" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="#94A3B8"/>
    </linearGradient>
  </defs>
  <rect width="300" height="300" rx="36" fill="#05070D"/>

  <!-- EJE CENTRAL DE TRANSMISIÓN (EL NODO SLÖNE) -->
  <line x1="150" y1="45" x2="150" y2="255" stroke="url(#whiteSilver)" stroke-width="12" stroke-linecap="round"/>

  <!-- ONDAS DE RADIO ANGULARES QUE FORMAN LA 'S' (CONECTIVIDAD PURA) -->
  <!-- Bucle superior derecho -->
  <path d="M 150 75 L 210 115 L 150 150" fill="none" stroke="url(#whiteSilver)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- Ala izquierda de frecuencia -->
  <path d="M 150 75 L 90 115 L 150 150" fill="none" stroke="#00F0FF" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
  
  <!-- Bucle inferior izquierdo (cerrando la S rúnica) -->
  <path d="M 150 150 L 90 185 L 150 225" fill="none" stroke="url(#whiteSilver)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- Ala derecha de frecuencia inferior -->
  <path d="M 150 150 L 210 185 L 150 225" fill="none" stroke="#00F0FF" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>

  <!-- DIÉRESIS DE LA Ö (TRANSMISIÓN VIVA) -->
  <circle cx="130" cy="28" r="5" fill="#00F0FF"/>
  <circle cx="170" cy="28" r="5" fill="#00F0FF"/>
</svg>"""

# 3. ISOTIPO C: EL LATIDO DEL ESTADIO (THE PULSE-S / VITAL MATCH)
# Lógica: ¿Qué es el fútbol? Es tensión, ritmo cardíaco y sonido.
# Una onda de monitor EKG que dibuja la S en el momento del gol.
svg_ekg_s = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="100%" height="100%">
  <defs>
    <linearGradient id="neonPulse" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00FF66"/>
      <stop offset="100%" stop-color="#00F0FF"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect width="300" height="300" rx="36" fill="#05070D"/>

  <!-- REJILLA DE EMISIÓN DEPORTIVA Y AUDIO -->
  <g opacity="0.1" stroke="#00F0FF" stroke-width="1">
    <line x1="30" y1="150" x2="270" y2="150"/>
    <line x1="150" y1="30" x2="150" y2="270"/>
    <circle cx="150" cy="150" r="100" fill="none"/>
  </g>

  <!-- LA ONDA VITAL CONTINUA QUE FORMA LA 'S' EN UN SOLO TRAZO -->
  <path d="M 40 150 L 80 150 L 95 120 L 110 180 L 125 70 C 140 45, 195 45, 195 95 C 195 140, 105 160, 105 205 C 105 255, 160 255, 175 230 L 190 120 L 205 180 L 220 150 L 260 150" 
        fill="none" stroke="url(#neonPulse)" stroke-width="11" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)"/>

  <!-- NODOS DE SEÑAL EN DIRECTO (LATENCIA CERO) -->
  <circle cx="138" cy="25" r="5" fill="#00FF66"/>
  <circle cx="162" cy="25" r="5" fill="#00FF66"/>
</svg>"""

# 4. ISOTIPO D: EL ESTADIO Y EL STREAM (THE STADIUM ORBIT)
# Lógica: La 'Ö' es el estadio de fútbol a vista de satélite. Los dos puntos son las torres de emisión que transmiten el audio sin compresión.
svg_stadium_o = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="100%" height="100%">
  <defs>
    <linearGradient id="goldTitanium" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="50%" stop-color="#CBD5E1"/>
      <stop offset="100%" stop-color="#475569"/>
    </linearGradient>
  </defs>
  <rect width="300" height="300" rx="36" fill="#05070D"/>

  <!-- EL ANILLO DEL ESTADIO (ARQUITECTURA MONUMENTAL) -->
  <ellipse cx="150" cy="165" rx="85" ry="95" fill="none" stroke="url(#goldTitanium)" stroke-width="14"/>

  <!-- CORTE INTERNO EN 'S' DE FIBRA ÓPTICA Y AUDIO DIRECTO -->
  <path d="M 190 125 C 190 100, 170 85, 150 85 C 125 85, 110 100, 110 125 C 110 155, 190 175, 190 205 C 190 230, 175 245, 150 245 C 125 245, 110 230, 110 205" 
        fill="none" stroke="#00F0FF" stroke-width="9" stroke-linecap="round"/>

  <!-- LAS DOS TORRES DE EMISIÓN DE ESTADIO (DIÉRESIS DE LA Ö) -->
  <circle cx="120" cy="42" r="7" fill="#00F0FF"/>
  <circle cx="180" cy="42" r="7" fill="#00F0FF"/>
</svg>"""

# Guardar los SVGs individuales en brain
with open(os.path.join(brain_dir, "slone_concept_soundwave_s.svg"), "w", encoding="utf-8") as f:
    f.write(svg_soundwave_s)
with open(os.path.join(brain_dir, "slone_concept_antenna_s.svg"), "w", encoding="utf-8") as f:
    f.write(svg_antenna_s)
with open(os.path.join(brain_dir, "slone_concept_ekg_s.svg"), "w", encoding="utf-8") as f:
    f.write(svg_ekg_s)
with open(os.path.join(brain_dir, "slone_concept_stadium_o.svg"), "w", encoding="utf-8") as f:
    f.write(svg_stadium_o)

print("SVGs conceptuales de lógica pura creados.")
