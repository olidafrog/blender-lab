# Matching a reference

For "recreate this image" work. Learned on eclipse-glow (93 renders, 17 judge rounds).

## Tools

- `tools/compare.py` — side-by-side PNG, MAE, and sampled colours along the centre lines. Render at the reference's exact resolution so pixels line up.
- `tools/screen_fft.py` — period and angle of a line screen or fine pattern in a flat patch. Run it on the reference and on the render; it catches a wrong or flipped angle in one run.
- `tools/crop_compare.py` — zoomed side-by-side of one region. Use it as soon as a reviewer flags a small area.
- `tools/metrics.py` — levels, clipping and gradient share per region, or a per-region diff between two versions. Works on renders of any size.

## Workflow

- Check whether another project already measured the same reference. `~/GitHub/photoshop-lab` rebuilt the Warp refs with a full numeric record that `printed-plastic` never had.

1. Sample the reference first: colours along lines, edge positions, radii. Seed ramps from real values, so early renders land close.
2. Iterate on numbers with `compare.py` until the pixel profile matches.
3. Then switch to the [review loop](review-loop.md).

- Judge light size from a pixel row across a cast shadow, not the overall mood. `wax-seal` research guessed "large soft key"; the row showed a 10 px hard edge, and two rounds flipped between soft and hard until it was measured.
- Sample each target as a region statistic (median, or 95th percentile for highlights), not one point. A single "lit rim" point (191) sat below the rim's real highlights (236). Seven reviewers then called the rim "40 too bright". `wax-seal`

## What to expect

- Pixel MAE and reviewer score correlate only loosely. MAE was best around scores of 7.3–7.5 while the scores sat at 7.0–7.6.

## Traps

- A parameter that feeds several effects moves things you did not mean to move. Keep one coordinate per purpose.
- Narrowing a shape that also sources a glow dims the glow. Rebalance both.
