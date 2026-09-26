# v2_20_hq — adversarial review

Bar numbering as before: **1** = tall left upright, **2** = tall centre upright, **3** = short slab
under bar 1, **4** = lower-centre slab, **5** = lower-right slab. **Peanut** = top-right figure.
Coordinates are pixels in the 1440×1440 render, origin top-left.

Verdict up front: the **band work landed** — bar 3's rim and most of bar 1's flank are now
continuous nested ribbons, and the poster-field fault is genuinely dead. But the **three floaters
that were ranked 2 and 5 last round are all still on screen, unchanged**, and the smoothing that
killed the bands also killed detail: measured edge density on lit pixels **fell** from 12.0 to
**10.9** against v1's **15.1**. The frame got cleaner and blander at the same time. Priority 1
still fails.

Measured this round: peak 255, **0.103%** of pixels >250 (was 0.164 — target met), 0.147% >240.
Background mean **0.70** sd **1.12** over three corner patches. Flatness test from last round's
item 4: of **475** 40×40 blocks on the glyph, **2** have luma sd < 2.0, both in bar 4's red lobe at
(440,1040) and (440,1080). That test is passed.

---

## 1. Artifact check by location

### Fixed — credit where due

- **The comb is mostly gone.** Bar 3's upper rim (crop 180–460, 820–930 at 400%) is now dozens of
  thin nested ribbons with soft boundaries and **no stepped terminations anywhere**. This is the
  region that failed three reviews running. It now looks like a prism edge.
- **Poster fields gone.** 473 of 475 glyph blocks clear sd 2.0. The solid vermilion lobe, the khaki
  dome and the cream bevel are all broken up. The nested V-contour terracing in bar 4 is gone.
- **Clipping down while coverage held.** 0.164% → 0.103% >250. Exactly the ratio asked for.
- **Peanut silhouette still clean.** Waist to bulb at 700%, no combing.

### Faults, worst first

1. **The floating oval is still there — fourth review running.** A connected-component scan at
   luma > 25 finds it as a **fully disconnected 687-pixel blob at (799,764)–(837,789)**. It is now
   magenta-into-purple rather than blue, with a soft red crescent above it at (770–800, 742–762).
   It sits in a pure-black interior void with no surface under it. Making the emitters
   reflection-only did not remove it, so the source is **not** a transmission path — it is reaching
   camera some other way. This is still the one element a viewer cannot explain, and it is the
   single reason the frame cannot be shipped.

2. **The rainbow chip at bar 5's lower-left is still there.** (865–930, 1258–1315) at 800%: a
   parallelogram of hard parallel green / yellow / red / cyan stripes with a **crisp straight upper
   edge and a blunt square termination**, lying in black. Unlike the oval it *is* topologically
   connected to bar 5, so it is geometry, not a light — a stray sliver or a bevel flap at the slab's
   lower-left corner. It still reads as a sticker dropped on the frame.

3. **Eight more disconnected components.** Same scan, all separated from the glyph: (159–195,
   845–861) a soft red crescent 248 px off bar 3's left tip — the most visible of these; (815–825,
   538–576) 154 px; (395–400, 427–453); (775–785, 242–261); (667–679, 1073–1084) and (683–689,
   1078–1093) as a pair; (1110–1118, 1159–1170); (824–828, 618–640). Individually dim. Collectively
   the frame has **ten unexplained objects floating in the black**.

4. **The key still reads as a rectangle.** Crop 180–420, 90–240 at 400%: a **fully clipped white
   bar with hard vertical terminations at x≈255 and x≈345**, sitting *outside* bar 1's silhouette,
   inside a glow with a **flat top and straight vertical sides** running (255,140)–(345,195). It is
   the softbox, in shot. There is also a small floating red dash at ~(352–362, 183–188). Item 5 of
   last round was not actioned.

5. **The kickers are thinner but still light sabres.** Bar 4's lower-right (620–840, 1120–1320 at
   400%): the core is now **4–6 px** instead of 8–12 — progress — but it is still **fully clipped,
   completely achromatic, of near-constant width along its whole run, with a 35–45 px soft skirt**.
   There is **no chroma fringe on either side anywhere along it**. Bar 5's lower-right (1060–1140,
   1200–1290) is identical. The brief was a hairline *with colour in it*; only the width half
   arrived.

