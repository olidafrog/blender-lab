# Review: v06

## Score: 6.1 / 10

## What works
- The ink now has a halo. Edge row at y=800 goes 204 → 140 over about 8 px, with a soft shoulder before the core. It reads as a print seen through haze, not a sticker. This was v04's top problem, and it is mostly fixed.
- Ink has a cool blue-black bias (about 85/85/95). The face is cool (210/211/215). The colour logic is now correct.
- The line screen is readable in the logo crop as a diagonal hatch. It is an improvement on v04's felt texture.
- Slab-to-sweep separation is a little better: face 210 against sweep 186–195 (v04: 211 against 207).

## Top problems (ranked by impact)

1. **The ink density gradient is still there.** Top of the left stroke is ~124. The bottom is ~85. The dot is ~122 and the right stroke bottom is ~83. It looks like a vertical fade in the light or the mask, not ink. Ink is a flat solid in every reference.
   *Fix:* find the source. It is either the key light falloff through transmission or a gradient in the veil. Clamp ink coverage to a constant and hold the target at ~95 sRGB across all glyphs. Check the result with a luminance probe at four points.

2. **The screen dies in the detail crop.** At 1:1 the inside of the glyph is random speckle. You cannot count lines. In ref crop1, the lines stay crisp and regular right through the blur.
   *Fix:* cut the speckle amplitude by another 50%. Harden the line threshold. Sample the screen after the depth blur, not before, so the lines stay sharp over the soft edge.

3. **The plastic has no specular life.** The face is a flat matte card from edge to edge. You can't see a sheen, a grazing highlight or roughness variation. It looks like painted board.
   *Fix:* add a long strip softbox at a grazing angle from the upper left. Set coat roughness to 0.4–0.5 so a broad satin band crosses the upper third.

4. **The surface texture is still a diagonal twill.** The edge crop shows regular woven stripes, like canvas. This was flagged in v04 and has not changed.
   *Fix:* replace it with isotropic fine noise (~0.1 mm). Drive bump at 0.02–0.04 and roughness ±0.1 from it.

5. **The slab is still thin, and the edge is inert.** It reads as 3–4 mm, and the side face is a dull grey band. "Thick-ish" wants 6–8 mm, a bevel catch-light, and some internal glow or a darker transmitted core on the edge.

6. **No tracking dots, and no toner dropout on the edges.** These are cheap, and they are what make ref1 and ref4 feel like printed matter.

## To reach 8.5+
Make the ink flat and dense. Make the line screen legible at 1:1. Add a satin sweep and isotropic grain to the plastic. Make the slab thicker with a lit edge. Fixes 1–3 get this to about 7.3.

## Lockup test (not scored)
The system holds up, and it flatters the material more than the lone logo does. The blue panel with knocked-out type, the red rule and the small mono text all read as print under haze. The vertical sheen on the blue block is the specular life v06 lacks. Weak points: the green is a pastel, not fluoro, so it needs emission and a halo. The line screen disappears on the coloured inks. Small text blurs close to illegible, so scale the depth blur down for small type or per layer.
