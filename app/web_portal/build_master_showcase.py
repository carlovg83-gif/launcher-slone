import os

web_dir = "/home/slone/slocast 1.0/app/web_portal"
brain_dir = "/home/slone/.gemini/antigravity/brain/ca19abdc-9859-4476-ab55-60c6b1483221"

html = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SLÖNE · MASTER BRAND SHOWCASE · DIRECCIÓN DELEGADA</title>
  <style>
    :root {
      --bg: #05070D;
      --card-bg: #090D18;
      --border: rgba(255, 255, 255, 0.1);
      --cyan: #00F0FF;
      --cyan-glow: rgba(0, 240, 255, 0.4);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: #FFFFFF;
      font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', 'Segoe UI', Roboto, sans-serif;
      padding: 32px 24px;
      line-height: 1.5;
    }
    .container {
      max-width: 1300px;
      margin: 0 auto;
    }
    .hero-header {
      text-align: center;
      margin-bottom: 48px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 32px;
      position: relative;
    }
    .badge-lead {
      display: inline-block;
      background: rgba(0, 240, 255, 0.15);
      border: 1px solid var(--cyan);
      color: var(--cyan);
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 3px;
      padding: 5px 14px;
      border-radius: 6px;
      text-transform: uppercase;
      margin-bottom: 14px;
    }
    .hero-title {
      font-size: 44px;
      font-weight: 900;
      letter-spacing: 3px;
      margin-bottom: 10px;
    }
    .hero-subtitle {
      font-size: 16px;
      color: #94A3B8;
      max-width: 780px;
      margin: 0 auto;
    }
    .showcase-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 32px;
    }
    @media (max-width: 900px) {
      .showcase-grid { grid-template-columns: 1fr; }
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 20px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 20px 50px rgba(0,0,0,0.8);
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .card:hover {
      border-color: var(--cyan);
      box-shadow: 0 20px 60px var(--cyan-glow);
      transform: translateY(-4px);
    }
    .card-img-wrap {
      width: 100%;
      height: 380px;
      background: #000;
      overflow: hidden;
      position: relative;
    }
    .card-img-wrap img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.4s ease;
    }
    .card:hover .card-img-wrap img {
      transform: scale(1.03);
    }
    .card-body {
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .card-tag {
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 2px;
      color: var(--cyan);
      text-transform: uppercase;
    }
    .card-title {
      font-size: 22px;
      font-weight: 800;
      letter-spacing: 0.5px;
    }
    .card-desc {
      font-size: 13px;
      color: #94A3B8;
      line-height: 1.6;
    }
    .tech-specs {
      display: flex;
      gap: 12px;
      margin-top: 12px;
      padding-top: 14px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      font-size: 11px;
      color: #CBD5E1;
      font-weight: 700;
    }
  </style>
</head>
<body>
  <div class="container">
    
    <header class="hero-header">
      <div class="badge-lead">DIRECCIÓN DE ARTE DELEGADA · PRODUCCIÓN SENIOR</div>
      <h1 class="hero-title">SLÖNE: EL SISTEMA VISUAL SOBERANO</h1>
      <p class="hero-subtitle">
        Sin código vectorial plano ni garabatos infantiles. Fotografía industrial, renderizado de producto físico, vallas perimetrales en estadio de Champions League y tipografía urbana en cromo líquido.
      </p>
    </header>

    <div class="showcase-grid">

      <!-- 1. EMBLEMA MAESTRO DE TITANIO -->
      <div class="card">
        <div class="card-img-wrap">
          <img src="/assets/slone_luxury_emblem.jpg" alt="Emblema Maestro de Titanio SLÖNE">
        </div>
        <div class="card-body">
          <div class="card-tag">01 · IDENTIDAD MAESTRA / HARDWARE</div>
          <h2 class="card-title">Medallón de Titanio & Cristal de Obsidiana</h2>
          <p class="card-desc">
            La 'S' esculpida como cinta de onda acústica tridimensional con biseles de corte de diamante. Dos nodos concéntricos tallados (la diéresis de la Ö) con retroiluminación cian viva sobre pizarra arquitectónica oscura.
          </p>
          <div class="tech-specs">
            <span>✦ Titanio aeroespacial</span>
            <span>✦ Cristal de zafiro</span>
            <span>✦ Halo cian #00F0FF</span>
          </div>
        </div>
      </div>

      <!-- 2. GRAFFITI EN CROMO LÍQUIDO -->
      <div class="card">
        <div class="card-img-wrap">
          <img src="/assets/slone_graffiti_chrome.jpg" alt="SLÖNE Graffiti en Cromo Líquido">
        </div>
        <div class="card-body">
          <div class="card-tag">02 · ADN DEL FUNDADOR / STREETWEAR</div>
          <h2 class="card-title">Firma 'SLÖNE' en Cromo Líquido & Mercurio</h2>
          <p class="card-desc">
            Traducción artística de tu tag original a nivel galería internacional: letras en mercurio líquido con biseles afilados, comillas de spray (" "), flecha inferior aerodinámica y destellos gemelos de aerosol cian sobre ladrillo industrial.
          </p>
          <div class="tech-specs">
            <span>✦ Cromo pulido</span>
            <span>✦ Destellos de aerosol</span>
            <span>✦ Textura urbana berlinesa</span>
          </div>
        </div>
      </div>

      <!-- 3. HARDWARE DE SALÓN Y SMART TV -->
      <div class="card">
        <div class="card-img-wrap">
          <img src="/assets/slone_hardware_mockup.jpg" alt="SLÖNE Hardware Mockup y Smart TV">
        </div>
        <div class="card-body">
          <div class="card-tag">03 · ECOSISTEMA FÍSICO / SMART TV</div>
          <h2 class="card-title">SLÖNE Box, Mando Ergonómico & Televisor OLED</h2>
          <p class="card-desc">
            El receptor de streaming en aluminio anodizado negro obsidiana con la runa iluminada en la esquina. El mando a distancia metálico de precisión y, de fondo, el televisor OLED de 85 pulgadas con el partido en 4K en directo y telemetría de sincronización a 0 ms.
          </p>
          <div class="tech-specs">
            <span>✦ Aluminio anodizado</span>
            <span>✦ Mando ergonómico</span>
            <span>✦ Pantalla OLED 85" 4K</span>
          </div>
        </div>
      </div>

      <!-- 4. RETRANSMISIÓN EN ESTADIO 360° -->
      <div class="card">
        <div class="card-img-wrap">
          <img src="/assets/slone_stadium_broadcast.jpg" alt="SLÖNE en Estadio de Fútbol Champions League">
        </div>
        <div class="card-body">
          <div class="card-tag">04 · BROADCAST EN VIVO / ESTADIO</div>
          <h2 class="card-title">Vallas LED de 360° en Estadio de Champions League</h2>
          <p class="card-desc">
            80.000 aficionados bajo la niebla y focos nocturnos. Las vallas perimetrales a ras de césped proyectan la onda cinética SLÖNE en cian eléctrico y ultravioleta, reaccionando en tiempo real al estruendo de la grada y reflejándose en el césped mojado.
          </p>
          <div class="tech-specs">
            <span>✦ Valla LED 360°</span>
            <span>✦ Frecuencia sonora reactiva</span>
            <span>✦ Cobertura deportiva global</span>
          </div>
        </div>
      </div>

    </div>

  </div>
</body>
</html>
"""

with open(os.path.join(web_dir, "master_showcase.html"), "w", encoding="utf-8") as f:
    f.write(html)

with open(os.path.join(brain_dir, "master_showcase.html"), "w", encoding="utf-8") as f:
    f.write(html)

print("Master showcase creado exitosamente.")
