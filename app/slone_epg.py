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
import re
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
            display_text = dn.text if dn is not None and dn.text else ""
            norm_dn = normalize_name(display_text)
            norm_cid = normalize_name(cid)
            if norm_dn:
                self._name_index.setdefault(norm_dn, cid)
                clean_dn = re.sub(r'(tv|hd|geo|es|cat|uhd)$', '', norm_dn)
                if clean_dn:
                    self._name_index.setdefault(clean_dn, cid)
            if norm_cid:
                self._name_index.setdefault(norm_cid, cid)
                clean_cid = re.sub(r'(tv|hd|geo|es|cat|uhd)$', '', norm_cid)
                if clean_cid:
                    self._name_index.setdefault(clean_cid, cid)

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
        if tvg_id:
            norm_tvg = normalize_name(tvg_id)
            if norm_tvg in self._name_index:
                return self._name_index[norm_tvg]
            clean_tvg = re.sub(r'(tv|hd|geo|es|cat|uhd)$', '', norm_tvg)
            if clean_tvg in self._name_index:
                return self._name_index[clean_tvg]
        if name:
            norm_name = normalize_name(name)
            if norm_name in self._name_index:
                return self._name_index[norm_name]
            clean_name = re.sub(r'(tv|hd|geo|es|cat|uhd)$', '', norm_name)
            if clean_name in self._name_index:
                return self._name_index[clean_name]
            for k, cid in self._name_index.items():
                if len(k) >= 3 and (k in norm_name or norm_name in k):
                    return cid
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
        for i, p in enumerate(progs):
            if p["start"] <= now and (p["stop"] is None or now < p["stop"]):
                current = p
                nxt = progs[i + 1] if i + 1 < len(progs) else None
                break
            if p["start"] > now:
                nxt = p
                if i > 0 and progs[i - 1].get("stop") and (now - progs[i - 1]["stop"]).total_seconds() < 10800:
                    current = progs[i - 1]
                break

        if not current and not nxt and progs:
            last_p = progs[-1]
            if last_p.get("stop") and (now - last_p["stop"]).total_seconds() < 28800:
                current = last_p

        return (current, nxt)

    def has_data(self) -> bool:
        return bool(self.programmes)
