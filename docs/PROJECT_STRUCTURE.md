# 🗂️ Estructura del monorepo SLOCAST / SLONE

Mapa del repositorio y **plan de organización incremental**. El objetivo es un monorepo
claro (`app/ backend/ web/ scripts/ …`) **sin romper** la aplicación que ya funciona.

> ⚠️ Decisión de seguridad: **no se han movido** las carpetas existentes (`app/`,
> `config/`, …) porque la app instalada y los lanzadores apuntan a esas rutas. Un
> `git mv` masivo las rompería. La migración es **aditiva y por fases**.

---

## Estructura actual (real)

```
SLOCAST/
├─ app/                 # Aplicación de escritorio (PyQt6) + módulos SLONE
│  ├─ slocast.py        #   entrypoint (reproductor + UI)
│  ├─ slone_auth.py     #   enclave biométrico / gateway PAM
│  ├─ slone_security.py #   ESCUDO anti-intrusión (rate-limit, baneos)
│  ├─ slone_licensing.py#   motor de licencias (HMAC-SHA256)
│  ├─ slone_payments.py #   webhooks Lemon Squeezy / Stripe
│  ├─ slone_vpn.py, slone_epg.py, slone_meta.py, slone_perf.py
│  ├─ xtream_parser.py  #   cliente Xtream Codes
│  └─ web_portal/       #   PWA (index.html, manifest, privacy, terms)
├─ backend/             # ★ NUEVO — Servidor de licencias Node (cero deps)
│  ├─ server.js         #   /health /api/plans /api/webhook/payment …
│  ├─ package.json, README.md, .env.example
│  └─ data/             #   licencias emitidas (git-ignored)
├─ scripts/             # Utilidades de sistema
│  ├─ slone_vault.py    # ★ NUEVO — Bóveda soberana (CLI)
│  ├─ slone_vault.sh    # ★ NUEVO — lanzador de la bóveda
│  ├─ install_pam_service.sh, proteger_carpeta.sh, slone_hardening.sh
│  └─ build_android_aab.sh, publicar_github.sh
├─ config/              # slone_control.json (directiva maestra), pam.d/, logs
├─ prototipo/           # prototipo.html + mockups (a proteger)
├─ corporate/           # estatutos, marca, cap table, term sheet, CIRCE
├─ legal/               # RGPD, términos, registro de marca
├─ docs/                # planes, walkthroughs, BOVEDA.md, SEGURIDAD_IP.md
├─ launchers/           # .desktop de SLOCAST / SLONE / Vault
├─ icons/, branding/    # activos visuales
├─ keystore/            # secretos (a proteger)
├─ legacy/, backups/    # histórico
├─ Makefile             # ★ NUEVO — orquestador
└─ .github/workflows/   # CI/CD (build & release)
```

## Estructura objetivo (migración futura, por fases)

```
SLOCAST/
├─ core/        ← app/ (backend lógico: parser, epg, perf, meta)
├─ ui/          ← interfaz PyQt6
├─ engine/      ← motor de reproducción (MPV/VLC/libmpv)
├─ shield/      ← slone_security.py + slone_vault.py
├─ license/     ← slone_licensing.py + slone_payments.py
├─ backend/     ← servidor Node (ya existe)
├─ web/         ← PWA / portal (mover app/web_portal)
├─ desktop/     ← launchers/, .desktop
├─ tools/       ← scripts/
└─ docs/, corporate/, legal/, ...
```

## Cómo trabajar ya con el monorepo actual

```bash
make help            # ver todos los objetivos
make app             # lanzar la aplicación
make backend         # servidor de licencias
make vault-unlock    # abrir la bóveda
make lint            # comprobar sintaxis Python
```

## Fases de migración (seguras)

1. **Fase A (hecha)**: `backend/` real, `scripts/slone_vault.*`, `Makefile`, docs.
2. **Fase B**: mover `app/web_portal` → `web/` manteniendo **enlaces simbólicos**
   de compatibilidad en la ruta antigua.
3. **Fase C**: dividir `app/` en `core/ ui/ engine/ license/` con re-exportaciones
   (imports antiguos siguen funcionando) y actualizar lanzadores/CI.
4. **Fase D**: mover `scripts/` → `tools/` con alias en `Makefile`.

Cada fase se valida con `make lint` y prueba de arranque antes de la siguiente.
