# Art direction review — v13b

Reviewed 2026-09-19 against `ref_ring.png`, `ref_puck.png`, `ref_abstract.png`, carried forward from
`review_v06b.md` (5.6) and `review_v11a.md` (6.8). Candidate: `renders/v13b.png` (40% scale, 160
samples). `renders/v13a.png` and `renders/v11a.png` seen for calibration only, not scored. Noise and
resolution ignored.

## Score: 7.4 / 10 — not accepted (threshold 8.5)

The structural fault is fixed. Colour now comes from the surface: it bends with the crown, pools in
the hollows and fringes the contours, and the grey slabs at the bar intersections are gone. Against
v13a the crown is clearly the right lever — v13a is a chrome sculpture, v13b is glass. What holds it
at 7.4 is hue range. The frame is almost entirely cream, amber, tobacco and red, with cyan appearing
as two isolated patches that look dropped in rather than part of a ramp; every reference runs a
continuous red→yellow→green→cyan→blue sweep, and green is missing here altogether. Second problem:
the large interiors are broad flat washes of pale warm grey at roughly 70–85% value, so the piece sits
in a muddy mid-tone band where the references go blown-white next to true black. Third: the peanut is
stranded top-right with a third of the canvas empty around it, and the mark still floats inside a wide
dead margin — a composition note now three rounds old.

## Ranked changes

1. **Complete the spectrum — you are missing green and most of blue.** Widen the R/G/B IOR split
   again (roughly 1.5× the current spread) and, more importantly, check the light colours: three
   bands at 2700 K / white / 7200 K give you warm and cool but no mid-spectrum, so the refraction has
   nothing green to separate out. Make the centre band genuinely neutral-to-slightly-green and push
   the cool band harder toward 9000 K. Target `ref_puck`: every band is a full ramp, not a warm
   gradient with a blue edge.
2. **Break up the flat cream interiors.** Roughly 40% of the glass is a featureless pale warm wash.
   Add a second axis of curvature — a cross-crown, or a subtle thickness variation along the bar
   length — so the refraction angle changes in two directions and the wash resolves into bands.
   Narrowing the light strips will also help: wide soft bands make wide soft washes.
3. **Restore the value range.** Push the band cores to clip white and let the valleys drop to near
   black, so contrast comes from the glass rather than from the background. Raise light power and
   simultaneously deepen absorption/tint so the bright cores blow but the mid-tones fall away. Right
   now nothing in the frame is either fully bright or fully dark inside the silhouette.
4. **Fix the composition.** Scale the mark to about 88% of frame height, balance the margins, and
   move the peanut closer to the bars so the three forms read as one group. The gap between the peanut
   and the upper bar is currently larger than the peanut itself.
5. **Add micro-detail.** Still outstanding from both previous rounds: faint scratches and dust
   (low-strength noise bump ~0.002) plus compositor Lens Distortion dispersion 0.01–0.02 and light
   grain. The surfaces in all three references are visibly imperfect; v13b is CG-clean.
6. **Vary the treatment per shape.** All three forms currently carry the same amber-and-cream
   signature. Rotate one bar or offset the light relative to it so one shape runs cool and another
   warm, giving the eye a focal point.

## Keep

- **The crowned faces.** This is the fix. Colour now follows curvature instead of sitting inside the
  form. Do not retreat to v13a's flatter surfaces when chasing contrast.
- The pure black world, no floor, no spill. Correct across all four rounds.
- The thin RGB fringing along the contours and bevels — that is genuine dispersion and it reads as
  real glass.
- The silhouette. The bars and the peanut stay legible with hard, intentional edges.
- The saturation discipline. Nothing here is neon. Add hue range without raising saturation past this
  ceiling.
- The absence of the grey slabs. Blocking defect from round 2 is resolved.
