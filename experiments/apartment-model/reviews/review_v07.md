# Review v07

Row note: the sheet has 7 rows (photos 1, 2, 3, 5, 6, 7, 8; photo 4 has no row). I read the targets' row numbers as photo numbers.

## 1. Score: 7.6 / 10

Layout 8.0 · Windows 7.5 · Structure 7.0 · Built-ins 7.5

Pairwise: Q is closer. Its pilaster shaft edge (photo 6) is 6 px nearer the photo than P's, and its left window's outer opening edge (photo 2) is 3 px nearer. Every other difference is under 2 px.

## 2. Targets

- Window wall, photo 2: arch tops 0–4 px, sills ≤2 px, central beam end 1–2 px, pier tops 2–7 px, frame jambs ≤5 px. The brick-opening edges on the outer sides miss: left window at x=332 against 344 in the photo (12 px), right window at x=710 against 701 (9 px). **Missed** (2 elements).
- Mezzanine front, photos 3 and 6: internal window edges ≤3 px, soffit and fascia ≤3 px, column ≤2 px, girder underside 5 px low (photo 3) and 8 px low (photo 6). **Hit**, with the girder at the limit.
- Ceiling-to-wall lines and corners: the far corners hit within 5 px in every row. The side-wall edge-beam soffit line misses near the frame edges: photo 2 by 16 px (x=975), photo 3 by 21 px (x=50) and 18 px (x=975), photo 5 by 26 px (x=1000). **Missed.**
- Kitchen, photos 7 and 8: counter tops ≤5 px, island ≤5 px, run fronts ≤5 px, and the peninsula end 13 px wide on its left (photo 7). **Hit.**

## 3. What works

- The camera fits are solid. The room box, the mezzanine front, the column and the under-mezzanine split (kitchen on one side, the deeper dining side and the hall door) all land within a few pixels in all 7 rows.
- The internal steel windows match the photos in outline and bar layout in photos 3 and 6.
- The kitchen runs, island and open shelves track the photos closely in photos 7 and 8.

## 4. Problems, ranked

1. **Side-wall edge-beam downstand (photos 2, 3, 5).** The line where the beam meets the wall sits 16–26 px above the photo near the camera and closes to about 4 px at the far end. A constant height error looks like this, so the beam underside is about 10 cm too high. Fix: refit the edge-beam underside from the LiDAR side-wall planes and lower it.
2. **Window opening width (photo 2; photo 5 too).** The frames fit, but the brick-face opening is wider on the outer side of each window: 12 px on the left window, 9 px on the right. In photo 5 the arch's right side is 10–12 px out. Fix: narrow the opening cut by about 8–10 cm on each outer jamb and keep the frame where it is.
3. **Pilaster heads (photo 6).** The shaft edge is at x=385; the photo has 376 below the head. The model rounds into the wall, but the photo shows a straight shaft that widens through a 45° chamfer about 18 px tall. Fix: make the shaft about 8 cm narrower and model a chamfered splay.

## 5. Research check

The image agrees with the listed heights, the sill, the arch tops and the piers. Two items contradict it. The "splayed heads" are modelled as rounded fillets. In photo 1, the corner pier's front edge sits 25 px left of the photo, so its 0.15 m projection may be overdone. In photo 3, the dining-recess back wall top and the hall door head sit 12 px low, while photos 6 and 8 fit; check the recess ceiling.

## 6. What 8.5 needs

- Lower the edge-beam underside about 10 cm.
- Narrow the outer jambs of both brick openings.
- Chamfer the pilaster splays and narrow the shafts.
- Check the corner pier's projection (photo 1) and shift the internal window bars in photo 5 by 8–10 px; they sit left of the photo.
