# Colour

- AgX (the default) desaturates bright saturated colours; orange reads as peach. Use `view_transform = "Standard"` for literal colours, or the `AgX - Punchy` look for contrast.
- Under Standard, anything above 1.0 clips to a hard flat shape. A glow with a long bright tail clips at its core. Build the tail from stacked blurs. `eclipse-glow`
- Low values show clearly on black: 0.1 linear is about 89/255 sRGB. A "smooth" fade into dark can still read as a hard line. Shape the mask with a power falloff. `eclipse-glow`
- AgX with High Contrast and exposure −0.75 gave neutral greys on a light background. `printed-plastic`
- Saved PNGs are sRGB. Linearise pixel values before you compare them with scene values. `caustics-v2`
- A mid-value sRGB tint (for example 255,175,130) multiplied in linear space is far darker than it looks: G and B drop to about 0.4 and 0.2. It nearly erased a reflection. Tint multiplies with near-white values (≥ 220) or mix toward the colour instead. `eclipse-glow`
- Khronos PBR Neutral keeps saturated orange and coral that AgX turns peach. AgX also turned a pink cloud pastel and a blue sky grey. `opal-essence` `clouds`
- A sky gradient mapped over 0–45° of elevation barely changes across a level camera's ±12–20° frame. Map it to the frame's own span. `clouds`
- Compositor saturation (Hue/Saturation/Value) works on linear light and is harsh: 1.35 turned a pink stop pure red. Use 1.1–1.2 at most. `5.x` `opal-essence`
- Re-measure exposure (median value of the subject against the reference) after removing any veil or spill. In `opal-essence` the backlight was lowered while a spill veil inflated brightness; once the veil went, the plate sat at 0.62 against the reference's 0.85, and reviewers called it "smoked glass" for four rounds.
- Grade in Colour Management before the compositor: `view_settings.use_white_balance` with `white_balance_temperature` and `white_balance_tint` (5.x), and `use_curve_mapping` for per-channel curves. It is free, saves in the `.blend`, and keeps the materials at their true colour. A Backrooms grade: about 7000 K, tint −30 to −40 (green), green lifted and blue lowered in the highlights, a little red in the shadows. The template exposes `wb_temp` and `wb_tint`. `5.x` Source: [Blender Guru, Backrooms](https://www.youtube.com/watch?v=kBsVJSETydU)
- AgX desaturates a mid-bright floor hard: oak albedo with sRGB chroma 61 rendered at 25, and roughness made no difference. Raise the albedo's saturation (or warm the white balance); switching to Khronos PBR Neutral fixed the floor but oversaturated a dark brick in the same frame. `5.x` `apartment-model`
- View white balance: a higher `white_balance_temperature` warms the image (6500 → 13000 K took a white wall from R/B 1.01 to 1.22, an iPhone's warm daylight balance). Judge material hue relative to a white wall in the same frame, never in absolute sRGB. `5.2` `apartment-model`

- Several phone photos of one room each have their own white balance (here 9000, 13000 and 8500 K for the same paint). One grade for all makes reviewers argue about the material's hue round to round; set the view white balance per camera until the paint matches each photo in absolute sRGB, then match materials in absolute terms too. `apartment-model`