6. **The dust and smudge read as damage, not handling.** On the peanut's waist (1120–1260, 300–400
   at 700%) the smudge is a **magenta blotch ~25×25 px at (1180–1205, 342–368)** with mottled
   hard-ish interior — it reads as a bruise or a compression smear, not a fingerprint. The motes
   near it are **light green dashes** on a cyan field, and inside bar 4 at (658–685, 1218–1258)
   they are a scatter of **bright yellow dots** that read as hot pixels. Real dust on glass is
   achromatic and darker than what it sits on; these are coloured and several are brighter.

7. **Detail density regressed.** Mean |gradient| over lit pixels: v1 **15.1**, v2_15 **12.0**,
   v2_20 **10.9**. Strong-edge fraction: v1 0.169, v2_20 0.134. Blurring the panel removed the
   bands and a third of the events with them.

### The tangent line — not counted

Withdrawn again, as agreed. Bar 4's bottom-left tangent still runs near-vertical; the optional 4–6°
Z rotation would still help and still costs nothing.

## 2. Glass realism — **5.5 / 10**

Up half a point. The contamination and the poster fields are gone; what is left is a shape-shaped
gradient.

- **There is no wall.** This is the biggest single miss and it has not been named before. In
  `v1_final` every edge carries a **double contour** — you see the outer surface, then the inner
  surface of the same wall a few pixels inside it, then what is behind the far wall. That double
  line is what tells the eye "this is a solid thing with a skin." In v2_20 every edge is a **single
  silhouette filled with colour**. `ref_ring` does the same thing v1 does: the inner bore shows its
  own rim inside the outer rim. Without that read, no amount of spectrum will make this perspex.
- **The peanut is airbrushed.** Crop 1000–1300, 40–300 at 300%: two broad smooth fields, one green,
  one blue, one soft cyan transition, one straight white streak. Four events in 78,000 pixels.
  `ref_ring` at the same relative scale carries surface scuff, a far-wall reflection, a caustic arc
  and dust.
- **Nothing in the frame is out of focus.** 0.42 m of depth, an 8°/−4°/−14° tilt, and every pixel
  equally sharp.
- In its favour: bar 2's flank (560–900, 380–780) is still the best thing here and got better — the
  tapering core, chroma either side, the elbow secondary, and now ribbon structure on the right
  cheek. If the whole frame matched this crop, it would score 8.

## 3. Style match to v1 and refs — **5.5 / 10**

Flat. Different failure from last round, same distance from target.

- Mean saturation on lit pixels: v2_20 **0.743**, v1 **0.804**. So the problem was never
  saturation — I was wrong about that last round. The problem is **where the colour sits**. v1 puts
  0.80 saturation into thin ribbons over a dark chromed body; v2_20 spreads 0.74 evenly across
  every square inch.
- Lit-but-dark fraction (luma < 40): v1 **0.329**, v2_20 **0.272**. v1 keeps a third of the object
  in near-black rest. Raising the panel's continuity filled in the rests.
- v1's speculars are **tiny gold points, 3–5 px**. v2_20's are **200–400 px straight streaks**.
  Compare bar 2's crown in each: v1 has a dotted broken highlight, v2_20 has a bar.
- `ref_ring` measures mean sat 0.368, strong-edge fraction 0.054 — a mostly neutral silver object
  with the spectrum in narrow arcs. Neither v1 nor the refs are rainbow objects.
- The peanut remains the closest to reference in silhouette and the furthest in surface detail.

## 4. Compositing — **6.0 / 10**

Flat. The invisible half is right; the visible half is unchanged.

- Grain correct: mean 0.70, sd 1.12. Veiling glow present. Clipped share now well judged at 0.103%.
- **Every flare is still geometric.** Flat-topped box above bar 1, straight-sided constant-width
  bars at bars 4 and 5, hard terminations on all of them. No optic in the world makes a rectangle.
