# v2_27_hq — adversarial review

Bar numbering as before: **1** = tall left upright, **2** = tall centre upright, **3** = short slab
/ elbow under bar 1, **4** = lower-centre slab, **5** = lower-right slab. **Peanut** = top-right
figure. Coordinates are pixels in the 1440×1440 render, origin top-left.

**Verdict up front: real progress, and one change that went backwards.**

Two named faults are genuinely closed. The orange blobs on bar 4 are gone — 108 blob pixels in
(692–712, 1055–1130) in v2_24, **0** now, peak 179 → 82. Stray component count halved,
**1968 → 998**, largest stray 363 → 298 px. The absorption cut and the vignette did what the tone
needed: the dark-body fraction on lit pixels moved **0.242 → 0.280** against v1's **0.297**, and
saturation **0.763 → 0.790** against v1's **0.821**. Those are the first numbers in this series to
land inside v1's neighbourhood.

**But the ripple bought mid-frequency wobble by spending high-frequency structure.** Every
strong-edge measure fell:

| grad threshold | v2_24 | v2_27 | v1 | ref_ring |
|---|---|---|---|---|
| >20 | 0.0458 | **0.0449** | 0.1814 | 0.0823 |
| >30 | 0.0217 | **0.0190** | 0.1038 | 0.0531 |
| >40 | 0.0132 | **0.0108** | 0.0574 | 0.0371 |
| >60 | 0.0055 | **0.0040** | 0.0187 | 0.0177 |

Mean |grad| rose 6.93 → 7.26 because *all* the added energy sits in the 1–20 band. That is the
lesson of this round and it is the mirror of last round's: **mean |grad| is the wrong dial.** It
can be raised by noise. Use `grad>20` from here on.

---

## 1. Artifact check by location

### Scan — connected components, max(R,G,B) > 25

**998 components (v2_24: 1968). Three bodies.** 305,549 (bars 2+4+5, x 489–1160, y 118–1325);
289,869 (bars 1+3, x 77–759, y 170–1333); 133,961 (peanut, x 991–1320, y 58–675).
Background over four 60 px corner patches: mean **1.33**, sd **1.83**, max **6**. Clean.

Every stray above 30 px:

| px | bbox | verdict |
|---|---|---|
| 298 | x 761–797, y 745–766 | **explicable.** Was 363. The red half of bar 2's shoulder fringe, blue half sub-threshold. Attached to and following the silhouette. |
| 88 | x 93–100, y 371–400 | **explicable.** Bar 1's left silhouette fringe, dashed by the threshold. |
| 60 | x 511–531, y 865–871 | sub-threshold sampler noise over bar 4's crown. Invisible at exposure 1. |
| 52 / 48 / 48 / 47 / 41 / 37 | x 396–412, y 287–551 and x 103–109, y 417–433 | **explicable.** The same dispersion fringe down bar 1's right edge, broken where green dips under 25. |
| 45 | x 795–807, y 740–748 | continuation of the 298 px fringe. |
| **36** | **x 352–367, y 186–190** | **NOT explicable.** Crop (290,180)–(400,300) at 800%, 1.8× exposure: a thin flat **red sliver, 16 × 5 px, lying in pure black** about 30 px clear of bar 1's rear top edge, with nothing joining it to any geometry. Small, but it is the one object in frame a viewer could point at and call a mistake. |

### Bar 4 right edge, the orange blobs — **FIXED**

Crop **(640,1040)–(780,1160) at 600%, 1.6×**. The saturated orange lumps are gone. What is there
now is a clean vermilion field carrying fine dark vertical striation — and that striation is the
best-looking surface in the render. It reads as brushed cast acrylic, exactly the "real glass with
subtle dust/smudge" the user asked for. **Do this everywhere.**

### Bar 1 crown and bar 3 rim — comb still dead

Crop **(150,150)–(350,330) at 500%** and **(290,180)–(400,300) at 800%**: no pickets, no square
stripe terminations, clean graded bevel bands. Four rounds on, that stays closed.

Bar 3's rim plateau was only half addressed. Crop (230,790)–(430,910) at 500%: still a near-white
field roughly **70 px wide**; block (320,760) measures sd **2.1** at mean **164**. Narrower than
before, still a plateau where `ref_ring` puts a 4–8 px hot line.

### Bar 5 corner throw, the lozenge — **improved, not closed**

