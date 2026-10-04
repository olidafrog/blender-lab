# Navigation

Pointers only. Each script's docstring has its usage. Run Blender scripts through `tools/blender.sh` from the repo root, without a `--` (the wrapper adds its own). Plain-Python scripts that need numpy use Blender's bundled Python.

## Folders

| Path | Holds | In git |
|---|---|---|
| `references/` | The user's photos, plans and scans ([references.md](references.md)) | yes |
| `scripts/` | The build and the measuring tools | yes |
| `assets/cams/` | One fitted camera per photo (`<n>.json`) and its overlay | yes |
| `assets/cache/` | The aligned scan (`scan.npz`), made on first use by `scan_tools.py` | no |
| `assets/scan_views/` | Plan slices, sections and elevations of the scan with a metric grid (`scan_views.py`, `scan_render.py`) | no |
| `assets/grid/` | The photos with a pixel grid, for reading landmark pixels (`grid_photos.py`) | no |
| `assets/mat/` | Photo crops and photos rectified onto the floor and window wall | yes (not `.npy`) |
| `assets/joint_fit.json` | The last joint fit of dimensions and cameras | yes |
| `renders/` | Every render and review sheet | no |
| `reviews/` | Reviewer briefs, prompts, reviews, crops, blind pairs, calibrations | yes |
| `snapshots/` | `build.py` as it was at each reviewed version | yes |
| `output/` | Finals, `apartment-model.blend` and its raw EXR | yes |

## Scripts

| Script | Role |
|---|---|
| `build.py` | **The entry point.** Builds the whole scene from `P`, renders the chosen views, saves the `.blend` |
| `shell_kit.py` | Geometry helpers in metres: boxes, walls with holes, prisms, lofted rings, arches, glazing bars |
| `mat_kit.py` | The `Brick` and `Oak_Floor` group nodes |
| `review_sheet.py` | Makes the review image `renders/vNN.png` from the per-view renders. `mat` mode for material rounds |
| `mat_measure.py` | Brick and floor luma relative to the white paint, photo against render |
| `rectify.py` | Projects a photo onto the floor or window wall through its camera, to measure patterns in metres |
| `fit_cam.py` | Fits a camera to a photo from landmark points and lines |
| `refine_cam.py` | Refines a camera by matching the textured scan's edges to the photo |
| `joint_fit.py` | Fits `P` and all cameras together against every photo's edges |
| `cam_util.py` | Lens distortion (k1). It stayed about 0 for every photo |
| `scan_tools.py`, `scan_views.py`, `scan_render.py` | Load, align, slice and render the scan for measuring |
| `grid_photos.py` | Writes `assets/grid/` |

## Which tool for which job

| Job | Use |
|---|---|
| Where is something, and how big? | `assets/scan_views/` first, then plane fits with `scan_tools.py` |
| Does the model line up with a photo? | Build with `--views <n>`, then `review_sheet.py` (red model edges over the photo) |
| A new photo needs a camera | `fit_cam.py` with landmarks on clean architectural corners, then `joint_fit.py --stage cams --only <n>` |
| How big is a pattern (planks, bricks, tiles)? | `rectify.py`, then read the gridded output |
| Is a material's brightness right? | `mat_measure.py` (add regions for new surfaces) |
| A/B two values | `tools/sweep.sh` (shell loops around `--set` are blocked) |
| Bring tweaks made in the `.blend` back | `/sync-tweaks` |

## Shared lab tools used here

`tools/review_round.py` (one review round), `tools/nodes.py` (one-node materials), `tools/comp.py` (the Post node), `tools/preflight.py`. Textures are in `library/textures/` (`brick/factory_brick`, `wood/oak_wood_planks`).
