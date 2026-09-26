# v2_42_hq — adversarial review

Bar numbering as before: **1** = tall left upright, **2** = tall centre upright, **3** = short slab
/ elbow under bar 1, **4** = lower-centre slab, **5** = lower-right slab. **Peanut** = top-right
figure. Coordinates are pixels in the 1440×1440 render, origin top-left. v1 is resampled to
1440×1440 for every comparison.

**Note on the metric plate.** I recomputed every figure this round with my own operator rather than
carrying numbers forward, so the absolute values shift slightly against `review_v2_39.md`
(my grad>20 on v1 reads 0.1505, not 0.1367). Every number below is measured with the same operator
on all four images, so the ratios are honest. Where I quote a v2_39 figure it is re-measured, not
quoted.

**Verdict up front: you bought back the picture and did not lose the bug fixes. It is the best
round of the v2 loop. It is still not v1.**

Three of the five MUSTs are genuinely closed. The kickers are fixed — properly, not by a rounding
error. The plume is gone. Component count is the lowest in the series. The rails are back on bar 1
and bar 4 with real contrast. Against that: the lozenge is on its **seventh** round, the crown
slats survived the 22° rotation intact, and the gap that actually separates this from v1 —
**gradient density, grad>40 at 0.0078 against 0.0428** — closed by only 20% when it needed to
close by 400%.

---

## 1. Artifact check by location

### Scan — connected components, max(R,G,B) > 25, 8-connected

**767 components** (v2_39: 1044, v2_32: 2867). Lowest in the series. Four bodies over 10,000 px:

| px | bbox | body |
|---|---|---|
| 238,349 | x 82–736, y 171–1332 | bars 1 + 3 |
| 176,172 | x 492–954, y 123–1229 | bars 2 + 4 |
| 95,329 | x 992–1300, y 58–674 | peanut |
| 35,993 | x 925–1141, y 769–1309 | bar 5 |

**Bar 5 is still severed from the main body at the elbow.** Change 4 of the v2_27 round said it
must rejoin; it has not, four rounds running. It grew (27,196 → 35,993 px) but it is still its own
component. At the resolution the user will look at this, the elbow junction at (920,1230) reads as
a real gap in the letterform — this is now the most visible *compositional* fault in the frame and
nobody has touched it.

Background: four 60 px corner patches, mean **0.68–0.72**, max **6.3** (v2_39: 0.85–0.91, max 10).
Cleanest floor yet.

Every stray 30–10,000 px:

| px | bbox | peak L | verdict |
|---|---|---|---|
| 1975 | x 646–688, y 887–1025 | **22** | **CLOSED.** The plume. Peak 47 → 22; nothing above L 25 in the box at display gamma. |
| 947 | x 1200–1248, y 90–190 | 56 | explicable — and the best thing in the frame. Peanut rear bevel. |
| **505** | **x 897–948, y 1306–1325** | **44** | **NOT explicable. Lozenge lower tail. Seventh round.** |
| **360** | **x 875–919, y 1271–1303** | **73** | **NOT explicable. The lozenge itself. Seventh round.** |
| **254** | **x 1033–1053, y 750–774** | **56** | **NOT explicable. The blocky red debris. Unchanged, third round.** |
| 214 | x 1275–1292, y 474–508 | 36 | explicable — new second rear-bevel segment on the peanut's lower right. Welcome. |
| 97 / 73 / 70 / 40 / 40 / 32 | rim and bevel runs, peanut + bar 5 | ≤39 | explicable — threshold-dashed silhouette fringes. |

### The plume at (646,887)–(688,1025) — **CLOSED**

Crop **(600,850)–(740,1070) at 300%, native gamma**. Box max **66** (that is bar 4's own rim
inside the box), the detached component itself peaks at **22**, box mean **7.8**. Against 3837 px
at peak 47 and a flat L 38 plateau last round. You chose "lose it" and it is lost. Correct call —
one plume on one rim was never going to read as atmosphere.

### The kickers — **CLOSED, and this is the headline**

Clipped pixels (L≥250) per box, against a cap of 100 each:

