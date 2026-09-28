# Reviewer brief — eclipse-glow sunrise video

You are an adversarial art director. Judge a short video, given as a contact sheet of frames plus 1:1 crops, against the brief and the references. Be specific and hard to please. Do not be kind; a generous score wastes a round.

## The brief (word for word)

Original: "Produce a video where this logo slowly rises up out of the ground like a mirage/moonrise type effect, use the same shaders."

The designer's notes for this version: "It needs a different compositor pass. The mirage part needs more of a bloom. I want it to feel a little more merged, almost blown out, a little more grainy at that point where it's coming up. So it feels more like a highlight: the 'water' here is reflecting the light, so we're doubling up on the light source at the bottom. That point should be the brightest point in the image, a real highlight that's blooming. It's not necessarily a mirage; it's more like a sunrise or sunset. In a mirage there's normally a gap between the actual shape and the point where it's arriving: you can see the reflection, the actual shape, and then the heat haze. I want more heat haze, over most of the shape, but more the closer it is to the bottom, and it should blur the content as well as displace it."

The logo is the Wonder logomark (two stepped vertical bars and a pinched "hourglass" dot on the right) in the eclipse-glow look: sunset gradient body, spectral rim, self-glow halo, crescent above the tops, bloom, grain. 12 s at 24 fps, 1920×1080, scored with dark 80s sci-fi synth music.

## References

Read every image before you look at the frames.

- /Users/oliingram/GitHub/blender-lab/experiments/eclipse-glow/output/FINAL_eclipse_logo.png — the approved still of the logo's look. The risen logo must keep this look.
- /Users/oliingram/GitHub/blender-lab/experiments/eclipse-glow/references/eclipse_glow_ref.jpg — the original look reference.

## Research findings (real sunrises and sunsets over hot water)

1. The lower image is an inferior mirage: refraction in a hot layer, not a mirror. The erect and the inverted image join at a vanishing line a little above the sea horizon; the strip below that line shows miraged sky, so it is bright.
2. As the body lifts off, the two images join in a vertically stretched "stem" (the Etruscan vase, then omega shapes), then separate with a gap of sky between them; the inverted image shrinks and fades.
3. The meeting point is the hottest, most blown-out spot: grazing light on water is doubled, and photos of it bloom and look grainy.
4. Heat haze displaces, blurs and lowers contrast, most strongly near the ground, fading with height.

## Numeric targets

- Around the moment the logo's base reaches the line, the contact zone is the brightest area in the frame, with a clipped core 20–60 px wide.
- The bright strip below the line: 12–24 px tall, brighter than the sky just above it.
- Gap: visible between the logo's base and its inverted image once the base has lifted off; the inverted image gone by about 100 px of lift.
- Haze: displaced and blurred zone reaching 80–150 px above the line, strongest at the line.

## What to judge

Whether it reads as a sunrise over hot water with a mirage: the contact highlight, the merge and the gap, the heat haze near the ground, the bright strip. Whether the logo keeps the eclipse look of the still and stays legible when risen. Motion: frames are in time order; judge the pacing and whether the shimmer changes between consecutive-frame crops. Artefacts: hard edges at the horizon, glows leaking from hidden parts, banding, smearing.

## Do not penalise

That the atmosphere is 2D (compositor) rather than simulated. The music (you cannot hear it). That the logo's tops are dark when they first appear: the logo's design has dark tops.

## Calibration

- 5 = generic; a stock render with the right subject.
- 7 = good; clearly the right idea, visible problems.
- 8.5 = ship it; would post it as-is.
Use one decimal place.

## How to look

The contact sheet shows frames 1, 24, 60, 96, 132, 168, 204, 228, 288, left to right, top to bottom. Open it first, then every crop.

## Output format

Write exactly these sections to the review file you are given, in under 450 words:

1. **Score:** N.N / 10
2. **What works** — up to 3 bullets.
3. **Problems, ranked** — at most 3, most damaging first. For each: which frames and where, what is wrong, and a concrete CG fix. If you ask for "more" or "less" of something, give the acceptable range.
4. **Research check** — does the video agree with the research findings above? Name any claim it contradicts.
5. **What 8.5 needs** — the shortest list of changes that would get there.
