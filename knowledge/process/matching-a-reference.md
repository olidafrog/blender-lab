# Matching a reference

For "recreate this image" work. Learned on eclipse-glow (93 renders, 17 judge rounds).

## Tools

- `tools/compare.py` — side-by-side PNG, MAE, and sampled colours along the centre lines. Render at the reference's exact resolution so pixels line up.
- `tools/screen_fft.py` — period and angle of a line screen or fine pattern in a flat patch. Run it on the reference and on the render; it catches a wrong or flipped angle in one run.
- `tools/crop_compare.py` — zoomed side-by-side of one region. Use it as soon as a reviewer flags a small area.
- `tools/silhouette.py` — subject outline against a reference mask: IoU, band widths, red/blue overlay. `--make-ref` thresholds the reference. For any subject with a clear outline (a figure, an object). `roman-model`
- `tools/metrics.py` — levels, clipping and gradient share per region, or a per-region diff between two versions. Works on renders of any size.

## Workflow

- Find the original artwork first: other views, a 4K copy and CAD line renders settle sizes and structure that no amount of guessing does. ArtStation blocks HTML fetches; `r.jina.ai/https://www.artstation.com/projects/<id>.json` returns the project JSON and the `/4k/` image URLs download directly. `cyber-model` never found it; `cyber-deck-v2` did in its first research pass.
- Separate material colour from grade. The Backrooms' "yellow wallpaper" is light beige on set; the yellow-green is white balance and grade. Matching reference pixels in albedo bakes the grade into every material. Source: [Blender Guru, Backrooms](https://www.youtube.com/watch?v=kBsVJSETydU)
- Check whether another project already measured the same reference. `~/GitHub/photoshop-lab` rebuilt the Warp refs with a full numeric record that `printed-plastic` never had.

1. Sample the reference first: colours along lines, edge positions, radii. Seed ramps from real values, so early renders land close.
2. Iterate on numbers with `compare.py` until the pixel profile matches.
3. Then switch to the [review loop](review-loop.md).

- Judge light size from a pixel row across a cast shadow, not the overall mood. `wax-seal` research guessed "large soft key"; the row showed a 10 px hard edge, and two rounds flipped between soft and hard until it was measured.
- Sample each target as a region statistic (median, or 95th percentile for highlights), not one point. A single "lit rim" point (191) sat below the rim's real highlights (236). Seven reviewers then called the rim "40 too bright". `wax-seal`

- **Oblique product shot: rectify it to a plan.** An affine warp (rotate by the azimuth, stretch the vertical by 1/sin(elevation)) makes the edges vertical, so outlines can be traced in plan px on a gridded, brightened copy. Tune azimuth and elevation until a known rectangle (the LCD) is level. Then render the model as an orthographic plan with the same framing and overlay it on the plan: layout was right in one pass. `cyber-model`
- **Fit the camera from landmarks.** Twelve points read off a gridded 2× reference, a pinhole model, Nelder–Mead in pure python (`experiments/cyber-model/scripts/fit_camera.py`): azimuth 41.0°, elevation 48.65°, lens at the 200 mm cap (near-orthographic), rms 6 px at 736 px. An edge-map overlay of render and reference then agreed. Two hand guesses at the lens and distance had missed by 1.6× in scale. `cyber-model`
- **Find where the reference's extremes are before tuning them.** A red overlay of pixels under luma 22–30, on the reference and the render, showed the blacks were a thin contact halo round the whole object plus gaps, not creases. Four rounds went to "blacks" before this. `cyber-model`
- **One measured table, same procedure on both images** (`experiments/cyber-model/scripts/measure.py`: backdrop corners, subject median, p5, p95, share under 12, LCD colour, grain std). It gave the reviewer numbers to trust and gave me a pre-review gate. Judge ratios for small quantities. `cyber-model`

## What to expect

- Pixel MAE and reviewer score correlate only loosely. MAE was best around scores of 7.3–7.5 while the scores sat at 7.0–7.6.

## Traps

- A parameter that feeds several effects moves things you did not mean to move. Keep one coordinate per purpose.
- Narrowing a shape that also sources a glow dims the glow. Rebalance both.

- **A photo reference is also a processing chain.** The reference was a sharpened JPEG (edge ratio and fine-detail energy higher than a raw render's in every region), and seven rounds of content fixes plateaued at 5.3–5.9 until a 2× render, Lanczos, light unsharp and a JPEG round trip (`tools/photo_finish.py`, gate `tools/sharpness.py`) lifted the loop to 6.0–6.5. `aztechno-building`
- **Mask what a region metric counts.** A "cream shade share" counted grey glass reflections as shaded paint; reviewers read the row as "relief too shallow" for four rounds while the measured cast shadow was on target. Check a metric's mask on one image before trusting it. A paint-class IoU stayed at 0.33 all loop (glass and shade dominate the labels), so it never ranked versions. `aztechno-building`

## Many photos of one space

Learned on `apartment-model` (7 cameras on one room).

- **Fit each camera to a textured scan first.** A Workbench FLAT/TEXTURE render of the scan at 512 px takes about 0.3 s. Nelder–Mead on blurred edge correlation against the photo locks a plan-position start in 1–2 min. Furniture in the scan matches the photo, which helps. It stalls where clutter dominates; landmark PnP on clean architectural corners plus line constraints fixed those cameras (4–6 px rms).
- **Then solve cameras and dimensions together.** Per-round single-value nudges traded off between photos: one cove depth fitted photo 3 and missed photos 1, 5 and 6 by 10–20 px. A joint coordinate search over P and the poses fixed this (`joint_fit.py`): Workbench object-colour renders, truncated distance from model edges to photo edges, furniture edges masked, scan priors at σ 3 cm. It runs in 2.5 min; 7.6 → 8.1 in one round.
- **Residuals that grow toward the frame edge are not always lens distortion.** A constant geometric offset d projects as f·d/depth, so it is largest at the nearest (frame-edge) points. k1 fitted against the scan or the model stayed at 0. The edge-beam drift was a 5–8 cm cove. Before adding distortion, check whether the error scales with 1/depth or with radius.
- iPhone EXIF beats memory for the lens (the user's 0.5x/1x notes were wrong for 3 of 8 photos). Use a 34.6 mm sensor width for 35 mm-equivalent focal lengths at 4:3. A photo edited in Photos (cropped or straightened) fits no pinhole: leave it out.
- **Materials against a photo** (`apartment-model` round two): put 1:1 photo crops above render crops at the same pixels from the matched camera (`review_sheet.py <v> mat`), and measure each material's luma relative to a white wall in the same regions (`scripts/mat_measure.py`): it cancels exposure, and it caught a brick 1.4× too light and a floor 0.8× too dark before any review. Rectify a photo onto a model plane with its fitted camera (`scripts/rectify.py`) to measure a pattern (plank pitch, course height, layout direction); cross-check with a second camera: two disagreed by 20 % on plank size.
