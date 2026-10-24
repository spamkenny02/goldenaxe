"""Persistent clone cache, dirty flags and SMS scanline oracle."""
import ctypes as c,json,random
from validate_sms_sprite8 import ROOT,Frame,source_plane,native_plane,sha
from md_z80_source_video_fixture import convert_sms_patterns

def main():
 report=json.loads((ROOT/'analysis/sms_sprite8_report.json').read_bytes())
 for name,digest in report['sources'].items():assert sha((ROOT/'megadrive/src'/name).read_bytes())==digest
 lib=c.CDLL(str(ROOT/'validation/sms-sprite8/sprite8.dll'));p8=c.POINTER(c.c_uint8)
 update=lib.source_sms_sprite8_update;update.argtypes=[c.POINTER(Frame),p8,p8,c.c_uint8,c.c_uint8,c.c_uint8,c.c_uint16,p8,p8];update.restype=c.c_uint8
 frame=Frame();tiles=[[0]*8 for _ in range(64)];previous=bytes(16384);results=[]
 def check(name,sat,vram,r0,r1,r6,base=1024):
  nonlocal previous
  dirty=bytearray(64)
  for n in range(512):
   if vram[n*32:n*32+32]!=previous[n*32:n*32+32]:dirty[n>>3]|=1<<(n&7)
  y=(c.c_uint8*64).from_buffer_copy(sat[:64]);xt=(c.c_uint8*128).from_buffer_copy(sat[64:]);flags=(c.c_uint8*64)(*([0xa5]*64));raw=(c.c_uint8*64).from_buffer_copy(dirty)
  assert not update(c.byref(frame),y,xt,r0,r1,r6,base,raw,flags)
  packed=convert_sms_patterns(vram)
  for n in range(frame.count):
   assert flags[n] in [0,1]
   if flags[n]:
    tile=frame.source_tile[n]
    tiles[n]=[(int.from_bytes(packed[tile*32+r*4:tile*32+r*4+4],'big')&frame.columns[n]) if frame.rows[n]&(1<<r) else 0 for r in range(8)]
  expected,overflow,count=source_plane(sat,vram,r0,r6)
  assert frame.count==count and bool(frame.overflow)==overflow,name
  actual=native_plane(frame,tiles) if count else bytes(256*192)
  assert actual==expected,(name,'incremental cache pixels')
  previous=vram;results.append(dict(name=name,sprites=count,clones=sum(flags[:count]),pixel_sha256=sha(expected)))
 source=ROOT/'validation/sms-vertical-check'
 for f in range(3101,3161):
  v=(source/f'vram_{f:05d}.bin').read_bytes()[:16384];r=(source/f'vdp_regs_{f:05d}.bin').read_bytes();base=(r[5]&126)*128
  sat=v[base:base+64]+v[base+128:base+256];check('source-'+str(f),sat,v,r[0],r[1],r[6])
  check('source-noop-'+str(f),sat,v,r[0],r[1],r[6]);assert not results[-1]['clones']
 rng=random.Random(0x2768);v=bytearray(previous)
 for n in range(128):
  sat=bytearray(rng.randbytes(192));count=rng.choice([0,1,8,9,16,63,64]);r0=rng.choice([4,12,36,44]);r6=rng.choice([0,4]);base=rng.choice([768,1024])
  if count<64:sat[count]=208
  for _ in range(8):
   tile=rng.randrange(512);v[tile*32:tile*32+32]=rng.randbytes(32)
  check('random-'+str(n),sat,bytes(v),r0,224,r6,base)
  check('random-noop-'+str(n),sat,bytes(v),r0,224,r6,base);assert not results[-1]['clones']
 before=bytes(frame);flags=(c.c_uint8*64)(*([0xa5]*64));flags_before=bytes(flags);ys=(c.c_uint8*64)();xt=(c.c_uint8*128)();invalid=0
 for r0,r1,base in [(0,224,1024),(4,225,1024),(4,226,1024),(4,232,1024),(4,240,1024),(4,224,1985)]:
  assert update(c.byref(frame),ys,xt,r0,r1,0,base,None,flags)==1 and bytes(frame)==before and bytes(flags)==flags_before;invalid+=1
 frame.count=65;before=bytes(frame)
 assert update(c.byref(frame),ys,xt,4,224,0,1024,None,flags)==1 and bytes(frame)==before and bytes(flags)==flags_before;invalid+=1
 out=dict(passed=True,sources=report['sources'],cases=len(results),pixels_compared=len(results)*256*192,invalid_atomic_checks=invalid,results=results,limits=['Persistent clone cache and separate SAT inputs, real source snapshots followed by changing counts/masks/patterns/bases and no-op frames. Complete sprite pixels compared with independent SMS planar scanline oracle; no whole-game or physical deadline claim.'])
 (ROOT/'analysis/sms_sprite8_update_report.json').write_bytes((json.dumps(out,indent=2)+'\n').encode());print(out['cases'],'persistent sprite frames;',out['pixels_compared'],'pixels;',invalid,'atomic invalid checks')

if __name__=='__main__':main()
