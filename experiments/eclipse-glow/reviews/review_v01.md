# Review v01 — eclipse_logo_v01.png

1. **Score:** 5.2 / 10

2. **Targets** — none set.

3. **What works**
- The mark reads clearly. It has both stepped bars and the pinched hourglass in the right proportions and the right places.
- The rim shows real dispersion (yellow/orange outside, a cyan hint inside) on the left edges. The bottom edges pick up the warm orange.
- The grain is fine and even and matches the reference texture. The world background is opaque near-black.

4. **Problems, ranked**

1. **Flat cyan fill on every bar (whole frame).** The front faces point straight at the camera, so the normal gradient sits at its mid value. About 80% of each bar is one flat cyan (~#3A8FD0). The dark top, navy band and pink-to-orange bottom appear only in the end caps. The reference is mostly near-black navy on top and lilac/peach below, with almost no flat cyan. Fix: stop relying on normals alone for the vertical ramp. Mix in a per-shape vertical coordinate (object-space Z normalised to each shape's bounds, weight about 0.6–0.8) with the camera-normal Y (weight about 0.2–0.4). Each bar then runs dark → navy → blue → pink → orange along its length. Also drop the blue stop's value. The mid-body should be navy/periwinkle, not sky cyan.

2. **Mitre chevrons and a jagged seam at the step joints (centre crop, hourglass neck).** Hard "V" shapes appear where the bevel sides meet the caps: dark V at the tops, pink ^ at the bottoms. The diagonal step joints show a stair-stepped, aliased dark seam. The hourglass lower lobe has a vertical streak down its centre. These are normal discontinuities in the bevel/extrude mesh. Fix: rebuild the shapes as inflated solids, not bevelled slabs. Voxel-remesh the extrusion (0.5–1% of the logo width), then smooth or corrective-smooth it and shade smooth. Or bevel with round profile, 8+ segments, depth = half the stroke width, with Harden Normals off. No crease may survive.

3. **Glow stack almost absent (all edges).** There is only a crisp 2–4 px hairline rim. The reference has a wide soft orange halo outside the silhouette (about 4–8% of the frame width), a lifted crescent arc above the top edge, and bloom that burns the lower edge to near-white. Here there is no halo, no crescent and no visible bloom. Fix: blur the silhouette mask to 30–60 px at 1200 wide and tint it orange. Add it at a strength that lifts the background next to the edges to about 0.15–0.25 value. For the crescent, offset the mask up 1–2% and subtract the original mask, then blur and add. Soften the rim to 6–12 px.

5. **Research check** — The findings say "dark top, blue middle, pink/orange bottom" driven by normals. On flat-faced extrusions the normal term gives one colour per face. The image shows that normals alone cannot carry the ramp on this geometry. The compositor glows named in the findings are not visibly present.

6. **What 8.5 needs**
- A per-shape vertical ramp mixed with the normals, and a deeper navy mid.
- Seamless inflated geometry with no chevrons or stair-step seams.
- A wide orange halo, a crescent above each top edge, and bloom on the lower edges.
