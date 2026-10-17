# 👑 GEMINI.md · PROTOCOLO DE DESARROLLO Y SEGURIDAD SLÖNE SOVEREIGN OS

Este archivo define las reglas maestras inquebrantables de desarrollo, seguridad y arquitectura para este repositorio.

> 📡 **COORDINACIÓN INTER-ASISTENTES (Single Source of Truth)**:
> Este proyecto mantiene su estado vivo, red y hardware sincronizados en [`PROJECT_STATE.md`](file:///home/slone/slocast%201.0/PROJECT_STATE.md).
> **OBLIGATORIO**: Lee `PROJECT_STATE.md` al iniciar para conocer la IP activa, estado de ADB y servicios. Al finalizar cualquier cambio o solución técnica, actualiza `PROJECT_STATE.md` para que los demás asistentes (Claude Code, Claude Desktop, Antigravity) continúen sin pérdida de contexto.

---

## 🛡️ PUNTO 1 OBLIGATORIO: SEGURIDAD Y BLINDAJE SOBERANO (MÁXIMA PRIORIDAD)

El núcleo del ecosistema SLÖNE es **Zero-Trust** y soberanía técnica total. Ninguna tarea técnica puede comprometer estas directrices:

### 1. Las Cinco Capas de Defensa
1. **Confidencialidad Técnica (Bóveda Criptográfica)**:
   - Todo secreto, clave privada, material legal, dossier o prototipo debe residir en la **Bóveda SLONE** (`SLOCAST_VAULT` vía `gocryptfs`).
   - El acceso exige factor biométrico (huella dactilar `fprintd`), contraseña maestra y 2FA/TPM.
2. **Moat de Producto (Zero-Trust Real)**:
   - Cero telemetría externa. Ningún dato de uso, canal o lista se envía jamás a servidores de terceros ni a analíticas no soberanas.
3. **Propiedad Formal y Protección Intelectual**:
   - Todo código, diseño y especificación pertenece a SLÖNE. Prohibido exponer propiedad intelectual a repositorios públicos o servicios no auditados.
4. **Higiene Operativa de Secretos**:
   - **TERMINANTEMENTE PROHIBIDO** subir o commitear claves criptográficas (`keystore/`, `*.pem`, `*.key`, `*.keystore`), variables de entorno (`config/*.env`), configuración privada (`slone_control.json`) o listas M3U de clientes a Git.
   - Todo fichero sensible debe estar reflejado en `.gitignore` y con permisos restrictivos (`chmod 700` directorios, `chmod 600` ficheros).
5. **Seguridad de Red y Dispositivos**:
   - El servidor TV Hub (`servidor_tv_hub.py`) y el portal PWA deben aplicar aislamiento estricto en la red local (`192.168.1.0/24`), mitigación de fuerza bruta y validación de tokens LAN.

---

## 🏛️ PUNTO 2: ARQUITECTURA TÉCNICA UNIVERSAL DEL ECOSISTEMA

- **Misión Universal**: Eliminar publicidad invasiva, rastreadores y lentitud para cualquier usuario en cualquier pantalla (Smart TV, Android TV, Google TV, Fire TV, webOS, Tizen, PC o móvil).
- **Sin sesgos de marcas ni geografías**: Neutral, abierto a todo tipo de contenidos y dispositivos internacionales.
- **Plataforma de Desarrollo**: Fedora 44 Linux · ThinkPad X390 · Banco de pruebas en `192.168.1.135:5555`.
- **Motor Web/PWA Universal**: `app/web_portal/launcher/index.html` (Multiview 4X, FanAudio Universal, Dock neutral, compatible con cualquier navegador).
- **Motor Android TV Nativo**: `platforms/android/slone-tv-launcher` (Kotlin + Compose for TV, universal para cualquier control remoto y dispositivo Android TV/Fire TV).
- **Daemon TV Hub Local**: `scripts/servidor_tv_hub.py` (Puerto 8765): puente de pruebas local y catálogo.
- **Criptografía Soberana**: Ed25519 y HMAC-SHA256 para validación de licencias y firmas de integridad.

---

## 🧪 PUNTO 3: VALIDACIÓN Y PASE DE CALIDAD ANTES DE GIT

Antes de cualquier confirmación o sincronización:
```zsh
# 1. Compilación limpia sin errores de sintaxis
python3 -m py_compile app/*.py scripts/*.py

# 2. Batería de pruebas unitarias e integración
python3 scripts/test_suite_completa.py

# 3. Validación de criptografía y licencias
python3 scripts/test_licencias.py

# 4. Auditoría de diff (verificar que NADA sensible esté staged)
git status
```

© 2026 SLÖNE ENTERPRISES LLC. TODOS LOS DERECHOS RESERVADOS.
