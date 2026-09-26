# v2_22_hq — adversarial review

Bar numbering as before: **1** = tall left upright, **2** = tall centre upright, **3** = short slab
under bar 1, **4** = lower-centre slab, **5** = lower-right slab. **Peanut** = top-right figure.
Coordinates are pixels in the 1440×1440 render, origin top-left.

**Verdict up front: the floaters are dead.** The oval, the crescent and the softbox rectangle are
gone, verified by scan, not by eye. That is the fault that blocked four reviews and it is now
genuinely closed. The frame contains nothing a viewer cannot explain.

What is left is a different problem, and it is now the only one that matters: **this is a flat
rainbow poster, not a photograph of glass.** Detail density at matched resolution is **4.21**
against v1's **8.63** — less than half. Priority 1 passes. Priorities 2 and 3 fail.

---

## 1. Artifact check by location

### Scan result — connected components, luma > 25

1013 components. Bodies: **239,265** (bars 1+3), **220,276** (bars 2+4), **128,665** (peanut),
**25,884** (bar 5, now separated because the 4–5 bridge fell below threshold — that is rest, not a
fault). Largest stray **420 px**, and it is not in black.

The luma metric under-reads deep red (a 150,20,20 vermilion is luma 32; a 110,20,20 is luma 23), so
the luma scan splits red fields and reports false strays. Re-run on **max(R,G,B) > 25**:

- **784 components. Three bodies. Largest stray 227 px.**
- v2_20 on the same mask: largest strays **895 px at (794,763)–(840,792)** — the oval — and
  **621 px at (157,838)–(208,863)** — the crescent. **Both are absent from v2_22.** Confirmed.
- The remaining strays are all explicable. The chain at **x 1085–1107, y 823–1002** (227, 50, 46,
  35, 23, 22 px) is the *red side of bar 5's left chromatic fringe*, broken into dashes where the
  blue side dips below threshold — crop (1040,800)–(1180,1020) at 350% with 3× exposure shows a
  continuous cyan-core / red-fringe edge, which is correct dispersion.
- The 124 px at **(508,864)–(532,876)** and the mottle above bar 4's crown are sub-threshold sampler
  noise, invisible at normal exposure. Ignore.

**No unexplained objects. Priority 1 passes.**

### Still wrong — worst first

1. **The comb is back, and it is the exact fault the user circled.** Crop **(230,800)–(400,900) at
   700%**: bar 3's upper-left rim is a picket of **hard vertical red / magenta / yellow / white
   stripes, 2–6 px wide, all terminating on one straight horizontal cut at y≈865 with square blunt
   ends**. No prism edge does that — a real one fans and fades. Same fault on bar 1's crown, crop
   **(150,150)–(330,330) at 500%**: short horizontal dashes of white, red and cyan along the top
   bevel, each with a **squared-off end**, laid over a smooth field. This was the circled complaint
   on v1 and it survives here.

2. **The bar-5 chip still reads as a decal, corner-prism explanation notwithstanding.** Crop
   **(840,1230)–(960,1340) at 400%**. I accept the diagnosis — it does come from the back panel
   through the corner. It still reads wrong, for three reasons the physics does not excuse: the
   band boundaries are **hard, not graded**; the far end is a **blunt square cut** rather than a
   fade; and the stripe axis bears **no relation to the corner's edge direction**, so the eye cannot
   attach it to the geometry that made it. A real corner prism throws a fan that is anchored at the
   corner, widest and dimmest at the far end. This is a parallelogram of stripes lying in black.

3. **Poster fields are returning.** Of **267** 40×40 blocks with >90% glyph coverage, **6** have
   luma sd < 2.0 — 2.2%, against 0.4% last round. Locations: **(1080,200)** and **(1080,240)** in
   the peanut's green dome, **(320,760)** and **(320,800)** in bar 1, **(440,1040)** and
   **(440,1080)** in bar 4's red lobe. Two of these are new and they are on the peanut, the element
   closest to the refs in silhouette.

4. **The contamination still reads as damage.** Crop **(650,1050)–(760,1150) at 400%**: a run of
   **bright orange blobs, 10–20 px, at (692–706, 1080–1121)**, each *brighter and more saturated*
   than the vermilion they sit on. Real dust on glass is achromatic and darker than its surround.
   These read as blown highlights or hot pixels.

### Fixed — credit where due

- **Oval, crescent and softbox rectangle: gone.** Crop **(120,80)–(420,260) at 300%** — the flat-
  topped white box above bar 1 is replaced by nested spectral ribbons and a soft radial veil. The
  square terminations at x≈255 and x≈345 are gone. That change worked.
- **The kickers carry colour.** Crop **(620,1120)–(860,1330) at 300%**: the core now tapers from
  ~5 px to a point, and there is a **warm amber fringe on both sides along the full run** with a
  soft asymmetric skirt. It reads as an anamorphic streak rather than a light sabre. Change 3 of
  last round landed.
- **Defocus is present.** The peanut and bar 5's rear edges are visibly softer than bar 2's front
  face. First real depth cue in the series.
- **Clipping and grain held.** Peak 254, **0.102%** >250, background mean **0.72** sd **1.15** over
  four corner patches. All correct.

### Tangent line — not counted, as agreed.

## 2. Glass realism — **6.0 / 10**

Up half a point on the defocus and the kicker colour. The core miss is unchanged.

