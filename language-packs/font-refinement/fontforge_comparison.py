"""Prepare distinctly named bitmap references for side-by-side FontForge review."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from font_work import Font
from resources.resource_map.resource_generator_font import FontResourceGenerator

root=Path(__file__).resolve().parent
repo=root.parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--references',type=Path,required=True)
args=parser.parse_args()
out=root/'fontforge/comparison'
revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
refs={
 'GOTHIC_14':('fourteen-regular.ttf',14,'Raster Gothic Fourteen Regular'),
 'GOTHIC_14_BOLD':('fourteen-bold.ttf',14,'Raster Gothic Fourteen Bold'),
 'GOTHIC_18':('eighteen-regular.ttf',18,'Raster Gothic Eighteen Regular'),
 'GOTHIC_18_BOLD':('eighteen-bold.ttf',18,'Raster Gothic Eighteen Bold'),
 'BITHAM_30_BLACK':('GothamSSm-Black.ttf',29,'Gotham ScreenSmart Black'),
 'BITHAM_42_BOLD':('GothamSSm-Bold.ttf',40,'Gotham ScreenSmart Bold'),
 'BITHAM_42_LIGHT':('GothamSSm-Light.ttf',40,'Gotham ScreenSmart Light'),
 'DROID_SERIF_28_BOLD':(str(repo/'resources/normal/base/ttf/DroidSerif-Bold.ttf'),28,'Droid Serif – projektový TTF'),
 'ROBOTO_CONDENSED_21':(str(repo/'resources/normal/base/ttf/Roboto-Condensed.ttf'),21,'Roboto Condensed – projektový TTF'),
}


def export(font,name,role):
    dest=out/role/(name+'__'+role+'.bdf')
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():raise RuntimeError('Refusing to overwrite '+str(dest))
    points=[p for g in font.g.values() for p in g['points']]
    xmin=min(x for x,y in points);xmax=max(x for x,y in points)
    ymin=min(y for x,y in points);ymax=max(y for x,y in points)
    baseline=font.line;descent=max(0,ymax+1-baseline);size=baseline+descent
    family=name+'__'+role
    lines=['STARTFONT 2.1',f'FONT -PebbleAudit-{family}-Medium-R-Normal--{size}-{size*10}-72-72-P-0-ISO10646-1',f'SIZE {size} 72 72',f'FONTBOUNDINGBOX {xmax-xmin+1} {ymax-ymin+1} {xmin} {baseline-ymax-1}','STARTPROPERTIES 7',f'FONT_ASCENT {baseline}',f'FONT_DESCENT {descent}','CHARSET_REGISTRY "ISO10646"','CHARSET_ENCODING "1"',f'PIXEL_SIZE {size}',f'FAMILY_NAME "{family}"',f'FACE_NAME "{family}"','ENDPROPERTIES',f'CHARS {len(font.g)}']
    for cp,g in sorted(font.g.items()):
        w,h,left,top=g['width'],g['height'],g['left'],g['top']
        lines += [f'STARTCHAR uni{cp:04X}',f'ENCODING {cp}',f'SWIDTH {round(g["advance"]*1000/size)} 0',f'DWIDTH {g["advance"]} 0',f'BBX {w} {h} {left} {baseline-top-h}','BITMAP']
        for y in range(top,top+h):
            bits=0
            for x in range(left,left+w):bits=(bits<<1)|int((x,y) in g['points'])
            lines.append(f'{bits<<((-w)%8):0{((w+7)//8)*2}X}' if w else '')
        lines.append('ENDCHAR')
    lines.append('ENDFONT');dest.write_text('\n'.join(lines)+'\n')
    return str(dest.relative_to(out))


def raster_reference(path,size,baseline,codes):
    font=ImageFont.truetype(str(path),size);cmap=TTFont(path).getBestCmap();glyphs={}
    for cp in codes:
        if cp not in cmap:continue
        im=Image.new('1',(160,200));ImageDraw.Draw(im).text((30,120),chr(cp),font=font,fill=1,anchor='ls')
        pts={(x-30,y-120+baseline) for y in range(200) for x in range(160) if im.getpixel((x,y))}
        if pts:
            left=min(x for x,y in pts);top=min(y for x,y in pts);w=max(x for x,y in pts)-left+1;h=max(y for x,y in pts)-top+1
        else:left=top=w=h=0
        glyphs[cp]=dict(points=pts,left=left,top=top,width=w,height=h,advance=round(font.getlength(chr(cp))))
    return SimpleNamespace(line=baseline,g=glyphs)


manifest=[]
for path in sorted((root/'online-comparison/candidates').glob('*.pbf')):
    name=path.stem;ours=Font(path.read_bytes())
    if name=='ROBOTO_CONDENSED_21':
        ttf=repo/'resources/normal/base/ttf/Roboto-Condensed.ttf';codes=ttf.parent/'basic_latin_codepoints.json'
        for p in [ttf,codes]:assert p.read_bytes()==subprocess.check_output(['git','show',revision+':'+str(p.relative_to(repo))],cwd=repo)
        d=SimpleNamespace(name=name,compatibility='2.7',extended=False,max_glyph_size=512,character_regex=None,character_list=str(codes),compress=None,tracking_adjust=None,pixel_height=None)
        data=FontResourceGenerator.build_font_data(str(ttf),d);data=b''.join(data) if isinstance(data,list) else data
        origin='TTF + original character list (firmware generator)'
    else:
        p=next(repo/'resources'/folder/path.name for folder in ['normal/base/pbf','common/base/pbf'] if (repo/'resources'/folder/path.name).exists())
        origin=str(p.relative_to(repo));data=subprocess.check_output(['git','show',revision+':'+origin],cwd=repo)
    original=Font(data)
    entry={'name':name,'revision':revision,'repo_source':origin,'repo_sha256':hashlib.sha256(data).hexdigest(),'ours_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'files':[export(original,name,'1_REPO'),export(ours,name,'3_NASE')]}
    if name in refs:
        filename,size,label=refs[name];reference_path=args.references/filename
        reference=raster_reference(reference_path,size,ours.line,set(ours.g)|set(original.g))
        entry['files'].append(export(reference,name,'2_PREDLOHA'))
        entry['reference']=label;entry['reference_size']=size;entry['reference_sha256']=hashlib.sha256(reference_path.read_bytes()).hexdigest()
    manifest.append(entry)
(out/'sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Created',sum(len(x['files']) for x in manifest),'BDFs;',len(refs),'complete triplets.')
