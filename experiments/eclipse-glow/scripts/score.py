"""An original dark-synth cue for the rise video, in the spirit of mid-80s sci-fi scores:
a low drone that opens up, metallic hits in an uneven 7/8 pulse, a brassy swell, and one
big hit when the logo comes to rest. Timed to build_rise.py's frames.

    tools/blender.sh experiments/eclipse-glow/scripts/score.py   (numpy comes with Blender)

Writes output/eclipse_rise_score.wav (48 kHz, stereo, 16-bit).
"""
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
EXP = Path(__file__).resolve().parents[1]

SR = 48000
FPS, FRAMES = 24, 288
RISE_START, REST = 12 / FPS, 228 / FPS  # seconds: top breaks the horizon, logo at rest
LENGTH = FRAMES / FPS
BPM_EIGHTH = 0.3                         # seconds per eighth note
PULSE = [1.0, 0, 0, 0.6, 0, 0.8, 0]      # 7/8: accents on 1, 4, 6
rng = np.random.default_rng(1984)
t = np.arange(int(SR * LENGTH)) / SR


def hz(note):
    """'D3' → Hz."""
    names = {"C": -9, "C#": -8, "D": -7, "Eb": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "Ab": -1,
             "A": 0, "Bb": 1, "B": 2}
    return 440.0 * 2 ** ((names[note[:-1]] + 12 * (int(note[-1]) - 4)) / 12)


def saw(f, detune=(-7, 0, 7)):
    """Detuned saw stack, cents."""
    out = np.zeros_like(t)
    for c in detune:
        ph = (t * f * 2 ** (c / 1200) + rng.random()) % 1.0
        out += 2 * ph - 1
    return out / len(detune)


def lowpass(x, cutoff, taps=255):
    n = np.arange(taps) - (taps - 1) / 2
    k = np.sinc(2 * cutoff / SR * n) * np.hamming(taps)
    return np.convolve(x, k / k.sum(), mode="same")


def env(points):
    """Piecewise-linear envelope from (seconds, level) points."""
    ts, vs = zip(*points)
    return np.interp(t, ts, vs)


def smooth(x0, x1):
    return np.clip((t - x0) / (x1 - x0), 0, 1) ** 2


def comb(x, d, g):
    y = x.copy()
    for k in range(d, len(x), d):
        y[k:k + d] += g * y[k - d:k][: len(y[k:k + d])]
    return y


def allpass(x, d, g):
    y = np.zeros_like(x)
    xd = np.concatenate([np.zeros(d), x[:-d]])
    y[:] = -g * x + xd
    for k in range(d, len(x), d):
        y[k:k + d] += g * y[k - d:k][: len(y[k:k + d])]
    return y


def reverb(x, size=1.0, decay=0.84):
    s = SR / 44100 * size
    wet = sum(comb(x, int(d * s), decay) for d in (1557, 1617, 1491, 1422, 1277, 1356)) / 6
    for d in (225, 556, 441):
        wet = allpass(wet, int(d * s), 0.5)
    return wet


def hit(at, f0=180.0, ratio=1.41, decay=0.35, index=6.0, noise=0.3):
    """Metallic FM clang: an inharmonic modulator and a noise click."""
    tt = np.clip(t - at, 0, None)
    on = (t >= at).astype(float)
    e = np.exp(-tt / decay) * on
    mod = np.sin(2 * np.pi * f0 * ratio * tt) * index * np.exp(-tt / (decay * 0.5))
    tone = np.sin(2 * np.pi * f0 * tt + mod) * e
    click = rng.standard_normal(len(t)) * np.exp(-tt / 0.02) * on * noise
    return tone + click


# Drone: D and A, dark at first, opening as the logo rises.
drone = saw(hz("D2")) + 0.6 * saw(hz("A2")) + 0.5 * saw(hz("D1"), (0, 4))
dark, bright = lowpass(drone, 180), lowpass(drone, 1400)
opening = smooth(RISE_START, REST)
drone = (dark * (1 - opening) + bright * opening) * env([(0, 0), (1.2, 0.5), (REST, 0.8), (LENGTH - 1.0, 0.7), (LENGTH, 0)])

