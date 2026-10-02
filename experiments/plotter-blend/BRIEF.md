# plotter-blend

## Brief

new experiment called 'plotter-blend'. Here's a reference image for some of the stuff I want to explore, particularly the top left image here, the kind of sphere, and also the bottom left one, the kind of vortex thing.

Yeah. A few things that I want to think about here. First of all, I think there's probably a technical term for this sphere, and there's probably a technical way that it's achieved because I've seen it elsewhere. The other thing is I would love for the final output of this to be SVG strokes so that I could use them with a Pen Plotter. I in the past I've used Sverchok in blender to achieve this kind of thing, So I'm not sure if it's worth exploring using that or if there's another way to do it. I guess I'd be interested in exploring how to produce these kind of shapes if there's some kind of parameterized playground or node setup or maybe it's a geometry node setup that we can get. Again, a target output here is to have SVGs with strokes. So like as opposed to actual mesh geometry. If you can go away and do a bit of research on this, you can use an Opus agent as you see fit, maybe for research purposes. So I'd like you to do, obviously, the main thinking. And can you use an Opus agent for a reviewer, rather than a Fable agent?

## References

- `ref_sheet.webp` / `ref_sheet.png` — the full icon sheet (1500×1001): thin monoline forms with a dot at each node.
- `ref_sphere.png` — 4× crop of the top-left sphere: swirled parallel lines, two eyes, see-through, dots along the lines. Target 1.
- `ref_vortex.png` — 4× crop of the bottom-left funnel: meridians × parallels, see-through, dots at crossings. Target 2.

## Target

Score 8.5 from the reviewer. (Change if the brief needs something else.)

## Budget

6 review rounds (an exploration brief: the method matters more than the last half point). No fork: after round 6 the top ask (cut the lines at the limb) is the reverse of round 1's (draw them through), so it is handed over as the `Back Reach` control. When they are spent or the scores go flat, `review-render` calibrates and, if the best is still more than 1.0 under the target, forks once to a new mechanism with 6 more rounds. Write "no fork" here to skip that.

## Deliverables

- `output/sphere.svg`, `output/sphere_cut.svg`, `output/vortex.svg` — strokes only, in mm, ready for a pen plotter.
- `output/FINAL_plotter-blend.png` — a raster preview of the SVGs (what the reviewer scores).
- `output/plotter-blend.blend` — the parameterised playground, with a `HOW_TO_TWEAK` text block.
- An answer in `RESEARCH.md`: what the sphere is called, how it is made, and Sverchok vs Geometry Nodes vs Python.
