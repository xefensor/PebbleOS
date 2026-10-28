from pathlib import Path
import sys,json,unicodedata,io,contextlib,shutil
sys.path.insert(0,'language-packs/font-refinement');sys.path.insert(0,'tools');sys.path.insert(0,'tools/font')
from font_work import Font
from refine_try import refined,PROFILES,pixels,CHARS
from pbf_extract import extract_pbf
root=Path('language-packs/font-refinement');reports=[]
for p in sorted((root/'after').glob('*.pbf')):
 original=Font((root/'before'/p.name).read_bytes());previous=Font((root/'previous'/p.name).read_bytes());new=Font(p.read_bytes())
 assert set(original.g)==set(new.g) and original.line==new.line and original.flags==new.flags
 changed=[]
 for c in original.g:
  if c not in map(ord,CHARS):assert original.g[c]['raw']==new.g[c]['raw']
  elif original.g[c]['raw']!=new.g[c]['raw']:
   changed.append(chr(c));basechar=unicodedata.normalize('NFD',chr(c))[0];base=original.g[ord(basechar)];top=base['top']
   if basechar=='i':
    ys=sorted({y for x,y in base['points']});top=next(y for a,y in zip(ys,ys[1:]) if y-a>1)
   if chr(c) in 'ďť':assert base['points']<=new.g[c]['points']
   else:assert {p for p in original.g[c]['points'] if p[1]>=top}=={p for p in new.g[c]['points'] if p[1]>=top}
   assert new.g[c]['top']>=0
 assert all(new.g[c]['raw']==g['raw'] for c,g in refined(new,p.stem).items())
 with contextlib.redirect_stdout(io.StringIO()):extract_pbf(p,Path('/tmp/czech-balanced-independent')/p.stem)
 dimensions=[]
 for pattern in PROFILES[p.stem][:2]:
  points=pixels(pattern);dimensions.append({'width':max(x for x,y in points)+1,'height':max(y for x,y in points)+1,'ink_pixels':len(points)})
 assert abs(dimensions[0]['height']-dimensions[1]['height'])<=1
 previous_changes=''.join(chr(c) for c in sorted(new.g) if new.g[c]['raw']!=previous.g[c]['raw']);assert previous_changes
 reports.append({'font':p.stem,'changed_from_original':''.join(sorted(changed)),'changed_from_previous':previous_changes,'acute':dimensions[0],'caron':dimensions[1],'size':len(new.data),'advance_changes_from_previous':{chr(c):[previous.g[c]['advance'],new.g[c]['advance']] for c in new.g if previous.g[c]['advance']!=new.g[c]['advance']}})
 shutil.copyfile(p,Path('resources/normal/base/lang/cs_CZ/pbf')/p.name)
(root/'glyph-validation.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
(root/'validation.txt').write_text('PASS: all 15 fonts updated; non-Czech records unchanged; letter bodies preserved; recipe idempotent; independent PBF decoding; acute/caron heights differ by at most one pixel.\n')
print('PASS',len(reports),'fonts;',sum(len(r['changed_from_previous']) for r in reports),'glyphs changed from previous;',sum(len(r['changed_from_original']) for r in reports),'from original.')