# Pulse: metallic hits on an uneven 7/8, growing towards the rest.
pulse = np.zeros_like(t)
beat, i = 1.5, 0
while beat < REST - 0.05:
    a = PULSE[i % 7]
    if a:
        grow = 0.25 + 0.75 * (beat - 1.5) / (REST - 1.5)
        pulse += a * grow * hit(beat, f0=150 if i % 7 == 0 else 210, decay=0.18, noise=0.12)
    beat += BPM_EIGHTH
    i += 1
low_thud = np.zeros_like(t)
for k in range(int((REST - 1.5) / (7 * BPM_EIGHTH)) + 1):  # a sub thump on each bar's downbeat
    at = 1.5 + k * 7 * BPM_EIGHTH
    tt = np.clip(t - at, 0, None)
    low_thud += np.sin(2 * np.pi * (55 + 60 * np.exp(-tt / 0.03)) * tt) * np.exp(-tt / 0.25) * (t >= at)

# Brass swell: D minor pad, then B-flat over D at the rest.
pad = sum(saw(hz(n), (-9, 0, 9)) for n in ("D3", "F3", "A3", "D4")) / 4
pad_b = sum(saw(hz(n), (-9, 0, 9)) for n in ("Bb2", "D3", "F3", "Bb3", "F4")) / 5
swell = smooth(3.0, REST)
pad = lowpass(pad, 500) * (1 - swell) + lowpass(pad, 2200) * swell
pad = pad * env([(0, 0), (3.0, 0), (REST - 0.02, 0.35), (REST, 0)])
pad_b = lowpass(pad_b, 2600) * env([(0, 0), (REST, 0), (REST + 0.05, 0.5), (LENGTH - 0.6, 0.3), (LENGTH, 0)])

# Lead: a lonely square-ish line, gliding between notes.
notes = [(4.6, "A4"), (5.8, "D5"), (7.0, "C5"), (8.2, "A4"), (REST, "F5")]
steps = [(0, "A4")] + notes  # held notes; the glide below smooths the steps
f = np.array([hz(n) for _, n in steps])[np.searchsorted([s for s, _ in steps], t, side="right") - 1]
g = int(0.09 * SR)  # 90 ms glide
f = np.convolve(np.concatenate([np.full(g, f[0]), f, np.full(g, f[-1])]), np.ones(g) / g, "same")[g:-g]
lead_phase = np.cumsum(f) / SR
lead = np.tanh(3 * np.sin(2 * np.pi * lead_phase)) * (1 + 0.1 * np.sin(2 * np.pi * 5.5 * t))
lead = lowpass(lead, 2500) * env([(0, 0), (4.4, 0), (4.8, 0.18), (REST, 0.22), (LENGTH - 0.5, 0.15), (LENGTH, 0)])

# Riser: filtered noise that climbs under the rise, cut at the hit.
nz = rng.standard_normal(len(t))
riser = lowpass(nz, 300) * (1 - opening) + lowpass(nz, 3000) * opening
riser *= env([(0, 0), (1.0, 0), (REST - 0.02, 0.25), (REST, 0)])

# The landing: big clang, sub boom.
tt = np.clip(t - REST, 0, None)
boom = np.sin(2 * np.pi * (40 + 80 * np.exp(-tt / 0.05)) * tt) * np.exp(-tt / 1.2) * (t >= REST)
clang = hit(REST, f0=110, ratio=1.37, decay=1.6, index=9.0, noise=0.6)

dry = 0.55 * drone + 0.45 * pulse + 0.5 * low_thud + 0.6 * pad + 0.6 * pad_b + lead + riser + 0.9 * boom + 0.6 * clang
wet = reverb(0.6 * pulse + 0.4 * pad + 0.5 * lead + 0.8 * clang + 0.3 * pad_b, size=1.3, decay=0.86)

# Stereo: reverb decorrelated by a small delay, hits panned slightly apart.
d = int(0.013 * SR)
L = dry + 0.55 * wet + 0.08 * pulse
R = dry + 0.55 * np.concatenate([np.zeros(d), wet[:-d]]) - 0.08 * pulse
mix = np.stack([L, R], 1)
mix *= env([(0, 0), (0.05, 1), (LENGTH - 0.4, 1), (LENGTH, 0)])[:, None]
mix = np.tanh(1.2 * mix / np.abs(mix).max()) / np.tanh(1.2) * 0.89  # soft limit, ~-1 dBFS

out = EXP / "output" / "eclipse_rise_score.wav"
with wave.open(str(out), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print(f"[out] WROTE {out}  {LENGTH:.1f} s")
