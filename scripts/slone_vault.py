#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SLONE™ SOVEREIGN VAULT — Bóveda cifrada con acceso biométrico (Zero-Trust).
══════════════════════════════════════════════════════════════════════════════
Protege TODO el material sensible de SLOCAST (prototipo, dossier, corporativo,
legal, secretos y keystore) en una carpeta cifrada que SOLO se abre con:
  1) Huella dactilar   (fprintd)          → quién eres
  2) Contraseña maestra (la escribes TÚ)  → algo que sabes
  3) Código 2FA TOTP    (opcional)        → algo que tienes
  4) Clave sellada al TPM 2.0 (opcional)  → este portátil y solo este

Nada se guarda en claro. La bóveda se monta cifrada (gocryptfs por defecto, que
también cifra los NOMBRES de archivo) y se desmonta al bloquear.

Subcomandos:
  init        Crea la bóveda y genera la clave de recuperación (apúntala).
  unlock      Desbloquea y monta la bóveda (huella → contraseña → 2FA).
  lock        Desmonta y borra cualquier clave de memoria.
  status      Estado actual (montada, motor, 2FA, TPM).
  recover     Recupera el acceso con la clave de recuperación.
  twofa       Activa/desactiva el 2FA TOTP y muestra el secreto.
  tpm         Sella/abre la contraseña al chip TPM 2.0 (opcional).
  add         Mueve rutas dentro de la bóveda (protege archivos).
  migrate     Mueve el material sensible a la bóveda y deja un symlink (reversible).
  restore     Deshace 'migrate' (devuelve todo a su sitio original).
  doctor      Diagnóstico no destructivo (dependencias + estado).
  help        Esta ayuda.

