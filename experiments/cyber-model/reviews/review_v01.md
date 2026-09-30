# Review v01

## 1. Score: 5.9 / 10
Form and edges 5.5 (x0.30) | Parts 6.5 (x0.20) | Materials 5.5 (x0.20) | Light and backdrop 6.0 (x0.15) | Technical 6.5 (x0.15)

## 2. Yes/no list
1. Partly. The shield plate has a soft lit bevel and a black foot. The lower block and right plates have only a hairline rim.
2. Yes. The lid inset and the slot at right (1250,830) follow the shield outline.
3. No. Camera-facing walls (base, lower-left) are near black, darker than the tops.
4. No smears. The red LED throws a red halo onto the shield edge (centre crop, about 200,240).
5. No. Drums, antenna, cord and button are smooth.
6. Yes. The round button (660,800) sits on the backdrop beside the plate, not on a tab. The black plug (1410,610) is not joined to the cord end (1350,520).
7. There are no scratches. The lid and right plate are clean.
8. Yes. The LCD has a gradient, a diagonal sheen and a glass rim. The "7" of "4:27" is clipped by the bezel.
9. Yes. The creases and gaps read black (p5 9 vs 7).
10. Partly. The grain is visible, but its blobs look 2-3x coarser than the reference at the same scale (my estimate).

## 3. Targets
- Backdrop TL 107 vs 96: hit (11, at the limit). TR, BL, BR: hit.
- Subject share 27 vs 36: hit by the rule (9), but the subject has 25% less area. A visible miss.
- Subject median 63 vs 75: hit at the limit (12). It reads too dark.
- p5, p95, <12 %: hit.
- LCD median: missed. R is 154 vs 140 (14 off). G and B hit.
- Backdrop grain std 13.6 vs 15.4: hit.

## 4. What works
- Every secondary part is present: antenna, drums, dial and gear, knob, LED, coil, rack, screws.
- The LCD reads as glass, with header bars and legible text.
- The shield plate has a stepped groove, a bevel and a black foot. The blacks match the reference.

## 5. Problems, ranked
1. **The body is a thin tray, not a moulded slab.** Look at the left edge (640-830, 745-890) and under the lower block. Walls are about 20-30 px. In the reference, the walls look about 4x taller in proportion (my estimate). Parts look laid on a board, and the subject share falls short.
   Fix: raise the base slab and each plate step by 3-4x. Keep a 0.5-1 mm Bevel with 2-3 segments. Cut a Boolean crease at each foot. Add a low, wide area light on the camera side at 30-40% of the key, so the walls read lighter than the tops. Target subject median 75.
2. **Loose parts and a clipped digit.** The button and the plug float, and the cord ends in a stub.
   Fix: put the button on a lug with a raised ring, as in the reference. Sink the plug into a rounded pocket in the right plate. Run a thin bevelled curve (0.6-1 mm) from the last coil loop to the plug top. Shrink the LCD digits about 15% so the "7" clears the bezel.
3. **Materials are flat.** There are no scratches. The bracket is near white and has no brushing. The bezel edge is speckled.
   Fix: draw 30-60 short strokes (3-10 px at 1600) into a mask. Cluster them on the lid and right plate. Drive roughness down by 0.15 and albedo up by 0.1 with the mask. Set the bracket albedo to 0.35-0.45. Add a stretched noise (x scale 200, y scale 1) to roughness. Use anisotropy 0.5-0.7 on the dial ring. Raise the backdrop noise frequency 2-3x.

## 6. Research check
The image agrees with the findings. The lit soft shoulder, the black foot, the parallel grooves and the two-cylinder antenna base all hold. The render misses "camera-facing walls lighter than tops". The research says nothing on body thickness, and that is the biggest gap. The drums read at roughly twice the reference size (my estimate). Their end faces show cyan, which the reference does not have.

## 7. What 8.5 needs
- Step and slab heights 3-4x, black creases at the feet.
- A camera-side fill so the walls lighten and the subject median rises 12.
- The button, plug and cord attached. The "7" unclipped.
- Scratches, and steel with brushing at a believable albedo.
- The device 15% larger in frame (my estimate). Drums at about half the diameter, no cyan ends. Finer backdrop grain.
- The LCD red channel down about 14.
