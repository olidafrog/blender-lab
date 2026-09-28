# Wax seal: decisions

Experiment: `wax-seal`. A lilac sealing-wax seal with a raised, swappable emblem (the Wonder logomark), matched to one product photo. It ended at 6.2 after 7 review rounds (best 6.6 at v05); the slope rule stopped it. Blind calibration picked v07 (6.4) over v05 (6.1), because v07 has violet shadows. Research is in `experiments/wax-seal/RESEARCH.md`.

## What makes the look

- **The seal is one live geometry-nodes heightfield.** A dense grid gets its z from three parts:
  - a rim bead (an elliptical arc between the stamp circle and a noise-warped outline),
  - a dished field,
  - the emblem relief, joined to the rest by a smooth max.
  From above, a heightfield never shows that it lacks overhang, and every value stays a modifier input.
- **The emblem is any object on the modifier's Emblem input.**
  - It is auto-fitted to Emblem Size from its bounding box. GN Bounding Box needs Use Radius off; see `geometry.md`.
  - A top-down raycast gives the inside test and the height of a 3D mesh.
  - The bevel comes from the distance to the boundary edges.
  - Curves are filled first, so SVG curves, Text objects and meshes share one path. All three were tested.
- **Scatter decides the wax.** Opaque sealing wax needs about 0.07 mm, with a violet-leaning radius (1, 0.5, 1.2). That setting gives violet shadow sides without a glow.
- **The light is a small key at a low angle.** The key is 0.12 m at 36° elevation, from the upper right, with a warm world fill. A pixel row across the reference's cast shadow shows a hard ~10 px edge. The research's guess of a "large soft key" was wrong.

## Rejected

- **Scatter above 0.15 mm.** It fills the rim groove, draws neon purple lines in every concave crease, and blurs the bump. On the thin field, light leaks out through the bottom and the lilac goes grey-green.
- **A saturated base colour for violet shadows.** It also saturates the lit field. A cool world fill had no effect, because the paper bounce dominates.
- **Fluid sim, boolean or displacement-image seals.** None of them stays live, and image displacement would need re-rasterising for every emblem swap.
- **Voronoi-edge cracks for flow lines.** They read as mesh seams. Contours of a lightly warped noise read as flow marks.

## Open (why it stopped at 6.2–6.6)

- **"Soft plastic or fondant."** Every round said it. The sheen layer, the micro bump and the roughness split did not break it. Next mechanism to try: roughness and colour variation at the 0.5–2 mm scale (mottling from the chalk filler), and real micro-geometry on the rim instead of a shader bump.
- **The lit rim is too bright over a wide band.** Every round said it. The rim faces a 36° key almost head-on. Try a rounder bead cross-section, or a key further toward the top of the frame.
- **The relief tops read no brighter than the field.** The reference's knight is almost all bevel. The bold Wonder bars are mostly flat top, so this is partly the artwork. `Relief Lift` is exposed but left at 0.
- **Contradicting asks, left to the designer as controls:** key hardness, relief height (0.3–0.9 mm) and flow-line style.
