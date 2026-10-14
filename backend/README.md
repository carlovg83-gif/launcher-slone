# SLONE™ Sovereign License Server (backend)

Servidor de **licencias y webhooks** en **Node puro (cero dependencias)**. Firma las
claves con **el mismo algoritmo HMAC-SHA256** que `app/slone_licensing.py`, de modo
que cualquier clave emitida aquí es válida dentro de SLOCAST.

---

## Arranque

```bash
# Opción A — directo
node backend/server.js

# Opción B — npm
npm --prefix backend start

# Opción C — desde la raíz del proyecto
make backend
```

Escucha en `http://127.0.0.1:8766` (configurable con `PORT`). El puerto coincide con
`config/slone_control.json → pasarela_pagos.webhook_puerto`.

## Variables de entorno (opcionales, ver `.env.example`)

| Variable | Descripción | Por defecto |
|---|---|---|
| `PORT` | Puerto de escucha | `8766` |
| `SLONE_ADMIN_TOKEN` | Token para `/api/license/issue` | `cambia-este-token` |
| `SLONE_WEBHOOK_SECRET` | Secreto del webhook (si no, se lee del `slone_control.json`) | — |
| `SLONE_PRODUCTION` | `1` exige firma HMAC en webhooks | `0` |

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Estado del servicio |
| GET | `/api/plans` | Catálogo de planes y precios (EUR) |
| POST | `/api/webhook/payment` | Webhook Lemon Squeezy / Stripe (firma HMAC) |
| POST | `/api/license/verify` | `{ "key": "..." }` valida una licencia |
| POST | `/api/license/issue` | `{ "plan_id", "user_id" }` emite (requiere `X-Admin-Token`) |

## Ejemplos

```bash
# Emitir una licencia (admin)
curl -X POST http://127.0.0.1:8766/api/license/issue \
  -H "X-Admin-Token: $SLONE_ADMIN_TOKEN" \
  -d '{"plan_id":"year","user_id":"cliente@ejemplo.com"}'

# Verificar una licencia
curl -X POST http://127.0.0.1:8766/api/license/verify \
  -d '{"key":"SLONE-334D-C09C-BB16-CBE2"}'

# Simular un pago con firma HMAC válida
BODY='{"meta":{"event_name":"order_created","custom_data":{"plan_id":"month"}}}'
SIG=$(python3 -c "import hmac,hashlib,sys;print(hmac.new(b'SLONE_SOVEREIGN_WEBHOOK_KEY_2026',sys.argv[1].encode(),hashlib.sha256).hexdigest())" "$BODY")
curl -X POST http://127.0.0.1:8766/api/webhook/payment \
  -H "X-Signature: sha256=$SIG" -d "$BODY"
```

## Seguridad

- **Firma HMAC-SHA256** del cuerpo crudo; comparación en tiempo constante.
- **Rate-limit** por IP (60 peticiones/min) y **límite de tamaño** (1 MB).
- El token de administrador se compara en tiempo constante.
- Las licencias emitidas se guardan en `backend/data/licenses.json` (permisos `600`).
- Enlaza por defecto a **127.0.0.1**; para exponerlo usa un proxy inverso con TLS.

> Las licencias emitidas aquí usan la MISMA fórmula que la app. En producción,
> cambia `LICENSE_SECRET` **en ambos sitios** (`app/slone_licensing.py` y aquí) por un
> secreto propio largo y aleatorio, y guárdalo fuera del repositorio.
