# Review — v10_sunset (target: 03_lone_sunset_cumulus)

## 1. Score: 6.8 / 10

## 2. Targets

| Target | Ref | Measured (v10) | Result |
|---|---|---|---|
| Lit peak | 225,200,170 | 230,178,150 (right lobe, x900–960 y760–830) | Missed: G/B 20 low, too orange |
| Shadow side | 95,78,86 | 47,68,92 (left lobe, x470–540 y760–840) | Missed: blue, not mauve; R half the target |
| Sky top | 41,88,120 | 15,80,116 | Near hit: R 26 low, too cyan |
| Shadow/lit luminance | ≥ ~0.35 | 63/186 = 0.34 overall; crevice between lobes 53/186 = 0.28 | Borderline; crevice missed |
| Edge falloff | 2–4 px / 700 px | Top edge 2 px, right edge ~4 px | Hit |

## 3. What works

- The right lobe's cauliflower shading is convincing. It has rounded sub-lobes at 3 scales, soft self-shadow between them and a warm, high-albedo body.
- The render is clean. There is no grain, no fireflies and no voxel steps in any crop. The sky gradient is smooth.
- The light direction matches: low sun from the right, top-right lit, underside dark (base 75,56,62).

## 4. Problems, ranked

1. **The left half is a blue cloud (x450–740).** In ref 03 the unlit side is warm grey-mauve. The sunset ambient and warm multiple-scatter bleed through it. Here it is sky-blue 47,68,92 and reads as a second, colder object. Fix: the shadow is getting only zenith sky. Do not tint the sky further. Change the mechanism instead. Add a warm, low-horizon fill: a second weak sun or an area light from behind the camera, colour ~#8a6a70, at 3–6% of the key. Also raise volume bounces to ≥ 32, so sunlight scatters across from the lit lobe. Aim for shadow R ≥ G, at 85–100 luma.
2. **The base is a ruler-straight cut with a dark rim line (y≈915, x460–990).** It reads as the domain clipped by a plane. Ref 03 has a flat base, but it is ragged and soft over 6–12 px, with small hanging lobes. Fix: do not hard-clip the density. Fade it over 3–5% of the cloud height with a noise-displaced height gradient, and let 1–2 small lobes break below the line.
3. **The crevice between the two masses is too deep (x≈760, luma 53).** Research: shadowed crevices stay light. It splits the cloud into two, where ref 03 is one continuous mass. Fix: bridge the lobes with a lower-density connecting lobe, and raise multiple-scatter gain in the shadowed interior, so the crevice is ≥ 0.4 of the lit side.

## 5. Research check

- The dark base agrees. The lit-side multiple scattering agrees.
- It contradicts "shadowed crevices stay light" (the crevice at 0.28).
- It contradicts the ambient part of "take the sky's colour". The shadow takes only the zenith blue, not the warm horizon of a dusk sky.
- No silver lining shows, which is correct for a front-lit setup.

## 6. What 8.5 needs

- A warm low fill, so the shadow side lands near 95,78,86.
- A soft, ragged base instead of a planar cut.
- One continuous mass, with the inter-lobe crevice ≥ 0.4 of the lit side.
- Lit peak desaturated toward 225,200,170: less orange, raise G/B by ~20.
