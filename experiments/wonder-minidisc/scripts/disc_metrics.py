"""Disc colour metrics from a render made with --set show_case=False (disc on white).

    python experiments/wonder-minidisc/scripts/disc_metrics.py renders/t60.png

Targets (from the ref4 read and the reviews): >= 4 hue families at saturation > 0.35,
20-40 % of the disc near-dark mirror, < 3 % clipped.
"""
import colorsys
import sys

import numpy as np
from PIL import Image

FAMILIES = [("red", 0, 15), ("orange", 15, 45), ("yellow", 45, 70), ("green", 70, 160), ("cyan", 160, 200),
            ("blue", 200, 250), ("violet", 250, 290), ("magenta/pink", 290, 345), ("red", 345, 360)]

a = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(float) / 255
flat = a.reshape(-1, 3)
disc = flat[(flat.min(1) < 0.93)]  # everything that is not the white table
hsv = np.array([colorsys.rgb_to_hsv(*p) for p in disc[:: max(1, len(disc) // 40000)]])
h, s, v = hsv[:, 0] * 360, hsv[:, 1], hsv[:, 2]
sat = s > 0.35
fam = {}
for name, lo, hi in FAMILIES:
    n = np.sum(sat & (h >= lo) & (h < hi)) / len(h)
    fam[name] = fam.get(name, 0) + n
present = [k for k, n in fam.items() if n > 0.01]
print(f"[out] saturated {sat.mean():.0%}  dark {np.mean(v < 0.3):.0%}  clipped {np.mean(disc.max(1) > 0.99):.0%}")
print("[out] families >1%: " + ", ".join(f"{k} {fam[k]:.0%}" for k in present) + f"  -> {len(present)}")
