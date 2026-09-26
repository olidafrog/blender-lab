# Art direction review — v06b

Reviewed 2026-09-19 against `ref_ring.png`, `ref_puck.png`, `ref_abstract.png` and `research-brief.md`.
Candidate: `renders/v06b.png` (35% scale, 128 samples). Noise and resolution ignored.

## Score: 5.6 / 10 — not accepted (threshold 8.5)

The black studio, the thick-perspex read and the general premium feel are there, but the image is
mostly monochrome. Colour appears as small isolated dots of yellow, orange and cyan sitting on top
of a silver/white body, where every reference carries wide saturated spectral sweeps that run along
the curvature for hundreds of pixels. The interiors are clipped to flat white across large areas,
so the forms lose their internal structure and the piece reads as polished chrome or mercury rather
than glass. The shapes have also inflated: corners are rounded until the two zig-zag bars read as
soft lozenges, and the peanut has lost its waist. Composition is loose — the logo sits small in a
4:5 frame with heavy dead margin, while the references crop tight and fill the canvas.

## Ranked changes

1. **Widen the R/G/B IOR spread and make the fringes travel.** Push the three refraction lobes to
   ±0.10–0.12 (currently reading closer to ±0.02) so colour runs as continuous bands along each
   edge instead of isolated specks. Target the `ref_puck` rim: a red-yellow-green-cyan-blue ramp
   that sweeps the whole silhouette.
2. **Kill the white clipping.** Drop strip-light power roughly 1.5–2 stops and clamp indirect to 8,
   or add a highlight rolloff in the compositor. Any region at pure 1.0 white carries no hue, and
   right now that is about a third of the glass. Recovering those areas is what turns silver into
   spectral.
3. **Reduce the bevel / shrinkwrap so the logo stays legible.** The geometry has puffed into
   pillow shapes. Cut the bevel width by about half and keep the bar ends square-ish; the
   references are all smooth but each still has a hard, readable silhouette.
4. **Add a warm/cool split in the lighting.** Two long thin strips (4 m x 0.08 m) at roughly 2700 K
   and 7000 K, placed edge-on behind the glass on opposite sides. `ref_ring` gets its whole
   identity from orange-versus-blue across one object; v06b lights everything neutrally.
5. **Crop tighter and vary the light bands.** Scale the logo to fill about 85% of frame height and
   reduce the margin. The current internal reflections are broad, soft and repetitive across all
   three shapes — make the strips thinner and stagger their angles so each shape gets a distinct
   pattern rather than the same white slab three times.
6. **Add fine surface detail and a touch of compositor dispersion.** Faint scratches and dust
   (a low-strength noise bump, ~0.002) plus Lens Distortion dispersion 0.01–0.02 and a light
   grain. All three references have visible micro-scratches; they are a large part of the
   photographed-object feel.

## Keep

- Pure black world with no visible floor, gradient or spill. Correct and matches all three refs.
- Overall glass thickness and the sense of real volume — the internal reflections show genuine
  multi-bounce depth, not a thin shell.
- The single small star/streak glint at the top right of the peanut. Restrained and premium; keep
  it at that strength and do not add more.
- The three-shape layout with overlap between the bars. The occlusions and see-through stacking are
  doing useful work.
