---
name: research-reference
description: Use before building anything for a new Blender experiment or reference image, and again whenever a reviewer's structural complaint repeats for two rounds, the score stalls, or you are about to brute-force values to match a look. Also use when the user asks "how was this made" or "what technique is this".
---

# Research the reference

Work out how the reference was probably made, then find the Blender techniques for it, before you build. Guessing values in Blender is the slowest path. A known technique, or a recent Blender feature you did not know about, often gets most of the way at once.

## Steps

1. **Look hard at each reference.** Read every image, then 1:1 crops of the telling areas (`tools/crops.py`). Write down what you see as physical or digital effects: light path (refraction, caustics, dispersion, subsurface), surface (grain, print, bumps), camera (DOF, bloom, lens distortion), post (blur, halftone, grain, grading).
2. **List hypotheses.** For each effect, 2–3 ways it could have been made: photographed practically, rendered in 3D, or made in 2D/post. Say which is most likely and why.
3. **Check local sources first.** Search `knowledge/` for each effect (`grep -ri`); past experiments may have the answer or the trap. Then the local Blender manual and release notes in `reference/` (see the `blender-docs` skill): a feature added in a recent version is often the shortcut.
4. **Search the web.** Use WebSearch and WebFetch, in parallel subagents if there are many effects. For each effect look for:
   - Blender tutorials and breakdowns (Blender Stack Exchange, Blender Artists, YouTube breakdowns, artist posts),
   - recent Blender features that do it natively. Check the release notes for the Blender version you run (`tools/blender.sh` prints it), for example Cycles manifold next-event estimation for caustics, and new compositor or shader nodes,
   - how the real-world process works (printing, glass, film), if the reference looks photographed,
   - render-side traps for the effect: aliasing of fine patterns, fireflies, denoiser smearing.
5. **Write `RESEARCH.md`** in the experiment folder, sections in this order:
   - **Read of the reference** — the effects, in the order they matter to the look.
   - **Most likely process** — one paragraph.
   - **Techniques to use** — per effect: the Blender approach, the source link, the Blender version it needs.
   - **Rejected approaches** — and why.
   - **Numeric targets** — measured from reference crops: key colours, edge widths in px, black and background levels, pattern pitch. These settle arguments between review rounds. For a "recreate this image" task, `tools/measure.py <ref> <render>` gives the same-procedure table (levels, blacks, grain) and `tools/fit_camera.py` fits the camera from landmark pairs. Measure regions (median, or 95th percentile for highlights), not single points. If there is a cast shadow, add a pixel row across it (edge width, core value); it sets the light's size. If the subject has a clear outline (a figure, an object), make a reference mask with `tools/silhouette.py --make-ref` and gate every version on its IoU and band widths before a review.
   - **Open questions** — what a test render must settle.
   - **Sources** — the links you read this session, and the searches that found nothing. Local files alone are not research; step 4 is not optional. The `research-gate` hook looks for this heading before it allows edits to `build.py`.
6. **Plan the first build** from the research. The most likely process is the v01 mechanism, not something to try later. For each effect: the mechanism, and the cheap test render that proves it. If the look has fine patterns, include how you will stop aliasing (2× render, then downsample). Then build. Do not wait for approval; show `RESEARCH.md` to the user only if they asked to see it first. Put a one-line process guess in `PROGRESS.md`.
7. Feed the research findings into `reviews/REVIEWER_PROMPT.md` so the reviewer judges fidelity to the real process.

## When stuck mid-project

When the same structural complaint survives two rounds of value changes, stop tuning. Re-run steps 1–5 for that one effect, and add what you found to `RESEARCH.md`.
