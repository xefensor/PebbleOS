"""Export review PBFs as bitmap-only BDFs, with explicit Pebble baseline metadata."""
import json
from pathlib import Path
from font_work import Font

root=Path(__file__).resolve().parent
out=root/'fontforge'
out.mkdir(exist_ok=True)
manifest=[]
for p in sorted((root/'online-comparison/candidates').glob('*.pbf')):
    font=Font(p.read_bytes());baseline=font.line
    all_points=[point for g in font.g.values() for point in g['points']]
    xmin=min(x for x,y in all_points);xmax=max(x for x,y in all_points)
    ymin=min(y for x,y in all_points);ymax=max(y for x,y in all_points)
    ascent=baseline;descent=max(0,ymax+1-baseline);strike_size=ascent+descent
    lines=['STARTFONT 2.1',f'FONT -Pebble-{p.stem}-Medium-R-Normal--{strike_size}-{strike_size*10}-72-72-P-0-ISO10646-1',f'SIZE {strike_size} 72 72',f'FONTBOUNDINGBOX {xmax-xmin+1} {ymax-ymin+1} {xmin} {baseline-ymax-1}','STARTPROPERTIES 5',f'FONT_ASCENT {ascent}',f'FONT_DESCENT {descent}','CHARSET_REGISTRY "ISO10646"','CHARSET_ENCODING "1"',f'PIXEL_SIZE {strike_size}','ENDPROPERTIES',f'CHARS {len(font.g)}']
    for cp,g in sorted(font.g.items()):
        w,h,left,top=g['width'],g['height'],g['left'],g['top']
        lines += [f'STARTCHAR uni{cp:04X}',f'ENCODING {cp}',f'SWIDTH {round(g["advance"]*1000/strike_size)} 0',f'DWIDTH {g["advance"]} 0',f'BBX {w} {h} {left} {baseline-top-h}','BITMAP']
        for y in range(top,top+h):
            row=0
            for x in range(left,left+w):row=(row<<1)|int((x,y) in g['points'])
            pad=(-w)%8
            lines.append(f'{row<<pad:0{((w+7)//8)*2}X}' if w else '')
        lines.append('ENDCHAR')
    lines.append('ENDFONT')
    dest=out/(p.stem+'.bdf')
    if dest.exists():raise SystemExit('Refusing to overwrite editable font: '+str(dest))
    dest.write_text('\n'.join(lines)+'\n')
    manifest.append({'name':p.stem,'pbf':str(p.relative_to(root)),'bdf':dest.name,'baseline':baseline,'glyphs':len(font.g)})
(out/'sources.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Exported',len(manifest),'fonts to',out)
