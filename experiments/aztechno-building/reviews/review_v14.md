# Review v14

**Score:** 6.3 / 10

## Targets

- Hit: red lit (223, 62, 74), cream lit (238, 238, 214), cream shade (111, 113, 99), yellow lit (242, 229, 150), orange lit (234, 136, 95), glass lower (39, 28, 18), sky top (149, 175, 210), sky low right (203, 228, 249), glass upper p90 luma 147.
- Glass upper (69, 81, 105): **missed** (blue +23)
- Pavement (188, 171, 167): **missed** (too bright and pink)
- Brick neighbour (58, 50, 55): **missed** (shade is grey-violet)
- Layout IoU mean: 0.332 (flat-trace level)

## What works

- The lit paint colours and the sky are on target.
- The central layout reads correctly: arches, oculi rows, pilasters and the octagon tower.

## Problems, ranked

1. **The left corner (x 20–200) looks like a block model.** The oblique curtain wall is flat grey with no reflection. The far-left column has square windows, not oval oculi. A cream box hides the sign. Fix: model the corner from the oblique references. The stepped pilaster runs to the ground, the glass is angled so it reflects, the oculi are oval and the sign is legible. Add a wall and a car to the left street.
2. **The glass reads as CG.** The lower panes show a checker of random tints (crop 640_560). The frames are black, not gold, and the upper glass is too blue. Fix: limit per-pane variation to ±3 % value and <0.3° tilt. Make the mullions gold metal (roughness 0.3–0.4). Set the upper glass to about (60, 67, 82).
3. **The relief is too shallow and every surface is too clean.** Cream shade share is 0.16 (reference 0.30). Make proud elements 0.15–0.3 m and keep the sun azimuth at 45° ±5°. The diamonds are dull grey and cast black arrow shadows; they must be chrome (metallic 1, roughness <0.1). The oculi rings are smooth tori, but the reference has flat stepped bands. The street is a uniform knurled strip, and the pavement has no cracks, patches or cast shadow.

## Research check

- The sun direction agrees: shadows fall left and down.
- The shadow shares show reliefs shallower than 0.1–0.3 m.
- The image contradicts "thin gold-coloured frames": the frames are black.
- The left return contradicts "dark reflective curtain wall".

## What 8.5 needs

- Rebuild the left corner and give the left street some context.
- Gold frames, continuous reflections and darker upper glass.
- Deeper mouldings (cream shade share 0.25–0.30).
- Chrome diamonds and flat stepped rings.
- A weathered warm pavement, a cast shadow at the bottom right and warm brick shade.
- Dirt at the sills and plinth.