- **Still no depth cue of any kind.** No defocus, no atmospheric falloff, no size-graded bloom.
  Three of the four things that would make this read as a photograph are free and none are present.

## 5. OVERALL — **6.0 / 10 — REJECTED**

Net zero against v2_15. Bands fixed, floaters untouched, richness down.

---

## 6. Ranked changes

1. **Kill the ten floaters, and verify with the scan, not by eye.** Run a connected-component
   labelling on the render at luma > 25. Every component other than the three glyph bodies
   (274k, 273k and 130k px) must be gone. Priority targets: the oval at **(799,764)–(837,789)** and
   the crescent at **(159,845)–(195,861)**. Reflection-only did not kill the oval, so try in this
   order: (a) set **Ray Visibility → Camera, Glossy, Transmission, Diffuse and Scatter all off** on
   every emitter, leaving only Light contribution; (b) if it survives, clamp **indirect light to
   4.0** and re-render, which will tell you whether it is a caustic spike; (c) if it *still*
   survives, it is geometry — isolate and delete. The chip at **(865–930, 1258–1315)** is connected,
   so it is a mesh fault: select bar 5, check for a loose face or a non-manifold bevel sliver at the
   lower-left corner.

2. **Give the glass a wall.** This is the realism unlock, worth more than everything else combined.
   The object currently refracts like a solid block of coloured gel. Raise **max transmission
   bounces from its current value to 32** (and total bounces to 40) so the far inner surface images
   through the near one, and add a **second, inward-offset shell at 6–10 mm** inside the outer skin
   if bounces alone do not produce it. Test: on bar 2's left edge at (500–560, 400–700) and on the
   peanut's outer curve at (1250–1300, 150–450), a 400% crop must show **two distinct contour lines
   4–12 px apart**, not one.

3. **Put colour in the rim and let it vary.** Keep the 0.06 m width. Give each kicker a **spectral
   emitter** — three offset strips at ±1.5 mm tinted warm / neutral / cool rather than one white
   one — and break its length with a **noise-modulated intensity mask at 0.3–0.5 amplitude and a
   150–250 px period** so the core pulses instead of running constant. Rotate from 15° to **25–30°
   behind**. Test at (620–840, 1120–1320): the core must vary between **2 and 6 px** along its run,
   and at least 40% of its length must carry a visible warm or cool fringe within 3 px of the core.

4. **Stop the key reading as a softbox.** The glow at **(255,140)–(345,195)** has a flat top and
   vertical sides. Shrink the emitter footprint to under **60 px** as projected, replace the glare
   node's input with the object matte so the bloom comes off the glass and not off the lamp, and
   force the falloff radial. Clear the red dash at (352–362, 183–188) with the same emitter-
   visibility pass as change 1.

5. **Get the detail back without getting the bands back.** Mean |grad| on lit pixels must rise from
   **10.9 to ≥ 14.0** (v1 is 15.1). Do it with **events, not edges**: add a **large low-frequency
   noise bump to the glass surface at 0.002–0.004 m amplitude and a 0.05–0.10 m scale** so the skin
   ripples the refraction, and put **two or three small bright cards at 0.05–0.10 m** into the
   reflection-only set to give the body specific things to reflect. Do **not** re-sharpen the panel.
   Also aim the lit-but-dark fraction back up from **0.272 to ~0.32** — let a third of the body rest.

6. **Redo the contamination, and add defocus.** Make every mote **achromatic and 25–40% darker**
   than its surround — no yellow dots, no green dashes. Replace the magenta blotch at
   (1180–1205, 342–368) with a **low-contrast roughness-only smudge**: no colour shift at all, just
   roughness 0.25 over a 60–150 px soft-edged patch, so it shows as a dulled highlight rather than a
   stain. Then add a **shallow defocus, f/8-equivalent, focused on bar 2's front face**, so the rear
   of the 0.42 m slab and the peanut soften by 2–4 px. That single change buys more photographic
   read than all the glow work so far.

Optional, unchanged: a **4–6° Z rotation** to take bar 4's bottom-left tangent off vertical.

SCORE: 6.0
