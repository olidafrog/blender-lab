# Review v04

1. **Score:** 6.3 / 10

2. **Targets** (1000 scale)
- Span y 76–935 vs 42–954: missed. x 204–787: hit.
- Helmet dome 133 vs 100, bottom 325 vs 290: missed (head ~35 low, worse than v03).
- Pad tops 297/308 vs 320: missed.
- Belt 500–533: hit. Hem 667: hit.
- Boot tops 730–750 vs 780: missed.
- Shield y 351–720: top hit, tip ~30 short: missed.
- Backdrop (255,225,178): missed, hot. Shadow (121,86,40): hit. Mid (185,149,89): hit. Lit (247,206,132): borderline.
- IoU 0.75: missed, no gain over v03.

3. **What works**
- Belt and skirt are clean planar bands and pleats.
- Sword fist, blade angle and tip land on the target.
- The T-opening and nose guard read at once. Key and contact shadow match.

4. **Problems, ranked**
1. **Head sunk into the shoulders (fourth round).** The figure reads hunched and neckless. The crest is still a forward-leaning wedge with no back sweep (red x 410–480, y 42–160). Fix: raise the helmet ~0.2 head (~35 px). Lower the pads ~20 px and pull each in ~8 %. Rebuild the crest as a crescent: peak (540,42), top edge back to (440,70), rear edge down to the rim at (410,145).
2. **Arms (third round).** A gap still opens between sword arm and waist (~70 px per row, y 440–560). Upper arms are too thick (~88 vs ~75 px). The shield fist sits ~80 px high (y 527 vs 610). Fix: widen the lats 15–20 % at y 400–500. Thin the upper arms 10–15 %. Bend the sword elbow ~15° in. Drop the shield fist to (680,610) and remove its buckle.
3. **Legs and boots.** Boots take ~60 % of leg height, so the thighs look stubby. The right leg sits ~30 px too far right; its toe reaches 717 vs 672. The shins show serrated star triangles, not planar faces. No sole. Fix: cuffs to y 780. Rotate the right leg in 5–7°. Make each shaft a clean 6–8-sided prism with no decimate. Add a sole 0.08–0.1 head thick, soles at y 945–955.

5. **Research check**
Partly agrees. Research says armour is clean and planar; the serrated, decimated boots contradict it. The reference pads are rounded faceted domes; the render has a lumpy slab-topped cap (left) and a curled shell (right). The helmet dome still shows regular rings, not irregular triangles.

6. **What 8.5 needs**
- Helmet up ~35 px, pads down ~20 px.
- A crescent crest that sweeps back.
- Lats that close the arm gap, thinner upper arms, shield fist at y 610.
- Prism boots with soles, cuffs at y 780, right leg in.
- Rounded dome pads, an irregular dome, shield tip at y 750.
- Backdrop down to (247,220,174).
