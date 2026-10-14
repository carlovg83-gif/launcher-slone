#!/usr/bin/env python3
"""
SLONE™ PERFORMANCE PROFILE — Perfil de máximo rendimiento integrado.
══════════════════════════════════════════════════════════════════════════
• Detección de hardware (CPU, núcleos, RAM, GPU) sin dependencias externas.
• Ajustes óptimos de decodificación por hardware y búfer para MPV y VLC.
• Guarda el perfil en config/slone_control.json → 'motor_reproduccion'.
• Tuning del SO opcional (gobernador CPU 'performance') vía script con sudo.
"""

import os
import json
import shutil
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_DIR / "config" / "slone_control.json"

# Mejores ajustes por defecto (perfil soberano de máximo rendimiento).
BEST_PROFILE = {
    "perfil_alto_rendimiento": True,
    "hwdec": "auto-safe",          # decodificación por hardware con fallback seguro
    "buffer_demuxer_mb": 128,      # timeshift generoso
    "buffer_back_mb": 64,
    "cache_secs": 1,               # mínimo retardo respecto al directo
    "deinterlace": "auto",         # 50 fps fluidos en deportes
    "gpu_api": "auto",
}


def _read(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def detect_gpu() -> str:
    if shutil.which("nvidia-smi"):
        try:
            out = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                                 capture_output=True, text=True, timeout=3)
            if out.stdout.strip():
                return "NVIDIA " + out.stdout.strip().splitlines()[0]
        except Exception:
            pass
    if shutil.which("lspci"):
        try:
            out = subprocess.run(["lspci"], capture_output=True, text=True, timeout=3).stdout
            for line in out.splitlines():
                if "VGA compatible controller" in line or "3D controller" in line:
                    return line.split(":", 2)[-1].strip()
        except Exception:
            pass
    return "Genérica"


def detect_hardware() -> dict:
    cpu = ""
    for line in _read("/proc/cpuinfo").splitlines():
        if line.lower().startswith("model name"):
            cpu = line.split(":", 1)[1].strip()
            break
    ram_gb = 0.0
    for line in _read("/proc/meminfo").splitlines():
        if line.startswith("MemTotal"):
            try:
                ram_gb = round(int(line.split()[1]) / 1024 / 1024, 1)
            except Exception:
                pass
            break
    return {
        "cpu": cpu or "Desconocida",
        "cores": os.cpu_count() or 1,
        "ram_gb": ram_gb,
        "governor": _read("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"),
        "governors": _read("/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors"),
        "gpu": detect_gpu(),
    }


def load_profile() -> dict:
    try:
        prof = json.loads(CONFIG_PATH.read_text(encoding="utf-8")).get("motor_reproduccion", {})
    except Exception:
        prof = {}
    merged = dict(BEST_PROFILE)
    merged.update({k: v for k, v in prof.items() if v is not None})
    return merged


def profile_active() -> bool:
    return bool(load_profile().get("perfil_alto_rendimiento", False))


def best_mpv_args() -> list:
    """Flags extra de MPV para máximo rendimiento. Vacío si el perfil no está activo."""
    prof = load_profile()
    if not prof.get("perfil_alto_rendimiento"):
        return []
    cores = os.cpu_count() or 2
    return [
        f"--hwdec={prof.get('hwdec', 'auto-safe')}",
        f"--vd-lavc-threads={max(2, cores)}",
        f"--demuxer-max-bytes={int(prof.get('buffer_demuxer_mb', 128))}M",
        f"--demuxer-max-back-bytes={int(prof.get('buffer_back_mb', 64))}M",
        f"--cache-secs={prof.get('cache_secs', 1)}",
        f"--deinterlace={prof.get('deinterlace', 'auto')}",
        "--cache-pause=no",
    ]


def best_vlc_options() -> list:
    """Opciones de libvlc para máximo rendimiento. Vacío si el perfil no está activo."""
    prof = load_profile()
    if not prof.get("perfil_alto_rendimiento"):
        return []
    ms = max(200, int(prof.get("cache_secs", 1)) * 1000)
    return [
        ":network-caching=%d" % ms,
        ":clock-jitter=0",
        ":clock-synchro=0",
        ":avcodec-hw=any",
    ]


def apply_performance_profile() -> bool:
    """Escribe los mejores ajustes en la directiva maestra. Devuelve True si tuvo éxito."""
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8")) if CONFIG_PATH.exists() else {}
    except Exception:
        data = {}
    motor = data.get("motor_reproduccion", {}) or {}
    motor.update(BEST_PROFILE)
    data["motor_reproduccion"] = motor
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception:
        return False


def summary_text() -> str:
    hw = detect_hardware()
    prof = load_profile()
    estado = "ACTIVO" if prof.get("perfil_alto_rendimiento") else "inactivo"
    gov = hw.get("governor") or "n/d"
    return (f"Perfil: {estado} · CPU: {hw['cpu']} · {hw['cores']} núcleos · "
            f"RAM: {hw['ram_gb']} GB · GPU: {hw['gpu']} · Gobernador: {gov}")


if __name__ == "__main__":
    print(summary_text())
    print("MPV:", " ".join(best_mpv_args()))
    print("VLC:", " ".join(best_vlc_options()))
