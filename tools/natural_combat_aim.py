"""Controller aiming geometry read from original combat descriptors, not ROM patches."""
from functools import lru_cache
from run_core import ROOT
ROM=(ROOT/'input/original.sms').read_bytes()
BOXES=ROM[0x8100:0x8200]

@lru_cache(None)
def attacks(variant,direction):
 table=int.from_bytes(ROM[0x300a0+variant*8+direction*2:0x300a2+variant*8+direction*2],'little')
 indices=set()
 for animation in range(4,8):
  address=int.from_bytes(ROM[0x30000+(table&0x3fff)+animation*2:0x30002+(table&0x3fff)+animation*2],'little')
  indices.add(ROM[0x30000+(address&0x3fff)+2])
 return tuple(BOXES[i*4:i*4+4] for i in sorted(indices) if i)

def rectangle(x,y,box):
 if len(box)!=4 or not box[1] or not box[3]:return None
 # Source tests require carry when adding the unsigned negative offsets,
 # then reject a wrapped right/bottom end.
 left=x+box[0];top=y+box[2]
 if left<256 or top<256:return None
 left&=255;top&=255;right=left+box[1];bottom=top+box[3]
 if right>=256 or bottom>=256:return None
 return left,right,top,bottom

def intersects(a,b):
 return bool(a and b and a[0]<b[1] and a[1]>=b[0] and a[2]<b[3] and a[3]>=b[2])

def directions(point,enemy,variant,safe=True):
 if abs(point[0]-enemy['x'])>64 or abs(point[1]-enemy['y'])>64:return ()
 index=enemy.get('hit_box',0)
 if not index:return ()
 target=rectangle(enemy['x'],enemy['y'],BOXES[(index*4)&255:((index*4)&255)+4])
 if not target:return ()
 if safe:
  index=enemy.get('contact_box',0)
  danger=rectangle(enemy['x'],enemy['y'],BOXES[(index*4)&255:((index*4)&255)+4]) if index else None
  if intersects(rectangle(*point,BOXES[20:24]),danger):return ()
 return tuple(d for d in range(4) if any(intersects(rectangle(*point,box),target) for box in attacks(variant,d)))


def contact(point,enemy,horizon=0):
 index=enemy.get('contact_box',0)
 if not index:return False
 hero=rectangle(*point,BOXES[20:24]);box=BOXES[(index*4)&255:((index*4)&255)+4]
 for step in ([0,horizon//2,horizon] if horizon else [0]):
  x=int(enemy['x']+enemy.get('vx',0)*step)&255;y=int(enemy['y']+enemy.get('vy',0)*step)&255
  if intersects(hero,rectangle(x,y,box)):return True
 return False
