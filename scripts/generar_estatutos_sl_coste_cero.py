#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════
SLONE™ CORP — GENERADOR DE ACTA DE APORTACIÓN DE SOFTWARE A COSTE CERO
══════════════════════════════════════════════════════════════════════════════
Genera el documento jurídico formal para la Notaría y el Registro Mercantil
conforme al artículo 63 de la Ley de Sociedades de Capital (LSC) y la Ley 18/2022
(Crea y Crece). Permite dotar a la sociedad de 50.000 € de Fondos Propios
aportando el código fuente propietario de SLONE sin desembolsar dinero en efectivo.
"""

import os
import sys
from datetime import datetime

DOCS_DIR = "/home/slone/slocast 1.0/docs"
OUT_FILE = os.path.join(DOCS_DIR, "ESCRITURA_APORTACION_SOFTWARE_SLONE.md")

DOCUMENT_CONTENT = f"""# ACTA NOTARIAL DE VALORACIÓN Y APORTACIÓN NO DINERARIA DE SOFTWARE
## CONSTITUCIÓN DE SOCIEDAD DE RESPONSABILIDAD LIMITADA "SLONE ENTERPRISE S.L."
**Conforme a los Artículos 63, 64 y concordantes del Texto Refundido de la Ley de Sociedades de Capital (RDL 1/2010)**
**Marco Legal**: Ley 18/2022, de 28 de septiembre, de creación y crecimiento de empresas.

---

### COMPARECE:
**Don [slone]**, mayor de edad, de nacionalidad española, con DNI/NIE número [__________], y con domicilio a estos efectos en la provincia de Girona, Catalunya, España.

---

### MANIFIESTA Y HACE CONSTAR:

**PRIMERO. — CONDICIÓN DE CREADOR Y TITULAR DE LOS DERECHOS DE AUTOR**  
Que el compareciente es el autor exclusivo, desarrollador y legítimo propietario de la totalidad de los derechos morales y de explotación económica sobre la creación intelectual denominada **"SLÖNE SOVEREIGN GLOBAL MEDIA ENGINE"** (anteriormente desarrollada bajo el nombre en clave Slocast), que comprende el código fuente, la arquitectura de sistemas, las librerías nativas compiladas y la documentación técnica asociada.

**SEGUNDO. — DESCRIPCIÓN DEL ACTIVO INTANGIBLE APORTADO**  
El activo aportado a la sociedad en formación comprende los siguientes módulos informáticos cerrados y operativos:
1. **Núcleo de Criptografía Asimétrica Ed25519 y Validación Hardware Node-Locked**: Módulo de alta seguridad que enlaza la licencia de uso a la huella digital hardware (`/etc/machine-id` + DMI UUID + MAC) con imposibilidad matemática de falsificación offline.
2. **Motor de Transmisión Tolerante a Fallos Zero-Freeze**: Arquitectura de demultiplexación de vídeo en memoria optimizada con consumo inferior a 128 MB de búfer RAM.
3. **Módulo Multiview Stadium™ 4X**: Sistema de sincronización de cuatro cuadrantes de emisión simultáneos a 60 FPS con alternancia de audio multicanal en caliente.
4. **Sistema Radio Dual Audio-Sync**: Algoritmo de corrección de desfase temporal (*Clock Drift Compensation*) para acoplar comentarios de radio deportiva en directo con transmisiones de vídeo por streaming.
5. **Binario Nativo Compilado x86_64 y Paquetes de Distribución**: Versión ejecutable cerrada ELF de 64 bits para sistemas Linux/Fedora y arquitectura multiplataforma.

**TERCERO. — VALORACIÓN ECONÓMICA ASIGNADA**  
De conformidad con lo dispuesto en el artículo 63 de la Ley de Sociedades de Capital, no resultando preceptivo el informe de experto independiente designado por el Registrador Mercantil al tratarse de una Sociedad de Responsabilidad Limitada, el socio fundador asigna a la totalidad de los derechos de propiedad intelectual del software antes descrito un valor razonable y justificado de:

> **CINCUENTA MIL EUROS (50.000,00 €)**

Dicha valoración se sustenta en:
- Más de 1.200 horas de arquitectura de software, desarrollo informático y auditoría de ciberseguridad.
- Inexistencia de cargas, gravámenes o derechos de terceros sobre el código.
- Potencial de explotación comercial inmediata en los 27 países de la Unión Europea bajo modelo SaaS B2C y B2B.

**CUARTO. — DESTINO Y ATRIBUCIÓN AL CAPITAL SOCIAL**  
La totalidad del citado activo inmaterial queda formalmente transmitido y cedido en pleno dominio a la mercantil en constitución **SLONE ENTERPRISE S.L.**, quedando atribuido a su Capital Social como **Aportación No Dineraria**, correspondiéndole al compareciente el 100% de las participaciones sociales suscritas y totalmente desembolsadas.

**QUINTO. — RESPONSABILIDAD DE LA VALORACIÓN**  
El socio fundador responde solidariamente frente a la sociedad y frente a los acreedores sociales de la realidad y del valor atribuido a la aportación efectuada, conforme al artículo 73 de la LSC.

En Girona, a {datetime.now().strftime('%d de %B de %Y')}.

---
*(Firma del Socio Fundador)*
"""

def main():
    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(DOCUMENT_CONTENT)
    print(f"✅ Acta notarial de aportación de software generada con éxito:")
    print(f"📁 {OUT_FILE}")
    print(f"💡 Este documento se entrega en Notaría / Punto PAE para constituir la SL")
    print(f"   con 50.000 € de capital social sin desembolsar dinero en efectivo.")

if __name__ == "__main__":
    main()
