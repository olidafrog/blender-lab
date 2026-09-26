# Printed plastic: decisions

Experiment: `wonder-printed-plastic`. A frosted acrylic A5 slab with artwork printed under the face. Final score 8.4/10 after 29 versions. The full research is in `experiments/wonder-printed-plastic/reviews/research-brief.md`.

## What the references are

- The Warp posters are scans of colour laser prints, not plastic.
  - The diagonal lines are the printer's line-screen halftone.
  - The lines stay sharp across the blurred edges. So the blur was in the digital artwork before printing.
  - The yellow dot grid is printer tracking dots.
- The Defying Decay pieces are probably photocopies on tracing paper, stacked and scanned.

## Decisions

**Blur the artwork in the shader, then screen it. Do not rely on the plastic for blur.**
A real diffuser in front of the ink would blur the halftone lines away. That does not match the references. The frosted slab adds only a small blur and a veil on top.
Rejected: blur from surface roughness alone. It was noisy, slow and destroyed the line screen.

**Two blur passes on the ink shape.**
A pre-blur tail (`max(crisp, 0.7 × 2.5 mm blur)`) gives the soft falloff. A 0.5 mm core soften stops the glyph cores from looking like vector art. A third unscreened blur adds a soft veil.

**Print plane 2 mm under the face, with a white flood backer.**
This copies second-surface printing. Depth is a custom property, `print_depth_mm`, on the Slab object. A driver moves the print plane from it.

**Render at 2× and downsample.**
The 0.34 mm line screen aliases at 1×. This doubles the render time (about 6 minutes at 1024 samples).

**Partial denoise plus grain.**
Full denoise erased the toner texture. None left sample noise.

**Lighting: satin strip at the mirror point, and a black flag.**
The first satin light put a veil over the logo. A small glossy-only strip, placed where the camera sees its reflection, gives sheen without the veil. A lifted black flag darkens the bright side face.

## Known limits

- Type smaller than about 4 pt blurs until it cannot be read at the default pre-blur. Reduce `PRE-BLUR` radius for text-heavy content.
- Fluoro inks glow but do not spread a halo yet.
- A faint hairline shows where the front bevel meets the side.
- Edge damage on outlines only shows in close crops.

## V2: leads from the Photoshop build

The same references were rebuilt in Photoshop (`~/GitHub/photoshop-lab/projects/wonder-printed-plastic`, 8.5/10). `scripts/build_v2.py` applies its findings. `build.py` stays as the v29 original. Not yet reviewed.
- **Plates (the big win).** A crisp FRONT plate for type and linework, with no pre-blur or soft copy, over the blurred BACK plate. Small type is now readable. The FRONT plate needs its own density (0.95) and the screen: without them it read as a flat grey sticker.
- **Screen angles** from ref1: the dark lines now measure 156° in the render (ref 153.4°; v1 was 23°).
- **Fluoro rim.** At 2.0 it read as a pale sticker outline, which the Photoshop build had rejected. 0.5 with a yellow tint is a faint edge.
- Ink density mottle and mostly-light specks: subtle at full frame.
- Untried: a smooth sinusoid screen, which might remove the need for 2× renders.
- Test content: `content/poster_back.svg` and `poster_front.svg` are the Photoshop poster scaled to A5.
