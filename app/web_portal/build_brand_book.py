import base64
import os

brain_dir = "/home/slone/.gemini/antigravity/brain/ca19abdc-9859-4476-ab55-60c6b1483221"
web_dir = "/home/slone/slocast 1.0/app/web_portal"

# Leer foto base64
with open(os.path.join(brain_dir, "slone_original_sketch_card.jpg"), "rb") as f:
    b64_card = base64.b64encode(f.read()).decode('utf-8')

# Leer SVGs
def read_svg(filename):
    with open(os.path.join(brain_dir, filename), "r", encoding="utf-8") as f:
        return f.read()

svg_rune = read_svg("slone_symbol_rune_bluetooth.svg")
svg_pulse = read_svg("slone_symbol_medical_pulse.svg")
svg_graffiti = read_svg("slone_symbol_graffiti_pure.svg")
svg_nexus = read_svg("slone_symbol_nexus_connectivity.svg")
svg_lovefrom = read_svg("logo_lovefrom.svg")
svg_teenage = read_svg("logo_teenage.svg")
svg_pentagram = read_svg("logo_pentagram.svg")
svg_collins = read_svg("logo_collins.svg")
svg_workandco = read_svg("logo_workandco.svg")

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SLÖNE · THE VISUAL BRAND BOOK · GLOBAL PITCH</title>
  <style>
    :root {{
      --bg-dark: #050811;
      --card-bg: #090E1A;
      --border-color: rgba(255, 255, 255, 0.1);
      --cyan: #00F0FF;
      --cyan-glow: rgba(0, 240, 255, 0.35);
      --orange: #FF4400;
      --gold: #D4AF37;
      --green: #00FF66;
      --text-white: #FFFFFF;
      --text-muted: #8E9BAE;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; user-select: none; }}
    body {{
      background: var(--bg-dark);
      color: var(--text-white);
      font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', 'Segoe UI', Roboto, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
    }}
    
    /* HEADER EJECUTIVO & NAVEGADOR */
    header {{
      background: rgba(9, 14, 26, 0.85);
      backdrop-filter: blur(20px);
      border-bottom: 1px solid var(--border-color);
      padding: 12px 24px;
      position: sticky;
      top: 0;
      z-index: 100;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }}
    .brand-mark {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .brand-logo-pill {{
      background: linear-gradient(135deg, #00F0FF, #0077FF);
      color: #000;
      font-weight: 900;
      font-size: 11px;
      letter-spacing: 2px;
      padding: 4px 10px;
      border-radius: 6px;
      text-transform: uppercase;
    }}
    .brand-title {{
      font-size: 17px;
      font-weight: 900;
      letter-spacing: 1.5px;
    }}
    .nav-tabs {{
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding: 4px 0;
      scrollbar-width: none;
    }}
    .nav-tabs::-webkit-scrollbar {{ display: none; }}
    .nav-btn {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.08);
      color: var(--text-muted);
      font-size: 11px;
      font-weight: 700;
      padding: 8px 14px;
      border-radius: 8px;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .nav-btn:hover {{
      background: rgba(255, 255, 255, 0.12);
      color: #FFF;
      border-color: rgba(255, 255, 255, 0.2);
    }}
    .nav-btn.active {{
      background: var(--cyan);
      color: #000;
      border-color: var(--cyan);
      font-weight: 800;
      box-shadow: 0 0 16px var(--cyan-glow);
    }}

    /* MAIN STAGE */
    main {{
      flex: 1;
      padding: 24px;
      max-width: 1400px;
      margin: 0 auto;
      width: 100%;
    }}

    .section-view {{
      display: none;
      animation: fadeIn 0.3s ease-out;
    }}
    .section-view.active {{
      display: block;
    }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(8px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* HERO COVER */
    .hero-banner {{
      background: linear-gradient(180deg, rgba(0, 240, 255, 0.08) 0%, rgba(9, 14, 26, 0.6) 100%);
      border: 1px solid var(--border-color);
      border-radius: 20px;
      padding: 40px;
      text-align: center;
      margin-bottom: 24px;
      position: relative;
      overflow: hidden;
    }}
    .hero-banner::before {{
      content: '';
      position: absolute;
      top: -50%;
      left: 50%;
      transform: translateX(-50%);
      width: 600px;
      height: 300px;
      background: radial-gradient(circle, var(--cyan-glow) 0%, transparent 70%);
      pointer-events: none;
    }}
    .hero-tag {{
      display: inline-block;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 3px;
      color: var(--cyan);
      text-transform: uppercase;
      margin-bottom: 12px;
    }}
    .hero-title {{
      font-size: 44px;
      font-weight: 900;
      letter-spacing: 6px;
      margin-bottom: 12px;
      text-shadow: 0 4px 24px rgba(0,0,0,0.8);
    }}
    .hero-sub {{
      font-size: 14px;
      color: var(--text-muted);
      letter-spacing: 1px;
      max-width: 640px;
      margin: 0 auto 24px auto;
    }}

    /* GRID LAYOUTS */
    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-bottom: 24px;
    }}
    .grid-3 {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-bottom: 24px;
    }}
    .grid-4 {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 24px;
    }}
    @media (max-width: 992px) {{
      .grid-2, .grid-3, .grid-4 {{ grid-template-columns: 1fr; }}
    }}

    /* CARDS */
    .showcase-card {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      position: relative;
      transition: all 0.25s ease;
    }}
    .showcase-card:hover {{
      border-color: rgba(0, 240, 255, 0.4);
      box-shadow: 0 12px 30px rgba(0,0,0,0.6);
    }}
    .card-header-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      padding-bottom: 12px;
    }}
    .card-badge {{
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 1.5px;
      padding: 3px 8px;
      border-radius: 4px;
      text-transform: uppercase;
    }}
    .badge-cyan {{ background: rgba(0, 240, 255, 0.15); color: var(--cyan); border: 1px solid var(--cyan); }}
    .badge-orange {{ background: rgba(255, 68, 0, 0.15); color: var(--orange); border: 1px solid var(--orange); }}
    .badge-gold {{ background: rgba(212, 175, 55, 0.15); color: var(--gold); border: 1px solid var(--gold); }}
    .badge-green {{ background: rgba(0, 255, 102, 0.15); color: var(--green); border: 1px solid var(--green); }}

    .preview-box {{
      background: #020409;
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 24px;
      min-height: 200px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 16px;
      position: relative;
      overflow: hidden;
    }}
    .preview-box img {{
      max-width: 100%;
      max-height: 240px;
      object-fit: contain;
      border-radius: 8px;
    }}
    .preview-box svg {{
      max-width: 100%;
      max-height: 180px;
    }}

    /* COLOR PALETTES */
    .palette-row {{
      display: flex;
      gap: 8px;
      margin-top: auto;
      padding-top: 14px;
    }}
    .swatch {{
      flex: 1;
      height: 36px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 9px;
      font-weight: 800;
      letter-spacing: 0.5px;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }}

    /* HARDWARE MOCKUPS */
    .hw-monolith {{
      width: 100%;
      height: 180px;
      background: linear-gradient(145deg, #181D26, #0A0D14);
      border: 1px solid #334155;
      border-radius: 14px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.9);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 24px 32px;
      position: relative;
    }}
    .hw-monolith::after {{
      content: '';
      position: absolute;
      bottom: 0;
      left: 10%;
      right: 10%;
      height: 2px;
      background: var(--cyan);
      box-shadow: 0 0 14px var(--cyan);
    }}
    .hw-remote {{
      width: 60px;
      height: 160px;
      background: #0E121C;
      border: 1px solid #475569;
      border-radius: 30px;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 14px 6px;
      justify-content: space-between;
      box-shadow: -10px 10px 30px rgba(0,0,0,0.8);
    }}
    .remote-dpad {{
      width: 38px;
      height: 38px;
      border-radius: 50%;
      border: 2px solid #334155;
      background: #1E293B;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .remote-btn {{
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background: var(--cyan);
      box-shadow: 0 0 8px var(--cyan);
    }}

    /* TEENAGE ENGINEERING FIELD RECORDER MOCKUP */
    .te-field-box {{
      width: 100%;
      height: 190px;
      background: #141414;
      border: 2px solid #333333;
      border-radius: 10px;
      padding: 16px;
      display: flex;
      gap: 16px;
      align-items: center;
      box-shadow: 0 15px 35px rgba(0,0,0,0.9);
    }}
    .te-screen {{
      flex: 1;
      height: 100%;
      background: #050505;
      border: 1px solid #222;
      border-radius: 6px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .te-controls {{
      width: 120px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .te-dial {{
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: #222;
      border: 2px solid #555;
      position: relative;
    }}
    .te-dial::after {{
      content: '';
      position: absolute;
      top: 4px;
      left: 50%;
      transform: translateX(-50%);
      width: 4px;
      height: 12px;
      background: var(--orange);
      border-radius: 2px;
    }}

    /* WORK & CO TV 10-FOOT UI MOCKUP */
    .tv-screen-mockup {{
      width: 100%;
      height: 220px;
      background: #000;
      border: 2px solid #27272A;
      border-radius: 12px;
      padding: 14px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
      overflow: hidden;
    }}
    .tv-top-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .tv-live-badge {{
      background: var(--green);
      color: #000;
      font-size: 9px;
      font-weight: 900;
      padding: 3px 6px;
      border-radius: 4px;
      display: flex;
      align-items: center;
      gap: 4px;
    }}
    .tv-grid-channels {{
      display: flex;
      gap: 12px;
      margin-top: 12px;
    }}
    .tv-channel-card {{
      flex: 1;
      background: #11141C;
      border: 1px solid #27272A;
      border-radius: 8px;
      padding: 10px;
      transition: all 0.2s ease;
    }}
    .tv-channel-card.focused {{
      border: 2px solid var(--green);
      box-shadow: 0 0 16px rgba(0, 255, 102, 0.4);
      transform: scale(1.04);
    }}

    /* VOTE / SELECTION BAR */
    .vote-panel {{
      background: rgba(9, 14, 26, 0.95);
      border: 1px solid var(--cyan);
      border-radius: 16px;
      padding: 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 32px;
      box-shadow: 0 0 30px var(--cyan-glow);
    }}
    .select-btn {{
      background: var(--cyan);
      color: #000;
      border: none;
      font-size: 13px;
      font-weight: 900;
      letter-spacing: 1px;
      padding: 12px 28px;
      border-radius: 8px;
      cursor: pointer;
      text-transform: uppercase;
      transition: all 0.2s ease;
    }}
    .select-btn:hover {{
      background: #FFF;
      box-shadow: 0 0 20px #FFF;
      transform: scale(1.05);
    }}

    /* TOAST */
    .toast {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #00F0FF;
      color: #000;
      padding: 14px 24px;
      border-radius: 10px;
      font-weight: 900;
      font-size: 13px;
      letter-spacing: 1px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.8);
      display: none;
      z-index: 999;
    }}
  </style>
</head>
<body>

  <!-- HEADER NAVEGADOR -->
  <header>
    <div class="brand-mark">
      <div class="brand-logo-pill">SLÖNE</div>
      <div class="brand-title">VISUAL BRAND BOOK</div>
    </div>
    <div class="nav-tabs">
      <button class="nav-btn active" onclick="switchTab('tab-all', this)">0. Visión Global</button>
      <button class="nav-btn" onclick="switchTab('tab-origin', this)">1. ADN Artista</button>
      <button class="nav-btn" onclick="switchTab('tab-symbols', this)">2. Símbolos Maestros</button>
      <button class="nav-btn" onclick="switchTab('tab-lovefrom', this)">3. LoveFrom</button>
      <button class="nav-btn" onclick="switchTab('tab-teenage', this)">4. Teenage Eng.</button>
      <button class="nav-btn" onclick="switchTab('tab-pentagram', this)">5. Pentagram</button>
      <button class="nav-btn" onclick="switchTab('tab-collins', this)">6. COLLINS</button>
      <button class="nav-btn" onclick="switchTab('tab-workandco', this)">7. Work & Co</button>
      <button class="nav-btn" onclick="switchTab('tab-decision', this)" style="border-color: var(--cyan); color: var(--cyan);">✦ Decisión CEO</button>
    </div>
  </header>

  <main>

    <!-- PESTAÑA 0: VISIÓN GLOBAL (PITCH ROOM) -->
    <section id="tab-all" class="section-view active">
      <div class="hero-banner">
        <div class="hero-tag">SISTEMA DE IDENTIDAD DE MARCA · PROPOSICIÓN VISUAL PURA</div>
        <div class="hero-title">SLÖNE: SOMOS CONECTIVIDAD</div>
        <div class="hero-sub">Cero números '1' forzados. El pulso vital de emisión deportiva, la runa de enlace universal y las 5 interpretaciones de las agencias más influyentes del planeta.</div>
      </div>

      <div class="grid-3">
        <!-- 1. ADN ORIGINAL -->
        <div class="showcase-card" onclick="switchTab('tab-origin', document.querySelectorAll('.nav-btn')[1])" style="cursor: pointer;">
          <div class="card-header-bar">
            <span style="font-weight: 800; font-size: 13px;">01 · ADN DEL FUNDADOR</span>
            <span class="card-badge badge-cyan">AUTÉNTICO</span>
          </div>
          <div class="preview-box">
            <img src="data:image/jpeg;base64,{b64_card}" alt="Boceto Original">
          </div>
          <div style="font-size: 11px; color: var(--text-muted);">Boceto manuscrito a bolígrafo traducido fielmente a cromo pulido y vectores.</div>
        </div>

        <!-- 2. RUNA BLUETOOTH -->
        <div class="showcase-card" onclick="switchTab('tab-symbols', document.querySelectorAll('.nav-btn')[2])" style="cursor: pointer;">
          <div class="card-header-bar">
            <span style="font-weight: 800; font-size: 13px;">02 · LA RUNA CONECTIVIDAD</span>
            <span class="card-badge badge-cyan">SÍMBOLO GLOBAL</span>
          </div>
          <div class="preview-box">
            {svg_rune}
          </div>
          <div style="font-size: 11px; color: var(--text-muted);">El isotipo independiente nivel Apple  o Bluetooth ᛒ. Reconocible al instante.</div>
        </div>

        <!-- 3. ONDA MÉDICA EKG -->
        <div class="showcase-card" onclick="switchTab('tab-symbols', document.querySelectorAll('.nav-btn')[2])" style="cursor: pointer;">
          <div class="card-header-bar">
            <span style="font-weight: 800; font-size: 13px;">03 · PULSO VITAL EKG</span>
            <span class="card-badge badge-green">60 HZ LIVE</span>
          </div>
          <div class="preview-box">
            {svg_pulse}
          </div>
          <div style="font-size: 11px; color: var(--text-muted);">Frecuencia cardíaca de retransmisión deportiva continua con electrodos en la Ö.</div>
        </div>
      </div>

      <!-- AGENCIA BANNER GRID -->
      <div style="font-size: 12px; font-weight: 800; letter-spacing: 2px; color: var(--text-muted); margin-bottom: 14px; text-transform: uppercase;">
        PROPUESTAS DE LAS 5 GRANDES AGENCIAS
      </div>

      <div class="grid-2">
        <!-- LOVEFROM -->
        <div class="showcase-card" onclick="switchTab('tab-lovefrom', document.querySelectorAll('.nav-btn')[3])" style="cursor: pointer;">
          <div class="card-header-bar">
            <span style="font-weight: 800; font-size: 14px;">LOVEFROM · JONY IVE</span>
            <span class="card-badge badge-cyan">TITANIO ÓPTICO</span>
          </div>
          <div class="preview-box">
            {svg_lovefrom}
          </div>
          <div class="palette-row">
            <div class="swatch" style="background: #FFFFFF; color: #000;">#FFF</div>
            <div class="swatch" style="background: #E2E8F0; color: #000;">#E2E8F0</div>
            <div class="swatch" style="background: #0B0E14; color: #FFF;">#0B0E14</div>
          </div>
        </div>

        <!-- TEENAGE ENGINEERING -->
        <div class="showcase-card" onclick="switchTab('tab-teenage', document.querySelectorAll('.nav-btn')[4])" style="cursor: pointer;">
          <div class="card-header-bar">
            <span style="font-weight: 800; font-size: 14px;">TEENAGE ENGINEERING</span>
            <span class="card-badge badge-orange">ANALÓGICO TÁCTICO</span>
          </div>
          <div class="preview-box">
            {svg_teenage}
          </div>
          <div class="palette-row">
            <div class="swatch" style="background: #FF4400; color: #FFF;">#FF4400</div>
            <div class="swatch" style="background: #141414; color: #FFF;">#141414</div>
            <div class="swatch" style="background: #FFFFFF; color: #000;">#FFF</div>
          </div>
        </div>

        <!-- PENTAGRAM -->
        <div class="showcase-card" onclick="switchTab('tab-pentagram', document.querySelectorAll('.nav-btn')[5])" style="cursor: pointer;">
          <div class="card-header-bar">
            <span style="font-weight: 800; font-size: 14px;">PENTAGRAM</span>
            <span class="card-badge badge-gold">HERÁLDICA INSTITUCIONAL</span>
          </div>
          <div class="preview-box">
            {svg_pentagram}
          </div>
          <div class="palette-row">
            <div class="swatch" style="background: #D4AF37; color: #000;">#D4AF37</div>
            <div class="swatch" style="background: #0D1B2A; color: #FFF;">#0D1B2A</div>
            <div class="swatch" style="background: #8492A6; color: #000;">#8492A6</div>
          </div>
        </div>

        <!-- COLLINS -->
        <div class="showcase-card" onclick="switchTab('tab-collins', document.querySelectorAll('.nav-btn')[6])" style="cursor: pointer;">
          <div class="card-header-bar">
            <span style="font-weight: 800; font-size: 14px;">COLLINS</span>
            <span class="card-badge badge-cyan">ONDA DE ESTADIO VIVA</span>
          </div>
          <div class="preview-box">
            {svg_collins}
          </div>
          <div class="palette-row">
            <div class="swatch" style="background: #00F0FF; color: #000;">#00F0FF</div>
            <div class="swatch" style="background: #7000FF; color: #FFF;">#7000FF</div>
            <div class="swatch" style="background: #040711; color: #FFF;">#040711</div>
          </div>
        </div>
      </div>
    </section>

    <!-- PESTAÑA 1: ADN DEL ARTISTA & BOCETO -->
    <section id="tab-origin" class="section-view">
      <div class="hero-banner" style="padding: 24px;">
        <div class="hero-tag">CAPA 0 · ADN DEL FUNDADOR</div>
        <div class="hero-title" style="font-size: 32px;">DEL BOLÍGRAFO AL CROMO PULIDO</div>
        <div class="hero-sub">El trazo grafitero genuino de tu tarjeta física: comillas, remate de flecha inferior y runa vertical.</div>
      </div>

      <div class="grid-2">
        <div class="showcase-card">
          <div class="card-header-bar">
            <span style="font-weight: 800;">FOTO ORIGINAL DE TU TARJETA</span>
            <span class="card-badge badge-gold">MANUSCRITO REAL</span>
          </div>
          <div class="preview-box" style="min-height: 280px;">
            <img src="data:image/jpeg;base64,{b64_card}" alt="Foto Manuscrita">
          </div>
          <div style="font-size: 12px; color: var(--text-muted); line-height: 1.6;">
            <strong>Análisis del trazo:</strong> Firma con comillas de autoridad callejera (" "), 'Ö' con satélites diacríticos, trazo dinámico en 'N' y 'E', flecha direccional inferior y símbolo rúnico vertical de conectividad en el centro.
          </div>
        </div>

        <div class="showcase-card">
          <div class="card-header-bar">
            <span style="font-weight: 800;">TRADUCCIÓN VECTORIAL · TAG GRAFITERO</span>
            <span class="card-badge badge-cyan">CROMO & AEROSOL</span>
          </div>
          <div class="preview-box" style="min-height: 280px;">
            {svg_graffiti}
          </div>
          <div style="font-size: 12px; color: var(--text-muted); line-height: 1.6;">
            <strong>Vectorización de alta fidelidad:</strong> Geometría depurada para corte láser, bordado en gorras/ropa urbana y branding rebelde sin perder el salvajismo del aerosol original.
          </div>
        </div>
      </div>
    </section>

    <!-- PESTAÑA 2: LOS DOS SÍMBOLOS MAESTROS -->
    <section id="tab-symbols" class="section-view">
      <div class="hero-banner" style="padding: 24px;">
        <div class="hero-tag">ISOTIPOS INDEPENDIENTES</div>
        <div class="hero-title" style="font-size: 32px;">LA RUNA BLUETOOTH & LA ONDA MÉDICA</div>
        <div class="hero-sub">Símbolos soberanos capaces de vivir sin texto en mandos a distancia, chips de TV y vallas publicitarias.</div>
      </div>

      <div class="grid-2">
        <!-- RUNA -->
        <div class="showcase-card">
          <div class="card-header-bar">
            <span style="font-weight: 800;">OPCIÓN A: LA RUNA DE CONECTIVIDAD</span>
            <span class="card-badge badge-cyan">HERENCIA RÚNICA</span>
          </div>
          <div class="preview-box" style="min-height: 260px;">
            {svg_rune}
          </div>
          <div style="font-size: 13px; font-weight: 800; margin-bottom: 6px;">Símbolo Universal de Enlace Inalámbrico</div>
          <div style="font-size: 12px; color: var(--text-muted); line-height: 1.5;">
            Basado directamente en el dibujo rúnico central de la tarjeta. Espejo moderno del símbolo Bluetooth (ᛒ), fusionando la 'S' angular con la antena y las diéresis de la Ö.
          </div>
        </div>

        <!-- PULSO MÉDICO -->
        <div class="showcase-card">
          <div class="card-header-bar">
            <span style="font-weight: 800;">OPCIÓN B: ONDA MÉDICA / PULSO EKG</span>
            <span class="card-badge badge-green">FRECUENCIA VIVA</span>
          </div>
          <div class="preview-box" style="min-height: 260px;">
            {svg_pulse}
          </div>
          <div style="font-size: 13px; font-weight: 800; margin-bottom: 6px;">Frecuencia Cardíaca de Estadio a 60 Hz</div>
          <div style="font-size: 12px; color: var(--text-muted); line-height: 1.5;">
            El pulso vital que mantiene vivo el deporte. El trazado electrocardiográfico que dibuja el latido del partido en directo, con los electrodos diacríticos sobre el pico R.
          </div>
        </div>
      </div>

      <!-- NEXUS HÍBRIDO -->
      <div class="showcase-card">
        <div class="card-header-bar">
          <span style="font-weight: 800;">OPCIÓN C: NEXUS MONOLÍTICO DE CONECTIVIDAD</span>
          <span class="card-badge badge-cyan">PÍLDORA DE HARDWARE</span>
        </div>
        <div class="preview-box" style="min-height: 140px;">
          {svg_nexus}
        </div>
      </div>
    </section>

    <!-- PESTAÑA 3: LOVEFROM (JONY IVE) -->
    <section id="tab-lovefrom" class="section-view">
      <div class="hero-banner" style="padding: 24px;">
        <div class="hero-tag">PROPUESTA DE AGENCIA · LOVEFROM</div>
        <div class="hero-title" style="font-size: 32px;">EL MONOLITO DE TITANIO ÓPTICO</div>
        <div class="hero-sub">Pureza absoluta, precisión de micras y hardware de lujo silencioso. Cero redundancias.</div>
      </div>

      <div class="grid-2">
        <div class="showcase-card">
          <div class="card-header-bar">
            <span style="font-weight: 800;">IDENTIDAD VISUAL LOVEFROM</span>
            <span class="card-badge badge-cyan">CALIFORNIA MINIMALISM</span>
          </div>
          <div class="preview-box" style="min-height: 240px;">
            {svg_lovefrom}
          </div>
          <div style="font-size: 12px; color: var(--text-muted); line-height: 1.6;">
            <strong>Concepto:</strong> Runa de conectividad tallada con diamante en prisma de cristal de zafiro. Wordmark con espaciado monumental que transmite la calma de un dispositivo premium indiscutible.
          </div>
        </div>

        <div class="showcase-card">
          <div class="card-header-bar">
            <span style="font-weight: 800;">HARDWARE · SLÖNE BOX & REMOTE</span>
            <span class="card-badge badge-cyan">MOCKUP REALISTA</span>
          </div>
          <div class="preview-box" style="min-height: 240px; background: #070A10;">
            <div class="hw-monolith">
              <div style="display: flex; flex-direction: column; gap: 8px;">
                <div style="font-weight: 900; font-size: 18px; letter-spacing: 4px;">SLÖNE</div>
                <div style="font-size: 9px; color: var(--cyan); letter-spacing: 2px;">TITANIUM STREAM NODE</div>
              </div>
              <div class="hw-remote">
                <div class="remote-dpad"></div>
                <div class="remote-btn"></div>
              </div>
            </div>
          </div>
          <div style="font-size: 12px; color: var(--text-muted);">
            Carcasa mecanizada en un solo bloque de aluminio aeroespacial. Botón físico de mando con retroiluminación viva de la runa SLÖNE.
          </div>
        </div>
      </div>
    </section>

    <!-- PESTAÑA 4: TEENAGE ENGINEERING -->
    <section id="tab-teenage" class="section-view">
      <div class="hero-banner" style="padding: 24px;">
        <div class="hero-tag">PROPUESTA DE AGENCIA · TEENAGE ENGINEERING</div>
        <div class="hero-title" style="font-size: 32px;">EL INSTRUMENTO TÁCTICO DE EMISIÓN</div>
        <div class="hero-sub">Ingeniería industrial sueca, perillas mecánicas de alta fricción y naranja de alerta deportiva.</div>
      </div>

      <div class="grid-2">
        <div class="showcase-card">
          <div class="card-header-bar">
            <span style="font-weight: 800;">IDENTIDAD TÉCNICA</span>
            <span class="card-badge badge-orange">STOCKHOLM INDUSTRIAL</span>
          </div>
          <div class="preview-box" style="min-height: 240px;">
            {svg_teenage}
          </div>
          <div style="font-size: 12px; color: var(--text-muted); line-height: 1.6;">
            <strong>Concepto:</strong> Dial analógico de osciloscopio en chasis oscuro con indicador de estado en naranja de emergencia (#FF4400). Tipografía monospace de precisión suiza.
          </div>
        </div>

        <div class="showcase-card">
          <div class="card-header-bar">
            <span style="font-weight: 800;">HARDWARE · FIELD BROADCAST UNIT</span>
            <span class="card-badge badge-orange">MOCKUP SINTETIZADOR</span>
          </div>
          <div class="preview-box" style="min-height: 240px; background: #070707;">
            <div class="te-field-box">
              <div class="te-screen">
                <div style="font-family: monospace; font-size: 10px; color: var(--orange); font-weight: 800;">LIVE BROADCAST // 2.4 GHZ</div>
                <div style="font-family: monospace; font-size: 20px; font-weight: 900; color: #FFF; letter-spacing: 2px;">SLÖNE.FIELD</div>
                <div style="font-family: monospace; font-size: 9px; color: #888;">LATENCY: 0.08 MS · STEREO SYNC</div>
              </div>
              <div class="te-controls">
                <div style="display: flex; gap: 8px;">
                  <div class="te-dial"></div>
                  <div class="te-dial" style="border-color: var(--orange);"></div>
                </div>
                <div style="background: #222; height: 18px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 8px; font-family: monospace; font-weight: 900; color: var(--orange);">PUSH TO SYNC</div>
              </div>
            </div>
          </div>
          <div style="font-size: 12px; color: var(--text-muted);">
            Dispositivo de audio de bolsillo para casters y streaming en vivo en el campo de fútbol.
          </div>
        </div>
      </div>
    </section>

    <!-- PESTAÑA 5: PENTAGRAM -->
    <section id="tab-pentagram" class="section-view">
      <div class="hero-banner" style="padding: 24px;">
        <div class="hero-tag">PROPUESTA DE AGENCIA · PENTAGRAM</div>
        <div class="hero-title" style="font-size: 32px;">HERÁLDICA MONUMENTAL SOBERANA</div>
        <div class="hero-sub">Diseño institucional de máxima autoridad internacional. Oro viejo sobre azul prusiano profundo.</div>
      </div>

      <div class="grid-2">
        <div class="showcase-card">
          <div class="card-header-bar">
            <span style="font-weight: 800;">IDENTIDAD INSTITUCIONAL</span>
            <span class="card-badge badge-gold">NEW YORK & LONDON</span>
          </div>
          <div class="preview-box" style="min-height: 240px;">
            {svg_pentagram}
          </div>
          <div style="font-size: 12px; color: var(--text-muted); line-height: 1.6;">
            <strong>Concepto:</strong> Sello heráldico de tres puntas en líneas finas de oro. Tipografía serif monumental que establece a SLÖNE como una casa de retransmisión soberana establecida para perdurar siglos.
          </div>
        </div>

        <div class="showcase-card">
          <div class="card-header-bar">
            <span style="font-weight: 800;">MEMBRESÍA VIP · TITANIUM CARD</span>
            <span class="card-badge badge-gold">APLICACIÓN REAL</span>
          </div>
          <div class="preview-box" style="min-height: 240px; background: #07090F;">
            <div style="width: 280px; height: 165px; background: linear-gradient(135deg, #1C2331, #0A0D14); border: 1px solid var(--gold); border-radius: 12px; padding: 18px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 15px 35px rgba(0,0,0,0.9);">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-family: serif; font-size: 18px; font-weight: 900; letter-spacing: 4px; color: #FFF;">SLÖNE</div>
                <div style="width: 18px; height: 18px; border: 1px solid var(--gold); border-radius: 50%;"></div>
              </div>
              <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                <div>
                  <div style="font-size: 9px; color: var(--gold); letter-spacing: 2px;">FOUNDER PASS</div>
                  <div style="font-size: 11px; font-weight: 700; color: #FFF;">SLONE · SOVEREIGN 001</div>
                </div>
                <div style="font-size: 8px; color: #64748B;">NFC LIVE KEY</div>
              </div>
            </div>
          </div>
          <div style="font-size: 12px; color: var(--text-muted);">
            Tarjeta de socio en metal noble para acceso a palcos de estadio y retransmisión sin compresión.
          </div>
        </div>
      </div>
    </section>

    <!-- PESTAÑA 6: COLLINS -->
    <section id="tab-collins" class="section-view">
      <div class="hero-banner" style="padding: 24px;">
        <div class="hero-tag">PROPUESTA DE AGENCIA · COLLINS</div>
        <div class="hero-title" style="font-size: 32px;">LA ONDA CINÉTICA DE ESTADIO</div>
        <div class="hero-sub">Identidad viva y reactiva al volumen de la hinchada. Cian eléctrico y energía pura.</div>
      </div>

      <div class="grid-2">
        <div class="showcase-card">
          <div class="card-header-bar">
            <span style="font-weight: 800;">IDENTIDAD CINÉTICA</span>
            <span class="card-badge badge-cyan">SOUND-REACTIVE</span>
          </div>
          <div class="preview-box" style="min-height: 240px;">
            {svg_collins}
          </div>
          <div style="font-size: 12px; color: var(--text-muted); line-height: 1.6;">
            <strong>Concepto:</strong> La onda sonora que vibra cuando hay gol. Logotipo cinético que se modula en tiempo real según la presión acústica del estadio y la emoción de los casters.
          </div>
        </div>

        <div class="showcase-card">
          <div class="card-header-bar">
            <span style="font-weight: 800;">VALLA DE ESTADIO · LED RIBBON 360°</span>
            <span class="card-badge badge-cyan">MOCKUP ESTADIO</span>
          </div>
          <div class="preview-box" style="min-height: 240px; background: #020306;">
            <div style="width: 100%; height: 100px; background: #000; border: 1px solid var(--cyan); border-radius: 8px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; box-shadow: 0 0 25px var(--cyan-glow);">
              <div style="font-size: 36px; font-weight: 900; letter-spacing: 16px; color: #FFF; text-shadow: 0 0 20px var(--cyan);">SLÖNE</div>
              <div style="position: absolute; bottom: 8px; font-size: 9px; font-weight: 800; letter-spacing: 4px; color: var(--cyan);">THE LIVING PULSE OF LIVE SPORTS</div>
            </div>
          </div>
          <div style="font-size: 12px; color: var(--text-muted);">
            Proyección en paneles perimetrales de estadios de fútbol y marquesinas de Times Square.
          </div>
        </div>
      </div>
    </section>

    <!-- PESTAÑA 7: WORK & CO -->
    <section id="tab-workandco" class="section-view">
      <div class="hero-banner" style="padding: 24px;">
        <div class="hero-tag">PROPUESTA DE AGENCIA · WORK & CO</div>
        <div class="hero-title" style="font-size: 32px;">SISTEMA OPERATIVO 10-FOOT TV UI</div>
        <div class="hero-sub">Diseñado milimétricamente para pantallas de televisión y navegación instantánea con mando a distancia.</div>
      </div>

      <div class="grid-2">
        <div class="showcase-card">
          <div class="card-header-bar">
            <span style="font-weight: 800;">IDENTIDAD DE SISTEMA (SLÖNE OS)</span>
            <span class="card-badge badge-green">DIGITAL PRODUCT</span>
          </div>
          <div class="preview-box" style="min-height: 240px;">
            {svg_workandco}
          </div>
          <div style="font-size: 12px; color: var(--text-muted); line-height: 1.6;">
            <strong>Concepto:</strong> El círculo de sincronización con señal en verde vivo (#00FF66). Tipografía Inter Tight hiper-legible a 3 metros de distancia desde el sofá.
          </div>
        </div>

        <div class="showcase-card">
          <div class="card-header-bar">
            <span style="font-weight: 800;">INTERFAZ SMART TV · FOCO ACTIVO</span>
            <span class="card-badge badge-green">MOCKUP TV EN VIVO</span>
          </div>
          <div class="preview-box" style="min-height: 240px;">
            <div class="tv-screen-mockup">
              <div class="tv-top-bar">
                <div style="font-size: 13px; font-weight: 900; letter-spacing: 2px;">SLÖNE TV</div>
                <div class="tv-live-badge"><div style="width: 5px; height: 5px; border-radius: 50%; background: #000;"></div> DIRECTO 4K</div>
              </div>
              <div class="tv-grid-channels">
                <div class="tv-channel-card focused">
                  <div style="font-size: 11px; font-weight: 900; color: var(--green);">EL CLÁSICO LIVE</div>
                  <div style="font-size: 8px; color: #888;">AUDIO: SLONE CASIS</div>
                </div>
                <div class="tv-channel-card">
                  <div style="font-size: 11px; font-weight: 700; color: #FFF;">PREMIER LEAGUE</div>
                  <div style="font-size: 8px; color: #888;">SONIDO AMBIENTE</div>
                </div>
              </div>
            </div>
          </div>
          <div style="font-size: 12px; color: var(--text-muted);">
            Foco verde de alta visibilidad para moverte con las flechas del mando a distancia sin perderte jamás.
          </div>
        </div>
      </div>
    </section>

    <!-- PESTAÑA 8: TABLERO DE DECISIÓN DEL CEO -->
    <section id="tab-decision" class="section-view">
      <div class="hero-banner" style="padding: 24px;">
        <div class="hero-tag">SALA DE DECISIÓN DEL CEO</div>
        <div class="hero-title" style="font-size: 32px;">ELIGE LA DIRECCIÓN DE SLÖNE</div>
        <div class="hero-sub">Haz clic en la propuesta que mejor represente tu visión para adoptarla como identidad oficial del ecosistema.</div>
      </div>

      <div class="grid-3">
        <!-- 1. GRAFFITI ADN -->
        <div class="showcase-card choice-card" id="choice-graffiti">
          <div class="card-header-bar">
            <span style="font-weight: 800;">1. GRAFFITI ADN</span>
            <span class="card-badge badge-cyan">ORIGINAL</span>
          </div>
          <div class="preview-box" style="min-height: 150px;">
            {svg_graffiti}
          </div>
          <button class="select-btn" onclick="selectChoice('GRAFFITI ADN (Firma auténtica en cromo)')">ELEGIR ÉSTA</button>
        </div>

        <!-- 2. RUNA BLUETOOTH -->
        <div class="showcase-card choice-card" id="choice-rune">
          <div class="card-header-bar">
            <span style="font-weight: 800;">2. RUNA BLUETOOTH</span>
            <span class="card-badge badge-cyan">SÍMBOLO GLOBAL</span>
          </div>
          <div class="preview-box" style="min-height: 150px;">
            {svg_rune}
          </div>
          <button class="select-btn" onclick="selectChoice('RUNA BLUETOOTH (Isotipo universal de conectividad)')">ELEGIR ÉSTA</button>
        </div>

        <!-- 3. PULSO MÉDICO EKG -->
        <div class="showcase-card choice-card" id="choice-pulse">
          <div class="card-header-bar">
            <span style="font-weight: 800;">3. PULSO MÉDICO EKG</span>
            <span class="card-badge badge-green">VITAL 60HZ</span>
          </div>
          <div class="preview-box" style="min-height: 150px;">
            {svg_pulse}
          </div>
          <button class="select-btn" onclick="selectChoice('PULSO MÉDICO EKG (Onda vital deportiva)')">ELEGIR ÉSTA</button>
        </div>

        <!-- 4. LOVEFROM -->
        <div class="showcase-card choice-card" id="choice-lovefrom">
          <div class="card-header-bar">
            <span style="font-weight: 800;">4. LOVEFROM</span>
            <span class="card-badge badge-cyan">TITANIO JONY IVE</span>
          </div>
          <div class="preview-box" style="min-height: 150px;">
            {svg_lovefrom}
          </div>
          <button class="select-btn" onclick="selectChoice('LOVEFROM (Titanio puro y zafiro óptico)')">ELEGIR ÉSTA</button>
        </div>

        <!-- 5. TEENAGE ENGINEERING -->
        <div class="showcase-card choice-card" id="choice-teenage">
          <div class="card-header-bar">
            <span style="font-weight: 800;">5. TEENAGE ENGINEERING</span>
            <span class="card-badge badge-orange">ANALÓGICO</span>
          </div>
          <div class="preview-box" style="min-height: 150px;">
            {svg_teenage}
          </div>
          <button class="select-btn" onclick="selectChoice('TEENAGE ENGINEERING (Instrumento industrial naranja)')">ELEGIR ÉSTA</button>
        </div>

        <!-- 6. COLLINS -->
        <div class="showcase-card choice-card" id="choice-collins">
          <div class="card-header-bar">
            <span style="font-weight: 800;">6. COLLINS</span>
            <span class="card-badge badge-cyan">ONDA ESTADIO</span>
          </div>
          <div class="preview-box" style="min-height: 150px;">
            {svg_collins}
          </div>
          <button class="select-btn" onclick="selectChoice('COLLINS (Onda cinética sonora de estadio)')">ELEGIR ÉSTA</button>
        </div>
      </div>

      <div class="vote-panel">
        <div>
          <div style="font-size: 11px; font-weight: 800; letter-spacing: 2px; color: var(--cyan); text-transform: uppercase;">ESTADO DE DECISIÓN DE DIRECCIÓN</div>
          <div id="selection-status" style="font-size: 18px; font-weight: 900; margin-top: 4px;">Selecciona una propuesta arriba para fijar la identidad de SLÖNE.</div>
        </div>
      </div>
    </section>

  </main>

  <div id="toast" class="toast">✦ PROPUESTA SELECCIONADA POR EL CEO</div>

  <script>
    function switchTab(tabId, btn) {{
      document.querySelectorAll('.section-view').forEach(s => s.classList.remove('active'));
      document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
      
      const target = document.getElementById(tabId);
      if (target) target.classList.add('active');
      if (btn) btn.classList.add('active');
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function selectChoice(name) {{
      document.getElementById('selection-status').innerText = 'SELECCIÓN CONFIRMADA: ' + name;
      const toast = document.getElementById('toast');
      toast.innerText = '✦ ' + name + ' SELECCIONADO';
      toast.style.display = 'block';
      setTimeout(() => {{ toast.style.display = 'none'; }}, 3500);
    }}

    // Atajos de teclado para pase de diapositivas (Flechas izquierda/derecha o números 0-8)
    window.addEventListener('keydown', (e) => {{
      const tabs = ['tab-all', 'tab-origin', 'tab-symbols', 'tab-lovefrom', 'tab-teenage', 'tab-pentagram', 'tab-collins', 'tab-workandco', 'tab-decision'];
      const buttons = document.querySelectorAll('.nav-btn');
      
      let currentIndex = -1;
      tabs.forEach((id, idx) => {{
        if (document.getElementById(id).classList.contains('active')) currentIndex = idx;
      }});

      if (e.key === 'ArrowRight' && currentIndex < tabs.length - 1) {{
        switchTab(tabs[currentIndex + 1], buttons[currentIndex + 1]);
      }} else if (e.key === 'ArrowLeft' && currentIndex > 0) {{
        switchTab(tabs[currentIndex - 1], buttons[currentIndex - 1]);
      }} else if (!isNaN(parseInt(e.key)) && parseInt(e.key) < tabs.length) {{
        const idx = parseInt(e.key);
        switchTab(tabs[idx], buttons[idx]);
      }}
    }});
  </script>
</body>
</html>"""

with open(os.path.join(web_dir, "brand_book.html"), "w", encoding="utf-8") as f:
    f.write(html_content)

with open(os.path.join(brain_dir, "brand_book.html"), "w", encoding="utf-8") as f:
    f.write(html_content)

print("Brand Book creado exitosamente en:")
print(os.path.join(web_dir, "brand_book.html"))
print(os.path.join(brain_dir, "brand_book.html"))
