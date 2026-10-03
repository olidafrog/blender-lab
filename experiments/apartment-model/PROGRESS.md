# apartment-model — progress

## Setup (2026-10-03)

Mac, Blender 5.2, Metal. Builder Opus 5.5 (this session's model); reviewer Opus.

Applies to v01, and where it lands:
- **Measure, don't eyeball.** The Polycam scan is ground truth for plan and heights: every wall, opening and level in `P` comes from the scan, cross-checked with the user's tape and the 1:60 plan. Scan heights (floor = 0): ceiling 4.09, under-mezzanine soffit 1.94, mezzanine girder underside 3.69. User: 4.05 / 1.91 / 3.55.
- **Fit cameras from landmarks** (`matching-a-reference`): each review view gets a camera fitted to its photo from scan landmarks, with the focal length from EXIF (14 mm or 24 mm equiv; 4:3 frame → sensor width 34.6 mm). Hand-guessed cameras missed by 1.6× in `cyber-model`.
- **Separate colour from grade**: white walls and the brick at true albedo; photo white balance goes in `wb_temp`/`wb_tint`.
- **Exterior light physics** (`cycles.md`, aztechno): one Sun lamp in W/m², multiple-scattering sky, indirect clamp 0, exposure via `film_exposure`. Windows face 142° (SE), London 51.53° N; sun from the date/time of the photos (EXIF).
- **Assert something countable** after each risky geometry step (boolean window cuts): print face counts and bounds.
- **Debug sheet** (ortho plan + section + views, random colour per object) before the first review; preflight sheet before round 1.
- **Window glass**: what it reflects matters more than its physics; the view outside is a backplate/HDRI, not modelled context, for now.
- Scan files are large (OBJ 55 MB, GLB 17 MB): keep them out of git.

**Process guess:** a 1909 RC-framed brick factory with a 1988 mezzanine insertion; the model is clean extrusions placed from scan plane fits (±2–5 cm), the plan for unscanned rooms, photos for detail.

**Advisor (Fable, plan stage):** the diagonal "haunches" are splayed heads of RC pilasters on the side walls; model the frame (pilasters, edge beams, girder, central beam). Model the open casements at the photo angles. Edge correlation is a drift measure, not a gate; edges from a Workbench id pass, judged on the upper band. Lift the sky for lighting but show it dimmer to the camera so glazing bars survive. → All applied in v01: pilasters measured in the scan (x 0.85–1.29, 0.20 / 0.12 proud), hinged sashes with `sash_deg`, `sky_camera` 0.3, id-pass overlay in the review sheet.

**Review instrument:** `renders/vNN.png` is a sheet built by `scripts/review_sheet.py`: per photo a row of photo | render | photo with model edges in red. Cameras: `assets/cams/<n>.json`, fitted by `scripts/fit_cam.py` (landmarks) and `scripts/refine_cam.py` (edge match against the textured scan).

Newest first. Updated after every review. Cost is what the version took: Blender runs and minutes since the last row.

| Version | Score | The one change | Cost | Render |
|---|---|---|---|---|
| v12 | 7.9 (L 8.3, W 7.6, S 7.9, B 7.4); pair preferred v12 over v11; all four targets hit | scalloped bookcase bays over a cupboard base; slimmer steel (40/20 mm); door east jamb 0.78 | 2 runs, 15 min | renders/v12.png |
| v11 | 7.7 (L 8.0, W 8.0, S 7.8, B 6.5); pair preferred v11 | reveals shifted 0.09 toward the central pier (asymmetric splay); overlay draws folds | 2 runs, 15 min | renders/v11.png |
| v10 | 7.4 (new brief; L 7.9, W 7.2, S 6.9, B 7.0); pair preferred v10 | windows closed, no secondary glazing (user); pilaster_x0 0.86→0.77; column depth 0.07; brief: rows by photo number | 3 runs, 15 min | renders/v10.png |
| v09 | 8.1 (L 8.3, W 8.0, S 7.8, B 8.2); pair preferred v09 | fork: joint fit of P + cameras; bookshelf block moved to its scan position | 4 runs, 20 min | renders/v09.png |
| v08 | 7.8 (L 8.3, W 7.8, S 7.5, B 7.0); pair preferred v07 | side-wall edge beams → cove (fold 3.60, 0.07 in) | 3 runs + advisor, 30 min | renders/v08.png |
| v07 | 7.6 (L 8.0, W 7.5, S 7.0, B 7.5); pair preferred v07 | pilasters 0.20/0.12→0.10/0.06 proud, head 0.10; splay 1.70→1.60 | 2 runs, 15 min (first reviewer stalled; its file was complete) | renders/v07.png |
| v06 | 7.5 (L 7.8, W 7.5, S 6.8, B 7.5); pair preferred v06 | splayed reveals 1.70→1.45, pier tops 1.57 | 2 runs, 20 min | renders/v06.png |
| v05 | 7.6 (L 7.9, W 7.2, S 7.5, B 7.8); pair preferred v05 | built-ins: full-length shelves, column radiator (top 0.98 from scan), panel heater; furniture blocks from scan components; cameras 6, 8 by landmark PnP | 4 runs, 40 min | renders/v05.png |
| v04 | 7.3 (L 7.5, W 7.5, S 7.3, B 6.5); pair preferred v04 | pilaster heads 0.30→0.12 (+ camera 8 refit at 768 px) | 2 runs, 25 min | renders/v04.png |
| v03 | 6.7 (L 7.0, W 6.8, S 6.2, B 6.3); pair preferred v03 | segmental arches: spring 3.22→3.50, rise 0.58→0.30 | 2 runs + cam 7/8 refits, 30 min | renders/v03.png |
| v02 | 6.7 (L 7.5, W 5.5, S 7.0, B 6.0); pair preferred v02 | internal windows: sill 2.52→2.64, frame flush; coplanar faces removed | 2 runs, 15 min | renders/v02.png |
| v01 | 6.8 (L 7.5, W 6.0, S 6.8, B 6.0) | first build: scan-measured shell, frame, sashes, mezzanine, kitchen blocks | ~25 Blender runs (scan analysis, camera fits), ~2.5 h incl. research | renders/v01.png |

Stall guard after v03: "pilaster heads too large" was raised in v02 and v03 but never changed until v04 (first change, read from photo 6 crops: a ~0.12 m splay, not 0.30). "Mezzanine front missed" in rows 5/6 is attributed by the v03 reviewer to cameras 5 and 6, not the model; photo 3 hits within 5 px. Camera refits queued after v04.

Stall guard after v04 ("camera fit errors" three reviews): mechanism changed for cameras 6 and 8, from edge correlation against the textured scan (stalls when clutter dominates the frame) to landmark PnP on clean architectural corners plus line constraints (`fit_cam.py`): camera 6 4.0 px rms, camera 8 5.9 px rms at 2048 px. Camera 5 had too few landmarks (14.6 px), kept the scan fit. The dining door misses its landmarks by ~33 px with camera 6 locked: suspect the door position (open item).

Stall guard after v05 ("camera fitting" three reviews): the residual pattern (error grows toward the frame edges, far ends fit) is lens distortion, as the camera research predicted ("if residuals grow with distance from the centre, add k1"). Mechanism change: a radial k1 per camera fitted with the pose (`cam_util.py`, `refine_cam.py k1`), and the sheet shows the photos undistorted to the render's pinhole.

Distortion check (after v05): k1 fitted with pose against the scan stays ~0 (|k1| < 0.004) for cameras 1, 2, 3, 5, 7; k1 from landmarks + lines on photo 3 is ill-conditioned (camera to 2.1 m). The edge-beam lines drift 12–28 px at the frame corners in photos 2 and 3; the scan shows no step at the wall tops (a smooth cove within 4 cm), so the photo's "beam" band is a plaster line the scan cannot resolve. Open item; not chased further this loop.

v06 plan: splayed window reveals (room face 1.70 m → glazing plane 1.45 m, both from the scan's reveal transitions), the mechanism behind the near-view misfits in photos 1 and 5 while photo 2 (head-on) fits; pier tops 1.52 → 1.57 (reviewer, photo 2 scale); dining-door coplanar cleanup.

Stall guard after v06 ("camera fit and lens distortion" three reviews): already acted on (k1 fits, landmark PnP; see above); the v06 reviewer's ranked problems are all model geometry. v07: pilaster projection W 0.20→0.10, E 0.12→0.06, head 0.12→0.10 (reviewer: 10–12 cm too proud; the scan's 0.2 at W was the LiDAR-rounded corner); splay reduced 1.70→1.60 (v06 false arris in photo 2).

Advisor (Fable) after v07, on the stall guard for ceiling lines / edge beams: (a) geometry, not distortion: the scan's side walls curve in from about z 3.3 and meet the ceiling 5–8 cm inside the wall plane; a constant 0.08 m step projects to 6 px far / 28 px near, the measured drift. The model's 3.72/4.08 boxes match nothing. (b) End piers in photos 1 and 7 sit 52° off-axis, where focal error dominates. (c) Central beam underside 3.74–3.765 in the scan. → v08: edge beams replaced by a cove (`cove_z` 3.60 by interpolating the photo 3 overlay: 3.72 was 20 px high, 3.40 28 px low; `cove_in` 0.07).

**Fork (after v08): per-round pixel nudges of single P values → joint fit of P (and camera poses) against all photos at once.** Advisor (Fable): the residual is shared between seven cameras and ~20 dimensions, so one-row nudges trade off between photos (v08's cove: 0–5 px in photo 3, 10–20 px in 1, 5, 6). Built as `scripts/joint_fit.py`: Workbench object-colour renders of the model, model edges (furniture edges masked) scored by truncated distance to photo edges, coordinate search over P with scan priors (σ 3 cm). Fork base: v07 (calibration winner). Budget 10 → 16.

Joint fit (fork step 1): 7 cameras then 21 P values then cameras again, 2.5 min. Mean model-edge distance to photo edges 4.24 → 3.90 px per view (768 px). Most gain from cameras; P moved little (col_w 0.115, col_y 0.00, radiator top 0.94, cove_z 3.69, cove_in 0.05, pilaster_x0 0.86, proud 0.108/0.053, pier_top 1.585, pier_proud 0.145, win_w 1.596): the shell values were already near their best for this metric. Bookshelf block moved to its scan position (x −0.95…0.30) — the calibration reviewer's "extra box at the pilaster".

**Instrument change before v10 (user):** the windows have secondary glazing, open in the photos with some factory casements; only the factory windows are needed. Reviewer brief design fact updated (closed factory windows, no secondary glazing); scores from v10 on are on the new brief, so compare across it only by blind pair. Stall guard after v09 ("edge-beam depth") — acted on (cove mechanism, joint fit); the v09 review does not raise it.

Stall guard after v10 ("camera 5" three reviews): k1 in the joint fit against model edges also stays 0 for camera 5, so the cause is geometry. Photo 5 sees the east window obliquely from 3.9 m; its near (pier-side) jamb at the room face is 24 px off, while v07's reviewer found the outer jambs too wide in photo 2: an asymmetric splay. v11: room-face openings shifted 0.09 toward the central pier (`reveal_shift`). Instrument: the overlay now also draws folds inside one object (studio-shaded pass), so the girder's front arris shows (v10's "girder flush" was the id pass missing it).

User (after v11): wrap up this round regardless of score; stairs are 10 steps in two flights (supports an upper floor at 2.08 = 10 × 0.208 risers) but are not to be modelled now. v12 is the last round; its blind pair against v11 stands in for the separate calibration (user asked to finish). Open after v11: rows 3/5 cove/ceiling line drift at frame edges (k1 stays 0; not resolved).

**Final: v12** (user asked to wrap up this round). Open items from the v12 review: lower-tier glazing rail and right-window mullion spacing; radiator 10–15 cm too high and ~15 cm too far from the window wall; central beam 18 px low in photo 5 only (beam west face or camera 5).

## Calibration

Stopped after v08: slope flat (best of v06–v08 7.8 vs v03–v05 7.6, under +0.3). Calibration: v08 vs v07 (blind). **v07 wins 7.3 vs v08 7.1** (same instrument; the deeper cove fits photo 3 but misses 1, 5, 6). 7.3 is 1.2 under 8.5 → fork once (budget +6).

(At the end of the loop: the best earlier version re-scored blind beside the final. See `review-render`.)
