# 🛡️ Protección de la Propiedad Intelectual de SLOCAST

> Respuesta directa a una pregunta clave: **«¿Qué hago con la idea? ¿En qué se
> diferencia de lo que hacen los competidores?»**

La idea (una plataforma de streaming soberana, zero-trust, sin telemetría) **no se
protege sola**. Se protege con **cinco capas** que se refuerzan entre sí.

---

## Las cinco capas de defensa

| Capa | Protege | Cómo se materializa en el proyecto |
|---|---|---|
| **1. Confidencialidad técnica** | Que nadie *lea* la idea | **Bóveda SLONE** (gocryptfs + huella + contraseña + 2FA + TPM). Ver `docs/BOVEDA.md` |
| **2. Moat de producto** | Que nadie *iguale* el valor | Zero-trust de verdad: cifra listas/credenciales/grabaciones; **cero telemetría** |
| **3. Propiedad formal** | Que la ley respalde | Marca OEPM + Estatutos S.L. (ver `legal/`, `corporate/`) |
| **4. Contratos** | Que terceros queden atados | RGPD, Términos, acuerdos de inversión (ver `legal/`, `corporate/`) |
| **5. Operativa** | Que no se te escape por descuido | Secretos **fuera de Git**, firmas HMAC, ESCUDO anti-intrusión |

---

## 1. Confidencialidad técnica — la Bóveda

Todo el material sensible se guarda **cifrado en reposo**. Sin tus factores de acceso,
el contenido en disco es matemáticamente ilegible, incluso copiando el portátil.

```bash
bash scripts/slone_vault.sh init
bash scripts/slone_vault.sh add prototipo DOSSIER_CEO.md corporate legal keystore
```

## 2. Moat de producto — ¿en qué te diferencias?

| Eje | Competidores típicos | SLOCAST / SLONE |
|---|---|---|
| Privacidad de datos | Venden/usan tus datos | **Cero telemetría**, cero analítica de terceros |
| Credenciales (listas IPTV) | En claro en disco/config | **Cifradas** en la bóveda |
| Grabaciones/EPG | En claro | Cifradas |
| Acceso | Usuario/contraseña | **Huella + contraseña + 2FA + (TPM)** |
| Bloqueo de plataforma | Instalación dependiente | Soberanía: funciona en tu equipo, tus claves |
| Anti-fraude | Licencias débiles | Licencias **firmadas con HMAC-SHA256** |

> Frase de posicionamiento: *«El primer reproductor IPTV **soberano y zero-trust**:
> tus listas, tus credenciales y tus grabaciones cifradas con tu huella, sin que nadie
> más —ni nosotros— pueda leerlas.»*

## 3. Propiedad formal

- **Marca**: solicitud registrada en la OEPM → `legal/REGISTRO_MARCA_OEPM.md`
- **Sociedad**: SLOCAST TECHNOLOGIES, S.L. → `corporate/ESTATUTOS_SOCIALES_SLOCAST_SL.md`
- **Modelo financiero / cap table**: `corporate/CAP_TABLE_Y_MODELO_FINANCIERO.md`
- **Inversión**: `corporate/TERM_SHEET_INVERSION_MA.md`

## 4. Contratos y cumplimiento

- **RGPD**: `legal/POLITICA_PRIVACIDAD_RGPD.md`
- **Términos y condiciones**: `legal/TERMINOS_Y_CONDICIONES.md`
- **Trámites constitutivos**: `docs/TRAMITES_EMPRESA_PRIVACIDAD.md`

## 5. Operativa — higiene de secretos

- 🚫 **Nunca** subas secretos a Git: `app/slone_licensing.py` (LICENSE_SECRET),
  `config/*.env`, `keystore/`, pasarelas de pago.
- ✅ Mete los secretos **dentro de la bóveda** o en variables de entorno.
- ✅ Cambia los secretos por defecto por valores largos y aleatorios antes de producción.
- ✅ Activa el **ESCUDO** de la app (`config/slone_control.json → seguridad`).

---

## Plan de acción recomendado (orden de impacto)

1. **Hoy**: crear la bóveda y meter dentro `prototipo/`, `corporate/`, `legal/`,
   `keystore/` y `app/slone_licensing.py`.
2. **Esta semana**: rotar `LICENSE_SECRET` y `webhook_secret`; activar 2FA en la bóveda.
3. **Este mes**: completar el registro de marca y cerrar el expediente constitutivo.
4. **Continuo**: mantener todo secreto fuera de Git y dentro de la bóveda.

> **Regla de oro:** si `git` o un tercero pueden leerlo, no está protegido. Muévelo a
> la bóveda.
