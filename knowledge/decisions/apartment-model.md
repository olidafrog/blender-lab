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
