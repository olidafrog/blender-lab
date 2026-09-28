# Review v05

1. **Score:** 6.8 / 10

2. **Targets** — none set.

3. **What works**
- The body palette matches the reference: near-black top, deep blue, cyan, lavender, pink. The hourglass dot is the best part of the frame.
- The mark is correct and legible: two stepped bars and the pinched dot, in the right orientation.
- The grain is fine and even, and the background is solid, not transparent.

4. **Problems, ranked**

1. **The crescent is a fat cream tube on every up-facing edge.** It sits on all three top caps and on both step shelves (centre of frame, y≈720–830). The shelves are the brightest things in the frame, so the eye goes to the steps and the mark reads as neon "4 4". The reference crescent is one thin arc, tapered at both ends, lifted off the body with a dark gap. Fix: build the mask as (alpha shifted up 0.5–0.8% of frame height) minus (alpha dilated 2–3 px). Blur it 2–4 px. Multiply by a per-shape "top cap" mask so the shelves get 0–30% strength. Aim for about one third of the current band width, peach-white, not yellow.

2. **The halo is uniform, and the bottoms have no hot orange-red.** In the reference the strongest warm energy is a saturated orange-red band along the bottom rim, and the glow below is 2–3× the glow above. Here every bottom ends in pale pink with a 2 px orange line, and the halo has the same strength all round. It also fills the gaps between the bars with muddy brown, so the negative space closes up. Fix: add a bottom rim in the shader (fresnel × clamp(−normal_y), mixed to about #FF5A1E). Feed the halo from that rim plus the silhouette, weighted by a vertical ramp. Cut the halo radius until the centre of each gap is at 30% of the halo peak or less.

3. **Edges are hard vector cut-outs, and the spectral rim is a 2–3 px teal hairline.** In the reference the edge is soft, and the rim is a wide blue→cyan→yellow→orange band, about 5% of the diameter. Fix: widen the bevel so the fresnel covers 4–8% of the bar width. Blur a copy of the rim 3–6 px before dispersion, and raise dispersion to 0.02–0.04. Soften the body edge by 1–2 px.

5. **Research check** — Mostly it agrees. Two claims don't hold. The halo is not asymmetric like the reference. The "crescent above the silhouette" is applied to every top edge, including the inner shelves. The body gradient also doesn't change across the bar width, so the forms read as flat panels, not rounded shapes. The per-shape normal shading is not visible.

6. **What 8.5 needs**
- A thin, tapered crescent on the top caps only, with a dark gap to the body.
- An orange-red bottom rim, with the halo weighted toward the bottom and clean gaps between the bars.
- A wider, softer spectral rim, so the edges stop looking cut out.
