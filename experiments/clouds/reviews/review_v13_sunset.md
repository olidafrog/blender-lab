# Review — v13_sunset (target: 03_lone_sunset_cumulus)

1. **Score:** 6.7 / 10

2. **Targets**
- Lit peak ~225,200,170: brightest 1% of the cloud is 213,166,144 and the single brightest pixel is 231,179,151. The mean of the lit lobe is 193,151,133. **Missed.** Brightness is close, but the light is too orange: green is 30–35 low and blue is 25 low.
- Shadow side ~95,78,86: the left lobe measures 72,78,96. **Missed on hue.** Luminance is about right (78 vs ~83), but the shadow is cold slate-blue, not warm mauve. Red is 23 low.
- Sky top ~41,88,120: measures 39,74,105. **Near hit.** It is about 14 too dark in green and blue.
- Edge falloff (for reference): the right edge fades over ~10 px at 1400 wide, which is ~5 px per 700 px. The top edge is 1–2 px. Acceptable.

3. **What works**
- The sky gradient (teal-blue top, dusty mauve bottom) matches ref 03 closely. It is clean and has no banding.
- The dark, flat base (L≈58 against sky ≈75) reads as a cool underside. The wispy left and lower-left fringe is like the reference.
- Render quality is clean: no fireflies, no voxel steps, and no grid pattern in the centre crop.

4. **Problems, ranked**
1. **Left lobe (x 460–740) is completely unlit.** Its top is cyan-blue (62,82,107), and only the right lobe gets sun. In ref 03, warm light catches every top, and the shadow falls on the lower-left flank only. Fix: raise the sun elevation from grazing to ~8–15° so it clears the right lobe. Or rotate its azimuth ~20–30° toward the camera. Also add a warm fill from the sky's horizon colour, so the tops in shadow go mauve and not blue.
2. **The lit colour is saturated orange and has little contrast.** The right lobe is a flat peach-grey (137 at its top, 159 at its right side). The brightest light is on the right flank (x≈914), not on the crown. The ref's lit crown is a paler cream (G/R ≈ 0.89; here ≈ 0.78). Fix: desaturate the sun colour toward ~1.0,0.85,0.68 linear. Move the brightest light to the crown. Raise sun strength ~20–30% so the peak reaches L≈200.
3. **The billow texture is fine and uniform, like cotton wool.** The centre crop shows the same small grain everywhere. The mid-scale lobes that separate light from shadow are weak. Ref 03 has 3–5 large rounded lobes with small detail only at the rims. Fix: shift octave weight toward the large scales (lower the high-frequency displacement amplitude ~40–50%). Mask the fine octave to the surface band only, not the whole density.

5. **Research check**
- The dark base agrees with "base darker than top".
- The cold-blue shadow contradicts "shadows take the sky's colour" as ref 03 shows it. The sky near the cloud is mauve (60,74,98 → 79,71,79), so the shadow should lean mauve. The blue comes from the zenith only.
- There is no visible silver lining on the sun-side edge. The right edge shows no brighter rim.

6. **What 8.5 needs**
- Light both crowns: raise the sun's elevation, or move it toward the camera.
- Make the lit crown cream (~225,200,170) and put the peak on top.
- Make the shadows warm mauve (~95,78,86): add a horizon-coloured fill, or weight the ambient term toward the lower sky.
- Use larger lobes and confine the fine grain to the rims.
