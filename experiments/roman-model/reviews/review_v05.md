# Review v05

1. **Score:** 6.4 / 10

2. **Targets** (1000 scale; 1 head ≈ 190 px)
- Span y 52–937 vs 42–954: missed. x 204–787: hit.
- Dome ≈ 120 vs 100: missed. Helmet bottom 287–307: hit (was 325).
- Pad tops 313/323: hit. Belt 500–527: hit. Hem 670–685: hit.
- Boot tops 720–740 vs 780: missed, worse than v04.
- Shield x 625–787: hit. y 353–705 vs 340–750: missed.
- Backdrop (255,226,179): missed. Shadow (121,86,40): hit. Mid (185,150,90): hit. Lit (248,207,131): missed.
- IoU 0.763: missed (v04 0.75).

3. **What works**
- The helmet now sits right. T-opening, nose guard and cheek guards read at once.
- Belt, pleats, cuffs, sword and shield are clean planar solids. Sword fist, pommel and blade tip land on the target.
- The chest has a strong V with faceted pecs.

4. **Problems, ranked**
1. **Window between sword arm and body (fifth round).** Backdrop shows at x 330–424, y 440–600, 60–71 px wide. The target is solid there. The belt spans x 413–593 vs 385–580. Fix: adduct the sword upper arm ~10° so the forearm moves in ~35 px. Widen the left flank ~30 px (0.15 head) at y 440–560. Shift the waist ~15 px left. Open a 15–20 px gap between torso and shield arm at y 480–560.
2. **Crest.** A flat plank with a stepped top and vertical back edge (x 427–544, y 52–147). It reads as a fin. Fix: a crescent 0.12–0.15 head thick, peak (540, 42), top edge back to (440, 70), rear edge curving down to the rim at (410, 145).
3. **Legs and boots (third round).** Cuffs at 720–740 leave ~50 px of thigh. Feet are 40–50 % too wide (left 276–391 vs 297–372 at y 900). Right toe at 717 vs 672. Shafts still show serrated star triangles. Fix: cuffs to 775–785, shafts ~0.25 head shorter, each a 6–8-sided prism with no decimate. Narrow the feet ~30 %. Rotate the right leg in 5–7°. Soles at 948–955.

5. **Research check**
Partly agrees. Boots and chest strap contradict "props are clean boxes": both are decimated like skin, and the strap is ~20 px wide vs ~35. The helmet is a vertical-sided bucket, not a rounded dome.

6. **What 8.5 needs**
- Close the sword-arm window.
- A crescent crest. A rounder dome, top at y 100.
- Prism boots, cuffs at 780, narrower feet, right leg in.
- Shield top tilted ~8° toward the body, tip at (725, 750). Shield fist ~55 px lower, at (680, 610).
- A clean 35 px strap.
- Backdrop to (247,220,174), lit tone to (234,198,128).
