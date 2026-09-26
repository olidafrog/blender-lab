# v2_39_hq — adversarial review

Bar numbering as before: **1** = tall left upright, **2** = tall centre upright, **3** = short slab
/ elbow under bar 1, **4** = lower-centre slab, **5** = lower-right slab. **Peanut** = top-right
figure. Coordinates are pixels in the 1440×1440 render, origin top-left.

**Verdict up front: you fixed the bug and paid for it with the picture.**

The chip is gone. Not reduced — gone. Both isolation diagnoses were right and both fixes worked.
That was the thing that made v2_32 a bug report instead of an image, and it is closed. The peanut
has a rear-bevel contour for the first time in five rounds. Those are two real wins.

Against that: **grad>20 fell from 0.0401 to 0.0229.** You did not narrow the rails, you dissolved
them. The one metric that separates this render from v1 is now *worse than v2_27's* (0.0489) and
**6.0× below v1**, against 2.8× last round. Every profile I pulled across a bar face is a smooth
200 px ramp where v1 puts spikes and black. The frame is cleaner, quieter, and further from the
target than it has been in four rounds.

---

## 1. Artifact check by location

### Scan — connected components, max(R,G,B) > 25

**1044 components** (v2_32: 2867 — a 64% drop, the frame is genuinely tidier). Four bodies over
10,000 px: 237,319 (bars 1+3, x 82–752, y 171–1334); 176,809 (bars 2+4, x 491–956, y 124–1234);
95,600 (peanut, x 991–1315, y 58–675); 27,196 (bar 5, x 940–1160, y 768–1304). Bar 5 is still
severed from the main body at the elbow. Change 4's test said it must rejoin. It has not.

Background: four 60 px corner patches, mean **0.85–0.91**, max **10** (v2_32: 1.32–1.39). Cleanest
floor in the series.

Every stray 30–10,000 px:

| px | bbox | peak L | verdict |
|---|---|---|---|
| **3837** | **x 642–693, y 884–1036** | **47** | **NEW. Soft, but a detached 51×152 plume in black.** |
| 905 | x 1220–1250, y 115–223 | 52 | **explicable — and welcome.** The peanut's new rear bevel, dashed by threshold. |
| **727** | **x 864–920, y 1270–1308** | **87** | **NOT explicable. The lozenge. Sixth round.** |
| 412 | x 1211–1241, y 220–266 | 45 | explicable — same rear bevel, next segment. |
| 347 | x 235–269, y 883–905 | 38 | explicable — bar 3 shoulder fringe, on the silhouette. |
| 311 | x 1008–1043, y 709–738 | 15 | explicable now. Chip remnant, below visible threshold. |
| 309 | x 616–657, y 848–873 | 17 | explicable — bar 4 crown fringe. |
| 303 | x 902–947, y 1305–1325 | 32 | marginal — lozenge's lower tail. |
| **296** | **x 1031–1054, y 749–775** | **54** | **NOT explicable. The blocky red debris survived.** |
| 223 / 158 / 119 / 118 / 78 / 56 / 45 / 42 / 35 | peanut and bar-5 rim runs | ≤43 | explicable — threshold-dashed silhouette fringes. |

### The floating chip at (1005,696)–(1073,749) — **CLOSED**

Crop **(960,660)–(1120,800) at 400%, native gamma**. The box now reads **peak L 15, mean 2.1, and
zero pixels above max(RGB)=25**. Against 1670 px at L 182 last round. At a 2.0 gamma lift you can
still see a dull red parallelogram ghost, but at display gamma there is nothing there. Your stated
figure of 65 is generous to yourself; I measure 15. Either way it is dead. The refraction-only
back panel plus the Light Path gate on the glossy lobe is the correct fix and it held.

**Not closed: the debris under it.** x 1031–1054, y 749–775, **296 px, peak L 54, 58 px above
threshold**. Still three blocky red rectangles stacked like corrupted scanlines, still square-cut,
still sitting in black off bar 5's corner. It came down from 200 px at higher luma to 296 px at
lower luma — it is more visible as an object now, not less. The chip's parent got gated; this
child did not.

### The bar-5 lozenge — **smaller, still there, sixth round**

Crop **(830,1240)–(970,1345) at 500%, native gamma**. At native gamma it is still an unambiguous
bright rainbow sliver lying in black with nothing touching it.

- 1158 px → **727 px**; peak L 178 → **87**; box mean 40 → **10.1**. Real movement.
- Cross-section at y=1288, every 2 px from x=858: `1 0 1 0 1 0 0 1 0 0 0 0 4 0 9 10 34 48 74 80 81
  66 48 43 36 22 2 0 0 1` — ~12 px of ramp each side. The sides were never the problem.
