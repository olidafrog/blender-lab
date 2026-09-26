# Colour

- AgX (the default) desaturates bright saturated colours; orange reads as peach. Use `view_transform = "Standard"` for literal colours, or the `AgX - Punchy` look for contrast.
- Under Standard, anything above 1.0 clips to a hard flat shape. A glow with a long bright tail clips at its core. Build the tail from stacked blurs. `eclipse-glow`
- Low values show clearly on black: 0.1 linear is about 89/255 sRGB. A "smooth" fade into dark can still read as a hard line. Shape the mask with a power falloff. `eclipse-glow`
- AgX with High Contrast and exposure −0.75 gave neutral greys on a light background. `printed-plastic`
- Saved PNGs are sRGB. Linearise pixel values before you compare them with scene values. `caustics-v2`
