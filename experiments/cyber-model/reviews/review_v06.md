# Review v06

## 1. Score: 6.5 / 10
Form and edges 6.0, part fidelity 7.0, materials 6.0, light/colour/backdrop 6.5, technical 7.5.
(0.3×6.0 + 0.2×7.0 + 0.2×6.0 + 0.15×6.5 + 0.15×7.5 = 6.5)

## 2. Yes/no list
1. Partly. Soft lit shoulders on plate tops (S-plate, 760–1000, 540–780). The foot of each step is dark grey, not a black crease, and still shows a soft bevel.
2. Yes. Lid (960–1250, 390–600), right plate (1200–1400, 560–820), lower-plate slot. The S-step has no parallel groove.
3. No. The lower wall (700–1400, 1050–1160) is as dark as the tops or darker.
4. No. Flat faces are clean.
5. No. Rod, cylinders, cord and gear are smooth.
6. No. All parts sit on something. The two antenna cylinders overlap only by occlusion.
7. Yes. Short thin strokes on the lid and right plate. Pale and sparse next to the reference.
8. Yes. Faint diagonal sheen plus a steel bezel. Not a flat sticker.
9. No. Creases are charcoal.
10. Yes. Std 16.2 vs 15.4. Grain size matches once scaled to 736 px.

## 3. Targets
- Backdrop TL 101/96, TR 133/142, BL 103/111: hit.
- Backdrop BR 106/117: hit (11, borderline).
- Subject share 38/36, median 70/75, p95 84/92: hit.
- Subject p5 21/7: missed (14 over).
- Subject <12 %: 2.4/7.6. Nominally a hit, but the render has a third of the blacks. Treat as missed.
- LCD median (142,203,211)/(140,204,212): hit.
- Grain std 16.2/15.4: hit.

## 4. What works
- The LCD colour, the backdrop gradient and the grain match the table.
- All major parts are present and attached: twin cylinders, coil cord, dial and gear, knob, switch, LED, steel plate.
- Grooves follow the lid and right-plate outlines. Scratches read as strokes.

## 5. Problems, ranked
1. **Blacks are missing.** Under the plate edges (1000, 700), (1200, 880), (830, 620) and along the lower wall. The tonal range is squeezed (p5 21, p95 84). Fix: put a matte black liner slab (albedo 0.005) under each part break, inset 0.3–0.5 mm. Add an Ambient Occlusion node to the body shader, distance about 1.5× the bevel width, that multiplies albedo to 0.02 in cavities.
2. **Edges are pillowy, not chamfered.** Plate rims and corners everywhere, for example the right plate (1200–1400, 560–820) and the lid corners. The reference shows flat 45° facets with a crisp highlight line. Fix: Bevel modifier, segments 1–2, width 0.4–0.8 mm, weighted to convex top edges only. Give concave feet a weight of 0.
3. **Walls are not lighter than tops, and the body reads as one flat charcoal.** Lower wall (700–1400, 1050–1160). Fix: a large soft fill card low on the camera side, at 25–40 % of key strength. Add Principled Sheen 0.2–0.4 on the polymer so the edges catch light. Add brushed anisotropic highlights on the bracket and roller so p95 rises toward 92.

## 6. Research check
The image agrees on light direction, backdrop falloff, part list, near-black gaps and groove logic. The wall-lighter-than-top claim is only weakly visible in the reference (my estimate). The render misses it entirely.

## 7. What 8.5 needs
- Black liners plus AO, so p5 falls to about 8–10 and the share below 12 reaches 6 % or more.
- Chamfer facets in place of soft radii.
- A fill card that lifts the walls.
- Brighter, brushed steel.
- A groove along the S-step.
- Denser scratch clusters.

**Blind pairwise (X = v05, Y = v06):** Y is closer. Its body is darker with more tonal range, and its backdrop has the lit top-right falloff and stronger grain of the reference. X is flatter and lighter, and its antenna cylinders carry too many collar rings.
