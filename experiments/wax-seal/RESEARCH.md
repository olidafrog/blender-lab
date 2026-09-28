# wax-seal — research

## Read of the reference

`references/ref_clean.png` (the photo cropped out of the screenshot window, 1212×1442). Crops were checked at 1:1. In order of importance to the look:

1. **The wax.** Pale lilac and opaque, like chalky pigmented wax. The wax has a satin sheen: soft broad highlights, and no sharp specular except a few glints on the lower-right rim. Shadows turn deep and saturated violet (outer left rim is 93,79,105) instead of grey, which shows short-range subsurface scatter plus coloured bounce. Thin relief edges do not glow, so the scatter distance is short.
2. **The light.** One large soft key from the **upper right**, at about 40–50° elevation. The seal casts a soft shadow to the **lower left**, and relief shadows also fall lower-left. The top-right edges of the relief catch near-white highlights. There is a soft ambient fill, and the paper is lit fairly evenly.
3. **The rim.** A thick rolled bead of squeezed-out wax. It stands higher than the field. Its inner wall at the stamp edge is steep and sits in shadow on the right. The outer slope rolls down to the paper in a soft rounded contact. The outline is an irregular blob, with a bulge at the lower right and a wrinkled or folded lump on the right side where the wax pooled.
4. **The field.** A flat stamped disc, slightly dished. It carries faint hairline flow lines and crack-like ridges from the wax flowing under the stamp.
5. **The relief.** Raised about 0.5–0.8 mm, with soft rounded tops and edges. The top faces are whiter than the field (228,222,233 against 192–211) because they face the key.
6. **Camera.** Near top-down, with a slight tilt. There is no visible DOF falloff and no grain worth copying.

## Most likely process

This is a straight product photo: a real wax seal on off-white card, lit by window light or one large softbox from the upper right, with no post beyond mild grading. In CG, that means a real-scale seal mesh (about 34 mm) in a short-scatter SSS wax material, one big area light and a dim world.

## Techniques to use

- **Seal body as a live heightfield in Geometry Nodes.** A dense grid gets its z from three parts: rim, field and emblem.
  - Rim: a radial profile, bead height and width, plus an irregular noise-warped outline and a lobe bulge.
  - Field: a dished flat disc.
  - Emblem: raised relief, added on top.
  - VisitLab builds the rim the same way, with a displacement map that is whiter at the seal border. A heightfield keeps every value live and tunable. The camera looks from above, so a heightfield never shows its lack of overhang.
  - Source: https://visitlab.cineca.it/index.php/2016/04/21/how-to-a-sealing-wax-stamp-animation-in-blender/
- **Swappable emblem.** The GN group takes an **Object input "Emblem"** and fits it to **Emblem Size** (mm, from its bounding box).
  - Curves (the Wonder logomark SVG, or any SVG): height = profile(distance inside the outline ÷ Bevel), from Proximity to the curve edges. This is the eclipse-glow inflate trick. It gives a true bevel with no Bevel-modifier overlap holes. Controls: **Relief** (height), **Bevel** (width), **Bevel Shape** (0 chamfer … 1 round).
  - Meshes (any model): a top-down Raycast gives the height, then Blur Attribute softens it.
  - Blendergrid does SVG → GN curves → mesh with a raycast: https://blendergrid.com/articles/svg-in-geometry-nodes
- **Wax material: Principled, Random Walk SSS, weight 1, short scale.** Scale 1–2 mm, radius near grey, about (1, 0.8, 0.7). The 5 mm default would make the ~0.7 mm relief glow. Roughness is about 0.4 for satin; no source gave a number, so the test render decides. The field is a touch glossier than the rim; the wax goes matte before pressing. Micro detail goes in a shader Bump: fine noise at under 0.05 mm amplitude, plus Voronoi-edge hairline flow lines on the field.
  - Sources: the local manual (`reference/manual/.../principled.rst`), https://blenderartists.org/t/cycles-subsurface-scattering-tips/1350174, https://www.blendernation.com/2022/05/22/how-to-make-a-procedural-wax-material/, https://en.wikipedia.org/wiki/Sealing_wax
