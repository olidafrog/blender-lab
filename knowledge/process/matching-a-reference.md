# Matching a reference

For "recreate this image" work. Learned on eclipse-glow (93 renders, 17 judge rounds).

## Tools

- `tools/compare.py` — side-by-side PNG, MAE, and sampled colours along the centre lines. Render at the reference's exact resolution so pixels line up.
- `tools/screen_fft.py` — period and angle of a line screen or fine pattern in a flat patch. Run it on the reference and on the render; it catches a wrong or flipped angle in one run.
- `tools/crop_compare.py` — zoomed side-by-side of one region. Use it as soon as a reviewer flags a small area.
- `tools/silhouette.py` — subject outline against a reference mask: IoU, band widths, red/blue overlay. `--make-ref` thresholds the reference. For any subject with a clear outline (a figure, an object). `roman-model`
- `tools/metrics.py` — levels, clipping and gradient share per region, or a per-region diff between two versions. Works on renders of any size.

## Workflow

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