Sin dependencias externas (solo stdlib + gocryptfs/gpg del sistema).
"""

import os
import sys
import json
import base64
import hmac
import hashlib
import struct
import time
import shutil
import getpass
import secrets
import subprocess
from pathlib import Path
from datetime import datetime

# ── Rutas ────────────────────────────────────────────────────────────────────
HOME = Path(os.environ.get("HOME", str(Path.home())))
VAULT_HOME = HOME / ".vault_slocast"
CONFIG_FILE = VAULT_HOME / "vault.json"
CIPHER_DIR = VAULT_HOME / "cipher"
MOUNT_DIR = HOME / "SLOCAST_VAULT"
RECOVERY_GPG = VAULT_HOME / "passphrase.recovery.gpg"
TOTP_GPG = VAULT_HOME / "totp.gpg"
TPM_BLOB = VAULT_HOME / "passphrase.tpm"
VERIFY_GPG = VAULT_HOME / "verify.gpg"
LOG_FILE = VAULT_HOME / "vault.log"
VERIFY_PLAINTEXT = "SLONE-VAULT-OK"

ENGINE = os.environ.get("SLONE_VAULT_ENGINE", "gocryptfs").lower()
RECOVERY_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
BRAND = "🔐 SLONE VAULT"

# ── Utilidades base ───────────────────────────────────────────────────────────
def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def human_ok(msg: str) -> None:
    print(f"  ✅ {msg}")


def human_err(msg: str) -> None:
    print(f"  ⛔ {msg}", file=sys.stderr)


def human_info(msg: str) -> None:
    print(f"  ℹ️  {msg}")


def log(msg: str) -> None:
    try:
        VAULT_HOME.mkdir(parents=True, exist_ok=True)
        line = f"{datetime.now().isoformat(timespec='seconds')} | {msg}\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
        os.chmod(LOG_FILE, 0o600)
    except Exception:
        pass


def load_config() -> dict:
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(cfg: dict) -> None:
    VAULT_HOME.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    os.chmod(CONFIG_FILE, 0o600)


def is_mounted() -> bool:
    """True si el punto de montaje está activo (contiene la bóveda)."""
    try:
        if not MOUNT_DIR.is_dir():
            return False
        # gocryptfs/FUSE: la raíz del montaje aparece en /proc/mounts
        with open("/proc/mounts", encoding="utf-8") as f:
            return str(MOUNT_DIR) in f.read()
    except Exception:
        return False


def run(cmd, **kw):
    return subprocess.run(cmd, **kw)


# ── Passfile temporal (nunca en argv, siempre 600 y borrado) ──────────────────
def _write_tmp_passfile(passphrase: str) -> str:
    fd, path = None, None
    import tempfile
    fd, path = tempfile.mkstemp(prefix=".slone_pf_", dir=str(VAULT_HOME))
    try:
        os.write(fd, (passphrase + "\n").encode())
    finally:
        os.close(fd)
    os.chmod(path, 0o600)
    return path


def _shred(path: str) -> None:
    try:
        if os.path.exists(path):
            size = os.path.getsize(path)
            with open(path, "r+b") as f:
                f.write(b"\0" * size)
                f.flush()
                os.fsync(f.fileno())
            os.remove(path)
    except Exception:
        try:
            os.remove(path)
        except Exception:
            pass


# ── Huella dactilar (fprintd) ─────────────────────────────────────────────────
def current_user() -> str:
    return os.environ.get("USER") or getpass.getuser()


def biometric_available(username: str | None = None) -> bool:
    username = username or current_user()
    if not (have("fprintd-verify") and have("fprintd-list")):
        return False
    try:
        res = run(["fprintd-list", username], capture_output=True, text=True, timeout=8)
        out = (res.stdout or "") + (res.stderr or "")
        return "Fingerprints for user" in out and "#0" in out
    except Exception:
        return False


def fingerprint_gate(username: str | None = None, timeout: int = 30) -> bool:
    """Verifica la huella. No bloquea si el sensor no está disponible."""
    username = username or current_user()
    if not biometric_available(username):
        human_info("Sensor/huella no disponibles — se omite la comprobación biométrica.")
        log(f"BIO skip (no disponible) user={username}")
        return True
    print("  🫱 Coloca tu huella registrada en el sensor...")
    try:
        res = run(["fprintd-verify", username], capture_output=True, text=True, timeout=timeout)
        out = (res.stdout or "") + (res.stderr or "")
        if res.returncode == 0 and "verify-match" in out:
            human_ok("Huella reconocida.")
            log(f"BIO match user={username}")
            return True
        human_err("Huella NO reconocida.")
        log(f"BIO reject user={username} rc={res.returncode}")
        return False
    except subprocess.TimeoutExpired:
        human_err("Tiempo de huella agotado.")
        log(f"BIO timeout user={username}")
        return False
    except Exception as e:
        human_err(f"Error biométrico: {e}")
        return False


# ── 2FA TOTP (RFC 6238, sin dependencias) ─────────────────────────────────────
def _b32(secret: str) -> bytes:
    secret = secret.strip().replace(" ", "").upper()
    pad = "=" * ((8 - len(secret) % 8) % 8)
    return base64.b32decode(secret + pad)


def totp_code(secret: str, t: float | None = None, digits: int = 6, period: int = 30) -> str:
    counter = int((t if t is not None else time.time()) // period)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(_b32(secret), msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = (struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF) % (10 ** digits)
    return str(code).zfill(digits)


def verify_totp(secret: str, code: str, window: int = 1) -> bool:
    now = time.time()
    code = (code or "").strip()
    for w in range(-window, window + 1):
        if hmac.compare_digest(totp_code(secret, now + w * 30), code):
            return True
    return False


def new_totp_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")


# ── Cifrado simétrico con gpg (para la clave de recuperación y el secreto 2FA) ─
def gpg_encrypt(plaintext: str, passphrase: str, outfile: Path) -> None:
    pf = _write_tmp_passfile(passphrase)
    import tempfile
    fd, src = tempfile.mkstemp(prefix=".slone_pt_", dir=str(VAULT_HOME))
    try:
        os.write(fd, plaintext.encode())
        os.close(fd)
        os.chmod(src, 0o600)
        res = run([
            "gpg", "--batch", "--yes", "--symmetric", "--cipher-algo", "AES256",
            "--pinentry-mode", "loopback", "--passphrase-fd", "0",
            "--output", str(outfile), src,
        ], stderr=subprocess.PIPE, stdin=open(pf, "rb"))
        if res.returncode != 0:
            raise RuntimeError("gpg encrypt falló")
        os.chmod(outfile, 0o600)
    finally:
        _shred(pf)
        _shred(src)


def gpg_decrypt(infile: Path, passphrase: str) -> str:
    pf = _write_tmp_passfile(passphrase)
    try:
        res = run([
            "gpg", "--batch", "--yes", "--decrypt",
            "--pinentry-mode", "loopback", "--passphrase-fd", "0",
            "--output", "-", str(infile),
        ], capture_output=True, stdin=open(pf, "rb"))
        if res.returncode != 0:
            return ""
        return res.stdout.decode("utf-8", "replace")
    finally:
        _shred(pf)


def verify_passphrase(passphrase: str) -> bool:
    """Comprueba la contraseña descifrando el archivo testigo."""
    if not VERIFY_GPG.exists():
        return False
    return gpg_decrypt(VERIFY_GPG, passphrase).strip() == VERIFY_PLAINTEXT


def gen_recovery_key(groups: int = 8, size: int = 4) -> str:
    return "-".join("".join(secrets.choice(RECOVERY_ALPHABET) for _ in range(size))
                    for _ in range(groups))


# ── TPM 2.0 (opcional) — sella la contraseña al chip ──────────────────────────
def tpm_available() -> bool:
    if not (have("tpm2_createprimary") and have("tpm2_unseal") and have("tpm2_create")):
        return False
    return os.access("/dev/tpmrm0", os.R_OK | os.W_OK) or os.path.exists("/dev/tpmrm0")


def tpm_seal(passphrase: str) -> bool:
    """Sella la contraseña al TPM. Devuelve True si tuvo éxito."""
    import tempfile
    ctx = tempfile.mkdtemp(prefix=".slone_tpm_", dir=str(VAULT_HOME))
    prim, pub, priv = f"{ctx}/prim.ctx", f"{ctx}/seal.pub", f"{ctx}/seal.priv"
    try:
        if run(["tpm2_createprimary", "-C", "o", "-c", prim],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
            return False
        if run(["tpm2_create", "-C", prim, "-u", pub, "-r", priv, "-i", "-"],
               input=passphrase.encode(), stdout=subprocess.DEVNULL,
               stderr=subprocess.DEVNULL).returncode != 0:
            return False
        # Guardamos el priv (blob sellado) y el pub necesarios para desellar.
        with open(TPM_BLOB, "wb") as f:
            f.write(Path(priv).read_bytes())
        with open(str(TPM_BLOB) + ".pub", "wb") as f:
            f.write(Path(pub).read_bytes())
        os.chmod(TPM_BLOB, 0o600)
        os.chmod(str(TPM_BLOB) + ".pub", 0o600)
        return True
    except Exception:
        return False
    finally:
        shutil.rmtree(ctx, ignore_errors=True)


def tpm_unseal() -> str:
    """Recupera la contraseña sellada en el TPM (o '' si no se puede)."""
    if not TPM_BLOB.exists():
        return ""
    import tempfile
    ctx = tempfile.mkdtemp(prefix=".slone_tpm_", dir=str(VAULT_HOME))
    prim = f"{ctx}/prim.ctx"
    try:
        if run(["tpm2_createprimary", "-C", "o", "-c", prim],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
            return ""
        res = run(["tpm2_load", "-C", prim, "-u", str(TPM_BLOB) + ".pub", "-r", str(TPM_BLOB), "-c", f"{ctx}/obj.ctx"],
                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode != 0:
            return ""
        res = run(["tpm2_unseal", "-c", f"{ctx}/obj.ctx"], capture_output=True)
        if res.returncode != 0:
            return ""
        return res.stdout.decode("utf-8", "replace").strip()
    except Exception:
        return ""
    finally:
        shutil.rmtree(ctx, ignore_errors=True)


# ── Motor de cifrado (gocryptfs por defecto; cryfs alternativo) ────────────────
def engine_binary() -> str:
    return "cryfs" if ENGINE == "cryfs" else "gocryptfs"


def _cryfs_env() -> dict:
    return dict(os.environ, CRYFS_FRONTEND="noninteractive")


def engine_init(passphrase: str) -> None:
    CIPHER_DIR.mkdir(parents=True, exist_ok=True)
    if ENGINE == "cryfs":
        r = run(["cryfs", "--config", str(VAULT_HOME / "cryfs.config"),
                 str(CIPHER_DIR), str(MOUNT_DIR)],
                input=(passphrase + "\n"), text=True, env=_cryfs_env(),
                capture_output=True)
        if r.returncode != 0:
            raise RuntimeError((r.stderr or r.stdout).strip())
    else:
        pf = _write_tmp_passfile(passphrase)
        try:
            r = run(["gocryptfs", "-q", "-init", "--passfile", pf, str(CIPHER_DIR)],
                    capture_output=True, text=True)
            if r.returncode != 0:
                raise RuntimeError((r.stderr or r.stdout).strip())
        finally:
            _shred(pf)


def engine_mount(passphrase: str) -> None:
    MOUNT_DIR.mkdir(parents=True, exist_ok=True)
    if ENGINE == "cryfs":
        r = run(["cryfs", "--config", str(VAULT_HOME / "cryfs.config"),
                 str(CIPHER_DIR), str(MOUNT_DIR)],
                input=(passphrase + "\n"), text=True, env=_cryfs_env(),
                capture_output=True)
        if r.returncode != 0:
            raise RuntimeError((r.stderr or r.stdout).strip())
    else:
        pf = _write_tmp_passfile(passphrase)
        try:
            r = run(["gocryptfs", "-q", "--passfile", pf, str(CIPHER_DIR), str(MOUNT_DIR)],
                    capture_output=True, text=True)
            if r.returncode != 0:
                raise RuntimeError((r.stderr or r.stdout).strip())
        finally:
            _shred(pf)


def engine_unmount() -> bool:
    for um in ("fusermount3", "fusermount"):
        if have(um):
            r = run([um, "-u", str(MOUNT_DIR)], capture_output=True, text=True)
            if r.returncode == 0:
                return True
    if have("umount"):
        r = run(["umount", str(MOUNT_DIR)], capture_output=True, text=True)
        return r.returncode == 0
    return False


def _open_after_unlock() -> None:
    """Abre el gestor de archivos y el prototipo dentro de la bóveda."""
    proto = MOUNT_DIR / "prototipo" / "prototipo.html"
    try:
        if have("xdg-open"):
            run(["xdg-open", str(MOUNT_DIR)], stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
            if proto.exists():
                run(["xdg-open", str(proto)], stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)
            else:
                human_info("Aún no hay 'prototipo/prototipo.html' en la bóveda "
                           "(usa: slone_vault.py add <ruta>).")
    except Exception as e:
        human_info(f"No se pudo abrir el gestor de archivos: {e}")


def count_files() -> int:
    if not is_mounted():
        return 0
    total = 0
    for _, _, files in os.walk(MOUNT_DIR):
        total += len(files)
    return total


# ── Prompts ───────────────────────────────────────────────────────────────────
def prompt_passphrase(confirm: bool = False, label: str = "Contraseña de la bóveda") -> str:
    while True:
        p1 = getpass.getpass(f"  🔑 {label}: ")
        if len(p1) < 8:
            human_err("Debe tener al menos 8 caracteres. Inténtalo de nuevo.")
            continue
        if not confirm:
            return p1
        p2 = getpass.getpass("  🔑 Repite la contraseña: ")
        if p1 != p2:
            human_err("No coinciden. Inténtalo de nuevo.")
            continue
        return p1


# ── Comandos ──────────────────────────────────────────────────────────────────
def cmd_init(args) -> int:
    print(f"{BRAND} · Creando bóveda soberana")
    if CONFIG_FILE.exists():
        human_err("La bóveda ya existe. Usa 'unlock' o 'status'.")
        return 1
    if not have(engine_binary()):
        human_err(f"Falta el motor de cifrado '{engine_binary()}' (instálalo o usa "
                  f"SLONE_VAULT_ENGINE=gocryptfs).")
        return 1
    if not have("gpg"):
        human_err("Falta 'gpg' (necesario para la clave de recuperación).")
        return 1
    VAULT_HOME.mkdir(parents=True, exist_ok=True)
    os.chmod(VAULT_HOME, 0o700)
    if not args.no_bio and not fingerprint_gate():
        return 13
    passphrase = prompt_passphrase(confirm=True, label="Nueva contraseña maestra")
    try:
        engine_init(passphrase)
    except Exception as e:
        human_err(f"Error inicializando el cifrado: {e}")
        return 1
    rec = gen_recovery_key()
    try:
        gpg_encrypt(passphrase, rec, RECOVERY_GPG)
        gpg_encrypt(VERIFY_PLAINTEXT, passphrase, VERIFY_GPG)
    except Exception as e:
        human_err(f"No se pudo crear la clave de recuperación: {e}")
        return 1
    save_config({
        "engine": ENGINE,
        "mountpoint": str(MOUNT_DIR),
        "cipherdir": str(CIPHER_DIR),
        "created": datetime.now().isoformat(timespec="seconds"),
        "two_factor_enabled": False,
        "tpm_enabled": False,
        "owner": current_user(),
        "version": 1,
    })
    os.chmod(CIPHER_DIR, 0o700)
    log("INIT vault created")
    print()
    print("  " + "═" * 60)
    print("  🔑 CLAVE DE RECUPERACIÓN — APÚNTALA EN PAPEL (guárdala segura)")
    print("  " + "═" * 60)
    print(f"     {rec}")
    print("  " + "═" * 60)
    human_info("Sin esta clave NO podrás recuperar la bóveda si olvidas la contraseña.")
    human_ok(f"Bóveda creada: {CIPHER_DIR}")
    human_info("Desbloquéala con:  slone_vault.py unlock")
    return 0


def cmd_unlock(args) -> int:
    print(f"{BRAND} · Desbloqueo")
    if not CONFIG_FILE.exists():
        human_err("No hay bóveda. Crea una con: slone_vault.py init")
        return 1
    if is_mounted():
        human_info("La bóveda ya está montada.")
        if not args.no_open:
            _open_after_unlock()
        return 0
    if not args.no_bio and not fingerprint_gate():
        return 13
    cfg = load_config()
    if getattr(args, "tpm", False) and TPM_BLOB.exists():
        passphrase = tpm_unseal()
        if passphrase:
            human_ok("Contraseña liberada por el chip TPM (solo este equipo).")
        else:
            human_info("El TPM no liberó la contraseña; se pedirá manualmente.")
            passphrase = prompt_passphrase()
    else:
        passphrase = prompt_passphrase()
    if cfg.get("two_factor_enabled") and TOTP_GPG.exists():
        secret = gpg_decrypt(TOTP_GPG, passphrase)
        if not secret:
            human_err("Contraseña incorrecta.")
            log("UNLOCK bad passphrase (2fa)")
            return 13
        code = input("  🔢 Código 2FA (6 dígitos): ").strip()
        if not verify_totp(secret, code):
            human_err("Código 2FA inválido.")
            log("UNLOCK bad 2FA")
            return 13
        human_ok("2FA correcto.")
    try:
        engine_mount(passphrase)
    except Exception as e:
        human_err(f"No se pudo montar (¿contraseña incorrecta?): {e}")
        log("UNLOCK mount failed")
        return 13
    human_ok(f"Bóveda montada en {MOUNT_DIR}  ({count_files()} archivos)")
    log("UNLOCK ok")
    if not args.no_open:
        _open_after_unlock()
    return 0


def cmd_lock(args) -> int:
    if not is_mounted():
        human_info("La bóveda ya estaba bloqueada.")
        return 0
    if engine_unmount():
        human_ok("Bóveda bloqueada y desmontada. Clave borrada de la memoria.")
        log("LOCK ok")
        return 0
    human_err("No se pudo desmontar (¿hay archivos abiertos?).")
    return 1


def cmd_status(args) -> int:
    cfg = load_config()
    print(f"{BRAND} · Estado")
    print(f"  Inicializada : {'sí' if CONFIG_FILE.exists() else 'no'}")
    print(f"  Montada      : {'sí' if is_mounted() else 'no'}   ({MOUNT_DIR})")
    if cfg:
        print(f"  Motor        : {cfg.get('engine', '?')}")
        print(f"  Cifrado      : {cfg.get('cipherdir', '?')}")
        print(f"  2FA TOTP     : {'activo' if cfg.get('two_factor_enabled') else 'inactivo'}")
        print(f"  TPM          : {'activo' if cfg.get('tpm_enabled') else 'inactivo'}")
        print(f"  Creada       : {cfg.get('created', '?')}")
        print(f"  Recuperación : {'disponible' if RECOVERY_GPG.exists() else 'NO'}")
    print(f"  Huella       : {'sí' if biometric_available() else 'no'}")
    if is_mounted():
        print(f"  Archivos     : {count_files()}")
    return 0


def cmd_recover(args) -> int:
    print(f"{BRAND} · Recuperación con clave física")
    if not CONFIG_FILE.exists():
        human_err("No hay bóveda.")
        return 1
    if not RECOVERY_GPG.exists():
        human_err("No existe el archivo de recuperación.")
        return 1
    if is_mounted():
        human_info("La bóveda ya está montada.")
        return 0
    rec = getpass.getpass("  🔑 Clave de recuperación: ").strip()
    passphrase = gpg_decrypt(RECOVERY_GPG, rec)
    if not passphrase:
        human_err("Clave de recuperación incorrecta.")
        log("RECOVER bad key")
        return 13
    if not args.no_bio and not fingerprint_gate():
        return 13
    try:
        engine_mount(passphrase)
    except Exception as e:
        human_err(f"No se pudo montar: {e}")
        return 1
    human_ok("Bóveda recuperada y montada.")
    log("RECOVER ok")
    if not args.no_open:
        _open_after_unlock()
    return 0


def cmd_twofa(args) -> int:
    cfg = load_config()
    if not cfg:
        human_err("No hay bóveda.")
        return 1
    if args.action == "enable":
        if not args.no_bio and not fingerprint_gate():
            return 13
        passphrase = prompt_passphrase()
        if not verify_passphrase(passphrase):
            human_err("Contraseña incorrecta.")
            return 13
        secret = new_totp_secret()
        try:
            gpg_encrypt(secret, passphrase, TOTP_GPG)
        except Exception as e:
            human_err(f"No se pudo guardar el secreto 2FA: {e}")
            return 1
        cfg["two_factor_enabled"] = True
        save_config(cfg)
        uri = (f"otpauth://totp/SLOCAST:{current_user()}?secret={secret}"
               f"&issuer=SLOCAST&algorithm=SHA1&digits=6&period=30")
        print()
        print("  " + "═" * 60)
        print("  🔢 2FA ACTIVADO — añádelo a tu app (Google Authenticator/Authy)")
        print("  " + "═" * 60)
        print(f"     Secreto : {secret}")
        print(f"     URI     : {uri}")
        print("  " + "═" * 60)
        human_ok("Desde ahora se pedirá un código de 6 dígitos al desbloquear.")
        log("2FA enable")
        return 0
    if TOTP_GPG.exists():
        TOTP_GPG.unlink()
    cfg["two_factor_enabled"] = False
    save_config(cfg)
    human_ok("2FA desactivado.")
    log("2FA disable")
    return 0


def cmd_tpm(args) -> int:
    cfg = load_config()
    if not cfg:
        human_err("No hay bóveda.")
        return 1
    if args.action == "enable":
        if not all(have(x) for x in ("tpm2_createprimary", "tpm2_create",
                                     "tpm2_load", "tpm2_unseal")):
            human_err("Faltan herramientas TPM. Ejecuta: sudo dnf install tpm2-tools")
            return 1
        if not args.no_bio and not fingerprint_gate():
            return 13
        passphrase = prompt_passphrase()
        if not verify_passphrase(passphrase):
            human_err("Contraseña incorrecta.")
            return 13
        if not tpm_seal(passphrase):
            human_err("El TPM no pudo sellar la clave (¿permisos de /dev/tpmrm0?).")
            human_info("Ejecuta:  sudo usermod -aG tss $USER   y reinicia sesión.")
            return 1
        cfg["tpm_enabled"] = True
        save_config(cfg)
        human_ok("Contraseña sellada al chip TPM. Desbloqueo rápido: "
                 "slone_vault.py unlock --tpm")
        log("TPM seal ok")
        return 0
    for p in (TPM_BLOB, Path(str(TPM_BLOB) + ".pub")):
        if p.exists():
            p.unlink()
    cfg["tpm_enabled"] = False
    save_config(cfg)
    human_ok("Sellado TPM eliminado (vuelve a usarse la contraseña).")
    log("TPM remove")
    return 0


def cmd_add(args) -> int:
    if not is_mounted():
        human_err("La bóveda no está montada. Usa 'unlock' primero.")
        return 1
    moved = 0
    for src in args.paths:
        srcp = Path(src).expanduser().resolve()
        if not srcp.exists():
            human_err(f"No existe: {src}")
            continue
        target = MOUNT_DIR / srcp.name
        if target.exists():
            human_err(f"Ya existe dentro de la bóveda: {target.name}")
            continue
        try:
            shutil.move(str(srcp), str(target))
            moved += 1
            human_ok(f"Protegido dentro de la bóveda: {srcp.name}")
        except Exception as e:
            human_err(f"Error moviendo {srcp.name}: {e}")
    log(f"ADD {moved} rutas")
    return 0 if moved else 1


def cmd_doctor(args) -> int:
    """Diagnóstico NO destructivo: requisitos del sistema + estado de la bóveda."""
    cfg = load_config()
    checks = []

    def record(label, cond, hint="", critical=False):
        checks.append((label, bool(cond), hint, critical))

    engine = engine_binary()
    record(f"Motor de cifrado ({engine})", have(engine),
           f"instálalo: sudo dnf install {engine}", critical=True)
    record("GPG disponible (secretos cifrados)", have("gpg"),
           "instálalo: sudo dnf install gnupg", critical=True)
    record("Bóveda inicializada", CONFIG_FILE.exists(),
           "ejecútalo: make vault-init")
    if CIPHER_DIR.exists():
        mode = oct(CIPHER_DIR.stat().st_mode & 0o777)
        record(f"Permisos del cifrado ({mode})", (CIPHER_DIR.stat().st_mode & 0o077) == 0,
               "chmod 700 ~/.vault_slocast/cipher")
    else:
        record("Carpeta de cifrado", False, "se crea al hacer 'vault-init'")

    if have("fprintd-verify") and have("fprintd-list"):
        record("Huella dactilar (fprintd) enrolada", biometric_available(),
               "enrola con: fprintd-enroll $USER")
    else:
        record("fprintd instalado", False, "sudo dnf install fprintd fprintd-pam")

    tpm_ok = os.path.exists("/dev/tpmrm0") and os.access("/dev/tpmrm0", os.R_OK | os.W_OK)
    record("TPM 2.0 accesible (/dev/tpmrm0)", tpm_ok,
           "sudo usermod -aG tss $USER   (y vuelve a iniciar sesión)")

    record("Clave de recuperación generada", RECOVERY_GPG.exists(),
           "se crea en 'vault-init'; apúntala en papel")
    if cfg:
        record("2FA TOTP activo", cfg.get("two_factor_enabled"),
               "opcional: slone_vault.py twofa enable")
        record("Sellado TPM activo", cfg.get("tpm_enabled"),
               "opcional: slone_vault.py tpm enable")

    print(f"{BRAND} · Diagnóstico del sistema")
    fails = 0
    for label, cond, hint, critical in checks:
        if cond:
            print(f"  ✅ {label}")
        else:
            print(f"  {'⛔' if critical else '⚠️ '} {label}" + (f"\n        → {hint}" if hint else ""))
            if critical:
                fails += 1

    montada = is_mounted()
    print()
    print(f"  {'🔓' if montada else '🔒'} Bóveda montada : {'sí' if montada else 'no'}   ({MOUNT_DIR})")
    if fails:
        human_err(f"{fails} requisito(s) crítico(s) sin cumplir.")
        return 1
    human_ok("Todos los requisitos críticos están presentes.")
    log("DOCTOR ok" if not fails else f"DOCTOR {fails} fallos criticos")
    return 0


# ── Migración a la bóveda (Fase 7) ─────────────────────────────────────────────
DEFAULT_MIGRATE = ["prototipo", "DOSSIER_CEO.md", "corporate", "legal", "keystore"]
MANIFEST_FILE = VAULT_HOME / "migration.json"


def _load_manifest() -> list:
    try:
        return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_manifest(items: list) -> None:
    VAULT_HOME.mkdir(parents=True, exist_ok=True)
    MANIFEST_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    os.chmod(MANIFEST_FILE, 0o600)


def cmd_migrate(args) -> int:
    """Mueve material sensible DENTRO de la bóveda y deja un symlink en su lugar.

    Con la bóveda montada el layout del repo sigue funcionando (npm/ant, build
    Android, helpers). Al bloquear, los symlinks quedan colgando → los datos
    (cifrados) son inalcanzables. Reversible con 'restore'.
    """
    targets = args.paths if getattr(args, "paths", None) else list(DEFAULT_MIGRATE)
    dry = getattr(args, "dry_run", False)
    print(f"{BRAND} · Migración a la bóveda{'  (SIMULACIÓN)' if dry else ''}")
    if not is_mounted():
        if dry:
            human_info("(dry-run) la bóveda no está montada; se muestra solo el plan previsto.")
        else:
            human_err(f"La bóveda no está montada ({MOUNT_DIR}).")
            human_info("Desbloquéala primero:  make vault-unlock")
            return 1

    try:
        mount_resolved = MOUNT_DIR.resolve()
    except Exception:
        mount_resolved = MOUNT_DIR

    manifest = _load_manifest()
    migrated, skipped, failed = [], [], []
    for src in targets:
        srcp = Path(src).expanduser()
        try:
            abs_src = srcp.resolve()
        except Exception:
            abs_src = srcp
        # Guarda: nunca migrar el punto de montaje ni nada dentro de él.
        if abs_src == mount_resolved or mount_resolved in abs_src.parents:
            human_err(f"Ignorado (ya está dentro de la bóveda): {src}")
            failed.append(src)
            continue
        if srcp.is_symlink():
            human_info(f"Ya migrado (symlink presente): {src}")
            skipped.append(src)
            continue
        if not srcp.exists():
            human_info(f"No existe, se omite: {src}")
            skipped.append(src)
            continue

        name = srcp.name
        target = MOUNT_DIR / name
        if target.exists() or target.is_symlink():
            human_err(f"Ya existe dentro de la bóveda: {target}  (se omite)")
            failed.append(src)
            continue

        if dry:
            human_info(f"[dry-run] {srcp}  →  {target}   (+ symlink {srcp} → {target})")
            migrated.append(src)
            continue
        try:
            shutil.move(str(srcp), str(target))
            os.symlink(str(target), str(srcp))
            manifest.append({"orig": str(srcp), "name": name,
                             "at": datetime.now().isoformat(timespec="seconds")})
            human_ok(f"Protegido: {name}  (symlink en {srcp})")
            migrated.append(src)
        except Exception as e:
            human_err(f"Error moviendo {src}: {e}")
            failed.append(src)

    if not dry:
        _save_manifest(manifest)
    log(f"MIGRATE moved={len(migrated)} skipped={len(skipped)} failed={len(failed)}{' dry' if dry else ''}")
    print()
    print(f"  Resultado: {len(migrated)} {'a migrar' if dry else 'migrados'} · "
          f"{len(skipped)} omitidos · {len(failed)} con incidencia")
    if dry:
        human_info("Simulación: NO se ha modificado nada. Ejecuta sin DRY=1 para migrar.")
    else:
        human_info("Bloquea al terminar:  make vault-lock")
    return 0 if not failed else 1


def cmd_restore(args) -> int:
    """Deshace la migración (rollback): devuelve todo a su ubicación original."""
    manifest = _load_manifest()
    if not manifest:
        human_info("No hay migración registrada (migration.json vacío).")
        return 0
    if not is_mounted():
        human_err(f"La bóveda no está montada ({MOUNT_DIR}); es necesaria para restaurar.")
        human_info("Desbloquéala primero:  make vault-unlock")
        return 1
    print(f"{BRAND} · Restaurando desde la bóveda")
    restored, failed, remaining = 0, 0, []
    for e in manifest:
        orig = Path(e["orig"])
        tgt = MOUNT_DIR / e["name"]
        try:
            if orig.is_symlink():
                orig.unlink()
            if tgt.exists():
                shutil.move(str(tgt), str(orig))
                human_ok(f"Restaurado: {orig}")
                restored += 1
            else:
                human_err(f"Falta dentro de la bóveda: {tgt}")
                failed += 1
                remaining.append(e)
        except Exception as ex:
            human_err(f"Error restaurando {orig}: {ex}")
            failed += 1
            remaining.append(e)
    _save_manifest(remaining)
    log(f"RESTORE restored={restored} failed={failed}")
    return 0 if not failed else 1


# ── CLI ───────────────────────────────────────────────────────────────────────
def main(argv=None) -> int:
    import argparse
    argv = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(
        prog="slone_vault.py",
        description="SLONE Sovereign Vault — bóveda cifrada con acceso biométrico.",
    )
    sub = parser.add_subparsers(dest="cmd")

    def common(sp):
        sp.add_argument("--no-bio", action="store_true", help="omitir huella (pruebas)")
        sp.add_argument("--no-open", action="store_true", help="no abrir carpeta/navegador")

    sub.add_parser("init").add_argument("--no-bio", action="store_true")
    sub.choices["init"].add_argument("--no-open", action="store_true")
    sp = sub.add_parser("unlock"); common(sp)
    sp.add_argument("--tpm", action="store_true", help="liberar contraseña con el chip TPM")
    sub.add_parser("lock")
    sub.add_parser("status")
    sub.add_parser("doctor")
    sp = sub.add_parser("migrate")
    sp.add_argument("paths", nargs="*")
    sp.add_argument("--dry-run", action="store_true")
    sub.add_parser("restore")
    sp = sub.add_parser("recover"); common(sp)
    sp = sub.add_parser("twofa"); common(sp)
    sp.add_argument("action", choices=["enable", "disable"])
    sp = sub.add_parser("tpm"); common(sp)
    sp.add_argument("action", choices=["enable", "disable"])
    sp = sub.add_parser("add"); sp.add_argument("paths", nargs="+")
    sub.add_parser("help")

    args = parser.parse_args(argv)
    if not args.cmd or args.cmd == "help":
        print(__doc__)
        return 0
    dispatch = {
        "init": cmd_init, "unlock": cmd_unlock, "lock": cmd_lock,
        "status": cmd_status, "recover": cmd_recover, "twofa": cmd_twofa,
        "tpm": cmd_tpm, "add": cmd_add, "doctor": cmd_doctor,
        "migrate": cmd_migrate, "restore": cmd_restore,
    }
    return dispatch[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
