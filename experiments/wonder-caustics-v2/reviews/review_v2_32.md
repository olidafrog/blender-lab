# v2_32_hq — adversarial review

Bar numbering as before: **1** = tall left upright, **2** = tall centre upright, **3** = short slab
/ elbow under bar 1, **4** = lower-centre slab, **5** = lower-right slab. **Peanut** = top-right
figure. Coordinates are pixels in the 1440×1440 render, origin top-left.

**Verdict up front: the mechanism is right and the execution spilled.**

The banded panel did what I said it would do. For the first time in this series there is a real
**bright rail with black beside it**. Horizontal scan across bar 2 at y=500, x=490→690:

```
3 3 2 0 0 3 0 0 | 51 94 91 114 93 97 | 8 9 4 2 5 4 12 10 11 7 10 9 14 ...
```

A ~24 px rail at L≈95, then ~100 px of channel at L<15. v2_27 gave one 50–60 px soft gradient
there. Every strong-edge measure moved the right way for the first time:

| grad threshold | v2_27 | **v2_32** | ref_ring | v1 |
|---|---|---|---|---|
| >20 | 0.0489 | **0.0654** | 0.0842 | 0.1852 |
| >30 | 0.0209 | **0.0316** | 0.0541 | 0.1065 |
| >40 | 0.0120 | **0.0186** | 0.0375 | 0.0595 |
| >60 | 0.0045 | **0.0074** | 0.0178 | 0.0198 |

(My numbers, LANCZOS to 1440, lit = max(RGB)>25. They run a little above yours; the ratios are
what matter.) grad>20 is up **34%**, grad>40 up **55%**. Target was ≥0.11 / ≥0.030. Not there,
but this is the first round where the curve points at v1 instead of away from it.

**It is rejected because goal 1 went backwards.** v2_27's largest unexplained object was 296 px.
v2_32 has **three detached bright objects over 1000 px**, one of them brand new and the worst
single thing in the frame.

---

## 1. Artifact check by location

### Scan — connected components, max(R,G,B) > 25

**2867 components** (v2_27: 2228). Four bodies over 10,000 px: 263,371 (bars 1+3, x 81–755,
y 170–1334); 186,125 (bars 2+4, x 490–1016, y 118–1232); 113,324 (peanut, x 991–1319, y 57–676);
**30,181 (bar 5, x 891–1160, y 768–1326)**. Bar 5 detaching into its own component is threshold
bookkeeping, not an artifact — the elbow at ≈(1010,760) now dips under 25 — but note it, because
the darker frame is starting to sever the letterform's own connectivity.

Background: four 60 px corner patches, mean **1.32–1.39**, max **10**. Clean.

Every stray 30–10,000 px:

| px | bbox | verdict |
|---|---|---|
| **1670** | **x 1005–1073, y 696–749** | **NOT explicable. New. Worst object in frame.** |
| **1158** | **x 862–925, y 1265–1311** | **NOT explicable. The lozenge, 4× bigger than last round.** |
| 1774 | x 785–826, y 193–451 | **explicable.** Bar 2's right dispersion flank, broken by threshold. Attached visually along its whole length. |
| 312 | x 761–815, y 740–764 | **explicable.** The shoulder fringe, was 296. Unchanged. |
| 245 | x 618–657, y 848–870 | explicable — bar 4 crown fringe, follows the silhouette. |
| **200** | **x 1037–1054, y 752–774** | **NOT explicable.** Debris under the chip above; see below. |
| 100 / 65 / 50 / 40 / 37 / 33 / 30 | x 511–532 y 865–877; x 775–791 y 353–385; x 219–234 y 843–853; x 403–410 y 518–531; x 647–656 y 655–666; x 427–435 y 920–930; x 698–703 y 1034–1047 | explicable — threshold-dashed silhouette fringes, all within a few px of geometry. |

The 36 px red sliver at x 352–367, y 186–190 that I flagged last round is **gone**. Closed.

### The floating chip at (1005,696)–(1073,749) — **NEW, and the worst thing in the render**

Crop **(980,660)–(1110,800) at 500%, 1.6×**. A **68 × 53 px parallelogram lying in pure black**,
about 20 px clear of bar 5's top-left corner, with **nothing joining it to any geometry**. It
carries a full red→white→blue dispersion ramp across its short axis with a **clipped white rail
down its centre** — i.e. it is a piece of the new band panel being imaged by something that should
not be visible. All four edges are straight and square-cut. Directly beneath it sit **three blocky
red rectangles** at x 1037–1054, y 752–774 (the 200 px stray), stacked like corrupted scanlines.

This is not a fringe and not a caustic. It is the first object in this series that a viewer will
read as a render error rather than an odd highlight. Everything else in §1 is secondary to it.

### The bar-5 lozenge — **worse, fifth round**

Crop **(830,1230)–(960,1340) at 600%, 2×**. It is now **1158 px**, peak L **178**, against a
comparable ~300 px object in v2_27. It has become a full rainbow-striped bar with a **blunt
rounded red cap** at its head near (918,1272).

The side ramps are genuinely soft — cross-section at y=1288, sampled every 2 px:

