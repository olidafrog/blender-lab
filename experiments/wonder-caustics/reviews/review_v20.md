# Art direction review — v20

Reviewed 2026-09-19 against `ref_ring.png`, `ref_puck.png`, `ref_abstract.png`, carried forward from
`review_v06b.md` (5.6), `review_v11a.md` (6.8), `review_v13b.md` (7.4), `review_v16.md` (7.9) and
`review_v18.md` (8.3). Candidate: `renders/v20.png` (45% scale, 200 samples). `renders/v18.png` and
`renders/v19b.png` seen for calibration only, not scored. Noise and resolution ignored.

## Score: 8.1 / 10 — not accepted (threshold 8.5)

The band-frequency note is fixed, and fixed well: three wide ribbons per bar with real calm between
them, the picket-fence gone, and the 18° rotation genuinely working — bar 2's ramp and bar 4's yellow
wedge now bend through the elbow instead of driving past it. The material also reads more expensive
than v18; the forms are cleaner and the crop is correct. But the round paid for that calm in hue.
Cutting the bands cut the spectrum with them: green is gone again, magenta is gone past the point
asked for, and the frame is now roughly 80% grey-steel with four or five isolated colour events
sitting in it. Against `ref_puck`, where a single ramp carries red, yellow, green, cyan and blue at
full width across a near-black field, v20 reads as polished chrome with an occasional oil-slick
fringe — the failure mode of `v19b`, arrived at from the other direction. The peanut, v18's
strongest form, is the clearest casualty: it was a full ramp and is now near-monochrome steel blue.

## Ranked changes

1. **Put the whole ramp back inside each surviving band.** Keep three wide ribbons, but make each one
   a complete spectral sweep — red → orange → yellow → green → cyan → blue across its width — rather
   than a single hue with fringes. Right now a band is "an orange stripe" or "a blue stripe". In every
   reference a band is a *ramp*. Widening each light strip's angular spread, or increasing dispersion
   so the sweep fills the wider band, is the move. This is the whole remaining gap.
2. **Recover the mid-tones from grey.** The large flat steel-grey areas — bar 1's right half, bar 3,
   the peanut's body, most of bar 5 — are the single biggest departure from the references, which hold
   near-black instead. Grey mid-tone reads as brushed metal; black reads as glass. Push the non-band
   areas down toward true black rather than leaving them at 30–40% grey, and the surviving colour will
   gain without raising saturation at all.
3. **Give the peanut its ramp back.** It has regressed from the strongest form in v18 to the weakest
   here. It should carry at least one full spectral ribbon through its waist, where the curvature is
   tightest and the references would be blazing.
4. **Bring green back at real width.** Round 4's green note is reopened. There is no green anywhere in
   the frame except a one-pixel fringe on bar 5's lower bevel. Every reference puts green mid-ramp at
   the same width as cyan and yellow.
5. **Close the frame.** The mark now occupies about 76% of frame height with a dead band across the
   top quarter and a large empty block lower right. Crop in from the top and right until it sits at
   88–90%. The peanut's fixed position argues for cropping *to* it, not away from it.
6. **One focal form.** Still outstanding since round 3. With the bands calmed down, no single form now
   leads — the eye goes to bar 2's white core by default rather than by design. Bias one bar warm
   against the rest, as `ref_ring` splits orange against blue on a single object.

## Keep

- **The reduced band count and the wider crown.** Correct, and the round's win. Do not go back toward
  v18's fifteen stripes when restoring hue — restore it *inside* these three bands.
- **The 18° rotation and the tilted crown axis.** The ribbons bending through the elbows on bars 2 and
  4 is exactly what round 5 asked for and exactly what `ref_ring` does.
- **The crop.** No longer clipping, unlike v19b.
- **The reduced magenta on the middle bar.** Poster-flat ink is gone. Do not push it further down.
- **The value extremes.** Blown white cores and true black are both intact.
- The pure black world, no floor, no spill. Correct across all six rounds.
- The silhouette, the legibility of the forms, and the restrained surface micro-detail.
