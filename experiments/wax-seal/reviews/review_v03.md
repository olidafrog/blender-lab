# Review — v03

## 1. Score: 6.2 / 10

## 2. Targets

- Paper: 213–221, 208–215, 204–211. Hit (slightly warm).
- Lit field: 183–188, 172–180, 190–197. Missed, 8–10 dark.
- Relief tops: 185–192, 174–180, 192–200. Missed, tops equal the field.
- Rim shadow side: 93, 78, 95. Near hit, B 10 low.
- Rim lit side: 239, 229, 245. Missed, blown.
- Cast-shadow core: 50, 44, 43. Missed, too dark and neutral.
- Seal width: ~93%. Hit.
- Rim bead: ~12% left, ~15% right. Hit left, wide right.
- Field: ~73% of seal width. Missed.

## 3. What works

- The key direction and cast shadow match: upper right, shadow lower left.
- The shadow side of the rim goes violet, not grey.
- The bead has a rolled section and a soft contact with the paper.

## 4. Problems, ranked

1. **The emblem reads as inflated plastic (centre crops).** The strokes are pillowed, with wide bevels and a hot edge specular. A thin saturated purple fringe outlines each stroke base and the field circle. In the ref the relief is low with crisp shoulders, and its flat tops read brighter than the field. Fix: relief height 0.3–0.5 mm, bevel radius 25–35% of height, flat tops. Roughness 0.45–0.55. The fringe is SSS bleed or a cavity multiply: set the SSS radius under 0.3 mm and remove any cavity darkening.
2. **The surface is CG-clean and the flow lines are straight facets (`crop_br`, `crop_centre`).** There is no micro-texture, so it reads as soap. Fix: make flow lines from stretched, domain-warped noise, with bump strength under 0.05. Add a chalky micro-bump (0.1–0.3 mm scale) and roughness variation of ±0.1.
3. **The lit rim clips and the shadow is black (right bead, left shadow).** The right bead hits 239 and loses the lilac. The cast shadow is neutral with a hard edge. Fix: make the key 2–3x larger and 0.5–0.7 EV dimmer. Add a warm, paper-coloured fill at 5–10% of the key.

Also: the rim is a regular torus; the ref has a pooled lump at lower right.

## 5. Research check

- Contradicts "thin relief edges do not glow": the strokes carry a purple fringe.
- Contradicts "satin, not glossy plastic": the relief specular is glossy.
- Contradicts "hairline flow lines": they render as straight seams.
- Agrees on light direction, violet shadow hue and a rolled bead.

## 6. What 8.5 needs

- A lower, crisper relief with no fringe, roughness 0.45–0.55.
- Organic flow lines and chalky micro-texture.
- A softer, dimmer key with warm fill: lit rim 191–222, relief tops brighter than the field.
- A field at 78% of seal width, and one or two pooled lumps on the outline.
