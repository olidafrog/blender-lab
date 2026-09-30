# Review v06

1. **Score:** 6.6 / 10

2. **Targets** (1000 scale; 1 head ≈ 190 px)
- Span y 47–933 vs 42–954: missed (soles ~12 px short). x 197–796: missed by 11–15.
- Dome ≈ 123: missed. Helmet bottom 292–310: hit.
- Pad tops: left 312 hit, right 335 missed.
- Belt 499–549: missed (low, 25 % too tall). Hem 663–690: hit.
- Boot tops 710–725: missed (fourth round).
- Shield x 623–796: hit. y 337–730: missed (tip 20 high).
- Backdrop (255,225,178): missed. Shadow (109,74,32): hit against the reference measured the same way. Mid (182,147,87): hit. Lit (248,207,131): missed.
- IoU 0.80: missed (v05 0.763).

3. **What works**
- Sword-arm window closed; pommel, fist and blade tip on target.
- Strong chest V, belt and pleat plates; body facet size matches.
- The helmet T-opening and dark face read at once.

4. **Problems, ranked**
1. **Legs and boots.** Cuffs at 710–725 leave ~40 px of thigh vs 100. Shafts at y 850 are 95 and 127 px wide vs 65 and 71. The right leg bulges to x 691 at y 750 vs 636. Star spikes remain on both shafts. Fix: cuffs to 775–785. Shafts 65–75 px wide, 6–8-sided prisms, no jitter. Right leg in 25–35 px. Legs ~12 px longer.
2. **Shoulders and shield arm.** The target traps run from the helmet (290) to the pads (320); the render dips at x 340–450, y 270–330. The shield fist is 40–60 px high, with no forearm or bracer strap. A C-shaped hoop over the right pad reads as stray. The belt reaches x 617 vs 580, so the torso fills the target gap at x 580–627, y 480–680. Fix: trapezius mass to put the neck-to-pad line at 285–300. Waist 30–35 px narrower on the shield side. Fist centre to (680, 605) ± 10, with a bracer and strap. Remove the hoop.
3. **Part shapes.** The crest is a flat plank; the target is a crescent whose rear edge curves down to (410, 145). The helmet is 181 px wide at y 250 vs 143: a bucket. Pads are near-spheres; the sword fist is a geodesic ball. Fix: crescent crest 0.12–0.15 head thick. Taper the cheek guards 18–20 px per side below y 220. Pads 6–8 segments around, flatter top. A bevelled box fist with a thumb. Crossguard ~40 % longer.

5. **Research check**
Partly. The lumpy strap contradicts "props are clean prisms". Pads and fist are spheres; the reference is angular.

6. **What 8.5 needs**
- Cuffs at 780, slim prism boots, right leg in.
- High traps, a waist-to-shield-arm gap, a lower fist with a bracer.
- Crescent crest, tapered cheek guards, dome at 100.
- A clean 35 px strap, a box fist, angular pads.
- Belt at 490–530; backdrop and lit tone to target.