| box | v2_39 | **v2_42** | cap |
|---|---|---|---|
| bar 5 (1040,1170)–(1220,1320) | 282 | **63** | 100 |
| bar 4 (620,1180)–(800,1330) | 316 | **44** | 100 |
| peanut (1180,540)–(1330,700) | 176 | **84** | 100 |

Row runs at L≥250 across the bar-5 streak, y=1210→1270: **1, 0, 2, 1, 1, 1, 1**. Last round:
4,4,5,4,4,4,4. The laser-straight constant-width clipped core is gone; what is left is a warm
graded bloom with a 1–2 px hot thread, which is what a cast-perspex edge actually does. The
overshoot past the geometry into black is gone with it. 260 W → 60 W was the right size of cut and
it cost the frame nothing — mean L on lit went **up**, 62.1 → 71.6.

Frame-wide pure-255 is **765** (v2_39: 1125, v1: 215). But the distribution changed completely.
**1420 of 1621 clipped pixels now sit in one object**: the specular blade down bar 2's right flank,
x 700–790, y 355–690. Profile across it at y=470, every 4 px from x=700:

```
130 127 137 154 162 170 176 185 210 251 255 227 195 186 184 182 104 70 50 21
```

3–8 px wide, curving, with shouldered falloff on both sides, entirely inside the silhouette. That
is a highlight, not a gizmo. v1's own largest clipped cluster is 291 px in a single 60 px cell on
bar 1's crown — the same kind of object. **I am closing the kicker note. Stop tuning it.**

### The bar-5 lozenge — **STILL OPEN. Seventh round.**

Crop **(820,1230)–(980,1350) at 500%, native gamma**. It is now a green-yellow spectral sliver
rather than a rainbow one, and it is dimmer. It is still an unambiguous detached object lying in
black with a clean gap between it and bar 5's corner.

- 727+303 px → **360+505 px**; peak L 87 → **73**.
- Long axis at x=890, every 2 px from y=1290: `9 15 42 41 18 9 1 0` — it ignites **9 → 42 in 4 px**
  and terminates in 6 px. Identical failure mode to last round.
- Cross-section at y=1288: `9 9 37 48 69 64 40 37 29 18 2` — ~14 px of ramp each side. The sides
  were never the problem.

My test was: **zero components over 150 px in (830,1230)–(970,1345), nothing above L 40**. You are
at **two components, 360 px and 505 px, peak L 73**. Fourth consecutive dim. The soft hole in the
panel reduced it by 16% in area. It is back-panel refraction, you have confirmed that by isolation,
and the answer is still to **mask the corner**, not to dim the thing that lights it.

### The debris at (1033,750)–(1053,774) — **STILL OPEN, unchanged**

Crop **(990,700)–(1090,800) at 600%**. 296 px / peak 54 → **254 px / peak 56**, 74 px above
threshold. Three square-cut red rectangles stacked like corrupted scanlines, sitting in black off
bar 5's upper corner. This is the chip's child. Its parent got gated in v2_39 and this did not, and
nothing this round reached it. Third round, no measurable movement.

### Bar 1 crown — the venetian blind **survived the 22° rotation**

Crop **(80,150)–(420,340) at 300%**. The band panel went to 22° and shrank to 8.5 m, and there are
**still three straight parallel ribbons** running off the crown to the upper-left, still apparently
parallel to the crown edge, still floating clear of the geometry.

Vertical profile at x=120, y=175→270 every 3 px:

```
3 0 0 0 0 | 39 62 7 | 0 0 0 | 10 59 34 6 | 2 0 5 9 34 43 34 22 | 0 3 0 0 ...
```

Three slats, 6–12 px wide, separated by true black. Peak in the crown box went **115 → 147** — the
rail-heat change hit these too, so they are *more* visible than last round, not less. This is the
object the user circled and called a jagged comb. **Four rounds on that note.** 22° was not enough,
or the slats are not coming from the band panel at all — the fact that a 22° rotation left them
still parallel to the crown edge suggests the second. Worth an isolation render before the next
rotation attempt.

### Peanut — second bevel segment gained

