# v2_15_hq — adversarial review

Bar numbering as before: **1** = tall left upright, **2** = tall centre upright, **3** = short slab
under bar 1, **4** = lower-centre slab, **5** = lower-right slab. **Peanut** = top-right figure.
Coordinates are pixels in the 1440×1440 render, origin top-left.

Verdict up front: three of the six notes landed. The starfield is gone, the grain is real, the key
specular tapers. But the frame picked up **two new floating artifacts**, the **crown comb is still
there for the third review running**, and the interiors have got *flatter* — large hard-edged
poster fields of pure red, green and blue that no piece of glass produces. On the priority-1 test
(no artifacts) this still fails.

Measured: peak 255, **0.164%** of pixels >250, 0.232% >240. Background mean **0.82**, sd **1.27**,
max 6 over four sample patches. Grain confirmed arriving.

---

## 1. Artifact check by location

### Fixed — credit where due

- **Dust starfield: gone.** Two 200×200 sample squares at 500% (peanut top bulb 1020–1220, 80–280;
  bar 4 interior 430–630, 1080–1280) contain **zero** visible motes. Invisible at 200px thumbnail
  too. Over-corrected — see fault 6 — but the v2_10 complaint is dead.
- **Key specular now tapers.** Bar 2's core (crop 500–900, 400–800) narrows, bends and breaks
  toward the bottom instead of running as a parallel-sided ruler. Best single improvement here.
- **Peanut rim: still clean.** No combing at the waist at 500%. The silhouette from the top bulb
  through the waist to the bottom bulb is a continuous curve.
- **Scratches: right density.** Fine diagonals across bar 2's crown (620–700, 130–260), low
  contrast, findable at 100%, invisible at thumbnail. Keep exactly this.
- **Grain in the air.** Background sd 1.27 against v2_10's 0.0. The blacks breathe now.

### Faults, worst first

1. **Bar 1, top-left crown (80–320, 160–300): the comb is still there.** At 500% this is a stack of
   five to seven hard-edged parallel bars — cyan / yellow / magenta / white — each with a straight
   upper and lower edge and a **stair-stepped, notched right-hand termination**. That notched
   termination is literally the comb the user circled in `v1_annotated`. Moving the panel 5.5 m → 8 m
   did not soften the band edges; it made each band subtend a smaller angle, so the crown now samples
   the *edges* rather than the bodies. The same fault, smaller, runs along bar 3's upper-left rim
   (210–420, 850–910).

2. **Floating rainbow chip off bar 5's lower-left, (865–930, 1255–1310).** A detached parallelogram
   of hard parallel colour stripes — green / red / cyan / yellow — with crisp straight edges and a
   sharp corner, sitting in black with **no surface under it and no contact with the glyph**. It
   reads as a sticker dropped on the frame. This is the single most damaging thing in the image: it
   is the one element a viewer cannot explain.

3. **Blue bokeh oval at the bar 4 / bar 5 junction, (780–850, 745–800).** A clean-edged, uniformly
   saturated blue ellipse ~70×55 px floating in an otherwise pure-black interior void. Same position
   as the grey blob in v2_10, now brighter and more obviously wrong. Either an emitter seen through a
   thin section, or a backdrop object reaching the camera through a specular path.

4. **The new rim lines are neon tubes, not caustics.** Bar 4's lower-right (crop 640–820, 1130–1300)
   carries a **fully clipped white band 8–12 px wide with a 40 px soft skirt**, razor-straight, of
   constant width, and **completely achromatic**. Bar 5's is the same. v1's rim was a 1–2 px hairline
   that varied along its length and carried a spectral fringe on both sides. As built these read as
   light sabres taped to the edge — a new artifact, not the requested feature. They also cover only
   about 20% of the silhouette; the rest of the outline still fades into black over 3–4 px.

5. **The key emitter is visible as a rectangle.** Above bar 1's crown (210–400, 110–220) sits a glow
   with **straight vertical sides and a flat top** — the softbox's own shape, ~180×110 px, floating
   *outside* the silhouette with a hard horizontal streak crossing it. Real bloom is radial. This
   reads as the light being in shot.

6. **Interiors have got flatter, not richer.** Bar 1's mid-section holds a solid vermilion lobe
   ~90×180 px with a hard green outline and **no internal variation at all**; bar 2's dome is still
   the khaki / mustard field with no reference support; bar 4's bevel is still a cream slab. Bar 4's
   interior (430–630, 1080–1280) shows **nested V-shaped contour steps** — visible terracing with
   discrete edges between cyan / teal / navy. Between the poster fields and the contour steps, most
   of the object now reads as a gradient-mesh vector illustration.

7. **Minor:** a magenta speck at ~(1185, 352) on the peanut's waist, sitting on nothing. Small, but
   it is the same class of fault as items 2 and 3.

### The tangent line — not counted

Accepted: the straight segment joining front-face arc to back-face arc on a tilted 0.42 m slab is
correct projection, and I withdraw it as an artifact. One composition note only: on bar 4's
bottom-left that tangent currently runs close to vertical, so it reads as a deliberate chamfer
rather than as a foreshortened curve. A 4–6° Z rotation would put it off-axis and the ambiguity
disappears. Optional.

## 2. Glass realism — **5.0 / 10**

Down from 5.5. The contamination is no longer fighting the illusion, but two things replaced it.

- **The surface has no event structure.** A 200×200 px square on the peanut's top bulb contains one
  soft green-to-blue gradient and nothing else. `ref_puck` at the same relative scale carries four
  or five overlapping layers — internal reflections, a far wall, trapped bubbles, surface scuff.
  Glass is busy; this is airbrushed.
