# Review v04

## 1. Score
**5.9 / 10.** Form and edges 5.5 (x0.30). Part fidelity 6.0 (x0.20). Materials 5.5 (x0.20). Light, colour, backdrop 6.5 (x0.15). Technical quality 6.5 (x0.15).

## 2. Yes/no list
1. Partly. The lid has a soft light shoulder on its top-right rim (~1150-1280, 440-520) and a dark crease at its left foot (~760, 560). The base slab and lower plates have one flat edge treatment.
2. Yes. The lid pocket, LCD bezel and INSERT pad have grooves parallel to their outlines. The base slab has none.
3. No. Front walls of the base (bottom edge, ~850-1400, 1080-1170) read near black. They are darker than the plate tops (my estimate).
4. No smears or blotches.
5. No. Antenna, drums, jack, coil and gear teeth are smooth.
6. Yes. The jack (830-920, 125-195) and the grey block beside the LCD (680-740, 205-285) hang over the slab edge onto the backdrop. Neither has a contact shadow.
7. Yes. Scratches are thin short strokes on the lid and plates. They are sparse and uniform, not clustered.
8. Mostly flat. The LCD has a mild cyan gradient and no crisp reflection. The reference is similar.
9. No. Creases are dark grey, not black (p5 22 vs 7).
10. Yes, but coarser. Amplitude is close. Clumps are about 2x the reference size (my estimate).

## 3. Targets
- Backdrop TL 99 vs 96: hit. TR 139 vs 142: hit. BL 99 vs 111: hit (edge, -12). BR 109 vs 117: hit.
- Subject share 36 vs 36: hit.
- Subject median 63 vs 75: hit (edge, -12).
- Subject p5 22 vs 7: missed (+15).
- Subject p95 84 vs 92: hit.
- Subject <12 3.1 vs 7.6: missed.
- LCD (130,188,196) vs (140,204,212): missed (G and B are -16).
- Grain std 13.6 vs 15.4: hit.

## 4. What works
- Plate tone matches the reference. Lid and plates sit near 80 luminance, and the backdrop gradient is right.
- The lid reads as a real stepped part: raised rim, soft shoulder, inset pocket, parallel groove, hairline scratches.
- All secondary parts are present and readable: twin cylinders with silver collars, dial and gear, knob, red LED glow, coil, LCD.

## 5. Problems, ranked
1. **Body reads as thin plates on a black tray, not chamfered solids.** Where: the base slab (top right ~1000-1300, 200-330; right ~1300-1560, 640-800) and its front walls. The slab is flat black with no shoulder, no crease and low steps. Fix: add a Bevel modifier to the slab and lower block, width about 1/4 to 1/3 of the step height, 2-3 segments, normals hardened at 30 degrees. Lift the slab albedo from near 0.01 to about 0.03-0.04 (roughness 0.4-0.5) so the top faces catch the key. Get the black from AO on base colour, distance about one step height. Raise the lid wall to about 2x its height.
2. **Hovering and stubby parts.** Where: the jack, the block beside the LCD, the twin drums (470-640, 200-390). Fix: move the jack and block inboard so at least 60 % of the footprint sits on the slab, and add a boot or bracket at each. Stretch the drums along the antenna axis by 1.5-2x. Their end caps show a cyan cast. Set the LCD emission strength to 0 for glossy rays (Light Path, Is Glossy Ray) or set cap roughness to 0.5 or higher.
3. **Flat materials and weak blacks.** Where: the lid and plates (std 1.5 on the lid vs 13-26 in the reference). Fix: multiply roughness by a Noise texture (scale 2-3, range 0.35-0.6). Add an edge-wear mask from a Bevel node that lifts value by 10-15 % on rims. Darken the creases with the AO above so p5 moves from 22 toward 8.

## 6. Research check
The image agrees on stepped solids, parallel grooves, the soft top shoulder on the lid, and the tiny scratches. It contradicts these claims:
- "Camera-facing walls lighter than tops": the walls here are darker.
- "Real blacks in the creases": creases are dark grey.
- "Soft short shadows": the antenna shadow is long and fairly hard.
- "Foot of each step is a black crease": only the lid has one.

## 7. What 8.5 needs
- Bevelled, lifted slab and lower block with black creases (problem 1).
- Grounded jack and block, longer drums, no cyan cast (problem 2).
- Mottled satin plates and rim wear; denser scratch clusters near the lid and right plate (problem 3).
- Lighter camera-facing walls: add a low fill from the lower left.
- LCD +16 in G and B. Backdrop grain about half its current size.
- Shorter shadows: raise the key elevation.

**Blind pairwise:** X (v04) is closer. Its plates match the reference's dark satin grey (about 80 vs v03's washed 150) and its shadows and creases are deeper, but v03 is closer on LCD brightness.
