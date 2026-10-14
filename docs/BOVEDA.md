# 🔐 Bóveda Soberana SLONE — Guía completa

> Protege **toda** la propiedad intelectual de SLOCAST (prototipo, dossier, material
> corporativo, legal, secretos y keystore) en una carpeta cifrada que **solo** se abre
> en tu portátil, contigo delante. Ni un `cat`, ni un `grep`, ni un disco extraído
> pueden leer el contenido sin tus claves.

---

## 1. Modelo de seguridad (defensa en capas)

La bóveda exige, en este orden, que se cumplan **todas** las capas activas:

| # | Capa | Qué aporta | Dónde vive |
|---|------|-----------|------------|
| 1 | **Cifrado en reposo** (gocryptfs) | El contenido **y los nombres de archivo** están cifrados en disco | `~/.vault_slocast/cipher/` |
| 2 | **Huella dactilar** (fprintd) | Algo que **eres** | sensor Synaptics Prometheus |
| 3 | **Contraseña maestra** | Algo que **sabes** (la escribes tú; nunca se guarda) | tu cabeza |
| 4 | **2FA TOTP** (opcional) | Algo que **tienes** (móvil) | `totp.gpg` (cifrado con la contraseña) |
| 5 | **TPM 2.0** (opcional) | Atado a **este** portátil | `/dev/tpmrm0` |
| 6 | **Permisos 700** + auto-bloqueo | Nadie más del sistema entra | `~/.vault_slocast/` |

**Garantías:**
- ✅ La contraseña **nunca** se almacena en claro (solo el `gocryptfs.conf` cifrado).
- ✅ El secreto 2FA se guarda **cifrado con tu contraseña** (`gpg` AES-256).
- ✅ Sin la contraseña + 2FA, el contenido es indescifrable incluso con `root`.
- ✅ Desmontar (`lock`) expulsa la clave de la memoria.

---

## 2. Requisitos

| Herramienta | Estado | Notas |
|---|---|---|
| `gocryptfs` | ✅ instalado (2.6.1) | motor de cifrado |
| `gpg` | ✅ instalado | clave de recuperación y secreto 2FA |
| `fprintd` + huella | ✅ instalado | capa biométrica |
| `tpm2-tools` | ⚠️ parcial | sellado al chip TPM (opcional) |

> **No hace falta instalar nada para empezar**: `gocryptfs`, `gpg` y `fprintd`
> ya están en tu equipo. El TPM es un extra.

---

## 3. Primeros pasos

```bash
cd ~/Documentos/SLOCAST

# 1) Crear la bóveda (te pedirá huella + nueva contraseña)
bash scripts/slone_vault.sh init
#   → IMPRIME tu CLAVE DE RECUPERACIÓN. Apúntala en papel. Guárdala fuera del equipo.

# 2) Meter dentro lo que quieres proteger
bash scripts/slone_vault.sh unlock
bash scripts/slone_vault.sh add prototipo DOSSIER_CEO.md corporate legal keystore
bash scripts/slone_vault.sh lock

# 3) Uso diario
bash scripts/slone_vault.sh unlock     # huella + contraseña (+2FA si activo)
bash scripts/slone_vault.sh lock       # al terminar
bash scripts/slone_vault.sh status     # consultar estado
```

La bóveda se monta en **`~/SLOCAST_VAULT`** (carpeta normal mientras está abierta;
invisible e ilegible cuando está cerrada).

---

## 4. Comandos

| Comando | Qué hace |
|---|---|
| `init` | Crea la bóveda y **genera la clave de recuperación** |
| `unlock` | Huella → contraseña → 2FA → monta la bóveda y abre el prototipo |
| `lock` | Desmonta y **borra la clave de la memoria** |
| `status` | Montada, motor, 2FA, TPM, nº de archivos |
| `recover` | Recupera el acceso con la **clave de recuperación** |
| `twofa enable\|disable` | Activa/desactiva el 2FA y muestra secreto + URI |
| `tpm enable\|disable` | Sella/elimina la contraseña en el chip TPM 2.0 |
| `add <rutas...>` | Mueve archivos/carpetas **dentro** de la bóveda |
| `migrate [rutas]` | **Fase 7**: mueve material sensible del repo a la bóveda y deja symlinks |
| `restore` | Deshace la migración (rollback completo con manifiesto) |
| `doctor` | Diagnóstico no destructivo: requisitos, permisos, TPM, 2FA, montaje |

Opciones útiles: `--no-open` (no abrir el gestor de archivos), `--tpm` (unlock por TPM),
`--no-bio` (omitir huella, para pruebas).

### Lanzador de un clic

Hay un icono en `launchers/slone-vault.desktop`. Para instalarlo en tu menú:

```bash
cp launchers/slone-vault.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications 2>/dev/null || true
```

---

## 5. La clave de recuperación (LEE ESTO)

Al hacer `init` se genera una clave tipo `ABCD-EFGH-…`. **Es el único modo** de abrir
la bóveda si olvidas la contraseña. Se guarda cifrada en
`~/.vault_slocast/passphrase.recovery.gpg`.

- ✍️ **Escríbela en papel** y guárdala en un lugar físico seguro (caja, caja fuerte).
- 🚫 No la guardes en el mismo equipo ni en la nube sin cifrar.
- 🔁 Si cambias la contraseña, vuelve a ejecutar `init` NO: usa el flujo de `passwd`
  (o restaura con `recover` y regenera).

> **Prueba mental:** un ladrón con tu portátil y tu huella grabada, sin la
> contraseña ni la clave de recuperación, obtiene **datos aleatorios**.

## 6. 2FA (doble factor)

```bash
bash scripts/slone_vault.sh twofa enable
#   → muestra un SECRETO y una URI otpauth://
```

