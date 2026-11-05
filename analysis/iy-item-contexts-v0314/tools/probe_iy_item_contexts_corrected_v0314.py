"""Expand source full-projectile-pool IY observations through hero item actions."""
import contextlib,ctypes as c,io,json
from run_core import ROOT,run
from validate_actor_tick import PRESSES
from archive_lossless_evidence import sha

def main():
 base=ROOT/'validation/iy-item-contexts-v0314-02';base.mkdir(exist_ok=False)
 core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_iytrace_libretro.dll'
 assert sha(core.read_bytes())=='5d59445cb53e515fc9b964921279d9303b3d68f1cddd79f57b1195f16d8c819a'
 dll=c.CDLL(str(core));dll.gaw_iytrace_size.restype=c.c_uint;dll.gaw_iytrace_data.restype=c.POINTER(c.c_uint);results=[]
 for action,item,level in [('axe1',1,1),('axe2',1,2),('sword2',0,2),('remedy',2,1),('lantern',3,1),('screen',6,1),('heal',7,1),('potion',8,1),('bell',10,1),('water-axe1',1,1),('water-axe2',1,2)]:
  for offset in(0,1,3):
   birth=2800+offset;e=bytearray(768);e[0]=0x64;e[1]=10;e[3]=0x43;e[4]=1;e[8]=0x13;e[9]=0x99;e[10]=1;e[12]=2;e[13]=40;e[0x11]=96;e[0x13]=128;e[0x18]=60;e[0x19]=20;e[0x1a]=4;e[0x20]=5
   for slot in range(8,16):
    at=slot*48;e[at]=0x73;e[at+0x11]=96;e[at+0x13]=128;e[at+10]=(slot-8)%5
   writes=[(2793,0xdf,bytes([item])),(2793,0xe0+item,bytes([level])),(2793,0x30a,b'\x03'),(birth,0x600,bytes(e)),(birth,0x310,(144<<8).to_bytes(2,'little')+(224<<8).to_bytes(2,'little')+bytes(4)),(birth,0xa2,b'\x09')]
   if item in(6,7):writes.append((2793,0xdb,b'\x40\x48'))
   if item in(7,8):writes.append((2793,0x318,b'\x08'))
   if item==2:writes.append((2793,0xbf,b'\x01'))
   if action.startswith('water-'):
    rom=(ROOT/'input/original.sms').read_bytes();groups=[]
    for j in range(5):
     at=0x2544+j*4;address=int.from_bytes(rom[at:at+2],'little');groups.append((rom[at+3],rom[address:address+rom[at+2]]))
    tile=next(tile for tile in range(256)if next((kind for kind,values in groups if tile in values),0)==3)
    writes += [(2793,0x1600,bytes([tile,0])*768),(2793,0xec,b'\x01'),(2793,0xf0,b'\x01')]
   presses=[(200,220,0)]+PRESSES[:8]+[(2794,2808,8)];out=base/f'{action}-{offset}';events=[];states=[];seen=0;previous=None;captures={birth-1,birth,birth+1,birth+120}
   dll.gaw_iytrace_reset()
   def observe(frame,raw):
    nonlocal seen,previous
    if frame==2792:assert raw[0x1d]==12
    if frame in(2792,2795,birth,birth+1,birth+30,birth+120):states.append(dict(frame=frame,game=raw[0x1d],hero=raw[0x301],spell=raw[0x330],spell_direction=raw[0x33a],selected=raw[0xdf],health=raw[0x318],magic=raw[0xdb],item_owned=raw[0xe0+item],curse=raw[0xbf],terrain=raw[0x41]))
    n=dll.gaw_iytrace_size();p=dll.gaw_iytrace_data()
    pool=([e[slot*48]for slot in range(8,16)]if frame==birth else[previous[0x600+slot*48]for slot in range(8,16)]if previous is not None else[])
    for i in range(seen,n):
     iy=p[i*8+2];at=(iy+10)&8191;before=previous[at]if previous is not None and iy>=0xc000 else None;after=raw[at]if iy>=0xc000 else None
     events.append(dict(frame=frame,iy=iy,value=p[i*8+3],ix=p[i*8+1],pool_before=pool,all_eight_slots_full=bool(pool and all(pool)),target_before_frame=before,target_after_frame=after,hero=raw[0x301],selected=raw[0xdf],spell=raw[0x330]))
     captures.update((frame,frame+1))
    seen=n;previous=bytes(raw)
   with contextlib.redirect_stdout(io.StringIO()):run(ROOT/'input/original.sms',birth+120,out,captures,presses,skip_intro=False,core=core,ram_writes=sorted(writes),ram_observer=observe)
   first_frame=min((r['frame']for r in events),default=None);first=[r for r in events if r['frame']==first_frame]
   after=[s for s in states if s['frame']>2793]
   activated=None
   if action.startswith('axe'):activated=any(s['hero']==5 for s in after)
   elif action=='sword2':activated=any(s['hero']==3 for s in after)
   elif action=='remedy':activated=any(s['curse']==0 and s['selected']==0 and s['item_owned']==0 for s in after)
   elif action=='screen':activated=any(s['magic']==32 for s in after)
   elif action=='heal':activated=any(s['health']==24 and s['magic']==40 for s in after)
   elif action=='potion':activated=any(s['health']==24 and s['selected']==0 and s['item_owned']==0 for s in after)
   elif action.startswith('water-'):activated=any(s['terrain']==3 and s['spell']==5 for s in after)
   if activated is not None:assert activated,(action,states)
   row=dict(action_activation_verified=activated,action=action,item=item,level=level,birth_frame=birth,first_fan=first,events=events,hero_states=states,incoming_iy_overridden=False)
   results.append(row);print(action,offset,'IY',sorted({r['iy']for r in first}),'fan',first_frame,'RAM changes',[(r['iy'],r['target_before_frame'],r['target_after_frame'])for r in first if r['target_before_frame']!=r['target_after_frame']],flush=True)
 report=dict(probe_passed=True,production_rom_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),trace_core_sha256=sha(core.read_bytes()),cases=results,controlled_fixture=True,natural_gameplay_proof=False,production_fix_applied=False,driver_sha256=sha(__import__('pathlib').Path(__file__).read_bytes()),supersedes_fixture_addresses_and_magic='Initial probe used C08F instead of actual curse C0BF and insufficient24MP for screen spell; those selected-only contexts are not active-action coverage.',scope='Original production-loop observations with explicit boss/full-pool/hero/item fixtures and ordinary C inputs. IY is never injected. First-fan frame-boundary target comparisons are finite observations; paused item actions may defer or omit the fan. No natural reachability or native bug is claimed.')
 (ROOT/'analysis/iy_item_contexts_corrected_v0314_report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
