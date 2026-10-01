# Review v07

1. **Score:** 5.9 / 10

2. **Targets**
- Red lit (220,52,63) hit. Cream lit (236,231,204) hit. Yellow lit (241,223,141) hit. Orange lit (232,133,90) hit.
- Cream shade (130,131,119) missed.
- Glass upper (88,105,121), p90 122: missed (too pale, too flat).
- Glass lower (25,21,12) hit.
- Sky top (148,175,210) hit. Sky low right (204,228,249) hit.
- Pavement (188,169,163) missed (too pink).
- Brick neighbour (104,58,35) missed (too orange).
- Layout mean IoU 0.338, the same as a flat trace. Cream share 0.15 against 0.23.

3. **What works**
- Lit paint colours and the sky are on target.
- The layout reads: clock tower, dotted arches, ladder piers, corner towers, shutters.

4. **Problems, ranked**
1. **Glass reflections (about 45% of the frame).** The lower panes reflect brick blocks at about 2.5x the scale of the neighbour's bricks, plus hard "mountain" triangles. The upper panes are a flat pale grey-blue. The reference panes are dark navy with streaky sky. Fix: reflect true-scale low-poly street geometry and a cloudy HDRI sky, not a brick image. Tilt each pane at random by 0.3–1.0°. Target glass-upper luma 60–70, with p90 140–155.
2. **Shallow relief, weak shadows.** Shade share is 0.19 against 0.30 for cream, and 0.01 against 0.03 for red. The bands hardly shadow the red wall. The stepped arch windows lack the cream reveal. Red shade (136,63,20) is brown, where the target is about (158,56,46). Fix: set mouldings 0.15–0.30 m proud, set the glass 0.2 m back behind painted reveals, and keep sun softness under 0.5°. Add blue sky fill so the shade stays red.
3. **Left corner, neighbours and ground read as a model.** The left pier has rectangles where the reference has four round oculi. There is a grey placeholder box, the curved orange corner is missing, and the sign is cut off. The right neighbour is a flat brick card. The pavement has no kerb or grime. The red paint has uniform noise mottle, with no streaks and no dirt at the base. Fix: model these parts as geometry, and add an AO-driven grime mask on sills and the plinth.

5. **Research check**
The sun direction agrees: the recesses shade on the upper-left. The soft, faint shadows contradict a hard sun about 35° high. The relief reads near 0.05 m, not 0.1–0.3 m. The glass reads light grey, not dark reflective curtain wall.

6. **What 8.5 needs**
- Real reflection geometry, an HDRI and per-pane tilt.
- True relief depth, reveals, and hard shadows with blue fill.
- A correct left corner and sign, and a modelled right neighbour.
- Chrome diamonds that reflect. They now read as black icons.