Crop **(830,1230)–(960,1340) at 700%, 2×**, side by side with v2_24.

It is shorter and its long sides are softer — the cross-section at y=1288 now ramps
`25 43 80 84 … 146 148 … 99 77 39 15`, about **10 px of ramp** each side against v2_24's 4 px. The
free end has picked up a green fray.

It still fails the test I set. Along the long axis at x=870 it reads
`… 1 2 4 1 40 35 27 25 42 32 62 79 95 … 107 105 97 81 42 2` — it **begins and ends**, over 3 px at
the free tip near **(868,1305)**, not over the ≥25 px I asked for. The far cap at ≈(925,1262) is
still square. It is still a striped object lying in black that a viewer cannot attach to anything.

### The three kicker streaks — **the worst thing in frame now, and unflagged until this round**

Crop **(1050,1180)–(1220,1320) at 500%**. The white streak off bar 5's lower-right corner is a
**perfectly straight, constant-width bar with two square ends**. Row scans across it at y = 1210,
1230, 1250, 1270 each show a run of **6–12 consecutive pixels at exactly 255**. **493 pixels at
≥250 inside that one 170×140 box.** It clips along its *whole* length, not at a core.

That is the same failure mode as the lozenge — two parallel straight sides, square termination,
constant width, lying in black — and it is repeated on bar 4's lower right (≈700,1230) and below
the peanut (≈1250,620). v1's speculars in the same role are **3–5 px gold points**. I did not hold
this to account in earlier rounds; at this level of finish it is now the loudest tell that the
frame was drawn rather than photographed.

### Peanut — clean, and empty

Crop (990,60)–(1330,400) at 300%: zero artifacts. Also zero optical event. Four poster-flat fields
of green, yellow and blue, a soft magenta rim, and one 900 px stretch of silhouette with no
contour inside it. §2 problem, not §1.

### Measured plate

Clipped (L>250) **0.112%**; lit fraction **35.3%** (v1 26.4%). Both fine.

---

## 2. Glass realism — **6.8 / 10** (was 6.3)

- **The tone finally moved.** Mean luma on lit pixels 81.9 → **74.8** (v1 67.3), dark fraction
  0.242 → **0.280** (v1 0.297), L>200 share 0.008 → 0.007. Cutting absorption 0.30 → 0.16 did not
  make it milkier as I feared; combined with the vignette it deepened the body. Keep this.
- **The ripple is not producing optical events.** Crop (480,380)–(620,720) at 400% on bar 2 against
  the same edge in v1 at (800,630)–(1030,1200): v1 gives a bright 3 px rail, a **black channel**,
  a second rail, then chromatic fringes — four separate contours inside 40 px. v2_27 gives one
  soft 50–60 px cyan-to-green gradient with **ragged pixel-scale fuzz on the colour boundaries**.
  That fuzz is what the two octaves bought. It reads as sampler noise and posterisation, not as
  a surface. This is why grad>40 fell 0.0132 → 0.0108.
- **No rear bevel reads through the front face anywhere.** Third round open. The absorption cut was
  the right thing to try and it was not the cause. Peanut crop (1230,140)–(1330,460) at 500%:
  one silhouette, then 40 px of smooth green, then blue. No second line.
- **The dark channel is the missing ingredient, not more colour.** Every real perspex edge in the
  refs puts *black* immediately beside its hot line. v2_27 never does.
- **I was over-weighting flat blocks and I am dropping it.** v2_27 has 4 blocks under sd 2.0 and 14
  under sd 3.0; **v1 has 6 and 14**. v1 is just as locally flat. It wins on rails, not on texture.
  The peanut's green dome (1080,240) is out of the bottom ten for the first time.
- In credit: bar 4's striated vermilion field, and the dispersion fringing on bar 1's right and
  bar 5's left edges, are both photographic.

## 3. Style match to v1 and refs — **6.0 / 10** (was 5.5)

- Saturation 0.763 → **0.790** against v1 **0.821**; dark fraction within 0.017 of v1. The tone
  half of the style gap is close to closed.
- The structure half is not, and it widened. **grad>20: 0.0449 against v1's 0.1814** — a factor of
  **4.0**, and worse than v2_24's 0.0458. `ref_ring`, which is the *least* structured reference, is
  0.0823 — still nearly double this render.
