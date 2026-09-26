# Art direction review — v11a

Reviewed 2026-09-19 against `ref_ring.png`, `ref_puck.png`, `ref_abstract.png`, and carried forward
from `review_v06b.md` (5.6). Candidate: `renders/v11a.png` (40% scale, 160 samples). Sibling
`renders/v11b.png` seen for calibration only, not scored. Noise and resolution ignored.

## Score: 6.8 / 10 — not accepted (threshold 8.5)

The colour problem from v06b is fixed and then some: the frame is now genuinely spectral, the blacks
are deep, and the silhouette is far more legible than the pillow shapes of round 1. But the colour
has arrived as the wrong kind of colour. In all three references the spectrum is an *edge* effect —
it hugs the rim, runs along curvature, and fans out where the surface turns away from the light, with
large calm areas of near-black or near-white between bands. In v11a the spectrum is an *interior*
effect: concentric blobs of red, yellow and cyan sitting flat inside each bar like a thermal image or
a projected gobo, unrelated to the form's contour. The result reads as printed or inked plastic rather
than thick perspex, and because every bar carries the same repeated blob motif the eye finds no focal
point. Two further faults cost real points: the opaque grey rectangles floating at the bar
intersections (roughly x280/y420, x450/y760, x700/y750) are clearly unintended non-glass geometry or
light cards in shot, and the composition still sits small and left-of-centre with a wide dead margin
the references never allow. v11b confirms the direction of travel is wrong, not just the amount —
more of the same pattern makes it worse, so the fix is the character of the dispersion, not its
strength.

## Ranked changes

1. **Move the spectrum from the interior to the edges.** This is the whole gap. The blob pattern
   suggests colour is coming from a textured or patterned light source (an IES/gobo, a coloured
   area-light texture, or a noise-driven emission) being refracted through a fairly flat interior.
   Strip that back to plain white strip lights and let the *dispersion* make the colour: raise the
   R/G/B IOR split, and add surface curvature (a wider, softer bevel plus a gentle crown across the
   bar faces) so the refraction angle changes across the width and the hues separate along the form
   instead of pooling in the middle. Target `ref_ring`: one continuous orange-to-blue sweep per
   surface, not fifteen small ones.
2. **Remove the opaque grey rectangles at the bar intersections.** Three flat mid-grey slabs are
   visible where the zig-zags cross and behind the lower-right bar. Whatever they are — backing
   geometry, a light card with visible camera ray, a shadow catcher — they are not glass and they
   break the illusion instantly. This is a blocking defect, not a taste note.
3. **Cut the number of colour cycles by about two thirds, and give the bands a white core.** Every
   reference has few, wide bands with blown-white centres and deep black valleys. v11a has many
   narrow bands of uniform mid-value, which posterises into a rainbow-oilslick look. Fewer, larger,
   higher-contrast bands will read as prismatic light; the current ones read as pigment.
4. **Crop tighter and centre the mark.** The logo occupies roughly 70% of frame height and is pushed
   left, leaving a third of the canvas empty at the top. Scale to about 88% of frame height, balance
   the margins, and the piece gains presence for free.
5. **Split the lighting warm/cool.** Still outstanding from round 1 and still the cheapest premium
   cue available. Two long thin strips, roughly 2700 K and 7000 K, edge-on from opposite sides, so
   the whole mark has a directional temperature gradient instead of every bar being lit the same.
6. **Add micro-detail and a touch of compositor dispersion.** Faint scratches and dust (low-strength
   noise bump ~0.002) plus Lens Distortion dispersion 0.01–0.02 and light grain. All three
   references carry visible micro-scratches; without them the surface reads as CG-perfect.

## Keep

- The pure black world, no floor, no spill. Correct across all three rounds.
- The deep value range. Unlike v06b there is almost no clipped white, and the darks go fully to
  black. Protect this when raising band contrast.
- The silhouette. The bevel reduction worked — the zig-zag bars and the peanut are each readable as
  distinct forms with hard, intentional edges. Do not inflate them again.
- The three-shape layout with overlap, and the small restrained glints at the top edges of the bars.
- The saturation ceiling: the hues are strong without going neon. v11b crosses that line; v11a does
  not.
