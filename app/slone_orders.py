#!/usr/bin/env python3
"""
SLONE™ ORDERS & WELCOME PACK LOGISTICS ENGINE v1.0
══════════════════════════════════════════════════════════════════════════
Maneja la persistencia y gestión de pedidos, asignación de licencias
y logística física de Welcome Packs de SLONE Global Technologies.
"""

import os
import sys
import json
import time
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
ORDERS_FILE = DATA_DIR / "orders.json"

try:
    from slone_license_core import generate_license_key, DURATION_DAYS
except ImportError:
    from app.slone_license_core import generate_license_key, DURATION_DAYS

PLAN_PRICES = {
    "sports_month": 3.99,
    "sports_year": 39.99,
    "quad_month": 7.99,
    "quad_year": 59.99,
    "royale": 149.00,
    # Legacy fallbacks
    "day": 1.99,
    "week": 4.99,
    "month": 9.99,
    "year": 39.99,
    "lifetime": 79.99
}

class OrderManager:
    """Gestor soberano de pedidos y logística física de SLONE."""

    @staticmethod
    def _load_orders() -> list:
        if not ORDERS_FILE.exists():
            return []
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def _save_orders(orders: list):
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(orders, f, indent=2, ensure_ascii=False)

    @classmethod
    def create_order(cls, plan_id: str, email: str, customer_name: str = "",
                     payment_method: str = "card", shipping_info: dict = None) -> dict:
        """
        Crea un nuevo pedido, genera la clave criptográfica de licencia HMAC-SHA256
        y registra los datos de envío del regalo físico si aplica.
        """
        plan_id = str(plan_id or "quad_year").lower()
        price = PLAN_PRICES.get(plan_id, 59.99)
        license_key = generate_license_key(plan_id, user_id=email)
        duration_days = DURATION_DAYS.get(plan_id, 365)

        order_id = f"SLONE-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Determinar si el plan incluye regalo físico
        requires_shipping = plan_id in ("sports_year", "quad_year", "royale")
        welcome_pack_type = "Sin regalo físico (100% Digital + Cupón 50% Merch)"
        if plan_id == "sports_year":
            welcome_pack_type = "Llavero SLONE grabado en láser + Pegatinas holográficas"
        elif plan_id == "quad_year":
            welcome_pack_type = "Welcome Pack Pro: Pendrive 128GB Metálico + Llavero + Carnet Físico"
        elif plan_id == "royale":
            welcome_pack_type = "Royale Founder Box: Prenda oficial de autor + Carnet Acero + Pendrive 256GB"

        order = {
            "order_id": order_id,
            "created_at": datetime.now().isoformat(),
            "customer_name": customer_name or "Socio SLONE VIP",
            "customer_email": email,
            "plan_id": plan_id,
            "amount_eur": price,
            "currency": "EUR",
            "payment_method": payment_method,
            "payment_status": "PAID",
            "license_key": license_key,
            "duration_days": duration_days,
            "requires_shipping": requires_shipping,
            "welcome_pack_type": welcome_pack_type,
            "shipping_info": shipping_info or {},
            "fulfillment_status": "PENDING_DISPATCH" if requires_shipping else "DIGITAL_DELIVERED",
            "tracking_number": None,
            "carrier": "Correos Express España" if requires_shipping else None
        }

        orders = cls._load_orders()
        orders.insert(0, order)
        cls._save_orders(orders)
        return order

    @classmethod
    def list_orders(cls, limit: int = 50) -> list:
        """Devuelve los pedidos más recientes."""
        return cls._load_orders()[:limit]

    @classmethod
    def get_order(cls, order_id: str) -> dict | None:
        """Busca un pedido por su identificador."""
        for o in cls._load_orders():
            if o.get("order_id") == order_id:
                return o
        return None

    @classmethod
    def update_shipping(cls, order_id: str, tracking_number: str, carrier: str = "Correos Express") -> bool:
        """Actualiza el estado de envío de un Welcome Pack."""
        orders = cls._load_orders()
        updated = False
        for o in orders:
            if o.get("order_id") == order_id:
                o["tracking_number"] = tracking_number
                o["carrier"] = carrier
                o["fulfillment_status"] = "SHIPPED"
                o["shipped_at"] = datetime.now().isoformat()
                updated = True
                break
        if updated:
            cls._save_orders(orders)
        return updated

if __name__ == "__main__":
    test_ord = OrderManager.create_order(
        "quad_year", "ceo@slone.es", "slone CEO",
        payment_method="simulation_vip",
        shipping_info={"address": "Girona Tech Hub", "kit_color": "Obsidiana"}
    )
    print("Pedido de prueba creado con éxito:")
    print(json.dumps(test_ord, indent=2, ensure_ascii=False))
