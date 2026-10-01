# Review v11

## 1. Score: 6.5 / 10

## 2. Targets

- Hits: red lit (223, 62, 72), cream lit (239, 238, 214), cream shade (111, 114, 110), yellow lit (242, 228, 148), orange lit (234, 136, 95), glass upper (68, 66, 90), sky top (149, 175, 210), sky low right (203, 228, 249).
- Missed: glass upper p90 luma 104 (ref 148); glass lower (48, 32, 16), R +19; pavement (188, 170, 165), B +31; brick neighbour (59, 49, 51), R −24.
- Layout mean IoU 0.322, below a flat trace (0.33). Cream share is 0.165 (ref 0.226).
- Painted shade lacks blue: red (143, 62, 22) vs (158, 56, 46). Red shade share is 0.01 (ref 0.03).

## 3. What works

- Lit paint colours hit. The oculus tower, stepped crown and arch bands read correctly.
- Verticals are parallel, scale is right, and the sky gradient matches.

## 4. Problems, ranked

1. **Glass (left windows, x 220–470, y 290–470).** A large gold onion dome reflects in the glass. It is the worst CG tell. The lower glass is too warm and bright (p90 74 vs 55). The upper glass is too dull. Fix: remove the dome from the reflection set and put low brown houses and a pale ridge there. Tilt each pane randomly by 0.3–1.0°, so each one catches a different part of the sky. Target upper p90 135–160.
2. **Left corner and roof.** The far left (x 20–110) is a grey untextured block with square windows. The reference has a red-and-cream column with oculi and a chamfered red tower over recessed glass. The roof tanks are pink capsules with domed tops. Make them flat-topped terracotta cylinders, about (225, 125, 100). The corner cornice caps (x 165–380, 1080–1290) show deep sloped tops. Halve their projection.
3. **Shadows and ground.** Cast shadow on red is a third of the reference's, and coloured shade lacks sky blue. Check the relief is 0.15–0.3 m proud. Raise the sky's share of the shade fill until red shade B is 40–50, without lifting lit values. The pavement is clean pink slabs. Use dusty grey-beige concrete near (170, 151, 134), a darker curb and grime at the wall base. Make the right neighbour's brick redder and rougher.

## 5. Research check

Sun direction, sky lift and shift-lens verticals agree. The sparse cast shadow on red contradicts relief 0.1–0.3 m proud. The glass reads grey-violet, not dark and reflective.

## 6. What 8.5 needs

- A fixed reflection environment and per-pane tilt.
- A rebuilt left corner and flat-topped tanks.
- Deeper, bluer cast shadows on the paint.
- Dusty pavement, base grime and a legible "Crucero del Sur" sign.