- **The ends still fail.** Long axis at x=890, every 2 px from y=1262: `1 0 1 0 0 1 1 2 0 6 1 5 6
  34 56 68 59 43 26 7 0 0 0` — it goes **6 → 34 → 56** in 4 px and terminates in 6 px. I asked for
  ≥25 px five rounds ago. My test was "no component over 150 px in (830,1230)–(960,1340) and
  nothing above L 120". You are at **727 px and L 87**. Half a pass.

You dimmed the throw instead of masking the corner, exactly what I told you to stop doing. It will
still be visible on the third iteration of dimming. Mask it.

### The new plume at (642,884)–(693,1036) — **NEW**

Crop **(590,850)–(740,1070) at 400%, native gamma**. A **51 × 152 px brown-orange haze** hugging
bar 4's right rim with a black gap between it and the geometry, then fading into black on its
outer side. 3837 px, peak L 47, mean 16.2. Cross-section at y=960 from x=636: `27 27 24 21 9 0 1 6
0 0 0 1 18 32 38 37 38 38 36 42 38 43 42 39 28 17 7 0` — a 14 px dark channel, then a 30 px body
at a flat L 36–43, then a 10 px fade.

I will not call this a bug. It has soft edges on all four sides and it reads as atmosphere. But it
is the largest detached object in the frame, it is a **dead plateau at L 38 for 30 px**, and it
sits in the one place where the render can least afford ambiguity — right where the chip used to
be, one slab over. Either commit to it as a dust/haze pass across the whole frame, or lose it.
One brown plume on one rim reads as a leak.

### Bar 1 crown — the venetian blind survived, narrower

Crop **(80,150)–(420,340) at 300%, 1.4×**. Change 3's second half — **rotate the band panel 25–40°
off the bar axis** — was not done. Three straight parallel ribbons still run off the crown to the
upper-left, still parallel to the crown edge, still apparently floating clear of it.

Vertical profile at x=120, y=175→270 every 3 px:

```
2 0 0 0 0 | 49 63 8 | 0 0 0 0 | 27 55 56 27 | 8 10 15 37 44 37 24 | 0 3 0 0 ...
```

Three slats, ~9–12 px wide now (was 20–25), separated by true black. Peak in the slat box came
down from 165–168 to **115**. Narrower is correct in isolation, but here it backfires: a 22 px
soft ribbon read as a lens flare, a 10 px hard-edged one reads as a **stick**. This is the exact
object the user circled on `v1_annotated` and called a jagged comb. Three rounds on that note.

### Kickers — **not touched**

Clipped pixels (L≥250) per box: bar 5 (1040,1170)–(1220,1320) **282** (was 300); bar 4
(620,1180)–(800,1330) **316** (was 326); peanut (1180,540)–(1330,700) **176** (was 191). Cap was
**100 each**. A 4% reduction is not a 40% dim.

Row runs at L≥250 across the bar-5 streak: y=1210 **4**, 1220 **4**, 1230 **5**, 1240 **4**, 1250
**4**, 1260 **4**, 1270 **4**. Identical to v2_32, row for row.

Crop **(1040,1170)–(1220,1320) at 300%**: a laser-straight, constant-width, fully clipped white bar
that **continues ~30 px past the geometry into empty black**. No cast perspex edge does this. The
warm bloom around it is good and photographic; the core inside it is a 3D-viewport gizmo. Frame
total 1125 px at pure 255 against **v1's 215**.

### Peanut — **rear bevel achieved**

Crop **(1170,60)–(1330,300) at 400%, 1.5×**. For the first time: a **second contour**. A curved
spectral line — red, green, magenta, cyan in sequence — running down the peanut's right flank,
**separated from the silhouette by a 25–40 px dark gap**. 905 px + 412 px as two threshold-dashed
components, peak L 52. Row at y=170 from x=1190: forty samples of near-zero, then `6 43 44 32 7 10
6` at x≈1238. A clean thin event on black.

That is the correct look, it is the first piece of this render that would pass unremarked in
`ref_ring`, and it closes a complaint I have carried since v2_10. It is also the proof that the
mechanism can produce v1-grade contour — you got one, on the surface furthest from the panel.

### Measured plate

| | v2_32 | **v2_39** | v1 | ref_ring |
|---|---|---|---|---|
| lit fraction | 0.2915 | **0.2640** | 0.2636 | 0.3259 |
| mean L on lit | 66.2 | **62.1** | 67.8 | 119.6 |
| dark frac (L<20 of lit) | 0.2603 | **0.2588** | 0.1399 | 0.0588 |
| saturation on lit | 0.806 | **0.8215** | 0.8215 | 0.367 |
| grad>20 | 0.0401 | **0.0229** | 0.1367 | 0.0589 |
| grad>30 | 0.0211 | **0.0108** | 0.0651 | 0.0354 |
| grad>40 | 0.0111 | **0.0058** | 0.0317 | 0.0217 |
| grad>60 | 0.0028 | **0.0015** | 0.0047 | 0.0080 |
| clipped L>250 | 0.1075% | **0.1059%** | 0.0362% | 0.0003% |
| pure 255 px | 1285 | **1125** | 215 | 0 |
| hf residual sd | 2.43 | **2.52** | 4.45 | 2.55 |