```
2 1 2 7 16 16 33 71 116 150 170 176 172 151 136 111 88 68 23 12 0 1
```

about 10 px of ramp each side. **The ends still fail the test I set five rounds ago.** Along the
long axis at x≈915 it reads `6 1 2 1 13` at y=1265 and `4 2 18 80 12` at y=1270 — it **begins in
under 5 px**, not the ≥25 I asked for. Making it bigger and brighter while leaving the caps is the
wrong direction: a 300 px mistake is a blemish, a 1158 px mistake is a subject.

### Bar 1 crown — the comb is back, in a new costume

Crop **(80,150)–(400,330) at 300%, 1.4×** and the right-hand pair at **(660,185)–(960,220)**.

The near-tangent rear bevel maps the new hot rails into **four long, straight, parallel white
ribbons that appear to float clear of the crown**, plus two more running off bar 1's right shoulder
to x≈960. Vertical profile at x=150, y=180→290:

```
5 39 95 129 158 162 163 136 | 49 36 37 | 54 123 155 172 179 179 157 128 98 79 61 37 16 5 1 3 4 0 0 0 | 8 18 28 41 66 99 126 137 140 152 157 ...
```

Three slats, real dark gaps. In its favour: the ends taper over ~7 px (row y=215 from x=88:
`0 1 2 20 31 42 51 91 130 145 …`), so the square picket terminations are still closed. Against it:
each slat body is a **dead plateau — L 165–168 held for 40+ px** — and the stack as a whole is
precisely the object the user circled on `v1_annotated` and called jagged comb on the bevels. You
have traded a jagged comb for a clean venetian blind. The mechanism is correct; it must not be
allowed to run tangent to the view for 300 px.

### Kickers — halved, still clipping along their whole length

Clipped pixels (L≥250) per box: bar 5 (1050,1180)–(1220,1320) **300** (was 493); bar 4
(620,1180)–(790,1320) **326**; peanut (1180,560)–(1330,700) **191**. My cap was ≤100 each.

Row runs at L≥250 across the bar-5 streak: y=1210 **5**, 1220 **4**, 1230 **5**, 1240 **4**,
1250 **4**, 1260 **4**, 1270 **4**. Constant 4–5 px core, unbroken over 65 px of length. The width
no longer exceeds 6 px, so half of that test passes — but it is still a **straight, constant-width,
fully clipped rail**. Credit where due: the warm bloom around it in crop
**(1050,1180)–(1220,1320) at 400%** is new and photographic, and the top end now ramps in over
~10 rows instead of switching on. Frame total: 1285 px at 255 in all three channels, against
**v1's 215**.

### Peanut — clean, still empty

Crop (1200,120)–(1340,480) at 300%: zero artifacts, and still **no second contour**. One
silhouette, one smooth blue ribbon, no rear-bevel line. Fourth round open.

### Measured plate

Clipped (L>250) **0.107%** (v1 0.035%). Lit fraction **0.2915** (v1 0.2636). High-frequency
residual (L minus 3×3 median) sd on lit pixels **2.45** against v1's **4.15** and ref_ring's
**2.55** — I withdraw the sampler-noise complaint from last round; this render is *cleaner* than
v1. Flat blocks sd<2: **186** against v1's **218**. Also withdrawn, as promised.

---

## 2. Glass realism — **7.1 / 10** (was 6.8)

- **The dark channel exists.** That was the one thing separating this from real perspex and it is
  now on bars 1, 2 and 4. The y=500 scan above is the single best piece of evidence in the round.
- **The tone overshot.** Mean luma on lit pixels **68.4** (v1 67.3) is bang on, but the dark
  fraction went **0.285 → 0.420** against v1's **0.302**. You are now 12 points *darker* than the
  target you were 2 points short of. Bar 2's right flank and the peanut's lower third have gone to
  near-black mud, and bar 5 has fallen out of the letterform's connected component because of it.
  Do not read "darker" as "more like v1" — v1 is dark *and* has 0.185 of its lit pixels above
  grad 20. Darkness without contour is just loss.
- **Bar 4 reads as a contour map, not as glass.** Crop **(380,880)–(700,1300) at 200%**: broad flat
  fields of magenta, cobalt, cyan and lemon with ragged stepped boundaries, nested like isotherms.
  The metrics say this is no flatter than v1, so the fault is not flatness — it is that every
  boundary in that slab is a **soft colour transition** where v1 puts a specular event. Bar 4 got
  none of the new rail treatment.
- **No rear bevel anywhere.** Peanut crop (1200,120)–(1340,480): one contour, then 40 px of smooth
  blue. Fourth round.
- Best surface in frame, again: bar 1's crown face, x 380–660, y 200–560 — striated vermilion with
  fine dark vertical texture. It is the only place that looks like cast material rather than
  coloured light.

## 3. Style match to v1 and refs — **6.8 / 10** (was 6.0)

- **grad>20 = 0.0654** against v1's 0.1852 — the gap closed from 3.8× to **2.8×**. Against
  `ref_ring`'s 0.0842 it is now within **22%**. That is the first genuine movement on the metric
  that defines the difference.
