# Review v09

## 1. Score: 6.0 / 10

## 2. Targets

- red lit (219, 58, 67): hit
- cream lit (237, 234, 208): hit
- cream shade (90, 86, 82): missed, 24–28 low
- yellow lit (240, 224, 144): hit
- orange lit (231, 132, 90): hit
- glass upper (50, 53, 71): hit; p90 luma 82 vs 148: missed
- glass lower (54, 43, 15): missed, too bright and yellow
- sky top (149, 175, 210): hit
- sky low right (203, 228, 249): hit
- pavement (187, 168, 161): missed, blue +27
- brick neighbour (62, 55, 52): missed, red −21
- Layout IoU mean 0.325: no better than a flat trace.

## 3. What works

- The paint colours in sun hit target.
- The layout and sky gradient match.
- The mouldings have real stepped depth.

## 4. Problems, ranked

1. **Glass in every bay.** The reflections show a foreign city: tower blocks and a gold onion dome (upper-left bay). The lower-left bay glows amber. Upper glass is flat navy, with no sky. The big bays lack thin gold vertical frames. Fix: replace the HDRI in reflections with a modelled El Alto backdrop: low brick houses, a mountain line and pale sky above. Upper glass then reaches p90 luma 130–160, and lower glass stays under luma 40. Add gold mullions on a 1 m grid. Tilt panes randomly 0.3–0.8°.
2. **Diamonds and oculi.** The silver diamonds appear as small brown triangles. The orange lines in the yellow rings are missing. Fix: model faceted mirror diamonds about 40% of the oculus width (metallic 1, roughness 0.03–0.08). Paint two orange lines in each ring.
3. **Left corner, neighbour and surfaces.** The left side is a grey placeholder slab. The right neighbour is tidy and glazed, but the reference shows raw brick, a bare frame and rebar. Fine procedural mottling on the red reads as noise. Fix: model the stepped side elevation with its oculi and chamfered glass. Make the neighbour raw brick. Replace the noise with a 2–5 m fade (±4% value) and streaks under the sills.

## 5. Research check

Sun direction, verticals, sky and scale agree. The shadows contradict the photo: they lack blue (orange shade blue 32 vs 56), and cream shade is too dark. The glass contradicts "dark reflective curtain wall in thin gold frames".

## 6. What 8.5 needs

- A matched reflection world and gold mullions.
- Mirror diamonds and the painted ring lines.
- A modelled left corner and a raw-brick neighbour.
- Stronger sky fill, so cream shade reaches about (114, 112, 110).
- Large-scale weathering.
- Greyer, worn pavement near (170, 151, 134).
