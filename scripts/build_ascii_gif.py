"""Rasterize the shared ASCII frames for GitHub's JavaScript-free README.

Every colored pixel comes from a real Menlo glyph. No painting pixels are used.
The fixed global palette and four-level glyph masks avoid dithering between frames.

Usage: python scripts/build_ascii_gif.py [--font /path/to/monospace.ttf]
Requires Pillow. The website uses the same JSON frames directly in its canvas.
"""
from argparse import ArgumentParser
from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]


def find_font(explicit):
    candidates = [explicit] if explicit else [
        Path('/System/Library/Fonts/Menlo.ttc'),
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'),
        Path('/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf'),
        Path('C:/Windows/Fonts/consola.ttf'),
    ]
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate
    raise FileNotFoundError('Pass --font with the path to a monospace TTF or TTC font.')


def render_frames(data, font_path):
    colors = [tuple(bytes.fromhex(color)) for color in data['palette']]
    background = tuple(bytes.fromhex(data['background'].lstrip('#')))
    # Reserve four coverage levels for each of 63 sampled ink colors. This
    # preserves antialiased Menlo strokes without temporal or spatial dithering.
    swatches = Image.new('RGB', (len(colors), 1))
    swatches.putdata(colors)
    reduced = swatches.quantize(colors=63, method=Image.Quantize.MEDIANCUT,
                               dither=Image.Dither.NONE)
    raw_palette = reduced.getpalette()
    inks = [tuple(raw_palette[i:i+3]) for i in range(0, 63*3, 3)]
    mapping = [min(range(len(inks)), key=lambda i: sum(
        (a-b)**2 for a, b in zip(inks[i], color))) for color in colors]
    palette = [background]
    for ink in inks:
        for alpha in (64, 128, 192, 255):
            palette.append(tuple(round(bg+(fg-bg)*alpha/255)
                                 for fg, bg in zip(ink, background)))
    palette_bytes = [channel for color in palette for channel in color]
    palette_bytes += [0] * (768-len(palette_bytes))
    spec = data.get('font', {})
    font = ImageFont.truetype(str(font_path), spec.get('size', 16))
    # Menlo's antialiased right edge may extend one pixel past a cell; retain it
    # and paste through a binary occupancy mask so the adjacent cell cannot erase it.
    cell = (data['cellWidth']+1, data['cellHeight'])
    glyphs = {}
    for character in data['ramp']:
        mask = Image.new('L', cell)
        draw = ImageDraw.Draw(mask)
        draw.text((spec.get('offsetX', 1), spec.get('baseline', 16)),
                  character, font=font, anchor='ls', fill=255)
        coverages = [min(4, (value+32)//64) for value in mask.tobytes()]
        occupied = Image.frombytes('L', cell, bytes(255 if value else 0 for value in coverages))
        for color in range(len(inks)):
            tile = Image.new('P', cell)
            tile.putpalette(palette_bytes)
            tile.putdata([1+color*4+coverage-1 if coverage else 0
                          for coverage in coverages])
            glyphs[character, color] = (tile, occupied)
    frames = []
    for frame in data['frames']:
        canvas = Image.new('P', (data['width'], data['height']), color=0)
        canvas.putpalette(palette_bytes)
        for i, (character, color) in enumerate(zip(frame['characters'], frame['colorIndices'])):
            if character == ' ':
                continue
            position = (
                (i % data['columns']) * data['cellWidth'],
                (i // data['columns']) * data['cellHeight'],
            )
            tile, occupied = glyphs[character, mapping[color]]
            canvas.paste(tile, position, occupied)
        frames.append(canvas)
    return frames


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT/'assets/starry-night-frames.json')
    parser.add_argument('--output', type=Path, default=ROOT/'assets/starry-night-ascii.gif')
    parser.add_argument('--font', type=Path)
    parser.add_argument('--contact-sheet', type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    font_path = find_font(args.font)
    frames = render_frames(data, font_path)
    # GIF stores delays in centiseconds. Alternating 120/130 ms retains 8 fps
    # on average and the exact six-second period, without dropping any frames.
    tick_ms = 1000/data['fps']
    durations = [int((i+1)*tick_ms/10)*10-int(i*tick_ms/10)*10
                 for i in range(len(frames))]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(args.output, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, disposal=1, optimize=True)
    with Image.open(args.output) as gif:
        total = 0
        for i in range(gif.n_frames):
            gif.seek(i)
            total += gif.info['duration']
        assert gif.n_frames == len(frames), 'GIF encoder lost frames'
        assert gif.info['loop'] == 0, 'GIF must loop indefinitely'
        assert total == round(data['duration']*1000), 'GIF duration differs from source'
    if args.contact_sheet:
        thumb_size = (800, 280)
        sheet = Image.new('RGB', (1600, 620), data['background'])
        labels = ImageDraw.Draw(sheet)
        label_font = ImageFont.truetype(str(font_path), 16)
        for slot, index in enumerate([0, len(frames)//4, len(frames)//2, len(frames)*3//4]):
            x, y = (slot % 2)*800, (slot // 2)*310
            sheet.paste(frames[index].convert('RGB').resize(thumb_size, Image.Resampling.LANCZOS), (x, y))
            labels.text((x+12, y+287), f'FRAME {index:02d} / {index/data["fps"]:.1f}s',
                        font=label_font, fill='#a4aaa2')
        args.contact_sheet.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(args.contact_sheet)
    print(json.dumps({'output': str(args.output), 'frames': len(frames),
                      'dimensions': [data['width'], data['height']],
                      'duration_ms': sum(durations), 'loop': 0,
                      'bytes': args.output.stat().st_size, 'font': str(font_path)}))


if __name__ == '__main__':
    main()
