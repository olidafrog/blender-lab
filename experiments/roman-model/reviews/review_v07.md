# Review v07

1. **Score:** 6.7 / 10

2. **Targets** (1000 scale; 1 head ≈ 190 px)
- Span y 47–933: missed (soles 21 high). x 197–801: missed (15 each side).
- Dome ≈ 125: missed. Helmet bottom ≈ 310: missed (20 low).
- Pad tops 318 / 328: hit.
- Belt 503–552: missed (low, 25 % too tall). Hem 672: hit.
- Boot tops 740–745: missed (35 high).
- Shield x 640–801, y 355–772: missed (edge 16 out, tip 22 low).
- Backdrop (249, 220, 174): hit; corners hot. Shadow (122, 87, 42), mid (185, 149, 89), lit (245, 205, 129): hit against the reference measured the same way.
- IoU 0.792: missed (v06 0.80).

3. **What works**
- Boots are clean prisms with a real cuff; the spikes are gone.
- Torso facets, belt and pleat plates match the reference's decimated-body, clean-armour split.
- Clay tone and contact shadow are on target.

4. **Problems, ranked**
1. **Neck and traps (y 270–330).** The helmet sits on a flat shelf. The left pad is a separate ball with a background notch at x 359–398, y 320. The right pad shows a dark open cavity. The target slopes the trapezius from 290 to the pads. Fix: raise the helmet 20 px. Add trapezius wedges from the neck (y 285–295) to the pad tops. Cap the right pad.
2. **Right leg and shield-side gap.** The right thigh sits 40–50 px right of the target at y 700; the shin 20 px. Skirt and forearm fuse; the target shows 15–45 px of background at x 580–625, y 480–690. Fix: right hip 0.2 head toward centre, knee in 20 px. Shield forearm out 25–30 px. Shield edge in 15 px, tip up 20. Soles down 20 px; cuffs to 775–785.
3. **Part shapes.** The crest is a jagged plank with 24 % less area than the target's clean crescent, whose rear edge sweeps to (410, 145). The face plate is solid, so the T reads as an eye slit. The sword fist is a geodesic ball; the crossguard is a third of the target's length. The right shin plugs into a flat-topped foot block. Fix: crescent crest 0.12–0.15 head thick, smooth top. Open both sides of the nose guard to the jaw. Box fist with a thumb; crossguard ~0.35 head. Taper the shaft into the foot.

5. **Research check**
Agrees on the faceting split. The helmet has dense small triangles; the target's has large planes. Ball pads and fist contradict "props are clean prisms".

6. **What 8.5 needs**
- Traps from neck to pads; helmet up 20 px; no notch or cavity.
- Right leg in 25–45 px; a shield-side gap.
- Cuffs 780, soles 954, belt 490–530.
- Crescent crest, full T-opening, box fist, longer crossguard.
