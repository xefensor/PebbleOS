import struct,sys,unicodedata,json,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'tools');sys.path.insert(0,'tools/font')
from pbf_extract import decompress_rle4
from pbf_repack import bitlist_to_bytes,compress_rle4
class Font:
 def __init__(self,data):
  self.data=data;v,self.line,n,w,self.buckets,self.cp=struct.unpack_from('<BBHHBB',data); self.hs=10 if v==3 else 8;self.flags=data[9] if v==3 else 0;self.es=self.cp+(2 if self.flags&1 else 4); self.base=self.hs+4*self.buckets;self.gb=self.base+n*self.es;self.g={}
  for k in range(self.buckets):
   _,count,off=struct.unpack_from('<BBH',data,self.hs+k*4)
   for i in range(count):
    p=self.base+off+i*self.es;c=int.from_bytes(data[p:p+self.cp],'little');o=int.from_bytes(data[p+self.cp:p+self.es],'little')+self.gb
    width,height,left,top,advance=struct.unpack_from('<BBbbb',data,o);size=(height+1)//2 if self.flags&2 else (width*height+7)//8; raw=data[o:o+5+((size+3)//4)*4];bitsdata=raw[5:]
    if self.flags&2: bits,height=decompress_rle4(bitsdata,height,width)
    else: bits=[(bitsdata[j//8]>>(j%8))&1 for j in range(width*height)]
    pts={(left+x,top+y) for y in range(height) for x in range(width) if bits[y*width+x]}
    self.g[c]={'points':pts,'width':width,'height':height,'left':left,'top':top,'advance':advance,'raw':raw}
 def render(self,txt):
  im=Image.new('RGB',(sum(self.g[ord(c)]['advance'] for c in txt)+8,self.line+14),'white');px=im.load();x=4
  for c in txt:
   g=self.g[ord(c)]
   for a,b in g['points']:
    if 0<=x+a<im.width and 0<=b+5<im.height:px[x+a,b+5]=(0,0,0)
   x+=g['advance']
  return im

def setup():
 out=Path('language-packs/font-refinement');(out/'before').mkdir(parents=True,exist_ok=True)
 for p in Path('resources/normal/base/lang/cs_CZ/pbf').glob('*.pbf'):
  q=out/'before'/p.name
  if not q.exists():shutil.copyfile(p,q)
 from pbpack import ResourcePack
 with open('language-packs/cs_CZ-with-fonts.pbl','rb') as f:p=ResourcePack.deserialize(f,False)
 entry=p.table_entries[18];q=out/'before/ROBOTO_CONDENSED_21.pbf'
 if not q.exists():q.write_bytes(p.contents[entry.content_index])
 if not (out/'cs_CZ-before.pbl').exists():shutil.copyfile('language-packs/cs_CZ-with-fonts.pbl',out/'cs_CZ-before.pbl')
 return out
if __name__=='__main__':
 out=setup();label=ImageFont.truetype('/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf',16)
 imgs=[]
 for p in sorted((out/'before').glob('*.pbf')):
  f=Font(p.read_bytes());im=f.render('ÁáÉéÍíÓóÚúÝý ČčĎďĚěŇňŘřŠšŤťŽž Ůů');im=im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST)
  canvas=Image.new('RGB',(max(1600,im.width),im.height+28),'#eeeeee');ImageDraw.Draw(canvas).text((8,4),p.stem,font=label,fill='black');canvas.paste(im,(0,28));imgs.append(canvas)
  print(p.stem,[(c,(f.g[ord(c)]['width'],f.g[ord(c)]['height'],f.g[ord(c)]['left'],f.g[ord(c)]['top'])) for c in 'Aáčďťí'])
 big=Image.new('RGB',(max(x.width for x in imgs),sum(x.height for x in imgs)), 'white');y=0
 for im in imgs:big.paste(im,(0,y));y+=im.height
 big.save(out/'before-all.png')
