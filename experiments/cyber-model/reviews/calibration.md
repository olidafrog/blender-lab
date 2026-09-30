# Calibration review: v09 (A) and v10 (B)

## Render A (v09)

**Score: 6.7 / 10.** Form and edges 6.5, part fidelity 7.0, materials 6.5, light/colour/backdrop 6.5, technical 7.0.

Top problem: the blacks are lifted (subject p5 19 vs 7, share under 12 is 2.2 % vs 7.6 %), so creases and gaps read as dark grey, not black, and the layering looks flatter than the reference. Fix: give recessed floors a near-black liner material (base colour about 0.005) and multiply a short-range AO (distance about 0.02–0.04 of the part size) into the diffuse.

## Render B (v10)

**Score: 6.5 / 10.** Form and edges 6.0, part fidelity 7.5, materials 6.0, light/colour/backdrop 6.0, technical 7.5.

Top problem: the base shell and camera-facing walls are crushed to near-black (my estimate: right wall about 40 vs about 65–70 on the top plates; A is about 61), so the plinth loses its chamfer and layer read and the walls end up darker than the tops. Fix: lift the wall material to a satin grey (higher base value, roughness about 0.35–0.5) so the upper-right key catches it, and keep true black only inside creases.

## Yes/no list (A | B)

| # | Question | A | B |
|---|---|---|---|
| 1 | Rim shoulder vs dark foot crease | Yes (shield plate, lid) | Yes |
| 2 | Grooves parallel to step outlines | Yes, but only lid and shield channel | Same |
| 3 | Camera-facing walls lighter than tops | Yes (left block, bottom wall); right wall about equal | No: right and bottom walls darker than tops |
| 4 | Smears or dark blotches on flat faces | No | No |
| 5 | Faceted cylinders | No | No |
| 6 | Floating or visibly intersecting parts | Yes: dark disc overlaps last vent slot (835, 795) | Yes: screw ring overlaps last slot (830, 770) |
| 7 | Scratches as short strokes | Yes (lid, right plate) | Yes |
| 8 | LCD shows reflection or gradient | Yes (diagonal glare band) | Yes |
| 9 | Blacks really black | No (p5 19) | No (walls dark, creases still lifted; p5 18) |
| 10 | Backdrop grain visible and similar | Yes, slightly soft (std 13.1 vs 15.4) | Yes (13.3) |

**Closer to the reference:** A. The reference walls are satin and lighter than the tops, and A keeps that, while B turns the base into a black slab that hides the layering. B's slotted pocket and metal screw are better than A's empty frame and dark blob, but that does not outweigh the form loss.
