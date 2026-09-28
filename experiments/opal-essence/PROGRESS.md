# opal-essence — progress

Newest first. Updated after every review.

## Setup

- Mac, Blender 5.2.2, Cycles on Metal (M4 Max). 5.x compositor API (node group, sockets as settings).
- Relevant gotchas:
  - Transparent things on black are invisible: something lit must sit behind the plastic to show through it. `caustics`
  - Per-object ray visibility: decide for each lamp whether it shows in reflections, through the plastic, or both. `caustics-v2`
  - Satin sheen without a veil: small glossy-only strip at the mirror point; camera-invisible black flags as negative fill. `printed-plastic`
  - Frosted look: sharp refraction core + wide refraction-only halo; imperfections change glossy roughness only. `printed-plastic`, `caustics-v2`
  - AgX desaturates bright saturated colours (orange → peach); consider Standard or Punchy for the neon gradient. `colour`
  - Library logotype: the GN mesh keeps its own empty material slot; end with Set Material. Check the `.glb` is not empty. `eclipse-glow`
  - Set DOF focus with an empty on the face. Review at full scale. Correctness pass before round 1.
  - Fine surface bumps under ~0.2 mm on a 0.4 m object, or orange peel.

Process guess: frosted transmissive resin (rough base + sharp coat) with a Rayleigh-weighted scatter volume inside, backlit by a hidden 5-stop gradient emitter behind dark hardware; front lights reflection-only via light linking.

## Finished

- `output/FINAL_opal-essence.png` (1024 samples, v11 settings plus the "Won|er" fix)
- `output/opal-essence.blend`: checked by `scripts/check_blend.py` (preview matches the final at 0.00/255 mean)

## Loop stopped after v11

Scores: 5.3 → 5.6 → 5.6 → 5.6 → 5.8 → 5.8 → 6.0 → 5.9 → 6.4 → 6.5 → 6.5. Plateau at 6.4–6.5.
What broke plateaus: frost 0.5 (milky read), removing the key strip's veil, backlight 3 → 6 (exposure).
Still open (each needs a new mechanism, not tuning):
- **Wet highlights**: flat plate has nothing to catch. A warp is built (`--set warp=0.0015`) but a bright reflection card also bounces off the glossy parts behind and washes the milk — needs parts excluded from the card (light-path/shadow tricks) or real folds in the geometry.
- **Teal parts**: the frost haze greys any dark base colour. Colour the milk's scatter from the gradient on the left third.
- **Opal blue skin**: needs front light, which veils; a coloured scatter tint (above) may carry it instead.
- Logotype reads as a soft grey fill; merge the glyphs into the plate face.

| Version | Score | The one change | Render |
|---|---|---|---|
| v11 | 6.5 | Parts under the plate: deep teal anodising (#0a3a40) instead of black; warm rim → cool; Filter Glossy 1.0 → 0.2. Parts still grey (the milk hazes any dark base colour). Stray line through "Wonder" traced to key strips linked to the type — fixed after review. | `renders/v11.png` |
| v10 | 6.5 | Photographic pass: studio environment seen only by glossy rays (Is Glossy Ray gate; no veil in the milk): soft overhead sheen card + low side card for chrome/rims; film grain on the Post node. Grain landed; env reflections too weak to see (coat F0 ≈ 4%). Top complaint: still a lit gel, no wet highlights or warp. | `renders/v10.png` |
| v09 | 6.4 | Brightness: backlight 3 → 6 (measured: median V 0.62 → 0.85; cream #eec489, pink #f7736f, no clipping). Rake moved to the camera side, low, so raised type edges glint. Top complaint: reads as CG — no wet highlights, flat, no grain, screws black holes. | `renders/v09.png` |
| v08 | 5.9 | Batched three long-repeating concrete fixes (deliberate): key strips light-linked off the plate (no glowing bar, 4th round; also removed their spill veil), micro-type ~2× (7th round), wet blobs clear; orange stop 0.80 → 0.84 for a wider cream band. Saturation back to 1.0. Micro-type target now hit. Top complaint: plate reads as dark smoked filter (35–55% lightness vs 80–95%). | `renders/v08.png` |
| v07 | 6.0 | Colour mechanism: the Rayleigh/warm-absorption shift turned teal olive and parts brown. Opal Blue 0.65 → 0.35, absorption off, Post Saturation 1.15 (new control). Top complaint: grey veil in the centre, cream hidden behind parts. | `renders/v07.png` |
| v06 | 5.8 | Near parts touch the back face (0.8 mm gap) so they read sharp; stops retuned so teal wraps the parts cluster and cream sits before orange. Near parts now sharp (worked). Top complaint: left muddy olive/brown (6th round). | `renders/v06.png` |
| v05 | 5.8 | Mechanism change for the 4-round "not milky" complaint: frost 0.22 → 0.5 (a diffuser's wide angle lets backlight wrap around the parts and lifts them). Type material gets Frost 0 (it was a second diffuser greying the logotype). Top complaint: nothing sharp against the back face; parts brown not teal. | `renders/v05.png` |
| v04 | 5.6 | Milk lit from behind everywhere: left stop navy → deep teal, backlight 5 → 3 (fixes red clipping: 81% → 10% of pixels), milk 0.4 → 0.6, fill 40 → 5 W, warm rim 40 → 15. Top complaint: gel filter, not milky resin; parts brown at full contrast (4th round). | `renders/v04.png` |
| v03 | 5.6 | Cool front fill 0.4 → 40 W, moved below camera outside the mirror angle: milky blue-grey skin over the parts. Top complaint: grey veil, not milk; the front-light lever failed in both directions, so change the mechanism. Pastel from red clipping (repeat). | `renders/v03.png` |
| v02 | 5.6 | Parts behind get form: grazing key + teal/orange rims, light-linked to hardware and skipping the plate as a shadow blocker; camera tilt 5° → 14°. Top complaint: left reads as brown tinted glass, no opal blue skin (repeat of v01 #3). | `renders/v02.png` |
| v01 | 5.3 | First build: plate + strip, hardware at 1–16 cm depth, gradient backlight, raised SF Mono micro-type + Wonder logotype. Top complaint: "lightbox with shadow puppets" — parts flat silhouettes, no object read. | `renders/v01.png` |
