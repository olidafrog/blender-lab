# Calibration — A (v04), B (v06), C (ctrl_waxseal_final)

Judged on full frame and 1:1 crops. Samples are sRGB patch means at y≈720. The reference's shadow-side rim measures 33, 22, 48, darker than the brief's 93, 79, 105; no render gets near either.

## A — v04

**Score:** 6.2 / 10

1. The light is too flat and frontal. The left bead reads almost white (232, 221, 240). The darkest shadow-side rim is only 117, 106, 117, a grey, not the deep violet crease.
2. The relief edges carry a thin pale-violet glow line. The flow lines are drawn cracks of even width, and a stray "eye" droplet sits near the bottom rim.

## B — v06

**Score:** 6.6 / 10

1. The thin relief walls glow pink-violet where the light grazes them. This is the SSS leak the research rules out. The rim also has a glossy specular streak, so it drifts toward plastic, not satin.
2. The shadow-side rim (101, 88, 96) is warm grey, not saturated violet. The cast shadow core (75, 61, 56) is short of 63, 48, 49.

## C — ctrl_waxseal_final

**Score:** 5.4 / 10

1. There are moulding seams. A hard dark-violet ring runs round the stamp edge, so the field reads as a separate inset disc. The right rim has a vertical band and a pale curved patch where geometry meets.
2. The field is over-saturated (200, 184, 214) and the lit rim is too bright (218, 204, 231 against 191, 184, 200). It reads as a toy.

## Ranking

**B > A > C**

- **B > A:** B has the only light with real direction. Its deeper shadows model the bead as a rolled lump; A's frontal light flattens it. B's edge glow and gloss need a small material fix; A's flatness needs a new light rig.
- **A > C:** A's material and moulding are clean and plausible. C has visible geometry seams at the stamp edge and on the rim. The mould looks assembled from parts.

## Shared, all three

- None reaches the reference's near-black violet crease under the left rim. Fix it with a lower key (25–35°), less fill, or a subtractive flag on the left. Do not fix it by lowering albedo.
- The relief is sharper, taller and cleaner than the reference's soft pressing, with none of its chalky micro-texture.
