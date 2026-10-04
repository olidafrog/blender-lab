# References

Everything in `references/` is the user's own material. All of it is in git, the scans included.

## The user's photos: `1.jpeg`–`8.jpeg`

iPhone 16 Pro, 2048 × 1536, taken 2026-10-03 around 11:34 UTC on a bright overcast day. Each position is marked on `annotated floorplan.png`.

The user said photos 1–5 are 0.5× and 6–8 are 1×. The EXIF and the camera fits disagree: **4 and 6 are the 1× camera (24 mm equivalent); the rest are 0.5× (14 mm)**. Trust the EXIF.

| Photo | Shows | Camera | Use for |
|---|---|---|---|
| 1 | West wall, mezzanine end, west window | `Cam_1`, fitted | Kitchen shelves, radiator, floor |
| 2 | The window wall, from the island | `Cam_2`, fitted | The main view. Brick, windows, floor. Brick and floor levels are measured here |
| 3 | From the window wall back to the mezzanine | `Cam_3`, fitted | Mezzanine front, girder, internal windows |
| 4 | Window wall, oblique | **none** | Look only. It was edited after capture and fits no camera |
| 5 | North-west corner: west window and west wall | `Cam_5`, fitted (few landmarks; least sure) | Brick close up, levels |
| 6 | Mezzanine front and dining area | `Cam_6`, fitted | Column, door, bookcase |
| 7 | From the dining area into the kitchen | `Cam_7`, fitted | Kitchen |
| 8 | From the kitchen toward the dining area | `Cam_8`, fitted | Floor pattern close up |

"Fitted" means `assets/cams/<n>.json` holds a camera that matches the photo. The build makes it as `Cam_<n>`. Rendering from it gives the photo's framing. Its `joint` entry is the best fit, so use that.

## Plans

- `annotated floorplan.png` and `floorplans.pdf`: the user's own 1:60 plan at A3 (April 2025), with the photo positions. Room sizes are right. The kitchen layout is out of date, so the photos win.
- `scans/03_10_2026 2/floorplan.jpg`: Polycam's plan. Its 9.00 × 5.82 measures into the reveals. Do not use it for dimensions.

## LiDAR scan

- `scans/03_10_2026.glb` and `scans/03_10_2026 2/03_10_2026.obj` (+ textures): a Polycam scan of the **living level only**, made on 2026-10-03.
- It is the truth for plan positions and heights (±2–5 cm, after plane fits). Never render it or snap to it: it rounds every corner by 5–15 cm and has holes at the glass.
- It still has the furniture in it. The furniture blocks in the model come from it.
- `scan_tools.py` aligns it to the model frame and caches it in `assets/cache/scan.npz`.
- `scans/03_10_2026 2/compass.png`: the bearing out of the windows, 142°.

## Listing photos: `other references/`

The 2023 sale listing of this flat. The photos are wide and clean, with no clutter.

- `1–6 of 12.jpg`: the living room. Good for wall surfaces, window bars and the kitchen. The furniture in them is the previous owner's.
- `bathroom/11 of 12.jpg`: the shower room.
- `top floor/8–10 of 12.jpg`: the bedrooms.

The numbers do not match the plan positions. Listings of **other** Bow Quarter flats must never set dimensions.

## Not yet supplied

- Stair photos (10 steps in two flights). The user will send them.
- A tape measurement of one floor plank.
- A close, straight-on photo of the brick wall (bond and course height).
- A scan of the upper floor, the hallway and the shower room. Today these rooms come from the plan only.

New references go in `references/<topic>/` (e.g. `references/furniture/sofa/`). Record the user's words about them in that round's section of `BRIEF.md`.