- Saturation on lit pixels **0.806** against v1's **0.821** — effectively matched (was 0.790).
- Lit fraction **0.2915** against v1's **0.2636** — matched.
- Where it still misses: v1's rails are **3–8 px** wide and there are dozens of them per bar,
  following the curvature. v2_32's are **20–25 px** wide, straight, and there are three per bar.
  You have v1's contrast at a quarter of its frequency. Narrow the rails before you add more of
  them.
- The crown slats and the three kicker streaks have no counterpart in v1 or in any of the three
  refs. `ref_ring` clips **zero** pixels in 800×1067.

## 4. Compositing — **7.3 / 10** (was 7.2)

- Bloom improved: the warm halo around the bar-5 kicker is graded and size-appropriate. The
  strengthened panel vignette is doing its job — corner throws fade rather than end.
- Background floor (mean 1.32–1.39, max 10) and clip share 0.107% are correct.
- Open: **1285 px at pure 255** against v1's 215; three streaks all over the 100 px cap; no
  front-to-back atmospheric falloff — the peanut, furthest back, is rendered at the same contrast
  as bar 4 in front.

## 5. OVERALL — **7.9 / 10 — REJECTED**

Up 0.2. The band panel is the right idea, correctly implemented, and it moved the only metric that
matters in the only direction that matters. I am not taking that away from you.

It is rejected on goal 1. Last round the worst unexplained object was 296 px. This round there is a
**1670 px bright chip floating in black with a clipped rail through it**, a **1158 px lozenge that
grew fourfold**, and 200 px of blocky red debris beneath the chip. The same light that bought the
structure is leaking into the frame in three places, and one of them is unambiguously a bug. Fix
the leaks without touching the panel and this goes over 8.5 next round.

---

## 6. Ranked changes

1. **Find and kill the floating chip at (1005,696)–(1073,749).** — **MUST for 8.5.**
   68 × 53 px, 1670 px, detached, square on all four sides, with a clipped white rail across it,
   plus 200 px of blocky red debris at (1037,752)–(1054,774). Most likely the band panel seen
   directly past bar 5's top-left corner, or a rear-face self-intersection. Diagnose by rendering
   one frame with the panel emission at 0: if the chip vanishes, mask that corner's view of the
   panel; if it survives, it is geometry. Test: **no component over 150 px may sit more than 10 px
   from a body**, and the four bodies plus the chip box must contain zero clipped pixels outside
   the kickers.

2. **Kill the lozenge — for the last time.** — **MUST for 8.5.** Fifth round.
   1158 px, peak L 178, at x 862–925, y 1265–1311. The soft sides are fine now; the ends are not:
   it goes `2 → 18 → 80` in 5 px at (915,1268) and caps in a blunt red dome. Stop reshaping the
   throw — **mask bar 5's lower-left corner from the panel entirely**, or drop the panel's
   bottom-left band to 0 emission. Test: no component over 150 px in the box
   (830,1230)–(960,1340), and nothing there may reach L>120.

3. **Narrow the rails and stop them running tangent.** — **MUST for 8.5.**
   The rails are 20–25 px wide and produce 40 px plateaus at L 165–168 (x=150, y=215). v1's are
   3–8 px. Take the Gaussian rail from ~6% of band width to **2.5–3%**, and raise strength so peak
   luma holds at 160–180. That alone should carry grad>20 from 0.065 toward the **≥0.11** target
   and grad>40 to **≥0.030**. Second half of this, which matters as much: the four slats floating
   off bar 1's crown at (85,180)–(400,270) and the pair running to x≈960 at y≈205 are the object
   the user circled on v1. **Rotate the band panel 25–40° off the bar axis** so no rail can run
   parallel to a crown edge for more than ~80 px.

4. **Bring the dark fraction back from 0.420 to 0.32–0.34.** — **MUST for 8.5.**
   You aimed at v1's 0.302 from 0.285 and landed at 0.420. Mean luma is right (68.4 vs 67.3), so
   the fix is the vignette, not exposure: take the panel edge dim from 60% back to **35–40%**.
   Test: dark fraction 0.32–0.34, mean luma on lit 66–72, and **bar 5 must rejoin the main body as
   a single connected component** at max(RGB)>25.

5. **Cap the kickers at 100 clipped pixels each and taper the tails.** — **MUST for 8.5.**
   Now 300 / 326 / 191 against a cap of 100. The width test passes (4–5 px runs); the length test
   does not — the core is at 255 continuously from y=1210 to y=1275. Confine 255 to the brightest
   **20%** of each streak and let the rest sit at 200–240. Test: ≤100 px at L≥250 per streak box,
   and total frame pixels at 255 in all channels **≤ 500** (now 1285, v1 215).

6. **Give bar 4 and the peanut the rail treatment.** — **nice-to-have.**
   Bar 4 (380,880)–(700,1300) and the whole peanut are the two places the new panel never reaches;
   both are still soft colour fields with no specular event inside a 400 px span. Once change 3
   narrows the rails, check that at least **two rails cross bar 4's face** and **one crosses the
   peanut's waist**. That also gives the rear-bevel contour its best chance, which is the only
   §2 complaint now entering its fourth round.

SCORE: 7.9
