# Review — v03

1. **Score:** 5.6 / 10

2. **Targets**
- Background: #000000 at all corners. **Hit.**
- Deep teal #012437–#085c62: none. The coolest plate tone is #799082. **Missed.**
- Sage #7c9f93: #7a9c87–#83a68f. **Hit.**
- Cream #e7c69d: #f5d49b. **Hit (marginal, too yellow).**
- Amber #fdbb55: #f8cd95. **Missed.**
- Orange #fca321: none. The best is #fbc08e peach. **Missed.**
- Hot pink #fe6f6b: #fb878b–#fb9093. **Missed.**
- Opal blue skin #9fb8b7: #45525e–#465460 at the left edge. The hue is right, but it is two stops too dark. **Missed.**
- Micro-type 1–1.5% cap height: top band ≈0.6%. The bottom-right and right-edge blocks do not read. **Missed.**

3. **What works**
- Blur grows with depth: the upper gear is crisp, and the dumbbell and the blocks melt.
- The thin rim on the top edge carries the teal → amber → pink gradient. It is the most photographic detail in the frame.
- The top-band micro-type now reads as moulded: bright letter edges on a clear strip.

4. **Problems, ranked**
1. **The front fill made a grey veil, not milk** (left 40% and top band). The plate over empty space is #45525e. The plate over the parts is #57565e–#605960. The parts lost their blacks, and the plate still does not glow. Two rounds of front-light tweaks have not fixed this, so change the mechanism. Put scatter inside the plate: a Principled Volume, or subsurface with albedo 0.85–0.92, blue-weighted. Extend the gradient emitter behind the left side with a deep-teal stop (#0a4a55), so the plate is lit from behind everywhere and never sits on black. Cut the front fill back to under 5 W. Targets: plate over a gap #9fb8b7–#c8ccc4, plate over a part #10202a–#2a3038.
2. **The gradient is pastel because it clips.** Across the right half, R sits at 251–253 and G and B rise, so orange goes peach and pink goes salmon. Lower the emitter by 1–1.5 stops so the peak R is ≤ 240. Use the Standard view transform or AgX Punchy, and make the orange and pink stops more saturated. v02 asked for this, and it has not moved.
3. **The "Wonder" logotype is still a flat grey decal** (#565660, bottom left). It has no edge highlight, and it fades out after "Wonde". The bottom-right text block and the right-edge vertical text are invisible. Model the logotype as raised plate-material geometry, 0.3–0.5 mm high. Give it a grazing strip for a highlight on the top edges. Set every micro-type block to 1–1.5% of the frame height, and place it where the plate is mid-toned.

5. **Research check**
- Blur by depth: agrees.
- Opalescence (blue skin, warm core): contradicted. The skin is dim blue-grey, and the core is not warm.
- Frosted plate: contradicted on the left, where the plate reads as tinted clear glass.
- Raised type read by highlights: agrees on the top band, and is contradicted by the logotype.

6. **What 8.5 needs**
- Volume or subsurface milk, backlit across the whole plate, with a deep-teal stop.
- An emitter that does not clip, reaching #fca321 and #fe6f6b.
- Raised, lit geometry for the logotype and all the micro-type.
- The hard vertical strip reflection with a cross (x≈1075) replaced by 2–3 small wet specular pools.
- A surface warp, fine scratches, and grain at σ 1–2%.
