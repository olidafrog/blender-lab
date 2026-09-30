## 1. Score: 6.6 / 10

Form and edges 6.5 · Parts 6.5 · Materials 6.5 · Light and backdrop 6.0 · Technical 7.5
(0.3×6.5 + 0.2×6.5 + 0.2×6.5 + 0.15×6.0 + 0.15×7.5 = 6.575)

## 2. Yes/no list

1. Mostly yes. The S-step and lid have a bright chamfer line on top and a dark crease at the foot (centre of frame, x 730–1250, y 560–760). The top line is a 1–2 px hairline, not a 2–3 px soft shoulder.
2. Partly. The lid pocket has a parallel groove (top right). The S-step has none. The bracket grooves converge, not parallel.
3. Partly (my patch estimates): lower-right walls about 83, tops 72–78, lower-left walls 45–60.
4. No large smears. One dark disc beside the vents (830, 795) reads as a blotch.
5. No. Antenna, pods, coil and thumb rack look smooth.
6. No. The twin pods cantilever off their block but touch it, with a contact shadow. The plug at right is grounded.
7. Yes. Short thin strokes on the lid and right plate, low contrast.
8. Not flat. Diagonal sheen and a gradient across the glass.
9. No. Creases and moats are dark grey. Only the LED seam nears black.
10. Visible, but 2–3× coarser and worm-shaped next to the reference's fine speckle (my estimate).

## 3. Targets

- Hit: backdrop TL, TR, BL, BR (off by 5, 9, 8, 11); subject share (6); median (6); p95 (10); LCD RGB (1, 2, 2); grain std (0.8).
- Borderline: p5, 19 vs 7, off by exactly 12.
- Missed: subject <12 %, 2.3 vs 7.6. That is a third of the reference. The 12-level rule does not suit a percentage.

## 4. What works

- The chamfer now catches light. Plate outlines read from across the room.
- Scratches, LCD glass, engraved lid and decals sit at the right level of tiny detail.
- Backdrop tone, LCD colour and part count match the reference.

## 5. Problems, ranked

1. **Blacks are grey.** Foot of the S-step, moats round the shield, plate seams lower right. p5 is 19 (reference 7). Fix: give groove and moat walls their own material slot with base colour 0.003 and specular 0. Widen the moats from 0.7 mm to 1.5–2 mm. Sink the floors 8–10 mm so AO cannot lift them.
2. **Walls do not lift.** Lower-left and bottom walls measure 45–60, darker than the tops. Fix: in the polymer shader, multiply albedo by 1 + 0.4 × (1 − |Normal.Z|). This lifts vertical faces and leaves the tops alone. Or add a low, device-linked area light from the lower left.
3. **Antenna pods are the weakest part.** They are fat matte-black "lipstick tubes" with one ring and flat caps. The reference shows thinner satin-metal pods with ribs, several rings, and a bracket. Fix: scale radius to about 0.75×, add 3–4 ring grooves with a bevelled step, use a satin steel base with roughness 0.35, and add a saddle block under both pods.

## 6. Research check

Mostly agrees. Two claims are too loose.
- "Soft 2–3 px shoulder" is only partly true in the render (hairline). The reference does look softer.
- "Camera-facing walls lighter than tops" holds for right-facing walls in the reference. Left-facing walls at the lower block and gear look as dark as the tops (my reading of a 736 px image).

## 7. What 8.5 needs

- Real black creases (p5 under 10, <12 % near 7).
- Right and camera-side walls lighter than the tops.
- A parallel groove along the S-step, and a two-segment top bevel instead of a hairline.
- Rebuilt satin-metal antenna pods.
- Fine backdrop grain, about 40 % of the current feature size, same std.
- More height variety in the lower-right block (still flat pads).

**Blind pair:** Y (v07) is closer. Its hard chamfer highlights and open moats make the plates read as stacked solids. v06 has softer, pillowy edges and a thin outline in place of a real gap. Both share the same grey creases.
