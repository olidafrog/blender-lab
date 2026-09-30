"""Fit the hero camera to the reference from 12 landmarks (assets/landmarks.json, device mm -> ref px).
   python3 experiments/cyber-model/scripts/fit_camera.py
Wrapper for tools/fit_camera.py. Result: azimuth 41.0, elevation 48.65, dist 1485 mm, lens 200, rms 6.3 px."""
import runpy
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.argv = [sys.argv[0], str(root / "assets/landmarks.json")]
runpy.run_path(str(root.parents[1] / "tools/fit_camera.py"), run_name="__main__")
