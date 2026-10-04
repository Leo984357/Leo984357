"""Build a deterministic, seamless ASCII cloud animation from the static SVG.

Usage: python scripts/build_ascii_animation.py
Requires Pillow. The input SVG is never changed. The output contains 48 frames
at 8 fps, one shared palette, and a fixed 160 x 28 character grid per frame.

Each cloud has a small, smoothly tapered displacement field. Its radial and
tangential components travel around the swirl together, returning exactly to
their starting position after one period. This moves the painted character
texture itself; it is not a brightness overlay or a random character effect.
The moon and every cell outside the two cloud regions stay fixed.
"""

from argparse import ArgumentParser
from bisect import bisect_right
from collections import deque
from hashlib import sha256
import json
import math
from pathlib import Path
from statistics import median
import xml.etree.ElementTree as ET

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
COLUMNS, ROWS = 160, 28
CELL_WIDTH, CELL_HEIGHT = 10, 20
WIDTH, HEIGHT = 1600, 560
RAMP = ' .:-=+*#%@'
FRAMES, FPS = 48, 8
NS = {'svg': 'http://www.w3.org/2000/svg'}
EDDIES = (
    {'center': [90, 12], 'radius': [42, 10.5], 'twist': 0.105,
     'radial': 0.018, 'direction': 1, 'spiral': 2.3},
    {'center': [45, 9], 'radius': [25, 8.5], 'twist': 0.135,
     'radial': 0.021, 'direction': -1, 'spiral': 1.8},
)


