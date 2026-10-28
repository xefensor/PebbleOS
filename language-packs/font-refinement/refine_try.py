from font_work import *
# acute, caron, side caron; patterns are pixels at native size.
PROFILES = {'GOTHIC_14': ('.#/#.', '#.#/.#.', '.#/.#/#.'),
 'GOTHIC_14_BOLD': ('.##/##.', '#..#/.##.', '##/##/#.'),
 'GOTHIC_18': ('..#/.#./#..', '#...#/.#.#./..#..', '.#/.#/#.'),
 'GOTHIC_18_BOLD': ('..##/.##./##..', '##..##/.####./..##..', '##/##/#.'),
 'GOTHIC_24': ('..#/.#./#..', '#...#/.#.#./..#..', '##/##/#./#.'),
 'GOTHIC_24_BOLD': ('..##/.##./##..', '##.##/.###./..#..', '##/##/#./#.'),
 'GOTHIC_28': ('..##/.##./.##./##..', '##...##/.##.##./..###../...#...', '##/##/#./#.'),
 'GOTHIC_28_BOLD': ('..###/.###./.###./###..', '##....##/.##..##./..####../...##...', '##/##/##/#./#.'),
 'GOTHIC_36': ('...##/..##./..##./.##../##...', '##...##/.##.##./..###../...#...', '###/###/##./##./#..'),
 'GOTHIC_36_BOLD': ('....###/...###./..###../.###.../###....',
                    '##....##/.##..##./..####../...##...',
                    '###/###/##./##./#..'),
 'BITHAM_30_BLACK': ('...###/..###./.###../.###../###...',
                     '###...###/.###.###./..#####../...###...',
                     '###/###/##./##./#..'),
 'BITHAM_42_BOLD': ('....####/...####./..####../.####.../.####.../####....',
                    '###.....###/.###...###./..###.###../...#####.../....###....',
                    '####/####/###./###./##../#...'),
 'BITHAM_42_LIGHT': ('...##/..##./..##./.##../##...', '##....##/.##..##./..####../...##...', '##/##/#./#.'),
 'DROID_SERIF_28_BOLD': ('..###/.###./.##../##...', '##...##/.##.##./..###..', '##/##/#.'),
 'ROBOTO_CONDENSED_21': ('.##/.##/##.', '#...#/.#.#./..#..', '##/##/#.')}
CHARS='ÁáÉéÍíÓóÚúÝýČčĎďĚěŇňŘřŠšŤťŽž'
def pixels(pattern):return {(x,y) for y,row in enumerate(pattern.split('/')) for x,c in enumerate(row) if c=='#'}
def refined(f,name):
 changes={}
 for c in CHARS:
  old=f.g[ord(c)];basechar,mark=unicodedata.normalize('NFD',c);base=f.g[ord(basechar)];bodytop=min(y for x,y in base['points'])
  if basechar=='i':
   ys=sorted({y for x,y in base['points']});bodytop=next(y for prev,y in zip(ys,ys[1:]) if y-prev>1)
  body={p for p in old['points'] if p[1]>=bodytop}
  side=c in 'ďť'
  if side:body=set(base['points'])
  pattern=PROFILES[name][2 if side else 0 if mark=='\u0301' else 1];accent=pixels(pattern);w=max(x for x,y in accent)+1;h=max(y for x,y in accent)+1
  if side:
   y0=bodytop-(1 if c=='ť' else 0)
   nearby=[x for x,y in body if y0-1<=y<=y0+h];x0=max(nearby)+2
  else:
   topink=[x for x,y in body if y<=bodytop+1]
   anchor=(min(topink)+max(topink))//2
   if mark=='\u0301':
    bottom=[x for x,y in accent if y==h-1];x0=anchor-(min(bottom)+max(bottom))//2
   else:x0=anchor-(w-1)//2
   y0=bodytop-1-h
  pts=body|{(x+x0,y+y0) for x,y in accent};left=min(x for x,y in pts);right=max(x for x,y in pts);top=min(y for x,y in pts);bottom=max(y for x,y in pts)
  oldright=max(x for x,y in old['points'])
  adv=old['advance']+max(0,right-oldright)
  if side:adv=max(base['advance'],right+1)
  width=right-left+1;height=bottom-top+1;bits=[int((x,y) in pts) for y in range(top,bottom+1) for x in range(left,right+1)]
  hf=height
  if f.flags&2:hf,bm=compress_rle4(bits)
  else:bm=bitlist_to_bytes(bits)
  assert hf<256
  raw=struct.pack('<BBbbb',width,hf,left,top,adv)+bm+b'\0'*((-len(bm))%4)
  changes[ord(c)]={'points':pts,'width':width,'height':height,'left':left,'top':top,'advance':adv,'raw':raw}
 return changes

def write(f,changes,path):
 head=f.data[:f.hs];ht=b'';ot=b'';gt=b'\0'*4;offsets={}
 for cp,g in sorted(f.g.items()):offsets[cp]=len(gt);gt+=changes.get(cp,g)['raw']
 for k in range(f.buckets):
  codes=sorted(c for c in f.g if c%f.buckets==k);ht+=struct.pack('<BBH',k,len(codes),len(ot))
  for c in codes:ot+=c.to_bytes(f.cp,'little')+offsets[c].to_bytes(f.es-f.cp,'little')
 path.write_bytes(head+ht+ot+gt)
if __name__=='__main__':
 out=setup();(out/'after').mkdir(exist_ok=True)
 label=ImageFont.truetype('DejaVuSans.ttf',16)
 for p in sorted((out/'before').glob('*.pbf')):
  f=Font(p.read_bytes());changes=refined(f,p.stem);dest=out/'after'/p.name;write(f,changes,dest);new=Font(dest.read_bytes())
  for c in f.g:
   if c not in changes:assert f.g[c]['raw']==new.g[c]['raw']
  ims=[]
  for txt in ['ÁáÉéÍíÓóÚúÝý ČčĎďĚěŇňŘřŠšŤťŽž Ůů','Příliš žluťoučký kůň úpěl ďábelské ódy.','ší ŠÍ čí ří ží ďá ťá íí ÚTERÝ ČTVRTEK']:
   for title,ft in [('Předchozí',Font((out/'previous'/p.name).read_bytes())),('Vyvážené',new)]:
    im=ft.render(txt);im=im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST);can=Image.new('RGB',(im.width+90,im.height),'#eeeeee');ImageDraw.Draw(can).text((3,5),title,font=label,fill='black');can.paste(im,(90,0));ims.append(can)
  sheet=Image.new('RGB',(max(im.width for im in ims),sum(im.height for im in ims)+28),'white');ImageDraw.Draw(sheet).text((6,4),p.stem,font=label,fill='black');y=28
  for im in ims:sheet.paste(im,(0,y));y+=im.height
  sheet.save(out/(p.stem+'.png'))
  print(p.stem,'changed',sum(f.g[c]['raw']!=new.g[c]['raw'] for c in f.g),'size',len(f.data),'->',dest.stat().st_size)
