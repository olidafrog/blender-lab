# Calibration fork — A vs B

## 1. Score
- **A: 6.0 / 10**
- **B: 5.4 / 10**

## 2. Targets (hit = within 15 per channel)

| Target | Ref | A | B |
|---|---|---|---|
| red lit | 230,65,70 | 223,62,72 hit | 217,60,69 hit |
| cream lit | 238,233,215 | 239,238,214 hit | 235,231,204 hit |
| cream shade | 114,112,110 | 111,114,110 hit | 122,123,113 hit |
| yellow lit | 250,219,151 | 242,228,148 hit | 240,222,144 hit |
| orange lit | 230,129,96 | 234,136,95 hit | 229,134,96 hit |
| glass upper | 60,67,82 | 68,66,90 hit | 47,72,99 missed |
| glass upper p90 | 148 | 104 missed | 89 missed |
| glass lower | 29,22,18 | 48,32,16 missed | 31,15,3 hit |
| sky top | 141,176,211 | 149,175,210 hit | 148,175,210 hit |
| sky low right | 214,230,245 | 203,228,249 hit | 203,227,249 hit |
| pavement | 170,151,134 | 188,170,165 missed | 186,167,160 missed |
| brick neighbour | 83,56,48 | 59,49,51 missed | 101,55,32 missed |
| label IoU mean (flat trace 0.33) | | 0.322 | 0.333 |

## 3. What works
- Both: paint colours on target; layout, oculus rows, stepped arches and tower read right; sun front-right, shadows fall left.
- A: neighbour brick at plausible scale; wispy sky close to the photo.
- B: lower glass dark and warm like the reference.

## 4. Problems, ranked
**A**
1. Whole frame: nothing is aged. Pavement is one clean slab with diagonal stripes, the kerb is a ruled line, paint has no dirt or sill streaks. Fix: broken concrete slabs with 1–3 cm height jitter; AO/pointiness grime, 10–20% darker in crevices; streak masks under every sill and cornice.
2. Upper-left glass (x 220–470, y 300–470): large blurred gold blobs reflect an object the photo does not have. Upper glass p90 is 104, target 148: panes must mirror bright pale sky. Fix: remove the gold reflector; roughness 0.02–0.05; tilt each pane ±0.3° so panes break up.
3. Form: roof tanks are domed (reference: flat-topped cylinders); diamonds are small and dark (reference: bright chrome, a third of the oculus); left-wing oculi are rectangles, not circles.

**B**
1. Red paint carries a blotchy 40–100 px marble mottle, an obvious procedural-noise tell. Fix: noise at 5 cm or finer, value amplitude 4% or less.
2. Right neighbour: bricks about 2.5× too big; windows are black decals on a flat wall. Fix: 0.24 × 0.07 m bricks; recessed openings and slab bands like the unfinished frame in the photo.
3. Same as A's 1 and 3, plus a flat cloudless sky.

## 5. Research check
Sun direction, raised camera and lifted sky agree, and relief depth reads 0.1–0.3 m. Contradictions: the hand-painted orange pinlines inside the yellow tower rings are missing in both, and the upper curtain wall does not read as reflective glass in either.

## 6. What 8.5 needs
- A weathering pass: grime, streaks, broken pavement, debris.
- Upper glass mirroring bright sky (p90 135 or more).
- Flat-topped tanks, large chrome diamonds, tower pinlines, round left-wing oculi.
- Ground floor: faded hanging sign, gold relief lettering, a stepped kerb.

## Verdict
A is closer: its paint, sky and brick could pass at a glance as a photographed street, while B's mottled red and oversized brick give it away as CG at once. B wins only on lower-glass colour and a 0.01 IoU margin, which do not offset those tells.
