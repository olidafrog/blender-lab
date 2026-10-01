# Review v08

**Score:** 6.0 / 10

## Targets

- Hit: red lit (218, 58, 67), cream lit (237, 234, 208), cream shade (125, 123, 110), yellow lit (240, 224, 144), orange lit (231, 131, 90), glass lower (35, 27, 18), sky top (149, 175, 210), sky low right (203, 228, 249).
- Glass upper (47, 72, 99): missed. p90 luma 89 vs 148: missed
- Pavement (186, 167, 161): missed
- Brick neighbour (100, 54, 31): missed
- Layout IoU mean: 0.338, flat-trace level.

## What works

- The layout reads correctly: the tower, the oculus bands, the pilasters with cream squares and the stepped motifs.
- The ground-floor shutters, hexagons and red base band are close.

## Problems, ranked

1. **Glass.** The lower panes reflect stacked brick boxes and flat blue triangle mountains. The upper glass is flat slate with no sky gradient. Fix: change the mechanism. Delete the box city. Use a photographic urban backplate or HDRI that only glossy rays see. Tilt each pane's normal at random by 0.2–0.5°. Upper p90 luma should be 130–160.
2. **Clean surfaces and missing context.** The paint is uniform except for a procedural blotch on the red. Edges are razor-perfect and nothing shows grime. The right neighbour is a flat tiled wall, not an RC frame with brick infill. The pavement joints run diagonally. Fix: add streaked dirt masks under every ledge, with value variation of ±3–5%. Bevel edges 5–10 mm. Model the neighbour's frame, openings and rebar. Run the joints square to the facade and add stains and a kerb.
3. **Shadows are too few, too short and too brown.** Shade share is 0.18 on cream (target 0.30) and 0.01 on red (target 0.03). The blue channel in orange and yellow shade is 32 and 66 (targets 56 and 85), so warm bounce fills the shadows, not sky. Fix: set relief to 0.15–0.3 m proud. Let the physical sky light the diffuse, and remove any warm fill.

## Research check

- Sun from the front right, parallel verticals: agree.
- Gold frames on dark glass: agrees in the lower bays only.
- Relief 0.1–0.3 m proud: contradicted. The shadows read shallower.
- Orange paint lines: missing on the upper yellow bands.

## What 8.5 needs

- Photographic glass reflections.
- Grime, softer edges, and a modelled neighbour and pavement.
- Deeper relief and sky-filled shadows.
- Large chrome faceted diamonds. They are now tiny dark triangles.
- Flat-topped terracotta tanks. They are now pink domed capsules.
- Small stacked cornice caps. They are now wide flat trays.
- Round oculi on the left wing. They are now square.
- A legible "Crucero del Sur" sign.
