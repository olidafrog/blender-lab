# clouds

## Brief

> I want to start a new experiment and call it Clouds. And your goal here is going to be to create a Blender environment that can generate very realistic looking clouds and make them pretty configurable in terms of things like colours, how they react to light, I think this is really a challenge of realism and I think research will play a big part into this, both in terms of how clouds, what the actual properties of light in cloud actually are, but more importantly I assume there's going to be a lot of people already with tutorials on how to do this in Blender. Your goal is to be able to create realistic clouds and to keep them as modular and dynamic as possible so that we can have different setups of clouds, from single solitary clouds to bigger kind of masses of cloud. And then how do we put objects within them and have them kind of intersect and interplay with the cloud in a realistic manner? What if we put a light source within the clouds? Does it I want it to be able to react to the light in a realistic way?

## References

- `01_pink_ring_quarry.jpg` — pink cumulus-like puff hovering over a white quarry at dusk, a thin neon ring orbiting through it. Take: dense billowy cauliflower lobes, soft self-shadowed pink, the ring passing *behind and in front* of the volume, faint glow bleeding into the cloud where it enters, cyan-tinted ground bounce under it.
- `02_pink_rod_sky.jpg` — pink cloud with a neon rod piercing it against a clear blue sky. Take: small, sharp, popcorn-scale billows (fine detail at the edge), cool blue sky fill on the shadow side, a hot glow where the rod enters the volume.
- `03_lone_sunset_cumulus.webp` — one small cumulus at sunset in a dark gradient sky. Take: warm lit top and cold dark base, strong silhouette, single solitary cloud scale.
- `04_cumulonimbus_street.webp` — towering cumulonimbus backlit behind a street. Take: scale (a mass of cloud), multiple-scattering brightness inside, the dark base, depth through stacked towers.
- `05_volcanic_plume.webp` — steam plume lit red from below by lava. Take: a light source *inside/under* the cloud glowing through it, dense white billows against a dark storm sky.

## Target

A modular cloud system (one reusable cloud generator + one cloud material with designer controls) that can produce all five setups. Each "scene preset" is judged against its reference. Score 8.0 from the reviewer on the hero preset (`pink_ring`, ref 01) and ≥ 7.5 on the realism preset (`sunset`, ref 03).

## Budget

12 review rounds across presets, extended by 2 on 2026-09-28 for the v13 camera/haze pass (user request). When they are spent, `review-render` stops and reports; the user can extend it.

## Deliverables

- `output/FINAL_clouds_<preset>.png` for each preset worked on
- `output/clouds.blend` with a `HOW_TO_TWEAK` text block: one Cloud control node (shape) and one Cloud Material control node (colour/light), presets switchable from `build.py --set preset=...`