- **Lighting (corrected after v02).** The shadow edge in the reference is hard (~10 px, 204→73 at row 900) with a core of 45–55 L, about 90 px wide. So the key is a *small* source at a low ~30° elevation, with moderate fill. Originally: one large area key, upper right, at about 45° elevation, with size about 3–4× the seal for soft shadows. Add a dim neutral world for fill and a matte off-white paper plane. This is the rule from knowledge `cycles.md`: set the paper to 1.0–1.05 raw, or the contact shadow clips.
- **View transform:** Khronos PBR Neutral, so the lilac stays lilac. AgX greys pastels (`colour.md`).

## Rejected approaches

- **Fluid sim for the blob** (VisitLab): slow, not live, and hard to tune. A noise-warped outline gives the same read from above.
- **Boolean of an extruded logo:** hard edges. Bevel-modifier overlap holes appear on the logomark above 0.03 × its width (`geometry.md`).
- **Displacement textures from an image:** the emblem would have to be rasterised for each swap, and the bevel control would be lost.
- **Volume-to-mesh SDF for the whole seal:** lumpy without extra smoothing, and not needed for a top-down heightfield. Keep it as a fallback if rim overhang ever matters.
- **Christensen-Burley SSS:** less accurate on thin curved relief. Use Random Walk.

## Numeric targets

sRGB, sampled from `ref_clean.png` (1212×1442).

| Region | RGB |
|---|---|
| Paper | 216–225, 205–217, 208–222 (warm off-white) |
| Field, lit centre | 192–211, 184–203, 200–216 (B > R > G) |
| Relief tops | about 228, 222, 233 |
| Outer rim, shadow side (left) | about 93, 79, 105 (saturated violet, not grey) |
| Rim, lit side (right) | about 191, 184, 200 |
| Cast shadow core, left of the seal | about 63, 48, 49 |

- Seal outer width is about 90% of the frame width. The seal is slightly oval, about 1100 × 1000 px.
- Rim bead width is about 10–12% of the seal diameter. The stamped field diameter is about 78% of the seal width.
- The emblem spans about 55% of the seal width.
- Shadow direction: lower-left. Relief highlights: upper-right edges.

## Open questions

- SSS scale: at 1 mm vs 2 mm, does the relief keep crisp form, and do the shadows go violet?
- Roughness 0.35 vs 0.5 for the satin read.
- Does a heightfield rim read as rolled, or does it need a steeper inner wall?

## Sources

Read:
- https://visitlab.cineca.it/index.php/2016/04/21/how-to-a-sealing-wax-stamp-animation-in-blender/
- https://blenderartists.org/t/is-there-a-way-to-smooth-out-volume-to-mesh-geometry-node/1467656
- https://blendergrid.com/articles/svg-in-geometry-nodes
- https://en.wikipedia.org/wiki/Sealing_wax
- https://stampdesign4u.co.uk/blogs/news/what-is-sealing-wax-made-of
- https://blenderartists.org/t/cycles-subsurface-scattering-tips/1350174
- https://www.blendernation.com/2022/05/22/how-to-make-a-procedural-wax-material/
- https://www.pelargondesign.com/blogs/how-to-use-wax-seals/how-to-make-perfect-wax-seals-step-by-step-tutorials-troubleshooting
- https://olivepaperieco.com/blogs/news/wax-sealing-technique-7-small-adjustments-that-make-a-big-difference
- https://blenderartists.org/t/candle-material/615753
- Local: `reference/manual/manual/render/shader_nodes/shader/principled.rst`, `reference/dev-docs/docs/release_notes/5.0/cycles.md`, `reference/api-dump-5.2` (SDF grid and Principled nodes)

Snippets only (the fetch failed):
- https://pressbooks.cuny.edu/waxseal/chapter/what-is-sealing-wax/
- https://coracreacrafts.com/blogs/inspiration-nook/wax-seal-guide-beginners
- https://developer.blender.org/T81602
- YouTube: 0qPyZiwxFes, Fy115tCg0As

Found nothing:
- Blender Stack Exchange and ArtStation/80.lv wax-seal breakdowns.
- A measured mean free path for sealing wax.
- Wax roughness values.
- Proof that the stamp polishes the field.
