# roman-model — research

## Read of the reference

In the order they matter to the look:

1. **Silhouette and proportions.** A chunky heroic figure about 5.3 heads tall (4.5 helmet heights). Huge shoulders with rounded pads, a narrow belted waist, short sturdy legs, big fists and boots. The crested helmet adds about 0.35 of a head above the crown.
2. **Faceting.** Every surface is flat shaded. The body (chest, arms, legs) has irregular triangles of mixed size: the look of a smooth form run through Decimate (Collapse). Armour and props (belt, strap, bracers, sword, shield, boot cuffs) are clean boxes and prisms with small chamfers, and the skirt is flat pleated plates.
3. **Pose.** 3/4 view, turned about 25° to the viewer's right. Feet apart, weight fairly even. Sword arm hangs forward-down on the viewer's left with the gladius angled across the front of the legs. Shield arm is bent at the viewer's right, the shield upright beside the body, its face turned toward the camera.
4. **Material.** One matte sand-coloured material on everything, no specular highlights. A faint paper-like grain at 1:1.
5. **Light.** One large soft key from the upper left and front; a warm, bright fill (shadow sides stay at about 60% of lit sides, never black). Soft contact shadow under the feet, a broad faint shadow cast to the right and back.
6. **Backdrop.** A seamless warm-sand cyclorama with no visible horizon, nearly flat in value, very slightly darker toward the top corners.

## Most likely process

Almost certainly an AI-generated image in the "printable low-poly figurine" genre. "Low Poly Factory" is a 3D-print tool brand (lowpolyfactory.com, Kartzy Studio) whose logo is different; this logo is invented, and the helmet mixes Greek-Corinthian with Roman kit. So there is no real pipeline to copy. The closest real process is how low-poly figurine artists work: a smooth or blocked-out form, decimated or hand-faceted, flat shaded, one clay material, rendered on a colour-matched cyc under one big soft key.

## Techniques to use

Rules from the modelling research, in the order they apply:

