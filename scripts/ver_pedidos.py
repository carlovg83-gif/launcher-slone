#!/usr/bin/env python3
"""
SLONE™ CEO ORDERS & LOGISTICS DASHBOARD
══════════════════════════════════════════════════════════════════════════
Panel de control por terminal para inspeccionar pedidos, licencias y envíos
de Welcome Packs de SLONE Global Technologies.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "app"))

try:
    from slone_orders import OrderManager
except ImportError:
    print("❌ Error importando gestor de pedidos.")
    sys.exit(1)

def print_dashboard():
    orders = OrderManager.list_orders(100)
    print("\n" + "═" * 80)
    print("👑 SLONE GLOBAL TECHNOLOGIES · PANEL DE PEDIDOS Y LOGÍSTICA DEL CEO")
    print("═" * 80)
    print(f"Total pedidos registrados: {len(orders)}\n")

    if not orders:
        print("ℹ️  No hay pedidos registrados todavía.")
        print("═" * 80 + "\n")
        return

    print(f"{'ID PEDIDO':<20} {'PLAN':<14} {'IMPORTE':<10} {'ESTADO PAGO':<12} {'LOGÍSTICA / ENVÍO':<20}")
    print("-" * 80)

    for o in orders:
        oid = o.get("order_id", "N/A")
        plan = o.get("plan_id", "N/A")
        amt = f"{o.get('amount_eur', 0):.2f} €"
        pay_st = o.get("payment_status", "PENDING")
        ful_st = o.get("fulfillment_status", "N/A")
        print(f"{oid:<20} {plan:<14} {amt:<10} {pay_st:<12} {ful_st:<20}")
        print(f"   👤 Cliente: {o.get('customer_name')} <{o.get('customer_email')}>")
        print(f"   🔑 Licencia: {o.get('license_key')}")
        if o.get("requires_shipping"):
            ship = o.get("shipping_info", {})
            print(f"   📦 Regalo: {o.get('welcome_pack_type')}")
            print(f"   📍 Dirección: {ship.get('address', 'Pendiente')}, {ship.get('city', '')} ({ship.get('postal_phone', '')})")
            if o.get("tracking_number"):
                print(f"   🚚 Seguimiento: {o.get('tracking_number')} ({o.get('carrier')})")
        print("-" * 80)

    print("\n💡 Opciones disponibles:")
    print("   • Ver pedidos:          python3 scripts/ver_pedidos.py")
    print("   • Marcar envío:         python3 scripts/ver_pedidos.py --ship <ID_PEDIDO> <TRACKING>")
    print("   • Resetear pedidos (0): python3 scripts/ver_pedidos.py --reset\n")

if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--ship":
        order_id = sys.argv[2]
        tracking = sys.argv[3]
        ok = OrderManager.update_shipping(order_id, tracking)
        if ok:
            print(f"✅ Pedido {order_id} actualizado a ENVIADO con tracking {tracking}.")
        else:
            print(f"❌ No se encontró el pedido {order_id}.")
    elif len(sys.argv) >= 2 and sys.argv[1] in ("--reset", "--clear"):
        orders_file = ROOT_DIR / "data" / "orders.json"
        if orders_file.exists():
            import shutil
            shutil.copy2(orders_file, str(orders_file) + ".bak")
            orders_file.write_text("[]\n", encoding="utf-8")
            print("✅ Base de datos de pedidos reseteada a 0. Copia de seguridad guardada en data/orders.json.bak.")
        else:
            print("ℹ️ No existe archivo de pedidos.")
    else:
        print_dashboard()
