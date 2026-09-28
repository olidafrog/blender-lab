# eclipse-glow — brief

## v2: Wonder logomark (2026-09-26)

Put the Wonder logomark (`library/models/wonder-logos`, object `wonder_logomark`) into the eclipse-glow look from v1 (`references/eclipse_glow_ref.jpg`): sunset gradient body from camera-space normals, spectral rim, halo, crescent lens, bloom, grain.

- Deliver an editable `.blend`: the material as one control node, the compositor as one Post node with a live preview, per the project skills.
- The background comes from the world colour. The render must not be transparent.
- The logo must stay legible as the Wonder mark.

v1 (sphere, Suzanne, torus): `scripts/eclipse_glow.py`, runs on 4.4 and 5.x.