- **Blockout in head units first, detail last** (primary → secondary → tertiary). Everything is driven by the big shapes. Valve's TF2 order: silhouette, then interior shapes, then model. Blockout is gated by a black silhouette check before any detail. [80.lv Sacrifice workflow](https://80.lv/articles/001agt-stylized-character-art-workflow-from-blockout-to-render), [Valve GDC 2008](https://cdn.fastly.steamstatic.com/apps/valve/2008/GDC2008_StylizationWithAPurpose_TF2.pdf), [Polycount forms](https://polycount.com/discussion/233026)
- **Proportions in `P`, in head units `H`.** One head unit drives all lengths, so the figure rescales as one.
- **Pose by forward kinematics in Python, no armature.** A joint dictionary with angles in `P`; every part is built already posed from the joint frames (`mathutils.Matrix`). Automatic weights (bone heat) fail on multi-part meshes, and A-pose/T-pose only matters for a skinned rig. [Blender Artists: bone heat](https://blenderartists.org/t/bone-heat-weighting-failed-to-find-solution-for-one-or-more-bones/1144412), [jessyleite.dev](https://jessyleite.dev/posts/blender-bone-heat-weighting-failed/), [A vs T pose](https://blog.neural4d.com/comparisons/a-pose-vs-t-pose/)
- **Body: bmesh lofts of superellipse rings along the posed chains** (torso with its own ring shapes for chest, lats and waist; neck; arms; legs; head). Ring index maths from [Sinestesia](https://sinestesia.co/blog/tutorials/python-tubes-cilinders/); `bmesh.ops.bridge_loops` also works. Parts overlap at the joints; the design's pads, belt, skirt and bracers cover the joins. Optional fusion: Mesh to SDF Grid → SDF Grid Boolean → Grid to Mesh (5.x, gotchas in `knowledge/gotchas/geometry.md`).
- **Facets: Decimate COLLAPSE** with `use_collapse_triangulate` on a denser smooth body, ratio tuned by the read-back `face_count`; then flat shading. The manual says Decimate suits sculpted or subdivided meshes, not economical ones, so the body is built dense and smooth first. [Decimate manual](https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/decimate.html)
- **Armour and props: separate low-poly bmesh parts, low-poly by construction.** Intersections are fine for a render ("fine for rendering purposes 99% of the time"). Every plate has thickness. A one-segment bevel only on silhouette and highlight edges. [Polycount layered geometry](https://polycount.com/discussion/89859/layered-geometry-and-animation), [Grant Abbitt low-poly axe](https://grantabbitt.substack.com/p/crafting-a-low-poly-axe-in-blender), [80.lv Cannibal breakdown](https://80.lv/articles/cannibal-stylized-character-breakdown)
  - Helmet: low-segment dome, T-slot, cheek guards as thick plates, crest as a fan of wedges.
  - Shoulder pads: bisected low-segment sphere shells, solidified.
  - Belt, bracers, greaves, boot cuffs: frustum bands (8–10 sides).
  - Skirt: pleated plates around a ring, fanned out.
  - Strap: a band following the torso, offset along the normal (BVH `find_nearest`).
  - Gladius: diamond-section blade, crossguard block, grip, pommel.
  - Shield: outline extruded, rim inset, slight curve.
- **Flat shading, no Smooth by Angle.** Auto Smooth left in 4.1; `mesh.shade_flat()` or faces with `smooth=False`. Merge by distance and recalculate normals in the build. [BlenderNation 4.1](https://www.blendernation.com/2024/03/14/shade-auto-smooth-missing-in-blender-4-1/)
- **Pose rules:** a line of action, hips and shoulders counter-tilted 5–10°, torso twisted 15–25° off the hips, no twinning, and the sword clear of the body. [Wikipedia: contrapposto](https://en.wikipedia.org/wiki/Contrapposto), [Character Design Notes](http://characterdesignnotes.blogspot.com/2010/11/how-to-kill-great-character-design-part.html), [anim.works silhouette](https://anim.works/silhouette-in-animation/)
- **Lens 50–85 mm**, camera at about chest height. [previspro](https://wiki.previspro.com/shots/lens-choice-for-character)
- **Lighting:** one large area key close to the subject, upper left, plus warm world fill; the cyc is a curved plane colour-matched to the backdrop. [Creative Shrimp](https://www.creativeshrimp.com/character-lighting-techniques.html)
- **Colour (soft goal):** flat colour per material, as low-poly Roman models on Sketchfab do (red crest, steel helmet, red tunic, peach skin, tan leather). Texture that suits facets: per-face value jitter (±3–6 %), local AO for crevices, large low-contrast object-space noise; no Pointiness (it smears across coarse triangles), no Bevel node (softens facets). Keep saturated colour to the crest, tunic and shield. Use Khronos PBR Neutral or Standard; AgX turns crimson toward pink and orange toward peach (`knowledge/gotchas/colour.md`). [Imphenzia PixPal](https://imphenzia.com/imphenzia-pixpal), [Polygon Treehouse swatches](https://www.polygon-treehouse.com/blog/2017/12/6/swatch-magic), [Sketchfab low-poly Roman soldier](https://sketchfab.com/3d-models/low-poly-roman-soldier-b1996cdaa9324a3281240339cd35a6a3)
- **Kit accuracy for the colour pass.** Greaves plus crest read as a centurion. Steel helmet with brass fittings; red horsehair crest; tunic madder red (popular image) or off-white; leather belt with brass plates; scutum red with yellow wings and bolt, brass boss and rim; gladius steel blade, bone grip, brass fittings. [Imperial helmet](https://en.wikipedia.org/wiki/Imperial_helmet), [RMRS centurion](https://www.romanmilitaryresearchsociety.com/post/centurion), [Legio XX scutum](https://www.larp.com/legioxx/scutum.html), [Cingulum militare](https://en.wikipedia.org/wiki/Cingulum_militare), [red tunics](http://byzantinemilitary.blogspot.com/2019/07/did-roman-legionaries-wear-red-tunics.html)

## Advisor review (Fable) — adopted plan

Fable reviewed the draft plan against the reference. Adopted:

- **Body: one closed loft per limb and one for the torso, overlapping. No SDF fusion for v1.** Every join is covered (cheek guards and strap at the neck, pads at the shoulders, belt and skirt at the hips, bracers and fists at the wrists, boot cuffs at the ankles). Knees and the bare elbow get a ring with a slightly larger radius. Chest and lats come from per-ring radial profiles r(θ) (superellipse with two pec bumps). SDF stays a fallback.
- **Two recipes.** Body: loft 8–10 verts per ring → Subdivision 1 → Decimate COLLAPSE to a triangle target per part (torso ≈ 400, limb ≈ 120) → flat. Armour and props: faces built directly, one-segment bevel on silhouette edges, no decimate.
- **Helmet:** 8×6 sphere, delete the face-opening polys (no boolean), extend the bottom ring down and forward into cheek guards, a nose wedge, flared neck guard, Solidify ≈ 0.04 H, and a dark head inside so the T reads as shadow. **Crest:** a fan of ≈ 8 thin plates on an arc, jagged top, peak over the front third. **Pads:** three overlapping sphere-band lames per shoulder, span ≈ 1 H. **Skirt:** a flared frustum with a zigzag ring (≈ 16 verts), hem heights varied ±0.03 H. **Fist:** bevelled box with a thumb wedge; the grip passes through. **Strap:** a ribbon on the torso rings at +0.02 H, not a BVH projection.
- **Review order:** round 0 (no Opus) locks the blockout and camera by silhouette IoU, split by body band. Rounds 1–6 judge the clay look on structure; the legion colour look joins at about round 7, scored as a separate pass/fail read, never averaged with the clay score.
- **Blind-modelling mitigations:** every build writes a debug sheet (Workbench ortho front, side and the hero camera, random colour per object); normals recalculated on every bmesh; a table of part sizes in H printed each build; asymmetric FK angles in `P`; camera locked after round 2.
- **Cut for now:** paper grain and per-face jitter (until the colour pass), a modelled face, BVH strap.

## Rejected approaches

- **Skin modifier body.** Two radii per vertex give boxy 4-sided sections; branch points (shoulders, hips) come out lumpy. Fine for a quick blockout only.
- **Metaballs.** Blobby, one global resolution, weak control; the 5.x SDF nodes replace them.
- **Armature with automatic weights.** Bone heat fails on meshes of many pieces. FK-posed construction needs no rig for one static render.
- **Importing a CC0 base mesh** (Quaternius Superhero, Blender Studio human base meshes). It works against the brief ("a modelling challenge") and needs weights to pose. Kept as plan B for the body only.
- **SDF-fused body for v1** (advisor). The armour covers every join; fusion adds voxel cost and terraces for nothing. Fallback if the pec/abs region will not read.
- **Palette-atlas texture.** A game-engine optimisation; per-material colour gives the same look in a render.
- **Modelling in a T-pose and rigging with Rigify.** Heavy, and a static pose does not need it.

## Numeric targets

From `references/lowpoly_legionnaire.png` (1000 × 1000), sRGB. Region medians; `references/ref_mask.png` is the thresholded silhouette (subject black).

- **Frame:** figure bbox x 212–785, y 42–954 (sword hilt to shield edge, crest to soles). Silhouette covers about 28 % of the frame.
- **Landmarks (y):** crest top ≈ 40, helmet dome ≈ 100, helmet bottom / cheek guards ≈ 290, shoulder-pad tops ≈ 320, belt 490–530, skirt hem ≈ 690–720, boot tops ≈ 780, soles ≈ 954.
- **Widths:** body at chest (y 400) x ≈ 278–635 (≈ 360 px, arms included); shield x ≈ 625–785, y ≈ 340–750; helmet width ≈ 160 px.
- **Proportion:** ≈ 5.3 heads (crown to sole ÷ head without helmet), ≈ 4.5 helmet heights. Shoulder span ≈ 2.2 helmet widths.
- **Material (clay look):** lit faces ≈ (212, 174, 106); mid ≈ (187, 147, 80); shadow side ≈ (129, 98, 48). Shadow ÷ lit ≈ 0.6 in value.
- **Backdrop:** ≈ (245, 220, 174) mid-frame, (243, 216, 170) top corners, (251, 225, 179) bottom right. Floor between the feet ≈ (238, 207, 154).
- **Contact shadow:** darkest by the soles ≈ luma 105–130 in a thin band; 20 px below the soles the floor is back to ≈ 205. The broad cast shadow is faint (≈ 5 % below the backdrop).
- **Facets:** body triangles ≈ 15–40 px across at this scale; armour faces larger and cleaner.

## Open questions

- Does Decimate COLLAPSE on dense lofts give the reference's facet size and irregularity, or do lofts with few rings (hand-faceted) read better? Test both on the torso at v01.
- Do overlapping lofts show seams at the neck, elbows and knees where no armour covers them? If yes, fuse the body with SDF.
- Camera: which focal length and height match the reference's perspective? Tune against the silhouette mask.
- Does the colour pass still read as the same model? Review the clay look first.

## Sources

Web (read this session, via four research agents):
- https://80.lv/articles/001agt-stylized-character-art-workflow-from-blockout-to-render
- https://80.lv/articles/the-soul-of-low-poly-characters
- https://80.lv/articles/liu-hao-low-poly-character-creation
- https://80.lv/articles/check-out-this-low-poly-head-sculpt-made-in-blender
- https://80.lv/articles/character-design-shape-language-and-readability
- https://80.lv/articles/cannibal-stylized-character-breakdown
- https://cdn.fastly.steamstatic.com/apps/valve/2008/GDC2008_StylizationWithAPurpose_TF2.pdf
- https://steamcdn-a.akamaihd.net/apps/valve/2007/NPAR07_IllustrativeRenderingInTeamFortress2.pdf
- https://bazaar.blendernation.com/listing/detailed-low-poly-characters-my-workflow-essential-tips-blender/
- https://grantabbitt.substack.com/p/crafting-a-low-poly-axe-in-blender
- https://www.onlinedesignteacher.com/2019/01/low-poly-character-modelling-part-1.html
- https://www.katsbits.com/tutorials/blender/character-beginning.php
- https://imphenzia.com/crispoly-characters-mini, https://imphenzia.com/imphenzia-pixpal
- https://www.blendernation.com/2024/03/14/shade-auto-smooth-missing-in-blender-4-1/
- https://www.blendernation.com/2020/05/21/texturing-low-poly-art-with-color-palettes/
- https://www.polygon-treehouse.com/blog/2017/12/6/swatch-magic
- https://cgiacademyhub.com/blog/modelado-low-poly-blender
- https://mages.edu.sg/blog/common-mistakes-in-3d-character-design-how-to-avoid-them/
- https://blog.neural4d.com/comparisons/a-pose-vs-t-pose/
- https://blenderartists.org/t/rigging-in-a-hero-pose/1543021
- https://blenderartists.org/t/bone-heat-weighting-failed-to-find-solution-for-one-or-more-bones/1144412
- https://jessyleite.dev/posts/blender-bone-heat-weighting-failed/
- https://sinestesia.co/blog/tutorials/python-tubes-cilinders/
- https://docs.blender.org/api/current/bmesh.ops.html
- https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/skin.html
- https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/decimate.html
- https://code.blender.org/2025/10/volume-grids-in-geometry-nodes/
- https://b3d.interplanety.org/en/quickly-apply-all-modifiers-to-the-object/
- https://github.com/makehumancommunity/mpfb2, https://github.com/jhodges0845/blender-object-generator
- https://quaternius.com/packs/universalbasecharacters.html
- https://developer.blender.org/docs/features/asset_system/asset_bundles/human_base_meshes/
- https://www.proko.com/course-lesson/human-proportions-idealistic-figures/
- https://twotap.art/blog/how-to-draw-body-proportions-for-stylized-characters/
- https://blog.cg-wire.com/character-shape-language/
- https://www.cookandbecker.com/en/article/378/designing-overwatch.html
- https://en.wikipedia.org/wiki/Contrapposto, https://en.wikipedia.org/wiki/Body_proportions
- http://characterdesignnotes.blogspot.com/2010/11/how-to-kill-great-character-design-part.html
- https://anim.works/silhouette-in-animation/
- https://3dxdev.com/low-poly-art-the-rules-that-separate-style-from-unfinished/
- https://gridmakerpro.com/learn/asaro-head/
- https://nastyrodent.com/stylized-3d-characters-art-direction-principles/
- https://wiki.previspro.com/shots/lens-choice-for-character
- https://www.creativeshrimp.com/character-lighting-techniques.html
- https://lowpolyfactory.com/, https://www.kartzystudio.com/
- https://en.wikipedia.org/wiki/Imperial_helmet, https://en.wikipedia.org/wiki/Lorica_segmentata, https://en.wikipedia.org/wiki/Cingulum_militare, https://en.wikipedia.org/wiki/Scutum_from_Dura-Europos
- https://www.romanmilitaryresearchsociety.com/post/centurion
- https://x-legio.com/en/wiki/musculata, https://x-legio.com/en/wiki/scutum
- https://www.larp.com/legioxx/scutum.html
- http://byzantinemilitary.blogspot.com/2019/07/did-roman-legionaries-wear-red-tunics.html
- https://sketchfab.com/3d-models/low-poly-roman-soldier-b1996cdaa9324a3281240339cd35a6a3 (and three other low-poly Roman soldiers)

Local: `reference/manual` (decimate, skin, smooth by angle, bone parenting), `reference/api-dump-5.2` (every bmesh.ops, modifier and GN node name above), `knowledge/gotchas/geometry.md` (SDF traps).

Found nothing: a sourced head count for Synty/Overwatch-style heroes; Imphenzia's step-by-step method (video pages would not render); any studio behind the "Low Poly Factory" cube logo; a worked SDF smooth-min on grids in 5.x; Polycount wiki (unreachable) and several Polycount/Medium/ArtStation pages (403).
