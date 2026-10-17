#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════
# SLÖNE™ SOVEREIGN SMART TV & LAN HUB
# ══════════════════════════════════════════════════════════════════════════
# Servidor autónomo de alta velocidad para Xiaomi TV, Android TV, TiviMate y Web
# ══════════════════════════════════════════════════════════════════════════

import http.server
import json
import os
import re
import socket
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import gzip
import threading

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
try:
    from app.slone_epg import EpgManager
    EPG_MGR = EpgManager()

    def _init_epg_cache():
        cache_dir = BASE_DIR / "cache"
        for p in [cache_dir / "epg_tdt.xml.gz", cache_dir / "epg_doblem.xml.gz", cache_dir / "epg_es.xml.gz"]:
            if p.exists():
                try:
                    with gzip.open(p, "rb") as f:
                        cnt = EPG_MGR.parse(f.read())
                        print(f"[SLÖNE EPG] Cargados {cnt} programas desde {p.name}")
                except Exception as ex:
                    print(f"[SLÖNE EPG] Error leyendo {p.name}: {ex}")

    threading.Thread(target=_init_epg_cache, daemon=True).start()
except Exception as e:
    EPG_MGR = None

PLAYLIST_FILE = BASE_DIR / "playlists" / "slone_sovereign_master.m3u8"
PLAYLIST_SOVEREIGN = BASE_DIR / "playlists" / "slone_sovereign_master.m3u8"
PLAYLIST_PRIVATE = BASE_DIR / "playlists" / "slone_private_master.m3u8"
WEB_PORTAL_DIR = BASE_DIR / "app" / "web_portal"
PORT = 8765

ADB_DEVICE = "192.168.1.135:5555"
ADB_BIN = "/home/slone/.local/bin/adb" if os.path.exists("/home/slone/.local/bin/adb") else "adb"

def safe_run_adb(*adb_args):
    """Ejecuta comandos ADB de forma segura con subprocess y lista fija, sin invocar bash shell."""
    cmd = [ADB_BIN, "-s", ADB_DEVICE] + list(adb_args)
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def load_channels():
    if not PLAYLIST_FILE.exists():
        return []
    channels = []
    current_name = "Canal"
    current_group = "General"
    current_logo = ""
    for line in PLAYLIST_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line.startswith("#EXTINF:"):
            # Extraer group-title
            if 'group-title="' in line:
                try:
                    current_group = line.split('group-title="')[1].split('"')[0]
                except Exception:
                    pass
            # Extraer tvg-logo
            if 'tvg-logo="' in line:
                try:
                    current_logo = line.split('tvg-logo="')[1].split('"')[0]
                except Exception:
                    pass
            # Extraer nombre
            if "," in line:
                current_name = line.split(",", 1)[1].strip()
        elif line and not line.startswith("#"):
            channels.append({
                "id": len(channels),
                "name": current_name,
                "group": current_group,
                "logo": current_logo,
                "url": line
            })
            current_name = "Canal"
            current_group = "General"
            current_logo = ""
    return channels

CEO_PLAYLIST_FILE = Path("/home/slone/Descargas/TV-76173252_playlist.m3u")

def load_ceo_catalog():
    cats = {
        "futbol": [],
        "motor": [],
        "deportes": [],
        "tdt": [],
        "cine": []
    }
    target_file = CEO_PLAYLIST_FILE if CEO_PLAYLIST_FILE.exists() else PLAYLIST_FILE
    if not target_file.exists():
        return cats

    with open(target_file, errors="ignore") as f:
        cur_name = ""
        cur_logo = ""
        cur_group = ""
        for line in f:
            line = line.strip()
            if line.startswith("#EXTINF:"):
                cur_name = line.split(",", 1)[1].strip() if "," in line else "Canal"
                cur_logo = line.split('tvg-logo="')[1].split('"')[0] if 'tvg-logo="' in line else ""
                cur_group = line.split('group-title="')[1].split('"')[0] if 'group-title="' in line else ""
            elif line and not line.startswith("#"):
                g_up = cur_group.upper()
                item = {
                    "name": cur_name,
                    "logo": cur_logo,
                    "url": line,
                    "group": cur_group
                }
                if ("FUTBOL" in g_up or "LALIGA" in g_up or "CAMPEONES" in g_up) and len(cats["futbol"]) < 60:
                    cats["futbol"].append(item)
                elif ("FORMULA" in g_up or "MOTOGP" in g_up or "MOTOR" in g_up) and len(cats["motor"]) < 40:
                    cats["motor"].append(item)
                elif ("DEPORTES" in g_up or "DAZN" in g_up or "EUROSPORT" in g_up) and len(cats["deportes"]) < 40:
                    cats["deportes"].append(item)
                elif ("TDT" in g_up or "SPAIN" in g_up or "GENERAL" in g_up) and len(cats["tdt"]) < 40:
                    cats["tdt"].append(item)
                elif ("CINE" in g_up or "ESTRENOS" in g_up or "SERIES" in g_up or "ACCIÓN" in g_up) and len(cats["cine"]) < 40:
                    cats["cine"].append(item)

    # Si la lista personal no cubre alguna categoría, rellenar con la lista soberana
    if not cats["tdt"] and PLAYLIST_FILE.exists():
        for ch in load_channels()[:20]:
            cats["tdt"].append(ch)

    return cats