Crop **(1170,60)–(1330,540) at 250%**. Last round's rear-bevel contour is intact (947 px, peak 56)
and there is now a **second segment** at x 1275–1292, y 474–508 (214 px, peak 36) on the lower
right flank. Both are thin spectral lines with black on both sides and a 25–40 px dark gap from the
silhouette. This remains the only surface in the render that would pass unremarked in `ref_ring`.

### Measured plate

| | v2_39 | **v2_42** | v1 | ref_ring |
|---|---|---|---|---|
| lit fraction | 0.2640 | **0.2662** | 0.2636 | 0.3257 |
| mean L on lit | 62.1 | **71.6** | 67.7 | 119.7 |
| dark frac (L<20 of lit) | 0.2588 | **0.2207** | 0.1399 | 0.0592 |
| saturation on lit | 0.8215 | **0.7995** | 0.8215 | 0.3671 |
| grad>20 | 0.0264 | **0.0324** | **0.1505** | 0.0922 |
| grad>30 | 0.0116 | **0.0139** | **0.0804** | 0.0599 |
| grad>40 | 0.0065 | **0.0078** | **0.0428** | 0.0410 |
| grad>60 | 0.0024 | **0.0025** | 0.0111 | 0.0208 |
| clipped L>250 | 0.106% | **0.078%** | 0.036% | 0.0002% |
| pure 255 px | 1125 | **765** | 215 | 0 |
| hf residual sd | 3.26 | **3.38** | 5.93 | 6.61 |
| flat-block frac, bar 1 face | — | **0.140** | **0.480** | — |
| components ≥30 px | ~30 | **16** | — | — |

Read the last three rows together, because they are the whole diagnosis. **v1 is simultaneously
flatter and sharper than v2_42.** 48% of v1's bar-1 face is genuinely flat — near-zero local
gradient — and it spends its contrast budget on a small number of 1–3 px hard events.
v2_42 is flat over only 14% and has no hard events: its colour boundaries take **10–30 px** to
cross. That is why grad>40 is 5.5× short while mean luma and hue travel already match. You do not
need more colour or more light. You need the *same* picture with every boundary a quarter as wide.

---

## 2. Glass realism — **7.5 / 10** (was 7.3)

- **The kicker fix is the single biggest realism gain in eight rounds.** Three clipped 3D-viewport
  gizmos became three warm graded blooms with a thin hot core. Every ref has this and no previous
  v2 did.
- **Rails are back and they work where they landed.** Bar 1 at y=600, x 150→420, every 6 px:
  `0 0 0 2 3 0 1 0 5 97 131 127 127 82 67 70 55 94 124 100 132 135 134 121 31 22 34 41 47 80 93 105 110 83 36`.
  There is a **real dark channel at x≈294–318 (L 31, 22, 34)** between two lit regions. Last round
  the same cut was a single 200 px monotone ramp with no zero in it. That is the structural change
  I asked for and it happened.
- **But the boundaries are still soft everywhere.** Bar 4 at y=1050 climbs `96 127 144 142 144 130
  123 141 142 155 158 148 150 157 154 158 158 162 172` — 250 px of plateau at L 130–172. v1's same
  cut is `57 98 97 97 96 94 94 97 97 100 104 108 114 118 123 128 131 137 142 143 140 137 138 138
  63 42 33 0` and then falls **138 → 63 → 42 → 33 → 0 in 24 px**. v1 terminates; v2_42 fades.
- **Bar 4 is still a contour map.** Crop **(380,880)–(700,1300) at 200%**: nested magenta, cobalt,
  cyan and lemon isotherms with ragged, noisy boundaries. It reads as a thermal map, not glass.
  This is the region you correctly rejected the five-band 30° version over — but bar 4 already has
  that look at three bands. It is the worst surface in the frame and it has been flagged four
  rounds.
- **No dust, no smudge, no surface — and the hf residual is lying to you.** 3.38 against v1's 5.93
  and `ref_ring`'s 6.61, but the crops show that what little hf v2_42 has is **chroma render noise
  in the black**, not surface detail. Look at the crown crop's background: speckled magenta-green
  grain. `ref_ring` carries visible hairline scratches and specks across the whole face and a clean
  black. You have the opposite of both. The user asked for this explicitly on the annotation and it
  has never been attempted in nine rounds.

## 3. Style match to v1 and refs — **6.6 / 10** (was 5.9)

