"""Extend each Bitham font's native hyphen stroke for the missing en dash."""

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "font-refinement"))
from font_work import Font as BitmapFont, bitlist_to_bytes, compress_rle4
from refine_try import write

root = ROOT
for name in ['BITHAM_30_BLACK','BITHAM_42_BOLD','BITHAM_42_LIGHT']:
 dest=root/'fonts'/f'{name}.pbf';b=BitmapFont(dest.read_bytes());g=b.g[ord('-')]
 left=g['left']; top=g['top'];width=max(g['width']+1,b.g[ord('n')]['advance']-2); height=g['height'];advance=width+2*left
 bits=[int((left+min(x,g['width']-1),top+y) in g['points']) for y in range(height) for x in range(width)]
 encoded_height,bitmap=(compress_rle4(bits) if b.flags&2 else (height,bitlist_to_bytes(bits)))
 raw=struct.pack('<BBbbb',width,encoded_height,left,top,advance)+bitmap+b'\0'*(-len(bitmap)%4)
 b.g[0x2013]={'raw':raw}
 head=bytearray(b.data);struct.pack_into('<H',head,2,len(b.g));b.data=bytes(head);write(b,{},dest)
