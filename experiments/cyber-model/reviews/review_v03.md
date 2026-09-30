# Review v03

## 1. Score: 6.0 / 10
Form and edges 5.5 · Part fidelity 6.5 · Materials 5.5 · Light and backdrop 6.0 · Technical 7.0

## 2. Yes/no list
1. Partly. Shield plate rim (750-1290, 340-760) has a soft shoulder. Feet show grey shade, no black crease.
2. Yes, faint. An inset line follows the lid and the S step.
3. No. Shield wall about 125, plate top about 131 (my patch estimate). Chassis walls are darker.
4. No.
5. No.
6. No. The black block above the LCD (680-730, 215-280) reads as a stub, but it touches the chassis.
7. No. No scratches, only fine grain.
8. Gradient yes, reflection no.
9. No. Only the exposed chassis is black. Gaps between plates are grey.
10. Yes. Grain is visible and close in size.

## 3. Targets
Hit: backdrop TL, TR, BL (edge, 12), BR; p5; p95; LCD; grain. Missed: subject share (27 vs 36), subject median (-16). Subject <12 % passes the rule (3.4 points) but holds only 55 % of the reference's black area; I count it missed.

## 4. What works
- All major parts are present and attached.
- LCD, steel and rubber read correctly.
- Backdrop light and grain match.

## 5. Problems, ranked
1. **Feet and gaps, every plate.** Gaps are grey. One large round bevel makes plates look like pillows. Fix: a two-segment top chamfer (0.3-0.5 mm, 4-6 px at 1600) over a vertical wall. Feed an Ambient Occlusion node (distance 1-2x step height) through a Color Ramp into the polymer colour, so feet fall to about 0.01.
2. **Polymer tone and wear, shield and lower-left plates.** They are flat matte grey, about 130-155 against 70-85 in the reference (my estimate). The black chassis drags the table median down, so the render is two-tone. Fix: base colour sRGB 65-80, roughness 0.35-0.45 with noise of plus or minus 0.1. Add scratches: a Noise Texture stretched 1:40, hard-cut by a Color Ramp, masked by low-frequency noise so strokes cluster on the lid.
3. **Empty plates, lower-left (640-1050, 640-800) and slab (830-1280, 760-1130).** Blank faces and low walls give the low subject share. The V line reads as a sticker. Fix: raise walls 1.5x. Add 4 screws, a 5-slot vent (1 mm boolean) and a groove parallel to each outline. Cut the V line 0.4 mm deep.

## 6. Research check
Two claims fail. Gaps are grey, not nearly black. Camera-facing walls are equal to or darker than the tops. The rest agrees.

## 7. What 8.5 needs
- Black creases at every foot.
- Dark satin polymer, clustered scratches.
- Taller walls, chamfer not round bevel.
- Detail on blank plates.

Blind pairwise: Y (v03) is closer. Its plates separate from the chassis through lit rims and visible walls, and the silver slab replaces v02's confusing black bar. Its plates are about 50 levels too light (my estimate), so it wins on structure and loses on tone.
