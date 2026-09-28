# Review v02 — pink_rod (target: 02_pink_rod_sky.jpg)

## 1. Score: 5.6 / 10

## 2. Targets

| Target | Ref | Measured | Result |
|---|---|---|---|
| Lit top | 180,146,170 | 189,150,178 | hit |
| Left | 183,123,148 | 191,160,183 | missed (G +37, washed out) |
| Violet shadow | 148,101,135 | 134,120,151 | missed (blue-grey, not violet-pink) |
| Bottom | 127,76,104 | 123,95,137 | missed (too blue, G +19) |
| Sky top | 63,109,155 | 120,144,163 | missed badly (grey, no depth) |
| Sky bottom | 134,165,184 | 140,158,169 | missed (too grey) |
| Shadow/lit luminance ≥0.35 | — | 0.78 (bottom 0.65) | hit |
| Edge falloff 2–4 px / 700 | — | ~8 px at 1400 = ~4 px | hit (borderline) |
| Entry glow 3–5 tube widths | — | ~2 at entry, 0 at exit | missed |

## 3. What works
- Multiple-scattering brightness: shadows stay light, no smoky single-scatter look.
- Rounded lobed silhouette with a soft few-pixel edge; no voxel steps, no fireflies.
- Lit-top colour is on target.

## 4. Problems, ranked
1. **Colour is paint, not albedo (whole cloud).** Pastel lilac everywhere; the core and shadows go blue-grey instead of deeper salmon-magenta. Ref 02 saturates hard in the shadows (G drops to ~76–101). Fix: set per-channel albedo, roughly R 0.99, G 0.90–0.93, B 0.95–0.97, with scatter density high enough for 20+ bounces, so saturation compounds with depth. Remove any flat colour tint. Cut the blue sky fill in shadows by ~40%.
2. **The rod does not pass through the volume.** It stops at the silhouette on both sides. Nothing glows through along its path, and the lower-right exit has no glow at all. Fix: make the rod a real emissive mesh through the cloud (not two stubs). Make sure the volume's scatter reaches it: raise volume bounces to 16+ and check the rod is not excluded by light linking. Target a magenta hotspot 3–5 tube widths wide where it is under 1–2 lobes of depth.
3. **Billows at one scale, smeared (centre crop).** Mid-size blobs look like clay; ref 02 has popcorn lobes down to ~1% of cloud width. The centre crop shows denoiser smear, not detail. Fix: add a second, finer displacement octave (lobe size ~1/8 of the current) with billow (abs) noise, not more amplitude on the same octave. Render more samples and denoise with albedo+normal passes, or drop the denoiser strength.

Also: sky and key light. Sky is flat grey. Ref is a saturated blue gradient with a warm low sun from the left giving a lit left side and a clear violet right. The render reads as overcast ambient.

## 5. Research check
- Contradicts "colour deepens and saturates in the core and shadow": it desaturates to blue-grey.
- Contradicts "emitter inside becomes a soft glow keeping its hue": no internal glow.
- Contradicts "lobes on lobes on lobes": one scale only.
- Agrees on near-white multiple scattering and on soft few-pixel edges.

## 6. What 8.5 needs
- Per-channel albedo below 1 so shadows go deep salmon-magenta.
- A continuous rod through the volume with a visible glow under the surface.
- A second fine billow octave, with less denoiser smear.
- A saturated blue sky gradient and a warm directional sun from upper-left.
