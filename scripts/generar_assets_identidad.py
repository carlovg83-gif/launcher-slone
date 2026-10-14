#!/usr/bin/env python3
import os
import shutil
from PIL import Image

BASE_DIR = "/home/slone/slocast 1.0"
SRC_PRUEBAS = "/home/slone/.gemini/antigravity/brain/b7290ecc-a035-4dae-846a-78c02a4174b1/pruebas_logo"
OUT_BRANDING = os.path.join(BASE_DIR, "branding/identidad_slone")
OUT_ICONS = os.path.join(BASE_DIR, "icons")
SYS_ICONS = os.path.expanduser("~/.local/share/icons")

os.makedirs(OUT_BRANDING, exist_ok=True)
os.makedirs(OUT_ICONS, exist_ok=True)
os.makedirs(SYS_ICONS, exist_ok=True)

OPCIONES = [
    ("prueba_01_corona_tag.jpg", "opcion_01_corona_tag.png", "slone_opcion1_corona_tag.png"),
    ("prueba_02_satelite_orbit.jpg", "opcion_02_orbit_satelite.png", "slone_opcion2_orbit_satelite.png"),
    ("prueba_03_mecha_cyber.jpg", "opcion_03_mecha_cyber.png", "slone_opcion3_mecha_cyber.png"),
    ("prueba_04_bubble_flow.jpg", "opcion_04_bubble_flow.png", "slone_opcion4_bubble_flow.png"),
    ("prueba_05_uplink_lightning.jpg", "opcion_05_uplink_lightning.png", "slone_opcion5_uplink_lightning.png"),
]

print("Procesando las 5 opciones de logotipo...")
for src_name, brand_png, icon_name in OPCIONES:
    src_path = os.path.join(SRC_PRUEBAS, src_name)
    if not os.path.exists(src_path):
        print(f"Aviso: {src_path} no encontrado.")
        continue

    img = Image.open(src_path).convert("RGBA")
    
    # Guardar en branding
    out_brand_path = os.path.join(OUT_BRANDING, brand_png)
    img.save(out_brand_path, format="PNG", optimize=True)
    
    # Generar icono 512x512
    icon_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
    out_icon_path = os.path.join(OUT_ICONS, icon_name)
    icon_512.save(out_icon_path, format="PNG", optimize=True)
    print(f"Generado: {brand_png} e icono {icon_name}")

# La opción 1 (Corona Tag & Ojo Satélite - Dibujo 1) es el icono oficial por defecto
opcion1_src = os.path.join(OUT_ICONS, "slone_opcion1_corona_tag.png")
if os.path.exists(opcion1_src):
    # Respaldar icono actual si no tiene .bak
    slone_icon = os.path.join(OUT_ICONS, "slone.png")
    slone_icon_bak = os.path.join(OUT_ICONS, "slone.png.bak")
    if os.path.exists(slone_icon) and not os.path.exists(slone_icon_bak):
        shutil.copy2(slone_icon, slone_icon_bak)
    
    shutil.copy2(opcion1_src, slone_icon)
    
    sys_icon = os.path.join(SYS_ICONS, "slone.png")
    sys_icon_bak = os.path.join(SYS_ICONS, "slone.png.bak")
    if os.path.exists(sys_icon) and not os.path.exists(sys_icon_bak):
        shutil.copy2(sys_icon, sys_icon_bak)
    shutil.copy2(opcion1_src, sys_icon)
    print("Icono oficial 'slone.png' actualizado con la Opción 1 (Corona Tag & Ojo Satélite).")

print("Procesamiento de identidad completado con éxito.")
