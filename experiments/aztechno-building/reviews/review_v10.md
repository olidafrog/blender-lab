# Review v10

## 1. Score: 6.2 / 10

## 2. Targets

- red lit (219, 58, 68): hit
- cream lit (237, 235, 209): hit
- cream shade (95, 97, 97): missed
- yellow lit (240, 224, 144): hit
- orange lit (231, 132, 91): hit
- glass upper (50, 53, 71): hit; p90 luma 82 vs 148: missed
- glass lower (39, 29, 13): hit
- sky top (149, 175, 210): hit
- sky low right (203, 228, 249): hit
- pavement (187, 168, 161): missed
- brick neighbour (52, 40, 39): missed

Layout IoU mean 0.336, a flat trace. Shade shares are low (red 0.01 vs 0.03, cream 0.21 vs 0.30).

## 3. What works

- The lit paint colours and the sky hit, so the palette reads as the photo.
- The central bay, oculus arcs, pilasters and stepped window heads sit in the right places.

## 4. Problems, ranked

1. **The relief is flat, and the shadows get no sky (whole facade).** The cast shadows left of the octagon, arcs and pilasters are 1–3 px wide; the photo shows 6–10 px. Shadows are too dark and warm. Fix: offset the main layers 0.15–0.25 m as real geometry, not bevels. Raise the world light's diffuse share until cream shade is near (114, 112, 110) and the red shade share is 0.025–0.035.
2. **The surfaces look procedural.** The red paint has large blotchy noise; the photo's paint is smooth, with faint streaks under the sills. Pavement is pink and uniform; the street is a noise band. Fix: cut the paint noise to 3% value variation or less. Add grime from AO and edges under sills and cornices. Make the pavement concrete slabs with a kerb (near 170, 151, 134), and cobbles with real bump.
3. **The silhouette and corners are wrong.** The roof tanks need flat tops, not domes. The parapet caps merge into two wide slabs; the photo has seven caps on red pedestals. The left return shows a grey box with square windows instead of red and cream panels with round oculi. The diamonds are small and dull; the photo's are larger mirror chrome. Fix: model them from the oblique references.

## 5. Research check

- Verticals and front-right sun agree.
- The relief contradicts "0.1–0.3 m proud": it reads as 2–5 cm.
- The upper glass contradicts "dark reflective curtain wall": it reflects almost no sky.

## 6. What 8.5 needs

- True relief depth with sky-filled shadows.
- Upper glass p90 luma 130–160: lower its roughness to show the sky.
- Smooth paint with sill grime; real pavement, street, and lit brick near (83, 56, 48).
- Flat-topped tanks, separate parapet caps, a left return with oculi, chrome diamonds.
