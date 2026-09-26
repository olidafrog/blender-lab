# v2_45_hq — adversarial review (final round)

Bar numbering as before: **1** = tall left upright, **2** = tall centre upright, **3** = short slab /
elbow under bar 1, **4** = lower-centre slab, **5** = lower-right slab. **Peanut** = top-right figure.
Coordinates are pixels in the 1440×1440 frame, origin top-left. v1 and `ref_ring` are resampled to
1440×1440. Every number below is measured with one operator across all five images in this pass.

**Operator note.** My component scan this round is 8-connected on `max(R,G,B) > 25` after the
resample, counting bodies ≥ 30 px. It returns lower absolute counts than the operator used in
rounds 39–44 (16 here vs that scan's 940 for v2_44). The *ordering* is what carries: re-measured
with this one operator, v2_42 = 16, v2_44 = 27, **v2_45 = 16**, v1 = 29.

**Verdict up front: the frame recovered, and the headline claim is not true.** Dimming the cards did
remove the two objects that sank v2_44 — the 1034 px filament and the 387 px peanut chip are both
gone — and duty 0.40 put the lit area back on v1. Those are real. But **the dark channel did not
arrive.** On the bar-1 mid-face cut at y=600 the darkest pixel strictly inside the silhouette is
**L 40**, and the longest run below L 10 inside that lit segment is **1 pixel**. The 46 px you
measured is the background gap between bars 1 and 2. And the lozenge, left as optics, is now the
largest and brightest it has been in nine rounds.

---

## 1. Artifact check by location

### Scan — connected components, max(R,G,B) > 25, 8-connected, ≥ 30 px

**16 components** (v2_42: 16, v2_44: 27, v1: 29). Four bodies over 10,000 px:

| px | bbox | body | v2_44 |
|---|---|---|---|
| 235,775 | x 82–736, y 172–1333 | bars 1 + 3 + 4 | 232,054 |
| 169,272 | x 492–942, y 124–1218 | bar 2 + diagonal | 151,622 |
| 90,465 | x 992–1300, y 58–674 | peanut | 78,540 |
| **30,278** | **x 932–1141, y 769–1314** | **bar 5 — still severed** | 27,908 |

**v1 has three bodies. Bar 5 is inside the same component as bars 2/4 there.** Here it is its own
object for the **sixth** round. It did grow back 27,908 → 30,278 px and its bbox climbs from y942 to
**y769**, which is the filament re-attaching rather than disappearing — see below. The elbow gap at
(920,1230) is narrower than last round but still a visible break at 100%.

Every stray 30–10,000 px:

| px | bbox | peak L | verdict |
|---|---|---|---|
| 1955 | x 646–689, y 887–1025 | **23** | CLOSED, holding. The old plume, still under threshold. |
| 1255 | x 1199–1249, y 90–237 | 48 | explicable — peanut rear bevel, now one run instead of three. Still the best surface in the project. |
| **586** | **x 862–916, y 1268–1305** | **84** | **The lozenge. Ninth round. Biggest and brightest yet.** |
| **410** | **x 893–939, y 1307–1324** | **45** | **Lozenge tail. Doubled, 195 → 410 px.** |
| **271** | **x 1032–1052, y 751–773** | **48** | **The red debris head. Fifth round. Unchanged.** |
| 214 | x 1275–1292, y 474–508 | 36 | explicable — peanut rear-bevel segment. |
| 203 | x 627–659, y 852–872 | 22 | sub-threshold at display gamma. Fine. |
| 196 | x 1016–1042, y 713–739 | 17 | sub-threshold. Fine. |
| 45 / 41 / 40 / 32 | rim and bevel runs | ≤ 41 | explicable fringes. |

### The 1034 px filament — **GONE as a free body. Not gone from the picture.**

Crop **(990,700)–(1100,930) at 500%.** v2_44's detached 127 px cobalt ribbon at x 1041–1060,
y 771–898 no longer appears in the stray list. It is now inside bar 5's component, which is why that
bbox reaches up to y769. Region test on (1010,730)–(1080,910):

| | v2_42 | v2_44 | **v2_45** |
|---|---|---|---|
| max L | 54 | 69 | **62** |
| mean L | 3.27 | 2.64 | **3.51** |

So the peak came down 10% and the *mean went up*. The object is dimmer at its brightest and slightly
broader overall. At 100% it no longer reads as a severed sliver in black; it reads as a soft flare
off bar 5's upper-left edge. **My standing test was no component over 100 px in that box: you pass
it — the only survivor is the 271 px debris head at (1032,751), which sits outside the box's own
bright zone and has not moved in five rounds.** Accept the filament as closed. The debris head is
not.

### The bar-5 lozenge — **STILL OPEN. Ninth round, and the core grew again.**

Crop **(820,1230)–(980,1350) at 500%.** It is a single hard-edged green-white sliver lying in pure
black, tilted about 25°, with a soft cyan wash below it. Nothing within 40 px of its upper end.

- Core component: 360 px / peak 72 (v2_42) → 510 / 79 (v2_44) → **586 px / peak 84** (v2_45).
- Tail: 505 / 41 → 195 / 38 → **410 px / peak 45**.
- Long axis at x=890, y 1265→1315 every 2 px:
  `0 1 0 2 2 0 3 1 5 2 17 24 66 61 52 33 14 7 4 4 0 1 3` — it ignites **5 → 66 in 8 px** and
  terminates in 10 px. Ninth time, same failure mode.
- My standing test: **zero components over 150 px in (830,1230)–(970,1345), nothing above L 40.**
  You are at two components, 586 px and 410 px, peak L 84.

**One honest credit.** The box as a whole is quieter than v2_42: region max **182 → 135**, region
mean **18.11 → 11.85**. The card dimming took a third of the energy out of that corner. The bright
core still grew inside it, which is the opposite of what a global dim should do, and tells you the
core is not coming from the cards.

You have chosen to keep it as optics. I understand the reasoning and I still disagree. Physically
correct is not the test. The test is whether a viewer at 100% asks what that is, and this one does —
it is the only hard-edged object in the frame that touches no silhouette. A 140×115 px garbage matte
ends nine rounds of argument in one compositor node.

### Crown slats — **REGRESSED. Sixth round.**

Crop **(80,150)–(420,340) at 300%.** Crown box (85,170)–(410,280):

| | v2_42 | v2_44 | **v2_45** |
|---|---|---|---|
| max L | 145 | 109 | **124** |
| mean L | 27.99 | 17.78 | **20.63** |

The 9.5 m panel bought a 25% dim in v2_44. Dimming the cards gave **16% of it back**. Three straight
ribbons, 6–12 px wide, with true black between them, running clear off bar 1's top-left silhouette
into empty frame. This is inside the circle the user drew on `v1_annotated`. It is the one place in
the picture where a regression is most expensive.

### Kickers and floor — **CLOSED, holding.**

Clipped pixels (L ≥ 250) per box, cap 100 each: bar 5 **60**, bar 4 **53**, peanut **86**. All inside
cap (v2_44: 56/52/92). Whole-frame clipping **0.081%** against v1's 0.036%. Background corner means
**0.65–0.67**, max 5–6, identical to the last two rounds; v1's corners are 0.00 with max 0–1. Your
black is still a faint chroma-grain field where v1's is a true floor, visible in every 300% crop.

### Measured plate

| | v2_42 | v2_44 | **v2_45** | v1 | ref_ring |
|---|---|---|---|---|---|
| lit fraction | 0.2662 | 0.2409 | **0.2570** | 0.2636 | 0.3259 |
| mean L on lit | 72.3 | 66.2 | **68.8** | 67.3 | 119.8 |
| dark frac (L<20 of lit) | 0.1700 | 0.1988 | **0.1859** | **0.1216** | 0.0492 |
| saturation on lit | 0.7995 | 0.8207 | **0.8117** | 0.8215 | 0.3667 |
| grad>20 | 0.0527 | 0.0535 | **0.0471** | **0.1814** | 0.0823 |
| grad>40 | 0.0112 | 0.0110 | **0.0104** | **0.0574** | 0.0371 |
| g40/g20 ratio | 0.213 | 0.206 | **0.221** | 0.316 | 0.451 |
| mean grad on lit | 7.52 | 7.70 | **7.28** | 10.93 | 6.99 |
| clipped L≥250 | 0.082% | 0.081% | **0.081%** | 0.036% | 0.000% |
| flat-block frac, bar 1 face | 0.122 | 0.136 | **0.133** | **0.443** | 0.539 |
| flat-block frac, bar 4 face | 0.052 | 0.038 | **0.046** | **0.398** | 0.588 |
| components ≥30 px | 16 | 27 | **16** | 29 | 7 |
| mean grad peanut ÷ bar 4 | 0.83 | 0.89 | **0.87** | 1.14 | 1.28 |

---

## 2. Glass realism — **7.2 / 10** (v2_44: 6.9, v2_42: 7.5)

- **The dark channel claim fails on measurement.** Bar 1 at y=600, full resolution, no sampling: the
  silhouette runs one unbroken lit segment from **x 195 to x 378**, 184 px wide, minimum **L 40**
  across the whole mid-face, values `26 98 106 96 59 50 46 62 58 80 108 …`. The longest run below
  L 10 inside it is **1 px**. Swept across bar 1's face, rows y 250–800: **0 of 550 rows** carry a
  ≥ 15 px sub-L 10 run inside a lit run. v1 has **45**, and that understates it — v1's channel is so
  dark it *breaks the mask*. v1's same row is **nine separate lit segments** (`103–111, 165–201,
  203–209, 317–346, 351–389, …`) with 108 px of true black between two of them, inside the bar. That
  is the difference in one line: **v1's quiet is an absence of light; yours is a dimmer light.**
- **Bar 4 is still a thermal map.** Crop **(380,880)–(700,1300) at 200%.** Nested chevron isotherms —
  magenta, cobalt, cyan, lemon, white — every boundary ragged and dithered, chroma grain across the
  whole face, flat-block **0.046** against v1's 0.398. It improved 0.038 → 0.046 and that is inside
  noise. There is still nowhere on that face for the eye to rest.
- **Bar 4 at y=1050 still does not terminate.** `24 40 43 43 40 40 37 80 52 75 53 90 146 137 136 136
  134 139 152 157 137 161 93 31 33 28 0 0 0 0` — 220 px of L 134–161 plateau and one cliff, the
  silhouette. v1: `0 2 0 0 5 5 126 0 54 103 … 133 129 81 41 0 0 3 17 71 79` — it hits **zero twice
  inside the object** and re-ignites. That is what a thick refracting solid does and it is the single
  most diagnostic number in this file.
- **f/2.8 is still invisible.** Peanut mean gradient on lit **6.44**, bar 4 **7.38** — a ratio of
  **0.87**, against 0.89 at f/4. The target was ≤ 0.60. Opening a stop and a half moved it 0.02.
  Either the focal distance is not on the front faces or the sensor/lens scale makes f/2.8 an
  infinite-depth stop here. In v1 the peanut is *sharper* than bar 4 (1.14) and in `ref_ring` the
  falloff is obvious at a glance.
- **The peanut rear bevel is still the one good surface.** 1255 px at peak 48, now a single clean run
  instead of v2_44's three fragments. It is the only edge in this project that would sit unremarked
  next to `ref_ring`. Everywhere else the silhouette is a paper cut-off with one spectral fringe on
  it, and you cannot count outer wall, inner wall and far wall through the glass the way you can in
  v1's uprights.
- **Ninth round with no surface pass.** `ref_ring` carries hairline scratches and dust specks across a
  clean black. You have clean faces over a grainy black. Still inverted.

## 3. Style match to v1 and refs — **6.6 / 10** (v2_44: 6.2, v2_42: 6.6)

- **Tone and colour: matched, done, do not touch.** Mean L 68.8 vs v1's 67.3. Saturation 0.8117 vs
  0.8215. Lit fraction 0.2570 vs 0.2636 — the duty-0.40 call was right and it undid v2_44's eaten
  look. Three numbers on target.
- **grad>40 fell again: 0.0104.** That is the lowest of the three candidates and **5.5× under v1**,
  3.6× under `ref_ring`. Sixteen rounds and this number has never moved. The one encouraging figure
  is the ratio g40/g20, up to **0.221** from 0.206 — the events that remain are a slightly larger
  share hard — but both terms fell, so the picture is simply softer than last round.
- **Flat area is the gap that decides this project.** 0.133 and 0.046 against v1's 0.443 and 0.398.
  Roughly **one ninth**. Every other difference between this frame and v1 is downstream of it.
- **Dark fraction is still the wrong kind of dark.** 0.1859 against v1's 0.1216. More near-black
  pixels than v1 and a quarter of its flat area. That combination only occurs when the dark is
  ripple, not surface.
- **Whole image, honestly.** At 100% on black this reads as a confident, saturated, well-exposed
  object and it is the best-looking frame of the v2 series. Next to v1 it still reads as *printed*
  rather than *cast*: v1 gives you three or four enormous calm zones with violent edges between them,
  and v2_45 gives you forty soft bands everywhere. Next to `ref_ring` and `ref_puck` it is louder and
  busier than either, and neither reference has a single object floating clear of its silhouette.

## 4. Compositing — **8.1 / 10** (v2_44: 7.6, v2_42: 8.2)

- **Component count back to 16**, level with v2_42 and below v1's 29. Two detached bodies removed
  (1034 px filament, 387 px peanut chip), one rim dash removed, nothing new gained. This is the
  cleanest structural read of the three candidates.
- **Lit area restored and bar 5 grown back** 27,908 → 30,278 px. The letterform no longer looks
  chewed at the lower right.
- **Bar 5 is still a separate component.** Sixth round. At 100% the elbow at (920,1230) reads as a
  break in the mark, and it remains the most visible compositional fault in the frame.
- **Background floor holds at the best in the series** (0.65–0.67, max 5–6) but is not v1's zero.
- **Highlight discipline holds:** 0.081%, all three kicker boxes inside cap. The orange rim kicker at
  (1050,1200) is a hard, perfectly straight 4 px line detached from the geometry it belongs to —
  crop **(880,1150)–(1180,1350) at 300%** — and it is now the second most graphic artifact after the
  lozenge.
- **Depth of field contributes nothing measurable** for the second round.

## 5. OVERALL — **8.3 / 10 — REJECTED**

Best frame of the v2 series, and still 0.3 short of the v1 it is meant to replace.

Up 0.3 on v2_44 and 0.1 on v2_42. The gain over v2_44 is straightforward: you found the real source
of the fill — the cards, not the panel — and removing it took out two detached objects and let you
put the lit area back without the frame going grey. The gain over v2_42 is thinner and comes from
two places: the crown is 14% darker at peak, and mean L plus saturation now land on v1 where v2_42
was hot and flat.

Three things hold it below 8.5, in order of weight.

**The round's stated purpose did not happen.** grad>40 went 0.0110 → **0.0104** and flat-block on
bar 1 went 0.136 → **0.133**. The 46 consecutive sub-L 10 pixels are in the background between bars
1 and 2, not in the face; inside the silhouette the mid-face floor is **L 40** and the longest
sub-L 10 run is **one pixel**. Dimming the cards 60% changed which light fills the channel. It did
not empty it. The channel is being written by the band panel itself, and until the emission between
bands is driven to zero rather than to a value, no amount of dimming anything else will produce v1's
black.

**The lozenge is worse.** 586 px at peak 84, plus a 410 px tail — the largest core and the highest
peak in nine rounds, on the round where you decided to keep it. I accept your read of the optics. I
do not accept the result: it is a hard-edged bright sliver in open black that touches nothing, and it
is the first thing my eye goes to at 100%.

**The crown gave back a quarter of last round's win** (max 109 → 124, mean 17.78 → 20.63) in exactly
the region the user circled.

Against that, credit where it is owed and it is not small: sixteen components, the filament closed,
lit fraction, mean L and saturation all on v1, the kickers closed for a fourth round, the background
floor untouched, and the cleanest structural read in the series.

---

## 6. Ranked changes

1. **Zero the panel between bands — not dim it, zero it.** — **MUST for 8.5.**
   Bar 1's mid-face floor is **L 40** across 184 unbroken pixels; v1's same row is nine separate lit
   segments with 108 px of true black inside the bar. You have now tried feather (no effect), duty
   (cost lit area), panel distance and card dimming. All four change *how much* light fills the gap.
   None makes the gap dark. Set the emission between bands to literal zero and cut the band count
   over bars 1 and 4 so each face carries **at most three lit regions**. Test: **flat-block ≥ 0.30**
   on both (150,250)–(340,800) and (430,930)–(660,1250), **≥ 15 consecutive pixels below L 10
   strictly inside a lit run** on a horizontal cut across each face, mean L held at 64–72.

2. **Matte the lozenge in the compositor. Ninth round.** — **MUST for 8.5.**
   586 px at peak **84**, x 862–916, y 1268–1305, plus 410 px at (893,1307). Five attempts in the
   light path have all failed and this round it grew while the box around it got 35% quieter, which
   proves the core is not fed by the cards. It is 586 px in a known 140×115 box. A garbage matte or a
   holdout plane between the back panel and bar 5's lower-left corner closes it tonight. Test: **zero
   components over 150 px in (830,1230)–(970,1345), nothing above L 40.**

3. **Put the crown back where v2_44 had it, without the cards.** — **MUST for 8.5.**
   Max 109 → **124**, mean 17.78 → **20.63**. This is inside the user's own circle on
   `v1_annotated`. Do not undo the card dim — it bought you change 5 below. Instead kill the bright
   horizontal target the top bevel is magnifying: a soft vertical gradient in the panel at the
   crown's altitude, or a smaller top-bevel radius on bar 1. Test: **crown box (85,170)–(410,280) max
   ≤ 90, mean ≤ 14**, with no run of ≥ 6 consecutive lit pixels left of x=140.

4. **Rejoin bar 5 and kill the 271 px debris head.** — **nice-to-have.**
   Bar 5 has been its own component for six rounds; v1 has three bodies to your four, and the elbow
   at (920,1230) reads as a break in the mark at 100%. The 271 px red rectangles at (1032,751),
   peak 48, have not moved in five rounds and are now the last free-floating object above L 40 apart
   from the lozenge. Test: **one connected component containing both bar 5 and bars 2/4**, and no
   component over 100 px in (1010,730)–(1080,910).

5. **Drop the defocus, or fix the focal distance.** — **nice-to-have.**
   Two rounds, two stops, no effect: peanut ÷ bar 4 mean gradient 0.89 at f/4, **0.87 at f/2.8**,
   target ≤ 0.60. It is costing render time and buying nothing. Either confirm the focus object is
   bar 4's front face rather than the world origin, or switch DoF off and add the separation in the
   compositor with a depth-pass blur, which is what the "more dynamic realistic compositing" note was
   asking for anyway.

---

## 7. Which one I would hand the client

**v2_45.**

v2_42 and v2_45 are within noise of each other on almost every number, so the pick comes down to what
a client's eye lands on. Three reasons:

1. **The two zones the user circled are quietest here.** Crown box max 124 against v2_42's 145. The
   lozenge box carries a third less energy — region max 135 vs 182, mean 11.85 vs 18.11. v2_45's
   lozenge core is the bigger component, but v2_42's corner is the brighter, busier picture.
2. **It matches the frame the user already approved.** Mean L 68.8 and saturation 0.8117 against
   v1's 67.3 and 0.8215. v2_42 sits 5 points hot and 2 points flat. Shown next to v1 in a deck,
   v2_45 is the one that looks like the same shoot.
3. **It is structurally the cleanest.** Sixteen components, no filament, no detached peanut chip, lit
   area back inside v1's range. v2_44 is out on its own merits — it gained a 1034 px filament and a
   387 px chip and lost 9% of the letterform to get there.

If the lozenge cannot be matted before delivery, I would still send v2_45 and crop or retouch that
one 140×115 box by hand. It is a two-minute fix on a frame that is otherwise the best of the series.

SCORE: 8.3
