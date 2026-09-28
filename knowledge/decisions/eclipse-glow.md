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

# v2: the Wonder logomark (2026-09-26, final score 7.2 peak / 6.8 last)

- **Geometry: Inflate modifier on the library curve** (curve → slab → SDF mesh → wall + quarter-round profile from distance to the outline). Puff, Roundness and Detail stay live. Defaults follow the designer's final GLB (0.18 m thick), edge 0.06 m (GLB 0.03). Rejected: the GLB mesh itself (no live controls); bevel + remesh + smooth (streaks, flat faces); a full dome (reviewers liked it, but it isn't the designer's shape).
- **Shape Gradient (per-shape height attribute) blended with the normal gradient, 0.7.** On flat faces the normal is constant, so the normal alone gives one flat colour. The same `shape_v` attribute also feeds a `height` AOV.
- **Halo = self-glow**: the body's bright parts, luminance-keyed, tinted, blurred, added outside the object. Rejected: a coverage-mask halo (even on every edge, filled the gaps between bars) and height-weighted coverage (the blur spread it back up).
- **Crescent and arc only on top caps**, from the height AOV. Without that, every step ledge gets an arc.
- **Opaque world background; coverage from an AOV**, not film alpha.
- **Open:** reviewers want rounder faces (a Roundness call for the designer), a tapered crescent (the lift-minus-self crescent is a uniform band on flat tops), and less brown where halos overlap.

# v2 rise video (2026-09-27, final score 7.3 peak / 7.2 last)

- **Atmosphere in the compositor, keyed to distance from a horizon line**, inside the same Post node (`post(..., extra, pre, stage)` hooks in `build.py`). `pre` hides every pass below the horizon before the glows, so hidden parts never glow. `stage` runs before bloom: shimmer (Displace from 4D noise on Scene Time), flattening, mirror, extinction, sky glow. One Horizon control. Rejected: a 3D ground plane (the horizon would live in two places) and a 3D mirror (camera-space normals shade it from below).
- **The mirror fades by the height of the reflected point**, not by depth below the horizon. It mirrors only what is within about 40 px of the ground, so it dies away once the logo clears, as a real inferior mirage does.
- **Horizon = broad warm sky + thin dim line + quick falloff into dark ground.** A single bright band read as a synthwave laser line for four rounds.
- **Shimmer: one smooth noise octave, about 20 px layers.** Three octaves at about 7 px read as video tearing.
- **Music: an original cue (`score.py`).** The requested Terminator theme is copyrighted and was not downloaded; `make_video.sh` takes a licensed file instead.
- **Open:** the reviewers disagree on haze height (40 px vs 150 px); the logo clears around f160, leaving a long slow drift.

# v3 sunrise video (2026-09-27, final score 7.4 peak / 7.1 last)

From the designer's notes on the rise: the contact point is the brightest, blooming, grainy highlight; a gap opens between the logo and its mirage image; the heat haze blurs as well as shimmers. `build_sunrise.py` imports `build_rise.py` and swaps its `pre`/`stage`.

- **Horizon = the vanishing line**, not the sea: the mirror hangs below it inside a bright band (miraged sky), then dark sea. Physics: the inferior mirage joins the erect and inverted images above the sea horizon (Etruscan vase → omega).
- **Contact highlight in three layers:** a zone key (luminance × nearness to the line, gain 1.5), an oval **core** found by blurring the key sideways and thresholding its peak (so the whole bar base does not clip), then near/far bloom plus a 900 × 12 px streak along the line. Rejected: one gain on the whole key (blew out full bar bases, "two slabs" for 3 rounds).
- **Mirror fades by per-column presence:** coverage within ~50 px above the line, blurred down over the mirror. No keyframes; it dies as the logo lifts. Rejected: fading by the reflected point's height alone (either too short at contact or never left).
- **Haze:** warm sky drawn *before* the Displace so the line shimmers and gets mirrored; blur + a wide contrast veil, fading with height. Grain reseeded per frame (it was frozen in every earlier video).
- **Open:** the stem at the join is subtle; reviewers want one merged core 30–50 px wide, where the logo's bars are 110 px wide.
