# Review v08

1. **Score:** 6.8 / 10

2. **Targets** (1000 scale; 1 head ≈ 190 px)
- Span y 50–950: hit. x 187–809: missed (25 out each side).
- Dome ≈ 130: missed (30 low). Helmet bottom ≈ 315: missed (25 low).
- Pad tops 340 / 350: missed (20–30 low).
- Belt ≈ 513–550: missed (20 low).
- Hem ≈ 700: hit. Boot tops ≈ 768: hit.
- Shield x 640–809, y 362–778: missed (top 20–40 low, tip 28 low, edge 24 out).
- Backdrop (250, 220, 174); shadow (118, 83, 38), mid (183, 148, 88), lit (246, 205, 130): hit.
- IoU 0.797: missed (v07 0.792).

3. **What works**
- Traps now slope from neck to pads; the shelf is gone.
- Sword reads right: box fist, longer guard, tip at (547, 797) against (530, 795).
- Boots, belt and pleats are clean planar armour.

4. **Problems, ranked**
1. **Upper body low and narrow (y 60–560).** At y 320 the render spans x 424–564; the target spans 327–616. Helmet, pads and belt are 20–30 px low. The sword upper arm sits 30–60 px inside the target at y 480–540. Fix: raise helmet, pads and shoulder line 0.12–0.15 head. Widen pad tops 0.25 head each side. Swing the sword upper arm out 0.2 head, bracer edge to x ≈ 245.
2. **Shield side still one blob (x 580–700, y 480–700).** Flagged for the second round. The target shows 15–45 px of background between skirt and shield forearm; the render shows none. A jagged arrow-shaped shard pokes out of the shield face (full frame 1090–1140, 660–790). Fix: shield forearm and shield out 0.15–0.2 head; right hip in 0.15 head; shield up 25 px, edge in 20 px. Delete the shard (likely arm or strap geometry).
3. **Part shapes.** The left pad is a lumpy puff of fine triangles with saw-tooth notches on its outline; it reads as a balloon sleeve. The helmet is a flat-fronted bucket; the target's dome is rounder, with a brow and a neck flap at (400, 240). The right thigh ends in an upward spike at the hem (full frame 870, 940). Fix: pads from 8–12 large facets with a smooth outline. Dome 10–15 % rounder plus the neck flap. Cap the thigh below the skirt.

5. **Research check**
The faceting split holds on torso and armour. The left pad and helmet use small dense triangles where the target uses large planes. The rest agrees.

6. **What 8.5 needs**
- Helmet, pads and belt up 20–30 px; pad tops 0.25 head wider.
- Sword arm out to x ≈ 245.
- A skirt–shield gap; shield up 25 px, edge in 20 px, shard gone.
- Large-facet pads, rounder dome with neck flap, no thigh spike.
