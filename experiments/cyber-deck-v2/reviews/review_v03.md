# Review v03

1. **Score:** 5.2 / 10

2. **Targets**
- Backdrop TL 108 vs 96: hit (edge). TR 137 vs 142: hit. BL 107 vs 111: hit. BR 111 vs 117: hit.
- Subject share 38 vs 36: hit. Median 65 vs 75: hit. p95 86 vs 92: hit.
- Subject p5 23 vs 7: **missed** (worse than v01's 21). Subject <12 % 1.8 vs 7.6 (ratio 0.24): **missed** (worse than v01's 2.4).
- LCD (141,202,210) vs (140,204,212): hit. Backdrop grain 13.1 vs 15.4 (0.85): hit.
- By eye: tops 64–73, a little under 70–85. S-step slope 99 at its middle, 138 at its left end: over the range.

3. **What works**
- The S-step now has a camera-facing slope that reads lighter than the tops, as in the reference.
- The LCD sits in a raised dark frame (about 20) with a pocket wall. It is closer to the shield.
- The LED no longer lights its neighbours. The backdrop grain is fine sand, not worms.

4. **Problems, ranked**
1. **No blacks anywhere (all joins).** The gaps between the battery, the upper shell and the lower-right block read 70–86. The reference has a black outline round every part and a deep channel under the S-step. The 1.2 mm gap over a liner does not work: the liner is lit from above. Fix: groove depth at least 3× its width (4 mm deep). Liner albedo 0.02, roughness 1, specular 0, and unlink it from the key. Give each upper shell a 1–2 mm overhang lip so its shadow falls into the join. Cut the channel under the S-step (about 3 mm wide). Target p5 ≤ 12 and <12 % ≥ 5.3.
2. **S-step is faceted, not swept (centre, x≈990–1200, y≈600–690).** The slope is flat bands that meet in hard mitre creases at each bend. The reference slope turns every corner with one constant radius. The top fillet at 1.2 mm gives no highlight line; the research asks 3–5 mm. Fix: sweep the section along a plan curve with 6–10 mm plan corner radii (curve bevel with a profile, or GN Curve to Mesh). Do not loft planar bands. Make the step taller (5–6 mm) so a 2.5–3 mm fillet does not eat the slope. Keep the slope at 90–105.
3. **Left side and pods unchanged since v01.** The dial is still face-up on a bright chrome triangle. The pods are still fat cans on a floating block. The chrome battery rim and the chrome cylinder at lower right have no match. Fix: rebuild the gunmetal side frame and upright gear from `ref_front.jpg`. Make the pods longer barrels built into the top shell. Steel base 0.35–0.5, roughness 0.3–0.4; bright chrome on screw heads only.

5. **Research check** — Contradicts "constant-radius fillets, 3–5 mm on shells" (mitred facets, 1.2 mm). Contradicts "tight crease at the foot" (no dark crease). Contradicts "wear as light speckle on edges only" (chalky 15–20 px band on the lower-right walls). Contradicts "sparse straight scratches" (curly hairs on the DT-03 plate). No bead-blast speckle on the tops. Light direction and lighter slopes agree.

6. **What 8.5 needs**
- Real black joins: deep grooves, lips, the S-step channel.
- Swept steps with round plan corners and 3–5 mm top fillets. A thick LCD shield with 45–60° walls.
- Rebuilt dial frame and pods; gunmetal instead of chrome.
- Crest-only speckle wear, straight scratches, bead-blast bump on the polymer.
