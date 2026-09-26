# Art direction review — v22

Reviewed 2026-09-19 against `ref_ring.png`, `ref_puck.png`, `ref_abstract.png`, carried forward from
`review_v06b.md` (5.6), `review_v11a.md` (6.8), `review_v13b.md` (7.4), `review_v16.md` (7.9),
`review_v18.md` (8.3), `review_v20.md` (8.1) and `review_v21.md` (8.4). Candidate: `renders/v22.png`
(50% scale, 320 samples). `renders/v21.png` seen for calibration only, not scored. Noise and
resolution ignored.

## Score: 8.6 / 10 — accepted (threshold 8.5)

The note I have called the whole remaining gap since round 6 is closed on the majority of the frame.
Bar 2 now runs red → orange → yellow → a thin white core → green → cyan → blue at full width, bent
through a chevron at the elbow; bar 4 runs the same sweep across its face and is the closest thing in
eight rounds to `ref_puck`'s single ramp crossing a black field. Lowering the band power worked
exactly as intended — the blown cores are lines rather than columns, and the middle of the ramp
resolves instead of clipping. Hue purity is also genuinely better: the oranges are clean rather than
tan, green sits at the same width as yellow and cyan, and the added violet gives the cool end a
proper terminus. The bevel comb is mostly gone — most edges now carry a continuous multicolour piping
that matches `ref_abstract` rather than a dashed RGB dotting.

What holds it at 8.6 rather than higher is that two of the five forms are not doing the work. Bar 1
is the weakest thing in the frame: a dull maroon → violet → navy wash with no yellow, no green and no
white, and its right half is near-dead. Maroon-over-navy is the one un-spectral colour event in the
image and it reads as tinted rather than refracted. The peanut is still cool-only after four rounds
of the same note — a flat cobalt field top and bottom with warmth surviving only as thin fringes at
the waist and the lower right rim — and its large flat blue areas are poster-flat where the
references keep gradient inside every hue. Residual dashed comb also survives in two places: the
peanut's inner rims and bar 5's lower-left bevel.

## Ranked changes

1. **Fix bar 1 — it is the one un-spectral form.** Its face carries maroon → violet → navy with no
   warm-to-cool sweep and a large dead right half. Every reference makes its darkest surface still
   run a ramp. Angle that bar's light band 15–20° so the sweep crosses the face rather than grazing
   it, or raise that strip's power a stop so the ramp's middle resolves as it does on bars 2 and 4.
2. **Give the peanut a warm half — fourth round on this note.** It is cyan → blue → blue with orange
   only as a 2px fringe at the lower right and a red fleck at the crown. One warm pass through the
   upper lobe would seat it in the group. Right now it is the only object in the frame that reads as
   a different material.
3. **Break up the flat cobalt fields.** The peanut's two lobes, bar 2's left face and bar 5's upper
   block are each a single flat blue with almost no internal value change, which reads as painted
   plastic. `ref_ring` keeps a value gradient inside its blue at all times. A little more variation
   in the light strip's intensity across its length, or a shallower crown on those faces, would give
   the blue somewhere to travel.
4. **Clear the last of the dashed comb.** Two places remain: the peanut's inner rims through the
   waist and lower loop, and bar 5's lower-left inner bevel. Everywhere else the fringe is now clean,
   so this is a local geometry problem — those are the tightest bevel radii in the scene. Widen the
   bevel slightly on those edges or add one more bevel segment there.
5. **Recover a little light in the lower-left quadrant.** The exposure lift landed on the bands but
   bar 1 and bar 3's left flank are now large near-black blocks, and the frame's weight has shifted
   right. Not a crop problem — the crop is correct. Lift the fill on the left-hand forms half a stop.
6. **Trim the poster-flat red at bar 4's crown.** The top-left of bar 4's face goes to a flat
   saturated red with no internal gradient, the same failure the middle bar had in v18. It is the one
   patch reading as ink rather than light.

## Keep

- **The completed ramp at width.** Red, orange, yellow, green, cyan, blue and violet all present at
  comparable width inside a single band on bars 2, 4 and 5. This is the round's win and the thing
  that closes a note open since round 6. Do not trade it back for calm.
- **The thin blown cores.** Dropping the band power so the highlight is a line rather than a column
  is what let the middle of the ramp resolve. Hold this exposure.
- **The purified hues and the added violet.** Clean spectral chroma, no tan, no rust, and a proper
  cool terminus.
- **The cleaned bevel fringes.** Continuous piping on most edges now, which is what `ref_abstract`
  runs. Only two local spots left.
- **The recovered blacks and the pure black world.** Intact across all eight rounds.
- **The square crop and the mark filling the frame.**
- **The focal hierarchy** — bar 2 leads, bar 4 supports warm. Do not flatten it.
- **The 18° rotation and the ribbons bending through the elbows.** Intact from v20.
- The silhouette, the legibility of the forms, and the restrained surface micro-detail.
