# v2_24_hq — adversarial review

Bar numbering as before: **1** = tall left upright, **2** = tall centre upright, **3** = short slab
/ elbow under bar 1, **4** = lower-centre slab, **5** = lower-right slab. **Peanut** = top-right
figure. Coordinates are pixels in the 1440×1440 render, origin top-left.

**Verdict up front: the comb is dead.** Both named sites are clean. That is the fault the user
circled on v1, it survived four revisions, and it is now genuinely gone — verified by 500–700%
crop against v2_22, not by eye on the full frame.

**And nothing else moved.** Mean |gradient| on lit pixels is **4.14** in v2_24 and **4.14** in
v2_22 — identical to two decimals. The ripple bought zero. The three reflection cards bought zero.
The panel push-back bought zero. A pixel diff shows the entire change is confined to bar 1's right
flank and bar 3; the peanut, bar 5 and bar 4 are within noise of the previous render. One fault
fixed, one fault of equal weight left standing (the bar-5 lozenge), and the gating problem —
detail density — untouched.

Priority 1 mostly passes. Priorities 2, 3, 4 stand still.

---

## 1. Artifact check by location

### Scan — connected components, max(R,G,B) > 25

**1968 components. Three bodies.** 306,842 (bars 2+4+5, x 489–1153, y 118–1326); 294,385
(bars 1+3, x 77–749, y 170–1334); 133,619 (peanut, x 991–1315, y 58–676).

Largest stray **363 px** at **x 761–805, y 745–767**. v2_22's largest was 848 px. Every stray
above 100 px checked individually:

| px | bbox | verdict |
|---|---|---|
| 363 | x 761–805, y 745–767 | **explicable.** Crop (720,710)–(860,800) at 500%, 2× exposure: a continuous red thread lying *on* bar 2's lower-right shoulder silhouette, the red half of an edge fringe whose blue half dips under threshold. Attached, follows the curve. |
| 315 / 295 / 211 / 164 / 90 / 83 | x 388–417, y 323–578 | **explicable.** Crop (360,300)–(440,600) at 500%, 2.5× exposure: one continuous green-core / blue-skirt dispersion fringe down bar 1's right edge, dashed only because the green dips below 25. Correct behaviour. |
| 205 | x 508–536, y 864–877 | sub-threshold sampler noise above bar 4's crown. Invisible at normal exposure. |
| 112 / 45 | x 1073–1093, y 792–816 | bar 5's left chromatic fringe, same mechanism as above. |

**No unexplained objects in black. Priority 1's scan test passes.**

### Bar 1 crown — **FIXED**

Crop **(150,150)–(350,330) at 500%**, side by side with v2_22.

v2_22: a picket of hard 2–6 px vertical stripes — white, red, magenta, cyan — running along the
top bevel from x≈245 to x≈330, every one terminating on the same horizontal line with a **square
blunt end**.

v2_24: **one continuous white-to-cyan bevel band**, graded over 8–14 px, curving with the crown
and fading into the magenta flank. No stripe. No square termination anywhere in the crop. The
5× kicker widening was the right diagnosis and the right fix.

### Bar 3 upper-left rim — **FIXED**

Crop **(230,790)–(410,900) at 700%**.

v2_22: fifteen-odd hard vertical pickets, red / magenta / white / yellow, 2–5 px, all cut off on
one straight horizontal line at y≈868.

v2_24: **a single broad graded rim band**, cream through yellow to white, with the transitions
spread over 10–25 px. Measured across the field (255–330, 795–860): mean 161, **sd 34** — the
variation is smooth gradient, not stripe. The comb is gone at 700%.

Cost, and it is real: the band is now **75 px wide and near-white**. Where v2_22 had a bad bright
edge, v2_24 has a large pale field. It is no longer an artifact; it is now a flat area. See §3.

### Bar 5 corner throw — **NOT FIXED. Now the worst thing in frame.**

Crop **(840,1240)–(950,1330) at 800%**. Pixel diff against v2_22 over this region: **1.69 mean**,
i.e. nothing changed. The 0.25 m panel push-back did not reach it.

What is on screen is a **striped lozenge lying in black**, long axis running roughly
(865,1305) → (925,1262), about 22 px across. Luma profile across the short axis at y=1288:
`0 8 29 71 132 147 137 95 14 1` — a solid bar with a defined edge, not a fan. Along the long axis
at x=880: `0 5 21 96 136 82 7 1` — it **starts and stops**, it does not fade.

