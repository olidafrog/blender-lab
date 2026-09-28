# Review — v05

1. **Score:** 5.8 / 10

2. **Targets**
- Background: #000000 at all corners and edges. **Hit.**
- Deep teal/navy behind dark parts (#012437–#085c62): gear #504745, bars #4c3f3a, top band #3f3529. Lifted from v04 (#372d2b), but still warm grey-brown. **Missed.**
- Sage #7c9f93: #7c8861 and #979869. Olive, too yellow. **Near miss.**
- Cream #e7c69d: none. Row y=1750 goes #c3a471 → #f0b179. **Missed.**
- Amber #fdbb55: best #f0b179. Washed. **Near miss.**
- Orange #fca321: plate reads #f3a975 apricot. Only edge pixels reach #e96e2b. **Missed.**
- Hot pink/coral #fe6f6b: #f16760. **Hit.**
- Opal blue skin #9fb8b7: 1,890 of 2.2 M plate pixels lean blue (median #7e90a0). **Missed.**
- Micro-type: "WONDER MATERIALS" cap height is about 12 px (0.6%). The lower-right lockup and the vertical right lockup are close to invisible at 1:1. **Missed.**

3. **What works**
- The frost change lifted the parts to about 40–45% of the surrounding luminance. The upper-right dumbbell and blocks now melt convincingly.
- "nder" in the logotype now reads as clear moulded relief with edge glints (crop 600_1700). Top band type has good glints.
- Thin orange and teal edge light on the cut-outs and plate edge is right.

4. **Problems, ranked**
1. **Parts behind: brown shadow puppets, 5th round.** Every part is a blurred warm silhouette. None sits sharp against the back face. In ref 02 the dark cluster sits in a teal halo, and near parts show glossy highlights. Value tweaks have failed. Change the mechanism: add a separate teal emitter (#085c62 → #0e6f74) behind the parts cluster only, so the glow around the parts goes teal and fades into cream. Move 2–3 parts to 0–2 mm behind the plate, with glossy dark navy clearcoat, so they read sharp with specular pips. Target gear median in the #3a5358–#4f6a6a range.
2. **Strip highlight at x≈1075: unchanged from v04.** It is a full-height, hard-edged bar that clips to #fef6f3. It reads as a CG plane. Replace it with a softbox that has a gradient falloff across its width. Add a low-frequency normal warp (0.2–0.5 mm) so the reflection bends. Keep peak at 0.85–0.92. Add small wet pools around the rivets like ref 02.
3. **No photographic surface or opal skin.** The plate is clean and smooth, with no grain, satin texture or blue sheen. Add a large dim cool softbox reflected in the coat only (roughness 0.3–0.4) across the upper-left third, to reach #9fb8b7. Add 1–2% film grain and a faint roughness breakup.

5. **Research check**
- Distance blur agrees, but "parts touching the back face read nearly sharp" is contradicted. Nothing is sharp.
- The opalescence claim (blue skin, warm core) is still contradicted.
- Relief type now agrees for "nder". "Wo" over the dark block reads as grey paint.
- The gradient palette is olive → apricot → coral. It skips teal and cream, so it is not the ref 02 family yet.

6. **What 8.5 needs**
- A teal halo behind the parts, and some parts sharp against the back face.
- A soft, warped key reflection in place of the strip.
- A cool coat sheen for opal skin, and a cream stop between sage and amber.
- Micro-type cap height at 1–1.5% of frame. Grain and wet highlights.
