import os

web_dir = "/home/slone/slocast 1.0/app/web_portal"
brain_dir = "/home/slone/.gemini/antigravity/brain/ca19abdc-9859-4476-ab55-60c6b1483221"

def read_svg(filename):
    with open(os.path.join(brain_dir, filename), "r", encoding="utf-8") as f:
        return f.read()

svg_soundwave = read_svg("slone_concept_soundwave_s.svg")
svg_antenna = read_svg("slone_concept_antenna_s.svg")
svg_ekg = read_svg("slone_concept_ekg_s.svg")
svg_stadium = read_svg("slone_concept_stadium_o.svg")

html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SLÖNE · LA LÓGICA DEL SÍMBOLO (BLUEPRINT)</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #04060A;
      color: #FFFFFF;
      font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
      padding: 32px 20px;
      line-height: 1.5;
    }}
    .container {{
      max-width: 1200px;
      margin: 0 auto;
    }}
    
    /* CABECERA */
    .top-header {{
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      padding-bottom: 24px;
      margin-bottom: 32px;
    }}
    .badge {{
      display: inline-block;
      background: rgba(0, 240, 255, 0.15);
      border: 1px solid #00F0FF;
      color: #00F0FF;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 2px;
      padding: 4px 10px;
      border-radius: 4px;
      text-transform: uppercase;
      margin-bottom: 10px;
    }}
    .title {{
      font-size: 36px;
      font-weight: 900;
      letter-spacing: 1px;
      margin-bottom: 8px;
    }}
    .subtitle {{
      font-size: 16px;
      color: #94A3B8;
      max-width: 800px;
    }}

    /* COMPARATIVA CON LOS GRANDES (LA REGLA TESLA / SPOTIFY) */
    .benchmark-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-bottom: 40px;
    }}
    @media (max-width: 768px) {{ .benchmark-grid {{ grid-template-columns: 1fr; }} }}
    .benchmark-card {{
      background: #090E17;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      padding: 18px;
    }}
    .benchmark-brand {{
      font-size: 14px;
      font-weight: 800;
      color: #FFF;
      display: flex;
      justify-content: space-between;
      margin-bottom: 6px;
    }}
    .benchmark-tech {{
      font-size: 12px;
      color: #00F0FF;
      font-weight: 700;
      margin-bottom: 6px;
    }}
    .benchmark-desc {{
      font-size: 12px;
      color: #8E9BAE;
    }}

    /* ANATOMÍA DEL PRODUCTO SLÖNE */
    .formula-box {{
      background: linear-gradient(135deg, rgba(0, 240, 255, 0.08), rgba(0, 102, 255, 0.04));
      border: 1px solid rgba(0, 240, 255, 0.25);
      border-radius: 16px;
      padding: 24px;
      margin-bottom: 40px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-around;
      gap: 20px;
      text-align: center;
    }}
    .formula-item {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
    }}
    .formula-circle {{
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: #0B101D;
      border: 1px solid rgba(255, 255, 255, 0.2);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      font-weight: 900;
      color: #00F0FF;
    }}
    .formula-op {{
      font-size: 28px;
      font-weight: 900;
      color: #64748B;
    }}

    /* LAS 4 PROPUESTAS LÓGICAS */
    .concepts-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-bottom: 40px;
    }}
    @media (max-width: 900px) {{ .concepts-grid {{ grid-template-columns: 1fr; }} }}
    .concept-card {{
      background: #070B14;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 18px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      position: relative;
    }}
    .concept-card:hover {{
      border-color: #00F0FF;
      box-shadow: 0 10px 30px rgba(0, 240, 255, 0.15);
    }}
    .concept-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }}
    .concept-title {{
      font-size: 18px;
      font-weight: 800;
      letter-spacing: 0.5px;
    }}
    .svg-viewport {{
      width: 100%;
      height: 240px;
      background: #020306;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 16px;
      padding: 16px;
      border: 1px solid rgba(255, 255, 255, 0.05);
    }}
    .svg-viewport svg {{
      max-width: 100%;
      max-height: 100%;
    }}
    .logic-list {{
      list-style: none;
      font-size: 13px;
      color: #CBD5E1;
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-bottom: 16px;
    }}
    .logic-list li::before {{
      content: "✦ ";
      color: #00F0FF;
      font-weight: 900;
    }}

    /* ESCALA DE RECONOCIMIENTO (SMART TV, APP, ESTADIO) */
    .scale-row {{
      background: #030508;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      padding: 14px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: auto;
    }}
    .scale-label {{
      font-size: 10px;
      font-weight: 800;
      color: #64748B;
      letter-spacing: 1.5px;
      text-transform: uppercase;
    }}
    .scale-icons {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}
    .icon-small {{ width: 28px; height: 28px; }}
    .icon-med {{ width: 44px; height: 44px; }}
  </style>
