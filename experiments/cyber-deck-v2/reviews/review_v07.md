# Review v07

1. **Score:** 6.2 / 10

2. **Targets**
- Backdrop TL 109/96: **missed** (+13). TR 139/142, BL 110/111, BR 114/117: hit.
- Share 37/36, median 73/75, p5 12/7, p95 89/92: hit. p5 hit for the first time.
- <12 % 4.7/7.6 (0.62): **missed**, but up from 2.7.
- LCD: hit. Grain 13.3/15.4 (0.86): hit.
- By eye: tops 71–86, hit. Slopes 86–87, the same as the tops: **missed** (target 90–105).

3. **What works**
- The S-step now reads as a moulded sloped face with a rounded top and a dark crease at the foot. It is the first shell that looks like CAD, not stacked plates.
- The gear has fine, dark teeth. Screws are grey domes in dimples. Scratches are sparse and straight.
- The door, the thumb wheels and the coil cord sit correctly and are grounded.

4. **Problems, ranked**
1. **The metal parts have the wrong shape and finish.** The left dial plate (x 400–600, y 470–700) is still a bright chrome teardrop pointing at the LCD corner. This is the third round. The reference is a broad gunmetal arm. It runs from under the pods down the left wall, wraps the dial, and ends at a screw beside ON/OFF. The battery trim (x 820–1290, y 850–1130) is a thin mirror strip. The reference has a thick faceted gunmetal frame, 8–10 mm wide, with cut-outs. The corner cylinder (x 1410–1560, y 680–800) is also too bright. Fix: build the arm and the frame as new plan curves traced from `ref_front.jpg` and `ref_dt03_4k.jpg`, and loft them. Do not edit the teardrop again. Metal: albedo 0.10–0.15, roughness 0.45–0.55, crest-only wear. Render value 90–130, not 180+.
2. **The pods are about 1.5× too big and cover the LCD.** Cap diameter is about 46 px at 736 wide; the reference is about 30 px. The left pod hides the LCD's top-left corner ("NT SOURCE"). In the reference the whole LCD bezel is clear. Fix: pod diameter 10–11 mm, length about 16 mm. Move the pods back behind the bezel's top edge. Remove the black cap on the LCD corner (x 505–530, y 445–475).
3. **The polymer looks like clay, not satin.** The bump is low-frequency orange peel (lumps 5–10 px) and reads as hammertone. The surface is mostly diffuse, so slopes shade like tops. Fix: move the speckle to albedo and roughness noise at 0.2–0.4 mm scale, with bump strength ≤ 0.03. Set roughness 0.35–0.45 and specular 0.5 so camera-facing slopes pick up the key at 90–105. Darken the gap liners to reach <12 % ≥ 5.3.

5. **Research check** — The fillets, the sloped S-step, the crease at the step foot, the domed screws and the straight scratches all agree. The render contradicts two findings. The grain is not a fine bead-blast speckle, and the sloped faces are not lighter than the tops. The upper-right key agrees, but the backdrop's TL is 13 levels too bright.

6. **What 8.5 needs**
- A traced gunmetal left arm and battery frame; no chrome anywhere.
- Pods at 10–11 mm diameter, behind the LCD.
- Fine speckle in albedo and roughness, a satin spec, and slopes at 90–105.
- <12 % ≥ 5.3, backdrop TL ≤ 108.
