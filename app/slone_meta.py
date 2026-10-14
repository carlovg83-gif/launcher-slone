#!/usr/bin/env python3
"""
SLONE™ AI METADATA ENGINE — Integración DeepSeek
══════════════════════════════════════════════════════════════════════════
• Cliente mínimo de la API DeepSeek (compatible con OpenAI).
• Endpoint: POST https://api.deepseek.com/chat/completions
• Auth: header  Authorization: Bearer <API_KEY>
• Modelos oficiales: deepseek-flash (por defecto) y deepseek-v4-pro.
• Se usa para enriquecer metadatos (sinopsis, año, género) de películas/VOD.
Solo stdlib (urllib, json). La clave se resuelve por prioridad:
  1) parámetro api_key   2) variable $DEEPSEEK_API_KEY
  3) archivo .env (config/deepseek.env  o  app/.env)
"""

import json
import os
import urllib.request
from pathlib import Path
from typing import List, Dict, Optional

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_DEFAULT_MODEL = "deepseek-flash"

# Ubicaciones donde buscar un archivo .env con DEEPSEEK_API_KEY=...
_ENV_CANDIDATES = [
    Path(__file__).resolve().parent.parent / "config" / "deepseek.env",
    Path(__file__).resolve().parent / ".env",
    Path.home() / ".config" / "slocast" / "deepseek.env",
]


def read_env_key() -> str:
    """Devuelve DEEPSEEK_API_KEY desde el entorno o desde un archivo .env."""
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if key:
        return key
    for path in _ENV_CANDIDATES:
        try:
            if not path.exists():
                continue
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() in ("DEEPSEEK_API_KEY", "API_KEY", "DEEPSEEK_KEY"):
                    val = v.strip().strip('"').strip("'")
                    if val:
                        return val
        except Exception:
            continue
    return ""


class DeepSeekError(Exception):
    pass


class DeepSeekClient:
    """Cliente ligero para el endpoint chat/completions de DeepSeek."""

    def __init__(self, api_key: str = "", model: str = DEEPSEEK_DEFAULT_MODEL,
                 base_url: str = DEEPSEEK_BASE_URL, timeout: int = 40):
        self.api_key = (api_key or "").strip() or read_env_key()
        self.model = (model or "").strip() or DEEPSEEK_DEFAULT_MODEL
        self.base_url = (base_url or DEEPSEEK_BASE_URL).rstrip("/")
        self.timeout = timeout

    def available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.4,
             max_tokens: int = 512, think: bool = False,
             reasoning_effort: str = "low", json_mode: bool = False,
             _retry: bool = True) -> str:
        """Envía una conversación y devuelve el texto de la primera respuesta.

        think=False desactiva el modo razonamiento (más rápido y barato para
        metadatos). json_mode fuerza una salida JSON válida.
        """
        if not self.api_key:
            raise DeepSeekError("Falta la API key de DeepSeek.")
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": False,
            # El modo razonamiento se desactiva explícitamente para metadatos.
            "thinking": {"type": "enabled" if think else "disabled"},
        }
        if think:
            payload["reasoning_effort"] = reasoning_effort
        else:
            # temperature solo tiene efecto fuera del modo razonamiento.
            payload["temperature"] = temperature
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        url = f"{self.base_url}/chat/completions"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))
        except urllib.error.HTTPError as e:
            detail = ""
            try:
                detail = e.read().decode("utf-8", errors="replace")[:300]
            except Exception:
                pass
            # Si el servidor rechaza response_format, reintenta sin JSON estricto.
            if json_mode and _retry and e.code in (400, 422):
                return self.chat(messages, temperature=temperature,
                                 max_tokens=max_tokens, think=think,
                                 reasoning_effort=reasoning_effort,
                                 json_mode=False, _retry=False)
            if e.code == 401:
                raise DeepSeekError("Clave API inválida o no autorizada (HTTP 401).") from e
            if e.code == 402:
                raise DeepSeekError("Saldo insuficiente en tu cuenta DeepSeek (HTTP 402).") from e
            if e.code == 429:
                raise DeepSeekError("Demasiadas peticiones / límite alcanzado (HTTP 429).") from e
            raise DeepSeekError(f"HTTP {e.code}: {detail}") from e
        except Exception as e:
            raise DeepSeekError(str(e)) from e

        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError):
            raise DeepSeekError(f"Respuesta inesperada: {str(data)[:200]}")

    def describe_title(self, title: str, kind: str = "película") -> Dict[str, str]:
        """Pide metadatos concisos en español. Devuelve dict con claves conocidas."""
        title = (title or "").strip()
        if not title:
            return {}
        system = (
            "Eres un experto en cine y televisión. Responde SIEMPRE y ÚNICAMENTE "
            "con un objeto JSON válido, sin texto adicional, sin markdown."
        )
        user = (
            f"Proporciona metadatos de la {kind} titulada «{title}». "
            "Devuelve exactamente estas claves JSON: "
            "\"titulo\", \"anio\", \"genero\", \"sinopsis\". "
            "La sinopsis debe tener 1 o 2 frases en español. "
            "Si no conoces el título, deja los campos como cadena vacía."
        )
        raw = self.chat(
            [{"role": "system", "content": system},
             {"role": "user", "content": user}],
            temperature=0.3, max_tokens=500, think=False, json_mode=True,
        )
        return self._parse_json(raw)

    def ping(self) -> str:
        """Prueba mínima de conexión/credenciales. Devuelve la respuesta de texto."""
        return self.chat(
            [{"role": "user", "content": "Responde únicamente con la palabra: OK"}],
            max_tokens=8, think=False,
        )

    @staticmethod
    def _parse_json(raw: str) -> Dict[str, str]:
        text = raw.strip()
        # Recorta posibles vallas de código ```json ... ```
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]
        try:
            obj = json.loads(text)
            if isinstance(obj, dict):
                return {str(k): ("" if v is None else str(v)) for k, v in obj.items()}
        except Exception:
            pass
        return {"sinopsis": raw.strip()}


if __name__ == "__main__":
    import sys
    key = sys.argv[1] if len(sys.argv) > 1 else ""
    c = DeepSeekClient(key)
    print("Clave detectada:", "sí" if c.available() else "no", "· Modelo:", c.model)
    if c.available():
        print(c.describe_title("El Padrino", "película"))
