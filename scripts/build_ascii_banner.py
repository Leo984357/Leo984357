"""Render a painting as a deterministic grid of colored ASCII characters.

Usage: python scripts/build_ascii_banner.py --source /path/to/starry-night.jpg
Requires Pillow. The output SVG contains text only, with no embedded raster.
"""
from argparse import ArgumentParser
from colorsys import hls_to_rgb, rgb_to_hls
from html import escape
from pathlib import Path

from PIL import Image


def color_grade(rgb):
    """Increase chroma while preserving the established hue and lightness."""
    hue, lightness, saturation = rgb_to_hls(*(channel/255 for channel in rgb))
    graded = hls_to_rgb(hue, min(1, lightness*1.04), min(1, saturation**0.5*1.45))
    return tuple(round(channel*255) for channel in graded)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'assets/starry-night-ascii.svg')
    args = parser.parse_args()
    columns, rows = 160, 28
    cell_width, cell_height = 10, 20
    ramp = ' .:-=+*#%@'
    with Image.open(args.source) as original:
        original = original.convert('RGB')
        # Same sky detail at any source resolution; includes the moon and spiral.
        w, h = original.size
        box = (round(w * 50 / 1879), round(h * 90 / 1500),
               round(w * 1829 / 1879), round(h * 713 / 1500))
        sampled = original.crop(box).resize((columns, rows), Image.Resampling.BOX)
    pixels = [sampled.getpixel((x, y)) for y in range(rows) for x in range(columns)]
    luminance = [0.2126*r + 0.7152*g + 0.0722*b for r, g, b in pixels]
    ordered = sorted(luminance)
    low, high = ordered[len(ordered)//100], ordered[len(ordered)*99//100]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 560" role="img" aria-labelledby="title desc">',
        '<title id="title">The Starry Night — colored ASCII art</title>',
        '<desc id="desc">A panoramic sky detail of Vincent van Gogh’s 1889 painting, rebuilt from 160 columns and 28 rows of colored ASCII characters.</desc>',
        '<rect width="1600" height="560" fill="#0d1117"/>',
        '<g font-family="Menlo,DejaVu Sans Mono,Consolas,monospace" font-size="16" font-weight="400">',
    ]
    for index, (rgb, light) in enumerate(zip(pixels, luminance)):
        level = max(0.0, min(1.0, (light-low)/(high-low))) ** 0.8
        char = ramp[round(level*(len(ramp)-1))]
        if char == ' ':
            continue
        # Keep the original density calibration separate from the display color,
        # so this restrained grade never changes a character or its animation.
        density_rgb = tuple(min(255, round(channel*1.12+10)) for channel in rgb)
        density_color = '#'+''.join(f'{channel:02x}' for channel in density_rgb)
        color = '#'+''.join(f'{channel:02x}' for channel in color_grade(density_rgb))
        x = (index % columns) * cell_width + 1
        y = (index // columns) * cell_height + 16
        parts.append(f'<text x="{x}" y="{y}" fill="{color}" data-density-color="{density_color}">{escape(char)}</text>')
    parts.append('</g></svg>')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text('\n'.join(parts)+'\n', encoding='utf-8')
    print(f'{args.output}: {columns} columns × {rows} rows; SVG text only')


if __name__ == '__main__':
    main()
