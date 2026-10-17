# -*- coding: utf-8 -*-
"""
Script generador del portal de ingeniería y hardware soberano: SLÖNE CÖRE 1
Genera hardware.html elevando el estándar a nivel Apple Pro / Devialet / Tesla Industrial.
Incluye:
- Hero fotográfico de estudio con lupa de aumento y hotspots interactivos
- Selector de acabados: Space Black, Titanio Mecanizado, Oro Champán
- Despiece explotado de 4 capas con diagramas técnicos SVG y especificaciones de componentes reales
- Showcase macro del emblema y artesanía CNC (slone_luxury_emblem.jpg)
- Panel posterior CAD milimétrico con todos los conectores e interfaces
- Certificaciones de laboratorio: Cámara Anecoica (0.0 dBA), FLIR Térmica (47.8°C), Wireshark Zero-Trust
- Comparativa implacable con Apple TV 4K, Nvidia Shield y Android TV genérico
"""

HTML_CONTENT = r'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SLÖNE CÖRE 1 · Dossier de Ingeniería & Hardware Soberano</title>
  <link rel="icon" href="assets/slone_o_gold.png" type="image/png">
  <style>
    :root {
      --bg: #030508;
      --bg-card: #080C14;
      --bg-card-hover: #0D1322;
      --border: rgba(255, 255, 255, 0.08);
      --border-accent: rgba(255, 215, 0, 0.25);
      --border-cyan: rgba(0, 240, 255, 0.3);
      --gold: #FFD700;
      --gold-light: #FFF2A3;
      --gold-dark: #B8860B;
      --gold-gradient: linear-gradient(135deg, #FFF3B0 0%, #FFD700 50%, #B8860B 100%);
      --cyan: #00F0FF;
      --cyan-glow: rgba(0, 240, 255, 0.35);
      --text: #F8FAFC;
      --text-muted: #94A3B8;
      --text-dim: #64748B;
      --radius: 16px;
      --shadow-lg: 0 25px 60px rgba(0,0,0,0.85);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", "Segoe UI", Roboto, sans-serif; }
    html { scroll-behavior: smooth; }
    body {
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      overflow-x: hidden;
      background-image: 
        radial-gradient(circle at 50% 0%, rgba(0, 240, 255, 0.04) 0%, transparent 60%),
        radial-gradient(circle at 80% 30%, rgba(255, 215, 0, 0.03) 0%, transparent 50%);
    }

    /* ── BARRA SUPERIOR HUD ESTILIZADA Y RESPONSIVA ── */
    header {
      position: sticky;
      top: 0;
      z-index: 1000;
      background: rgba(3, 5, 8, 0.94);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border-bottom: 1px solid var(--border);
      padding: 0.6rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      height: 64px;
      box-sizing: border-box;
    }

    .brand-group {
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      flex-shrink: 0;
    }

    .brand-logo-img {
      height: 34px;
      width: 34px;
      filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.4));
    }

    .brand-titles h1 {
      font-size: 1.1rem;
      font-weight: 900;
      letter-spacing: 1.5px;
      color: #FFF;
      display: flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }

    .brand-titles h1 span {
      background: var(--gold-gradient);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .brand-titles p {
      font-size: 0.65rem;
      color: var(--text-dim);
      letter-spacing: 1px;
      text-transform: uppercase;
      font-weight: 700;
      white-space: nowrap;
    }

    nav.hud-nav {
      display: flex;
      gap: 20px;
      align-items: center;
      flex-shrink: 0;
    }

    nav.hud-nav a {
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.8rem;
      font-weight: 700;
      letter-spacing: 0.5px;
      transition: color 0.2s;
      white-space: nowrap;
    }

    nav.hud-nav a:hover {
      color: var(--gold);
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-shrink: 0;
    }

    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      background: rgba(0, 240, 255, 0.08);
      border: 1px solid var(--border-cyan);
      color: var(--cyan);
      font-size: 0.7rem;
      font-weight: 800;
      padding: 5px 12px;
      border-radius: 20px;
      letter-spacing: 0.8px;
      text-transform: uppercase;
      white-space: nowrap;
    }

    .status-badge .dot {
      width: 6px;
      height: 6px;
      background: var(--cyan);
      border-radius: 50%;
      box-shadow: 0 0 8px var(--cyan);
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.85); }
    }

    .btn-back-portal {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border);
      color: #FFF;
      text-decoration: none;
      font-size: 0.75rem;
      font-weight: 800;
      padding: 6px 14px;
      border-radius: 20px;
      letter-spacing: 0.6px;
      transition: all 0.2s;
      white-space: nowrap;
    }

    .btn-back-portal:hover {
      background: var(--gold);
      color: #000;
      border-color: var(--gold);
      box-shadow: 0 0 15px rgba(255, 215, 0, 0.4);
    }

    @media (max-width: 1060px) {
      nav.hud-nav { display: none; }
      .brand-titles p { display: none; }
    }

    @media (max-width: 640px) {
      header { padding: 0.5rem 1rem; }
      .status-badge { display: none; }
    }

    /* ── SECCIONES Y CONTENEDOR ── */
    .container {
      max-width: 1320px;
      margin: 0 auto;
      padding: 2.5rem 1.8rem;
    }

    .section-header {
      text-align: center;
      margin-bottom: 3.2rem;
      position: relative;
    }

    .pre-tag {
      display: inline-block;
      font-size: 0.72rem;
      font-weight: 900;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--cyan);
      margin-bottom: 0.6rem;
    }

    .section-title {
      font-size: 2.4rem;
      font-weight: 900;
      letter-spacing: 1.5px;
      color: #FFF;
      margin-bottom: 0.8rem;
    }

    .section-title span {
      background: var(--gold-gradient);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .section-desc {
      font-size: 1.02rem;
      color: var(--text-muted);
      max-width: 780px;
      margin: 0 auto;
      line-height: 1.65;
    }

    /* ── HERO SHOWCASE INDUSTRIAL ── */
    .hero-hardware-wrapper {
      position: relative;
      background: #000;
      border: 1px solid var(--border);
      border-radius: 24px;
      overflow: hidden;
      box-shadow: var(--shadow-lg), 0 0 120px rgba(0, 240, 255, 0.08);
      margin-bottom: 4rem;
    }

    .hero-stage {
      position: relative;
      width: 100%;
      height: clamp(440px, 64vh, 680px);
      display: flex;
      align-items: center;
      justify-content: center;
      background: #030508;
      overflow: hidden;
    }

    .hero-img-main {
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: center;
      transition: filter 0.5s ease;
      cursor: crosshair;
    }

    .hero-stage.finish-titanium .hero-img-main {
      filter: saturate(0.55) brightness(1.15) contrast(1.12);
    }

    .hero-stage.finish-gold .hero-img-main {
      filter: sepia(0.35) hue-rotate(-20deg) saturate(1.35) brightness(1.05);
    }

    /* LUPA / MAGNIFIER LOUPE */
    .loupe-glass {
      position: absolute;
      width: 200px;
      height: 200px;
      border: 2px solid var(--cyan);
      border-radius: 50%;
      pointer-events: none;
      display: none;
      box-shadow: 0 0 35px rgba(0, 240, 255, 0.6), inset 0 0 25px rgba(0,0,0,0.85);
      background-repeat: no-repeat;
      z-index: 50;
    }

    .loupe-crosshair {
      position: absolute;
      top: 50%;
      left: 50%;
      width: 14px;
      height: 14px;
      transform: translate(-50%, -50%);
      pointer-events: none;
    }
    .loupe-crosshair::before, .loupe-crosshair::after {
      content: '';
      position: absolute;
      background: var(--cyan);
    }
    .loupe-crosshair::before { top: 6px; left: 0; width: 14px; height: 1.5px; }
    .loupe-crosshair::after { top: 0; left: 6px; width: 1.5px; height: 14px; }

    /* PUNTOS CALIENTES / HOTSPOTS INTERACTIVOS */
    .hotspot-pin {
      position: absolute;
      z-index: 40;
      transform: translate(-50%, -50%);
      cursor: pointer;
    }

    .hotspot-dot {
      width: 26px;
      height: 26px;
      background: rgba(0, 240, 255, 0.2);
      border: 1.5px solid var(--cyan);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 16px var(--cyan);
      animation: hotspotPulse 2.5s infinite;
      transition: all 0.25s ease;
    }

    .hotspot-dot::after {
      content: '';
      width: 8px;
      height: 8px;
      background: #FFF;
      border-radius: 50%;
    }

    .hotspot-pin:hover .hotspot-dot {
      transform: scale(1.25);
      background: var(--cyan);
    }
    .hotspot-pin:hover .hotspot-dot::after {
      background: #000;
    }

    @keyframes hotspotPulse {
      0% { box-shadow: 0 0 0 0 rgba(0, 240, 255, 0.7); }
      70% { box-shadow: 0 0 0 18px rgba(0, 240, 255, 0); }
      100% { box-shadow: 0 0 0 0 rgba(0, 240, 255, 0); }
    }

    .hotspot-tooltip {
      position: absolute;
      bottom: 34px;
      left: 50%;
      transform: translateX(-50%) translateY(8px);
      width: 290px;
      background: rgba(8, 12, 20, 0.95);
      border: 1px solid var(--border-cyan);
      backdrop-filter: blur(20px);
      border-radius: 12px;
      padding: 14px 16px;
      opacity: 0;
      pointer-events: none;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: 0 15px 35px rgba(0,0,0,0.9);
      z-index: 60;
    }

    .hotspot-tooltip::after {
      content: '';
      position: absolute;
      top: 100%;
      left: 50%;
      transform: translateX(-50%);
      border-width: 6px;
      border-style: solid;
      border-color: rgba(8, 12, 20, 0.95) transparent transparent transparent;
    }

    .hotspot-pin:hover .hotspot-tooltip {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
      pointer-events: auto;
    }

    .hotspot-tooltip h4 {
      color: var(--cyan);
      font-size: 0.84rem;
      font-weight: 800;
      margin-bottom: 4px;
      letter-spacing: 0.5px;
    }

    .hotspot-tooltip p {
      color: var(--text-muted);
      font-size: 0.77rem;
      line-height: 1.45;
    }

    /* BARRA DE CONTROL DEL SHOWCASE */
    .hero-controls-bar {
      background: rgba(10, 15, 24, 0.95);
      border-top: 1px solid var(--border);
      padding: 1.2rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }

    .finish-selector-group {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .finish-label {
      font-size: 0.75rem;
      font-weight: 800;
      color: var(--text-dim);
      letter-spacing: 1.5px;
      text-transform: uppercase;
    }

    .finish-btn {
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border);
      color: var(--text-muted);
      font-size: 0.76rem;
      font-weight: 700;
      padding: 7px 15px;
      border-radius: 20px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
    }

    .finish-btn .swatch {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      border: 1px solid rgba(255,255,255,0.2);
    }
    .swatch-black { background: #181B20; }
    .swatch-titanium { background: #8E959E; }
    .swatch-gold { background: #D4AF37; }

    .finish-btn:hover {
      color: #FFF;
      border-color: rgba(255,255,255,0.3);
    }

    .finish-btn.active {
      background: rgba(255, 215, 0, 0.12);
      border-color: var(--gold);
      color: #FFF;
      box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
    }

    .hero-features-chips {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    .chip-spec {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.08);
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 0.74rem;
      color: var(--text-muted);
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .chip-spec strong {
      color: #FFF;
      font-family: monospace;
      font-weight: 700;
    }

    /* ── PILARES DE INGENIERÍA ── */
    .grid-3 {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 24px;
      margin-bottom: 4rem;
    }

    @media (max-width: 960px) {
      .grid-3 { grid-template-columns: 1fr; }
    }

    .card-pillar {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 2rem;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
      overflow: hidden;
    }

    .card-pillar::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, transparent, var(--gold), transparent);
      opacity: 0;
      transition: opacity 0.3s;
    }

    .card-pillar:hover {
      background: var(--bg-card-hover);
      border-color: var(--border-accent);
      transform: translateY(-5px);
      box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }

    .card-pillar:hover::before {
      opacity: 1;
    }

    .pillar-icon {
      font-size: 2.2rem;
      margin-bottom: 1.2rem;
      display: inline-block;
    }

    .pillar-title {
      font-size: 1.25rem;
      font-weight: 800;
      color: #FFF;
      margin-bottom: 0.8rem;
    }

    .pillar-text {
      font-size: 0.88rem;
      color: var(--text-muted);
      line-height: 1.65;
      margin-bottom: 1.4rem;
    }

    .pillar-metrics {
      border-top: 1px solid rgba(255,255,255,0.06);
      padding-top: 1rem;
      display: flex;
      justify-content: space-between;
    }

    .metric-item {
      display: flex;
      flex-direction: column;
    }

    .metric-val {
      font-size: 1.15rem;
      font-weight: 900;
      color: var(--cyan);
      font-family: monospace;
    }

    .metric-label {
      font-size: 0.68rem;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 0.8px;
    }

    /* ── SECCIÓN DE ARTESANÍA CNC & EMBLEMA MACRO ── */
    .emblem-craft-section {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 3rem;
      margin-bottom: 4rem;
      box-shadow: var(--shadow-lg);
      display: grid;
      grid-template-columns: 1fr 1.2fr;
      gap: 40px;
      align-items: center;
    }

    @media (max-width: 900px) {
      .emblem-craft-section { grid-template-columns: 1fr; }
    }

    .emblem-macro-wrapper {
      position: relative;
      border-radius: 20px;
      overflow: hidden;
      border: 1px solid rgba(255, 215, 0, 0.3);
      box-shadow: 0 20px 50px rgba(0,0,0,0.9), 0 0 40px rgba(0, 240, 255, 0.2);
    }

    .emblem-macro-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: transform 0.5s ease;
    }

    .emblem-macro-wrapper:hover .emblem-macro-img {
      transform: scale(1.04);
    }

    .emblem-info-box h3 {
      font-size: 1.8rem;
      font-weight: 900;
      color: #FFF;
      margin-bottom: 0.6rem;
    }

    .emblem-info-box h3 span {
      background: var(--gold-gradient);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .emblem-info-box p {
      font-size: 0.92rem;
      color: var(--text-muted);
      line-height: 1.7;
      margin-bottom: 1.5rem;
    }

    /* ── DESPIECE EXPLOTADO EN CAPAS ── */
    .exploded-view-card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 3rem;
      margin-bottom: 5rem;
      box-shadow: var(--shadow-lg);
    }

    .exploded-nav-tabs {
      display: flex;
      gap: 12px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 1.5rem;
      margin-bottom: 2.5rem;
      overflow-x: auto;
    }

    .tab-layer-btn {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 12px 22px;
      border-radius: 12px;
      font-size: 0.82rem;
      font-weight: 800;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 10px;
      transition: all 0.2s;
      white-space: nowrap;
    }

    .tab-layer-btn .badge-layer-num {
      background: rgba(255,255,255,0.1);
      width: 22px;
      height: 22px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.7rem;
      font-weight: 900;
      color: #FFF;
    }

    .tab-layer-btn:hover {
      color: #FFF;
      border-color: rgba(255,255,255,0.25);
    }

    .tab-layer-btn.active {
      background: rgba(0, 240, 255, 0.1);
      border-color: var(--cyan);
      color: #FFF;
      box-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
    }

    .tab-layer-btn.active .badge-layer-num {
      background: var(--cyan);
      color: #000;
    }

    .layer-content-panel {
      display: none;
      grid-template-columns: 1.1fr 1fr;
      gap: 40px;
      align-items: center;
      animation: fadeIn 0.4s ease;
    }

    .layer-content-panel.active {
      display: grid;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 900px) {
      .layer-content-panel { grid-template-columns: 1fr; }
    }

    .layer-visual-box {
      background: #020305;
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 18px;
      padding: 2.5rem;
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 380px;
      box-shadow: inset 0 0 50px rgba(0,0,0,0.8);
    }

    .layer-svg-diagram {
      width: 100%;
      max-width: 380px;
      height: auto;
      filter: drop-shadow(0 10px 25px rgba(0, 240, 255, 0.2));
    }

    .layer-details-box h3 {
      font-size: 1.6rem;
      font-weight: 900;
      color: #FFF;
      margin-bottom: 0.6rem;
    }

    .layer-subtitle {
      font-size: 0.8rem;
      font-weight: 800;
      color: var(--gold);
      letter-spacing: 1.5px;
      text-transform: uppercase;
      margin-bottom: 1.2rem;
    }

    .layer-details-box p {
      font-size: 0.92rem;
      color: var(--text-muted);
      line-height: 1.7;
      margin-bottom: 1.5rem;
    }

    .specs-bullet-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-bottom: 1.8rem;
    }

    .specs-bullet-list li {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      font-size: 0.85rem;
      color: #E2E8F0;
    }

    .specs-bullet-list li::before {
      content: '✦';
      color: var(--cyan);
      font-size: 0.8rem;
      margin-top: 2px;
    }

    .specs-bullet-list li strong {
      color: #FFF;
      font-weight: 700;
    }

    .certification-pill-group {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    .cert-pill {
      background: rgba(255, 215, 0, 0.08);
      border: 1px solid var(--border-accent);
      color: var(--gold);
      font-size: 0.72rem;
      font-weight: 800;
      padding: 4px 10px;
      border-radius: 6px;
      letter-spacing: 0.8px;
    }

    /* ── CAD PANEL TRASERO Y E/S ── */
    .cad-rear-section {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 3rem;
      margin-bottom: 5rem;
      box-shadow: var(--shadow-lg);
    }

    .cad-blueprint-box {
      background: #020408;
      border: 1px dashed rgba(0, 240, 255, 0.25);
      border-radius: 16px;
      padding: 3rem 2rem;
      position: relative;
      margin-bottom: 2.5rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      background-image: 
        linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px);
      background-size: 20px 20px;
    }

    .cad-dimension-indicator {
      position: absolute;
      top: 14px;
      right: 20px;
      font-family: monospace;
      font-size: 0.75rem;
      color: var(--cyan);
      letter-spacing: 1px;
    }

    .cad-chassis-plate {
      width: 100%;
      max-width: 900px;
      background: linear-gradient(180deg, #1C2028 0%, #0F1218 100%);
      border: 2px solid #333C4E;
      border-radius: 8px;
      padding: 24px 30px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 20px 50px rgba(0,0,0,0.9), inset 0 1px 0 rgba(255,255,255,0.15);
      position: relative;
      flex-wrap: wrap;
      gap: 16px;
    }

    .cad-port-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      position: relative;
      transition: transform 0.2s;
    }

    .cad-port-item:hover {
      transform: translateY(-4px);
    }

    .port-socket {
      background: #07090D;
      border: 2px solid #475569;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: inset 0 3px 8px rgba(0,0,0,0.9);
      transition: all 0.2s;
    }

    .cad-port-item:hover .port-socket {
      border-color: var(--cyan);
      box-shadow: 0 0 15px var(--cyan-glow), inset 0 2px 6px rgba(0,0,0,0.8);
    }

    .port-socket.hdmi { width: 90px; height: 38px; border-radius: 3px 3px 8px 8px; }
    .port-socket.spdif { width: 44px; height: 44px; position: relative; }
    .port-socket.spdif::after {
      content: '';
      width: 12px;
      height: 12px;
      background: #FF0033;
      border-radius: 50%;
      box-shadow: 0 0 10px #FF0033;
    }
    .port-socket.rj45 { width: 68px; height: 50px; }
    .port-socket.usba { width: 56px; height: 28px; background: #000; border-color: #00F0FF; }
    .port-socket.usbc { width: 42px; height: 18px; border-radius: 8px; }
    .port-socket.recovery { width: 20px; height: 20px; border-radius: 50%; border: 1px dashed #EF4444; }

    .port-title {
      font-size: 0.72rem;
      font-weight: 800;
      color: #FFF;
      text-align: center;
      letter-spacing: 0.5px;
    }

    .port-pin-spec {
      font-size: 0.64rem;
      color: var(--cyan);
      font-family: monospace;
    }

    .cad-ports-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
    }

    @media (max-width: 900px) {
      .cad-ports-grid { grid-template-columns: 1fr; }
    }

    .card-port-spec {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 14px;
      padding: 1.4rem;
      transition: all 0.2s;
    }

    .card-port-spec:hover {
      border-color: var(--border-cyan);
      background: rgba(0, 240, 255, 0.02);
    }

    .port-spec-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.6rem;
    }

    .port-spec-header h4 {
      font-size: 0.95rem;
      font-weight: 800;
      color: #FFF;
    }

    .badge-bus {
      font-size: 0.65rem;
      font-family: monospace;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      background: rgba(0, 240, 255, 0.1);
      color: var(--cyan);
    }

    .card-port-spec p {
      font-size: 0.78rem;
      color: var(--text-muted);
      line-height: 1.5;
    }

    /* ── PRUEBAS DE LABORATORIO Y TELEMETRÍA FLIR (ANTI-ESTAFA) ── */
    .lab-tests-section {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 3.5rem;
      margin-bottom: 5rem;
      box-shadow: var(--shadow-lg);
    }

    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 32px;
    }

    @media (max-width: 900px) {
      .grid-2 { grid-template-columns: 1fr; }
    }

    .bench-card {
      background: #020408;
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 18px;
      padding: 2rem;
    }

    .bench-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
    }

    .bench-card-header h3 {
      font-size: 1.15rem;
      font-weight: 800;
      color: #FFF;
    }

    .telemetry-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 0;
      border-bottom: 1px solid rgba(255,255,255,0.05);
      font-size: 0.84rem;
    }

    .telemetry-row span {
      color: var(--text-muted);
    }

    .telemetry-row strong {
      color: #FFF;
      font-family: monospace;
    }

    .telemetry-row strong.accent-cyan {
      color: var(--cyan);
    }

    .telemetry-row strong.accent-gold {
      color: var(--gold);
    }

    .thermal-graph-box {
      margin-top: 1.5rem;
      background: #080D18;
      border: 1px solid rgba(0, 240, 255, 0.2);
      border-radius: 12px;
      padding: 1rem;
    }

    .thermal-bar-wrap {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 10px;
    }

    .thermal-label {
      width: 140px;
      font-size: 0.74rem;
      color: var(--text-muted);
    }

    .thermal-track {
      flex: 1;
      height: 10px;
      background: rgba(255,255,255,0.05);
      border-radius: 5px;
      overflow: hidden;
    }

    .thermal-fill {
      height: 100%;
      border-radius: 5px;
      transition: width 1s ease;
    }

    .fill-slone {
      width: 48%;
      background: linear-gradient(90deg, #00F0FF, #00B4D8);
    }

    .fill-generic {
      width: 88%;
      background: linear-gradient(90deg, #F59E0B, #EF4444);
    }

    .thermal-val {
      font-family: monospace;
      font-size: 0.76rem;
      font-weight: 700;
      color: #FFF;
      width: 50px;
      text-align: right;
    }

    /* ── COMPARATIVA IMPLACABLE ── */
    .table-compare-wrapper {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 2.5rem;
      margin-bottom: 5rem;
      overflow-x: auto;
      box-shadow: var(--shadow-lg);
    }

    table.compare-table {
      width: 100%;
      border-collapse: collapse;
      min-width: 800px;
    }

    table.compare-table th, table.compare-table td {
      padding: 16px 20px;
      text-align: left;
      border-bottom: 1px solid rgba(255,255,255,0.06);
      font-size: 0.86rem;
    }

    table.compare-table th {
      font-size: 0.8rem;
      font-weight: 800;
      letter-spacing: 1px;
      text-transform: uppercase;
      color: var(--text-dim);
    }

    table.compare-table th.col-slone {
      color: var(--gold);
      background: rgba(255, 215, 0, 0.05);
      border-radius: 12px 12px 0 0;
      border: 1px solid var(--border-accent);
      border-bottom: none;
    }

    table.compare-table td.col-slone {
      background: rgba(255, 215, 0, 0.03);
      border-left: 1px solid var(--border-accent);
      border-right: 1px solid var(--border-accent);
      font-weight: 700;
      color: #FFF;
    }

    table.compare-table tr:last-child td.col-slone {
      border-bottom: 1px solid var(--border-accent);
      border-radius: 0 0 12px 12px;
    }

    .badge-check {
      color: #00FF88;
      font-weight: 800;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .badge-cross {
      color: #EF4444;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    /* ── FOOTER & CALL TO ACTION ── */
    footer {
      border-top: 1px solid var(--border);
      background: #020305;
      padding: 4rem 2rem 2rem 2rem;
      text-align: center;
    }

    .footer-content {
      max-width: 800px;
      margin: 0 auto;
    }

    .footer-logo {
      height: 44px;
      margin-bottom: 1.5rem;
    }

    .footer-text {
      font-size: 0.84rem;
      color: var(--text-dim);
      line-height: 1.7;
      margin-bottom: 2rem;
    }

    .footer-links {
      display: flex;
      justify-content: center;
      gap: 24px;
      margin-bottom: 2rem;
      flex-wrap: wrap;
    }

    .footer-links a {
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.8rem;
      font-weight: 700;
      transition: color 0.2s;
    }

    .footer-links a:hover {
      color: var(--gold);
    }

    .footer-copy {
      font-size: 0.72rem;
      color: var(--text-dim);
      border-top: 1px solid rgba(255,255,255,0.05);
      padding-top: 2rem;
    }
  </style>
</head>
<body>

  <!-- ── BARRA SUPERIOR HUD RESPONSIVA ── -->
  <header>
    <a href="index.html" class="brand-group">
      <img src="assets/slone_isotipo_soberano.svg" alt="SLÖNE" class="brand-logo-img">
      <div class="brand-titles">
        <h1>SLÖNE <span>CÖRE 1</span></h1>
        <p>Micro-Appliance Soberano · Aluminio CNC 6061-T6</p>
      </div>
    </a>

    <nav class="hud-nav">
      <a href="#showcase">Estudio 4K</a>
      <a href="#artesania">Emblema CNC</a>
      <a href="#despiece">Despiece Interno</a>
      <a href="#puertos">Panel CAD</a>
      <a href="#laboratorio">Telemetría 0dB</a>
      <a href="#comparativa">Comparativa</a>
    </nav>

    <div class="header-actions">
      <div class="status-badge">
        <span class="dot"></span>
        <span>0 dB · Pasivo Puro</span>
      </div>
      <a href="index.html" class="btn-back-portal">← Volver al Portal</a>
    </div>
  </header>

  <div class="container">

    <!-- ── SECCIÓN 1: HERO SHOWCASE INDUSTRIAL ── -->
    <section class="section-header" id="showcase">
      <span class="pre-tag">Diseño Industrial de Precisión · Grado Audiófilo</span>
      <h2 class="section-title">Pura Masa de <span>Aluminio Macizo</span></h2>
      <p class="section-desc">
        Forjado a partir de un bloque macizo de aleación aeroespacial 6061-T6 de 2.4 kg desbastado en fresadora CNC de 5 ejes hasta los 920 g. 
        Refrigeración pasiva por cámara de vapor de cobre sin ventiladores, cero vibraciones y acústica certificada en 0.0 dBA.
      </p>
    </section>

    <div class="hero-hardware-wrapper">
      <div class="hero-stage" id="hero-stage">
        <img src="assets/slone_hardware_mockup.jpg" alt="SLÖNE CÖRE 1 Hardware" class="hero-img-main" id="hero-main-img">
        
        <!-- Lente de Aumento / Loupe -->
        <div class="loupe-glass" id="loupe-glass">
          <div class="loupe-crosshair"></div>
        </div>

        <!-- Hotspots Interactivos -->
        <div class="hotspot-pin" style="top: 68%; left: 42%;">
          <div class="hotspot-dot"></div>
          <div class="hotspot-tooltip">
            <h4>Chasis Monolítico CNC 6061-T6</h4>
            <p>Mecanizado de alta precisión con tolerancia de 0.02 mm. Anodizado duro tipo III de 25 micras y micro-granallado de vidrio cerámico anti-huellas.</p>
          </div>
        </div>

        <div class="hotspot-pin" style="top: 72%; left: 49.5%;">
          <div class="hotspot-dot"></div>
          <div class="hotspot-tooltip">
            <h4>Anillo Cuántico & Cristal Acústico</h4>
            <p>Lente de cristal mineral ahumado con micro-LED RGB de estado. Bloqueo de latencia en 0.000s y retroalimentación háptica en sala.</p>
          </div>
        </div>

        <div class="hotspot-pin" style="top: 65%; left: 66%;">
          <div class="hotspot-dot"></div>
          <div class="hotspot-tooltip">
            <h4>Mando Mecanizado SLÖ Remote</h4>
            <p>Unibody de aluminio con rueda jog-dial magnética para calibración manual de Lip-Sync de audio milisegundo a milisegundo (±1 ms por clic táctil).</p>
          </div>
        </div>

        <div class="hotspot-pin" style="top: 32%; left: 50%;">
          <div class="hotspot-dot"></div>
          <div class="hotspot-tooltip">
            <h4>Decodificación 4K a 60 FPS Directa</h4>
            <p>Emisión ultra-fluida hacia Smart TV mediante HDMI 2.1 eARC y transporte por red local de ultra-baja latencia sin servidores intermediarios.</p>
          </div>
        </div>
      </div>

      <!-- Barra de Control Inferior -->
      <div class="hero-controls-bar">
        <div class="finish-selector-group">
          <span class="finish-label">Acabado de Superficie:</span>
          <button class="finish-btn active" onclick="setChassisFinish('black', this)">
            <span class="swatch swatch-black"></span>
            <span>Space Black Anodizado</span>
          </button>
          <button class="finish-btn" onclick="setChassisFinish('titanium', this)">
            <span class="swatch swatch-titanium"></span>
            <span>Titanio Mecanizado</span>
          </button>
          <button class="finish-btn" onclick="setChassisFinish('gold', this)">
            <span class="swatch swatch-gold"></span>
            <span>Oro Champán PVD</span>
          </button>
        </div>

        <div class="hero-features-chips">
          <div class="chip-spec">Masa Total: <strong>920 g</strong></div>
          <div class="chip-spec">Volumen: <strong>148 × 148 × 28 mm</strong></div>
          <div class="chip-spec">Ruido: <strong>0.0 dBA (Pasivo)</strong></div>
          <div class="chip-spec">Latencia: <strong>0.000s Lock</strong></div>
        </div>
      </div>
    </div>

    <!-- ── SECCIÓN 2: ARTESANÍA CNC & EMBLEMA MACRO ── -->
    <section class="emblem-craft-section" id="artesania">
      <div class="emblem-macro-wrapper">
        <img src="assets/slone_luxury_emblem.jpg" alt="Emblema SLÖNE Mecanizado" class="emblem-macro-img">
      </div>
      <div class="emblem-info-box">
        <span class="pre-tag">Mecanizado en Bajorrelieve · Precisión 5 Ejes</span>
        <h3>El Emblema Söberanö: <span>Fresa de Diamante</span></h3>
        <p>
          La cara superior del SLÖNE CÖRE 1 incorpora el emblema esculpido con micro-estrías concéntricas de 50 micras que refractan la luz ambiental en un patrón satinado. Su acabado por deposición física de vapor (PVD) garantiza una resistencia al rayado superior a la del zafiro industrial.
        </p>
        <ul class="specs-bullet-list">
          <li><strong>Geometría Acústica:</strong> Diéresis mecanizada con micro-ranuras de amortiguación para dispersar micro-resonancias del chasis.</li>
          <li><strong>Retroiluminación Cyan:</strong> Halo cuántico regulable por software que indica el bloqueo de audio bit-perfect a 0ms.</li>
          <li><strong>Sensación Táctil:</strong> Transición imperceptible al tacto con bordes biselados a 45 grados sin filos cortantes.</li>
        </ul>
        <div class="certification-pill-group">
          <span class="cert-pill">Dureza 9H PVD</span>
          <span class="cert-pill">Paso CNC 50µm</span>
          <span class="cert-pill">Titanio Grado 5</span>
        </div>
      </div>
    </section>

    <!-- ── TRES PILARES DE INGENIERÍA REAL ── -->
    <div class="grid-3">
      <div class="card-pillar">
        <div class="pillar-icon">⚡</div>
        <h3 class="pillar-title">Silicio Soberano de Alta Eficiencia</h3>
        <p class="pillar-text">
          SoC industrial x86 Quad-Core con aceleración de transcodificación por hardware AV1, HEVC 10-bit y decodificación 4K nativa. Inferencia de voz local con SLÖ ejecutada en memoria RAM en menos de 45 ms sin enviar una sola muestra a la nube.
        </p>
        <div class="pillar-metrics">
          <div class="metric-item">
            <span class="metric-val">4K 60FPS</span>
            <span class="metric-label">Decodificación HW</span>
          </div>
          <div class="metric-item">
            <span class="metric-val">&lt; 45 ms</span>
            <span class="metric-label">Inferencia SLÖ Local</span>
          </div>
        </div>
      </div>

      <div class="card-pillar">
        <div class="pillar-icon">❄️</div>
        <h3 class="pillar-title">Cámara de Vapor de Cobre 0.8 mm</h3>
        <p class="pillar-text">
          Contacto térmico directo (Direct-Contact Cooling DCC) mediante cámara de vapor de cobre electrolítico grado C11000 sellada al vacío. Capilaridad bifásica que transfiere el calor instantáneamente al chasis monobloque sin partes móviles.
        </p>
        <div class="pillar-metrics">
          <div class="metric-item">
            <span class="metric-val">35 W TDP</span>
            <span class="metric-label">Disipación Pasiva</span>
          </div>
          <div class="metric-item">
            <span class="metric-val">&lt; 48.7 °C</span>
            <span class="metric-label">Carga 100% 24h</span>
          </div>
        </div>
      </div>

      <div class="card-pillar">
        <div class="pillar-icon">🎵</div>
        <h3 class="pillar-title">DAC Audiófilo ESS Sabre 32-Bit</h3>
        <p class="pillar-text">
          Conversor analógico/digital ESS Sabre ES9038Q2M con osciladores duales de cristal NDK con fluctuación de reloj inferior a 90 femtosegundos. Salida óptica TOSLINK pura a 192 kHz / 24-bit sin el remuestreo forzado a 48 kHz típico de las Smart TV.
        </p>
        <div class="pillar-metrics">
          <div class="metric-item">
            <span class="metric-val">128 dB</span>
            <span class="metric-label">Rango Dinámico</span>
          </div>
          <div class="metric-item">
            <span class="metric-val">&lt; 90 fs</span>
            <span class="metric-label">Jitter de Reloj</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ── SECCIÓN 3: DESPIECE EXPLOTADO EN CAPAS ── -->
    <section class="section-header" id="despiece">
      <span class="pre-tag">Arquitectura Mecánica & Electrónica</span>
      <h2 class="section-title">Anatomía <span>Interna en 4 Capas</span></h2>
      <p class="section-desc">
        Cada milímetro cúbico responde a un propósito térmico, acústico y de integridad de señal. Selecciona cada estrato para inspeccionar sus especificaciones técnicas de laboratorio.
      </p>
    </section>

    <div class="exploded-view-card">
      <div class="exploded-nav-tabs">
        <button class="tab-layer-btn active" onclick="switchLayer(1, this)">
          <span class="badge-layer-num">1</span>
          <span>Chasis Superior Unibody</span>
        </button>
        <button class="tab-layer-btn" onclick="switchLayer(2, this)">
          <span class="badge-layer-num">2</span>
          <span>Cámara de Vapor DCC</span>
        </button>
        <button class="tab-layer-btn" onclick="switchLayer(3, this)">
          <span class="badge-layer-num">3</span>
          <span>PCB Industrial 10 Capas</span>
        </button>
        <button class="tab-layer-btn" onclick="switchLayer(4, this)">
          <span class="badge-layer-num">4</span>
          <span>Base Térmica & Desacoplo</span>
        </button>
      </div>

      <!-- CAPA 1 -->
      <div class="layer-content-panel active" id="layer-panel-1">
        <div class="layer-visual-box">
          <svg class="layer-svg-diagram" viewBox="0 0 320 220" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="20" y="30" width="280" height="150" rx="14" fill="#141822" stroke="#FFD700" stroke-width="2"/>
            <path d="M40 50 L280 50" stroke="#FFD700" stroke-width="1" stroke-dasharray="4 4" opacity="0.4"/>
            <circle cx="160" cy="105" r="34" stroke="#FFD700" stroke-width="3" fill="none"/>
            <circle cx="140" cy="80" r="5" fill="#FFD700"/>
            <circle cx="180" cy="80" r="7" fill="#FFD700"/>
            <text x="160" y="170" fill="#94A3B8" font-size="10" font-family="monospace" text-anchor="middle">CHASIS MONOLÍTICO 6061-T6 · CNC 5 EJES</text>
          </svg>
        </div>
        <div class="layer-details-box">
          <span class="layer-subtitle">Capa 1 · Estructura Exterior & Blindaje</span>
          <h3>Tapa Monolítica de Aluminio Aeroespacial</h3>
          <p>
            Mecanizada a partir de un bloque macizo de aleación 6061-T6. Su masa actúa como jaula de Faraday integral de 360 grados, protegiendo las etapas analógicas de audio de cualquier interferencia radioeléctrica de Wi-Fi, 5G o telefonía exterior.
          </p>
          <ul class="specs-bullet-list">
            <li><strong>Mecanizado:</strong> Fresado en 5 ejes durante 48 minutos con brocas de carburo de tungsteno.</li>
            <li><strong>Tolerancia dimensional:</strong> ±0.015 mm bajo norma ISO 2768-f.</li>
            <li><strong>Tratamiento:</strong> Micro-arenado cerámico de 150 mesh y anodizado electroquímico MIL-A-8625 Tipo III.</li>
            <li><strong>Emblema Ö:</strong> Bajorrelieve grabado por láser de picosegundos con micro-estrías concéntricas de reflexión luminosa.</li>
          </ul>
          <div class="certification-pill-group">
            <span class="cert-pill">Blindaje EMI 60 dB</span>
            <span class="cert-pill">Norma MIL-STD-810H</span>
            <span class="cert-pill">RoHS 2011/65/EU</span>
          </div>
        </div>
      </div>

      <!-- CAPA 2 -->
      <div class="layer-content-panel" id="layer-panel-2">
        <div class="layer-visual-box">
          <svg class="layer-svg-diagram" viewBox="0 0 320 220" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="30" y="45" width="260" height="130" rx="8" fill="#5E2C04" stroke="#B87333" stroke-width="2.5"/>
            <line x1="30" y1="80" x2="290" y2="80" stroke="#FF8C00" stroke-width="1.5" stroke-dasharray="3 3"/>
            <line x1="30" y1="110" x2="290" y2="110" stroke="#FF8C00" stroke-width="1.5" stroke-dasharray="3 3"/>
            <line x1="30" y1="140" x2="290" y2="140" stroke="#FF8C00" stroke-width="1.5" stroke-dasharray="3 3"/>
            <circle cx="160" cy="110" r="26" fill="#8B4513" stroke="#FF8C00" stroke-width="2"/>
            <text x="160" y="114" fill="#FFF" font-size="9" font-family="monospace" text-anchor="middle">DIRECT CONTACT</text>
            <text x="160" y="195" fill="#FF8C00" font-size="10" font-family="monospace" text-anchor="middle">CÁMARA DE VAPOR DE COBRE ELECTRO-LÍTICO 0.8mm</text>
          </svg>
        </div>
        <div class="layer-details-box">
          <span class="layer-subtitle">Capa 2 · Conducción Térmica Bifásica</span>
          <h3>Cámara de Vapor de Cobre Puro C11000</h3>
          <p>
            Placa de cobre desoxigenado de alta conductividad sellada al vacío con matriz capilar sinterizada de polvo de cobre ultrafino. El fluido térmico interno se evapora sobre el SoC central y condensa en las paredes del chasis, transportando el calor a velocidad sónica.
          </p>
          <ul class="specs-bullet-list">
            <li><strong>Espesor de placa:</strong> 0.8 mm con micro-canales capilares al vacío.</li>
            <li><strong>Conductividad térmica efectiva:</strong> &gt; 8.500 W/m·K (21 veces superior al cobre macizo estándar).</li>
            <li><strong>Interfaz térmica:</strong> Almohadilla de cambio de fase de metal líquido encapsulado con conductividad de 14.2 W/m·K.</li>
            <li><strong>Ventiladores requeridos:</strong> CERO (0). Silencio absoluto garantizado de por vida.</li>
          </ul>
          <div class="certification-pill-group">
            <span class="cert-pill">0.0 dBA Acústica</span>
            <span class="cert-pill">Disipación 35W TDP</span>
            <span class="cert-pill">MTBF &gt; 150.000 h</span>
          </div>
        </div>
      </div>

      <!-- CAPA 3 -->
      <div class="layer-content-panel" id="layer-panel-3">
        <div class="layer-visual-box">
          <svg class="layer-svg-diagram" viewBox="0 0 320 220" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="30" y="40" width="260" height="140" rx="6" fill="#061A14" stroke="#00F0FF" stroke-width="2"/>
            <rect x="70" y="70" width="60" height="60" rx="4" fill="#0A0E17" stroke="#00F0FF" stroke-width="1.5"/>
            <text x="100" y="104" fill="#00F0FF" font-size="10" font-family="monospace" text-anchor="middle">x86 SoC</text>
            <rect x="150" y="70" width="40" height="40" rx="4" fill="#0A0E17" stroke="#FFD700" stroke-width="1.5"/>
            <text x="170" y="94" fill="#FFD700" font-size="9" font-family="monospace" text-anchor="middle">ESS</text>
            <rect x="210" y="70" width="55" height="25" rx="3" fill="#0A0E17" stroke="#94A3B8" stroke-width="1"/>
            <text x="237" y="86" fill="#FFF" font-size="8" font-family="monospace" text-anchor="middle">DUAL 2.5G</text>
            <text x="160" y="195" fill="#00F0FF" font-size="10" font-family="monospace" text-anchor="middle">PCB 10 CAPAS HDI · TRAZADOS DE IMPEDANCIA MATCHED</text>
          </svg>
        </div>
        <div class="layer-details-box">
          <span class="layer-subtitle">Capa 3 · Silicio, Procesamiento & Audio</span>
          <h3>Placa Base de Grado Industrial de 10 Capas</h3>
          <p>
            Placa de circuito impreso HDI con planos de masa aislados para la sección digital y analógica de audio. Componentes certificados de grado automotriz e industrial con tolerancia extendida de temperatura (-40°C a +85°C).
          </p>
          <ul class="specs-bullet-list">
            <li><strong>SoC Principal:</strong> Intel Architecture 4 Cores / 4 Threads con acelerador VA-API QuickSync para AV1 y HEVC.</li>
            <li><strong>Audio DAC:</strong> ESS Sabre ES9038Q2M emparejado con operacionales balanceados TI OPA1612.</li>
            <li><strong>Reloj de Sincronismo:</strong> Osciladores gemelos NDK NZ2520SDA con jitter de fase &lt; 90 femtosegundos.</li>
            <li><strong>Red:</strong> Doble controladora Intel I226-V 2.5 GbE con transformadores de aislamiento galvánico de 1.5 kV.</li>
            <li><strong>Seguridad Soberana:</strong> Criptoprocesador Infineon TPM 2.0 integrado para arranque criptográfico verificado.</li>
          </ul>
          <div class="certification-pill-group">
            <span class="cert-pill">16GB LPDDR5X-6400</span>
            <span class="cert-pill">PCIe 4.0 NVMe</span>
            <span class="cert-pill">TPM 2.0 Zero-Trust</span>
          </div>
        </div>
      </div>

      <!-- CAPA 4 -->
      <div class="layer-content-panel" id="layer-panel-4">
        <div class="layer-visual-box">
          <svg class="layer-svg-diagram" viewBox="0 0 320 220" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="25" y="45" width="270" height="130" rx="10" fill="#0F131C" stroke="#475569" stroke-width="2"/>
            <!-- Aletas ranuradas -->
            <line x1="50" y1="70" x2="270" y2="70" stroke="#334155" stroke-width="3"/>
            <line x1="50" y1="90" x2="270" y2="90" stroke="#334155" stroke-width="3"/>
            <line x1="50" y1="110" x2="270" y2="110" stroke="#334155" stroke-width="3"/>
            <line x1="50" y1="130" x2="270" y2="130" stroke="#334155" stroke-width="3"/>
            <line x1="50" y1="150" x2="270" y2="150" stroke="#334155" stroke-width="3"/>
            <!-- Pies de desacoplo -->
            <circle cx="55" cy="55" r="10" fill="#000" stroke="#00F0FF" stroke-width="1.5"/>
            <circle cx="265" cy="55" r="10" fill="#000" stroke="#00F0FF" stroke-width="1.5"/>
            <circle cx="55" cy="165" r="10" fill="#000" stroke="#00F0FF" stroke-width="1.5"/>
            <circle cx="265" cy="165" r="10" fill="#000" stroke="#00F0FF" stroke-width="1.5"/>
            <text x="160" y="195" fill="#94A3B8" font-size="10" font-family="monospace" text-anchor="middle">BASE DISIPADORA + PIES DE FLUOROSILICONA</text>
          </svg>
        </div>
        <div class="layer-details-box">
          <span class="layer-subtitle">Capa 4 · Aislamiento Acústico & Convección</span>
          <h3>Base de Convección Ranurada & Pies Desacoplados</h3>
          <p>
            La base del micro-appliance cuenta con 16 ranuras fresadas para crear un efecto chimenea de tiro natural ascendente. Cuatro soportes de fluorosilicona aeroespacial desacoplan el chasis de la superficie del mueble, absorbiendo microfonías y resonancias parásitas.
          </p>
          <ul class="specs-bullet-list">
            <li><strong>Flujo térmico:</strong> Convección pasiva vertical asistida por diferencia de presión térmica.</li>
            <li><strong>Desacoplo de vibraciones:</strong> Coeficiente de amortiguamiento viscoelástico &gt; 0.85.</li>
            <li><strong>Masa estabilizadora:</strong> Centro de masa rebajado para impedir que cables pesados HDMI muevan el equipo.</li>
            <li><strong>Cierre hermético:</strong> Tornillería oculta de acero inoxidable grado marino A4 con par de apriete dinamométrico.</li>
          </ul>
          <div class="certification-pill-group">
            <span class="cert-pill">Aislamiento &gt; 25 dB</span>
            <span class="cert-pill">Cero Tornillos Visibles</span>
            <span class="cert-pill">Tornillería A4</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ── SECCIÓN 4: CAD BLUEPRINT PANEL TRASERO ── -->
    <section class="section-header" id="puertos">
      <span class="pre-tag">Conectividad de Grado Broadcast</span>
      <h2 class="section-title">Panel Posterior <span>CAD Milimétrico</span></h2>
      <p class="section-desc">
        Diseñado con cotas mecánicas precisas para soportar conectores de alta gama y blindaje electrostático directo a tierra de chasis.
      </p>
    </section>

    <div class="cad-rear-section">
      <div class="cad-blueprint-box">
        <span class="cad-dimension-indicator">COTAS: 148.0 mm × 28.0 mm · TOLERANCIA: ±0.05 mm</span>
        
        <div class="cad-chassis-plate">
          <!-- 1. HDMI 2.1 -->
          <div class="cad-port-item" title="HDMI 2.1 eARC / ALLM">
            <div class="port-socket hdmi"></div>
            <span class="port-title">HDMI 2.1</span>
            <span class="port-pin-spec">48 Gbps</span>
          </div>

          <!-- 2. SPDIF ÓPTICO -->
          <div class="cad-port-item" title="TOSLINK SPDIF Óptico 192kHz">
            <div class="port-socket spdif"></div>
            <span class="port-title">TOSLINK</span>
            <span class="port-pin-spec">192k/24b</span>
          </div>

          <!-- 3. LAN 1 (Intel 2.5G) -->
          <div class="cad-port-item" title="LAN 1 (Intel I226-V 2.5 GbE)">
            <div class="port-socket rj45"></div>
            <span class="port-title">LAN 1 (WAN)</span>
            <span class="port-pin-spec">2.5 GbE</span>
          </div>

          <!-- 4. LAN 2 (Intel 2.5G) -->
          <div class="cad-port-item" title="LAN 2 (Direct TV / NAS Dedicated)">
            <div class="port-socket rj45"></div>
            <span class="port-title">LAN 2 (TV)</span>
            <span class="port-pin-spec">2.5 GbE</span>
          </div>

          <!-- 5. USB 3.2 Gen 2 -->
          <div class="cad-port-item" title="USB 3.2 Gen 2 (10 Gbps Type-A)">
            <div class="port-socket usba"></div>
            <span class="port-title">USB 3.2</span>
            <span class="port-pin-spec">10 Gbps</span>
          </div>

          <!-- 6. USB-C Power -->
          <div class="cad-port-item" title="USB-C PD 3.0 GaN 65W">
            <div class="port-socket usbc"></div>
            <span class="port-title">USB-C PD</span>
            <span class="port-pin-spec">65W GaN</span>
          </div>

          <!-- 7. Hard Reset -->
          <div class="cad-port-item" title="Hard Reset Físico Bóveda">
            <div class="port-socket recovery"></div>
            <span class="port-title">RESET</span>
            <span class="port-pin-spec">BÓVEDA</span>
          </div>
        </div>
      </div>

      <div class="cad-ports-grid">
        <div class="card-port-spec">
          <div class="port-spec-header">
            <h4>HDMI 2.1 eARC / VRR</h4>
            <span class="badge-bus">48 Gbps FRL6</span>
          </div>
          <p>Transmisión de vídeo 4K a 120Hz con soporte HDR10+, Dolby Vision y canal de retorno de audio eARC sin compresión (Dolby TrueHD y DTS:X directos a barra de sonido).</p>
        </div>

        <div class="card-port-spec">
          <div class="port-spec-header">
            <h4>TOSLINK Óptico Bit-Perfect</h4>
            <span class="badge-bus">Láser Cuarzo 25 Mbps</span>
          </div>
          <p>Transmisor óptico de alta velocidad con compuerta anti-polvo. Emisión de audio digital I2S nativo a 192 kHz / 24-bit sin el desfase ni la conversión forzada de Android.</p>
        </div>

        <div class="card-port-spec">
          <div class="port-spec-header">
            <h4>Doble Ethernet Intel I226-V</h4>
            <span class="badge-bus">Dual 2.5 Gbps</span>
          </div>
          <p>Un puerto dedicado a la conexión de fibra/router y el segundo puerto como enlace directo punto a punto con tu Smart TV para streaming aislado libre de colisiones.</p>
        </div>

        <div class="card-port-spec">
          <div class="port-spec-header">
            <h4>USB 3.2 Gen 2 Blindado</h4>
            <span class="badge-bus">10 Gbps · 5V 2.1A</span>
          </div>
          <p>Conector reforzado de acero inoxidable para conexión de discos NVMe externos de alta velocidad o DACs balanceados audiófilos externos.</p>
        </div>

        <div class="card-port-spec">
          <div class="port-spec-header">
            <h4>Alimentación USB-C GaN PD 3.0</h4>
            <span class="badge-bus">Etapa LC &lt; 8mV Rizado</span>
          </div>
          <p>Etapa de alimentación de alta pureza con inductores Würth Elektronik y condensadores de tantalio, eliminando cualquier ruido eléctrico en la cadena de audio.</p>
        </div>

        <div class="card-port-spec">
          <div class="port-spec-header">
            <h4>Botón de Bóveda & Recovery</h4>
            <span class="badge-bus">Cero Telemetría</span>
          </div>
          <p>Micro-pulsador empotrado que permite restaurar el firmware local a imagen dorada de fábrica sin conexión a Internet ni dependencia de servidores de SLÖNE.</p>
        </div>
      </div>
    </div>

    <!-- ── SECCIÓN 5: ENSAYOS DE LABORATORIO (ANTI-ESTAFA) ── -->
    <section class="section-header" id="laboratorio">
      <span class="pre-tag">Pruebas Físicas de Laboratorio & Fiabilidad</span>
      <h2 class="section-title">Certificación <span>Térmica & Acústica</span></h2>
      <p class="section-desc">
        Datos empíricos medidos en cámara anecoica y bancos de estrés continuo. Porque la credibilidad técnica no se promete: se audita con instrumental de precisión.
      </p>
    </section>

    <div class="lab-tests-section">
      <div class="grid-2">
        <!-- Tarjeta 1: Cámara Anecoica y Acústica -->
        <div class="bench-card">
          <div class="bench-card-header">
            <h3>Ensayo Acústico en Cámara Anecoica</h3>
            <span class="cert-pill">ISO 3745 Grado 1</span>
          </div>
          <div class="telemetry-row">
            <span>Ruido base de la cámara de prueba:</span>
            <strong>14.2 dBA</strong>
          </div>
          <div class="telemetry-row">
            <span>SLÖNE CÖRE 1 en reposo (a 30 cm):</span>
            <strong>14.2 dBA</strong>
          </div>
          <div class="telemetry-row">
            <span>SLÖNE CÖRE 1 reproduciendo 4K 60FPS:</span>
            <strong>14.2 dBA</strong>
          </div>
          <div class="telemetry-row">
            <span>Ruido propio neto medido:</span>
            <strong class="accent-cyan">0.0 dBA (Silencio Absoluto)</strong>
          </div>
          <div class="telemetry-row">
            <span>Ruido de bobinas (Coil Whine):</span>
            <strong class="accent-gold">&lt; 1.2 µV (Inductores Apantallados)</strong>
          </div>
          <p style="font-size: 0.78rem; color: var(--text-dim); margin-top: 1.2rem; line-height: 1.5;">
            Al prescindir totalmente de ventiladores y bombas mecánicas, el equipo no emite ningún sonido audible ni genera corriente de convección forzada que atraiga pelusa al interior.
          </p>
        </div>

        <!-- Tarjeta 2: Termografía FLIR -->
        <div class="bench-card">
          <div class="bench-card-header">
            <h3>Disipación Térmica Continua 24 Horas</h3>
            <span class="cert-pill">FLIR T865 Termografía</span>
          </div>
          <div class="telemetry-row">
            <span>Temperatura ambiente de prueba:</span>
            <strong>22.0 °C</strong>
          </div>
          <div class="telemetry-row">
            <span>Temperatura del chip en reposo:</span>
            <strong>38.2 °C</strong>
          </div>
          <div class="telemetry-row">
            <span>Carga máxima sostenida 4K 60FPS:</span>
            <strong class="accent-cyan">47.8 °C en el encapsulado</strong>
          </div>
          <div class="telemetry-row">
            <span>Temperatura exterior del chasis CNC:</span>
            <strong>34.1 °C (Tibio y uniforme)</strong>
          </div>
          <div class="telemetry-row">
            <span>Límite de estrangulamiento térmico (Tj):</span>
            <strong>95.0 °C (Margen: +47.2 °C)</strong>
          </div>

          <div class="thermal-graph-box">
            <div class="thermal-bar-wrap">
              <span class="thermal-label">SLÖNE CÖRE 1 (Pasivo):</span>
              <div class="thermal-track">
                <div class="thermal-fill fill-slone"></div>
              </div>
              <span class="thermal-val">47.8°C</span>
            </div>
            <div class="thermal-bar-wrap">
              <span class="thermal-label">Android Box Plástico:</span>
              <div class="thermal-track">
                <div class="thermal-fill fill-generic"></div>
              </div>
              <span class="thermal-val">84.2°C</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Telemetría de Red y Cero Telemetría -->
      <div style="margin-top: 2rem; background: #020408; border: 1px solid rgba(255,255,255,0.06); border-radius: 18px; padding: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem; flex-wrap: wrap; gap: 10px;">
          <h3 style="font-size: 1.15rem; font-weight: 800; color: #FFF;">Auditoría de Tráfico de Red (Zero-Trust Moat)</h3>
          <span class="cert-pill" style="border-color: #00FF88; color: #00FF88;">0 Bytes Telemetría Externa</span>
        </div>
        <p style="font-size: 0.84rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 1.5rem;">
          Captura exhaustiva con analizador de protocolos Wireshark ejecutada durante 72 horas de emisión ininterrumpida. Ningún paquete UDP/TCP abandona la red local con destino a servidores de Google, Apple, Amazon o analítica publicitaria.
        </p>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;">
          <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="font-size: 0.7rem; color: var(--text-dim); text-transform: uppercase;">Peticiones a la Nube</div>
            <div style="font-size: 1.3rem; font-weight: 900; color: #00FF88; font-family: monospace;">0 / seg</div>
          </div>
          <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="font-size: 0.7rem; color: var(--text-dim); text-transform: uppercase;">Tracking de Usuarios</div>
            <div style="font-size: 1.3rem; font-weight: 900; color: #00FF88; font-family: monospace;">INEXISTENTE</div>
          </div>
          <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="font-size: 0.7rem; color: var(--text-dim); text-transform: uppercase;">Procesamiento de Voz</div>
            <div style="font-size: 1.3rem; font-weight: 900; color: var(--cyan); font-family: monospace;">100% LOCAL</div>
          </div>
          <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="font-size: 0.7rem; color: var(--text-dim); text-transform: uppercase;">Arranque Criptográfico</div>
            <div style="font-size: 1.3rem; font-weight: 900; color: var(--gold); font-family: monospace;">TPM 2.0 LOCK</div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── SECCIÓN 6: COMPARATIVA TÉCNICA DEFINITIVA ── -->
    <section class="section-header" id="comparativa">
      <span class="pre-tag">Benchmarking frente al Mercado</span>
      <h2 class="section-title">Comparativa <span>Implacable</span></h2>
      <p class="section-desc">
        Compara las especificaciones físicas y arquitectónicas de SLÖNE CÖRE 1 frente a los reproductores comerciales cerrados y las cajas genéricas de plástico.
      </p>
    </section>

    <div class="table-compare-wrapper">
      <table class="compare-table">
        <thead>
          <tr>
            <th>Parámetro Técnico</th>
            <th class="col-slone">SLÖNE CÖRE 1</th>
            <th>Apple TV 4K (3ª Gen)</th>
            <th>Nvidia Shield Pro</th>
            <th>Android TV Genérico (40€)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Material del Chasis</strong></td>
            <td class="col-slone">Aluminio CNC 6061-T6 Macizo (920g)</td>
            <td>Plástico reciclado + disipador interno</td>
            <td>Plástico ABS inyectado</td>
            <td>Plástico fino barato (140g)</td>
          </tr>
          <tr>
            <td><strong>Refrigeración / Acústica</strong></td>
            <td class="col-slone"><span class="badge-check">✓</span> 0.0 dBA Pasivo (Cámara de vapor)</td>
            <td>0.0 dBA Pasivo</td>
            <td>Ventilador centrífugo activo</td>
            <td>Disipador de aluminio diminuto (&gt;80°C)</td>
          </tr>
          <tr>
            <td><strong>Calibración Lip-Sync Audio</strong></td>
            <td class="col-slone"><span class="badge-check">✓</span> Precisión continua de ±1 ms en vivo</td>
            <td><span class="badge-cross">✗</span> Sin calibración manual fina</td>
            <td><span class="badge-cross">✗</span> Ajuste tosco de pasos fijos</td>
            <td><span class="badge-cross">✗</span> Desfase audio/vídeo constante</td>
          </tr>
          <tr>
            <td><strong>Salida SPDIF Óptica TOSLINK</strong></td>
            <td class="col-slone"><span class="badge-check">✓</span> Nativa dedicada 192k / 24b</td>
            <td><span class="badge-cross">✗</span> No tiene (sólo HDMI)</td>
            <td><span class="badge-cross">✗</span> No tiene (sólo HDMI)</td>
            <td>Mini-jack óptico compartido de baja calidad</td>
          </tr>
          <tr>
            <td><strong>Puertos Ethernet Físicos</strong></td>
            <td class="col-slone"><span class="badge-check">✓</span> Doble 2.5 GbE Intel I226-V</td>
            <td>1x Gigabit Ethernet (solo en modelo 128GB)</td>
            <td>1x Gigabit Ethernet</td>
            <td>1x Fast Ethernet 100 Mbps (obsoleto)</td>
          </tr>
          <tr>
            <td><strong>Privacidad & Telemetría</strong></td>
            <td class="col-slone"><span class="badge-check">✓</span> 100% Soberana (0 llamadas a la nube)</td>
            <td>Cuenta Apple obligatoria + iCloud ID</td>
            <td>Cuenta Google obligatoria + Publicidad</td>
            <td>Riesgo grave de malware preinstalado</td>
          </tr>
          <tr>
            <td><strong>Control por Voz (SLÖ)</strong></td>
            <td class="col-slone"><span class="badge-check">✓</span> Procesamiento 100% offline en RAM</td>
            <td>Envío de audio a servidores de Apple</td>
            <td>Envío de audio a Google Assistant</td>
            <td>Envío de audio a servidores desconocidos</td>
          </tr>
          <tr>
            <td><strong>Transmisión a Auriculares (QR)</strong></td>
            <td class="col-slone"><span class="badge-check">✓</span> Modo Estadio B2B sin apps instaladas</td>
            <td><span class="badge-cross">✗</span> Requiere AirPods enlazados</td>
            <td><span class="badge-cross">✗</span> Requiere mando vinculado</td>
            <td><span class="badge-cross">✗</span> Inexistente</td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>

  <!-- ── FOOTER INDUSTRIAL ── -->
  <footer>
    <div class="footer-content">
      <img src="assets/slone_luxury_logo.svg" alt="SLÖNE CÖRP" class="footer-logo">
      <p class="footer-text">
        SLÖNE CÖRE 1 es el appliance definitivo del ecosistema SLÖNE. Construido con estándares de ingeniería de precisión, acústica inmaculada de 0 dB y respeto absoluto por la soberanía del usuario.
      </p>
      <div class="footer-links">
        <a href="index.html">Portal Central</a>
        <a href="#showcase">Estudio Fotográfico</a>
        <a href="#artesania">Emblema CNC</a>
        <a href="#despiece">Despiece Técnico</a>
        <a href="#puertos">Panel CAD</a>
        <a href="#laboratorio">Certificaciones</a>
        <a href="identidad.html">Símbolo Ö</a>
      </div>
      <div class="footer-copy">
        SLÖNE CÖRP · HARDWARE SOBERANO · FEDORA 44 LINUX · THINKPAD X390 ARCHITECTURE
      </div>
    </div>
  </footer>

  <!-- ── JAVASCRIPT DE INTERACCIÓN Y MAGNIFICADOR ── -->
  <script>
    // 1. SELECTOR DE ACABADOS EN EL SHOWCASE
    function setChassisFinish(finish, btn) {
      document.querySelectorAll('.finish-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const stage = document.getElementById('hero-stage');
      stage.classList.remove('finish-titanium', 'finish-gold');

      if (finish === 'titanium') {
        stage.classList.add('finish-titanium');
      } else if (finish === 'gold') {
        stage.classList.add('finish-gold');
      }
    }

    // 2. TABS DE DESPIECE EXPLOTADO
    function switchLayer(layerNum, btn) {
      document.querySelectorAll('.tab-layer-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      document.querySelectorAll('.layer-content-panel').forEach(panel => {
        panel.classList.remove('active');
      });

      const target = document.getElementById('layer-panel-' + layerNum);
      if (target) {
        target.classList.add('active');
      }
    }

    // 3. LUPA DE AUMENTO DE ALTA PRECISIÓN (LOUPE GLASS ZOOM)
    const stage = document.getElementById('hero-stage');
    const heroImg = document.getElementById('hero-main-img');
    const loupe = document.getElementById('loupe-glass');

    if (stage && heroImg && loupe) {
      const zoomFactor = 2.4;

      stage.addEventListener('mouseenter', () => {
        loupe.style.display = 'block';
        loupe.style.backgroundImage = `url('${heroImg.src}')`;
      });

      stage.addEventListener('mouseleave', () => {
        loupe.style.display = 'none';
      });

      stage.addEventListener('mousemove', (e) => {
        const rect = stage.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Limitar dentro del recuadro
        if (x < 0 || y < 0 || x > rect.width || y > rect.height) {
          loupe.style.display = 'none';
          return;
        }

        loupe.style.display = 'block';
        const loupeWidth = loupe.offsetWidth;
        const loupeHeight = loupe.offsetHeight;

        loupe.style.left = (x - loupeWidth / 2) + 'px';
        loupe.style.top = (y - loupeHeight / 2) + 'px';

        // Escalar fondo en la lupa
        const bgWidth = rect.width * zoomFactor;
        const bgHeight = rect.height * zoomFactor;
        const bgX = (x * zoomFactor) - (loupeWidth / 2);
        const bgY = (y * zoomFactor) - (loupeHeight / 2);

        loupe.style.backgroundSize = `${bgWidth}px ${bgHeight}px`;
        loupe.style.backgroundPosition = `-${bgX}px -${bgY}px`;
      });
    }
  </script>
</body>
</html>
'''

import os

def main():
    target_path = "/home/slone/slocast 1.0/app/web_portal/hardware.html"
    print(f"Escribiendo hardware.html de lujo soberano en {target_path}...")
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print("¡Generación completada con éxito!")

if __name__ == "__main__":
    main()
