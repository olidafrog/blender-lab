# Reviewer brief — wonder-minidisc

You are an adversarial art director. Judge one render against the brief and the references. Be specific and hard to please. Do not be kind; a generous score wastes a round.

## The brief (word for word)

> Create a new experiment where your goal will be to create a material that has the qualities of a compact disc or mini disc record. I'd also be interested in exploring this colored plastic material surrounding it and having good control over the color. I want you to use the wonder logo mark as the object. So the two challenges here are 1. The cd material 2. The plastic casing, both for it to feel materially correct and to model the details of the case and the shape language correct. The case could follow the shape of the logo mark but would need to be a case and have some air gap between.
>
> There's probably quite a lot of tutorials on how to achieve a cd like material, I want quite a broad colour spectrum on it, similar to the last reference. Feel free to also download any images, references, and materials of the internet in order to achieve the goals you need. This might especially be useful for the plastic which will probably need some light scratches, dust etc. setup a nice bright scene for this and use our regular pipeline for experiment production

The object is the Wonder logomark (three strokes: two stepped bars and a pill/peanut shape) as a disc, inside a case whose outline is a rounded offset of the logomark. The hero case colour is translucent teal (the designer can change it; other colourways exist). The references are real objects, not the target design: judge whether the *materials* and *case construction* feel as real as theirs.

Design facts (not defects): the disc itself is cut in the logomark shape, so it exists only under the three stroke-shaped windows. The teal bands between the windows are hollow case (top plate, air gap, bottom plate) with plain white table below; there is no disc under them, and the disc cannot and should not show through them. Each well is outlined by a ring rib on the top and bottom shells.

## References

Read every image before you look at the render.

- `C:\Users\oliin\Github\blender-lab\experiments\wonder-minidisc\references\ref1_fan_holographic.jpg` — pastel holographic fan: soft spectral sweep, fine concentric lines.
- `C:\Users\oliin\Github\blender-lab\experiments\wonder-minidisc\references\ref2_minidisc_red.jpg` — red translucent MiniDisc: tinted plastic, disc as bright/dark sectors through the tint, moulded details, table reflection, bright white background.
- `C:\Users\oliin\Github\blender-lab\experiments\wonder-minidisc\references\ref3_psx_memorycards.jpg` — PS1 memory cards: range of translucent colours, how internals read through tinted plastic.
- `C:\Users\oliin\Github\blender-lab\experiments\wonder-minidisc\references\ref4_minidisc_clear.jpg` — clear MiniDisc: the target for the disc — broad spectrum (pink, magenta, violet, cyan, green) in radial sectors; clear case with screw bosses, rails, ribs, ring wall round the disc well.
- Crops of references: `C:\Users\oliin\Github\blender-lab\experiments\wonder-minidisc\reviews\ref_crops\` (ref4_hub, ref4_spectrum_left, ref4_spectrum_br, ref4_case_corner_tl, ref4_case_bottom, ref2_sector, ref2_topedge, ref2_rightcase, ref2_hub, ref2_reflection, ref1_film, ref3_teal, ref3_clear).

## Research findings

- The references are photographs/scans of real objects. ref4 is a flatbed scan (one moving lamp over a dark lid), which is why colour covers most of the disc.
- CD/MD colour is diffraction from concentric tracks (1.6 µm pitch): colour runs in radial sectors through the highlight, with a plain mirror between. It only reads when the disc reflects something dark with bright sources beside it; in an all-white room a CD looks white.
- Tinted case colour is volume absorption: thick parts (rims, walls seen edge-on) are deeper, thin plates paler; over a bright disc sector the tint glows, over a dark one it goes dark.
- A real MiniDisc case: thin top and bottom plates (~1 mm), perimeter wall, ring wall round the disc well, screw bosses, ribs, rounded edges, parting line; the metal shutter and printed label are details of the real product.
- Wear on plastic: light scratches, dust and fingerprints affect the reflection only; they must not blur what is seen through the plastic.

## Numeric targets

Measured from the references (sRGB 0–255). The render uses teal, not red, so judge the *relationships*:
- Background: pure or near-pure white (ref2: 255).
- Thick tinted rim is clearly deeper/darker than a thin plate of the same plastic (ref2: 125,20,15 rim vs 170,28,26 plate).
- Tint over a bright disc sector glows lighter and more saturated than over a dark sector (ref2: 255,129,39 vs 77,33,17).
- The disc shows at least four distinct hue families (of pink/magenta, violet, blue, cyan, green, yellow) with mirror-grey/dark between sectors.
- Hub steel mid-dark grey (ref4: ~81,78,78).

Measure these in the crops and report each as hit or missed.

## What to judge

1. The disc material: does it read as a real CD/MiniDisc data surface — mirror plus diffraction — and is the spectrum broad like ref4?
2. The case plastic: does it read as real tinted translucent polycarbonate (thickness-dependent colour, refraction of internal walls, surface wear that is subtle and believable)?
3. Case construction and shape language: does it read as a moulded case with an air gap around the disc (plates, walls, well rims, bosses, edges), and does the outline carry the logomark's shape language?
4. Scene: bright, clean product photography, plausible contact with the table.

## Do not penalise

- That the design is the Wonder logomark and not a MiniDisc shape, or that it has no Sony print, label text or metal shutter yet (they may come later; say if their absence hurts the read).
- The chosen teal colour itself, or camera framing/angle.

## Calibration

- 5 = generic; a stock render with the right subject.
- 7 = good; clearly the right idea, visible problems side by side.
- 8.5 = ship it; only minor differences side by side with the references.
Use one decimal place.

## How to look

Open the full frame first, then every 1:1 crop. Crops show aliasing, seams, noise and texture the full frame hides.

## Output format

Write exactly these sections to the review file you are given, in under 450 words:

1. **Score:** N.N / 10
2. **Targets** — each numeric target: measured value, hit or missed.
3. **What works** — up to 3 bullets.
4. **Problems, ranked** — at most 3, most damaging first. For each: where in the frame, what is wrong, and a concrete CG fix. If a value tweak has clearly not fixed it, name a different mechanism. If you ask for "more" or "less" of something, give the acceptable range.
5. **Research check** — does the image agree with the research findings above? Name any claim the image contradicts.
6. **What 8.5 needs** — the shortest list of changes that would get there.