Lit fraction and saturation now match v1 to three decimals. Every gradient measure halved.

---

## 2. Glass realism — **7.3 / 10** (was 7.1)

- **The peanut's rear bevel is the best thing in the render.** A thin spectral contour with black
  either side is what perspex does and what this series has never had. Up half a point on its own.
- **The bars lost their specular events.** Horizontal L across bar 1 at y=600, every 6 px from
  x=150:

  ```
  v2_39: … 36 58 92 44 50 27 21 45 37 95 125 104 134 138 143 140 98 122 140 152 160 164 166 165 164 89 21 …
  v1:    … 38  8 56 90 59 60 48 12  3   0   0   0   0   0   0   0  0   0  14  85 130  53  51   0  73 122 100 27 …
  ```

  v1 alternates spike–zero–spike across the same 270 px. v2_39 is one **200 px monotone ramp with
  no zero in it**. That is not a rail-width problem, it is an absence of rails. Bar 2 is the only
  face that still has the rail-and-channel structure (y=300: `31 50 106 149 156 148 127 84 65 22 15
  12 12 …`) and its rail is **~50 px wide**, not the 3–8 px I asked for.
- **Bar 4 is still a contour map.** Crop **(380,880)–(700,1300) at 200%**: nested isotherms of
  magenta, cobalt, cyan and lemon with **ragged staircase boundaries**. The flat-block count says
  it is *less* flat than v1's same box (0.076 vs 0.326), so this is not banding in the tonal sense
  — it is that every boundary is a soft colour transition where v1 puts a hard event. Bar 4 still
  gets no rail treatment, three rounds after I flagged it.
- **No dust, no smudge, no surface.** hf residual 2.52 against v1's 4.45. `ref_ring` at 2.55 gets
  away with it because it carries **visible fine scratches and specks across the whole face** —
  look at its lower-left quadrant. The user asked for that explicitly on the annotation. Nothing
  has been attempted in eight rounds.
- **The frame went dim.** Mean L on lit 62.1 against v1's 67.8, the lowest in four rounds. You
  eased the vignette to 35% and it still landed darker, so the loss is in the rails, not the
  vignette.

## 3. Style match to v1 and refs — **5.9 / 10** (was 6.8)

This is where the round is lost.

- **grad>20 = 0.0229** against v1's 0.1367. The gap went from 2.8× to **6.0×**. Against `ref_ring`'s
  0.0589 you are now **61% below**, having been within 22% last round. grad>40 halved to 0.0058
  against a target of ≥0.030.
- This is **below v2_27** (0.0489), the render I called a soft gradient with no dark channel. Four
  rounds of movement on the defining metric, undone in one.
- The cause is legible in the numbers: narrowing the rails to 3% removed their *area* without the
  strength increase recovering their *contrast*. Peak on the crown slats fell 165 → 115. You need
  narrow **and** hot. You got narrow and cool.
- **Genuinely matched now:** saturation 0.8215 vs v1 0.8215 (exact), lit fraction 0.2640 vs 0.2636
  (exact). Those two are done — stop tuning them.
- **Still alien to all four references:** three fully clipped straight streaks. `ref_ring` clips
  **zero** pixels in 800×1067. v1 clips 215.

## 4. Compositing — **7.5 / 10** (was 7.3)

- **Background floor is the best in the series:** corner means 0.85–0.91, max 10, down from
  1.32–1.39. Clean black, no lift, no banding.
- Bloom around the bar-5 kicker is graded, warm, and correctly sized. That part is photographic.
- Component count 2867 → 1044 — the frame no longer reads as noisy.
- **Open:** 1125 px at pure 255 against v1's 215, and 0.106% clipped against v1's 0.036%. The three
  streaks are unchanged and all three overshoot the geometry into black.
- **Open:** no front-to-back falloff. The peanut sits furthest back and is rendered at the same
  contrast and saturation as bar 4 in front.

## 5. OVERALL — **8.0 / 10 — REJECTED**

Up 0.1. That is the honest arithmetic of a round that went sharply right on goal 1 and sharply
wrong on goal 3.

Credit in full: the 1670 px chip is at **peak L 15 and zero pixels above threshold**, the isolation
diagnosis was correct, the fixes were the right fixes, the background floor is the cleanest yet,
and the peanut finally has a rear bevel that would not look out of place in `ref_ring`.