- v1's identity is a near-black body crossed by thin bright ribbons. v2_27 is still wall-to-wall
  colour with soft boundaries: lit area 35.3% against v1's 26.4%.
- The kicker streaks have no counterpart in v1 or any of the three refs.

## 4. Compositing — **7.2 / 10** (was 7.0)

- **The vignette worked.** Corner throws fade out instead of ending. That specific complaint is
  closed.
- Grain, background floor (mean 1.33, sd 1.83) and clip share 0.112% are all correct.
- Still open, and listed for the third round: **kicker cores clipping along their entire run**
  (493 px at ≥250 in one streak, 6–12 px wide at 255), square streak ends, no size-graded bloom,
  no front-to-back atmospheric falloff.

## 5. OVERALL — **7.7 / 10 — REJECTED**

Up 0.4. Two artifacts closed for real, the component count halved, and the tone distribution is
inside v1's neighbourhood for the first time in the series. That is the most honest round of work
so far. It is rejected because the one metric that separates this from v1 moved the **wrong way**,
and because the frame contains three straight, square-ended, fully-clipped white bars that I
should have called out earlier and am calling out now.

---

## 6. Ranked changes

1. **Build the dark channel. Stop adding ripple.** — **MUST for 8.5.**
   Two octaves of normal perturbation raised mean |grad| and *lowered* grad>40. More of it will
   lower it further. What v1 has and this does not is a **thin bright rail with black immediately
   beside it**. Get it from the lighting, not the surface: replace the smooth back panel with
   **4–6 narrow bright bars, 2–4 cm wide, on a near-black field, separated by gaps ≥ 3× their
   width**. A rounded bevel maps a hard light/dark boundary into a thin rail with a dark channel.
   Test: **grad>20 on lit pixels must reach ≥ 0.11** (now 0.0449; `ref_ring` 0.0823; v1 0.1814) and
   **grad>40 ≥ 0.030** (now 0.0108). Ignore mean |grad| entirely from here.

2. **Fix the three kicker streaks.** — **MUST for 8.5.**
   Each is a constant-width bar of pure 255 with square ends: 6–12 px at 255 across every row,
   493 px ≥250 in the (1050,1180)–(1220,1320) box alone. Same fault on bar 4 at ≈(700,1230) and
   below the peanut at ≈(1250,620). Taper each to a point over its last 20% of length, vary its
   width between **2 and 8 px** along the run, and cap clipped pixels at **≤ 100 per streak,
   confined to the brightest 20% of its length**. Test: no row scan may show more than 6
   consecutive pixels at 255, and no streak end may be square at 500%.

3. **Kill the bar-5 lozenge.** — **MUST for 8.5.** Fourth round.
   The soft side ramps helped; the ends did not. Test unchanged and unmet: at 800% on
   (830,1230)–(960,1340) nothing may **begin** in under 25 px (it currently goes 1 → 40 → 95 in
   3 px at (868,1305)) and nothing may have a square cap (it still does at ≈(925,1262)). Mask that
   one corner's view of the panel rather than trying to reshape the throw.

4. **Get the rear bevel to read.** — **MUST for 8.5.**
   Absorption was not the lever; the bevel radius is the next candidate. Take the **back** bevel to
   **60–70%** of the front bevel radius so it catches its own distinct highlight. Test: 400% crops
   at **(1250,150)–(1300,450)** on the peanut and **(500,400)–(560,700)** on bar 2 must each show
   **two distinct contour lines 4–12 px apart**, with luma dropping **below 40** between them.
   Change 1 makes this much easier; do 1 first.

5. **Remove the red sliver at x 352–367, y 186–190.** — **must** if it is a light or geometry
   escaping, **nice-to-have** if it is a legitimate sub-threshold fringe. Diagnose before deciding:
   a 16 × 5 px red flake 30 px clear of the nearest geometry with no path back to it is the kind of
   thing a client circles. Test: no component over 30 px may sit more than 10 px from a body.

6. **Spread bar 4's striation to every face.** — **nice-to-have**, and cheap.
   The fine dark vertical striae in (640,1040)–(780,1160) are the single most convincing surface in
   the render and exactly the "subtle dust and smudge" note. The peanut has none. Apply it at the
   same amplitude across all faces, and hold the tone where it is — do **not** cut absorption
   below 0.16, it has landed correctly at dark fraction 0.280 against v1's 0.297.

SCORE: 7.7
