# ──────────────────────────────────────────────────────────────
#  SLOCAST / SLONE — Orquestador del monorepo
#  Usa `.RECIPEPREFIX := >` para no depender de tabuladores.
#  Ejecuta:  make help
# ──────────────────────────────────────────────────────────────
.RECIPEPREFIX := >
.DEFAULT_GOAL := help

PY ?= python3
PORT ?= 8766

.PHONY: help app backend backend-dev vault-init vault-unlock vault-lock vault-status \
        vault-twofa vault-recover vault-add vault-doctor vault-migrate vault-restore test-backend test-licencias test lint clean-data secrets

help:
> @echo "SLOCAST / SLONE — objetivos disponibles:"
> @echo "  make app            → inicia la aplicación (app/slocast.py)"
> @echo "  make backend        → inicia el servidor de licencias (Node)"
> @echo "  make backend-dev    → servidor de licencias en modo watch"
> @echo "  make vault-init     → crea la bóveda cifrada (genera clave de recuperación)"
> @echo "  make vault-unlock   → desbloquea la bóveda (huella + contraseña + 2FA)"
> @echo "  make vault-lock     → bloquea la bóveda"
> @echo "  make vault-status   → estado de la bóveda"
> @echo "  make vault-doctor   → diagnóstico: requisitos + estado sin modificar nada"
> @echo "  make vault-migrate  → mueve lo sensible a la bóveda (DRY=1 para simular)"
> @echo "  make vault-restore  → deshace la migración (rollback)"
> @echo "  make vault-twofa    → activa/desactiva el 2FA (make vault-twofa ACTION=enable)"
> @echo "  make vault-add      → mete rutas en la bóveda (make vault-add PATHS='prototipo corporate')"
> @echo "  make vault-recover  → recupera el acceso con la clave física"
> @echo "  make test-backend   → prueba automática del servidor de licencias"
> @echo "  make test-licencias → prueba el núcleo de licencias (anti-falsificación)"
> @echo "  make test           → ejecuta TODAS las pruebas"
> @echo "  make secrets        → rota los secretos de producción (config/secrets.env)"
> @echo "  make lint           → comprueba sintaxis Python"
> @echo "  make clean-data     → borra licencias de prueba generadas"

app:
> $(PY) app/slocast.py

backend:
> PORT=$(PORT) node backend/server.js

backend-dev:
> PORT=$(PORT) node --watch backend/server.js

vault-init:
> bash scripts/slone_vault.sh init

vault-unlock:
> bash scripts/slone_vault.sh unlock

vault-lock:
> bash scripts/slone_vault.sh lock

vault-status:
> bash scripts/slone_vault.sh status

vault-doctor:
> bash scripts/slone_vault.sh doctor

vault-migrate:
> bash scripts/slone_vault.sh migrate $(if $(DRY),--dry-run)

vault-restore:
> bash scripts/slone_vault.sh restore

vault-twofa:
> bash scripts/slone_vault.sh twofa $(or $(ACTION),enable)

vault-add:
> bash scripts/slone_vault.sh add $(PATHS)

vault-recover:
> bash scripts/slone_vault.sh recover

test-backend:
> node --check backend/server.js && echo "backend: sintaxis OK"

test-licencias:
> $(PY) scripts/test_licencias.py

test-suite:
> $(PY) scripts/test_suite_completa.py

test: test-backend test-licencias test-suite
> @echo "✅ Todas las suites de pruebas integradas pasaron con éxito"

secrets:
> bash scripts/rotar_secretos.sh

lint:
> $(PY) -m py_compile app/*.py scripts/*.py && echo "python: sintaxis OK"

clean-data:
> rm -f backend/data/licenses.json && echo "datos de prueba eliminados"
