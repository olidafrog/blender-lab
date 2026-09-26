# Art direction review — v16

Reviewed 2026-09-19 against `ref_ring.png`, `ref_puck.png`, `ref_abstract.png`, carried forward from
`review_v06b.md` (5.6), `review_v11a.md` (6.8) and `review_v13b.md` (7.4). Candidate:
`renders/v16.png` (40% scale, 160 samples). `renders/v15.png` (rejected) and `renders/v13b.png` seen
for calibration only, not scored. Noise and resolution ignored.

## Score: 7.9 / 10 — not accepted (threshold 8.5)

Real progress. The value range is fixed: band cores now blow to white and the valleys fall to true
black, so contrast comes from the glass and the piece finally has the depth of `ref_abstract`. Blue
and cyan are present as genuine parts of a ramp rather than dropped-in patches, and the restraint
after v15 is correct — v15 traded legibility for noise, and v16 keeps the forms readable. Two faults
hold it under the bar. First, the spectrum is still a two-ended thing: it runs black → blue/cyan →
white → cream → rust → black, and green survives only as a one-pixel fringe on contours. Every
reference puts green at full width in the middle of the ramp, and rust-brown is a hue none of them
contain — the warm end is desaturated and muddy where the refs are pure orange-red. Second, the
colour still resolves into closed concentric islands — the blue-ringed red "eye" at the lower left
bar and the matching one at the lower right — instead of continuous ribbons that run the length of
the form. That is a v11a residue, softened but not gone. The polished mid-grey facets on the right
side of each bar also push the material back toward chrome, and composition remains a note now four
rounds old: dead band top and bottom, and the peanut still parked in its own corner.

## Ranked changes

1. **Give green real width in the ramp.** The pale-green-white centre band is being read as white.
   Make it unambiguously green (roughly 520–540 nm, saturation around 0.35–0.45, not a green tint on
   white) and drop its power maybe half a stop relative to the outer two so it is not the brightest
   band. Target `ref_puck`: green occupies as many pixels as cyan or yellow.
2. **Clean the warm end.** The reds are reading as rust/tobacco, which means the warm band is picking
   up glass absorption or sitting too low in value. Either remove the amber tint from the volume
   absorption or push the warm band toward pure orange-red at higher intensity. Nothing in the three
   references is brown.
3. **Turn the colour islands back into ribbons.** The closed concentric blobs mean the crown is
   locally dome-like, so the refraction angle sweeps out and back within one small region. Stretch
   the cross-curvature strongly along the bar axis — one long gentle sweep, not a series of bumps —
   or rotate the strip lights closer to parallel with the bar length so the bands elongate rather
   than ring.
4. **Break the chrome facets.** The flat mid-grey vertical faces on the right of each bar carry no
   hue and read as brushed metal. Angle those side walls a few degrees more so they catch a light
   band, or narrow the bevel there, so every visible face is doing spectral work.
5. **Fix the composition.** Still outstanding since round 1. Scale the mark to about 88–90% of frame
   height, close the top and bottom margins, and pull the peanut in toward the upper bar. It is
   currently a satellite, not part of the group.
6. **Differentiate one shape.** All five bars still carry the same signature. Give one form a cooler
   lighting bias so the eye has a focal point, as `ref_ring` does with its orange-versus-blue split
   across a single object.

## Keep

- **The restored value range.** Blown cores next to true black. This is the round's win and the
  largest single step toward the references. Protect it.
- **The restraint relative to v15.** The subtle hairline scratches and bump are at the right level
  here; v15's were vandalism. Do not raise them.
- The crowned faces and the thin RGB fringing on contours and bevels — still genuine dispersion.
- The pure black world, no floor, no spill. Correct across all four rounds.
- The silhouette. Hard, intentional edges, forms still legible under much higher contrast.
- The saturation ceiling. v16 adds hue range without going neon; v15 shows what crossing that line
  costs.
