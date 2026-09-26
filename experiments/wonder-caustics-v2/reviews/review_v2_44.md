# v2_44_hq — adversarial review

Bar numbering as before: **1** = tall left upright, **2** = tall centre upright, **3** = short slab /
elbow under bar 1, **4** = lower-centre slab, **5** = lower-right slab. **Peanut** = top-right figure.
Coordinates are pixels in the 1440×1440 render, origin top-left. v1 and `ref_ring` are resampled to
1440×1440 for every comparison, and every number below is measured with the same operator across all
four images in this session.

**Verdict up front: the change you made is not the change I asked for, and the frame moved
backwards.** The feather cut from 0.18 to 0.07 was supposed to buy hard boundaries. Measured,
**grad>40 went 0.0112 → 0.0110.** That is zero. Meanwhile the duty cut to 0.35 removed 9% of the lit
area and, instead of leaving black calm between events, it shredded what was left: **flat-block
fraction on bar 4 fell from 0.077 to 0.030** against v1's 0.387. Component count rose 767 → 940. The
lozenge got **bigger and brighter** on its eighth round. And bar 5 has begun to shed a new 1034 px
filament. Two real gains: mean L now lands on v1 exactly, and the crown slats are dimmer.

---

## 1. Artifact check by location

### Scan — connected components, max(R,G,B) > 25, 8-connected

**940 components** (v2_42: 767, v1: **461**). Up 23% — the first rise in four rounds. Four bodies
over 10,000 px:

| px | bbox | body | v2_42 |
|---|---|---|---|
| 232,054 | x 82–736, y 171–1332 | bars 1 + 3 + 4 | 238,349 |
| 151,622 | x 492–931, y 125–1189 | bar 2 + diagonal | 176,172 |
| 78,540 | x 991–1300, y 73–674 | peanut | 95,329 |
| **27,908** | **x 932–1141, y 942–1305** | **bar 5 — still severed** | 35,993 |

**v1 has three bodies. Bar 5 is inside the same component as bars 2/4 there.** Here it is its own
object for the **fifth** round running, and it *shrank* 35,993 → 27,908 px — the duty cut took 22%
off it, so the elbow gap at (920,1230) is wider than last round, not narrower.

Every stray 30–10,000 px:

| px | bbox | peak L | verdict |
|---|---|---|---|
| 1918 | x 647–688, y 887–1025 | **24** | CLOSED, holding. The old plume, still under threshold. |
| **1034** | **x 1041–1060, y 771–898** | **68** | **NEW. Worst artifact in the frame. See below.** |
| 687 | x 1221–1249, y 117–192 | 50 | explicable — peanut rear bevel. Still the best surface here. |
| **510** | **x 868–917, y 1269–1306** | **79** | **The lozenge. Eighth round, and it grew.** |
| 401 | x 1097–1159, y 58–70 | 19 | sub-threshold at display gamma. Fine. |
| **387** | **x 1233–1264, y 461–489** | **79** | **NEW. Detached bright chip off the peanut's lower right.** |
| 315 | x 1226–1246, y 197–237 | 24 | fine. |
| 307 | x 327–354, y 866–902 | 32 | rim dash at the bar 1/3 elbow. Borderline. |
| **244** | **x 1032–1053, y 752–773** | **52** | **The red debris. Unchanged. Fourth round.** |
| 212 | x 1276–1292, y 474–508 | 36 | explicable — second peanut rear-bevel segment. |
| 195 | x 897–933, y 1313–1324 | 37 | lozenge tail remnant. |
| 170 / 158 / 134 / 69 / 58 / 40 / 39 / 39 / 34 / 32 | rim and bevel runs | ≤46 | explicable fringes. |

### The new 1034 px filament at (1041,771)–(1060,898) — **NEW, and it is the headline**

Crop **(1000,730)–(1090,910) at 600%, native gamma.** Peak **68**, 127 px long, 20 px wide, tapering.
It is a thin cobalt ribbon running down into black off bar 5's upper-left edge, capped at its head by
the three square-cut red rectangles that have been sitting at (1032,752) for four rounds. Read the
two together: **the old "debris" was the head of this thing and it has now grown a 130 px tail.** It
lies in pure black with no geometry within 40 px of it. It is not a rim, not a bevel, not a
refraction of anything the viewer can see. This is a worse object than the lozenge because it is
long, directional, and points at nothing.

Box (1030,765)–(1070,900): max **68** (v2_42: 54), mean 3.8.

### The bar-5 lozenge — **STILL OPEN. Eighth round, and it got worse.**

