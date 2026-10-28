"""Compare actual firmware-generated Czech fonts with the current manual proposal."""
import hashlib
import html
import json
import sys
from pathlib import Path
from types import SimpleNamespace

from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent
repo = root.parents[1]
sys.path.insert(0, str(root))
sys.path.insert(0, str(repo / 'tools'))
from font_work import Font
from resources.resource_map.resource_generator_font import FontResourceGenerator

out = root / 'generated-ttf'
out.mkdir(exist_ok=True)
source = repo / 'resources/normal/base/ttf/basic_latin_codepoints.json'
original_list = json.loads(source.read_text())
characters = 'ÁáÉéÍíÓóÚúÝýČčĎďĚěŇňŘřŠšŤťŽžŮů'
codepoints = {int(c) for c in original_list['codepoints']} | set(map(ord, original_list['characters']))
added = sorted(set(map(ord, characters)) - codepoints)
codepoints.update(map(ord, characters))
expanded = {'characters': ''.join(map(chr, sorted(codepoints))), 'codepoints': list(map(str, sorted(codepoints)))}
expanded_path = out / 'basic_latin_codepoints.json'
expanded_path.write_text(json.dumps(expanded, ensure_ascii=False, indent=2) + '\n')
samples = ['ÁáÉéÍíÓóÚúÝý ČčĎďĚěŇňŘřŠšŤťŽž Ůů',
           'Příliš žluťoučký kůň úpěl ďábelské ódy.',
           'tťa ďá ťá ší ří íí ČTVRTEK ÚTERÝ',
           'AaBbEeGgIiMmRrTt 0123456789']
parts = []
metadata = []


def build(name, ttf, character_list):
    definition = SimpleNamespace(name=name, compatibility='2.7', extended=False,
        max_glyph_size=512, character_regex=None, character_list=str(character_list),
        compress=None, tracking_adjust=None, pixel_height=None)
    data = FontResourceGenerator.build_font_data(str(ttf), definition)
    return b''.join(data) if isinstance(data, list) else data


def aligned(font, text):
    # Same bottom of H as the main comparison gallery, without changing glyph metrics.
    shift = 54 - max(y for x, y in font.g[ord('H')]['points']) - 1
    im = Image.new('RGB', (sum(font.g[ord(c)]['advance'] for c in text) + 8, 72), 'white')
    x = 4
    for c in text:
        g = font.g[ord(c)]
        for a, b in g['points']:
            assert 0 <= x + a < im.width and 0 <= b + shift < im.height
            im.putpixel((x + a, b + shift), (0, 0, 0))
        x += g['advance']
    return im


for name, filename in [('ROBOTO_CONDENSED_21', 'Roboto-Condensed.ttf'), ('DROID_SERIF_28_BOLD', 'DroidSerif-Bold.ttf')]:
    ttf = source.parent / filename
    old_data = build(name, ttf, source)
    data = build(name, ttf, expanded_path)
    (out / (name + '.pbf')).write_bytes(data)
    before, generated = Font(old_data), Font(data)
    manual = Font((root / 'online-comparison/candidates' / (name + '.pbf')).read_bytes())
    assert all(ord(c) in generated.g for c in characters)
    assert all(before.g[cp]['points'] == generated.g[cp]['points'] and before.g[cp]['advance'] == generated.g[cp]['advance'] for cp in before.g)
    meta = {'font': name, 'source_ttf': str(ttf.relative_to(repo)), 'ttf_sha256': hashlib.sha256(ttf.read_bytes()).hexdigest(),
            'generated_sha256': hashlib.sha256(data).hexdigest(), 'original_bytes': len(old_data), 'generated_bytes': len(data),
            'added_codepoints': added, 'existing_glyphs_unchanged': True,
            'ascii_differences_from_manual': ''.join(chr(cp) for cp in range(32,127) if generated.g[cp]['points'] != manual.g[cp]['points'] or generated.g[cp]['advance'] != manual.g[cp]['advance'])}
    metadata.append(meta)
    parts.append(f'<section><h2>{name}</h2><p>Firmware PBF: {len(old_data):,} → {len(data):,} bajtů. Všechny dříve generované znaky zůstávají stejné; přibývá {len(added)} českých znaků.</p>')
    for i, text in enumerate(samples):
        parts.append('<div class="sample">')
        for key, label, font in [('candidate','Current proposal / současný návrh',manual),('generated','Generated TTF / automaticky z TTF',generated)]:
            im = aligned(font, text)
            filename = f'{name}-{i}-{key}.png'
            im.save(out / filename)
            parts.append(f'<div class="row"><b>{label}</b><img src="{filename}" data-w="{im.width}" data-h="{im.height}" alt="{html.escape(text)}"></div>')
        parts.append('</div>')
    parts.append('</section>')
header = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Firmware-generated Czech fonts</title><style>body{font:16px system-ui;margin:24px;background:#f4f4f4}p{max-width:960px;line-height:1.5}section{background:white;padding:16px;margin:20px 0}header{position:sticky;top:0;background:#f4f4f4;padding:12px;z-index:1}.sample{overflow:auto}.row{display:flex;align-items:center;gap:16px;width:max-content}.row b{width:180px;font-size:14px}img{image-rendering:pixelated}</style><a href="../online-comparison/index.html">← Full font comparison</a><h1>Actual firmware generation from TTF</h1><p><a href="../pt2-generated-check/index.html">PT2 emulator screenshots →</a></p><p>Current manual proposal versus the output of PebbleOS FontResourceGenerator, using the repository TTF files and an expanded character list. All 19 missing Czech characters are included. No manual accent editing or Pillow text rasterization is applied to the generated fonts; these images decode the generated PBF pixels.</p><p>The generated variant preserves every existing glyph from the current TTF build. Droid Serif may also differ in basic letter shapes from the manual proposal, because that proposal preserves the legacy PBF bodies, whereas the current firmware uses TTF generation. The final ASCII row makes this visible.</p><p>The character list used for this preview is a separate copy. Production firmware sources and installed language packs have not been changed. A separate PT2 test firmware now demonstrates this generated variant; see the emulator screenshots above. Rows align the bottom of H; glyphs retain their widths and spacing.</p><header>Scale <input id="scale" type="range" min="1" max="6" value="3"> <output id="value">3×</output></header>'''
footer = '''<script>const s=document.getElementById('scale');function resize(){document.getElementById('value').textContent=s.value+'×';document.querySelectorAll('img').forEach(i=>{i.style.width=i.dataset.w*s.value+'px';i.style.height=i.dataset.h*s.value+'px'})}s.addEventListener('input',resize);resize();</script></html>'''
(out / 'index.html').write_text(header + ''.join(parts) + footer)
(out / 'validation.json').write_text(json.dumps(metadata, indent=2) + '\n')
print(json.dumps(metadata, indent=2))
