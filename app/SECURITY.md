# SLONE™ Zero-Trust & Biometric Security Policy

## Filosofía de Seguridad
SLONE OS incorpora principios de seguridad Zero-Trust diseñados para entornos de alta confidencialidad y control absoluto:

1. **Autenticación Biométrica de Hardware**: Integración directa con `fprintd` y sensores biométricos de huella dactilar Synaptics en ThinkPad X390. Ninguna sesión de streaming ni lista de reproducción se desencripta en memoria sin verificación de huella válida.
2. **Aislamiento de Permisos**: Los directorios de configuración y caché operan bajo directivas estrictas POSIX `700` (`rwx------`), impidiendo la lectura por parte de usuarios o demonios no autorizados.
3. **Monocanal Anti-Leak**: El hub de transmisión no almacena credenciales en texto plano ni expone las rutas maestras del proveedor ascendente en la red local.

## Reporte de Vulnerabilidades
Para reportar cualquier incidente o sugerencia de seguridad, contacta directamente con el Enclave de Seguridad de SLONE en `security@slone.global`.
