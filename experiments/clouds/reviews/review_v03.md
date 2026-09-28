# Review v03 — pink_rod (target: 02_pink_rod_sky.jpg)

## 1. Score: 6.2 / 10

## 2. Targets

| Target | Ref | Measured | Result |
|---|---|---|---|
| Lit top | 180,146,170 | 219,127,187 | missed (magenta, G −19, B +17) |
| Left | 183,123,148 | 224,145,201 | missed (too bright, B +53) |
| Violet shadow (right) | 148,101,135 | 127,89,143 | hit (slightly dark and blue) |
| Bottom | 127,76,104 | 113,70,129 | missed (B +25, violet not rose) |
| Sky top | 63,109,155 | 65,108,152 | hit |
| Sky bottom | 134,165,184 | 128,157,179 | hit |
| Shadow/lit luminance ≥0.35 | — | 0.61 right, 0.50 base | hit |
| Edge falloff 2–4 px / 700 | — | ~12 px at 1400 = ~6 px | missed (soft) |
| Entry glow 3–5 tube widths | — | ~2 at entry, ~0 at exit | missed |

## 3. What works
- Sky is now on target: saturated blue gradient, top and bottom within a few levels.
- Light direction matches: lit left, violet right side and base. Colour deepens in the core (190,103,162) and shadows, so it now behaves like albedo.
- Clean: no fireflies, no voxel steps, no grid artefacts.

## 4. Problems, ranked
1. **Rod still stops at the surface (entry 345,530; exit 1055,1080).** Same fault as v02, so bounce and light-linking tweaks are not the answer. New mechanism: add volume emission driven by distance to the rod axis, `rod_colour × strength × exp(−d / r)`, r ≈ 2 tube widths. Target a hot pink bloom 3–5 tube widths wide at the exit (ref 02's brightest cloud area) and a fainter one at the entry.
2. **Billows are smeared single-scale blobs (centre and 1060_1090 crops).** Waxy surface; a flat plateau near (520,680). Ref 02 is tight popcorn down to ~1% of cloud width. The extra noise octave did not produce it. New mechanism: instanced spheres at 3 scales (radius ratio ~0.4 per level) unioned via Points to SDF Grid, with a thin density falloff. Denoise with albedo and normal passes at 512+ samples.
3. **Colour is bubblegum magenta, not salmon-lavender.** Blue too high everywhere. Raise green albedo ~0.02, lower blue ~0.02, drop exposure ~0.3 stop. Target lit R:G:B ≈ 1 : 0.8 : 0.93.

## 5. Research check
- Contradicts "crisp rounded silhouettes with a soft few-pixel falloff": the edges are ~2× too soft.
- Contradicts "emitter becomes a soft glow keeping its hue": there is no internal glow.
- Agrees with multiple scattering (light shadows), dark base and albedo-driven saturation.

## 6. What 8.5 needs
- Distance-driven rod glow inside the volume, strongest at the exit.
- Multi-scale sphere-lobe density with a 2–4 px edge (per 700 px) and no denoiser smear.
- Shift the hue from magenta to salmon-lavender (less blue, more green).
- Light film grain to match ref 02.
