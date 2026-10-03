# apartment-model — decision record

The user's own flat (Flat 233, Manhattan Building, Bow Quarter; a 1909 RC-framed brick factory with a 1988 mezzanine), round one: the shell, judged on dimensional accuracy and detailing against 7 of the user's phone photos. Opus built and reviewed, Fable advised (plan, edge beams, fork). 12 rounds with a fork at round 8; the user asked to wrap up after v12. Final **v12, 7.9** on the revised brief, all four pixel targets hit (pair preferred v12 over v11). Pre-fork: v07 won blind calibration 7.3 vs v08 7.1. Trend 6.8, 6.7, 6.7, 7.3, 7.6, 7.5, 7.6, 7.8 | fork 8.1 | new brief 7.4, 7.7, 7.9.

## Chosen

- **LiDAR scan as ground truth, never rendered.** Polycam OBJ aligned by an area-weighted wall-normal histogram (yaw 0.54°), floor from up-facing faces, every plane from per-family face-position histograms; textured ortho elevations with a metric grid to read openings (`scripts/scan_tools.py`, `scan_render.py`). The model is clean extrusions in `P` (`scripts/shell_kit.py`: filled outlines with holes, prisms, lofted reveal rings).
- **One camera per photo, fitted three ways.** Edge correlation between a Workbench render of the *textured scan* and the photo (Nelder–Mead; works where the scan's furniture matches the photo), landmark PnP on clean architectural corners plus line constraints (where clutter dominates), then a **joint fit** of cameras and `P` against model edges (`scripts/joint_fit.py`).
- **Review instrument:** one sheet per version (photo | render | photo with model edges in red), edges from an object-colour id pass plus a studio-shaded fold pass (`scripts/review_sheet.py`). Pixel targets per element group in the brief.
- **Fork mechanism (v09): joint fit of P + cameras** over all seven photos by truncated edge distance with scan priors, replacing per-round single-value nudges (which traded off between photos). It gave the best single round (8.1).
- Structure read from photos, checked by scan: segmental arches (spring 3.50, rise 0.30), splayed reveals shifted toward the central pier (asymmetric), pilasters with small splayed heads, a cove (fold 3.69, 0.05 in) where the side walls meet the ceiling, not edge beams.
- **Overcast daylight:** CIE overcast world (Lz 9.8, zenith 3× horizon), sky shown at 0.3× to the camera so glazing bars survive, portals in the openings, thin Fresnel glass, indirect clamp 0, exposure +2.5, AgX.

## Rejected

- **Rendering or snapping to the scan mesh:** LiDAR rounds every corner 5–15 cm and has holes at glass.
- **The Polycam floor plan (9.00 × 5.82):** plane fits give 8.74 × 5.63; the plan measures into reveals.
- **Per-camera radial k1:** stays ~0 against both the scan and the model; with sparse landmarks it trades against camera height. The frame-edge drift was geometry (the cove), found by the advisor.
- **Box edge beams at 3.72 and a deeper cove at 3.60:** the cove's depth trades photo 3 against 1, 5, 6; the calibration preferred the shallower line.
- **Modelling the open sashes from the photos:** they were mostly secondary glazing (user); final windows are the factory frames, closed.
- **Photo 4:** fits no pinhole (edited after capture); left off the sheet.

## Open items

- Lower-tier glazing rail and right-window mullion spacing (photo 2); the radiator 10–15 cm too high and ~15 cm too far from the window wall; the central beam 18 px low in photo 5 only (beam west face or camera 5).
- Cove/ceiling lines drift up to 10–20 px at the frame corners of photos 3 and 5.
- Upper floor, hallway, stairs (10 steps, two flights) and shower room are grey boxes from the plan; materials are placeholders (round two: brick, herringbone, paint).

## Round two: brick and floor materials (v13–v18)

User: "Fix the brick and floor materials." New reviewer brief (materials only; scores restart at v13): sheet = photo | render | 1:1 photo and render crops at the same pixels (`review_sheet.py <v> mat`), plus luma relative to the white paint in fixed regions (`scripts/mat_measure.py`). Six rounds, then the slope rule: 5.2, 5.3, 6.1, 6.0, 6.2, 5.8. Calibration: **v18 5.9 beat v17 5.7** blind. No second fork (the experiment forked at v08). Final **v18**: all four luma targets hit (brick/paint 0.22, 0.25 vs 0.21, 0.25; floor/paint 0.93, 0.95 vs 0.89, 0.99).

### Chosen
- **Brick: a whole-wall CC0 scan at true scale, regraded through its height mask** (Poly Haven factory_brick, 1.5 m → 1.36 m so a course is 85 mm; `library/textures/brick/factory_brick`). Faces take the measured brick colour, shifted by the scan's own tone; joints take the mortar colour; wall-scale soot and bloom noises on top. Advisor (Fable): the scan carries arris wear and bloom correlated with the joints, which independent noises cannot fake.
- **Floor: herringbone from integer cells (c = (i − j) mod 2n) with a scanned rustic oak per plank** (Poly Haven oak_wood_planks, `library/textures/wood/oak_wood_planks`): each plank samples one randomly chosen source plank, centred, so no source seam crosses it; 600 × 120, spine along the room; satin roughness 0.3, anisotropy along the plank, 1 mm dark bevel.
- **Grade: view white balance 13000 K** (paint R/B 1.22 vs the phone's 1.24). Material hue judged relative to the white paint.
- **Measuring: photos rectified onto the model planes with the fitted cameras** (`scripts/rectify.py`): spine direction, plank pitch, course height.

### Rejected
- Procedural per-brick grid (v13–v16): "CG tile" three rounds running; the mortar grid was the pattern instead of the tone spread.
- Procedural flat-sawn ring grain (v13–v14): pinstripes, then zebrano. Clean veneer scan (v15–v16): read as fresh-cut top-grade oak.
- Per-brick sampling of a scan (ghost joints inside bricks); a stone detail layer over the grid (keeps the straight grid).
- Khronos PBR Neutral to keep the floor saturated: oversaturated the brick. AgX stays; saturation goes into the albedo and white balance.
- One gain on the whole brick scan: turns grey mortar violet.

### Open items
- Texture contrast is about half the photos' (floor 6–7 vs 8.5–13, brick 4 vs 7.6). The photos' floor is a rustic print with cracks, knots and straight dark streaks: a higher-contrast rustic scan, or a second scan blended per plank.
- Lit window reveals read mauve-grey; in the photos they glow orange-red. The brick in daylight is redder than the plum it reads in shade: a lit-vs-shade trade-off in the albedo, or the phone's processing.
- Plank size: photo 2's rectification read 700 × 140, photo 8 and two reviewers ~20 % smaller; 600 × 120 chosen. A tape measure on one plank settles it.
- Mortar: reviewers split between "paler net" and "dark, flush"; the scan's joints still catch a lit top edge at Relief 0.3.