- **grad>20 recovered 0.0264 → 0.0324 (+23%)**, and grad>40 0.0065 → 0.0078 (+20%). Real movement,
  and in the right direction after a round that went backwards. Against v1 you are **4.6× short on
  grad>20 and 5.5× short on grad>40**, against 5.7× and 6.6× last round. Two rounds of this rate
  will not get there.
- **Against `ref_ring` the gap widened in the way that matters**: ring runs grad>40 at 0.0410 with
  only 0.0922 at grad>20 — a *high ratio of hard events to soft ones*, 0.44. v1's ratio is 0.28.
  v2_42's is **0.24**. Your events are disproportionately soft, and that is the fingerprint.
- **Hue travel already matches.** Mean hue travel per scanline across bar 1: v2_42 **15.3**,
  `ref_ring` **15.2**, v1 23.1. Across bar 4: v2_42 18.7, v1 36.6. You are not short of colour.
  Stop adding bands. The five-band rejection was correct and the same instinct should now be
  applied to bar 4's existing three.
- **Matched and done:** lit fraction 0.2662 vs 0.2636, saturation 0.7995 vs 0.8215, mean L 71.6 vs
  67.7 (slightly hot now — do not push further). Component count and background floor both beat
  every earlier round.
- **Still alien:** the three crown slats. Nothing in v1, `ref_ring`, `ref_puck` or `ref_abstract`
  has a straight hard-edged ribbon floating off a silhouette into black.

## 4. Compositing — **8.3 / 10** (was 7.5)

- **Background floor is the best in the series:** corner means 0.68–0.72, max 6.3.
- **Highlight discipline arrived.** 0.078% clipped against v1's 0.036% — the closest yet — and the
  clipping is now concentrated in one plausible specular blade rather than spread across three
  synthetic streaks.
- **767 components.** The frame no longer reads as noisy at any zoom a viewer will use.
- **Open, and now the most visible fault:** bar 5 is a separate body. The elbow at (920,1230) is a
  visible break in the letterform. Four rounds.
- **Open:** still no front-to-back falloff. The peanut sits furthest back and is rendered at the
  same contrast, saturation and sharpness as bar 4 in front. Both `ref_ring` and `ref_puck` carry
  visible depth-of-field. This is the cheapest "more dynamic, realistic compositing" win left on
  the user's original note and it has never been tried.
- **Open:** chroma noise in the black at 400%+. Not visible at 100%, but it is what your hf
  residual is made of, and it will block any genuine dust pass from reading.

## 5. OVERALL — **8.2 / 10 — REJECTED**

Up 0.2, and I want to be clear this is a good round, not a token increment. You closed the two
hardest artifact notes properly: the kickers went from 282/316/176 clipped to **63/44/84** against
a cap of 100, and the plume went from 3837 px at peak 47 to a component that peaks at **22**. The
rails came back without costing luma — mean L on lit is **up** to 71.6. The background floor and
the component count are both the best of the series. And the peanut grew a second rear-bevel
segment, which is the second surface in this project that looks like the reference.

Rejected on one thing, stated plainly: **grad>40 is 0.0078 against v1's 0.0428.** Every colour
boundary on every bar takes 10–30 px where v1 takes 1–3. Bar 4's face is 250 px of unbroken L
130–172 plateau. v1 is simultaneously **flatter** (0.480 of bar 1 truly flat, against your 0.140)
**and sharper**. Until that flips, the render reads as an airbrushed contour map with glass-coloured
paint, and the user will see that before he sees any of the fixes.

Two carried faults also have to stop being carried: the lozenge is on its **seventh** round and its
fourth consecutive dim, and the crown slats survived a 22° panel rotation unchanged and got
**brighter** (peak 115 → 147). Three rounds of the same mechanism failing to remove them is a sign
the diagnosis is wrong, not that the angle is wrong.

**If you change one thing, change the boundary width.** Not the colour, not the band count, not the
lighting — just make every spectral transition terminate instead of fade.

---

## 6. Ranked changes

