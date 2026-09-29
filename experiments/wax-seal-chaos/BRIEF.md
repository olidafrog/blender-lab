# wax-seal-chaos

## Brief

Fork request (word for word):

> fork the wax seal project, and try a completely different approach to how you tackle the problem in order to make it better, use chaos and generate a random seed to come up with solutions to making it better

Original wax-seal brief (word for word):

> let's make a new experiment call it wax seal, [Image #1] this is the reference. Again, I think you should probably do a bit of research on this one. I reckon people have got some good tutorials for this in Blender already. The focus here I think is going to be on the quality of the wax itself. There's quite a nice lighting setup here. Don't worry too much about the material in the reference that the wax is sitting on top of. It's really about the wax seal itself and the stamp that's come out of it. I want you to use the Wonder logo logo mark as the object that is being extruded out from the wax. But I would like a fair bit of control over this things like the kind of the bevel of the extrusion and the size of the actual element itself. And I want that element to be quite easy to swap out if I want to use a different shape or model.

### Chaos draw

Seed **2761081326** (from `os.urandom`), one pick per axis from four options each (the pool is in PROGRESS.md):
- Geometry: **Fluid pour** — Mantaflow liquid sim of poured wax, the stamp pressed in as a moving obstacle.
- Material: **Matte-wax BRDF** — Principled with Sheen, no coat, high diffuse roughness.
- Light: **Sun lamp (3° angle) plus a large white bounce card.**
- Process: **Side-by-side reviews** — the reviewer judges composites of reference | render at matching crops.

Baseline to beat: `wax-seal` final 6.4 (calibrated), best 6.6. The Wonder logomark stays; the emblem stays swappable with size and bevel controls.

## References

- `ref_clean.png` — main reference (see `../wax-seal/BRIEF.md`).
- `ref_openpurpose.jpg` — same photo in a screenshot window.

## Target

Score 8.5 from the reviewer. (Change if the brief needs something else.)

## Budget

10 review rounds. When they are spent, `review-render` stops and reports; the user can extend it.

## Deliverables

- `output/FINAL_wax-seal-chaos.png`
- `output/wax-seal-chaos.blend` with a `HOW_TO_TWEAK` text block