Rejected because the picture got quieter. **grad>20 is 0.0229** — below the render I rejected four
rounds ago for having no structure — and bar 1's face is now a 200 px ramp with no black in it.
The lozenge is on its sixth round at 727 px. The kickers were not dimmed by any measurable amount:
282/316/176 clipped against a cap of 100, with identical row runs to last round.

You have proven the panel can make a v1-grade contour — it made one on the peanut. Put that same
event on the bar faces at v1's frequency, mask the two corners that leak, and cut the kickers for
real, and this clears 8.5.

---

## 6. Ranked changes

1. **Restore the rails: narrow *and* hot, at v1's frequency.** — **MUST for 8.5.**
   grad>20 fell 0.0401 → **0.0229** against v1's 0.1367. Narrowing to 3% without a matching
   strength rise cost you 43% of the metric. Keep the 3% width, **raise band emission until peak
   luma on a rail holds at 190–220** (crown slats are at 115 now), and **increase the band count
   so at least 6 rails cross bar 1's face between x=150 and x=420** — it currently has none, just
   a 200 px ramp (`95 125 104 134 138 143 140 98 122 140 152 160 164 166 165 164`). Test:
   **grad>20 ≥ 0.080, grad>40 ≥ 0.022**, and a horizontal cut at y=600 across bar 1 must contain
   **≥3 excursions from below L 30 to above L 140**. Do not let mean L on lit drop below 64.

2. **Mask the lozenge corner. Stop dimming it.** — **MUST for 8.5.** Sixth round.
   727 px, peak L 87, x 864–920, y 1270–1308, with a 303 px tail at (902,1305)–(947,1325). It still
   ignites in 4 px (`6 → 34 → 56` at x=890) and it is still a detached rainbow sliver on black.
   You have now dimmed it three times. **Mask bar 5's lower-left corner from the panel entirely**,
   or set the panel's bottom-left band to 0 emission. Test: **zero components over 150 px in the
   box (830,1230)–(970,1345)**, nothing there above L 40.

3. **Cut the kickers for real.** — **MUST for 8.5.**
   The stated 40% dim did not register: 282 / 316 / 176 clipped against 300 / 326 / 191, with the
   bar-5 row runs identical row for row (4,4,5,4,4,4,4 at y=1210–1270). The core is a constant-width
   clipped bar that **overshoots the geometry by ~30 px into black**. Confine L≥250 to the
   brightest **15%** of each streak, taper the outer 40 px of each tail to L 120–180, and **clip
   the streak to the silhouette so no clipped pixel sits outside the glass**. Test: **≤100 px at
   L≥250 per streak box**, **total frame pure-255 ≤ 400** (now 1125, v1 215), and no pixel above
   L 200 more than 8 px outside any body's mask.

4. **Rotate the band panel 25–40° off the bar axis.** — **MUST for 8.5.** Carried from last round,
   not done.
   Three slats still run parallel to bar 1's crown edge at (85,175)–(410,275), now 9–12 px wide
   with hard black gaps — narrower has made them read more like floating sticks, not less. This is
   the object the user circled. Test: **no rail may run within 15° of a crown or shoulder edge for
   more than 80 px**, and the crown-slat box must contain no straight run above L 90 longer than
   120 px.

5. **Kill the 296 px debris and decide about the 3837 px plume.** — **MUST for 8.5.**
   The debris at x 1031–1054, y 749–775 (peak L 54, 58 px above threshold) is the chip's leftover
   — three square-cut red rectangles in black. The same gate that killed the chip should reach it.
   The plume at x 642–693, y 884–1036 (3837 px, peak 47, a flat L 38 plateau for 30 px) is soft
   enough to pass as haze, but as the only one in the frame it reads as a leak. Test: no component
   over 250 px more than 12 px from a body, **or** — if you keep the plume — extend the same haze
   to at least three rims so it reads as an atmosphere pass.

6. **Give the bars the peanut's treatment, and add surface dirt.** — **nice-to-have.**
   The peanut's new rear bevel at (1211,115)–(1250,266) is the only place in eight rounds that
   looks like `ref_ring`. Bar 4 (380,880)–(700,1300) is still nested isotherms with no specular
   event in 400 px. Aim for **one rear-bevel contour on bar 4 and one on bar 1**, thin, with black
   on both sides. Separately, the dust/smudge note from `v1_annotated` has never been attempted:
   hf residual is 2.52 against v1's 4.45, and `ref_ring` carries visible specks and hairline
   scratches across its whole face. A low-amplitude scratch/dust map on the glass at roughness
   0.03–0.06 would lift hf residual toward 3.5–4.0 and is the cheapest realism gain left.

SCORE: 8.0
