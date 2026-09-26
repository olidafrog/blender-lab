# v2_10_hq — adversarial review

Bar numbering: **1** = tall left upright, **2** = tall centre upright, **3** = short lower-left slab
(under bar 1), **4** = lower-centre slab, **5** = lower-right slab. **Peanut** = top-right figure,
top bulb / waist / bottom bulb.

Verdict up front: v2_10 is a real recovery from v2_06 — the highlights are back, the colour is back,
and the frame has energy again. But the contamination pass overshot badly. The dust reads as a
starfield, not as dust, and it is the first thing the eye lands on at thumbnail size. Two of the
v2_06 geometry faults also survived untouched. This is not shippable.

Measured: peak 255, **0.154%** of pixels above 250, 0.215% above 240. Background outside the glyph
is **exactly 0.0 with 0.0 standard deviation** — the grain at 0.02 is not reaching the render, or is
being crushed by the S-curve.

---

## 1. Artifact check by location

**Genuine wins since v2_06:**

- Peanut rim combing: still gone. The waist silhouette is clean at 200%.
- Contour ringing inside bar 2: gone. The B-spline ramp killed the concentric lobes.
- Speculars exist. Bar 2's left flank carries a full-length clipped white stripe; bar 1's crown and
  the peanut's top bulb both hold blown cores.

**Faults, worst first:**

1. **Dust reads as a starfield — everywhere, but worst on bar 2's crown, the peanut's top bulb, and
   bar 1's mid-section.** At 200% the specks are 2–3px hard white dots at luma 150–255 sitting on a
   local background of ~62. That is a 2.5–4× contrast step. Real dust on glass is *darker* than what
   is behind it, or a low-contrast smear — it occludes, it does not emit. Two secondary tells make
   it worse:
   - **They clump.** Bar 2's crown has a distinct swarm of ~40 specks in a 120px cluster, with
     empty surface either side. Bar 1's crown has the same. Bar 5's lower-left has a dense knot.
     That is Voronoi/Noise cell structure showing through, not random contamination.
   - **They follow the UV.** On bar 2's dome and the peanut's top bulb the specks trace curved arcs
     parallel to the surface gradient. Real dust does not know about the object's parameterisation.
   - **They sit in black voids.** On bar 1's mid-section and bar 5's lower-left the specks appear in
     regions that are otherwise pure black interior, so they float in space with no surface under
     them. They read as fireflies.
   - **They survive the thumbnail.** At 200px wide I can still see them. `ref_ring` and `ref_puck`
     both go clean at that size. This is the test the brief set and it fails it.

2. **Step-terraces are still on bar 1's top-left crown.** Exactly the spot the user circled in
   `v1_annotated`, and exactly the fault flagged in the v2_06 review. Four horizontal
   yellow/black/blue bands with hard straight upper and lower edges, stacked like a staircase down
   the crown. Narrower than v2_06's blocks, but still hard-edged and still reading as broken
   geometry. The B-spline ramp fixed the interior terracing and did nothing for this. Smaller
   instances on bar 2's top-left shoulder and along bar 3's upper-left rim.

3. **Octagonal faceting persists on bars 3, 4 and 5.** Bar 4's bottom-left and bottom-right corners
   are straight 45° chamfers meeting at hard vertices — the silhouette is a cut octagon, not a
   superellipse. Bar 5's bottom-right corner is the same. This was point 4 on the v2_06 list and was
   not actioned. It is the single clearest "this is CG" signal in the frame, because no real object
   has a corner like that.

4. **Bar 4's bottom bevel is a flat cream slab.** A large uniform near-white field with a hard
   straight red/green line above it and no internal variation. Same fault as v2_06's bronze bevel,
   relocated. Bar 5's yellow-orange wedge is the same — a flat poster fill with a hard green edge.

5. **Bar 2's dome is still khaki.** The saturation lift to 1.2 helped the reds elsewhere, but where
   the red and green lobes overlap on bar 2's upper third the result is still olive/mustard. No
   reference has this colour.

6. **The key specular is a perfect parallel-sided stripe.** Bar 2's white core is a ruler-straight
   band of constant width running the full height with no break, no pinch, no variation. It reads as
   a rendered area light, not as a reflection of a strip light in a surface with curvature. v1's
   speculars broke up, tapered and pinched at the corners.

7. **Scratches: correct, and the one thing here that works.** Faint diagonals across bar 2's dome
   and bar 1's right flank, low contrast, visible only at 100%. This is the density the dust should
   have been.

## 2. Glass realism — **5.5 / 10**

Up from 3.5. The clipped white does the heavy lifting: the object now has the luminous range a
photograph of perspex has, and the peanut's top bulb genuinely reads as a solid with a lit shoulder.

Against it:

- **The contamination actively destroys the illusion.** A photographed object gets *less* believable
  when covered in emitting white dots. It now reads as glass composited over a star field.
