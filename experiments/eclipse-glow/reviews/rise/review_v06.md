# Review v06 — rise video

1. **Score:** 7.3 / 10

2. **What works**
- The rise reads as a moonrise. Crescent caps break the horizon first (f24), squashed flat. The bodies clear at about f204, then hold for 3.5 s. The pacing is slow and even.
- Extinction works. At f96 the bodies are dim and violet, and they come back to full sunset colour as they rise (f168 onward).
- At rest (f270) the logo is legible and keeps the still's gradient, spectral rim and crescents.

3. **Problems, ranked**
1. **The shimmer reads as digital tearing, not heat haze.** Look at horizon_f160 and the f160–165 strip, on the vertical edges in the 80 px above the horizon. The offsets are hard, regular, high-frequency teeth with a period of about 6–8 px, like interlace combing. Only the edges move; the interior gradient stays flat. The teeth also stay on the rested logo: in rested_f270 the pink bar bottoms, 65 px above the horizon, show scalloped right edges. The pattern does change between frames, which is good. Fix: drive the displacement with 2–3 octaves of low-frequency noise, in bands 12–24 px tall. Give it 2–6 px of amplitude at the horizon, falling off exponentially to 0 at 40 px above. Add a 1–2 px vertical blur inside the displaced band, and make the pattern drift upward over time.
2. **The mirror is too weak while rising, then leaks at rest.** In f60–f168 the inverted image is a dim, 20–40 px pink smear, too faint to see at video scale. At f270, two faint purple blobs sit under bars 1 and 2, below the horizon, detached from a logo that is 65 px above it. They look like a leak. Fix: while the base is within about 30 px of the horizon, set the mirror to 0.35–0.5 of source brightness and 25–40 % of the visible height, in the source's colours. Fade it to 0 as the base climbs 30–60 px above the horizon.
3. **The atmosphere flattens the look of the still.** The orange sky gradient climbs to the logo's tops, so the background is brown, not the still's near-black. The self-glow halo at rest is visibly tighter and weaker than in FINAL_eclipse_logo.png. The horizon is a hard, full-width 2 px line over flat, dead ground. Fix: make the sky gradient reach black by about 35 % of the frame height above the horizon. Match the halo radius and strength to the still, within ±15 %. Soften the horizon line to 3–6 px with a glow falloff, and add a faint warm band on the ground for the first 10–20 px below it.

4. **Research check** — The video follows all four findings: dimmer and redder low, flattened low, layered shimmer, and a mirror below the horizon. It contradicts the claim that the effects "fade with height". The shimmer and the mirror ghosts both stay once the logo has cleared the horizon (f270).

5. **What 8.5 needs**
- Organic, soft haze bands that fall off to 0 by 40 px above the horizon.
- A mirror you can see during the rise, gone at rest.
- The background back to black above the horizon glow, and the halo matched to the still.
