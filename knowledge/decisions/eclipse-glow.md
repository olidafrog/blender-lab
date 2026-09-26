# Decision: how the eclipse glow effect is built

Context: recreate `references/eclipse_glow_ref.jpg` as an effect that works on any mesh and stays
non-destructive and tweakable.

## Choices

- **Colour from camera-space normals, not geometry or UVs.** "Vertical" is the normal's Y in
  camera space; "Edge" is the facing ratio. Any mesh therefore gets the same banding and rim
  logic, and the object can be swapped or animated without touching the material.
  Rejected: object/generated coordinates (break on non-spheres), UV gradients (mesh-specific).
- **Emission only, Standard view transform.** Colours on the ramps are literal sRGB samples from
  the reference, so what you pick is what you get. Rejected: lit Principled BSDF (the look is not
  physically lit), AgX (shifts the sampled colours).
- **Glows live in the compositor, fed by shader AOVs** (`halo`, `arc_glow`). Glow outside a
  silhouette can't be drawn by a surface shader. AOVs keep it object-driven while the spread,
  tint and amount stay adjustable after rendering.
- **Crescent = the object's own alpha, shifted and scaled, minus itself.** This is the
  two-overlapping-circles lens the reference is built on, and it works for any silhouette.
  Rejected: an offset circle in normal space (can't extend beyond the silhouette), an extra shell
  mesh (not non-destructive, breaks when swapping the object).
- **Glow tails from stacked blurs (near/mid/far), not Fog Glow.** Fog Glow needs a very bright
  source for a long tail, which clips the core into a hard shape under Standard.
- **Halo and arc glow masked by object coverage.** Without it the blurred glow bleeds inward and
  tints the rim spectrum and the dark cap.

## Known limits

- Compositor Transform scales about the image centre; keep the subject roughly centred or retune
  Crescent Offset/Scale.
- Viewport compositing may not show AOV-based glows in every mode; F12 render is the reference.
