# Research brief: the "printed under frosted plastic" look

## 1. How the references were made

**Warp posters (ref1, ref2): scans of a colour laser print. Not physical plastic.** Confidence: high for the laser print, medium for the rest.
- The designer is Elliott Elder (@_lliott, studio UNCANNY). No process notes are published ([UNCANNY work](https://uncanny.services/work), [X post](https://x.com/_lliott/status/1914981879209472377)). The sold A3 is litho on 300gsm silk, 3 spot + CMYK ([Warp store](https://warp.net/products/515794-warp-records-x-barbican-a-warp-happening-a3-poster)). The frosted version is the social image.
- Evidence from the crops. The diagonal lines are a **line-screen halftone**, and each ink has its own angle (blue steep, black shallow). The lines stay sharp *across* the blurred edges of "Warp". Line width changes through the blur gradient. So the blur was in the digital file *before* printing. A diffuser in front of the ink would have blurred the lines away.
- The tiny yellow dot grid is almost certainly a **Machine Identification Code**: yellow tracking dots from a colour laser printer or copier. The dots are about 0.1 mm, spaced about 1 mm ([Wikipedia](https://en.wikipedia.org/wiki/Printer_tracking_dots), [EFF](https://w2.eff.org/Privacy/printers/docucolor/)).
- The raised blacks and cool grey whites come from toner on uncoated or translucent stock, plus the scan's black point and white balance.

**Defying Decay (ref3, ref4), Dan Barkle: photocopy or toner on tracing paper or vellum, stacked and scanned.** Confidence: medium. You can see ghosted large type from sheets underneath, toner dropout, fibre mottle and drafting grids. Barkle works from scans and found graphics ([The Brand Identity](https://the-brandidentity.com/interview/dan-barkle-reveals-process-references-behind-post-apocalyptic-brand-postdigital)). Scanned tracing-paper asset packs are common in this scene ([design syndrome](https://designsyndrome.com/products/trace-paper-asset-pack)).

**Design Dojo (ref5): most likely digital emulation with texture overlays.** Confidence: low to medium.

## 2. Optics of blur behind a frosted layer

- A frosted sheet sends each ray out in a cone. The blur radius is about **r ≈ d · tan(θ½)**, where d is the gap between ink and the scattering surface. Ink in contact with the sheet is sharp. Lift it and it goes soft. This is why back layers blur more. Confidence: high (geometric optics).
- If the scatter is in the bulk of the sheet rather than on its surface, the blur also grows with sheet thickness.
- Real numbers for Acrylite Satinice at 2 mm: 92% transmission with a 20° half-angle, down to 72% with 50° ([Acrylite PDF](https://www.acrylite.co/files/content/acrylite.co/documents/product-information/ACRYLITE-Satinice-Enhanced-Technical-Information.pdf)). Worked example: a 0.5 mm gap with a 30° half-angle gives about 0.3 mm of blur. Haze (ASTM D1003) is the share of light scattered more than 2.5°. Matte diffuser films are often above 80% haze ([Intertek](https://www.intertek.com/polymers-plastics/testlopedia/haze-astm-d1003/), [HunterLab](https://www.hunterlab.com/en/blog/how-is-astm-d1003-transmission-haze-measured-at-levels-30/)).
- Why contrast drops: the top surface reflects about 4% of the light, spread wide by the roughness, and the bulk scatters some light back. Both add a veil V to every pixel, so contrast becomes (W+V)/(K+V). Blacks lift and whites take on the sheet's cool tint. Light also crosses the diffuser twice, in and out, so the blur applies twice.

## 3. Second-surface printing on acrylic

The art is mirrored and printed on the back face, colour first, then a **flood white** backer. Some shops add a third colour layer for day/night signs ([ASG](https://www.asg-companies.com/second-surface-acrylic-printing), [LargePrinting](https://largeprinting.com/resources/terms-used-in-large-format-printing/colorwhitecolor-printing-explained.html)). On clear acrylic the art looks deep and glossy, with a sheet-thickness gap before the ink. On frosted acrylic printed on the back, the blur is small, because the ink touches the scattering surface.

## 4. The diagonal lines and yellow dots

- **Lines:** a laser or digital-press line screen, with a different angle per separation. Laser engines prefer line screens because they misregister mainly in the paper-feed direction ([US 7508549](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7508549)). The lines are not an embossed plastic texture and not screen-print mesh. Scanner moiré may add some beat patterns. Confidence: high.
- **Yellow dots:** MIC tracking dots, as in section 1. Confidence: high.

## 5. Fluorescent ink halo

Fluorescent pigment turns UV and blue light into green or pink, so it can reflect more than 100% at its peak. In a diffusing layer, this very bright colour spreads sideways. Against a grey neighbour, the spread shows as a glow. In ref1 the thin bright rim may also be misregistration or a trap between plates. Confidence: medium.

## 6. Blender Cycles recommendations

**Recommendation: do the depth blur in the artwork, not in the light paths.** This is what the designers did. It is noise-free and you can direct it.

1. **Ink layers:** one image per ink. Put a "depth" blur on each one before shading, from pre-blurred PNGs or Blur nodes in the compositor. Set blur per layer: blur_px = gap × tan(θ½) × px/mm.
2. **Line screen per ink:** in the shader, rotate the UVs by the ink's angle (for example 15°, 45° or 75°). Build the lines as `sin(u·freq)` and threshold them against the ink coverage. This makes the lines sharp over blurred edges, as in ref1. Use a frequency of about 100–150 lpi at print scale.
3. **Tone:** map black to about 0.12–0.18 linear grey and white to about 0.75–0.85 with a cool tint. Multiply in the ink colours.
4. **MIC dots:** a sparse yellow dot grid with a 1 mm pitch, dots 0.1 mm, at about 30% opacity.
5. **Optional physical sheet:** a thin plane about 0.2–1 mm above the print. Use Principled BSDF with Transmission 1.0, IOR 1.49 and roughness about 0.3–0.5 for real blur, or about 0.1–0.2 if you blur in 2D. Add a coat or specular roughness of 0.4–0.6 for a satin sheen. Scattering at render time is slow and noisy, so keep this sheet thin and near the art.
6. **Grain:** add toner speckle as high-frequency noise thresholded into ink coverage, per layer, before the line screen. Add a separate low-amplitude fibre or mottle noise on the sheet's base colour and roughness.
7. **Fluorescent ink:** an Emission of about 0.3–0.8 masked to the fluoro ink, plus a small blurred copy of the mask for the halo. Or use Glare (Fog Glow) in the compositor on that pass.
8. **Controls:** put all of this in one node group with inputs for gap per layer, line lpi, line angle per ink, black lift, white tint, grain amount and fluoro glow.
