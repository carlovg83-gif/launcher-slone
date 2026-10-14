# 🛡️ GUÍA CONFIDENCIAL: CREACIÓN DE EMPRESA Y COBROS SOBERANOS (SLONE OS)

> **AVISO DE MÁXIMA PRIVACIDAD**: 
> Este documento reside exclusivamente en el almacenamiento local cifrado de tu ThinkPad X390 (`chmod 700`). 
> **Nunca envíes tu DNI, certificado digital, contraseñas ni cuenta bancaria a ningún chat de IA**. 
> Toda la gestión se realiza directamente entre tú y los organismos oficiales.

---

## 1. Elección de la Estructura Legal en España

Para monetizar legalmente un software o servicio de streaming/IPTV existen dos caminos principales:

### Opción A: Alta como Autónomo (Recomendada para Iniciar en 24h)
- **Coste mensual inicial**: **80 €/mes** durante el primer año (Tarifa Plana de la Seguridad Social).
- **Trámite**: 100% telemático con tu Certificado Digital o DNIe en la Sede Electrónica de la AEAT y Seguridad Social (portal Import@ss).
- **Epígrafe IAE (Hacienda)**: 
  - **763**: *Programación, análisis y diseño de sistemas informáticos*.
  - **845**: *Explotación electrónica por terceros de servicios informáticos y redes de telecomunicación*.
- **VIES / ROI (Registro de Operadores Intracomunitarios)**: Imprescindible marcar la casilla del ROI (Modelo 036) para que Stripe, Google Play o Lemon Squeezy no te apliquen IVA irlandés y puedas operar con inversión del sujeto pasivo (IVA 0% B2B intracomunitario).

### Opción B: Sociedad Limitada (S.L.) — Protección Patrimonial Total
- **Capital social**: Desde **1,00 €** (con la Ley Crea y Crece).
- **Ventaja**: Tu patrimonio personal queda totalmente separado y blindado de la actividad de SLOCAST. Es la forma requerida si vas a vender la compañía en una operación de M&A (adquisición corporativa por 1,2M€ - 1,8M€).
- **Trámite telemático rápido (CIRCE)**: A través de un Punto de Atención al Emprendedor (PAE), se cumplimenta el **DUE (Documento Único Electrónico)** y en 48-72 horas se firma en notaría con costes reducidos por ley (aprox. 150-250 €).

---

## 2. La Cuenta Bancaria de Empresa (100% Online y Rápida)

Para recibir los pagos de las suscripciones necesitas una cuenta con IBAN español (ES):

1. **Revolut Business** (Recomendada para SaaS):
   - Apertura en menos de 24 horas sin comisiones de mantenimiento básicas.
   - IBAN español propio. Tarjetas virtuales para pagar servidores (Hetzner, OVH, Cloudflare).
2. **Qonto España**:
   - Neobanco especializado en pymes y autónomos españoles.
   - Genera los libros contables y conciliación bancaria automáticamente para el modelo 303 de IVA.
3. **Wise Business**:
   - Excelente para conversiones de divisas automáticas si recibes cobros en dólares o libras esterlinas.

---

## 3. Pasarela de Cobro: Lemon Squeezy vs. Stripe

### ¿Por qué Lemon Squeezy / Paddle (Merchant of Record - MoR)?
- **Cero problemas de IVA mundial**: Como Merchant of Record, **ellos son legalmente el vendedor** ante el cliente final. Ellos calculan, cobran y liquidan el IVA en España, Francia, Alemania, Reino Unido, EE.UU., etc.
- **Facturación automática**: El cliente recibe la factura emitida por Lemon Squeezy; a ti te hacen una única transferencia periódica consolidada (payout) libre de complicaciones tributarias individuales.
- **Soporte nativo en SLOCAST**: Ya tienes el motor de webhooks listo en `app/slone_payments.py`.

---

## 4. Checklist para Activar la Facturación Real

1. [ ] Obtén tu **Certificado Digital de la FNMT** (si no lo tienes instalado en tu Firefox en Fedora).
2. [ ] Presenta el **Modelo 036** telemático en la web de la Agencia Tributaria marcando Alta de Actividad (IAE 763) y alta en el **ROI**.
3. [ ] Abre la cuenta en **Revolut Business** o **Qonto**.
4. [ ] Regístrate en **Lemon Squeezy** (o Stripe), introduce el IBAN de tu cuenta bancaria y copia las claves API en `config/slone_control.json`.
5. [ ] ¡Listo! El motor de SLOCAST procesará los cobros y emitirá licencias VIP instantáneamente.
