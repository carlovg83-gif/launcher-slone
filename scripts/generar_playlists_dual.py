#!/usr/bin/env python3
"""
SLÖNE DUAL-TRACK PLAYLIST ENGINE
══════════════════════════════════════════════════════════════════════════
Genera dos listas maestras optimizadas:
1. Soberana (100% legal, abierta, sin riesgo legal para distribución pública).
2. Privada (IPTV de slone con EPG oficial inyectado y Timeshift 7 días).
"""

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
PLAYLISTS_DIR = BASE_DIR / "playlists"
PLAYLISTS_DIR.mkdir(parents=True, exist_ok=True)

SOVEREIGN_SOURCE = PLAYLISTS_DIR / "slone_sovereign_master.m3u8"
PRIVATE_SOURCE = Path("/home/slone/Descargas/TV-76173252_playlist.m3u")
PRIVATE_DEST = PLAYLISTS_DIR / "slone_private_master.m3u8"

def process_sovereign():
    if not SOVEREIGN_SOURCE.exists():
        print(f"⚠️ Aviso: Fuente soberana no encontrada en {SOVEREIGN_SOURCE}")
        return
    
    content = SOVEREIGN_SOURCE.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()
    
    epg_header = '#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_ES1.xml.gz,https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guiatv.xml"'
    
    if lines and lines[0].startswith("#EXTM3U"):
        lines[0] = epg_header
    else:
        lines.insert(0, epg_header)
        
    SOVEREIGN_SOURCE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✅ Lista Soberana enriquecida con EPG Multi-Idioma: {SOVEREIGN_SOURCE}")

def process_private():
    if not PRIVATE_SOURCE.exists():
        print(f"⚠️ Aviso: Fuente IPTV privada no encontrada en {PRIVATE_SOURCE}")
        return
    
    content = PRIVATE_SOURCE.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()
    
    # Cabecera enriquecida con XMLTV EPG del proveedor + fallback España + Timeshift Catchup 7 días
    private_header = (
        '#EXTM3U url-tvg="http://398607.solanaflix.com/xmltv.php?username=TV-76173252&password=624816943106,https://epgshare01.online/epgshare01/epg_ripper_ES1.xml.gz" '
        'catchup="timeshift" catchup-days="7" '
        'catchup-source="http://398607.solanaflix.com/timeshift/TV-76173252/624816943106/{duration}/{start}.ts"'
    )
    
    if lines and lines[0].startswith("#EXTM3U"):
        lines[0] = private_header
    else:
        lines.insert(0, private_header)
        
    PRIVATE_DEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✅ Lista Privada IPTV enriquecida con EPG y Timeshift 7d: {PRIVATE_DEST} ({len(lines)} líneas)")

def main():
    print("══════════════════════════════════════════════════════════")
    print("SLÖNE — GENERACIÓN DUAL DE LISTAS IPTV Y SOBERANA")
    print("══════════════════════════════════════════════════════════")
    process_sovereign()
    process_private()
    print("══════════════════════════════════════════════════════════")

if __name__ == "__main__":
    main()