Crop **(820,1230)–(980,1350) at 500%.** It is now a single bright green-white sliver, sharper than
last round and lying in a wider field of black because the duty cut darkened bar 5's corner around it.

- 360+505 px → **510+195 px**; peak L **71 → 79**.
- Long axis at x=890, y=1265→1315 every 2 px: `0 1 0 2 1 0 2 0 4 1 14 19 59 53 47 29 12 6 4 4 0 0 3`
  — it ignites **4 → 59 in 8 px** and terminates in 10 px. Same failure mode, eighth time.
- My standing test is **zero components over 150 px in (830,1230)–(970,1345), nothing above L 40.**
  You are at two components, 510 px and 195 px, peak L 79.

The soft hole did not work, and the brief says a larger hole darkens bars 4 and 5 unacceptably. Then
the hole is the wrong instrument. **Cut it in the render, not in the light** — this is 510 px in a
known 140×115 box and it has now cost eight rounds. A garbage matte on that box, or a holdout object
between the panel and bar 5's lower-left corner that occludes only the ray path, ends it tonight.

### Crown slats — dimmer, still present. Fifth round.

Crop **(80,150)–(420,340) at 300%.** Crown box (85,170)–(410,280): max **109** (v2_42: 144), mean
17.45 (was 27.66). The 9.5 m panel made them **25% dimmer** — the first movement in four rounds.

They are still three straight ribbons, 6–12 px wide, with true black between them. Vertical profile
at x=120, y=175→270 every 3 px:

```
2 0 0 0 0 | 41 50 0 | 0 0 0 1 | 39 41 15 9 0 | 4 11 34 40 30 20 0 | 3 0 0 0 0 0 0 0
```

The isolation is convincing and I accept the optics: 12,771 lit px with the panel, 298 without, and a
horizontal cylinder draws anything behind it into horizontal streaks. **That explains the object. It
does not excuse it.** Nothing in v1, `ref_ring`, `ref_puck` or `ref_abstract` has a hard-edged ribbon
floating clear of a silhouette into black, and this is the object the user circled. The bevel is
doing what bevels do; the answer is to stop feeding it a bright horizontal target — put a soft
horizontal gradient in the panel at the crown's altitude, or shrink the top bevel radius on bar 1 so
the cylinder's magnification drops.

### Kickers — **CLOSED, holding.** Stop tuning.

Clipped pixels (L≥250) per box, cap 100 each: bar 5 **48**, bar 4 **36**, peanut **86**. All inside
cap, all down from v2_42's 63/44/84 except the peanut which is flat. Background floor is identical
to last round: corner means **0.70–0.74**, max **6.5**. Cleanest in the series, unchanged.

### Measured plate

| | v2_42 | **v2_44** | v1 | ref_ring |
|---|---|---|---|---|
| lit fraction | 0.2662 | **0.2409** | 0.2636 | 0.3257 |
| mean L on lit | 72.3 | **66.2** | 67.3 | — |
| dark frac (L<20 of lit) | 0.1744 | **0.2042** | **0.1263** | — |
| saturation on lit | 0.7995 | **0.8207** | 0.8215 | 0.3671 |
| grad>20 | 0.0527 | **0.0535** | **0.1814** | 0.0823 |
| grad>40 | 0.0112 | **0.0110** | **0.0574** | 0.0371 |
| mean grad on lit | 7.52 | **7.70** | 10.93 | 6.99 |
| clipped L>250 | 0.075% | **0.074%** | 0.034% | 0.000% |
| flat-block frac, bar 1 face | 0.208 | **0.199** | **0.391** | — |
| flat-block frac, bar 4 face | 0.077 | **0.030** | **0.387** | — |
| components ≥30 px | 767 | **940** | **461** | — |

Read rows 5–6 against rows 9–10. **The feather cut produced no measurable sharpening at all**
(grad>40 0.0112 → 0.0110, inside noise), while the duty cut made both faces *less* calm. You now have
v1's mean luma and v1's saturation on a picture with **1/5 of v1's hard events and 1/13 of its flat
area on bar 4.** Every knob you turned moved the two numbers that were already correct.

---

## 2. Glass realism — **6.9 / 10** (was 7.5)

- **Bar 4 is no longer a contour map; it is a thermal image.** Crop **(380,880)–(700,1300) at 200%.**
  Nested chevron isotherms — magenta, cobalt, cyan, lemon, white — in concentric V's, every boundary
  ragged and dithered, chroma grain visible across the whole face. Flat-block 0.030. There is not one
  square inch on that face where the eye can rest. This is the single most damaging surface in the
  frame and it is worse than last round.
