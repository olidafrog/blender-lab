# Research brief — dispersion / caustics in Blender 5.2 (Opus agent, 2026-09-19)

- No Dispersion socket on Principled/Glass in 5.2. Native Dispersion Scale / Abbe only in 5.3+. Use 3× R/G/B refraction lobes + Add Shader.
- Exaggerated IOR spread ±0.06–0.10 needed for the look; AgX desaturates extremes.
- Lighting is the look: 2–4 long thin area strips (4 m × 0.08 m) behind/edge-on the glass, pure black world, warm strip vs cool strip.
- Geometry: thick, big bevels, curvature is what makes fringes.
- Render: 32 max bounces, 24 transmission, clamp indirect 8, OIDN accurate, 1024+ samples.
- MNEE shadow caustics (is_caustics_light / caster / receiver) only affect caustics inside shadows on a receiver — needs a floor. Both cited videos are about this feature (CGMatter "Blender 3.1 Caustics", PIXXO 3D caustics tutorial).
- Compositor 5.x: Glare settings are sockets. Fog Glow + Streaks (Color Modulation = chromatic fringe), Lens Distortion dispersion 0.01–0.03, grain.
- Reference images: behance.net/gallery/56555015/Chromatic-Black, behance.net/gallery/110079163/Glass-Dispersion, behance.net/gallery/192722805/Dispersion-Glass-Graphics