- **There is still no wall.** Change 2 of last round — transmission bounces to 32 — was made, and it
  did not produce the double contour. Test crop **(1200,120)–(1330,470) at 300%** on the peanut's
  outer curve: **one silhouette edge, then a 30–50 px smooth green-to-cyan gradient, then blue.**
  No inner surface line anywhere. Same at bar 2's left edge, crop **(480,380)–(600,700) at 400%**:
  soft 20–40 px parallel bands, no second contour. `v1_final` shows the inner wall 4–12 px inside
  the outer one on every edge; `ref_ring` shows the bore's own rim inside the outer rim. Bounces
  were not the mechanism. **The geometry is a solid; it needs an actual inward-offset shell.**
- **Detail density regressed again.** Mean |gradient| on lit pixels: **v1 downsampled to 1440 =
  8.63**, v2_20 = 5.08, **v2_22 = 4.21**. Strong-edge fraction: v1 **0.073**, v2_22 **0.017** — a
  quarter. `ref_ring` measures 7.05 / 0.054. The f/5.6 defocus bought a depth cue and paid for it
  with 17% of the remaining detail, on an image that could not afford it.
- **The peanut is still airbrushed**, and now has two certified-flat blocks in it.
- In its favour: bar 2's flank and bar 1's crown are the best surfaces in the series so far, and the
  spectral fringing on bar 5's left edge is textbook correct.

## 3. Style match to v1 and refs — **5.5 / 10**

Flat. The diagnosis from last round holds exactly.

- Mean saturation on lit pixels: v2_22 **0.755**, v1 **0.800**, `ref_ring` **0.336**. Saturation is
  not the problem. **Distribution is.** v1 puts 0.80 into narrow ribbons over a dark chromed body;
  v2_22 spreads 0.755 across every square inch of every face.
- Lit-but-dark fraction (luma < 40): v1 **0.183** at matched scale, v2_22 **0.220**. Closer than
  last round, but v1's dark is *structured* — black channels between bright ribbons — where v2_22's
  is a general dimming.
- v1's speculars are **3–5 px gold points**. v2_22's are 200–400 px streaks. Unchanged.
- Neither v1 nor the refs are rainbow objects. v2_22 is.

## 4. Compositing — **7.0 / 10**

Up a full point, and this is now the strongest of the four.

- Grain, clip share and veiling glow all correct and unchanged.
- **No flare is geometric any more.** The radial falloff on the key killed the box; the shortened
  kickers killed the square ends. There is not a straight-sided constant-width bar left in the frame.
- **Depth cue present** for the first time — the defocus works.
- Remaining: no atmospheric falloff, no size-graded bloom, and the kicker cores are still fully
  clipped along their whole length rather than clipping only at the brightest 20%.

## 5. OVERALL — **7.0 / 10 — REJECTED**

Up 1.0. The floaters are genuinely dead and the lighting is no longer visible in shot — both real,
both verified. The gap to 8.5 is now one thing wearing two hats: **the object has no wall, so every
surface is a gradient, so there is no detail for the eye to read as glass.** Fix that and the score
moves several points at once.

---

## 6. Ranked changes

1. **Give the glass an actual wall — as geometry, not as bounces.** Bounces at 32 did not do it, so
   stop trying. Solid-ify the mesh: duplicate each body, **inset/shrink by 8 mm**, flip normals, and
   join, so the ray crosses **four** surfaces instead of two. Set the enclosed volume to IOR 1.0
   (air). Test: a 400% crop at **(1250,150)–(1300,450)** on the peanut and at **(500,400)–(560,700)**
   on bar 2 must each show **two distinct contour lines 4–12 px apart**. This is worth more than
   everything below it combined.

2. **Kill the comb on the bevels.** Two named sites: **(240–300, 800–870)** on bar 3's upper-left
   rim and **(160–330, 170–260)** on bar 1's crown. The stripes are ray-bundle aliasing at a
   near-tangent bevel, so raise **transmission samples / light-path clamp on that pass** and add
   **0.5–1.5 px of shading-rate jitter**; if it survives, the bevel resolution is the cause —
   raise the bevel segment count from its current value to **24+** on the top and upper-left edges
   only. Test: at 700%, no stripe may terminate on a shared straight line, and no termination may
   be square.

3. **Get the detail back to v1's density.** Mean |grad| on lit pixels must rise from **4.21 to
   ≥ 7.0** (v1 is 8.63 at this size; `ref_ring` is 7.05) and strong-edge fraction from **0.017 to
   ≥ 0.045**. Do it with **events, not sharpening**: a low-frequency surface bump at **0.002–0.004 m
   amplitude, 0.05–0.10 m scale**, plus **three or four small bright cards at 0.05–0.10 m** in the
   reflection-only set so the body has specific things to reflect. Do not touch the defocus — keep
   f/5.6, it is earning its place.

4. **Break the remaining flat fields.** Six 40×40 blocks read sd < 2.0: **(1080,200)**,
   **(1080,240)**, **(320,760)**, **(320,800)**, **(440,1040)**, **(440,1080)**. Target **zero**
   blocks under sd 2.0 and none under sd 3.0 on the peanut. Change 3 should mostly do this; check it
   specifically at the peanut's green dome, which is the newly-regressed area.

5. **Make the bar-5 corner throw read as a corner throw.** Keep the mechanism, fix the shape. Soften
   the back panel's gradient edge so the band boundaries grade over **8–15 px instead of 1–2**, and
   push the panel **0.15–0.25 m further back** so the fan widens and dims with distance rather than
   ending square at **(930,1258)**. Test: the far end must fade to background over ≥ 25 px, and the
   fan must visibly widen from the corner outward.

6. **Redo the motes as dirt.** The blobs at **(692–706, 1080–1121)** are brighter and more saturated
   than the vermilion under them. Make every mote **achromatic and 25–40% darker** than its surround,
   4–10 px, and drive it through **roughness only** — no emission, no colour shift. Real glass dirt
   dulls a highlight; it never adds one.

SCORE: 7.0
