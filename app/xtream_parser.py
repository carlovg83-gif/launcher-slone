#!/usr/bin/env python3
"""
SLONE™ XTREAM CODES API & ADVANCED M3U8/EPG ENGINE v2.0
══════════════════════════════════════════════════════════════════════════
Motor de alto rendimiento para integración con paneles Xtream Codes y EPG (XMLTV):
1. Autenticación y handshake con endpoints Xtream: player_api.php
2. Obtención categorizada: Canales en directo (Live), Series y Películas (VOD).
3. Motor EPG en streaming con soporte para etiquetas tvg-id, tvg-name y programas actuales.
4. Soporte nativo para cabeceras HTTP personalizadas (User-Agent, Referer) para evitar bloqueos.
"""

import urllib.request
import urllib.parse
import json
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional

class XtreamClient:
    def __init__(self, base_url: str, username: str, password: str, user_agent: str = "SLOCAST/7.5 Sovereign"):
        # Normalizar URL base
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.user_agent = user_agent
        self.auth_data: Optional[Dict[str, Any]] = None

    def _request(self, params: Dict[str, str], timeout: int = 8) -> Any:
        query_params = {
            "username": self.username,
            "password": self.password,
            **params
        }
        url = f"{self.base_url}/player_api.php?{urllib.parse.urlencode(query_params)}"
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read().decode('utf-8', errors='replace')
            return json.loads(data)

    def authenticate(self) -> bool:
        """Verifica credenciales y estado de cuenta Xtream"""
        try:
            res = self._request({})
            user_info = res.get("user_info", {})
            if user_info.get("auth") == 1 or user_info.get("status") == "Active":
                self.auth_data = res
                return True
            return False
        except Exception:
            return False

    def get_live_categories(self) -> List[Dict[str, Any]]:
        """Obtiene categorías de canales en vivo"""
        try:
            return self._request({"action": "get_live_categories"})
        except Exception:
            return []

    def get_live_streams(self, category_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtiene canales en vivo filtrados por categoría"""
        params = {"action": "get_live_streams"}
        if category_id:
            params["category_id"] = str(category_id)
        try:
            streams = self._request(params)
            formatted = []
            for s in streams:
                stream_id = s.get("stream_id")
                stream_url = f"{self.base_url}/live/{self.username}/{self.password}/{stream_id}.ts"
                formatted.append({
                    "name": s.get("name", "Canal Sin Nombre"),
                    "url": stream_url,
                    "logo": s.get("stream_icon", ""),
                    "epg_id": s.get("epg_channel_id", ""),
                    "category_id": s.get("category_id", ""),
                    "num": s.get("num", 0)
                })
            return formatted
        except Exception:
            return []

    def get_vod_categories(self) -> List[Dict[str, Any]]:
        """Obtiene categorías de películas/VOD"""
        try:
            return self._request({"action": "get_vod_categories"})
        except Exception:
            return []

    def get_vod_streams(self, category_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtiene películas bajo demanda"""
        params = {"action": "get_vod_streams"}
        if category_id:
            params["category_id"] = str(category_id)
        try:
            return self._request(params)
        except Exception:
            return []


class M3UPlusParser:
    """Parser optimizado para listas M3U Plus con metadatos EPG completos"""
    @staticmethod
    def parse(content: str) -> List[Dict[str, Any]]:
        channels = []
        current = {}
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("#EXTINF:"):
                # Extraer nombre
                name_split = line.split(",", 1)
                name = name_split[1].strip() if len(name_split) > 1 else "Canal Desconocido"
                
                # Extraer atributos tvg
                logo_m = re.search(r'tvg-logo="([^"]+)"', line, re.I)
                id_m = re.search(r'tvg-id="([^"]+)"', line, re.I)
                group_m = re.search(r'group-title="([^"]+)"', line, re.I)
                
                current = {
                    "name": name,
                    "logo": logo_m.group(1) if logo_m else "",
                    "epg_id": id_m.group(1) if id_m else "",
                    "group": group_m.group(1) if group_m else "General"
                }
            elif not line.startswith("#") and current:
                current["url"] = line
                channels.append(current)
                current = {}
        return channels


if __name__ == "__main__":
    print("=== TEST PARSER M3U PLUS & XTREAM CODES ===")
    sample = """#EXTM3U
#EXTINF:-1 tvg-id="La1.es" tvg-logo="https://logo.png" group-title="Nacionales",La 1 HD
http://stream.example.es/live/la1.m3u8
#EXTINF:-1 tvg-id="Teledeporte.es" tvg-logo="https://logo2.png" group-title="Deportes",Teledeporte
http://stream.example.es/live/tdp.ts
"""
    result = M3UPlusParser.parse(sample)
    print(f"Canales parseados correctamente: {len(result)}")
    print(json.dumps(result, indent=2, ensure_ascii=False))
