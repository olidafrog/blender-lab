# Opal essence: decisions

Experiment: `opal-essence`. A milky, opalescent resin plate over dark hardware, lit through a 5-stop gradient, with raised Wonder type. It ended at 6.5/10 after 11 review rounds (5.3 at the start) and stopped on a plateau. Research is in `experiments/opal-essence/RESEARCH.md`.

## What makes the look

- **The gradient is light behind the plate, not paint on it.** A hidden emission plane sits 0.5 m behind the plate and carries the stops (`Backlight` node). The camera sees it only through the resin, so the stops blur naturally with distance.
- **The milky read comes from transmission roughness.** Frost 0.5 (roughness ~0.3) lets backlight reach the plate from wide angles around each part, so parts behind are lifted and veiled like a real opal diffuser. Four rounds of front-light and scatter-density changes before this did not work.
- **Distance blur is free.** Parts touching the back face (~1 mm gap) read sharp and deeper parts melt, with no compositor work.
- **Exposure decides the palette.** Backlight strength 6 put cream, pink and plate lightness on the ref 02 values. At 3 the plate read as smoked glass.

## Decisions

**A Rayleigh volume, kept weak.** Volume Coefficients with scatter R:G:B ≈ 1:2.3:5.7 is real opalescence. At full strength it shifts every transmitted colour warm: teal goes olive, parts go brown. Opal Blue is set to 0.35 with no absorption, and the designer can raise it.

**The front lights are reflection-only, and linked.** Any front light veils the milk, whatever its ray-visibility flags. Accent lights (Softbox, Rake) reach only the type and hardware through light linking. The thin key strip reaches only the rivets and the top strip; in the flat plate it read as a glowing bar. A cool 5 W fill below the camera is the only light allowed into the milk.

**The frosted base does not reflect.** Principled `Specular IOR Level` is 0. A sharp Coat (roughness ~0.02) does all the reflecting, so lights do not smear across the plate.

**Hardware gets its own lights through shadow linking.** A grazing key and cool rims light only the parts under the plate. The plate is not a blocker for them, so the parts show form through it.

**Raised type is live Text objects in a clear version of the resin.** It uses the same group node with Frost set to 0. With frost on, the type becomes a second diffuser and greys what is under it. SF Mono, because the trial fonts lack `&`, `·`, `—` and `/`.

**Khronos PBR Neutral view transform.** AgX turned orange to peach. A Post Saturation control is exposed, but 1.0 is final.

## Rejected

- Subsurface scattering for the body: no image passes through it.
- Blur in post or from DOF: wrong falloff, and it softens the type.
- A black board behind the left side for the dark zone: it made a hard edge. A dark teal stop does the job.
- Strip banks and env cards for wet highlights on a flat plate: they give a straight bar or a uniform veil. A bright card also bounces off the glossy parts behind and washes the milk.

## Open (why it stopped at 6.5)

- **Wet highlights.** They need folds or warps in the geometry. `--set warp=0.0015` builds an SDF-remeshed plate with a shared analytic warp, and the type and hardware follow it. It still needs something bright to mirror that the parts behind do not also reflect.
- **Teal parts.** The frost haze greys any dark base colour. Try tinting the milk's scatter from the gradient on the left third.
- **Opal blue skin.** It needs front light, which veils the milk. A coloured scatter tint may carry it instead.
- **The Wonder logotype** reads as a soft grey fill. Merge the glyphs into the plate face.
