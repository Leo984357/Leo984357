# ASCII artwork credit

The banner is **colored ASCII art**, built from a regular grid of 160 columns × 28 rows. Every visible mark is a monospace ASCII character from ` .:-=+*#%@` on a dark background. The static SVG contains text elements and no embedded raster image.

- Original painting: Vincent van Gogh, *The Starry Night* (1889).
- Source: https://commons.wikimedia.org/wiki/File:VanGogh-starry_night.jpg
- Original image: https://upload.wikimedia.org/wikipedia/commons/c/cd/VanGogh-starry_night.jpg
- The source identifies the artwork and reproduction as public domain.
- Interpretation: a panoramic sky detail, sampled into character density and color. The complete character grid is displayed without stretching or additional cropping.
- Generator: https://github.com/Leo984357/Leo984357/blob/main/scripts/build_ascii_banner.py (Python + Pillow).

## Motion

The sky flows through **48 distinct character frames over a six-second loop**. Two localized swirls displace the source grid by at most 1.91 cells; the moon remains fixed. The periodic motion returns to the starting state without an extra duplicate endpoint or random flicker.

- [Shared frame data](starry-night-frames.json): character grids and a fixed sampled color palette, played at an average of 8 fps by the website and the GitHub banner.
- [Frame generator](../scripts/build_ascii_animation.py): deterministic local motion from the original ASCII SVG.
- [GIF generator](../scripts/build_ascii_gif.py): renders the actual characters in Menlo at 1600 × 560 pixels. A fixed palette of 63 ink colors, each with four antialiasing coverage levels, preserves smooth lettering without dithering. Alternating 120/130 ms frame delays preserve the six-second period in GIF's centisecond timing format.
- [Animated banner](starry-night-ascii.gif): an indefinitely looping GIF that works in GitHub without JavaScript.
- [Static banner](starry-night-ascii.svg): selected automatically when the browser requests reduced motion, and always available through the profile's static-version link.

Rebuild the GIF from the shared frame data with `python scripts/build_ascii_gif.py`. Menlo is selected on macOS; DejaVu Sans Mono and Liberation Mono are supported fallbacks, or pass an installed monospace font with `--font`.

The website also uses a browser-rendered PNG of the same character SVG for social link previews.
