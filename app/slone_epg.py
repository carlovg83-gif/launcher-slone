#!/usr/bin/env python3
"""
SLONE™ EPG ENGINE — Guía de programación XMLTV
══════════════════════════════════════════════════════════════════════════
• Descarga y cachea guías XMLTV (incluidas las comprimidas .xml.gz).
• Índice por tvg-id y por nombre normalizado (fallback).
• Consulta "ahora / siguiente" por canal.
Sin dependencias externas: solo stdlib (urllib, gzip, xml.etree).
"""

import gzip
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

# Fuentes públicas gratuitas por país (epgshare01 — agregador XMLTV)
EPG_PRESETS = {
    "🇪🇸 España": "https://epgshare01.online/epgshare01/epg_ripper_ES1.xml.gz",
    "🇬🇧 Reino Unido": "https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz",
    "🇫🇷 Francia": "https://epgshare01.online/epgshare01/epg_ripper_FR1.xml.gz",
    "🇩🇪 Alemania": "https://epgshare01.online/epgshare01/epg_ripper_DE1.xml.gz",
    "🇮🇹 Italia": "https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz",
    "🇵🇹 Portugal": "https://epgshare01.online/epgshare01/epg_ripper_PT1.xml.gz",
}

UA_EPG = "SLOCAST/8.0 EPG"


def normalize_name(s: str) -> str:
    """Normaliza un nombre de canal para emparejamiento tolerante."""
    if not s:
        return ""
    return "".join(ch for ch in s.lower() if ch.isalnum())


def _parse_xmltv_time(value: str) -> Optional[datetime]:
    """Convierte '20260101120000 +0000' (o sin offset) a datetime con tz."""
    if not value:
        return None
    raw = value.strip()
    for fmt in ("%Y%m%d%H%M%S %z", "%Y%m%d%H%M%S%z", "%Y%m%d%H%M%S"):
        try:
            dt = datetime.strptime(raw, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


class EpgManager:
    """Gestiona varias guías XMLTV en memoria."""

    def __init__(self):
        # tvg_id -> lista de programas ordenados por inicio
        self.programmes: Dict[str, List[dict]] = {}
        # nombre normalizado -> tvg_id
        self._name_index: Dict[str, str] = {}
        self.loaded_urls: List[str] = []

    # ── Descarga ────────────────────────────────────────────────
    @staticmethod
    def fetch(url: str, timeout: int = 25) -> Optional[bytes]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA_EPG})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            if data[:2] == b"\x1f\x8b" or url.lower().endswith(".gz"):
                try:
                    data = gzip.decompress(data)
                except OSError:
                    pass
            return data
        except Exception:
            return None

    # ── Análisis ────────────────────────────────────────────────
    def parse(self, xml_bytes: bytes) -> int:
        """Parsea XMLTV y añade sus programas al índice. Devuelve nº de programas."""
        if not xml_bytes:
            return 0
        try:
            root = ET.fromstring(xml_bytes)
        except ET.ParseError:
            return 0

        count = 0
        for ch in root.findall("channel"):
            cid = ch.get("id")
            if not cid:
                continue
            dn = ch.find("display-name")
            if dn is not None and (dn.text or "").strip():
                self._name_index.setdefault(normalize_name(dn.text), cid)

        for prog in root.findall("programme"):
            cid = prog.get("channel")
            start = _parse_xmltv_time(prog.get("start", ""))
            stop = _parse_xmltv_time(prog.get("stop", ""))
            if not cid or not start:
                continue
            title_el = prog.find("title")
            desc_el = prog.find("desc")
            self.programmes.setdefault(cid, []).append({
                "start": start,
                "stop": stop,
                "title": (title_el.text or "").strip() if title_el is not None else "",
                "desc": (desc_el.text or "").strip() if desc_el is not None else "",
            })
            count += 1

        for cid in self.programmes:
            self.programmes[cid].sort(key=lambda p: p["start"])
        return count

    def load_urls(self, urls: List[str]) -> int:
        """Descarga y parsea varias URLs. Devuelve nº total de programas nuevos."""
        total = 0
        for url in urls or []:
            if not url:
                continue
            data = self.fetch(url)
            if data:
                total += self.parse(data)
                if url not in self.loaded_urls:
                    self.loaded_urls.append(url)
        return total

    # ── Consulta ────────────────────────────────────────────────
    def _resolve_id(self, tvg_id: str, name: str) -> Optional[str]:
        if tvg_id and tvg_id in self.programmes:
            return tvg_id
        if name:
            return self._name_index.get(normalize_name(name))
        return None

    def now_next(self, tvg_id: str = "", name: str = "") -> Tuple[Optional[dict], Optional[dict]]:
        """Devuelve (programa_actual, programa_siguiente) para el canal dado."""
        cid = self._resolve_id(tvg_id, name)
        if not cid:
            return (None, None)
        progs = self.programmes.get(cid, [])
        if not progs:
            return (None, None)
        now = datetime.now(timezone.utc)
        current = None
        nxt = None
        for p in progs:
            if p["start"] <= now and (p["stop"] is None or now < p["stop"]):
                current = p
                break
            if p["start"] > now:
                nxt = p
                break
        ref = current["start"] if current else now
        for p in progs:
            if p["start"] > ref:
                nxt = p
                break
        return (current, nxt)

    def has_data(self) -> bool:
        return bool(self.programmes)
