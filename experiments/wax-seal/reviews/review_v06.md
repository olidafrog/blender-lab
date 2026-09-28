# Review v06

1. **Score:** 6.4 / 10

2. **Targets**
- Paper: 215, 209, 205. Near miss (B 3 below range; slightly warm).
- Lit field: 199, 185, 205. Hit.
- Relief tops: about 235, 221, 241. Hit, but a little too magenta.
- Outer rim, shadow side: 108, 97, 101 (min 91, 79, 85). Missed. Near-neutral grey (R ≥ B), not saturated violet.
- Rim, lit side: 235, 223, 241. Missed. About 40 too bright; clipping toward white.
- Cast-shadow core: 59, 47, 42. Hit on value; too brown (B 42 vs 49).
- Seal width: about 1093 px, 90%. Hit.
- Rim bead: about 118 px, 10.8%. Hit.
- Stamped field: about 76%. Hit.

3. **What works**
- Proportions, framing and the field colour match the reference closely.
- The emblem sits in the same wax. Its bevel is soft and its lower-left contact shadows read correctly.
- The irregular outer outline and the pooled lump at lower right are in the right places.

4. **Problems, ranked**
1. **Material reads as soap or matte plastic.** The rim, the field and the relief are uniformly smooth, with no chalky grain. The specular is a broad, even sheen. Fix: add a micro-bump (noise, scale about 0.05–0.1 mm, strength 0.02–0.05) and a roughness breakup (0.35–0.55). Add a thin coat (weight 0.1–0.2, roughness 0.15) so the bead gets the small, sharp highlights you see on the reference rim at upper right.
2. **Lighting is too frontal and soft, so the rim does not model.** The left outer wall is a lit grey (108) where the reference is a deep violet band. The right rim clips. Fix: lower the key to 25–35° elevation, reduce its size by about half, and cut fill so the shadow-side rim lands at 80–100 luminance. Tint the shadows through the wax, not by exposure: raise the subsurface radius on R and G relative to B, or set the SSS colour more saturated than the base, so shadow areas go violet. Bring the lit rim down to 190–210.
3. **Surface detail is wrong in kind.** The field has a few long, drawn-looking hair curves. The right rim has pale, translucent swirl bands (crop 1000_1050) that look like marbling or an SSS seam. The reference shows many fine, short, crackle-like flow lines across the field and nothing on the rim. Fix: remove the rim swirls. Drive the field lines with a Voronoi-edge or distorted-noise mask at 10–20 cells across the field, as a bump of 0.01–0.03 mm.

5. **Research check**
- "Shadows deep and saturated violet, not grey": contradicted. The rim's shadow side is grey.
- "Thin relief edges do not glow": mostly holds, but the relief edges carry a bright hairline rim that reads as translucency or a bevel highlight.
- "Steep inner wall at the stamp edge": too shallow. It reads as a thin crease, not a wall in shadow.
- "Satin, not glossy plastic": holds for gloss, but the texture is missing, so it reads as smooth plastic.

6. **What 8.5 needs**
- A lower, smaller key with less fill, and violet SSS-tinted shadows. Get the left rim to about 93, 79, 105.
- Micro grain and roughness breakup, plus small coat highlights on the bead.
- Replace the hair curves and rim swirls with fine crackle flow lines.
- A deeper, steeper inner rim wall.
