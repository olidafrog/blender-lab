# Review v11

1. **Score:** 6.3 / 10

2. **Targets**
- Backdrop TL 111 / 96: **missed** (+15). TR 141/142, BL 110/111, BR 113/117: hit.
- Share 38/36, median 73/75, p5 13/7, p95 89/92: hit.
- <12 % 4.4 / 7.6 (0.58): **missed**.
- LCD (142,203,211): hit. Grain std 16.7/15.4: hit.
- By eye: tops 81–85, hit. S-step slopes 158–198: **missed** (target 90–105). S-step crease minimum 25–30: **missed** (needs under 12).

3. **What works**
- Camera, layout, share and LCD match closely. The dial module, gear, vents and screws are in the right places.
- The S-step has a flat sloped band with a crest fillet and a foot crease. It reads as a moulded step.
- The lower battery lid and the right vent block now have plausible CAD fillets (br crop).

4. **Problems, ranked**
1. **The S-step slopes are still chrome ribbons** (x 780–1300, y 590–760 at 1600 px). They measure 160–198, with a hard specular streak. Dropping Card Slopes from 10 W to 4 W and raising roughness to 0.44 did not help, so the light that makes them bright is something else. Fix: render Diffuse and Glossy Direct passes and sample the band to find which light is responsible. If glossy is more than half, set roughness to 0.6–0.7 on faces with normal.z 0.3–0.85 only (a Geometry Normal mask into roughness). Target 90–105 with a soft gradient and a crest highlight of 4 px or less.
2. **The LCD shield and pods are still the wrong part** (x 450–950, y 250–600). The shield is a grey frame with a 35–40 px pillow bevel. The reference has a black shield with a thin 6–8 px steel rim and a sharp inner wall. The pods are black rubber stubs in a U-bracket: about 7 mm across and 10 mm long. The reference pods are scratched gunmetal barrels, 10–11 mm across and 22–25 mm long (about 2.2:1). They lie on the shield's top-left edge, along the antenna axis. The "too big" and "too small" notes were both about length, not diameter. Fix: build pods at 10.5 × 24 mm in steel material, delete the bracket, and make the bezel a thin steel rim. The rotary knob touches the bezel. Move it 3 mm clear.
3. **The finish is too clean, and the creases are not black.** The tops show almost no bead-blast speckle. There is about one visible scratch on the whole body. The reference has dozens of straight hairlines per plate. Creases bottom out at 25–30. Fix: add speckle to albedo at ±8 levels, with 1–2 px grains at 1600 px. Add 20–40 straight scratches per plate. Cut the S-step foot and the plate gaps 3 mm deep over an albedo-0.01 liner.

5. **Research check**
- Sloped steps with a crest fillet and a foot crease: agrees.
- "Sloped faces read lighter than tops": overshoots into specular. The reference slopes are matte.
- "Strong fine bead-blast speckle": contradicted. The polymer reads as smooth grey plastic.
- The backdrop grain is harsh salt-and-pepper at 1:1 (bl crop). The reference grain is softer and lower in contrast.

6. **What 8.5 needs**
- Slopes 90–105 and matte, with no streak.
- Long gunmetal pods lying on a black shield with a thin steel rim.
- Creases under 12, <12 % at 5.3 or more, backdrop TL at 108 or less.
- Visible speckle and straight hairline scratches on every plate.
