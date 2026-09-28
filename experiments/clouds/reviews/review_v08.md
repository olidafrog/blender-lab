# Review v08: pink_rod vs 02

1. **Score:** 6.7 / 10

2. **Targets**
- Lit top 180,146,170 → 222,142,168. Luminance OK, red +42 (salmon). **Missed.**
- Left 183,123,148 → 222,140,165. **Missed.**
- Violet shadow 148,101,135 → 167,94,129, no violet. **Missed.**
- Bottom 127,76,104 → 132,72,106. **Hit.**
- Sky top 63,109,155 → 66,108,152. **Hit.** Sky bottom 134,165,184 → 129,158,179. **Hit.**
- Shadow/lit luminance ≥ 0.35 → 0.54. **Hit.**
- Edge falloff 2–4 px/700 → about 12–15 px/700. **Missed.**
- Entry glow 3–5 tube widths → about 8 widths, white core. **Missed.**

3. **What works**
- The sky gradient matches.
- The base and core darken, and the shadows stay light.
- The upper-left entry is sharp outside and swallowed cleanly at the surface.

4. **Problems, ranked**
1. **Emitter inside (centre, x 720–960, y 780–1000).** The rod shows as a blown white streak in a crevice, with firefly specks. It reads as a slot cut through the cloud, not light glowing through volume. Fix: add density along the rod path (within about 2 tube radii) so the tube sits ≥ 0.5 optical depths under the surface. Clamp indirect light to about 10. Cap the in-cloud peak below R 250 and G 180.
2. **Flat hue (whole body).** It is one salmon pink everywhere. The reference goes from peach lit faces to lavender faces and shadows. Tinting the colour value has not fixed this. Use per-channel absorption instead (green about 3x red, blue about 1.5x red), and raise the blue sky fill.
3. **Billows and edges (crops tl, bl, br).** The small bumps are even polka dots on mushy mid-size lobes, and the silhouette is smoky. The reference has crisp lobes-on-lobes with dark gaps between them. Fix: build 3 octaves of sphere or Worley lobes, each about 0.4x the size of the one above, instead of noise displacement. Sharpen the density ramp to a 2–4 px edge.

5. **Research check**
- Multiple scattering, the dark base and bright shadows agree with the findings.
- "Colour deepens in the core and shadow": the colour darkens but does not shift to violet.
- "The emitter becomes a soft glow sized by depth": contradicted. The glow is hard and white, and the hue is lost.
- There is no silver lining. The light is near-frontal; the reference is lit from the upper right.
- The rod bloom outside the cloud is about 3x the reference width.

6. **What 8.5 needs**
- Bury the rod's middle in density. Keep a magenta glow of 3–5 tube widths.
- Add per-channel absorption and a lilac sky fill.
- Build crisp multi-octave lobes with a 2–4 px edge.
- Cut the rod bloom to about 1/3 of its width.
