# Review v09

1. **Score:** 6.5 / 10

2. **Targets** (at 1000 scale; HU = helmet height ≈ 190 px)
- Span y 42–960: hit. x 192–786: left 20 px over at the pommel, near miss.
- Helmet dome ≈ 110, bottom ≈ 293: hit.
- Pad tops ≈ 308: hit.
- Belt 493–530, hem 667–687: hit.
- Boot tops ≈ 765–773: hit.
- Shield x 630–785, y 322–748: hit. The top-left corner is 20–30 px high.
- IoU 0.82: missed.
- Backdrop (255, 225, 178): red clipped, near miss.
- Shadow (116, 82, 38): about 10% dark, missed. Mid (185, 150, 89) and lit (243, 203, 129): hit.

3. **What works**
- Every landmark height hits. Stance, sword angle and shield read as the same pose.
- Good mixed triangles on the chest; clean planar belt, bracers and strap.
- The helmet has a T-opening, nose guard and dark slot.

4. **Problems, ranked**
1. **Legs too thin, skirt a lampshade** (lower centre). The thighs and calves are poles, about 55 px wide against 80. The hem is 1.5× the belt width, in 5 wide panels. Fix: add 30–45% to the thigh and calf radius. Cut the hem to 1.15–1.25× the belt, with 8–10 narrow pleats that hang near vertical. Make the boot shafts run from about 780 to 890, with a thick band cuff. Lengthen the right toe 30 px.
2. **Shoulder pads are puffed domes** (upper left). The left pad is a half-sphere 150 px tall that sticks out 30–35 px too far. The arm below is thin, with a gap to the torso. Fix: make the pad an angular plate 0.35–0.45 HU tall, with 8–12 faces. Move it 0.15 HU inward onto the deltoid. Thicken the arm about 20% so it fills x 243–330 at y 480–560.
3. **No trapezius** (y 280–310). At y 300 the render is 139 px wide; the reference is 259. The helmet sits on a flat shelf. Fix: raise the traps 15–20 px to meet the helmet rim, at least 240 px wide at y 300.

5. **Research check** — Agrees, except that the helmet reads as a flat-faced bucket, not a Corinthian dome. It has no cheek guards that angle to the jaw and no neck flare at the back (reference: 400, 235).

6. **What 8.5 needs**
- Thick legs, a narrow skirt with 8–10 pleats, taller boots.
- Flat angular pads, with a full arm and no hole under them.
- Traps up to the helmet rim.
- A rounder dome, cheek guards that taper to the jaw, and a neck flare.
- A leaf blade 35% broader and a crossguard 40% longer.
- 5% less exposure.