def luminance(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def read_source(path):
    raw = path.read_bytes()
    svg = ET.fromstring(raw)
    if svg.attrib.get('viewBox') != '0 0 1600 560':
        raise ValueError('Expected a 1600 x 560 source SVG')
    characters = [' '] * (COLUMNS * ROWS)
    colors = [None] * len(characters)
    for glyph in svg.findall('.//svg:text', NS):
        character = glyph.text or ''
        x, y = float(glyph.attrib['x']), float(glyph.attrib['y'])
        column, row = round((x - 1) / CELL_WIDTH), round((y - 16) / CELL_HEIGHT)
        if (character not in RAMP or len(character) != 1
                or not 0 <= column < COLUMNS or not 0 <= row < ROWS
                or abs(x - (column * CELL_WIDTH + 1)) > 1e-8
                or abs(y - (row * CELL_HEIGHT + 16)) > 1e-8):
            raise ValueError('Source must contain one ASCII glyph per grid cell')
        index = row * COLUMNS + column
        if colors[index] is not None:
            raise ValueError('Duplicate source cell')
        color = glyph.attrib['fill'].lstrip('#')
        colors[index] = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        characters[index] = character

    # Spaces have no painted color in SVG. Extend the nearest sky color into
    # them so interpolation cannot introduce artificial black halos. Their
    # source character density remains exactly zero.
    queue = deque(index for index, color in enumerate(colors) if color is not None)
    while queue:
        index = queue.popleft()
        column, row = index % COLUMNS, index // COLUMNS
        neighbors = []
        if column > 0:
            neighbors.append(index - 1)
        if column + 1 < COLUMNS:
            neighbors.append(index + 1)
        if row > 0:
            neighbors.append(index - COLUMNS)
        if row + 1 < ROWS:
            neighbors.append(index + COLUMNS)
        for neighbor in neighbors:
            if colors[neighbor] is None:
                colors[neighbor] = colors[index]
                queue.append(neighbor)
    if any(color is None for color in colors):
        raise ValueError('Source has no visible glyphs')

    background = svg.find('svg:rect', NS).attrib['fill']
    return ''.join(characters), colors, background, sha256(raw).hexdigest()


def density_field(characters, colors):
    """Use source luminance while preserving every original character at t=0.

    The source uses a nonlinear luminance-to-character ramp. Calibrating its
    density anchors from the actual glyphs avoids assuming another contrast
    curve. A small per-cell residual retains smooth brightness information
    while staying safely inside the source character's rounding interval.
    """
    groups = [[] for _ in RAMP]
    for character, color in zip(characters, colors):
        if character != ' ':
            groups[RAMP.index(character)].append(luminance(color))
    anchors = [0.0]
    for rank in range(1, len(RAMP)):
        value = median(groups[rank]) if groups[rank] else anchors[-1] + 20
        anchors.append(max(value, anchors[-1] + 0.01))
    anchors[0] = max(0, anchors[1] - (anchors[2] - anchors[1]))
    values = []
    for character, color in zip(characters, colors):
        rank = RAMP.index(character)
        if rank == 0:
            values.append(0.0)
            continue
        light = luminance(color)
        lower = min(len(RAMP) - 2, max(0, bisect_right(anchors, light) - 1))
        measured = lower + (light - anchors[lower]) / (anchors[lower + 1] - anchors[lower])
        residual = max(-0.28, min(0.28, (measured - rank) * 0.65))
        values.append(max(0.0, min(len(RAMP) - 1.0, rank + residual)))
    return values


def prepare_fields():
    prepared = []
    for row in range(ROWS):
        for column in range(COLUMNS):
            local = []
            # Explicitly protect the moon, in addition to the eddy falloffs.
            if not (column > 138 and row < 15):
                for eddy in EDDIES:
                    cx, cy = eddy['center']
                    rx, ry = eddy['radius']
                    u, v = (column - cx) / rx, (row - cy) / ry
                    radius = math.hypot(u, v)
                    if 0 < radius < 1:
                        angle = math.atan2(v, u)
                        envelope = (1 - radius * radius) ** 3
                        spiral_phase = angle + eddy['spiral'] * radius
                        local.append((eddy, radius, angle, envelope, spiral_phase))
            prepared.append(local)
    return prepared


def source_position(column, row, fields, phase):
    x, y = float(column), float(row)
    for eddy, radius, angle, envelope, spiral_phase in fields:
        moving_phase = spiral_phase - eddy['direction'] * phase
        twist = eddy['twist'] * envelope * (math.sin(moving_phase) - math.sin(spiral_phase))
        radial = eddy['radial'] * envelope * (math.cos(moving_phase) - math.cos(spiral_phase))
        rx, ry = eddy['radius']
        displaced_radius = radius * (1 + radial)
        x += rx * (displaced_radius * math.cos(angle + twist) - radius * math.cos(angle))
        y += ry * (displaced_radius * math.sin(angle + twist) - radius * math.sin(angle))
    return max(0.0, min(COLUMNS - 1.0, x)), max(0.0, min(ROWS - 1.0, y))


def sample(colors, densities, x, y):
    left, top = math.floor(x), math.floor(y)
    right, bottom = min(left + 1, COLUMNS - 1), min(top + 1, ROWS - 1)
    fx, fy = x - left, y - top
    points = ((top * COLUMNS + left, (1 - fx) * (1 - fy)),
              (top * COLUMNS + right, fx * (1 - fy)),
              (bottom * COLUMNS + left, (1 - fx) * fy),
              (bottom * COLUMNS + right, fx * fy))
    rgb = tuple(sum(colors[index][channel] * weight for index, weight in points)
                for channel in range(3))
    density = sum(densities[index] * weight for index, weight in points)
    return rgb, density


def build_frames(characters, colors):
    densities = density_field(characters, colors)
    fields = prepare_fields()
    color_frames, density_frames = [], []
    maximum_displacement = 0.0
    for frame in range(FRAMES):
        phase = math.tau * frame / FRAMES
        rgb_frame, density_frame = [], []
        for index, local in enumerate(fields):
            column, row = index % COLUMNS, index // COLUMNS
            x, y = source_position(column, row, local, phase)
            maximum_displacement = max(maximum_displacement, math.hypot(x - column, 2 * (y - row)))
            rgb, density = sample(colors, densities, x, y)
            rgb_frame.append(tuple(round(channel) for channel in rgb))
            density_frame.append(density)
        color_frames.append(rgb_frame)
        density_frames.append(density_frame)

    # A circular temporal filter suppresses one-frame threshold crossings. The
    # tiny t=0 correction keeps the first frame's original character choices.
    smoothed = []
    for frame in range(FRAMES):
        previous = density_frames[(frame - 1) % FRAMES]
        current = density_frames[frame]
        following = density_frames[(frame + 1) % FRAMES]
        smoothed.append([(a + 2 * b + c) / 4 for a, b, c in zip(previous, current, following)])
    offsets = [source - smooth for source, smooth in zip(densities, smoothed[0])]
    character_frames = []
    for frame in range(FRAMES):
        output = []
        for density, offset in zip(smoothed[frame], offsets):
            rank = min(len(RAMP) - 1, max(0, math.floor(density + offset + 0.5)))
            output.append(RAMP[rank])
        character_frames.append(''.join(output))
    assert character_frames[0] == characters
    assert color_frames[0] == colors
    return character_frames, color_frames, fields, maximum_displacement


def shared_palette(color_frames):
    image = Image.new('RGB', (COLUMNS, ROWS * FRAMES))
    image.putdata([color for frame in color_frames for color in frame])
    indexed = image.quantize(colors=256, method=Image.Quantize.MEDIANCUT,
                             dither=Image.Dither.NONE)
    raw_palette = indexed.getpalette()
    palette = [''.join(f'{channel:02x}' for channel in raw_palette[index:index + 3])
               for index in range(0, 768, 3)]
    indices = list(indexed.getdata())
    count = COLUMNS * ROWS
    return palette, [indices[start:start + count] for start in range(0, len(indices), count)]


def validate(payload, source_characters, fields):
    frames = payload['frames']
    count = COLUMNS * ROWS
    assert len(frames) == FRAMES and len(payload['palette']) <= 256
    assert all(len(frame['characters']) == count and len(frame['colorIndices']) == count
               and set(frame['characters']).issubset(RAMP)
               and all(0 <= index < len(payload['palette']) for index in frame['colorIndices'])
               for frame in frames)
    assert frames[0]['characters'] == source_characters
    assert len({frame['characters'] for frame in frames}) == FRAMES
    frozen = [index for index, local in enumerate(fields) if not local]
    for frame in frames:
        assert all(frame['characters'][index] == source_characters[index]
                   and frame['colorIndices'][index] == frames[0]['colorIndices'][index]
                   for index in frozen)
    # Check the exact mathematical endpoint, which is not duplicated in JSON.
    endpoint_error = max(math.hypot(x - index % COLUMNS, y - index // COLUMNS)
                         for index, local in enumerate(fields)
                         for x, y in [source_position(index % COLUMNS, index // COLUMNS,
                                                       local, math.tau)])
    assert endpoint_error < 1e-10
    transitions = [sum(a != b for a, b in zip(frames[frame]['characters'],
                                              frames[(frame + 1) % FRAMES]['characters']))
                   for frame in range(FRAMES)]
    assert transitions[-1] <= max(transitions[:-1]) * 1.25
    return {'visibleSourceGlyphs': sum(character != ' ' for character in source_characters),
            'fixedCells': len(frozen), 'uniqueCharacterFrames': len(frames),
            'changedCellsPerStep': {'min': min(transitions), 'max': max(transitions),
                                    'loopSeam': transitions[-1]},
            'endpointErrorCells': endpoint_error}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'assets/starry-night-ascii.svg')
    parser.add_argument('--output', type=Path, default=ROOT / 'assets/starry-night-frames.json')
    args = parser.parse_args()
    characters, colors, background, source_hash = read_source(args.source)
    character_frames, color_frames, fields, displacement = build_frames(characters, colors)
    palette, index_frames = shared_palette(color_frames)
    payload = {
        'version': 1, 'columns': COLUMNS, 'rows': ROWS,
        'cellWidth': CELL_WIDTH, 'cellHeight': CELL_HEIGHT,
        'width': WIDTH, 'height': HEIGHT, 'fps': FPS, 'duration': FRAMES / FPS,
        'background': background, 'ramp': RAMP,
        'font': {'family': 'Menlo,DejaVu Sans Mono,Consolas,monospace',
                 'size': 16, 'weight': 400, 'offsetX': 1, 'baseline': 16},
        'palette': palette,
        'frames': [{'characters': character_frame, 'colorIndices': index_frame}
                   for character_frame, index_frame in zip(character_frames, index_frames)],
        'source': {'file': args.source.name, 'sha256': source_hash},
        'motion': {'algorithm': 'periodic-local-swirl-v1', 'eddies': EDDIES,
                   'frozenMoon': 'column > 138 and row < 15',
                   'maximumDisplacementCells': round(displacement, 6),
                   'seam': 'frame 48 equals frame 0; the endpoint is not duplicated'},
    }
    checks = validate(payload, characters, fields)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=True, separators=(',', ':')) + '\n')
    print(json.dumps({'output': str(args.output), 'bytes': args.output.stat().st_size,
                      'frames': FRAMES, 'fps': FPS, 'duration': FRAMES / FPS,
                      'maximumDisplacementCells': round(displacement, 6),
                      'validation': checks}, ensure_ascii=False))


if __name__ == '__main__':
    main()
