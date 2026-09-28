# Volumes: grids, volume shaders, clouds

## Geometry-nodes volumes

- Cycles rendered a GN grid only when it was named `density`. A grid stored as `shape` and read by an Attribute node rendered nothing. `5.x` `clouds`
- Field to Grid leaves a non-zero background value. Cycles then fills the whole bounding box with fog, and the object looks hollow. Put Set Grid Background (0) after it. `5.x` `clouds`
- A GN-made volume has no material. Cycles ignores the object's material slot and renders default grey smoke, and the Density input has no effect. End the tree with Set Material, as for GN meshes (`geometry.md`). `5.x` `clouds`
- Points to SDF Grid is narrow-band. Sample Grid inside it returns the background value, so a field built from it is hollow. Points to Volume fills the spheres. `5.x` `clouds`
- Mesh to Points overwrites the `radius` attribute with its Radius input (default 0.05). Feed the named attribute into that input. `clouds`
- Field to Grid on a dilated topology gives each sparse tile a single value. It rendered as blocky 8-voxel slabs of thin density under a cloud base, probably the "dark rim" reviewers flagged on sunset v09–v11. Put Voxelize Grid on the topology first. `5.x` `clouds`
- Grid Dilate & Erode adds voxels at the background value. Use it to make room for noise and soft edges outside the source shape. `5.x` `clouds`

## Volume shading

- Volume Scatter's Color is not albedo. It scales each channel's scattering and adds no absorption, so a thick cloud stays white and its shadows go to the complementary colour (a pink Colour gives mint shadows). For a true albedo, add Volume Absorption with Color = albedo at the same density. `clouds`
- Multiple scattering compounds the albedo: 0.98 in one channel turns strongly coloured after 100+ bounces. Map a designer "looks like" colour to albedo with the Christensen–Burley inversion: a = 1 − (4.09712 + 4.20863 C − √(9.59217 + 41.6808 C + 17.7126 C²))². `clouds`
- Keep the free path (1/density) well under the lobe size. At 20/m on 0.8 m lobes, 128 bounces washed every lobe flat. At 100/m the lobes shade each other. `clouds`
- An emitter inside a dense volume shows through only near the surface. At 100/m it was invisible 0.55 m deep and glowed along its whole length 0.3 m deep, with strength ~800 on a 12 mm tube. Set emitters `visible_shadow = False`. `clouds`
- A Sun at 4 W/m² under a sky gradient of strength 1 lit a cloud mostly from the sky: flat and grey. Use about 15. `clouds`
- At 1400×1712, 128 volume bounces and voxel 7 mm: 256 spp took ~17 min. At 128 spp a 3 m cloud took 8–12 min, and the 6 m tower filling the frame took 24 min. `mac` `clouds`

## Cloud look

- Aerial perspective with no noise: a box of Volume Absorption plus Emission, visible to camera rays only (every other ray visibility off, so it never dims the sun). Set σ = Haze / box length, and make the emission colour the designed sky gradient for that ray (Geometry › Incoming) × sky strength. Sky pixels then stay exactly as designed and only the cloud is veiled. A fixed haze colour flattened the sky gradient. Cycles writes no depth for volumes, so a Mist or Z haze in Post cannot find the cloud. `5.x` `clouds`
- The scene is a scale model, so judge perspective by distance ÷ cloud size. A lone cumulus shot on a telephoto lens is 10–20 widths away. A cumulonimbus seen from the ground is only 2–3 heights away, but the camera sits far below its base, looking up. `clouds`
- Cauliflower detail comes from geometry: 5 tiers of spheres, each placed on the exposed skin of all earlier spheres, down to puffs of radius 0.009 × size. Voronoi billow noise on the grid added nothing visible. `clouds`
- Tier 0 as 2–5 big lobes in a row gives the big-lobe hierarchy. Fourteen random lobes read as a ball of same-size popcorn. `clouds`
- Cut a flat cumulus base as a density fade below a noisy height in the shape node. Rejecting lobes below the cut in Python leaves bare spheres. `clouds`
- A sunset shadow side lit only by a designed gradient sky goes teal. The physical sky alone makes it brown-orange and ~50× too bright. Two changes gave ref 03's mauve-grey. First, a split world: the camera sees the gradient (Is Camera Ray), and the cloud is lit by the gradient plus 0.015× the physical sky. Second, a warm fill sun opposite the key at ~4 % of its power. `5.x` `clouds`
- Sky Texture `MULTIPLE_SCATTERING`: `sun_rotation` = the lab's sun azimuth + 90° lines its sun up with a Sun lamp, where azimuth 0 = behind the camera. `5.x` `clouds`
