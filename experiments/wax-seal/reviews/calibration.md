# Calibration: A (v07) vs B (v05)

## A — renders/v07.png

**Score:** 6.4 / 10

**Targets**
- Paper: 215, 209, 204. Missed (blue about 4 low, slightly warm).
- Lit field: 188, 174, 202. Missed (green 10 low; B > R > G order holds).
- Relief tops: 235, 222, 244. Hit (blue about 11 high).
- Rim shadow side (left): 101, 89, 103. Missed. The value is close, but the chroma is near neutral, not deep violet.
- Rim lit side (right): 234, 221, 239. Missed (about 40 too bright).
- Cast-shadow core at the left of the seal: 89, 80, 75. Missed (far too light). The darkest shadow sits low-left (51, 39, 37), not beside the seal.
- Seal width 88%, bead about 10%, field about 80%. Hit.

**Top 3 problems**
1. Crevice lines at the emblem edges and the inner rim wall are saturated, ink-like purple. They read as drawn outlines, not occlusion. Lower the saturation of the scatter or AO tint in the crevices by about 30–40%. Keep the violet, but take the value down.
2. Material: at 1:1 the surface is smooth, soft plastic. There is no chalky micro-grain, no satin sheen break-up and no hairline flow texture. The reference has all of these. Add a fine noise bump (0.02–0.05 mm) and roughness variation (0.35–0.55).
3. Lighting: the lit rim is blown and the cast shadow at the left is weak. Make the key smaller or harder, and cut the fill by about half, so the left shadow core reaches about 60–70.

## B — renders/v05.png

**Score:** 6.1 / 10

**Targets**
- Paper: 212, 208, 204. Missed (same warm cast as A).
- Lit field: 192, 179, 201. Missed (green 5 low). Closer than A.
- Relief tops: 240, 229, 247. Missed (about 10–15 high).
- Rim shadow side: 80, 71, 81. Missed. The band is grey, not violet.
- Rim lit side: 239, 228, 241. Missed (blown).
- Cast-shadow core: 48, 43, 41. Hit on value, missed on hue (the reference is red-warm: 63, 48, 49).
- Proportions: 88%, about 10%, about 80%. Hit.

**Top 3 problems**
1. Shadows go grey-brown in the rim wall and under the emblem. This contradicts the research: sealing-wax shadows turn deep, saturated violet. The subsurface colour or the radius is too neutral. Tint it and let the shadow terminator pick up violet.
2. The same plastic, texture-free surface as A. The flow lines are the only detail.
3. The lit side is blown out and the whole seal reads flat and pale. The shadow-to-lit range on the rim is narrower than in the reference.

## Verdict

A is better. The brief puts the wax first, and A's violet shadow chroma follows the research and the reference, while B's grey crevices make the wax read as painted clay. B has the better cast-shadow depth, but that is a lighting value A can copy, whereas A's lead is in the material.
