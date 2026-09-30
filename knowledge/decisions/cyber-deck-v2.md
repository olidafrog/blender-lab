# cyber-deck-v2 — decision record

Second attempt at the DT-03 radio (`cyber-model` was the first, Sonnet-reviewed, 6.7). Lab defaults this time: three Opus research agents, ten Opus reviews, one Fable advisor consult, blind calibration. Final **6.4** (v10, calibrated 6.4 against 6.2 for v11) of a target 8.5. Trend 4.8, 5.2, 5.6, 5.5, 5.7, 6.2, 6.3, 6.3, 6.4, 6.3. Scores do not compare with `cyber-model` (different reviewer model).

## Chosen

- **Found the original.** ArtStation `VgGQyg` (AFI, 2020): Fusion 360 + KeyShot. A 4K copy, a front orthographic view and the artist's CAD line render went into `references/`. They settled fillet sizes (3–5 mm, tangent), bead-blast grain and wear placement.
- **Plan × section loft** (`library/models/hardsurface-kit/hardsurface_kit.py`): every shell is a rounded plan outline swept through a designed section (foot, wall, 48–55° flat slope band, 1.2–1.4 mm top fillet, 0.4 mm crease, optional undercut stem). Flat n-gon caps, sharp crease stations, smooth fillets. Whole device builds in 4 s; clean in clay and mirror at the first build. Shallow plan bends get the largest radius the edges allow (`Outline.auto(sweep=)`), so the S-step sweeps instead of creasing.
- **Profiled boolean cutters** carry their own rim and floor fillets (`sec_cutter`), each cutter its own object in a Collection operand, Manifold solver with an Exact fallback and a poly-count check. No Bevel modifier after booleans.
- **Black joins by geometry:** black-walled moat channels cut into each lower part along the foot of each higher part (Boolean material transfer); outer shells come down to the table on an inset foot over a hidden black core.
- **Light (advisor, v07):** one small 0.25 m device key at camera-left, off the tops' mirror direction, casting shadows between parts; a dim dome (0.12) as the only ambient; polymer albedo 0.085; far-side key linked to the backdrop only; a card linked to the metals; a dim glossy-only "Card Slopes" behind the camera (10 W; a designer trade-off: more lifts slopes, greys blacks).
- **Wear on the fillet crest only**, tagged at loft time (FACE attribute `wear` on the middle stations of the top fillet), read by the Polymer and Steel groups. Straight scratch strokes from a PIL mask.
- **Parts rebuilt from 4K crops:** dial bracket as a thin aluminium plate (arm + lobe) on a black housing to the table, 36-tooth gear; gunmetal pods with rubber caps in a cradle on a wide LCD shield; separate battery block with raised diagonal panel, INSERT latch, gunmetal strip; tight 34-turn coiled cord looping onto the table; dome plug.

## Rejected

- **v1's extruded plates, vertical walls, 0.5 mm chamfer** — thin CAD plates; the S-step vanished.
- **Bevel modifier after booleans** — Clamp Overlap is whole-mesh: a 2 mm rim fell to 0.16 mm (Exact) with slots and screw holes (research, measured). Bevel before boolean and custom bevel profiles smeared shading.
- **SubD, SDF grid route, GN Mesh Bevel** — star artefacts on booleaned n-gons; voxel-rounded edges and GBs of faces; Miter explodes the mesh.
- **Two 0.9 m softboxes** (v01–v06) — every facet, gaps included, reflected softbox; tops, slopes and walls read the same, p5 stuck at 20–23 through four rounds of moats and undercuts.
- **A far-side key on the device** — tops mirrored it (grey), LCD blew out.
- **Base slab under the plates** — its rim read as a tray round the device for five rounds.
- **Wear on the whole fillet** — a chalky 15–25 px band. **3 mm fillets on 4 mm slopes** — one pillow, no band.
- **v11** (slope card 4 W, roughness 0.44, trimmed shield) — lost the blind calibration.

## Open items

- Blacks still short: 3.5 % of subject pixels under luma 12 against 7.6 %; creases at 20–30 where the reference is under 12.
- The "chrome ribbon" on the S-step is the 1.2 mm fillet crest mirroring the small device key (isolated after the loop: band 89 on target, crest hot). Next: rougher crest faces via the `wear` tag, or a slightly larger key.
- Backdrop top-left 111 against 96 in every round (backdrop key gradient).
- LCD shield reads as a separate frame; pods are short (reference ~10.5 × 24 mm, lying along the shield edge).
- Bead-blast speckle and scratches too faint at 1:1.