1. **Sharpen every colour boundary. Narrow transitions, not the bands.** — **MUST for 8.5.**
   grad>40 is **0.0078** against v1's **0.0428** and `ref_ring`'s 0.0410, and the hard-to-soft event
   ratio is 0.24 against v1's 0.28 and ring's 0.44. Hue travel already matches ring exactly (15.3
   vs 15.2), so **do not add bands** — the five-band rejection was right. Instead compress each
   existing band's edge profile: drop the panel's band feather / gradient falloff so a transition
   completes in **≤4 px** instead of 10–30, and raise glass IOR dispersion contrast rather than
   emitter count. Test: **grad>40 ≥ 0.025**, **grad>20 ≥ 0.070**, and the bar-4 cut at y=1050 must
   fall from above L 140 to below L 40 within **30 px** at its right edge (currently 250 px of
   plateau, then a cliff only at the silhouette).

2. **Let the faces go quiet. Restore large flat areas.** — **MUST for 8.5.**
   Flat-block fraction on bar 1's face is **0.140** against v1's **0.480**. v1 wins by being calm
   over most of the surface and violent in a few places; v2_42 is mid-contrast everywhere. Reduce
   the panel's *coverage* on bar 1 and bar 4 so each face carries **at most three lit events with
   near-black or near-uniform between them**. Test: **flat-block frac ≥ 0.35** on both
   (150,250)–(340,800) and (430,930)–(660,1250), with mean L on lit held at **64–72**. This works
   with change 1, not against it: fewer, sharper events.

3. **Mask the lozenge corner. Seventh round, fourth dim.** — **MUST for 8.5.**
   360 px at peak L 73 at x 875–919, y 1271–1303, plus a 505 px tail at (897,1306)–(948,1325). It
   still ignites **9 → 42 in 4 px** and it is still a detached spectral sliver on black. The soft
   hole took 16% off its area. Dimming has now failed four times. **Mask bar 5's lower-left corner
   from the back panel entirely**, or set the panel's bottom-left band to zero emission. Test:
   **zero components over 150 px in (830,1230)–(970,1345)**, nothing there above L 40.

4. **Rejoin bar 5 to the main body, and kill the 254 px debris.** — **MUST for 8.5.**
   Bar 5 is still its own connected component (35,993 px, x 925–1141) four rounds after the note.
   At 100% the elbow at (920,1230) reads as a break in the letterform — it is now the most visible
   compositional fault in the frame, ahead of any artifact. Separately, the debris at
   x 1033–1053, y 750–774 (254 px, peak L 56, 74 px above threshold) is three square-cut red
   rectangles in black and is unchanged for three rounds; the gate that killed the chip should
   reach it. Test: **one connected component containing both bar 5 and bars 2/4** at the max(R,G,B)>25
   threshold, and **no component over 100 px in (1010,730)–(1080,800)**.

5. **Diagnose the crown slats properly before rotating the panel again.** — **MUST for 8.5.**
   Three straight ribbons, 6–12 px wide, still run off bar 1's crown at (85,175)–(410,275) with
   true black between them, and the crown-box peak went **115 → 147**. They survived a 22° rotation
   still parallel to the crown edge, which means they are probably **not** the band panel. Render an
   isolation pass with the panel removed before touching the angle again. This is the object the
   user circled, four rounds ago. Test: **no straight run above L 90 longer than 120 px** in
   (85,170)–(410,280), and **no lit component more than 12 px clear of the silhouette** in that box.

6. **Add depth-of-field and a real surface pass.** — **nice-to-have, but it is the user's own note.**
   Two things from `v1_annotated` that have never been attempted in nine rounds. (a) The peanut sits
   furthest back and renders at the same sharpness as bar 4 in front; both `ref_ring` and
   `ref_puck` carry visible DoF. A light defocus on the peanut and a touch on bar 1 would deliver
   "more dynamic realistic compositing" in one change. (b) Dust and smudge: hf residual is 3.38
   against v1's 5.93 and ring's 6.61, and what hf you have is **chroma noise in the black**, not
   surface detail. Raise denoiser strength on the background so the corner max drops below 3, then
   add a low-amplitude scratch/fingerprint map on the glass at roughness 0.03–0.06. Target hf
   residual **4.5–5.5 measured on lit pixels only** with corner max unchanged.

SCORE: 8.2
