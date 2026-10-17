import os

web_dir = "/home/slone/slocast 1.0/app/web_portal"
brain_dir = "/home/slone/.gemini/antigravity/brain/ca19abdc-9859-4476-ab55-60c6b1483221"

html = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SLÖNE · EL SÍMBOLO PURO · SÍNTESIS CORPORATIVA</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #000000;
      color: #FFFFFF;
      font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
      padding: 40px 24px;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .container {
      max-width: 1200px;
      width: 100%;
    }
    header {
      text-align: center;
      margin-bottom: 48px;
    }
    .badge {
      display: inline-block;
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.3);
      color: #FFFFFF;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 3px;
      padding: 6px 14px;
      border-radius: 4px;
      text-transform: uppercase;
      margin-bottom: 14px;
    }
    h1 {
      font-size: 40px;
      font-weight: 900;
      letter-spacing: 2px;
      margin-bottom: 8px;
    }
    p.subtitle {
      font-size: 15px;
      color: #8E9BAE;
      max-width: 650px;
      margin: 0 auto;
    }

    /* GRID DE LOS 3 SÍMBOLOS */
    .symbols-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 28px;
      margin-bottom: 48px;
    }
    @media (max-width: 900px) {
      .symbols-grid { grid-template-columns: 1fr; }
    }
    .symbol-card {
      background: #080A10;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 16px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      align-items: center;
      transition: all 0.25s ease;
      cursor: pointer;
    }
    .symbol-card:hover {
      border-color: #00F0FF;
      box-shadow: 0 0 30px rgba(0, 240, 255, 0.25);
      transform: translateY(-4px);
    }
    .symbol-card.selected {
      border: 2px solid #00F0FF;
      box-shadow: 0 0 40px rgba(0, 240, 255, 0.4);
    }
    .symbol-img-box {
      width: 100%;
      aspect-ratio: 1 / 1;
      background: #020306;
      border-radius: 12px;
      overflow: hidden;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .symbol-img-box img {
      width: 100%;
      height: 100%;
      object-fit: contain;
    }
    .symbol-num {
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 2px;
      color: #00F0FF;
      margin-bottom: 4px;
      text-transform: uppercase;
    }
    .symbol-title {
      font-size: 19px;
      font-weight: 800;
      margin-bottom: 8px;
      text-align: center;
    }
    .symbol-logic {
      font-size: 12px;
      color: #94A3B8;
      text-align: center;
      line-height: 1.6;
      margin-bottom: 16px;
    }
    .btn-select {
      margin-top: auto;
      background: #FFFFFF;
      color: #000000;
      border: none;
      font-size: 11px;
      font-weight: 900;
      letter-spacing: 1.5px;
      padding: 10px 20px;
      border-radius: 6px;
      text-transform: uppercase;
      cursor: pointer;
      width: 100%;
      transition: all 0.2s ease;
    }
    .btn-select:hover {
      background: #00F0FF;
      color: #000000;
    }

    /* BARRA DE ESCALA REAL */
    .scale-test {
      background: #06080F;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 14px;
      padding: 24px 32px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
    }
    .scale-info {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .scale-title {
      font-size: 14px;
      font-weight: 800;
      letter-spacing: 1px;
    }
    .scale-sub {
      font-size: 12px;
      color: #64748B;
    }
    .scale-preview-row {
      display: flex;
      align-items: center;
      gap: 24px;
    }
    .scale-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
    }
    .scale-item span {
      font-size: 9px;
      font-weight: 700;
      color: #64748B;
    }
    .scale-box-large { width: 64px; height: 64px; border-radius: 12px; overflow: hidden; background: #000; border: 1px solid #333; }
    .scale-box-med { width: 36px; height: 36px; border-radius: 8px; overflow: hidden; background: #000; border: 1px solid #333; }
    .scale-box-small { width: 20px; height: 20px; border-radius: 4px; overflow: hidden; background: #000; border: 1px solid #333; }
    .scale-box-large img, .scale-box-med img, .scale-box-small img { width: 100%; height: 100%; object-fit: contain; }

    /* TOAST DE SELECCIÓN */
    .toast {
      position: fixed;
      bottom: 24px;
      background: #00F0FF;
      color: #000;
      font-size: 13px;
      font-weight: 900;
      letter-spacing: 1px;
      padding: 14px 28px;
      border-radius: 8px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.8);
      display: none;
      z-index: 1000;
    }
  </style>
</head>
<body>
  <div class="container">
    
    <header>
      <div class="badge">SÍNTESIS PURA · SÍMBOLO SOBERANO</div>
      <h1>EL SÍMBOLO DEFINITIVO DE SLÖNE</h1>
      <p class="subtitle">
        Sin grafitis, sin paredes, sin adornos. Solo los 3 símbolos puros, reconocibles a 50 metros y con la física exacta de lo que vende la empresa.
      </p>
    </header>

    <div class="symbols-grid">

      <!-- OPCIÓN 1: LA 'S' DE ONDA ACÚSTICA -->
      <div class="symbol-card" onclick="selectSymbol('OPCIÓN 1: LA S DE ONDA ACÚSTICA (SOUNDWAVE)')" id="card-1">
        <div class="symbol-img-box">
          <img src="/assets/slone_pure_soundwave.jpg" alt="SLÖNE Soundwave S">
        </div>
        <div class="symbol-num">OPCIÓN 01</div>
        <div class="symbol-title">La 'S' de Onda Acústica</div>
        <p class="symbol-logic">
          <strong>La física de Spotify aplicada a la S:</strong> Dos arcos concéntricos de compresión de audio que se abrazan formando una 'S' perfecta, coronada por los dos nodos de emisión estéreo (la Ö).
        </p>
        <button class="btn-select">SELECCIONAR ÉSTE</button>
      </div>

      <!-- OPCIÓN 2: LA RUNA DE TRANSMISIÓN -->
      <div class="symbol-card" onclick="selectSymbol('OPCIÓN 2: LA RUNA DE TRANSMISIÓN (BLUETOOTH STREAM)')" id="card-2">
        <div class="symbol-img-box">
          <img src="/assets/slone_pure_rune.jpg" alt="SLÖNE Transmission Rune">
        </div>
        <div class="symbol-num">OPCIÓN 02</div>
        <div class="symbol-title">La Runa de Transmisión</div>
        <p class="symbol-logic">
          <strong>El Bluetooth de la retransmisión:</strong> Mástil vertical de emisión central con dos alas angulares que dibujan la 'S' y los satélites gemelos de sincronización. Nivel hardware.
        </p>
        <button class="btn-select">SELECCIONAR ÉSTE</button>
      </div>

      <!-- OPCIÓN 3: EL PULSO CONTINUO -->
      <div class="symbol-card" onclick="selectSymbol('OPCIÓN 3: EL PULSO CONTINUO (LIVING STREAM)')" id="card-3">
        <div class="symbol-img-box">
          <img src="/assets/slone_pure_pulse.jpg" alt="SLÖNE Living Pulse">
        </div>
        <div class="symbol-num">OPCIÓN 03</div>
        <div class="symbol-title">El Pulso Continuo</div>
        <p class="symbol-logic">
          <strong>Retransmisión ininterrumpida:</strong> Cinta fluida continua en bucle aerodinámico que traza la 'S' del latido deportivo y la frecuencia viva sin cortes, con la diéresis gemela.
        </p>
        <button class="btn-select">SELECCIONAR ÉSTE</button>
      </div>

    </div>

    <!-- TEST DE ESCALABILIDAD A 64PX, 36PX Y 20PX -->
    <div class="scale-test">
      <div class="scale-info">
        <div class="scale-title">TEST DE ESCALABILIDAD (SMART TV, APP & MANDO)</div>
        <div class="scale-sub">Un gran logo debe ser inconfundible a 64px en la pantalla del televisor y a 20px en un botón físico.</div>
      </div>
      <div class="scale-preview-row">
        <div class="scale-item">
          <div class="scale-box-large"><img src="/assets/slone_pure_soundwave.jpg" alt="64px"></div>
          <span>64px (Smart TV)</span>
        </div>
        <div class="scale-item">
          <div class="scale-box-med"><img src="/assets/slone_pure_soundwave.jpg" alt="36px"></div>
          <span>36px (Favicon)</span>
        </div>
        <div class="scale-item">
          <div class="scale-box-small"><img src="/assets/slone_pure_soundwave.jpg" alt="20px"></div>
          <span>20px (Botón Mando)</span>
        </div>
      </div>
    </div>

  </div>

  <div id="toast" class="toast">✦ SÍMBOLO SELECCIONADO</div>

  <script>
    function selectSymbol(name) {
      document.querySelectorAll('.symbol-card').forEach(c => c.classList.remove('selected'));
      event.currentTarget.classList.add('selected');
      const toast = document.getElementById('toast');
      toast.innerText = '✦ ' + name + ' SELECCIONADO COMO SÍMBOLO OFICIAL';
      toast.style.display = 'block';
      setTimeout(() => { toast.style.display = 'none'; }, 3000);
    }
  </script>
</body>
</html>
"""

with open(os.path.join(web_dir, "simbolo_puro_slone.html"), "w", encoding="utf-8") as f:
    f.write(html)

with open(os.path.join(brain_dir, "simbolo_puro_slone.html"), "w", encoding="utf-8") as f:
    f.write(html)

print("Página de símbolo puro creada exitosamente.")
