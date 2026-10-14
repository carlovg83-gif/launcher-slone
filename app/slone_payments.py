#!/usr/bin/env python3
"""
SLONE™ PAYMENTS & AUTOMATED SUBSCRIPTION WEBHOOK ENGINE v1.0
══════════════════════════════════════════════════════════════════════════
Maneja la recepción de webhooks de Lemon Squeezy y Stripe para:
1. Validar firmas criptográficas de la pasarela de pago.
2. Emitir y activar automáticamente licencias SLONE Soberanas al recibir el pago.
3. Desactivar licencias en caso de cancelación o reembolso.
4. Generar enlaces de Checkout dinámicos para los 5 planes in-crescendo.
"""

import os
import sys
import json
import time
import hmac
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Importar el gestor de licencias existente
sys.path.insert(0, str(Path(__file__).parent))
try:
    from slone_licensing import LicenseManager, PRICING_PLANS, TIER_PREMIUM, TIER_FREE
except ImportError:
    from app.slone_licensing import LicenseManager, PRICING_PLANS, TIER_PREMIUM, TIER_FREE

# Escudo de seguridad compartido (rate-limit anti-abuso de webhooks)
try:
    from slone_security import RateLimiter
    _WEBHOOK_LIMITER = RateLimiter(60)   # máx. 60 peticiones/min por IP
except Exception:
    _WEBHOOK_LIMITER = None

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "slone_control.json"

class PaymentConfig:
    """Configuración soberana de pasarelas de pago"""
    @staticmethod
    def load():
        if CONFIG_PATH.exists():
            try:
                data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
                return data.get("pasarela_pagos", {})
            except Exception:
                pass
        return {
            "proveedor": "lemonsqueezy",  # lemonsqueezy o stripe
            "lemon_store_id": "TU_STORE_ID",
            "lemon_api_key": "TU_API_KEY_PRIVADA",
            "webhook_secret": "SLONE_WEBHOOK_SECRET_KEY_2026",
            "stripe_public_key": "pk_test_...",
            "stripe_secret_key": "sk_test_...",
            "moneda": "EUR",
            "url_exito": "http://localhost:8765/portal?pago=completado",
            "url_cancelado": "http://localhost:8765/portal?pago=cancelado"
        }

