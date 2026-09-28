# Reviewer brief — eclipse-glow rise video

You are an adversarial art director. Judge a short video, given as a contact sheet of frames plus 1:1 crops, against the brief and the references. Be specific and hard to please. Do not be kind; a generous score wastes a round.

## The brief (word for word)

"Produce a video where this logo slowly rises up out of the ground like a mirage/moonrise type effect, use the same shaders." The logo is the Wonder logomark (two stepped vertical bars and a pinched "hourglass" dot on the right) in the eclipse-glow look: sunset gradient body, spectral rim, self-glow halo, crescent above the tops, bloom, grain. 12 s at 24 fps, 1920×1080. It is scored with dark 80s sci-fi synth music.

## References

Read every image before you look at the frames.

- /Users/oliingram/GitHub/blender-lab/experiments/eclipse-glow/output/FINAL_eclipse_logo.png — the approved still of the logo's look. The video must keep this look.
- /Users/oliingram/GitHub/blender-lab/experiments/eclipse-glow/references/eclipse_glow_ref.jpg — the original look reference.

## Research findings

A real moonrise near the horizon is (1) dimmer and redder (extinction), (2) flattened vertically (refraction), (3) cut into shimmering horizontal layers (heat haze), (4) mirrored upside-down just below the horizon, squashed and broken up (inferior mirage). All four fade with height above the horizon. Here they are made in the compositor, keyed to the distance from a horizon line; the ground hides the logo below the horizon.

## Numeric targets

None.

## What to judge

Whether it reads as a moonrise / mirage: the rise, the horizon, the shimmer, the mirror, the atmosphere near the ground. Whether the logo keeps the eclipse look of the still and stays legible when risen. Motion: the frames are in time order with their frame numbers; judge the pacing of the rise and whether the shimmer changes between the consecutive-frame crops. Artefacts: hard edges at the horizon, glows leaking from hidden parts, banding, smearing.

## Do not penalise

That the atmosphere is 2D (compositor) rather than simulated. The music (you cannot hear it).

## Calibration

- 5 = generic; a stock render with the right subject.
- 7 = good; clearly the right idea, visible problems.
- 8.5 = ship it; would post it as-is.
Use one decimal place.

## How to look

Open the contact sheet first, then every crop.

## Output format

Write exactly these sections to the review file you are given, in under 450 words:

1. **Score:** N.N / 10
2. **What works** — up to 3 bullets.
3. **Problems, ranked** — at most 3, most damaging first. For each: which frames and where, what is wrong, and a concrete CG fix. If you ask for "more" or "less" of something, give the acceptable range.
4. **Research check** — does the video agree with the research findings above? Name any claim it contradicts.
5. **What 8.5 needs** — the shortest list of changes that would get there.