- **Saturated flat fields kill the material read.** Pure R, pure G, pure B poster shapes with hard
  boundaries are a signature of an under-sampled dispersion stack, not of a prism. v1 never did this;
  its colour arrived as many thin adjacent ribbons whose overlap produced the richness.
- **The rim is a light, not a caustic.** See fault 4.
- Working in its favour: bar 2's flank (crop 500–900, 400–800) is genuinely good — tapering core,
  chroma fringes either side, a believable secondary reflection under the elbow. That region is the
  proof the setup can reach 8; nothing else in the frame matches it.

## 3. Style match to v1 and refs — **5.5 / 10**

Down from 6.5, and this is the regression that hurts most.

- v1's identity was **many thin nested spectral lines per edge** over a mostly dark, chromed body.
  v2_15 inverts that: wide flat colour over the body, few lines at the edges. Squint at the two side
  by side — v1 is a dark object with rainbow edges, v2_15 is a rainbow object. That is a different
  picture.
- v1's black was structural. Whole interior regions went to near-black and let the ribbons read. In
  v2_15 the bars are filled edge to edge with saturated colour, so there is no rest anywhere.
- `ref_ring` and `ref_puck` both keep large clean-ish neutral areas and put the spectral energy in
  narrow arcs. Neither is a poster.
- The peanut is again the closest to reference, and closer than in v2_10.

## 4. Compositing — **6.0 / 10**

Flat vs v2_10, moving in the right direction under the hood.

- **Grain delivered**: mean 0.82, sd 1.27. Correct amount — visible in the blacks at 100%, invisible
  at thumbnail.
- **Veiling glow delivered**: the black around bar 4's rim sits at luma 4–9 rather than 0. Good.
- Against: **every flare is geometric.** Rectangular softbox above bar 1, straight-edged white bar at
  bar 4, a hard horizontal spike crossing black. A lens does not produce hard edges. Nothing here
  reads as an optic between camera and subject.
- Still no depth. Everything is equally sharp at every distance; the object has an 8°/−4°/−14° tilt
  and 0.42 m of depth and the frame does not know it. A shallow defocus would do more for "dynamic
  realistic compositing" than any of the glow work so far.

## 5. OVERALL — **6.0 / 10 — REJECTED**

---

## 6. Ranked changes

1. **Kill the comb properly: stop using discrete bands.** The panel is still a set of hard-edged
   strips; distance does not fix a hard edge. Replace the banded texture with a **continuous
   colour ramp** (no stops closer than 20% of panel height) and blur the whole panel texture so no
   luminance edge on it is sharper than ~2° as seen from the glyph — at 8 m that is a blur radius of
   roughly **0.28 m in panel space**. Keep the noise warp. Test region: (80,160)–(320,300) at 500%
   must contain **zero straight hard-edged bars and zero stepped terminations**; recheck bar 3 at
   (210,850)–(420,910).

2. **Remove the two floating objects.** (a) The chip at **(865–930, 1255–1310)** — look for a stray
   loose face or a detached bevel sliver near bar 5's lower-left; select-linked the glyph and check
   the object count. (b) The blue oval at **(780–850, 745–800)** — camera-hidden is not enough for an
   emitter seen through glass. Turn **Visibility → Glossy and Transmission both off** on the kickers
   and the key strip, leaving only their light contribution, then re-render and confirm both regions
   are black. Also clear the magenta speck at (1185, 352).

3. **Make the rim a hairline with colour in it.** Reduce each kicker's emitter width by **3×** and
   its power by **50%**, and rotate them from 15° to about **25–30° behind** so they graze rather
   than face. Target a **2–3 px** core, not 8–12, covering **50–60%** of the outer silhouette instead
   of the current ~20%, with at least one visible chroma fringe on each side. Clipped share should
   *fall* from 0.164% to about **0.10–0.12%** while covering more outline — that ratio is the test.

4. **Break the poster fields: raise the spectral sample count.** The solid R/G/B lobes and the nested
   V contours in bar 4 are an under-sampled IOR stack, not a ramp problem. Raise the dispersion
   sampling from its current count to **24–32 wavelengths** across the 0.45 spread, and give the
   backdrop a gentle luminance gradient plus **5–8% noise** so each refracted field has internal
   falloff. Test: no **40×40 px** block anywhere on the glyph may have luma sd below **2.0**.
   Specific check regions: bar 1's red lobe, bar 2's khaki dome, bar 4's cream bevel.

5. **Stop the key reading as a rectangle.** The glow at (210–400, 110–220) has straight sides because
   the emitter's own shape is reaching the glare node. Shrink its footprint to under **60 px**, make
   the falloff radial, and if the shape persists, mask the glare input to the object matte so the
   bloom comes off the glass rather than off the lamp.

6. **Put a little dust back, and add smudge.** Zero motes in two 200 px samples is over-corrected.
   Raise density from **0.1% to ~0.5%** of cells, keep size at 1.5–2 mm, and make each mote **20–25%
   darker** than its surround. Separately add **3–5% coverage** of large soft smudges (60–150 px,
   coat roughness ~0.25) — that, not specks, is what makes `ref_ring` look handled. Both must stay
   invisible at 200 px.

Optional, composition only: a **4–6° Z rotation** to take bar 4's bottom-left tangent off vertical,
and a shallow defocus on the rear of the slab to let the 0.42 m of depth show.

SCORE: 6.0