- **The dark channels are grey, not black.** Bar 1 at y=600, x 150→420 every 6 px shows a dip at
  x≈222–246 reading `48 48 46 59 53`. v1's same cut has **twenty consecutive true zeros** mid-face
  (`0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0`) before it ignites again to 83/119. v1's calm is *black*
  and its events are violent; yours is mid-grey everywhere with quieter grey between. Making the
  faces darker (mean L 72 → 66) without making the quiet parts actually reach zero bought nothing.
- **Bar 4 at y=1050 still does not terminate.** `42 38 34 57 71 78 51 58 109 144 133 125 124 131 148
  154 164 147 161 137 26 29 25 0 0 0 0` — 200 px of L 109–164 plateau, and the only cliff is the
  silhouette itself. v1: `… 129 135 138 133 128 80 40 0 0 2 16 70 79` — it falls to zero *inside the
  object* and then re-ignites. That is what a thick refracting solid does.
- **No bevel structure reads anywhere.** Compare any edge here to v1's uprights, where you can count
  the outer wall, the inner wall and the far wall through the glass. In v2_44 the silhouette is a
  paper cut-off with one spectral fringe on it. The peanut's rear bevel contour (687 px, peak 50) is
  still the only surface in this project that would pass unremarked next to `ref_ring`.
- **Still no dust, no smudge, no surface.** Ninth round unattempted. `ref_ring` carries hairline
  scratches and specks across its whole face over a clean black; you have clean faces over a grainy
  black, which is exactly inverted.

## 3. Style match to v1 and refs — **6.2 / 10** (was 6.6)

- **grad>40 0.0110 against v1's 0.0574 — a 5.2× gap, unchanged.** Against `ref_ring`'s 0.0371 you are
  3.4× short. Fifteen rounds in, this number has never moved.
- **Hard-to-soft event ratio (g40/g20): v2_44 0.206, v2_42 0.213, v1 0.316, ref_ring 0.451.** It went
  *down*. Your events are more disproportionately soft than last round.
- **Matched and done, again:** saturation 0.8207 vs 0.8215, mean L 66.2 vs 67.3, clipping 0.074% vs
  0.034%. Do not touch colour, exposure or clipping again.
- **Lit fraction now undershoots:** 0.2409 against v1's 0.2636 and ring's 0.3257. The duty cut went
  one step too far — the letterform has started to look eaten rather than dramatic, and it is what
  shrank bar 5 by 22% and widened the elbow gap.
- **Dark fraction is the wrong kind of dark.** 0.2042 against v1's 0.1263: you have *more* near-black
  pixels than v1 and *less* flat area. That combination only happens when the dark is noise and
  ripple rather than quiet surface.

## 4. Compositing — **7.6 / 10** (was 8.3)

- **Background floor holds at the best in the series:** corner means 0.70–0.74, max 6.5.
- **Highlight discipline holds:** 0.074%, three kicker boxes all inside cap.
- **Component count rose 767 → 940** after three rounds of falling. v1 is 461.
- **Bar 5 is still a separate body and the gap grew.** Fifth round on this note. At 100% the elbow at
  (920,1230) reads as a break in the letterform, and it is still the most visible compositional fault
  in the frame.
- **The f/4 defocus does not read.** This was the one genuinely new idea this round and I cannot see
  it. The peanut's rear-bevel contour at (1221,117) is a 687 px component with peak 50 and hard
  edges — it is not softer than bar 4's front face. Measured sharpness on the peanut is indistinguish-
  able from the front slabs. Either the focal distance is wrong or f/4 is far too tight a stop at this
  scale; both `ref_ring` and `ref_puck` show DoF you can see at a glance.
- **Two new detached objects** (1034 px at x 1041–1060, 387 px at x 1233–1264) against one removed.

## 5. OVERALL — **8.0 / 10 — REJECTED**

Down 0.2. I am scoring what is on screen, and on screen this is a slightly worse picture than v2_42
and a long way from v1.

Credit where it is owed: the crown-slat isolation is good engineering and the 9.5 m panel cut their
peak 144 → 109, the first movement there in four rounds. Mean L now lands on v1 within 1.1, the
kickers stayed closed, and the background floor is untouched. None of that is nothing.

