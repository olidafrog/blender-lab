"""Shared helpers for experiment scripts.

Import from an experiment script (experiments/<name>/scripts/*.py):
    import sys; from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
    from common import ROOT, enable_gpu, experiment_paths
"""
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent.parent
LIBRARY = ROOT / "library"

# Preference order; first backend with a device wins.
# Windows: OPTIX (RTX 3090 Ti). Mac: METAL (M4 Max).
GPU_BACKENDS = ("OPTIX", "CUDA", "HIP", "ONEAPI", "METAL")


def enable_gpu(scene=None):
    """Point Cycles at the best available GPU. Returns the backend name, or "CPU".

    Needed every run: --factory-startup discards saved preferences.
    """
    scene = scene or bpy.context.scene
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for backend in GPU_BACKENDS:
        try:
            prefs.compute_device_type = backend
        except TypeError:
            continue
        prefs.refresh_devices()
        gpus = [d for d in prefs.devices if d.type == backend]
        if not gpus:
            continue
        for d in prefs.devices:
            d.use = d.type == backend
        scene.cycles.device = "GPU"
        print(f"[common] Cycles on {backend}: {', '.join(d.name for d in gpus)}")
        return backend
    scene.cycles.device = "CPU"
    print("[common] No GPU found, Cycles on CPU")
    return "CPU"


def experiment_paths(script_file):
    """Standard folders for the experiment that owns `script_file`. Creates renders/ and output/."""
    exp = Path(script_file).resolve().parent.parent
    paths = {k: exp / k for k in ("references", "assets", "renders", "reviews", "output")}
    paths["root"] = exp
    paths["name"] = exp.name
    for k in ("renders", "output"):
        paths[k].mkdir(parents=True, exist_ok=True)
    return paths
