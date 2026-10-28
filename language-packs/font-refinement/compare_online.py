"""Render reference specimens; downloaded commercial fonts stay outside the repository."""
import argparse
import html
import json
import sys
import subprocess
import hashlib
from types import SimpleNamespace
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from font_work import Font

parser = argparse.ArgumentParser()
parser.add_argument('--references', type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parent
out = root / 'online-comparison'
out.mkdir(exist_ok=True)
source = root.parents[1] / 'resources/normal/base/lang/cs_CZ/pbf'
styles = [('fourteen-regular', 'GOTHIC_14', 14),
          ('fourteen-bold', 'GOTHIC_14_BOLD', 14),
          ('eighteen-regular', 'GOTHIC_18', 18),
          ('eighteen-bold', 'GOTHIC_18_BOLD', 18)]
samples = ['ÁáÉéÍíÓóÚúÝý ČčĎďĚěŇňŘřŠšŤťŽž Ůů',
           'Příliš žluťoučký kůň úpěl ďábelské ódy.']
parts = []


repo = root.parents[1]
revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
originals = {}
original_sources = []


def original_font(name):
    if name in originals:
        return originals[name]
    if name == 'ROBOTO_CONDENSED_21':
        from resources.resource_map.resource_generator_font import FontResourceGenerator
        ttf = repo / 'resources/normal/base/ttf/Roboto-Condensed.ttf'
        codepoints = repo / 'resources/normal/base/ttf/basic_latin_codepoints.json'
        for path in (ttf, codepoints):
            committed = subprocess.check_output(['git', 'show', revision + ':' + str(path.relative_to(repo))], cwd=repo)
            assert committed == path.read_bytes(), 'Reference input differs from HEAD: ' + str(path)
        definition = SimpleNamespace(name=name, compatibility='2.7', extended=False,
            max_glyph_size=512, character_regex=None, character_list=str(codepoints),
            compress=None, tracking_adjust=None, pixel_height=None)
        data = FontResourceGenerator.build_font_data(str(ttf), definition)
        if isinstance(data, list):
            data = b''.join(data)
        origin = str(ttf.relative_to(repo)) + ' + basic_latin_codepoints.json (projektový generátor)'
    else:
        candidates = [repo / 'resources' / directory / (name + '.pbf')
                      for directory in ('normal/base/pbf', 'common/base/pbf')]
        path = next(path for path in candidates if path.exists())
        origin = str(path.relative_to(repo))
        data = subprocess.check_output(['git', 'show', revision + ':' + origin], cwd=repo)
    font = Font(data)
    originals[name] = font
    original_sources.append({'font': name, 'revision': revision, 'source': origin,
                             'sha256': hashlib.sha256(data).hexdigest(),
                             'missing_czech': ''.join(c for c in samples[0] if ord(c) not in font.g)})
    return font


from font_candidate import make_candidate, CHOICES
candidates = {}


def candidate_font(name):
    if name not in candidates:
        refs = {
            'BITHAM_30_BLACK': (args.references / 'GothamSSm-Black.ttf', 29),
            'BITHAM_42_BOLD': (args.references / 'GothamSSm-Bold.ttf', 40),
            'BITHAM_42_LIGHT': (args.references / 'GothamSSm-Light.ttf', 40),
            'DROID_SERIF_28_BOLD': (repo / 'resources/normal/base/ttf/DroidSerif-Bold.ttf', 28),
            'ROBOTO_CONDENSED_21': (repo / 'resources/normal/base/ttf/Roboto-Condensed.ttf', 21),
        }
        path, size = refs.get(name, (None, None))
        ours = Font((source / (name + '.pbf')).read_bytes())
        candidates[name] = make_candidate(name, ours, original_font(name), path, size,
                                          out / 'candidates' / (name + '.pbf'))
    return candidates[name]


def original_image(name, sample, baseline, height, candidate=False):
    font = candidate_font(name) if candidate else original_font(name)
    ours = Font((source / (name + '.pbf')).read_bytes())
    advance = lambda c: font.g.get(ord(c), ours.g[ord(c)])['advance']
    im = Image.new('RGB', (sum(advance(c) for c in sample) + 8, height), 'white')
    draw = ImageDraw.Draw(im)
    y_offset = baseline - max(y for x, y in font.g[ord('H')]['points']) - 1
    x = 4
    for c in sample:
        glyph = font.g.get(ord(c))
        if glyph is None:
            draw.rectangle((x, baseline - 9, x + max(2, advance(c) - 2), baseline - 1), outline='#c62828')
        else:
            for a, b in glyph['points']:
                assert 0 <= x + a < im.width and 0 <= b + y_offset < height
                im.putpixel((x + a, b + y_offset), (0, 0, 0))
        x += advance(c)
    return im


def missing_note(name):
    font = original_font(name)
    missing = ''.join(c for c in samples[0] if ord(c) not in font.g)
    detail = 'Chybějící české znaky: ' + missing if missing else 'Původní font obsahuje všechny české znaky této ukázky.'
    origin = next(x['source'] for x in original_sources if x['font'] == name)
    return '<p><strong>Původní repo:</strong> ' + html.escape(origin) + '<br>' + html.escape(detail) + '</p>'


def picture(im, filename, label, alt):
    im.save(out / filename)
    return (f'<div class="row"><b>{html.escape(label)}</b><img src="{filename}" '
            f'data-w="{im.width}" data-h="{im.height}" '
            f'alt="{html.escape(alt)}"></div>')


for style, name, size in styles:
    ours = Font((source / (name + '.pbf')).read_bytes())
    reference = ImageFont.truetype(str(args.references / (style + '.ttf')), size)
    parts.append(f'<section><h2>{name}</h2>')
    parts.append(f'<p><a href="https://www.marksimonson.com/fonts/view/raster-gothic/{style}/">Raster Gothic {style}</a>, {size} px.</p>')
    parts.append(missing_note(name))
    for i, sample in enumerate(samples):
        # Align the baseline inferred from the bottom of H, preserving accent gaps.
        baseline = 32
        own = ours.render(sample)
        own_canvas = Image.new('RGB', (own.width, 46), 'white')
        own_canvas.paste(own, (0, baseline - max(y for x, y in ours.g[ord('H')]['points']) - 6))
        ref = Image.new('1', (int(reference.getlength(sample)) + 12, 46), 1)
        ImageDraw.Draw(ref).text((4, baseline), sample, font=reference, fill=0, anchor='ls')
        parts.append('<div class="sample">')
        parts.append(picture(ref, f'{name}-{i}-reference.png', 'Autor, online předloha', sample))
        parts.append(picture(original_image(name, sample, baseline, 46), f'{name}-{i}-original.png', 'Původní repo', sample))
        parts.append(picture(own_canvas, f'{name}-{i}-ours.png', 'Náš český PBF', sample))
        parts.append(picture(original_image(name, sample, baseline, 46 if name.startswith('GOTHIC') else 72, candidate=True), f'{name}-{i}-candidate.png', 'Nový návrh', sample))
        generated_path = root / 'generated-ttf' / f'{name}-{i}-generated.png'
        if name in ('ROBOTO_CONDENSED_21', 'DROID_SERIF_28_BOLD') and generated_path.exists():
            parts.append(picture(Image.open(generated_path), f'{name}-{i}-generated.png', 'Generováno z TTF', sample))
        parts.append('</div>')
    parts.append('<p><strong>Nový návrh:</strong> ' + CHOICES.get(name, 'Beze změny proti našemu českému PBF') + '</p>')
    parts.append('</section>')

# Compare outline references at the same rendered capital height as each PBF.
from fontTools.ttLib import TTFont
import hashlib

other_sources = []
findings = {
    'BITHAM_30_BLACK': 'Naše čárky a háčky jsou vůči silnému tělu písmen příliš subtilní. ScreenSmart Black má výrazně plnější znaménka a plošší háčky. Samotné prodloužení čárek tento rozdíl nevyřeší; rozhodující je tloušťka a tvar tahu.',
    'BITHAM_42_BOLD': 'Naše háčky mají tenčí ramena a hlubší tvar V. Předloha má háčky plošší a hmotnější; čárky více připomínají klín. Rozdíl je dobře patrný nad Č, Ě, Ř a Š.',
    'BITHAM_42_LIGHT': 'Tenká znaménka se k lehkému řezu hodí lépe než u Bold. Naše čárky jsou užší a háčky jemnější než v ScreenSmart Light. Rozdíly celé kresby připomínají, že ScreenSmart není totožná historická předloha.',
    'DROID_SERIF_28_BOLD': 'Projektová předloha má plnější, širší háčky a čárky s výraznějším klínovým tvarem. Naše znaménka jsou drobnější; zejména háčky by při dalším ladění měly lépe odpovídat váze patkového písma.',
    'ROBOTO_CONDENSED_21': 'Proporce jsou předloze bližší. Zůstávají rozdíly v šířce a umístění znamének a v bočních háčcích ď/ť. U této velikosti má i jeden pixel značný vliv.',
}

other_fonts = [
    ('BITHAM_30_BLACK', args.references / 'GothamSSm-Black.ttf', 30, 'Gotham ScreenSmart Black', 'https://www.typography.com/fonts/gotham/styles'),
    ('BITHAM_42_BOLD', args.references / 'GothamSSm-Bold.ttf', 42, 'Gotham ScreenSmart Bold', 'https://www.typography.com/fonts/gotham/styles'),
    ('BITHAM_42_LIGHT', args.references / 'GothamSSm-Light.ttf', 42, 'Gotham ScreenSmart Light', 'https://www.typography.com/fonts/gotham/styles'),
    ('DROID_SERIF_28_BOLD', source.parents[2] / 'ttf/DroidSerif-Bold.ttf', 28, 'Droid Serif Bold – projektový TTF', 'https://developer.rebble.io/guides/app-resources/system-fonts/'),
    ('ROBOTO_CONDENSED_21', source.parents[2] / 'ttf/Roboto-Condensed.ttf', 21, 'Roboto Condensed – projektový TTF', 'https://github.com/googlefonts/roboto-3-classic'),
]
parts.append('<h2 id="other-fonts">Bitham, Droid Serif a Roboto: česká diakritika</h2><p>Gotham je zde v obrazovkové variantě ScreenSmart (SSm), získané z veřejných webfontů výrobce. Jde o příbuznou oficiální předlohu, nikoli důkaz shody s historickým Gothamem použitým pro Bitham. Droid Serif a Roboto jsou vykreslené přímo z TTF uložených v tomto projektu, nikoli z dnešní odlišné verze Google Fonts.</p><p>Velikost TTF volíme tak, aby výška vykresleného H odpovídala PBF. Písmena neroztahujeme ani nezužujeme. Rozdíly ve šířce a proporcích proto zůstávají vidět. Vše je monochromatické; výsledek ovlivňuje také rasterizace.</p>')
for name, path, nominal, title, url in other_fonts:
    ours = Font((source / (name + '.pbf')).read_bytes())
    ys = [y for x, y in ours.g[ord('H')]['points']]
    cap_height = max(ys) - min(ys) + 1
    def rendered_height(size):
        f = ImageFont.truetype(str(path), size)
        im = Image.new('1', (120, 120), 0)
        ImageDraw.Draw(im).text((8, 90), 'H', font=f, fill=1, anchor='ls')
        box = im.getbbox()
        return box[3] - box[1]
    size = min(range(10, 71), key=lambda n: (abs(rendered_height(n) - cap_height), abs(n - nominal)))
    reference = ImageFont.truetype(str(path), size)
    ft = TTFont(path)
    cmap = ft.getBestCmap()
    assert all(ord(c) in cmap for sample in samples for c in sample)
    version = next((n.toUnicode() for n in ft['name'].names if n.nameID == 5), 'neuvedena')
    other_sources.append({'pbf': name, 'reference': title, 'filename': path.name, 'version': version, 'source': url, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'pixels': size, 'capital_height': cap_height, 'reference_capital_height': rendered_height(size), 'local_path': str(path.relative_to(root.parents[1])) if path.is_relative_to(root.parents[1]) else None, 'asset_url': 'https://www.typography.com/fonts/woff2/' + path.stem + '_Web.woff2' if name.startswith('BITHAM') else None})
    parts.append(f'<section id="{name}"><h2>{name}</h2><p><a href="{url}">{title}</a> · {size} px · výška H {cap_height} px · {html.escape(version)}</p>')
    parts.append('<p><strong>Hodnocení dosavadního návrhu (3. řádek):</strong> ' + findings[name] + '</p>')
    parts.append(missing_note(name))
    for i, sample in enumerate(samples):
        baseline = 54
        own = ours.render(sample)
        canvas = Image.new('RGB', (own.width, 72), 'white')
        canvas.paste(own, (0, baseline - max(ys) - 6))
        ref = Image.new('1', (int(reference.getlength(sample)) + 16, 72), 1)
        ImageDraw.Draw(ref).text((4, baseline), sample, font=reference, fill=0, anchor='ls')
        parts.append('<div class="sample">')
        parts.append(picture(ref, f'{name}-{i}-reference.png', 'Předloha', sample))
        parts.append(picture(original_image(name, sample, baseline, 72), f'{name}-{i}-original.png', 'Původní repo', sample))
        parts.append(picture(canvas, f'{name}-{i}-ours.png', 'Náš český PBF', sample))
        parts.append(picture(original_image(name, sample, baseline, 46 if name.startswith('GOTHIC') else 72, candidate=True), f'{name}-{i}-candidate.png', 'Nový návrh', sample))
        generated_path = root / 'generated-ttf' / f'{name}-{i}-generated.png'
        if name in ('ROBOTO_CONDENSED_21', 'DROID_SERIF_28_BOLD') and generated_path.exists():
            parts.append(picture(Image.open(generated_path), f'{name}-{i}-generated.png', 'Generováno z TTF', sample))
        parts.append('</div>')
    parts.append('<p><strong>Nový návrh:</strong> ' + CHOICES.get(name, 'Beze změny proti našemu českému PBF') + '</p>')
    parts.append('</section>')
(out / 'other-sources.json').write_text(json.dumps(other_sources, ensure_ascii=False, indent=2) + '\n')

parts.append('<h2>Ukázky z dokumentace Pebble</h2><p>Původní PNG obsahují také popisek a rozměry. Naše ukázka používá stejný text; rozložení řádků není kopií dokumentace. Tyto obrázky neobsahují diakritiku a slouží k porovnání základního vzhledu.</p>')
names = [name for _, name, _ in styles] + ['GOTHIC_24', 'GOTHIC_24_BOLD', 'GOTHIC_28', 'GOTHIC_28_BOLD', 'BITHAM_30_BLACK', 'BITHAM_42_BOLD', 'BITHAM_42_LIGHT', 'ROBOTO_CONDENSED_21', 'DROID_SERIF_28_BOLD']
for name in names:
    key = {'ROBOTO_CONDENSED_21': 'roboto_21_condensed', 'DROID_SERIF_28_BOLD': 'droid_28_bold'}.get(name, name.lower())
    reference = Image.open(args.references / (key + '.png')).convert('RGB')
    ours = Font((source / (name + '.pbf')).read_bytes())
    lines = [ours.render(s) for s in ['0123456789', 'ABCDEFabcdef']]
    own = Image.new('RGB', (max(im.width for im in lines), sum(im.height for im in lines)), 'white')
    y = 0
    for line in lines:
        own.paste(line, (0, y))
        y += line.height
    url = 'https://developer.rebble.io/assets/images/guides/app-resources/fonts/' + key + '_preview.png'
    parts.append(f'<section><h2>{name}</h2><p><a href="{url}">Zdrojový obrázek Pebble</a></p><div class="sample">')
    parts.append(picture(reference, name + '-pebble.png', 'Dokumentace Pebble', name + ' oficiální ukázka'))
    original = Image.new('RGB', own.size, 'white')
    offset = 0
    for sample, line in zip(['0123456789', 'ABCDEFabcdef'], lines):
        baseline = max(y for x, y in ours.g[ord('H')]['points']) + 6
        rendered = original_image(name, sample, baseline, line.height)
        original.paste(rendered, (0, offset))
        offset += line.height
    parts.append(picture(original, name + '-ascii-original.png', 'Původní repo', '0123456789 ABCDEFabcdef'))
    parts.append(picture(own, name + '-ascii.png', 'Náš český PBF', '0123456789 ABCDEFabcdef'))
    candidate = Image.new('RGB', own.size, 'white')
    offset = 0
    for sample, line in zip(['0123456789', 'ABCDEFabcdef'], lines):
        baseline = max(y for x, y in ours.g[ord('H')]['points']) + 6
        candidate.paste(original_image(name, sample, baseline, line.height, candidate=True), (0, offset))
        offset += line.height
    parts.append(picture(candidate, name + '-ascii-candidate.png', 'Nový návrh', '0123456789 ABCDEFabcdef'))
    parts.append('</div></section>')

prefix = '''<!doctype html><html lang="cs"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Raster Gothic a Pebble: porovnání fontů</title>
<style>body{font:16px system-ui;margin:24px;background:#f4f4f4;color:#171717}p,li{max-width:950px;line-height:1.5}header{position:sticky;top:0;background:#f4f4f4;padding:16px 0;z-index:1}section{background:white;padding:16px;margin:20px 0;border-radius:8px}.sample{overflow:auto}.row{display:flex;align-items:center;gap:16px;width:max-content}.row b{width:180px;font-size:14px}.row img{image-rendering:pixelated}h2{font-size:20px}</style>
<a href="../index.html">← Předchozí a vyvážený návrh</a> <a href="../pt2-candidate-check/index.html">Opravené fonty v PT2 emulátoru →</a><h1>Předloha · původní repo · náš český font · nový návrh</h1><p><a href="../generated-ttf/index.html">Actual firmware-generated Roboto and Droid Serif →</a> These two fonts also have a fifth row: Generováno z TTF.</p><p>Každá ukázka má čtyři řádky: předlohu, původní font repozitáře, naši dosavadní úpravu a nový návrh podle tvého výběru. Nový návrh zachovává těla písmen Pebble a přebírá vybranou diakritiku. U Bitham 30 Black jsou tahy předlohy zúžené o jeden pixel; u Bitham 42 Light zůstávají původní dostupné znaky a nové háčky navazují tenkými tahy. Fonty bez nového zadání zůstávají stejné. Návrh je pouze v galerii a souborech candidates/, instalační balíček se nemění. Původní PBF se čtou přímo z Git HEAD; nejde o dřívější návrh českého balíčku. Roboto je znovu sestaveno projektovým generátorem z TTF a seznamu znaků shodných s HEAD. Přesný commit a zdroje jsou v <a href="original-sources.json">metadatech původních fontů</a>.</p><p><strong>Červený rámeček znamená, že původní font znak vůbec neobsahuje.</strong> Je to značka této galerie, nikoli simulace náhradního vykreslení firmwaru. Šířka prázdného místa je převzatá z českého fontu; skutečné znaky mají původní rozestupy.</p><p><a href="#other-fonts">Přejít na Bitham, Droid Serif a Roboto →</a></p>
<p>Čtyři řezy Raster Gothic pocházejí z veřejného vzorníku Marka Simonsona (verze 2.2.0, načteno 8. 9. 2026). Z jejich skutečných webfontů jsou zde vykreslené monochromatické ukázky pomocí Pillow při 14 a 18 px. Nejde o screenshot prohlížeče ani o zaručeně totožnou historickou verzi použitou Pebblem. Současné PBF jsou z českého balíčku.</p>
<p>Řádky mají zarovnanou spodní hranu velkého H, takže lze porovnat i odstup znamének od písmene. Zvětšení pouze násobí pixely. Při 1× uvidíš původní velikost.</p>
<ul><li><strong>Gothic 14 Bold a 18 Bold:</strong> autorovy háčky jsou plošší; naše mají hlubší střed a výraznější tvar V. Stejná výška čárky a háčku tedy sama o sobě nezaručuje shodu s předlohou.</li><li><strong>Gothic 18 Regular:</strong> tvary čárek a háčků jsou bližší předloze. Rozdíly zůstávají v jejich umístění a u jednotlivých znaků.</li><li><strong>Ď/ď a Ť/ť:</strong> porovnej zvlášť boční znaménka a rozestupy. Online předloha a naše bitmapy se zde viditelně liší.</li></ul>
<p><a href="https://developer.rebble.io/guides/app-resources/system-fonts/">Dokumentace Pebble</a> uvádí Raster Gothic jako předlohu Gothic a Gotham jako předlohu Bitham. Bitham nyní porovnáváme také s Gotham ScreenSmart; omezení této reference jsou uvedena u příslušné sekce. Gothic 36 v citované galerii chybí a nemá zde přímé online porovnání. Zobrazení PBF rovněž nedokazuje, že je firmware na konkrétní obrazovce upřednostní před vestavěným fontem.</p>
<header><label>Zvětšení <input id="scale" type="range" min="1" max="6" value="3"> <output id="value">3×</output></label></header>
'''
suffix = '''<script>const s=document.getElementById('scale');function resize(){document.getElementById('value').textContent=s.value+'×';document.querySelectorAll('img').forEach(i=>{i.style.width=(i.dataset.w*s.value)+'px';i.style.height=(i.dataset.h*s.value)+'px'})}s.addEventListener('input',resize);resize();</script></html>'''
(out / 'original-sources.json').write_text(json.dumps(original_sources, ensure_ascii=False, indent=2) + '\n')
(out / 'index.html').write_text(prefix + ''.join(parts) + suffix)
(out / 'sources.json').write_text(json.dumps({'date': '2026-09-08', 'pebble': 'https://developer.rebble.io/guides/app-resources/system-fonts/', 'raster_gothic': 'https://www.marksimonson.com/fonts/view/raster-gothic/', 'version': '2.2.0', 'method': 'Pillow monochrome rendering at 14/18 px; baseline aligned using H; font files excluded'}, indent=2) + '\n')
print('Generated', out / 'index.html')
