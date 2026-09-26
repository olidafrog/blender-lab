# Research brief v2 — why v1 doesn't read as glass, and what to change

Diagnosis from `scripts/build.py` + v1_annotated. Three root causes:
- `rough=0.0` on all three refraction lobes **and** the glossy lobe → perfect mirror → 1-px highlights.
- Lights are 0.20 m × 6.0 m strips with 35–45° spread at ~3.5 m → ~3° angular size → pinstripe, not softbox.
- `remesh_voxel=0.012` on a 2 m object ≈ 170 voxels across → faceted surface. A mirror highlight
  crawling over facets is what makes the circled edges look *jagged*, not just thin.
The missing dust/scratch layer is real but secondary; fix roughness + light size first.

---

## 1. Procedural imperfection stack (shader nodes only)

All coords from **Texture Coordinate → Object** (object space = metres, logo is 2 m wide).
Noise `Scale` therefore = cycles per metre. Do **not** re-use the current `Mapping Scale (1,1,240)`
squash — at 240 it slices the solid and smears on any face not facing Z.

**Layer 0 — base roughness floor (do this first, biggest win).**
`rough` 0.0 → **0.035**. Apply to all 3 refraction lobes and the glossy lobe. At 0.035 an 85 mm
lens at 5.9 m turns a 1-px line into a 4–6 px graduated band. Range that still reads "optical
quality perspex": 0.02–0.06. Above 0.08 it goes frosted.

**Layer 1 — greasy haze (broad, the thing that actually sells handled glass).**
Noise `Scale 2.2`, `Detail 4`, `Roughness 0.5` → ColorRamp `0.42 / 0.62` → Map Range
`To Min 0.025 / To Max 0.075`. Feed the **glossy roughness only**, leave refraction clean —
haze belongs on the reflection, not inside the volume. Patches ~45 cm, so ~4 across the logo.

**Layer 2 — fingerprints (localised, 3–4 patches max).**
Ridges: Noise `Scale 42`, `Detail 2`, `Roughness 0.35` → ColorRamp `0.485 / 0.515` (very narrow →
thin closed loops, ~2.4 cm spacing ≈ real ridge pitch at this object size).
Mask: Noise `Scale 2.8` → ColorRamp `0.58 / 0.74` → Math MULTIPLY with the ridges.
Drives: roughness `+0.05`, and Bump `Strength 0.03 / Distance 0.0012`.
Amount check: prints should be invisible until a highlight sweeps them.

**Layer 3 — dust specks.**
Voronoi `F1`, `Scale 210`, `Randomness 1.0` → ColorRamp `0.0 / 0.030` (inverted, so only the cell
centres light). Break it up: second Voronoi `Scale 19` → ColorRamp `0.70 / 0.72` → MULTIPLY, so
only ~1 cell in 8 carries a speck. Drives roughness to **0.35** locally and Bump
`Strength 0.15 / Distance 0.0004`. Target coverage **< 0.3 %** of surface. These are what make
ref_ring and ref_puck read as photographed objects.

**Layer 4 — micro-scratches.**
Two families. Per family: Mapping `Rotation (58°, 23°, 99°)` / `Scale (1, 1, 36)`, Noise
`Scale 11` (family A) and `Scale 17` (family B), `Detail 3` → ColorRamp `0.630 / 0.660`.
Combine with Math MAXIMUM. Drives roughness `+0.10` and Bump `Strength 0.05 / Distance 0.0008`.
36 (not 240) keeps them hairline without turning into a Z-smear on side faces.

**Layer 5 — edge wear.**
**Bevel** shader node (`Radius 0.004`, `Samples 8`) → Vector Math DOT with Geometry → Normal →
ColorRamp `0.55 / 0.98` inverted = an edge mask. Add `+0.035` roughness on it. Softens the
knife-edge fringe on every bevel.

