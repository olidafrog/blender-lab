# Review — v13_tower (target: 04 cumulonimbus)

## 1. Score: 5.4 / 10

## 2. Targets

| Target | Measured | Result |
|---|---|---|
| Bright body ~238,236,227 | 174,168,166 (lit top); p99 luma 204 | missed, about 65 levels too dark |
| Base ~66,74,82 | 69,80,98 (bottom band); underside 29,52,79 (sky shows through) | colour close, density missed |
| Base ≈ 0.3 of top luminance | 0.31 / 0.66 = 0.47 | missed |
| Edge falloff 2–4 px per 700 px | about 1–1.5 px per 700 px (right edge: 149→135→103→39) | missed, too hard |

## 3. What works

- Lobe-on-lobe structure along the silhouette. The upper-right edge (tr crop) reads as real cumulus towers.
- Warm-neutral body against a cool sky, with sky blue wrapping into the shadowed lobes.
- Clean render. No fireflies, no voxel steps, no grain.

## 4. Problems, ranked

1. **Whole body: grey plaster, not white cloud.** The lit body is 174, and ref 04 is 238. It reads as putty or clay. Research says clouds are near-white from multiple scattering. Raise volume bounces to 32 or more. If bounces are already high, the fault is the view transform. AgX pulls white down to grey, so add +0.7 to +1.0 stops exposure, or use Standard with a highlight roll-off. Target: lit body 225–245 and p99 no higher than 250.

2. **Centre: dark hollow with smooth sheet surfaces.** The core is 29,45,69, which is darker than the sky at the horizon. The cavity walls are smooth, stretched planes with no billow detail (centre crop and tl crop, lower right). These are the untextured insides of separate lobe shapes that do not overlap. Value tweaks will not fix it. Union a low-frequency core volume (an ellipsoid or capsule at 60–70 % of the tower width) under the lobes so the inside is solid, and apply detail displacement to that core as well. Target: crevices at 0.45–0.6 of lit-body luminance, tinted by the sky.

3. **Base: thin transparent skirt, not a dark flat base.** Below y≈1080 the sky shows through a smoky fringe, and the lower-left flank (x 200–400, y 550–850) is low-density smoke. Ref 04 has a dense, flat, dark shelf. Clamp density to full right down to a flat cut-off plane, with a falloff over 2–4 % of the tower height, so the base is lit only from below. Target base 60–85 per channel, about 0.3 of top luminance.

## 5. Research check

- Contradicts "crevices stay light": the centre goes near-black, which is the dirty single-scatter look.
- Contradicts "near-white": the body is mid-grey.
- Contradicts "soft few-pixel falloff": edges are close to hard surfaces.
- Agrees with "base darker than top", but only because the base is thin.
- The lobes are too uniform in size. Small spherical warts cover every surface (popcorn), where ref 04 has large soft rolls that fade into haze.

## 6. What 8.5 needs

- Lit body 225–245. Use exposure or view transform first, then bounces.
- A solid, displaced core. No hollow, no smooth sheets.
- A dense, flat base at about 0.3 of top luminance.
- Edge ramp 2–4 px per 700 px. Halve the smallest noise octave so large rolls dominate.
