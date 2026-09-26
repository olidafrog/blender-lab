# v2_06_hq — adversarial review

Bar numbering: **1** = tall left upright, **2** = tall centre upright, **3** = short lower-left slab
(under bar 1), **4** = lower-centre slab, **5** = lower-right slab. **Peanut** = top-right figure,
top bulb / waist / bottom bulb.

Verdict up front: v2_06 traded one class of artifact for another, and in doing so it threw away the
two things that made v1 read as glass — blown speculars and crisp edges. It is softer, darker,
duller and flatter than v1. This is a regression, not a fix.

---

## 1. Artifact check

**Gone (genuine wins):**

- The fine jagged "comb" on the peanut rims — the two arrowed areas in `v1_annotated` — is
  essentially cleared. The waist silhouette is now continuous.
- The dotted/dashed micro-stipple that ran along bar 1's left rim and bar 4's bottom rim in v1 is
  gone.
- Fireflies: gone. No isolated hot pixels anywhere. No render noise in the object.

**New / still present:**

1. **Hard rectangular step-terraces, bar 1 top-left crown.** This is the exact spot the user circled.
   Four blocky yellow / black / blue rectangles march diagonally down the crown, each with a hard
   straight edge and a hard corner. This is the banded emissive panel resolving as discrete tiles
   instead of a spectrum. It is more offensive than the v1 comb, because the blocks are bigger and
   read as broken geometry, not as sampling noise.
2. **Same terracing, smaller, on bar 2 top-left crown** and along **bar 3's upper-left rim**.
3. **Faceted octagonal silhouettes.** Bars 4 and 5 no longer have superellipse corners — every
   corner is a straight 45° chamfer, so the outline is a cut octagon. Bar 4's bottom-left and
   bottom-right corners are the worst. It reads as a low-poly bevel, i.e. as CG geometry.
4. **Contour ringing / posterised lobes inside bar 2.** The dark-red lobe at mid-height is encircled
   by two concentric soft contour rings, and the olive field above it steps rather than ramps.
5. **Residual ripple on the peanut, right rim at the waist.** A fine horizontal streak texture at
   grazing angle — shader-bump moiré. Much reduced from v1 but not clean.
6. **Flat dead fields.** The bevel band down bar 4's right side is a uniform tan/bronze with no
   variation at all. Bar 5's lower orange wedge is a flat field. These are not artifacts in the
   sampling sense, but they read as painted plastic.

**Measured:** background is lifted to mean luma 1.5 with a standard deviation of 0.5/255. The grain
at 0.008 is not visible. So the lift produces a flat grey veil over the black with nothing granular
in it — the worst of both.

## 2. Glass realism — **3.5 / 10**

- **Highlights: absent.** Measured peak luminance across the frame is **224**, and **zero pixels
  exceed 250**. v1 peaked at 255 with 0.031% clipped. There is not one specular hit in this image.
  Real glass and perspex are defined by clipped white — every reference has it (`ref_ring`'s rim
  arcs, `ref_puck`'s white lower half, `ref_abstract`'s white ribbon cores). Without it the material
  reads as matte pigment. This one fact costs more than everything else combined.
- **Imperfections: none.** I searched every surface at 4× zoom. No dust specks, no lint, no
  fingerprint smudge, no hairline scratches. `ref_ring` and `ref_puck` are both covered in them —
  that is precisely what sells them as photographs of real objects. The user asked for this by name
  and it was not delivered.
- **Edges: soft and wrong.** The silhouette is blurred over several pixels on every bar. Glass edges
  are the sharpest thing in a photograph — a bright caustic line against black. Here the object
  dissolves into the background.
- **Thickness: lost.** The interiors of bars 1 and 5 are roughly half black void. There is no
  internal reflection stack, no visible far wall, no sense of a solid you could pick up. v1 read
  thicker.
- **Screams CG:** the chamfered octagon outlines, the airbrushed gradient-mesh interiors, and the
  total absence of any surface contamination.

## 3. Style match to references — **5.5 / 10** (v1 was stronger)

Lost against v1:

- **White cores.** v1's ribbons ran through white at their peak. v2's peak out at mid-grey. Compare
  `ref_abstract`, which is white-cored throughout.
