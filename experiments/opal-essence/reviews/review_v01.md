# Review — v01

1. **Score:** 5.3 / 10

2. **Targets**
- Background #000000: **hit**.
- Deep teal #162d30 at the left edge, but brown #451e1d over the parts: **partly hit**.
- Sage: #5a876a, too green and dark: **missed**.
- Cream: #eccd8e: **hit**.
- Amber: #facb93, peach: **missed**.
- Orange: best #f7ba83: **missed**.
- Pink: #fb8a8c, pastel: **missed**.
- Opal blue skin: none on the plate: **missed**.
- Micro-type cap height: about 12 px (0.6%): **missed**.

3. **What works**
- Depth diffusion: the big gear is nearly sharp, and the bar and dumbbell behind it melt, as in refs 02–03.
- The hue order runs teal → cream → peach → pink, in the ref 02 family. Blacks are clean.

4. **Problems, ranked**
1. **Whole plate: it reads as a lightbox with shadow puppets, not resin.** The gradient is flat, like an emissive card. The parts behind are dark silhouettes with no highlights. The plate has no thickness, no bright edges and no wet gloss. *Fix:* build a 6–10 mm slab with transmission 1.0, roughness 0.25–0.4 and volume scatter at density 2–6. Light it with 3–4 coloured area lights behind the parts, not with a gradient texture. Make the parts glossy and add a front key. Add a clear coat with a ripple bump at strength 0.02–0.05.
2. **Type and logotype: not moulded.** "Wonder" is a flat grey decal, cut off by the gradient. The top line has a broken glyph ("WONOER"). *Fix:* use raised resin geometry, 0.3–0.5 mm, with a 0.1 mm bevel so the key light draws highlight lines. Set the cap height to 20–30 px. Check the font's glyph map.
3. **Colour: no opalescence, and the palette is muddy.** There is no blue skin and no warm core. The teal goes brown over the parts, and the orange and pink wash to pastel. *Fix:* add a cool fresnel scatter term (#9fb8b7 at grazing angles). Saturate the back lights until the orange reaches #fca321 and the pink reaches #fe6f6b.

5. **Research check**
- The depth blur agrees with the research.
- The opalescence contradicts it: there is no blue skin and no warm core.
- The type contradicts "read mainly by edge highlights": it reads as a dark decal.
- "Hard strip lights for wet highlights" only partly holds: there is one strip, but no wet gloss.

6. **What 8.5 needs**
- A volumetric slab lit by real coloured back lights.
- Glossy parts behind the plate.
- Raised, readable type with highlight lines.
- A blue fresnel skin.
- Saturated orange and pink.
- Ripple, dust, scratches and fine grain.