class PaymentGateway:
    def __init__(self):
        self.cfg = PaymentConfig.load()
        self.lic_mgr = LicenseManager()

    def get_checkout_url(self, plan_id: str, customer_email: str = "") -> str:
        """
        Genera la URL de pago para el plan seleccionado.
        Si está en modo demostración/desarrollo, devuelve un enlace seguro simulado.
        """
        plan = next((p for p in PRICING_PLANS if p["id"] == plan_id), PRICING_PLANS[3])
        provider = self.cfg.get("proveedor", "lemonsqueezy")

        # IDs de productos en Lemon Squeezy o Stripe (configurables en slone_control.json)
        variant_ids = self.cfg.get("variant_ids", {
            "day": "https://slone.lemonsqueezy.com/buy/pase-dia",
            "week": "https://slone.lemonsqueezy.com/buy/pase-semana",
            "month": "https://slone.lemonsqueezy.com/buy/suscripcion-mes",
            "year": "https://slone.lemonsqueezy.com/buy/pase-anual",
            "lifetime": "https://slone.lemonsqueezy.com/buy/vitalicio"
        })

        url = variant_ids.get(plan_id, "https://slone.lemonsqueezy.com/buy/pase-anual")
        if customer_email:
            url += f"?checkout[email]={customer_email}"
        return url

    def process_webhook_payload(self, raw_body: bytes, signature_header: str) -> dict:
        """Valida la firma HMAC y procesa eventos de compra completada"""
        raw_secret = (os.environ.get("SLONE_WEBHOOK_SECRET")
                      or self.cfg.get("webhook_secret")
                      or "SLONE_WEBHOOK_SECRET_KEY_2026")
        secret = raw_secret.encode("utf-8")
        computed_sig = hmac.new(secret, raw_body, hashlib.sha256).hexdigest()

        # ── Verificación de firma (bloquea webhooks falsificados) ──
        modo_prod = bool(self.cfg.get("modo_produccion", False))
        provided = (signature_header or "").strip()
        if "=" in provided:                      # formato "sha256=<hex>"
            provided = provided.split("=", 1)[1]
        if provided:
            if not hmac.compare_digest(provided, computed_sig):
                return {"status": "error", "message": "Firma HMAC inválida"}
        elif modo_prod:
            return {"status": "error", "message": "Firma del webhook ausente (modo producción)"}

        try:
            event = json.loads(raw_body.decode("utf-8"))
        except Exception as e:
            return {"status": "error", "message": f"JSON no válido: {e}"}

        event_name = event.get("meta", {}).get("event_name", "") or event.get("type", "")
        custom_data = event.get("meta", {}).get("custom_data", {})
        customer_email = event.get("data", {}).get("attributes", {}).get("user_email", "cliente@slone.tv")
        plan_id = custom_data.get("plan_id", "year")

        if event_name in ["order_created", "subscription_created", "checkout.session.completed"]:
            # Generar clave de licencia única
            key = self.lic_mgr.generate_license_key(plan_id, user_id=customer_email)
            duration = 1 if plan_id == "day" else 7 if plan_id == "week" else 30 if plan_id == "month" else 365 if plan_id == "year" else 0
            
            # Guardar y activar
            self.lic_mgr.save_license(key, TIER_PREMIUM, plan_id, duration)
            return {
                "status": "success",
                "action": "license_issued",
                "key": key,
                "plan": plan_id,
                "email": customer_email,
                "duration_days": duration
            }

        elif event_name in ["subscription_cancelled", "subscription_expired"]:
            self.lic_mgr.set_free_tier()
            return {"status": "success", "action": "license_revoked"}

        return {"status": "ignored", "event": event_name}


class WebhookServerHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/api/webhook/payment":
            self.send_response(404)
            self.end_headers()
            return

        ip = self.client_address[0]
        if _WEBHOOK_LIMITER is not None and not _WEBHOOK_LIMITER.check(ip):
            self.send_response(429)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"error","message":"rate-limit excedido"}')
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except Exception:
            content_length = 0
        if content_length > 1_000_000:      # 1 MB máximo por petición
            self.send_response(413)
            self.end_headers()
            return

        body = self.rfile.read(content_length)
        sig = self.headers.get("X-Signature", "")

        gw = PaymentGateway()
        res = gw.process_webhook_payload(body, sig)

        code = 200 if res.get("status") in ("success", "ignored") else 400
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(res, indent=2).encode("utf-8"))

    def do_GET(self):
        # Sin panel público: solo se atiende el POST de la pasarela.
        self.send_response(405)
        self.end_headers()

    def log_message(self, format, *args):
        # Silenciar logs ruidosos
        pass

def run_webhook_listener(port: int = None, bind: str = "127.0.0.1"):
    """Inicia el servidor de webhooks (bind seguro en 127.0.0.1 por defecto)."""
    cfg = {}
    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8")).get("pasarela_pagos", {})
    except Exception:
        pass
    port = int(port or cfg.get("webhook_puerto", 8766))
    bind = cfg.get("webhook_bind", bind)
    server = HTTPServer((bind, port), WebhookServerHandler)
    print(f"[*] SLONE Payment Webhook escuchando en http://{bind}:{port}/api/webhook/payment")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

if __name__ == "__main__":
    gw = PaymentGateway()
    print("=== SLONE PAYMENT GATEWAY TEST ===")
    url = gw.get_checkout_url("year", "usuario@ejemplo.com")
    print(f"URL de Pago generada para Pase Anual: {url}")
    # Simulación de compra
    dummy_payload = json.dumps({
        "meta": {"event_name": "order_created", "custom_data": {"plan_id": "year"}},
        "data": {"attributes": {"user_email": "vip_user@slone.es"}}
    }).encode("utf-8")
    result = gw.process_webhook_payload(dummy_payload, "")
    print(f"Resultado de emisión automática de licencia: {result}")