The bands inside it run red / yellow / green / cyan in even parallel strips with 1–3 px
boundaries, and the far end at ≈(925,1262) is a **square cut**. It touches the body at one corner
and is otherwise surrounded by black. A viewer cannot attach it to any geometry. It reads as a
sticker. Everything I wrote about this last round applies verbatim, because nothing was done to it.

### Bar 4 right edge, the "motes" — **NOT FIXED**

Crop **(650,1050)–(770,1150) at 600%**. The change note says motes are now pure black occluders,
roughness-only. The blobs at **(692–712, 1055–1130)** are still there and still **bright saturated
orange, 12–25 px, brighter than the vermilion they sit on** (peaks 200+ against a 110 field).
Whatever those are, they are not the motes that were changed, and they still read as blown
pixels rather than as dirt. Speck census confirms nothing moved: 789 dark specks / 534 bright
specks in v2_24 against 793 / 527 in v2_22.

### Peanut — clean

No strays, no comb, no terminations. Crop (1190,110)–(1330,470) at 400% is artifact-free. It is
also the most featureless element in the frame; that is a §2 problem, not a §1 problem.

### Measured plate

Peak **255**, **0.1395%** > 250 (your 0.11% is on a luma mask; on max(R,G,B) it is 0.14 — both
fine). Background over four 60 px corner patches: mean **0.89**, sd **1.44**. Correct.

---

## 2. Glass realism — **6.3 / 10**

Up 0.3 on the bevels alone. Everything else is flat, literally.

- **Detail density did not move. At all.** Mean |grad| on lit pixels: **v2_22 4.14, v2_24 4.14**.
  Strong-edge fraction (|grad| > 20): **0.030 → 0.030**. Against **v1 = 8.36 / 0.137**,
  `ref_ring` = 5.08 / 0.059, `ref_abstract` = 9.15 / 0.121. The 0.5 mm / 12 cm ripple is either
  too shallow or too coarse to produce an optical event at this focal length — at 12 cm scale on
  a 0.42 m slab you get roughly three undulations across a face, which is a slow bend, not a
  caustic. The three reflection cards are not visible as reflections anywhere I can find them.
- **No back bevel is readable through the front face, anywhere.** I accept the solid-cast brief
  and I am not asking for a shell. But a solid tilted slab *must* show its rear bevel ring as a
  second contour inside the silhouette on the faces that are angled toward camera, and v1 — same
  solid brief — does exactly that on every edge. Crop (1190,110)–(1330,470) at 400% on the
  peanut: one silhouette edge, then 35–50 px of smooth green-to-cyan, then blue. Crop
  (470,370)–(610,700) at 400% on bar 2: parallel 25–35 px colour bands, no line. The rear bevel
  is either being washed out by the transmission colour or the back faces are not receiving
  anything to refract. That, not hollowing, is the ask.
- **The bevel fix traded a comb for a plateau.** Bar 3's rim is now a 75 px near-white field. Real
  perspex at a rolled edge gives a *thin* hot line with dark immediately beside it — see
  `ref_ring`, where the outer roll is 4–8 px at this scale.
- **Flat blocks got slightly worse where the change landed.** Of 364 40×40 blocks with >90% glyph
  coverage, **6 are under sd 2.0 and 17 under sd 3.0** (v2_22: 7 and 17). Two *new* flat blocks
  appeared inside the area the ripple was supposed to fix: **(240,240) sd 1.7** and
  **(240,280) sd 1.8**, both on bar 1. And **(320,760)** got flatter, **1.8 → 1.1**. The peanut's
  green dome still reads **(1080,240) sd 2.0**.
- In credit: bar 1's crown and bar 3's rim are now the two cleanest bevels in the series, and the
  dispersion fringing along bar 1's right edge and bar 5's left edge is textbook.

## 3. Style match to v1 and refs — **5.5 / 10**

Unchanged. Nothing in this revision addressed it.

- Mean saturation on lit pixels: **v2_24 0.763**, v1 **0.821**, `ref_ring` **0.367**. Saturation is
  not the problem; **distribution is**. v1 concentrates its colour in narrow ribbons over a dark
  body. v2_24 spreads it wall to wall. Lit area: **v2_24 35.8%** of frame, **v1 26.4%** — v2_24 is
  a bigger, flatter, brighter shape.
- Strong-edge fraction **0.030 against v1's 0.137** — under a quarter. This single number is the
  style gap.
- v1's speculars are 3–5 px gold points scattered along edges. v2_24 has none of those. Its
  highlights are 100–400 px fields.
- The bevel fix moved this *slightly the wrong way*: the comb was ugly but it was high-frequency.
  Replacing it with a smooth 75 px band removed edge energy from the exact place v1 has most of it.
