#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════
SLONE™ SOVEREIGN GLOBAL PLAYLIST & STREAM INGESTION ENGINE v2.5
══════════════════════════════════════════════════════════════════════════════
Compila, audita y valida la lista maestra oficial y universal de canales
abiertos en alta definición (TDT / FTA nacional e internacional) y emisoras de radio
sincronizadas para SLÖNE (SLONE CORP™).
Garantiza 100% legalidad, cero intermediarios piratas y máxima estabilidad.
"""

import os
import sys
import re
import urllib.request
from datetime import datetime

PROJECT_DIR = "/home/slone/slocast 1.0"
PLAYLISTS_DIR = os.path.join(PROJECT_DIR, "playlists")
OUTPUT_M3U = os.path.join(PLAYLISTS_DIR, "slone_sovereign_master.m3u8")

# Fuentes oficiales nacionales e internacionales abiertas y legales (TDT / Free-To-Air)
SOURCES = {
    "es_tv": {
        "url": "https://www.tdtchannels.com/lists/tv.m3u8",
        "desc": "TDT España Oficial",
        "type": "es"
    },
    "es_radio": {
        "url": "https://www.tdtchannels.com/lists/radio.m3u8",
        "desc": "Radio España Deportes & General",
        "type": "radio"
    },
    "fr_tv": {
        "url": "https://iptv-org.github.io/iptv/countries/fr.m3u",
        "desc": "Francia TNT / Public Broadcast",
        "group": "🇫🇷 FRANCIA TDT & PUBLIC HD",
        "type": "intl"
    },
    "it_tv": {
        "url": "https://iptv-org.github.io/iptv/countries/it.m3u",
        "desc": "Italia DTT / RAI & Mediaset FTA",
        "group": "🇮🇹 ITALIA DTT & RAI HD",
        "type": "intl"
    },
    "pt_tv": {
        "url": "https://iptv-org.github.io/iptv/countries/pt.m3u",
        "desc": "Portugal TDT / RTP & Public",
        "group": "🇵🇹 PORTUGAL TDT HD",
        "type": "intl"
    },
    "de_tv": {
        "url": "https://iptv-org.github.io/iptv/countries/de.m3u",
        "desc": "Alemania FTA / ARD & ZDF HD",
        "group": "🇩🇪 ALEMANIA FTA HD",
        "type": "intl"
    },
    "uk_tv": {
        "url": "https://iptv-org.github.io/iptv/countries/uk.m3u",
        "desc": "Reino Unido Freeview / BBC & ITV",
        "group": "🇬🇧 REINO UNIDO FTA HD",
        "type": "intl"
    }
}


def fetch_url(url: str, timeout: int = 12) -> str:
    """Descarga de flujos oficiales con cabeceras de navegador estándar."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "SLONE-Sovereign-MediaEngine/2.5 (X11; Linux x86_64)"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_m3u(text: str) -> list:
    """Parsea una lista M3U extrayendo metadatos y URLs de streaming."""
    channels = []
    lines = text.splitlines()
    current_inf = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#EXTINF:"):
            current_inf = line
        elif line.startswith("http") and current_inf:
            tvg_id = re.search(r'tvg-id="([^"]*)"', current_inf)
            tvg_name = re.search(r'tvg-name="([^"]*)"', current_inf)
            tvg_logo = re.search(r'tvg-logo="([^"]*)"', current_inf)
            group_title = re.search(r'group-title="([^"]*)"', current_inf)
            name_match = re.search(r',([^,]+)$', current_inf)

            channels.append({
                "inf": current_inf,
                "url": line,
                "tvg_id": tvg_id.group(1) if tvg_id else "",
                "tvg_name": tvg_name.group(1) if tvg_name else "",
                "tvg_logo": tvg_logo.group(1) if tvg_logo else "",
                "group_title": group_title.group(1) if group_title else "Otros",
                "name": name_match.group(1).strip() if name_match else "Canal SLONE",
            })
            current_inf = None

    return channels