But the round's stated purpose failed on its own terms. **Feather 0.18 → 0.07 moved grad>40 by
-0.0002.** Whatever that parameter controls, it is not the thing making your boundaries 10–30 px
wide, so the diagnosis behind this round was wrong and repeating it at 0.03 will not help either. And
the duty cut did active harm: it took 9% of the lit area, 22% of bar 5, widened the elbow break,
pushed the frame under v1's lit fraction, and left bar 4 at **3% flat** — the least restful surface in
fifteen rounds. On top of that, the frame gained a 1034 px filament and a 387 px chip, the lozenge
grew and brightened on its eighth round, and the component count went up for the first time since
v2_32.

**If you change one thing, change what "flat" means.** Stop trying to sharpen the boundaries by
narrowing them and instead **remove most of them.** v1's bar 1 face is 39% blocks of near-identical
pixels and v1's own mid-face cut holds *twenty consecutive zeros*. Cut the number of spectral bands
crossing each face to two or three, make the space between them read **L < 10, not L ≈ 50**, and let
the events that survive be as wide as they like — width has never been the problem, count has. You
have been adding contrast where v1 spends nothing and spending nothing where v1 puts everything.

---

## 6. Ranked changes

1. **Cut the number of events per face, and make the gaps black.** — **MUST for 8.5.**
   Bar 4's face is **0.030** flat against v1's **0.387**; bar 1's is 0.199 against 0.391. Your dark
   channel on bar 1 at y=600 sits at **L 46–59** where v1's sits at **0**. Reduce the band panel's
   band *count* over bars 1 and 4 so each face carries **at most three lit regions**, and drive the
   emission between them to zero rather than to a dim value. Do **not** re-cut the feather; it did
   nothing (grad>40 0.0112 → 0.0110). Test: **flat-block frac ≥ 0.30** on both (150,250)–(340,800)
   and (430,930)–(660,1250), with at least one horizontal cut across each face containing **≥ 15
   consecutive pixels below L 10** strictly inside the silhouette, and mean L on lit held at 64–72.

2. **Kill the new 1034 px filament and the 244 px debris head together.** — **MUST for 8.5.**
   x 1041–1060, y 771–898, peak L **68**, 127 px long, lying in black off bar 5's upper-left edge,
   with the four-round-old red rectangles at (1032,752) as its head. New this round and the most
   alien object in the frame. It reads as a severed sliver of bar 5's edge. Find it by isolation the
   way you found the crown slats — remove bar 5, then the panel, then the rim lights — before you
   dim anything. Test: **no component over 100 px in (1010,730)–(1080,910)**, nothing above L 40.

3. **Matte the lozenge out. Eighth round.** — **MUST for 8.5.**
   510 px at peak L **79**, x 868–917, y 1269–1306, plus a 195 px tail at (897,1313). It grew and
   brightened this round. Four attempts at dimming the light and one at holing the panel have all
   failed, and the brief says a bigger hole costs bars 4 and 5. So stop working in the light path:
   put a **holdout / shadow-catcher plane between the back panel and bar 5's lower-left corner**, or
   matte the box in the compositor. Test: **zero components over 150 px in (830,1230)–(970,1345)**,
   nothing above L 40.

4. **Give the lit area back and rejoin bar 5.** — **MUST for 8.5.**
   Lit fraction fell to **0.2409** against v1's 0.2636, bar 5 shrank 35,993 → 27,908 px, and the
   elbow gap at (920,1230) is wider than last round. Duty 0.35 overshot; take it back to ~0.38 and
   spend the calm you need on change 1 instead (fewer bands, black between) rather than on less
   light. Test: **lit fraction 0.255–0.275** and **one connected component containing both bar 5 and
   bars 2/4** at the max(R,G,B)>25 threshold.

5. **Make the defocus visible, or drop it.** — **nice-to-have.**
   f/4 focused on the front faces produced no measurable softening: the peanut's rear-bevel contour
   at (1221,117) is still a hard-edged 687 px component with peak L 50, as crisp as bar 4 in front.
   Open up to f/1.8–f/2.2 and confirm the focal distance is on bar 4's front face, not the origin.
   This is the user's own "more dynamic realistic compositing" note and both `ref_ring` and
   `ref_puck` carry DoF you can see at 100%. Test: mean gradient on the peanut's lit pixels at
   **≤ 0.6×** the same figure for bar 4's lit pixels.

6. **Surface pass — dust, smudge, hairline scratches — and clean the black.** — **nice-to-have, but
   it is the user's own note and it has never been attempted in nine rounds.**
   The crops show chroma grain in the background and clean faces; `ref_ring` has the exact opposite.
   Raise denoiser strength on the background so the corner max drops below 3, then add a
   low-amplitude scratch/fingerprint map on the glass at roughness 0.03–0.06.

SCORE: 8.0