- Neither v1 nor any of the three refs is a rainbow object. `ref_ring` sits at sat 0.37 and gets
  its life from contrast, not hue count. v2_24 is still a rainbow poster.

## 4. Compositing — **7.0 / 10**

Unchanged from v2_22, and still the strongest category.

- Grain, clip share (0.14% > 250) and veiling glow all correct.
- No geometric flare left in frame. Nothing is a straight constant-width bar except the bar-5
  lozenge, which is a refraction artifact, not a flare.
- Defocus depth cue holds on the peanut and bar 5's rear edges.
- Still missing: atmospheric falloff front-to-back, size-graded bloom, and kicker cores that clip
  only at their brightest 20% rather than along their whole run. All three were listed last round
  and none was attempted.

## 5. OVERALL — **7.3 / 10 — REJECTED**

Up 0.3. The circled fault is closed and that is worth real credit. But three of the four changes
made this round are unmeasurable in the output, and the two artifacts I ranked 2nd and 6th last
time are pixel-for-pixel unchanged. The gap to 8.5 is still one number: **strong-edge fraction
0.030 against v1's 0.137.** Until the body has high-frequency optical structure on it, this reads
as a coloured shape, not as photographed perspex.

---

## 6. Ranked changes

1. **Make the ripple actually produce events — it is currently invisible.** 0.5 mm at 12 cm gives
   ~3 undulations across a 0.42 m face and a surface-slope change of about 0.05°, which refracts
   nothing. Go to **two octaves: 0.8–1.2 mm at 2.5–4 cm, plus 0.3 mm at 0.8–1.2 cm**, applied as
   a normal/bump perturbation rather than displaced geometry so the silhouette stays clean. Test,
   and do not ship without it: **mean |grad| on lit pixels must rise from 4.14 to ≥ 6.5** and
   **strong-edge fraction from 0.030 to ≥ 0.060** (`ref_ring` is 5.08 / 0.059; v1 is 8.36 / 0.137).
   If the number does not move, the change did not happen — that is the lesson of this round.

2. **Kill the bar-5 lozenge. Stop trying to fix its shape.** It survived a 0.25 m push-back with a
   mean diff of 1.69 over its own bounding box, so the panel is not the lever. Either remove the
   back panel's bright band from the solid angle that corner sees, or **mask that one corner's
   contribution**. Test: at 800% on crop (840,1240)–(950,1330) there must be **no object with two
   parallel straight sides and a square end** lying in black. Anything left there must fade to
   background over ≥ 25 px and must widen visibly away from the corner.

3. **Get the back bevel to read through the front face.** Not a shell — the rear bevel ring of the
   solid slab. Likely causes in order: transmission colour too saturated to carry the second
   surface (drop absorption density **40–50%** and see if the contour appears), or the back bevel
   radius too large to catch a distinct highlight (reduce it to **60–70%** of the front bevel).
   Test: 400% crops at **(1250,150)–(1300,450)** on the peanut and **(500,400)–(560,700)** on
   bar 2 must each show **two distinct contour lines 4–12 px apart**. This is the single biggest
   realism lever and it has now been open for three rounds.

4. **Narrow the new bevel bands.** Bar 3's rim is a 75 px near-white plateau and bar 1's crown is
   a 40 px one. Real rolled perspex gives a **4–10 px hot line with a dark channel beside it**.
   Bring the widened kickers back to **2–2.5× their original width, not 5×**, and recover the
   picket-free result by raising transmission samples instead. Test: rim highlight width
   ≤ 15 px at (255–330, 795–860), with luma dropping below 60 within 10 px of its edge, and still
   no square stripe termination at 700%.

5. **Fix the orange blobs at (692–712, 1055–1130) — they were reported fixed and are not.**
   They are 12–25 px, peak 200+, on a 110 vermilion field, and they are the same pixels as v2_22.
   Find what is actually generating them (it is not the mote pass), then make every contaminant
   **achromatic and 25–40% darker than its surround**, 4–10 px, roughness-driven only.

6. **Break the six flat blocks, two of which this round created.** Under sd 2.0:
   **(320,760) sd 1.1**, **(440,1040) sd 1.4**, **(440,1080) sd 1.7**, **(240,240) sd 1.7**,
   **(240,280) sd 1.8**, **(1080,240) sd 2.0**. Target **zero blocks under sd 2.0 and none under
   sd 3.0 on the peanut**. Change 1 should carry most of this; check the peanut's green dome
   specifically, which has been flat for three rounds running.

SCORE: 7.3