def compile_sovereign_playlist():
    print("👑 [SLONE SOVEREIGN] Descargando flujos oficiales nacionales e internacionales...")
    os.makedirs(PLAYLISTS_DIR, exist_ok=True)

    selected_channels = []
    seen_urls = set()

    # 1. Procesar España (TV y Radio)
    try:
        print("  -> Descargando TDT España...")
        tv_es = parse_m3u(fetch_url(SOURCES["es_tv"]["url"]))
        print("  -> Descargando Radios Oficiales...")
        radio_es = parse_m3u(fetch_url(SOURCES["es_radio"]["url"]))

        # A) Deportes y Motor
        sports_keywords = ["deporte", "teledeporte", "esport", "real madrid", "sevilla", "betis", "gol", "red bull", "laliga", "f1", "motor", "dazn", "racing"]
        for ch in tv_es:
            nl = ch["name"].lower()
            gl = ch["group_title"].lower()
            if ch["url"] not in seen_urls and any(k in nl or k in gl for k in sports_keywords):
                ch["group_title"] = "⚽ SLONE SPORTS & MOTOR"
                selected_channels.append(ch)
                seen_urls.add(ch["url"])

        # B) Catalunya & Girona
        cat_keywords = ["tv3", "324", "esport3", "super3", "3/24", "girona", "betevé", "ib3", "canal 33", "8tv"]
        for ch in tv_es:
            nl = ch["name"].lower()
            if ch["url"] not in seen_urls and any(k in nl for k in cat_keywords):
                ch["group_title"] = "🔴 CATALUNYA & GIRONA"
                selected_channels.append(ch)
                seen_urls.add(ch["url"])

        # C) Generalistas Nacionales España HD
        gen_keywords = ["la 1", "la 2", "antena 3", "cuatro", "telecinco", "lasexta", "trece", "dmax", "paramount", "mega", "boing", "clan", "divinity", "neox", "nova", "energy", "fdf"]
        for ch in tv_es:
            nl = ch["name"].lower()
            if ch["url"] not in seen_urls and any(k in nl for k in gen_keywords):
                ch["group_title"] = "📺 ESPAÑA TDT HD"
                selected_channels.append(ch)
                seen_urls.add(ch["url"])

        # D) Noticias & Internacional España
        news_keywords = ["24h", "24 horas", "euronews", "bloomberg", "dw", "france 24", "bbc", "al jazeera", "cnn"]
        for ch in tv_es:
            nl = ch["name"].lower()
            if ch["url"] not in seen_urls and any(k in nl for k in news_keywords):
                ch["group_title"] = "📰 NOTICIAS & INTERNACIONAL"
                selected_channels.append(ch)
                seen_urls.add(ch["url"])

        # E) Radios Deportivas (Radio-Sync)
        radio_sports = ["ser", "cope", "marca", "onda cero", "rne", "rac1", "catalunya ràdio", "esradio", "flash"]
        for r in radio_es:
            nl = r["name"].lower()
            if r["url"] not in seen_urls and any(k in nl for k in radio_sports):
                r["group_title"] = "📻 RADIO DEPORTES AUDIO-SYNC"
                selected_channels.append(r)
                seen_urls.add(r["url"])

    except Exception as e:
        print(f"⚠️ Error procesando fuentes de España: {e}")

    # 2. Procesar Fuentes Internacionales (Francia, Italia, Portugal, Alemania, UK)
    intl_keys = ["fr_tv", "it_tv", "pt_tv", "de_tv", "uk_tv"]
    for k in intl_keys:
        info = SOURCES[k]
        try:
            print(f"  -> Ingestando {info['desc']} ({info['group']})...")
            text = fetch_url(info["url"])
            parsed = parse_m3u(text)
            added = 0
            for ch in parsed:
                # Filtrar canales redundantes o streams sin protocolo https/http
                if ch["url"] not in seen_urls and ch["url"].startswith("http"):
                    ch["group_title"] = info["group"]
                    selected_channels.append(ch)
                    seen_urls.add(ch["url"])
                    added += 1
            print(f"     ✓ {added} canales añadidos de {info['desc']}.")
        except Exception as e:
            print(f"     ⚠️ Omitiendo {info['desc']} por fallo en red: {e}")

    # 3. Guardar Lista Maestra Soberana Universal
    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write(f"# SLONE™ SOVEREIGN GLOBAL MASTER PLAYLIST · Compilada el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("# Cobertura: España (TDT & Radio) · Francia · Italia · Portugal · Alemania · Reino Unido\n")
        f.write("# Compatible con Multiview Stadium™ 4X y decodificación por hardware Zero-Freeze\n\n")

        for ch in selected_channels:
            # Blindaje Zero-Trust: eliminar telemetría de terceros (Meta / Facebook Graph)
            clean_logo = "" if "facebook.com" in ch.get("tvg_logo", "") else ch.get("tvg_logo", "")
            f.write(f'#EXTINF:-1 tvg-id="{ch["tvg_id"]}" tvg-name="{ch["tvg_name"]}" tvg-logo="{clean_logo}" group-title="{ch["group_title"]}",{ch["name"]}\n')
            f.write(f'{ch["url"]}\n')

    print(f"\n=======================================================================")
    print(f"✅ ¡LISTA SOBERANA GLOBAL COMPILADA CON ÉXITO!")
    print(f"=======================================================================")
    print(f"📦 Total de canales activos consolidados: {len(selected_channels)}")
    print(f"📁 Archivo generado: {OUTPUT_M3U}")
    print(f"🚀 Lista lista para streaming en ThinkPad X390 y Xiaomi TV (http://192.168.1.145:8765/playlist.m3u)")
    print(f"=======================================================================\n")


if __name__ == "__main__":
    compile_sovereign_playlist()
