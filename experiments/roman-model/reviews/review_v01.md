# Review v01 — roman-model

1. **Score:** 5.3 / 10

2. **Targets** (1000-scale)
- Span y 89–941 vs 42–954: missed (crest). x 279–775 vs 212–785: missed (sword side).
- Helmet dome ≈ 177 vs 100: missed. Helmet bottom ≈ 300: hit.
- Shoulder-pad tops ≈ 320: hit.
- Belt 463–503 vs 490–530: missed.
- Skirt hem ≈ 640 vs 650–700: missed.
- Boot tops ≈ 710 vs 780: missed.
- Shield x 667–775, y 383–743: missed (narrow, top low).
- Backdrop (255,242,189), lower-left clips to (255,255,205): missed. Shadow (108,78,37): missed, dark. Mid (180,147,90), lit (237,200,134): hit.
- IoU 0.72: missed.

3. **What works**
- Body faceting: irregular mixed triangles; armour reads as clean prisms.
- Stance width, sword angle (~35°) and the bulky V-torso.
- Key direction and mid/lit clay tones.

4. **Problems, ranked**
1. **Helmet and crest.** It reads as a medieval bucket helm: a slot visor, no T-opening, no nose guard, no cheek guards. It is too small, pitched back ~15°, and the crest is a thick hood wrapped round the back. Fix: scale the helmet 1.45–1.55× (dome at y 95–110). Cut a T-opening with a nose bar and run cheek guards to the jaw. Pitch it forward 15°. Replace the crest with a fin ~0.15 head thick that rises from the back rim to a peak over the brow at y ≈ 42.
2. **Leg and torso lengths.** Boots are ~40% too tall; the torso is short. Fix: boot tops to y 770–790, belt down 25–30 to 490–530, hem to 660–690. The viewer-right sole sits 50 higher; bring that foot forward ~0.4 head so both soles land at y 940–955.
3. **Midsection and sword arm.** The belt floats above the skirt with a visible gap. The skirt is a smooth lampshade with no pleats. The strap melts into the chest and stops at the pec. Fix: close the gap, model 7–9 box pleats, and make the strap a flat 0.3-head band that reaches the belt at the right hip. Move the sword fist out to x 250–290 (now ≈ 345) to fill the hole between arm and waist.

5. **Research check**
The rest agrees. One claim is wrong: the crest does not sweep back. It rises from the back of the helmet and peaks over the brow. The reference backdrop is even; the render has a clipped lower-left and a visible horizon band.

6. **What 8.5 needs**
- Corinthian helmet at 1.5×, pitched forward, with a forward-peaking fin.
- Shorter boots, lower belt, soles on one line.
- Pleated skirt joined to the belt; full-length strap.
- Sword fist at x ≈ 270; shield 160 wide, top at y 340.
- Even backdrop; shadow tone near (127,95,44).
