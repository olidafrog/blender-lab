# Review v12 — pink_ring (target: 01)

1. **Score:** 6.2 / 10

2. **Targets**
- Lit top 205,124,164 vs ~169,105,129: **missed** (too bright, too magenta).
- Core 229,110,152 vs ~217,127,155: **hit**.
- Shadow side 228,115,156 vs ~183,130,145: **missed**. It is as bright as the core.
- Sky 214,226,239 vs ~196,208,218: **missed** (+20 in each channel).
- Shadow/lit ≥ 0.35: ratio ~1.0. **Hit on paper** only because there is no shadow side.
- Edge falloff ~2.5 px per 700 px vs smoke 6–10: **missed**.
- Emitter glow: the ring gives no measurable falloff into the cloud. **Missed.**

3. **What works**
- Colour acts like albedo. The crevices drop to ~204,77,117, deeper and more saturated than the lobes.
- The render is clean. There are no fireflies, voxel steps or smear.
- Ring occlusion is right: the back arc hides behind the cloud.

4. **Problems, ranked**
- **Flat light on the whole cloud.** Luminance stays 132–147 from top to base and from left to right. The ref has a soft-lit upper-left and a grey-mauve lower-right and base. The ground shows a hard sun shadow, but the volume ignores that key light. Fix: raise density or the shadow step until the base and lower-right sit at 0.65–0.8 of the top. Soften the sun to 15–30° angle, or use an overcast dome.
- **The ring does not light the cloud (front arc).** The lobes next to the tube are no brighter than lobes 120 px away. Ref 01 glows hot pink along the ring. The tube core clips to white (255,250,251); the ref tube is pink-white. The ring also casts a shadow on the ground, and an emitter must not do that. Fix: make the volume see the ring's emission, adding 20–40 L within 3–5 tube widths. Tint the ring pink (saturation 0.3–0.5). Turn off the ring's shadow visibility.
- **The billows have one scale.** The small lumps are even everywhere, like noise displacement. There are no big billows carrying the shading. The ref reads as 6–10 large lobes with lobes on them. Fix: add a low-frequency lobe layer 2–3× the current largest lobe. Soften the edge to 6–10 px.

5. **Research check**
- It contradicts "the base is darker than the top": the base is 141 L and the top is 144.
- The silver lining and the emitter glow are missing.
- It agrees with albedo deepening in the crevices.

6. **What 8.5 needs**
- A darker base and lower-right under soft key light.
- A pink ring that lights the nearby cloud and casts no shadow.
- Large lobes, with 6–10 px edges.
- Cloud R and B down about 30. Sky down about 20.
