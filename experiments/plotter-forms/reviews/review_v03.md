# Review v03 — plotter-forms

1. **Score:** 7.0 / 10. 3D read 7.0, hidden lines 7.0, plot readiness 6.0, variety 8.0.
   Pairwise: Q (new) is slightly better than P. The Mobius twist now reads and monkey-slices is cleaner. But klein-eight was dropped (49 to 48), and the blots are unchanged.

2. **Targets**
- Forms: 48 in 5 families. **Hit.**
- Lines through opaque surfaces: none found. **Hit.**
- Fragments: 0 isolated strokes under 1 mm. Attached stubs remain: a tab on helicoid-catenoid (step 5), a dot in knot-slices' upper hole, and broken radials at the enneper and enneper-3 centres. **Missed (marginal).**
- Blots over 15 px: hopf-onion 54×70, hopf-meridian 61×61, hopf-nested 38×70, contour-terrain 43×32, hopf-torus 35×27, ridgeline-range 29×17, scherk 20×17, ridgeline-ripple 19×26, mobius 19×67. **Missed (9 cells).**
- Lines leaving the cell: 0 edge pixels. **Hit.**

3. **What works**
- The slices read as solids, with clean hidden lines.
- seashell, richmond, dini, kuen and helicoid-catenoid read as 3D at once.
- The range is real: 48 distinct plots.

4. **Problems, ranked**
1. **Blots where lines converge** (Hopf centres, mobius edge, contour-terrain cliffs, ridgeline-range edges). Add a pen-occupancy pass: rasterise at 0.35 mm, draw by priority, and cut segments whose cells are already inked.
2. **hopf-links and hopf-meridian read as flat fans of ellipses**, and hopf-tumble's core is a tangle. Add over/under breaks at crossings, as in a knot diagram. Rotate in 4D so no fibre projects as a needle.
3. **Cusps on self-intersecting surfaces.** Catalan has a tangle at its central cusp. Henneberg has a notch in its lower-left rim and a stray vertical line on the fold. Kuen has hooks at its lower left. Trim the domain an epsilon away from singular curves, and drop strokes under 2 mm after hidden-line removal.
4. **The harmonic spheres read as flat patterns in a circle** (tesseral, pair, charges), and arcs pile up at the limb (ripples, fine). Displace the radius by the field (r = 1 + a·f), or tilt so a pole sits inside the disc.
5. **monkey-slices.** The planes are nearly edge-on, so the head reads as a hatched silhouette with wobbly lines. Tilt the slice normal about 25° toward the camera, and smooth the mesh first.

5. **Checklist**
1. No. hopf-links, hopf-meridian, hopf-tumble and monkey-slices read flat or tangled.
2. Mostly yes, except at the catalan and henneberg cusps.
3. No. Limb dashes on sphere-ripples; a tab on helicoid-catenoid.
4. Yes. 9 blots.
5. No. monkey-slices wobbles; the henneberg rim has a notch; torus-waffle has a kinked lens at the top.
6. Mostly yes. torus-slices and torus-shells look alike.
7. No, for about 12 cells.
8. Uncertain for scherk. It shows one pinched saddle, not the periodic surface.

6. **What 8.5 needs**
- A pen-occupancy cull.
- Crossing breaks and a new 4D view for the Hopf plots.
- Trimmed domains and a short-stroke filter for the cusps.
- Relief on the field spheres.
- A tilted, smoothed slice for the monkey.