Añádelo a **Google Authenticator** o **Authy** (escaneando la URI o metiendo el secreto
a mano). A partir de ahí, `unlock` pedirá los 6 dígitos. El secreto 2FA se guarda
**cifrado con tu contraseña**, así que sin ella es inservible.

Desactivar: `bash scripts/slone_vault.sh twofa disable`.

## 7. TPM 2.0 (opcional, «solo este portátil»)

Tu equipo tiene chip TPM 2.0 (`/dev/tpm0`). Para usarlo, primero autoriza tu usuario
en el grupo `tss` (lo ejecutas TÚ una sola vez, con tu contraseña de administrador):

```bash
sudo usermod -aG tss $USER      # desconecta y vuelve a entrar después
```

Luego:

```bash
bash scripts/slone_vault.sh tpm enable    # sella la contraseña al chip
bash scripts/slone_vault.sh unlock --tpm  # huella + liberación por TPM (+2FA)
```

> El sellado liga la contraseña a **este chip concreto**. Si extremos el uso,
> podría añadirse sellado a PCRs (medidas de arranque) para que falle si alguien
> manipula el firmware. Se deja documentado como siguiente paso.

## 8. ¿Qué conviene guardar dentro?

Recomendado: `prototipo/`, `DOSSIER_CEO.md`, `corporate/`, `legal/`, `keystore/`,
`app/slone_licensing.py` (secreto de licencias) y cualquier volcado de BD o `.env`.

```bash
bash scripts/slone_vault.sh add app/slone_licensing.py config/deepseek.env.example
```

## 9. ¿En qué se diferencia de «poner los HTML en el escritorio»?

| Enfoque | Nombres cifrados | Contenido cifrado | Biométrico | 2FA | Atado al equipo |
|---|---|---|---|---|---|
| ZIP con contraseña | ❌ (a veces) | ✅ | ❌ | ❌ | ❌ |
| Carpeta oculta | ❌ | ❌ | ❌ | ❌ | ❌ |
| Disco externo | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Bóveda SLONE** | ✅ | ✅ | ✅ | ✅ | ✅ (TPM) |

Poner la idea en un ZIP o en una carpeta oculta **no la protege**: se abre en segundos,
se lista, se copia y se filtra. La bóveda SLONE aporta **zero-trust de verdad**:
sin tus factores, los datos son ruido matemático.

## 10. Recuperación y solución de problemas

| Síntoma | Causa / solución |
|---|---|
| «La bóveda ya está montada» | Ya está abierta; `lock` para cerrar |
| «No se pudo montar (¿contraseña incorrecta?)» | Revisa la contraseña; usa `recover` con la clave física |
| «No se pudo desmontar» | Cierra archivos/ventanas abiertos y reintenta |
| Olvidé la contraseña | `bash scripts/slone_vault.sh recover` con la clave de recuperación |
| Perdí la clave de recuperación **y** la contraseña | Irrecuperable por diseño (aún queda el TPM si lo sellaste) |
| TPM no sella | Falta el grupo `tss` (ver §7) |

**¿Dónde está todo?**
- Cifrado: `~/.vault_slocast/cipher/`
- Config: `~/.vault_slocast/vault.json`
- Recuperación: `~/.vault_slocast/passphrase.recovery.gpg`
- 2FA: `~/.vault_slocast/totp.gpg`
- Registro: `~/.vault_slocast/vault.log`
- Punto de montaje: `~/SLOCAST_VAULT`

## 11. Motor alternativo: CryFS (oculta también los tamaños)

Por defecto se usa **gocryptfs** (rápido, robusto, cifra nombres). Si quieres ocultar
también **el tamaño y la estructura** de las carpetas, puedes crear la bóveda con CryFS:

```bash
SLONE_VAULT_ENGINE=cryfs bash scripts/slone_vault.sh init
```

> CryFS oculta más metadatos a cambio de algo menos de velocidad. Elige un motor **al
> crear** la bóveda; no se pueden mezclar.

## 12. Migración al repo — Fase 7 (simbiosis bóveda + repo)

`migrate` mueve el material sensible **dentro** de la bóveda y deja un **symlink** en
su lugar. Resultado: con la bóveda montada, el repo funciona exactamente igual que antes
(builds Android, helpers `corporate/`, referencias en código). Al **bloquear**, los
symlinks quedan colgantes — los datos cifrados son inalcanzables.

### Flujo completo

```bash
# 1) Simular (no toca nada)
make vault-migrate DRY=1

# 2) Inicializar + desbloquear la bóveda (primera vez)
make vault-init     # pedirá huella + nueva contraseña → apunta la clave de recuperación
make vault-unlock

# 3) Migrar el material sensible
make vault-migrate
#   Por defecto: prototipo/, DOSSIER_CEO.md, corporate/, legal/, keystore/
#   Override:  make vault-migrate PATHS="prototipo corporate"

# 4) Bloquear — los symlinks quedan colgantes, datos ilegibles en disco
make vault-lock

# ── Rollback completo ────────────────────────────────────────────────────────
make vault-unlock
make vault-restore   # devuelve todo a su lugar original, elimina symlinks
make vault-lock
```

### Garantías de la migración

| Aspecto | Garantía |
|---|---|
| **Rollback** | `migration.json` (permisos 600) registra cada movimiento |
| **Idempotente** | Re-ejecutar omite los ya migrados (symlinks detectados) |
| **Seguridad Git** | `.gitignore` protege estas rutas: nunca acabarán en un commit |
| **Build Android** | `keystore/slone.keystore` sigue accesible vía symlink (bóveda montada) |
| **Código** | `app/`, `backend/`, `scripts/`, `config/` **no** se migran (runtime) |

> El manifiesto de rollback está en `~/.vault_slocast/migration.json`.