**Combine:** Math MAXIMUM the roughness contributions (not ADD — ADD stacks to frosted), then
CLAMP 0.02–0.40. Bumps: chain Bump nodes (each node's `Normal` input from the previous).
Total bump budget across the stack: keep under 0.20 combined strength.

**Coat.** The material doesn't use Principled, so there's no Coat socket to reach. Add a fourth
lobe instead: Glossy `Roughness 0.11`, Normal = *unbumped* (coat sits over the defects),
Add-Shader on top, weighted by Layer Weight `Fresnel 1.5` → Math MULTIPLY `0.55`. This is the
single biggest contributor to a broad, soft, believable highlight — it gives you a wide soft
specular *and* a tight one in the same place, which is exactly what real coated glass does.

**Thin Film — don't.** 5.2 Principled has `Thin Film Thickness` / `Thin Film IOR`, but they are
**not** on the standalone Glossy/Refraction BSDFs you're using. Even if you switched: thin-film
hue cycling fights the 0.30 IOR-spread dispersion and reads as soap bubble / oil slick, not
perspex. Verdict: off. (If you ever want a rim shimmer only, 280–340 nm at IOR 1.35 on the coat
lobe alone, with `spread` dropped to ≤0.08.)

**Also fix the jaggies:** `remesh_voxel` 0.012 → **0.006**, or drop the voxel remesh and rely on
the Bevel modifier + Shade Smooth with 30° auto-smooth. Broader highlights hide facets, finer
voxels remove them.

---

## 2. Lighting for glass highlights

Softness = angular size of the source as seen from the surface. Current: 0.20 m at 3.5 m = **3.3°**.
Target for a graduated bevel highlight: **18–28°**.

Replace the two strips with:
- **Key softbox** — area light, `size 1.4 × 3.6 m`, at `(-2.9, -1.1, 2.6)`, spread **150°**,
  power **900 W**, 9500 K. 1.4 m at 3.0 m ≈ 26°.
- **Rim softbox** — `1.0 × 3.0 m` at `(3.1, 1.5, 1.4)`, spread 150°, power 550 W, 2700 K.
- **Keep one thin strip** — `0.10 × 4.0 m`, power 250 W, spread 30°, placed near-edge-on. One
  razor glint among broad highlights reads as expensive; twelve of them read as CG.

**Gradient reflector cards** (the thing that produces long graduated highlights along a bevel):
camera-hidden emissive planes, **3.2 m × 2.2 m**, at `(±2.5, -1.4, 1.2)`, aimed at the logo.
Material: Texture Coordinate → Object → Gradient (Linear) → ColorRamp with stops at
`0.00 = 0.0` black, `0.45 = 0.15`, `1.00 = 1.0` white → Emission `Strength 4.0`.
Set `visible_camera = False`, `visible_shadow = False`. The black-to-white ramp is what makes a
highlight *fall off along its length* instead of being a uniform stripe — the single most
recognisable signature of a commercial glass shot.

Also: the existing `Grad_back` panel at 7×7 m with `P_STRIPES = 3` is generating the hard
rainbow banding. Drop to `stripe_duty 0.75`, `stripe_soft 0.22` for softer band shoulders.

---

## 3. Compositing (5.2 node-group compositor)

Chain, in this order (lens effects → sensor effects → grade):

1. **Render Layers**
2. **Glare — `'Fog Glow'`**, `Quality 'High'`, `Size 8`, `Threshold 0.8` (down from 2.0),
   `Strength/Mix 0.35`. Fog Glow is the right choice for glass: it's the halation bloom around
   blown highlights. `'Bloom'` is tighter and more "game engine"; `'Streaks'` is anamorphic and
   will fight the dispersion colour. Use Streaks only as a *second* very low pass —
   `Iterations 3`, `Streaks 4`, `Angle Offset 12°`, Strength **0.06**.
3. **Lens Distortion** — `Dispersion 0.018`, `Distortion 0.0`. Radial CA. Above ~0.03 it doubles
   the existing dispersion and looks broken.
4. **Vignette** (no image needed): `CompositorNodeEllipseMask` `Width 0.82 / Height 0.82`,
   `Mask Type 'Add'` → `CompositorNodeBlur` Fast Gaussian, `Size X/Y 320 px`, `Relative` on →
   Mix `MULTIPLY`, `Fac 0.30`.
5. **Color Balance**, `correction_method 'LIFT_GAMMA_GAIN'`, `Lift (1.014, 1.014, 1.026)`.
   Lift is centred on 1.0, so >1 raises blacks. This puts the background at a near-black with a
   cool cast instead of clipped 0,0,0 — the "filmic lift".
6. **RGB Curves**, combined C curve: add points `(0.26, 0.225)` and `(0.74, 0.795)`. Gentle S.
7. **Grain.** There is **no Noise texture node in the compositor**. Two options:
   - `CompositorNodeTexture` fed a texture datablock: `bpy.data.textures.new("grain", type='CLOUDS')`,
     `noise_scale 0.06`, `noise_depth 1` → Mix `ADD`, `Fac 0.018`. Works headless.
   - Skip it. AgX + Fog Glow already carry most of the filmic feel, and Cycles' own residual
     noise at 256 spp reads as grain on a black field.

**Uncertain in 5.2 — verify by printing sockets before relying on them:**
- Whether the Glare node exposes `Threshold` as a socket or only `Highlights` (renamed in the
  4.5 rewrite). The existing code already loops `for s in gl.inputs` by name — keep that pattern.
- `CompositorNodeMixRGB` vs a newer `CompositorNodeMix`. Print `bpy.types` for both.
- `EllipseMask`'s `Mask Type` may be a node property (`mask_type`) rather than a socket.
- Whether `CompositorNodeTexture` still accepts a legacy texture datablock in 5.2.

---

## 4. What separates real glass from CG glass in the references

1. **Black cores, not rainbow everywhere.** ref_ring is mostly deep black with colour confined to
   two or three zones. v1 is saturated across 100 % of the surface — that alone reads CG.
2. **Blown-out white highlight centres with colour only on the shoulders.** ref_abstract's
   highlights are pure white in the middle, spectrum at the edges. v1 has no white anywhere.
3. **Visible surface debris.** Hairline scratches and dust specks are clearly readable in both
   ref_ring and ref_puck. This is the entire tell that an object was photographed.
4. **Large low-frequency gradients across flat faces.** ref_puck's top face is one slow sweep.
   v1's `P_STRIPES = 3` banding is high-frequency and periodic — the eye reads periodicity as CG.
5. **Doubled internal reflection.** In ref_ring you can see a second, offset ghost of the ring's
   own silhouette through the body. Comes from thickness + bounce count, not from the shader.
