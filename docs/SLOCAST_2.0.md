# 🚀 SLOCAST 2.0 — Qué se ha construido y cómo empezar

> Entrega de la **primera fase** del plan «TODO Y MÁS»: bóveda soberana + backend
> de licencias + monorepo + CI/CD + documentación consolidada.
> Los originales **no se han movido** (la app instalada sigue funcionando).

---

## 1. Lo que ya está listo y probado

| Entrega | Ruta | Estado |
|---|---|---|
| 🔐 **Bóveda Soberana** (gocryptfs + huella + contraseña + 2FA + recuperación) | `scripts/slone_vault.py` | ✅ probada (ciclo completo) |
| Lanzador de la bóveda | `scripts/slone_vault.sh`, `launchers/slone-vault.desktop` | ✅ |
| 🩺 Diagnóstico de la bóveda (deps + estado, **no destructivo**) | `make vault-doctor` | ✅ |
| ⚙️ **Backend de licencias** (Node puro) | `backend/server.js` | ✅ probado (HTTP 200/401/403) |
| 🛡️ **Núcleo de licencias** (claves firmadas, anti-falsificación, autocaducables) | `app/slone_license_core.py` | ✅ probado |
| Pruebas automáticas | `backend/test.mjs`, `scripts/test_licencias.py` | ✅ 5 + 8 |
| 🔑 **Rotación de secretos** (sin tocar código) | `scripts/rotar_secretos.sh`, `config/secrets.env.example` | ✅ |
| 📲 **Portal PWA instalable** (service worker + manifest) | `app/web_portal/` | ✅ |
| 🗂️ Orquestador del monorepo | `Makefile` | ✅ |
| 📄 Documentación | `docs/BOVEDA.md`, `docs/SEGURIDAD_IP.md`, `docs/PROJECT_STRUCTURE.md`, `corporate/MASTER_SLOCAST.md` | ✅ |
| 🧱 CI/CD reforzado | `.github/workflows/build_and_release.yml` | ✅ (job `validate`) |
| 🔒 Protección de secretos | `.gitignore` | ✅ |

## 2. Empezar en 3 pasos

```bash
cd ~/Documentos/SLOCAST
make help                 # ver todo lo disponible
make vault-doctor         # comprueba gocryptfs, gpg, huella y TPM antes de empezar

# 1) Crear la bóveda (huella + contraseña nueva). APUNTA la clave de recuperación.
make vault-init

# 2) Meter dentro lo sensible
make vault-unlock
make vault-add PATHS="prototipo DOSSIER_CEO.md corporate legal keystore"
make vault-lock

# 3) Uso diario: abrir y cerrar
make vault-unlock          # huella + contraseña (+2FA)
make vault-lock
```

## 3. Lo que SOLO puedes ejecutar TÚ (contraseña de administrador)

La bóveda, el 1-clic y el 2FA no necesitan permisos. Para las dos capas extra:

```bash
# a) Servicio PAM (contraseña de respaldo sin esperar a la huella)
sudo install -m 0644 config/pam.d/slone /etc/pam.d/slone

# b) Chip TPM 2.0 (opcional, "solo este portátil"). Requiere reiniciar sesión.
sudo usermod -aG tss $USER
```

## 4. Dónde está cada cosa

- Bóveda: cifrado en `~/.vault_slocast/cipher/`, montada en `~/SLOCAST_VAULT`
- Backend: `backend/` (arranque: `make backend`)
- Licencias: núcleo puro en `app/slone_license_core.py` (probado con `make test-licencias`)
- Secretos de producción: `make secrets` → `config/secrets.env` (nunca se sube a Git)
- Docs: `docs/BOVEDA.md` · `docs/SEGURIDAD_IP.md` · `docs/PROJECT_STRUCTURE.md`
- Corporativo consolidado: `corporate/MASTER_SLOCAST.md`

## 5. Seguridad — garantías

- ✅ La contraseña maestra **nunca** se guarda en claro.
- ✅ El secreto 2FA se guarda **cifrado con tu contraseña** (gpg AES-256).
- ✅ Sin tus factores, el contenido en disco es **ilegible** (verificado).
- ✅ Las licencias son **autoverificables y autocaducables**:
  `SLONE-<PLAN>-<AAMMDD>-<FIRMA>`. Una clave **falsificada o caducada se rechaza**
  (verificado: válida → HTTP 200, falsa → HTTP 403; y en la app: válida → PREMIUM, falsa → FREE).
- ✅ El secreto de firma **no está en el código**: se rota con `make secrets`
  (→ `config/secrets.env`, permisos 600, ignorado por Git). App y backend leen
  `SLONE_LICENSE_SECRET`.
- ⚠️ Antes de producción: ejecuta `make secrets` y exporta `SLONE_LICENSE_SECRET`
  **también en la app** (p. ej. en `~/.profile`) para que ambos coincidan.
- ✅ El secreto del **webhook de pago** ya **no** vive en `config/slone_control.json`
  (ese archivo se sube a Git): se lee de `SLONE_WEBHOOK_SECRET`/`make secrets`.

## 6. Checklist de validación final (Fase 8)

Ejecuta esto **tú** cuando la bóveda ya tenga contenido, para confirmar las garantías:

```bash
make vault-doctor      # 1) requisitos OK (gocryptfs, gpg, huella, TPM)
make vault-unlock      # 2) huella + contraseña (+2FA) → monta en ~/SLOCAST_VAULT
ls ~/SLOCAST_VAULT     #    ves tus archivos en claro (solo tras desbloquear)
make vault-lock        # 3) bloquea → la carpeta deja de estar montada
ls ~/SLOCAST_VAULT     #    ya no ves nada (punto de montaje vacío)
file ~/.vault_slocast/cipher/* | head   # 4) en disco solo hay CIPHERTEXT ilegible
make vault-recover     # 5) recupera con la clave física de recuperación
```

- [ ] `vault-doctor`: sin requisitos críticos en rojo.
- [ ] Tras `vault-lock`, el contenido **no** es legible ni con `sudo`.
- [ ] La clave de recuperación (en papel) vuelve a montar la bóveda.

## 7. Pendiente (siguientes fases)

- Migración por fases al layout `core/ ui/ engine/ license/` (ver `docs/PROJECT_STRUCTURE.md`).
- Portal PWA **ya instalable, offline y con onboarding guiado** (service worker + manifest + sección «Cómo empezar»).
- Sellado del TPM a PCRs (medidas de arranque) para máxima exigencia.

## 8. Migración a la bóveda (Fase 7) — reversible

`make vault-migrate` mueve el material sensible **dentro** de la bóveda y deja un
**symlink** en su lugar: con la bóveda montada todo sigue funcionando (build
Android, helpers `corporate/`); al **bloquear**, los symlinks quedan colgando →
datos cifrados inalcanzables. Es **reversible** con `make vault-restore`.

```bash
make vault-migrate DRY=1   # 1) SIMULACIÓN: muestra el plan, no toca nada
make vault-unlock          # 2) desbloquea (huella + contraseña)
make vault-migrate         # 3) migra el material sensible
make vault-lock            # 4) bloquea → los symlinks quedan colgando
```

- Material migrado por defecto: `prototipo/`, `DOSSIER_CEO.md`, `corporate/`,
  `legal/`, `keystore/` (override con `make vault-migrate PATHS="..."`).
- Manifiesto para rollback: `~/.vault_slocast/migration.json` (permisos 600).
- El código (`app/`, `backend/`, `scripts/`, `config/`) **no** se migra: se necesita en runtime.
