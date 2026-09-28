# Colour

- AgX (the default) desaturates bright saturated colours; orange reads as peach. Use `view_transform = "Standard"` for literal colours, or the `AgX - Punchy` look for contrast.
- Under Standard, anything above 1.0 clips to a hard flat shape. A glow with a long bright tail clips at its core. Build the tail from stacked blurs. `eclipse-glow`
- Low values show clearly on black: 0.1 linear is about 89/255 sRGB. A "smooth" fade into dark can still read as a hard line. Shape the mask with a power falloff. `eclipse-glow`
- AgX with High Contrast and exposure −0.75 gave neutral greys on a light background. `printed-plastic`
- Saved PNGs are sRGB. Linearise pixel values before you compare them with scene values. `caustics-v2`
- A mid-value sRGB tint (for example 255,175,130) multiplied in linear space is far darker than it looks: G and B drop to about 0.4 and 0.2. It nearly erased a reflection. Tint multiplies with near-white values (≥ 220) or mix toward the colour instead. `eclipse-glow`
- Khronos PBR Neutral keeps saturated orange and coral that AgX turns peach. `opal-essence`
- Compositor saturation (Hue/Saturation/Value) works on linear light and is harsh: 1.35 turned a pink stop pure red. Use 1.1–1.2 at most. `5.x` `opal-essence`
- Re-measure exposure (median value of the subject against the reference) after removing any veil or spill. In `opal-essence` the backlight was lowered while a spill veil inflated brightness; once the veil went, the plate sat at 0.62 against the reference's 0.85, and reviewers called it "smoked glass" for four rounds.