CEO_CATALOG_CACHE = load_ceo_catalog()
CHANNELS_CACHE = load_channels()

class SmartTVHandler(http.server.BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1a. Lista Soberana 100% Legal y Distribuible
        if path in ("/playlist/sovereign.m3u", "/playlist/sovereign.m3u8", "/sovereign.m3u", "/sovereign.m3u8"):
            target = PLAYLIST_SOVEREIGN if PLAYLIST_SOVEREIGN.exists() else PLAYLIST_FILE
            if target.exists():
                content = target.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.apple.mpegurl; charset=utf-8")
                self.send_header("Content-Disposition", 'inline; filename="slone_sovereign_master.m3u8"')
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "Lista Soberana no encontrada")
            return

        # 1b. Lista Privada IPTV de slone con EPG y Timeshift de 7 días
        if path in ("/playlist/private.m3u", "/playlist/private.m3u8", "/private.m3u", "/private.m3u8"):
            if PLAYLIST_PRIVATE.exists():
                content = PLAYLIST_PRIVATE.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.apple.mpegurl; charset=utf-8")
                self.send_header("Content-Disposition", 'inline; filename="slone_private_master.m3u8"')
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "Lista Privada IPTV no encontrada")
            return

        # 1c. Endpoint Global por Defecto (Prioriza Privada si existe, sino Soberana)
        if path in ("/playlist.m3u", "/playlist.m3u8", "/slone.m3u", "/slone.m3u8"):
            target = PLAYLIST_PRIVATE if PLAYLIST_PRIVATE.exists() else PLAYLIST_SOVEREIGN
            if target.exists():
                content = target.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.apple.mpegurl; charset=utf-8")
                self.send_header("Content-Disposition", f'inline; filename="{target.name}"')
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "Lista M3U no encontrada")
            return

        # 2. Catálogo de Canales en JSON para Smart TVs y PWA
        if path == "/api/channels":
            data = json.dumps({"status": "ok", "count": len(CHANNELS_CACHE), "channels": CHANNELS_CACHE}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # 2b. Catálogo VIP del CEO (Fútbol, Motor, TDT, Cine y Apps)
        if path == "/api/tv/ceo_catalog":
            data = json.dumps({"status": "ok", "catalog": CEO_CATALOG_CACHE}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # 3. Estado de la pasarela
        if path in ("/api/status", "/health"):
            st = {
                "status": "online",
                "service": "SLÖNE Sovereign Smart TV Bridge",
                "ip": get_local_ip(),
                "port": PORT,
                "total_channels": len(CHANNELS_CACHE),
                "device": "Xiaomi TV Ready"
            }
            data = json.dumps(st, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # 4. Servir el SLÖNE TV Launcher interactivo
        if path in ("/launcher", "/launcher/", "/tv", "/tv/"):
            launcher_file = WEB_PORTAL_DIR / "launcher" / "index.html"
            if launcher_file.exists():
                content = launcher_file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        # 5. API de Configuración del Launcher (100% Modificable)
        cfg_file = BASE_DIR / "config" / "slone_launcher_config.json"
        if path == "/api/tv/config":
            if cfg_file.exists():
                content = cfg_file.read_bytes()
            else:
                content = b'{"installed_tv_apps": []}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        # 6. Lanzamiento remoto de aplicaciones en la Xiaomi TV vía ADB
        if path.startswith("/api/tv/launch"):
            params = urllib.parse.parse_qs(parsed.query)
            pkg = params.get("package", [""])[0]
            if pkg and re.match(r"^[a-zA-Z0-9_\.]+$", pkg):
                safe_run_adb("shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1")
                resp = json.dumps({"status": "launched", "package": pkg}).encode()
            else:
                resp = b'{"status": "error", "message": "Paquete invalido o ausente"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        # 7. Proyectar el Launcher directamente en la pantalla de la Xiaomi TV
        if path.startswith("/api/tv/open_launcher"):
            my_ip = get_local_ip()
            target_url = f"http://{my_ip}:{PORT}/launcher/"
            safe_run_adb("shell", "am", "force-stop", "com.phlox.tvwebbrowser")
            safe_run_adb("shell", "am", "start", "-n", "com.phlox.tvwebbrowser/.activity.main.MainActivity", "-a", "android.intent.action.VIEW", "-d", target_url)
            resp = json.dumps({"status": "opened_on_tv", "url": target_url}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        # 7b. Abrir URL o búsqueda web en el Navegador Soberano de la TV (TV Bro / Brave / DuckDuckGo)
        if path.startswith("/api/tv/open_url"):
            params = urllib.parse.parse_qs(parsed.query)
            target_url = params.get("url", ["https://search.brave.com"])[0]
            parsed_u = urllib.parse.urlparse(target_url)
            if parsed_u.scheme in ("http", "https"):
                safe_run_adb("shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", target_url, "com.phlox.tvwebbrowser")
                resp = json.dumps({"status": "opened_url", "url": target_url}).encode()
            else:
                resp = b'{"status": "error", "message": "Esquema de URL no permitido"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        # 7c. Lanzar SmartTube sin anuncios con vídeo o búsqueda directa
        if path.startswith("/api/tv/open_smarttube"):
            params = urllib.parse.parse_qs(parsed.query)
            vid = params.get("v", [""])[0]
            if vid and re.match(r"^[a-zA-Z0-9_-]+$", vid):
                yt_url = f"https://www.youtube.com/watch?v={vid}"
                safe_run_adb("shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", yt_url, "org.smarttube.stable")
            else:
                safe_run_adb("shell", "monkey", "-p", "org.smarttube.stable", "-c", "android.intent.category.LAUNCHER", "1")
            resp = json.dumps({"status": "smarttube_opened", "video": vid}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        if path.startswith("/api/tv/search_youtube"):
            params = urllib.parse.parse_qs(parsed.query)
            q = params.get("q", [""])[0]
            if q:
                # Lanzar búsqueda en SmartTube
                search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(q)}"
                safe_run_adb("shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", search_url, "org.smarttube.stable")
            else:
                safe_run_adb("shell", "monkey", "-p", "org.smarttube.stable", "-c", "android.intent.category.LAUNCHER", "1")
            resp = json.dumps({"status": "youtube_search_launched", "query": q}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        # 7c-bis. Alias universal de Cast / ADB Send
        if path.startswith("/api/adb_send"):
            my_ip = get_local_ip()
            target_url = f"http://{my_ip}:{PORT}/launcher/"
            safe_run_adb("shell", "am", "start", "-n", "com.phlox.tvwebbrowser/.activity.main.MainActivity", "-a", "android.intent.action.VIEW", "-d", target_url)
            resp = json.dumps({"status": "cast_ok", "device": ADB_DEVICE, "url": target_url}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        # 7c-ter. Intérprete Soberano de Comandos de Voz hacia Smart TV y Hub
        if path.startswith("/api/tv/voice_command"):
            params = urllib.parse.parse_qs(parsed.query)
            q = params.get("q", [""])[0].lower().strip()
            action_done = "none"

            if any(k in q for k in ["launcher", "menu", "tele", "tv", "inicio"]):
                my_ip = get_local_ip()
                target_url = f"http://{my_ip}:{PORT}/launcher/"
                safe_run_adb("shell", "am", "start", "-n", "com.phlox.tvwebbrowser/.activity.main.MainActivity", "-a", "android.intent.action.VIEW", "-d", target_url)
                action_done = "launcher_opened"
            elif any(k in q for k in ["volumen arriba", "sube volumen", "mas volumen"]):
                safe_run_adb("shell", "input", "keyevent", "24")
                action_done = "volume_up"
            elif any(k in q for k in ["volumen abajo", "baja volumen", "menos volumen"]):
                safe_run_adb("shell", "input", "keyevent", "25")
                action_done = "volume_down"
            elif any(k in q for k in ["mute", "silencio", "mutear"]):
                safe_run_adb("shell", "input", "keyevent", "164")
                action_done = "volume_mute"
            elif any(k in q for k in ["apagar", "suspender", "apaga la tele"]):
                safe_run_adb("shell", "input", "keyevent", "26")
                action_done = "power_toggle"
            else:
                # Búsqueda o reproducción multimedia directa
                search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(q)}"
                safe_run_adb("shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", search_url, "org.smarttube.stable")
                action_done = "media_search"

            resp = json.dumps({
                "status": "voice_executed",
                "query": q,
                "action": action_done,
                "device": ADB_DEVICE
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        # 7d. SLÖNE Ultra-Fast Streaming Proxy (Anti-Bloqueo, Inyección IPTVSmartersPro & CORS)
        if path.startswith("/api/stream/proxy"):
            params = urllib.parse.parse_qs(parsed.query)
            target_url = params.get("url", [""])[0]
            if not target_url:
                self.send_error(400, "URL requerida")
                return

            try:
                # Spoofing de User-Agent oficial de IPTV para saltar bloqueos 403
                headers = {
                    "User-Agent": "IPTVSmartersPro",
                    "Accept": "*/*",
                    "Connection": "keep-alive"
                }
                req = urllib.request.Request(target_url, headers=headers)
                upstream = urllib.request.urlopen(req, timeout=8)

                content_type = upstream.headers.get("Content-Type", "video/mp2t")
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.end_headers()

                # Si es una lista HLS m3u8, reescribir URLs para pasar por el proxy
                if "mpegurl" in content_type or target_url.endswith(".m3u8"):
                    body = upstream.read().decode("utf-8", errors="ignore")
                    lines = []
                    base_url = target_url.rsplit("/", 1)[0]
                    for l in body.splitlines():
                        if l and not l.startswith("#"):
                            full_chunk = l if l.startswith("http") else f"{base_url}/{l}"
                            lines.append(f"/api/stream/proxy?url={urllib.parse.quote(full_chunk)}")
                        else:
                            lines.append(l)
                    self.wfile.write("\n".join(lines).encode("utf-8"))
                    return

                # Flujo continuo para MPEG-TS (.ts)
                while True:
                    chunk = upstream.read(64 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
            except Exception:
                pass
            return

        # 7e. Lanzar stream en reproductor nativo de la Xiaomi TV (TiviMate / Xiaomi Video)
        if path.startswith("/api/tv/play_external"):
            params = urllib.parse.parse_qs(parsed.query)
            stream_url = params.get("url", [""])[0]
            pkg = params.get("package", ["ar.tvplayer.tv"])[0]
            parsed_stream = urllib.parse.urlparse(stream_url)
            if stream_url and parsed_stream.scheme in ("http", "https") and re.match(r"^[a-zA-Z0-9_\.]+$", pkg):
                safe_run_adb("shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", stream_url, "-t", "video/*", pkg)
                resp = json.dumps({"status": "external_play_started", "url": stream_url, "package": pkg}).encode()
            else:
                resp = b'{"status": "error", "message": "Parametros de stream invalidos"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        # 7f. Consulta de Guía EPG en tiempo real (Ahora / Siguiente)
        if path.startswith("/api/epg"):
            params = urllib.parse.parse_qs(parsed.query)
            ch_query = params.get("channel", [""])[0]
            tvg_id = params.get("id", [""])[0]
            now_prog = None
            next_prog = None
            if EPG_MGR:
                now_prog, next_prog = EPG_MGR.now_next(tvg_id=tvg_id, name=ch_query)
            
            res = {
                "channel": ch_query or tvg_id,
                "now": {
                    "title": now_prog["title"],
                    "desc": now_prog["desc"],
                    "start": now_prog["start"].isoformat() if hasattr(now_prog["start"], "isoformat") else str(now_prog["start"]),
                    "stop": now_prog["stop"].isoformat() if now_prog.get("stop") and hasattr(now_prog["stop"], "isoformat") else str(now_prog.get("stop", ""))
                } if now_prog else None,
                "next": {
                    "title": next_prog["title"],
                    "start": next_prog["start"].isoformat() if hasattr(next_prog["start"], "isoformat") else str(next_prog["start"])
                } if next_prog else None
            }
            resp = json.dumps(res, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        # 8. Archivos Estáticos de la Interfaz Web PWA
        rel_path = path.lstrip("/")
        if not rel_path:
            rel_path = "index.html"

        target_file = (WEB_PORTAL_DIR / rel_path).resolve()
        # Seguridad: evitar path traversal
        if WEB_PORTAL_DIR not in target_file.parents and target_file != WEB_PORTAL_DIR / "index.html":
            target_file = WEB_PORTAL_DIR / "index.html"

        if target_file.is_file():
            mime_map = {
                ".html": "text/html; charset=utf-8",
                ".js": "application/javascript; charset=utf-8",
                ".json": "application/json; charset=utf-8",
                ".css": "text/css; charset=utf-8",
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
                ".svg": "image/svg+xml",
                ".ico": "image/x-icon",
                ".mp4": "video/mp4",
                ".webm": "video/webm",
                ".m4v": "video/x-m4v",
                ".m3u8": "application/vnd.apple.mpegurl",
                ".ts": "video/mp2t",
                ".mp3": "audio/mpeg",
                ".aac": "audio/aac",
            }
            content_type = mime_map.get(target_file.suffix.lower(), "application/octet-stream")
            file_size = target_file.stat().st_size
            range_header = self.headers.get("Range")

            # Soporte de peticiones de rango HTTP (206 Partial Content) para vídeo/audio
            if range_header and range_header.startswith("bytes="):
                try:
                    ranges = range_header.split("=")[1].split("-")
                    start = int(ranges[0]) if ranges[0] else 0
                    end = int(ranges[1]) if len(ranges) > 1 and ranges[1] else file_size - 1
                    start = max(0, min(start, file_size - 1))
                    end = max(start, min(end, file_size - 1))
                    length = end - start + 1

                    self.send_response(206)
                    self.send_header("Content-Type", content_type)
                    self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                    self.send_header("Content-Length", str(length))
                    self.send_header("Accept-Ranges", "bytes")
                    self.end_headers()

                    with open(target_file, "rb") as f:
                        f.seek(start)
                        bytes_to_send = length
                        chunk_size = 64 * 1024
                        while bytes_to_send > 0:
                            chunk = f.read(min(chunk_size, bytes_to_send))
                            if not chunk:
                                break
                            self.wfile.write(chunk)
                            bytes_to_send -= len(chunk)
                    return
                except (ConnectionResetError, BrokenPipeError):
                    return
                except Exception:
                    pass

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
            with open(target_file, "rb") as f:
                chunk_size = 64 * 1024
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    try:
                        self.wfile.write(chunk)
                    except (ConnectionResetError, BrokenPipeError):
                        break
            return

        self.send_error(404, "Recurso no encontrado")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path == "/api/tv/config":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            cfg_file = BASE_DIR / "config" / "slone_launcher_config.json"
            try:
                # Validar que es JSON correcto
                json.loads(body.decode("utf-8"))
                cfg_file.write_bytes(body)
                resp = b'{"status": "ok", "message": "Configuracion guardada"}'
            except Exception as e:
                resp = json.dumps({"status": "error", "message": str(e)}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        if path == "/api/boceto/select":
            import base64
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode("utf-8"))
                # Guardar selección JSON
                sel_file = Path("/home/slone/slone_sketch_selection.json")
                sel_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                
                # Si viene imagen en base64 recortada, guardarla
                if "imageBase64" in data and data["imageBase64"]:
                    img_data = data["imageBase64"].split(",")[-1]
                    img_bytes = base64.b64decode(img_data)
                    crop_file = Path("/home/slone/slone_sketch_selected.png")
                    crop_file.write_bytes(img_bytes)
                
                resp = b'{"status": "ok", "message": "Seleccion de boceto guardada correctamente"}'
            except Exception as e:
                resp = json.dumps({"status": "error", "message": str(e)}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        self.send_error(404, "Ruta POST no encontrada")

    def log_message(self, format, *args):
        # Silenciar logs para máximo rendimiento y discreción
        pass

def run():
    # Conexión proactiva no bloqueante con la Smart TV Xiaomi
    try:
        subprocess.Popen([ADB_BIN, "connect", ADB_DEVICE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), SmartTVHandler)
    ip = get_local_ip()
    print(f"👑 [SLÖNE TV HUB] Activo en http://{ip}:{PORT}")
    print(f"📡 Lista M3U para Xiaomi TV: http://{ip}:{PORT}/playlist.m3u")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    run()
