"""Build review-only accent candidates, preserving Pebble letter bodies."""
import copy
import struct
import unicodedata
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from font_work import Font, bitlist_to_bytes, compress_rle4
from refine_try import write

CZECH = 'ÁáÉéÍíÓóÚúÝýČčĎďĚěŇňŘřŠšŤťŽžŮů'
CHOICES = {
    'GOTHIC_14': 'Původní repo',
    'GOTHIC_14_BOLD': 'Původní repo',
    'GOTHIC_18': 'Dosavadní český návrh',
    'GOTHIC_18_BOLD': 'Dosavadní český návrh',
    'BITHAM_30_BLACK': 'Gotham SSm Black; tahy znamének zúžené o jeden pixel',
    'BITHAM_42_BOLD': 'Diakritika Gotham SSm Bold',
    'BITHAM_42_LIGHT': 'Původní čárky repo; doplněné háčky ve stejné tloušťce',
    'DROID_SERIF_28_BOLD': 'Diakritika projektového Droid Serif Bold TTF',
    'ROBOTO_CONDENSED_21': 'Diakritika projektového Roboto Condensed TTF',
}


def outline_points(font, char):
    im = Image.new('1', (128, 160), 0)
    ImageDraw.Draw(im).text((24, 110), char, font=font, fill=1, anchor='ls')
    return {(x - 24, y - 110) for y in range(160) for x in range(128) if im.getpixel((x, y))}


def body_for(font, char):
    basechar = unicodedata.normalize('NFD', char)[0]
    base = font.g[ord(basechar)]['points']
    top = min(y for x, y in base)
    if basechar == 'i':
        rows = sorted({y for x, y in base})
        top = next(y for previous, y in zip(rows, rows[1:]) if y - previous > 1)
    if char in 'ďť':
        return set(base), top
    return {p for p in font.g[ord(char)]['points'] if p[1] >= top}, top


def shrink_runs(points):
    result = set()
    for y in sorted({y for x, y in points}):
        xs = sorted(x for x, row in points if row == y)
        groups = []
        for x in xs:
            if not groups or x != groups[-1][-1] + 1:
                groups.append([])
            groups[-1].append(x)
        for group in groups:
            # Preserve position and connected tips; remove only one edge pixel.
            if len(group) > 2:
                group = group[:-1]
            result.update((x, y) for x in group)
    return result


def largest_component(points):
    remaining = set(points)
    components = []
    while remaining:
        pending = [remaining.pop()]
        component = set(pending)
        while pending:
            x, y = pending.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    point = (x + dx, y + dy)
                    if point in remaining:
                        remaining.remove(point)
                        component.add(point)
                        pending.append(point)
        components.append(component)
    return max(components, key=len)


def record(font, old, points, advance):
    left = min(x for x, y in points)
    top = min(y for x, y in points)
    width = max(x for x, y in points) - left + 1
    height = max(y for x, y in points) - top + 1
    bits = [int((x, y) in points) for y in range(top, top + height) for x in range(left, left + width)]
    encoded_height = height
    if font.flags & 2:
        encoded_height, bitmap = compress_rle4(bits)
    else:
        bitmap = bitlist_to_bytes(bits)
    raw = struct.pack('<BBbbb', width, encoded_height, left, top, advance) + bitmap
    raw += b'\0' * (-len(bitmap) % 4)
    return dict(old, points=points, left=left, top=top, width=width, height=height, advance=advance, raw=raw)


def make_candidate(name, ours, original, reference_path, reference_size, output):
    changes = {}
    if name in ('GOTHIC_14', 'GOTHIC_14_BOLD'):
        for char in CZECH:
            glyph = original.g[ord(char)]
            changes[ord(char)] = record(ours, ours.g[ord(char)], glyph['points'], glyph['advance'])
    elif name in CHOICES and name not in ('GOTHIC_18', 'GOTHIC_18_BOLD'):
        ref = ImageFont.truetype(str(reference_path), reference_size)
        for char in CZECH:
            old = ours.g[ord(char)]
            if name == 'BITHAM_42_LIGHT' and ord(char) in original.g:
                glyph = original.g[ord(char)]
                changes[ord(char)] = record(ours, old, glyph['points'], glyph['advance'])
                continue
            basechar, mark = unicodedata.normalize('NFD', char)
            body, top = body_for(ours, char)
            ref_base = outline_points(ref, 'ı' if basechar == 'i' else basechar)
            ref_char = outline_points(ref, char)
            ref_top = min(y for x, y in ref_base)
            if char in 'ďť':
                # Precomposed side-caron forms can shift their base horizontally.
                shift = max(range(-4, 5), key=lambda dx: len({(x + dx, y) for x, y in ref_base} & ref_char))
                accent = ref_char - {(x + shift, y) for x, y in ref_base}
                # Keep the side mark, never rasterization differences at the baseline.
                accent = {(x, y) for x, y in accent if y < ref_top + max(6, reference_size // 3)}
                # Discard detached crossbar residues from the reference's t shape.
                accent = largest_component(accent)
                x_offset = max(x for x, y in body if y < top + 5) + 2 - min(x for x, y in accent)
            else:
                accent = {p for p in ref_char if p[1] < ref_top}
                ref_center = (min(x for x, y in ref_base) + max(x for x, y in ref_base)) / 2
                body_center = (min(x for x, y in body) + max(x for x, y in body)) / 2
                x_offset = round(body_center - ref_center)
            if name == 'BITHAM_30_BLACK':
                accent = shrink_runs(accent)
            if name == 'BITHAM_42_LIGHT':
                # Existing light acutes use a mostly 1–2 pixel diagonal stroke.
                # Use compact carons with matching strokes and preserve current rings.
                if mark == '\u030a':
                    continue
                if mark == '\u0301':
                    repo_acute = original.g[ord('Á')]['points']
                    repo_top = min(y for x, y in original.g[ord('A')]['points'])
                    a = {(x, y) for x, y in repo_acute if y < repo_top}
                    x_offset = round((min(x for x, y in body) + max(x for x, y in body)) / 2 - (min(x for x, y in original.g[ord('A')]['points']) + max(x for x, y in original.g[ord('A')]['points'])) / 2)
                    accent = {(x, y - repo_top + ref_top) for x, y in a}
                elif char not in 'ďť':
                    accent = shrink_runs(accent)
            placed = {(x + x_offset, y - ref_top + top) for x, y in accent}
            assert placed, (name, char)
            points = body | placed
            # Expanded side marks require room before the following letter.
            advance = max(old['advance'], max(x for x, y in points) + 1)
            assert min(y for x, y in points) >= 0, (name, char, 'accent exceeds font ascent')
            changes[ord(char)] = record(ours, old, points, advance)
            assert body <= points
    output.parent.mkdir(exist_ok=True)
    write(ours, changes, output)
    result = Font(output.read_bytes())
    for cp in ours.g:
        if chr(cp) not in CZECH:
            assert result.g[cp]['raw'] == ours.g[cp]['raw'], (name, cp)
    return result
