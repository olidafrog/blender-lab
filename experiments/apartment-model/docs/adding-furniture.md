# Adding a piece of furniture

One piece, or a small group the user names, is one round. Set up the round as in `CLAUDE.md` ("Starting a new round"), then run the lab pipeline.

## Get the inputs first

Ask the user for anything missing before research:

- **Photos of the piece:** front, side, three-quarter, and a close-up of each material.
- **Tape measurements:** overall width × depth × height, plus the parts that set its look (seat height, leg size, top thickness).
- **The make and model, if they know it.** A product page gives exact sizes and a second source for the true colour. One phone photo cannot separate a colour from the white balance. If it is still on sale, send a research agent for every product photo, the dimension drawings and any spec sheet before building (the sofa's drawings corrected its seat, back and arm shapes four rounds in).

Put them in `references/furniture/<piece>/`. Copy the user's words and numbers into the round's section of `BRIEF.md`.

## Where the code goes

- One module per piece: `scripts/furniture/<piece>.py`, called from `build_furniture` in `build.py`. Its objects go in the `Furniture` collection, so `--set furniture=False` still hides all of it.
- Its values go in `build.py`'s `P` under `# ---- furniture: <piece>`, with keys prefixed `<piece>_`. `--set` only accepts keys that are in that `P`, and `/sync-tweaks` reads it.
- Delete the piece's grey block from the list in `build_furniture` when the piece lands.
- Build in metres in the model frame ([flat.md](flat.md)). The grey block gives the position and footprint, from the scan. Refine the position against the photos' edge overlays, not by eye.

## Building it

- **Model at true size, with bevels.** Real edges are never sharp. For upholstery, the edge roll radius is what reads as a cushion under this room's even light (the sofa: 4.5 cm on seats, 3 cm on arms and backs); face puff alone barely shades. `scripts/furniture/upholstery.py` has the blocks, flanges and deformation fields. Profiled or lofted hard shapes can use `library/models/hardsurface-kit/`. Research soft goods (cushions, upholstery, throws) per piece.
- **Materials start from a scanned texture** (Poly Haven or ambientCG, CC0), not a procedural pattern. Round two lost four rounds to procedural brick and grain. New textures go in `library/textures/` and get a line in `library/README.md`.
- **One group node per material** (`tools/nodes.py`), with designer-named inputs and ranges. Add the piece to `HOW_TO_TWEAK`.
- **Judge colour against the white paint**, as `mat_measure.py` does. The phone's warmth is in the grade, one white balance per photo (`wb_view`), so do not paint it into the albedo.
- **A texture from the real thing** beats a generic scan: a flat, evenly lit patch of a product close-up, high-passed and made seamless (the sofa's `pumice_weave.png`). Size texture features to the pixel footprint: at 3–4 m a pixel is ~4 mm, so a 1 mm weave vanishes.

## Reviewing it

- Write a new `reviews/REVIEWER_PROMPT.md` for the piece: shape and proportion against the photos, then materials.
- **Views:** use the fitted cameras whose photos show the piece, plus 1:1 crops of it. Add a mode to `review_sheet.py` for the round, like `mat`.
- **New photos** get a camera from `fit_cam.py` only if architectural corners show in the frame. A close-up of the piece alone cannot be fitted. Compare those against a render of the piece from a matching angle instead.
- Render with `--scale 2 --finish`: the photos are sharpened phone JPEGs, and a soft render reads as "painted" at 1:1.
- Check every measuring region in both photo and render: a box that lands on a stand-in block in the render cost three rounds in round three.
- After each round, check that the shell, brick and floor have not moved. Rerun `mat_measure.py`; if the piece now covers one of its regions, choose a new region.

## Done

The piece is done when it scores in its round and the `.blend` hand-off has its materials as control nodes. If the piece is generic enough for other projects, ask the user before moving it to `library/models/`.