- **No rim caustic.** v1's defining feature was a hairline of clipped white running the whole
  silhouette — the bright edge where the glass turns away. v2_10 has bright *ribbons* inside the
  form but the outer edge mostly fades into black over 3–4px. That edge line is what makes v1 look
  photographed and v2 look rendered.
- **Interiors are airbrushed.** Bars 1, 2 and 4 are smooth gradient meshes. No internal reflection
  stack, no far wall, no secondary caustic. `ref_puck` has four or five layers of event inside it.
- **The octagon corners.** See above.

## 3. Style match to v1 and refs — **6.5 / 10**

Recovered: the reds are red again, the whites clip, the spectral bands are back to being narrow and
fast on bar 1's left flank and around the peanut's rim. The peanut is the best object in the frame
and is close to `ref_ring`.

Still short of v1's 8.6:

- v1's ribbons were *thin, layered and multiple* — three or four nested spectral lines per edge. v2's
  are single, wide and soft.
- v1's interiors had structure. v2's have gradients.
- The dust is a style departure in itself. Neither v1 nor any reference has bright specks.

## 4. Compositing — **6.0 / 10**

Better balanced than v2_06. Vignette at 0.15 is invisible in a good way. Glow halved is correct —
it now halates off the clipped cores instead of blurring mid-tones.

- **Grain is not there.** Background measures 0.0 mean, 0.0 stddev. The blacks are mathematically
  pure, which no camera produces. Combined with the pin-sharp white specks, the frame has noise in
  exactly the wrong place: on the subject instead of in the air.
- **Dispersion at 0.010** is still doing nothing measurable against spectral subject matter.
- **No atmosphere.** Nothing sits between camera and object — no veiling flare off the clipped
  highlights, no soft bloom skirt. "Dynamic realistic compositing" means the lens contributes; here
  the lens is perfect.

## 5. OVERALL — **6.2 / 10 — REJECTED**

---

## 6. Ranked changes

1. **Rebuild the dust so it occludes instead of emits.** Cut the count by roughly 4× (target ~0.05%
   of surface area, not the current ~0.3%), drop each speck to 0.5–1px at 1440 by raising the noise
   scale ~3×, and flip the contribution: drive **transmission down to ~0.9 and coat roughness to
   0.5** at the speck, with **no** emissive or diffuse white. A speck should render 15–30% *darker*
   than its neighbourhood, never brighter. Break the clumping by driving the mask from a high-scale
   White Noise thresholded at ~0.995 rather than Voronoi cells, and map it in **generated/world
   space, not UV**, so it stops tracing the surface parameterisation. Verify: at 200px wide the
   specks must be invisible; at 100% they must be findable but unremarkable.

2. **Kill the crown terracing at bar 1 top-left.** The B-spline ramp fixed the interiors and not
   this, so the source is the emitter's own geometry, not the ramp. Move the banded panel **2× further
   behind the glyph** and **halve the band count** so each crown sweeps 4–6 bands instead of landing
   on 2–3, and add a ~0.05 UV Noise warp on the panel so the band boundaries are not straight lines.
   Recheck bar 1 top-left, bar 2 top-left shoulder, bar 3 upper-left rim.

3. **Fix the octagon corners — third time of asking.** Raise bevel segments on bars 3, 4 and 5 from
   the current ~3 to **8–12**, or add one subdivision pass with a 30° crease angle. Bar 4's
   bottom-left and bottom-right and bar 5's bottom-right are the test cases. The silhouette must
   read as a continuous curve at 200%.

4. **Add the rim caustic.** This is what separates v1 from v2. Add a thin grazing-angle kicker: a
   narrow strip emitter roughly **1.5× the glyph height, placed 15–25° behind the object relative to
   camera**, at ~4× the key's intensity. Target a 1–2px clipped line along 40–60% of the outer
   silhouette, particularly bar 1's left edge, bar 4's bottom edge and the peanut's outer curve.
   Measured: clipped-pixel share should rise from 0.154% to about 0.25–0.30%, with the new hits
   landing on the silhouette rather than the interior.

5. **Break up the key stripe and the flat bevels.** Give the strip light a **gradient falloff along
   its length** (bright at one end, ~40% at the other) and put a subtle texture on it so bar 2's
   white core tapers and varies instead of running at constant width. Separately, bar 4's bottom
   bevel and bar 5's orange wedge need dispersion reaching into them — widen the IOR spread from
   0.36 to about **0.45** and check those two regions specifically for flat fields.

6. **Put the noise back in the air.** Grain 0.02 is not arriving — background measures exactly zero.
   Push to **0.035 applied after the tonemap** so it survives, and add a faint veiling flare of about
   **0.03 strength at a wide radius** keyed off pixels above 250, so the clipped highlights bleed a
   little haze into the surrounding black. Both changes should be measurable: background stddev
   above 1.5, and the black immediately around bar 2's specular should sit at luma 2–5, not 0.

SCORE: 6.2