- **Colour richness.** v2's saturated reds and oranges have collapsed into olive, maroon and bronze.
  Bar 2's upper half is a muddy khaki. v1's reds were pure.
- **Ribbon quality.** v1's spectral bands were thin, crisp and fast. v2's are wide, soft and slow —
  more airbrush poster than prism.

Kept or improved:

- The deep black cores are still there, and on bar 1 and bar 5 the blue/green edge ribbons are
  genuinely reference-like.
- The peanut's blue body with rainbow rim edges is the closest thing in the frame to `ref_ring`.

Net: the spectral idea survives; the intensity and the crispness that made it match do not.

## 4. Compositing — **4.5 / 10**

Not more dynamic. Less. It is muddy and soft, not noisy.

- **Fog glow with no highlights to bloom from** just smears mid-tones. It is acting as a blur, not
  as halation. Halation needs a clipped source.
- **Lens dispersion at 0.018** is invisible against subject matter that is already spectral. It
  contributes nothing and slightly softens the rims.
- **Vignette 0.30** is too strong on a frame this dark — it is eating bar 1's bottom and the
  peanut's top-right and pulling the composition inward.
- **Lift** is flattening the blacks to a grey veil with no compensating contrast anywhere.
- **Grain 0.008** does not exist at viewing size.
- **The faint streaks** are not readable in this frame.

The stack is all applied, and every element of it is pushing the same direction: softer and flatter.

## 5. OVERALL — **4.6 / 10 — REJECTED**

---

## 6. Ranked changes

1. **Get clipped white back — this is the whole job.** Raise the key softbox by roughly 2.5–3 stops
   (×6–8 power) and shrink it to about a third of its current area so it produces a small, hard,
   fully-clipped reflection. Target 0.05–0.15% of frame pixels above luma 250, with the brightest
   hits on bar 1's top crown, bar 2's top-left shoulder and the peanut's upper-right rim. Verify
   numerically, not by eye. Nothing else on this list matters until this is true.

2. **Kill the step-terraces at their source.** The banded emitter is resolving as discrete tiles in
   the crowns. Blur the band transitions on the emissive panel — a ColorRamp with hard stops should
   become smooth interpolation, or push a Noise/Blur of about 0.05 in the panel's UV. Simultaneously
   move the panel 1.5–2× further behind the glyph so the bands subtend a smaller angle and the
   crowns sweep several bands rather than landing on one. Recheck bar 1 top-left, bar 2 top-left and
   bar 3 upper-left specifically.

3. **Add contamination.** Three layers on the coat lobe: dust specks (Voronoi or Noise, threshold so
   about 0.3% of surface area lights up, feeding coat roughness to 0.4 and a faint diffuse white);
   smudge (large-scale Noise, scale ~4, driving coat roughness 0.02 → 0.12); scratches (stretched
   Noise, anisotropic ~20:1, very low amplitude, into normal only). `ref_ring` and `ref_puck` are the
   target density — visible at 100%, invisible at thumbnail size.

4. **Sharpen the silhouette and unfaceted the corners.** Raise the bevel segment count on bars 4 and
   5 until the 45° chamfers disappear (likely 3 → 8+ segments, or a subdivision pass). Separately,
   cut the fog glow strength by about half and reduce its radius so it stops blurring the outline;
   the edge should be a 1–2px hard transition into black.

5. **Restore colour intensity.** The refraction colour split has gone muddy where lobes overlap.
   Widen the IOR spread from 1.49 ± 0.15 to about ± 0.22 for more separation, and after the S-curve
   add a saturation lift of roughly 1.2–1.3 targeted at mid-tones. Bar 2's upper half must stop being
   khaki; bar 4's right bevel must stop being flat bronze.

6. **Rebalance the comp.** Vignette 0.30 → 0.15. Grain 0.008 → 0.025 so it is actually visible.
   Remove the lift entirely, or cut it enough that background luma returns under 0.5 — with real
   speculars in frame you will not need lifted blacks to carry the contrast. Lens dispersion can drop
   to 0.010; it is buying nothing at 0.018.

SCORE: 4.6
