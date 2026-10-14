#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════
# SLÖNE™ SOVEREIGN SMART TV & LAN HUB
# ══════════════════════════════════════════════════════════════════════════
# Servidor autónomo de alta velocidad para Xiaomi TV, Android TV, TiviMate y Web
# ══════════════════════════════════════════════════════════════════════════

import http.server
import json
import os
import socket
import sys
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PLAYLIST_FILE = BASE_DIR / "playlists" / "slone_sovereign_master.m3u8"
WEB_PORTAL_DIR = BASE_DIR / "app" / "web_portal"
PORT = 8765

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

        # 1. Lista Maestra M3U para TiviMate, VLC, IPTV Smarters en Xiaomi TV
        if path in ("/playlist.m3u", "/playlist.m3u8", "/slone.m3u", "/slone.m3u8"):
            if PLAYLIST_FILE.exists():
                content = PLAYLIST_FILE.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.apple.mpegurl; charset=utf-8")
                self.send_header("Content-Disposition", 'inline; filename="slone_sovereign_master.m3u8"')
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
            if pkg:
                adb_bin = "/home/slone/.local/bin/adb"
                os.system(f"{adb_bin} -s 192.168.1.135:5555 shell monkey -p {pkg} -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1 &")
                resp = json.dumps({"status": "launched", "package": pkg}).encode()
            else:
                resp = b'{"status": "error", "message": "Falta el paquete"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        # 7. Proyectar el Launcher directamente en la pantalla de la Xiaomi TV
        if path.startswith("/api/tv/open_launcher"):
            adb_bin = "/home/slone/.local/bin/adb"
            my_ip = get_local_ip()
            target_url = f"http://{my_ip}:{PORT}/launcher/"
            os.system(f"{adb_bin} -s 192.168.1.135:5555 shell am force-stop com.phlox.tvwebbrowser >/dev/null 2>&1")
            os.system(f"{adb_bin} -s 192.168.1.135:5555 shell am start -a android.intent.action.VIEW -d '{target_url}' com.phlox.tvwebbrowser >/dev/null 2>&1 &")
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
            adb_bin = "/home/slone/.local/bin/adb"
            os.system(f"{adb_bin} -s 192.168.1.135:5555 shell am start -a android.intent.action.VIEW -d '{target_url}' com.phlox.tvwebbrowser >/dev/null 2>&1 &")
            resp = json.dumps({"status": "opened_url", "url": target_url}).encode()
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
            adb_bin = "/home/slone/.local/bin/adb"
            if vid:
                yt_url = f"https://www.youtube.com/watch?v={vid}"
                os.system(f"{adb_bin} -s 192.168.1.135:5555 shell am start -a android.intent.action.VIEW -d '{yt_url}' org.smarttube.stable >/dev/null 2>&1 &")
            else:
                os.system(f"{adb_bin} -s 192.168.1.135:5555 shell monkey -p org.smarttube.stable -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1 &")
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
            adb_bin = "/home/slone/.local/bin/adb"
            if q:
                # Lanzar búsqueda en SmartTube
                search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(q)}"
                os.system(f"{adb_bin} -s 192.168.1.135:5555 shell am start -a android.intent.action.VIEW -d '{search_url}' org.smarttube.stable >/dev/null 2>&1 &")
            else:
                os.system(f"{adb_bin} -s 192.168.1.135:5555 shell monkey -p org.smarttube.stable -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1 &")
            resp = json.dumps({"status": "youtube_search_launched", "query": q}).encode()
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
                ".svg": "image/svg+xml",
                ".ico": "image/x-icon",
            }
            content_type = mime_map.get(target_file.suffix.lower(), "application/octet-stream")
            content = target_file.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
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
        self.send_error(404, "Ruta POST no encontrada")

    def log_message(self, format, *args):
        # Silenciar logs para máximo rendimiento y discreción
        pass

def run():
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
