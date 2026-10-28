"""Temporarily stage preview resources and restore source files after the build."""
import json
import os
from pathlib import Path
import shutil
import subprocess

repo = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
build = repo / 'cmake-build-matrix/qemu_emery-normal'
cmake = '/home/xela/Aplikace/clion-2026.2.2/bin/cmake/linux/x64/bin/cmake'
candidates = out.parent / 'online-comparison/candidates'
names = ['GOTHIC_14','GOTHIC_14_BOLD','GOTHIC_18','GOTHIC_18_BOLD','BITHAM_30_BLACK','BITHAM_42_BOLD','BITHAM_42_LIGHT','DROID_SERIF_28_BOLD','ROBOTO_CONDENSED_21']
originals = {}
staged = {}

def stage(path, data):
    originals[path] = path.read_bytes() if path.exists() else None
    staged[path] = data
    path.write_bytes(data)

try:
    for name in names:
        if name in ('DROID_SERIF_28_BOLD', 'ROBOTO_CONDENSED_21'):
            continue
        path = repo / 'resources/normal/base/pbf' / (name + '.pbf')
        common = repo / 'resources/common/base/pbf' / (name + '.pbf')
        if common.exists(): path = common
        stage(path, (candidates / (name + '.pbf')).read_bytes())
    stage(repo / 'resources/normal/base/ttf/basic_latin_codepoints.json',
          (out.parent / 'generated-ttf/basic_latin_codepoints.json').read_bytes())
    path = repo / 'src/fw/apps/demo/font_test/font_test.c'
    source = path.read_text()
    start = source.index('static const FontEntry s_fonts[] = {')
    end = source.index('\n};',start) + 3
    source = source[:start] + 'static const FontEntry s_fonts[] = {\n' + ''.join('  { FONT_KEY_' + name + ', "' + name + '" },\n' for name in names) + '};' + source[end:]
    insert = '''\nstatic const char *s_samples[] = {
  "tťa\\nďá ťá\\nžluťoučký",
  "Aa Áá\\nEe Éé Ěě\\nIi Íí",
  "Cc Čč\\nDd Ďď\\nTt Ťť",
  "Nn Ňň\\nRr Řř\\nSs Šš",
  "Uu Úú Ůů\\nYy Ýý\\nZz Žž",
  "Příliš\\nžluťoučký\\nkůň úpěl",
  "ší ŠÍ\\nčí ří ží\\nďa ťa íí",
};\n'''
    source = source.replace('typedef struct {\n  Window window;', insert + '\ntypedef struct {\n  Window window;')
    source = source.replace('char glyph_buf[2];','char glyph_buf[160];')
    start = source.index('  sniprintf(data->info_buf')
    end = source.index('\n\n  text_layer_set_font',start)
    source = source[:start] + '''  sniprintf(data->info_buf, sizeof(data->info_buf), "Vzorek %u/%u",
           data->codepoint + 1, (unsigned int)ARRAY_LENGTH(s_samples));
  sniprintf(data->glyph_buf, sizeof(data->glyph_buf), "%s", s_samples[data->codepoint]);''' + source[end:]
    source = source.replace('FIRST_GLYPH','0').replace('LAST_GLYPH','(ARRAY_LENGTH(s_samples) - 1)')
    source = '\n'.join(line for line in source.split('\n') if not line.startswith('#define 0') and not line.startswith('#define (ARRAY_LENGTH'))
    source = source.replace('data->font_index = 0;', 'data->font_index = 7;').replace("data->codepoint = '0';", 'data->codepoint = 0;')
    stage(path, source.encode())
    (out / 'font_test.preview.c').write_text(source)
    env = dict(os.environ)
    env['PATH'] = str(repo / '.venv/bin') + ':' + str(Path(cmake).parent) + ':' + env['PATH']
    with (out / 'build.log').open('w') as log:
        subprocess.run([str(repo / '.venv/bin/pbl'), 'configure', '-b', str(build), '--board=qemu_emery', '-DCONFIG_DEMO_APP_FONT_TEST=y'], cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        subprocess.run([cmake,'--build',str(build),'--target','qemu_image_micro','qemu_image_spi','-j','6'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    for name in ['pebbleos.elf','qemu_spi_flash.bin','system_resources.resball']:
        shutil.copy2(build/name,out/name)
    print('Preview built and copied to',out)
finally:
    for path, data in originals.items():
        assert path.read_bytes() == staged[path], 'Concurrent edit detected: ' + str(path)
        if data is None: path.unlink()
        else: path.write_bytes(data)
    print('Staged source files restored.')
