<div align="center">

# 👑 SLONE™ OS
### Sovereign Media Engine · Low-Latency Sports · Zero-Freeze Core

[![License: Proprietary / Open-Core](https://img.shields.io/badge/License-Proprietary%20%2F%20Open--Core-E3FF00.svg?style=for-the-badge&logo=shield)](LICENSE)
[![Fedora 44 Verified](https://img.shields.io/badge/Fedora%2044-Ready-00E676.svg?style=for-the-badge&logo=fedora)](https://fedoraproject.org)
[![Platform Support](https://img.shields.io/badge/Platform-Linux%20%7C%20Android%20%7C%20Windows%20%7C%20macOS%20%7C%20iOS-white.svg?style=for-the-badge)](https://slone.global)
[![Security Grade](https://img.shields.io/badge/Security-Biometric%20Enclave-E3FF00.svg?style=for-the-badge&logo=fingerprint)](SECURITY.md)

**RULE YOUR STREAM. RULE THE STREET.**

---

</div>

## ⚡ Visión General

**SLONE OS** es el centro de entretenimiento multimedia y streaming en directo concebido para superar las limitaciones de *Kodi*, *VLC* y *TiviMate*. Diseñado con una arquitectura monocanal hiper-resiliente, **elimina los cortes de señal en partidos decisivos de fútbol y carreras de MotoGP**, sincroniza la señal a latencia satélite en tiempo real y permite alternar instantáneamente la pista de audio a **Català**, radio deportiva o versión original.

---

## 🚀 Características Clave

| Capacidad | SLONE OS | Kodi | TiviMate | VLC |
| :--- | :---: | :---: | :---: | :---: |
| **Zero-Freeze Anti-Drop Watchdog** | ✅ **150ms Relay** | ❌ Buffers largos | ❌ Reconexión lenta | ❌ Se cuelga |
| **Instant Multi-Audio (Català / Radio)** | ✅ **1-Clic MPV IPC** | ⚠️ Menús complejos | ⚠️ Requiere reinicio | ⚠️ Desincronizado |
| **Low-Latency Live Mode (<1.5s vs satélite)** | ✅ **Paso Directo** | ❌ 15s - 30s delay | ❌ 8s - 20s delay | ❌ Buffer estándar |
| **1-Click Xiaomi Smart TV Relay** | ✅ **Nativo Cast** | ❌ Requiere plugin | ❌ Solo local | ❌ Inestable |
| **Enclave Biométrico ThinkPad X390** | ✅ **Synaptics Hardware** | ❌ No disponible | ❌ No disponible | ❌ No disponible |
| **Mando Móvil Táctil en Red Local** | ✅ **HTTP /remote** | ⚠️ Requiere Kore | ❌ De pago | ⚠️ Web básica |

---

## 🛠 Instalación y Despliegue

### 1. Fedora Linux (KDE Plasma 6 / ZSH)
```zsh
# Clonar el núcleo seguro
git clone https://github.com/slone-enterprises/slone-os.git
cd slone-os

# Instalar dependencias del sistema con dnf
sudo dnf install -y python3-pyqt6 mpv socat fprintd

# Ejecutar con enclave biométrico
slone
```

### 2. Android & Xiaomi TV
Accede desde el navegador de tu Smart TV o smartphone a la IP de tu servidor local:
```
http://TU_IP_LOCAL:8765/
```
Pulsa en el menú del navegador: **"Instalar aplicación"** o **"Añadir a pantalla de inicio"** para disponer de SLONE OS nativo a pantalla completa.

### 3. Windows & macOS
Descarga los instaladores binarios precompilados de la pestaña [Releases](https://github.com/slone-enterprises/slone-os/releases) de GitHub.

---

## 💎 Ecosistema de Marca: SLONE ATELIER & HARDWARE LABS

SLONE trasciende el software de televisión:
* **The Sovereign Heavyweight Hoodie (500 GSM)**: Algodón orgánico japonés cepillado, corona en hilo flúor y chip criptográfico NFC cosido en la manga.
* **SLONE Precision Remote**: Mando a distancia unibody fresado en aluminio aeroespacial CNC con pantalla micro-OLED.
* **Drop 01 Genesis**: Preventa internacional activa en [https://slone.global/](https://slone.global/).

---

## 🔐 Seguridad y Privacidad

El repositorio y el software cuentan con verificación biométrica obligatoria en hardware ThinkPad y permisos inmutables de archivo. Consulta [SECURITY.md](SECURITY.md) para más detalles.

---

© 2026 SLONE ENTERPRISES LLC. TODOS LOS DERECHOS RESERVADOS.
