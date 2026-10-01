# Review v12 — aztechno-building

## 1. Score: 6.3 / 10

## 2. Targets

- red lit (224,62,72): hit
- cream lit (239,238,214): hit; cream shade (124,125,112): hit
- yellow lit (243,228,148): hit
- orange lit (234,136,95): hit
- glass upper (59,71,94): hit; p90 luma 99.6 vs 148: **missed**
- glass lower (44,31,19): hit, at the limit
- sky top (149,175,210): hit; low right (203,228,249): hit
- pavement (189,172,166): **missed**, too pink and bright
- brick neighbour (59,49,51): **missed**, too dark and purple
- Layout IoU mean **0.327**, below the 0.33 flat-trace baseline.

## 3. What works

- Lit paint, sky and exposure match.
- The facade grid, arch bands, oculus rows and central tower are in place. The lower glass reflects a believable street.
- Sun direction is correct.

## 4. Problems, ranked

1. **Roof caps (top edge, x 165–380 and 1075–1290).** Wide flat yellow slabs overhang both corner towers. The reference has small separate blocks: a yellow cap on a red plinth, about 3 m wide, five or six along the parapet. Fix: model each cap as its own plinth-plus-cap at the reference x positions.
2. **Paint and glass read as CG.** The red has large pink procedural blotches (crop 300_600). Real paint is even, with soft plaster edges. The upper and tower glass is a flat dark gradient. Fix: replace the blotches with fine grain (under 5% value variation) and bevel moulding edges 1–2 cm. Make the glass reflect sky and cloud: lower its roughness and tilt panes 0.5–1°. Target p90 140–155.
3. **Diamonds and oculi.** The reference diamonds are chrome gems about 45% of the oculus width, and the brightest things in frame. The render has small dull grey arrowheads. The rings are peach toruses, but should be flat stepped yellow bands with two orange lines and a cream inner ring.

Also weak: a grey placeholder box at the left edge, which should be round medallions on cream. The shutters have no slats, and the right shop has a noise fill. Coloured shade lacks blue (red shade (143,61,22) vs (158,56,46)): desaturate albedo about 15% and add rough specular so shade picks up sky (blue 45 or more).

## 5. Research check

Sun direction, shift-lens verticals and scale agree. Relief depth (0.1–0.3 m) does not. The upper yellow bands cast almost no shadow (red shade share 0.01 vs 0.03). The upper glass does not reflect, which contradicts "dark reflective glass".

## 6. What 8.5 needs

- Separate plinth-and-cap roof blocks.
- Chrome diamonds at reference size, and flat striped oculus rings.
- Even paint, bevelled edges, deeper moulding shadows.
- Sky-reflecting upper glass.
- Left medallions, slatted shutters, and pavement and brick on target.