</head>
<body>
  <div class="container">
    
    <div class="top-header">
      <div class="badge">INGENIERÍA DE MARCA · ZERO HUMO</div>
      <h1 class="title">LA LÓGICA INQUEBRANTABLE DEL SÍMBOLO SLÖNE</h1>
      <p class="subtitle">
        Tienes toda la razón: Tesla no usa un neumático ni un tenedor; usa el rotor magnético de su motor. 
        Spotify no usa una clave de sol genérica; usa las 3 ondas de compresión de streaming. 
        <strong>Aquí está la física y la lógica exacta de lo que vende SLÖNE.</strong>
      </p>
    </div>

    <!-- CÓMO LO HACEN LOS GRANDES -->
    <div class="benchmark-grid">
      <div class="benchmark-card">
        <div class="benchmark-brand"><span>TESLA</span><span style="color: #64748B;">MOTOR ELÉCTRICO</span></div>
        <div class="benchmark-tech">T = Sección del rotor de inducción</div>
        <div class="benchmark-desc">No es una 'T' tipográfica: es el corte transversal del inducido y los polos magnéticos que Nikola Tesla patentó en 1888.</div>
      </div>
      <div class="benchmark-card">
        <div class="benchmark-brand"><span>SPOTIFY</span><span style="color: #64748B;">STREAMING AUDIO</span></div>
        <div class="benchmark-tech">Ondas de sonido expansivas</div>
        <div class="benchmark-desc">Tres ondas acústicas dentro de una pastilla verde. Todo el mundo ve sonido y transmisión sin necesidad de leer una sola letra.</div>
      </div>
      <div class="benchmark-card">
        <div class="benchmark-brand"><span>BLUETOOTH</span><span style="color: #64748B;">ENLACE INALÁMBRICO</span></div>
        <div class="benchmark-tech">Runa Hagall (ᚼ) + Bjarkan (ᛒ)</div>
        <div class="benchmark-desc">Las iniciales rúnicas del rey vikingo que unificó las islas. Comunica unión inalámbrica entre dos dispositivos distintos.</div>
      </div>
    </div>

    <!-- LA FÓRMULA SLÖNE -->
    <div class="formula-box">
      <div class="formula-item">
        <div class="formula-circle">S</div>
        <div style="font-size: 11px; font-weight: 800; color: #FFF;">LETRA S</div>
        <div style="font-size: 10px; color: #64748B;">Identidad Soberana</div>
      </div>
      <div class="formula-op">+</div>
      <div class="formula-item">
        <div class="formula-circle">〰</div>
        <div style="font-size: 11px; font-weight: 800; color: #FFF;">ONDA DE AUDIO</div>
        <div style="font-size: 10px; color: #64748B;">Frecuencia & Casters</div>
      </div>
      <div class="formula-op">+</div>
      <div class="formula-item">
        <div class="formula-circle">Ö</div>
        <div style="font-size: 11px; font-weight: 800; color: #FFF;">DIÉRESIS DUAL</div>
        <div style="font-size: 10px; color: #64748B;">Audio + Vídeo a 0 ms</div>
      </div>
      <div class="formula-op">=</div>
      <div class="formula-item">
        <div class="formula-circle" style="background: #00F0FF; color: #000; border-color: #00F0FF;">⚡</div>
        <div style="font-size: 11px; font-weight: 800; color: #00F0FF;">SLÖNE MARK</div>
        <div style="font-size: 10px; color: #CBD5E1;">Inconfundible a 50 metros</div>
      </div>
    </div>

    <!-- LAS 4 PROPUESTAS BASADAS EN LA TECNOLOGÍA REAL DE SLÖNE -->
    <div class="concepts-grid">
      
      <!-- PROPUESTA 1 -->
      <div class="concept-card">
        <div class="concept-header">
          <div class="concept-title">PROPUESTA 1: LA 'S' DE ONDA ACÚSTICA (SOUNDWAVE)</div>
          <span class="badge">DIRECTO & PURO</span>
        </div>
        <div class="svg-viewport">
          {svg_soundwave}
        </div>
        <ul class="logic-list">
          <li><strong>¿Qué es?</strong> La letra 'S' está construida literalmente por dos ondas de compresión de audio opuestas que se abrazan.</li>
          <li><strong>¿Por qué funciona?</strong> Exactamente igual que las ondas de Spotify, pero aquí la onda forma la inicial 'S' de SLÖNE.</li>
          <li><strong>Los dos satélites superiores:</strong> Representan la diéresis de la Ö y los dos canales de sonido estéreo sincronizados al milisegundo con la TV.</li>
        </ul>
        <div class="scale-row">
          <span class="scale-label">RECONOCIMIENTO EN SMART TV (64px & 32px)</span>
          <div class="scale-icons">
            <div class="icon-med">{svg_soundwave}</div>
            <div class="icon-small">{svg_soundwave}</div>
          </div>
        </div>
      </div>

      <!-- PROPUESTA 2 -->
      <div class="concept-card">
        <div class="concept-header">
          <div class="concept-title">PROPUESTA 2: LA ANTENA DE TRANSMISIÓN DIRECTA</div>
          <span class="badge">NIVEL BLUETOOTH</span>
        </div>
        <div class="svg-viewport">
          {svg_antenna}
        </div>
        <ul class="logic-list">
          <li><strong>¿Qué es?</strong> Un mástil central de emisión de señal hacia la Smart TV donde los frentes de onda izquierdo y derecho forman la silueta de la 'S'.</li>
          <li><strong>¿Por qué funciona?</strong> Comunica "HARDWARE Y CONECTIVIDAD INALÁMBRICA" al primer golpe de vista, como la runa de Bluetooth.</li>
          <li><strong>Aplicación física:</strong> Ideal para imprimir en relieve en el botón central del mando a distancia de la Smart TV.</li>
        </ul>
        <div class="scale-row">
          <span class="scale-label">RECONOCIMIENTO EN SMART TV (64px & 32px)</span>
          <div class="scale-icons">
            <div class="icon-med">{svg_antenna}</div>
            <div class="icon-small">{svg_antenna}</div>
          </div>
        </div>
      </div>

      <!-- PROPUESTA 3 -->
      <div class="concept-card">
        <div class="concept-header">
          <div class="concept-title">PROPUESTA 3: EL PULSO CARDÍACO DEL PARTIDO (LIVE EKG)</div>
          <span class="badge">EMOCIÓN & VITALIDAD</span>
        </div>
        <div class="svg-viewport">
          {svg_ekg}
        </div>
        <ul class="logic-list">
          <li><strong>¿Qué es?</strong> El monitor de ritmo cardíaco: la línea plana de reposo que ante el estallido del gol a 110 dB dibuja la curva de la 'S' en un trazo continuo.</li>
          <li><strong>¿Por qué funciona?</strong> El fútbol es taquicardia y emoción en vivo. Nadie confunde un trazado de pulso médico con otra cosa.</li>
          <li><strong>Color neón verde:</strong> Señal de directo permanente ("ON-AIR") en la esquina superior del televisor.</li>
        </ul>
        <div class="scale-row">
          <span class="scale-label">RECONOCIMIENTO EN SMART TV (64px & 32px)</span>
          <div class="scale-icons">
            <div class="icon-med">{svg_ekg}</div>
            <div class="icon-small">{svg_ekg}</div>
          </div>
        </div>
      </div>

      <!-- PROPUESTA 4 -->
      <div class="concept-card">
        <div class="concept-header">
          <div class="concept-title">PROPUESTA 4: EL ESTADIO Y EL HAZ DE SEÑAL</div>
          <span class="badge">ARQUITECTURA DEPORTIVA</span>
        </div>
        <div class="svg-viewport">
          {svg_stadium}
        </div>
        <ul class="logic-list">
          <li><strong>¿Qué es?</strong> La 'Ö' es la silueta monumental del estadio de fútbol vista desde el cielo. Los dos puntos son las torres de emisión satelital.</li>
          <li><strong>El interior:</strong> La fibra óptica interna dibuja la 'S' conectando las gradas con los hogares.</li>
          <li><strong>¿Por qué funciona?</strong> Une directamente el estadio de fútbol con la marca de retransmisión soberana.</li>
        </ul>
        <div class="scale-row">
          <span class="scale-label">RECONOCIMIENTO EN SMART TV (64px & 32px)</span>
          <div class="scale-icons">
            <div class="icon-med">{svg_stadium}</div>
            <div class="icon-small">{svg_stadium}</div>
          </div>
        </div>
      </div>

    </div>

  </div>
</body>
</html>"""

with open(os.path.join(web_dir, "logica_logo.html"), "w", encoding="utf-8") as f:
    f.write(html)

with open(os.path.join(brain_dir, "logica_logo.html"), "w", encoding="utf-8") as f:
    f.write(html)

print("Página de lógica técnica creada en:")
print(os.path.join(web_dir, "logica_logo.html"))
