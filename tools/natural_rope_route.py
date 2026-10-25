"""Deploy acquired magic rope through ordinary input after a verified campaign prefix."""
import argparse,contextlib,io,json
from pathlib import Path
from run_core import ROOT,run
from natural_dungeon_route import World
from assisted_prefix import prefix_writes
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence

def main():
 p=argparse.ArgumentParser();p.add_argument('--sms',action='store_true');p.add_argument('--prefix',required=True);p.add_argument('--assisted-prefix',action='store_true');p.add_argument('--trial',required=True);p.add_argument('--frames',type=int,required=True);a=p.parse_args()
 base=ROOT/'validation/natural-dungeon-combat'/a.prefix;capture=json.loads((base/'capture.json').read_bytes());prior=json.loads((base/'report.json').read_bytes());controls=json.loads((base/'controls.json').read_bytes())
 assert prior['full_dungeon_cleared'] and prior['failure'] is None and not prior['deaths']
 rom=ROOT/('input/original.sms' if a.sms else 'gaw-megadrive.bin');assert capture['rom_sha256']==sha(rom.read_bytes())
 writes=prefix_writes(base,capture,a.assisted_prefix);assert not writes or max(f for f,_,_ in writes)<capture['frames']
 sy=None if a.sms else symbols(ROOT/'megadrive/out/release/symbol.txt');start=capture['frames'];prefix_ram=evidence(base/f'ram_{start:05d}.bin');timeline=[()]*(start+1)
 for i,r in enumerate(controls):
  end=controls[i+1]['frame']-1 if i+1<len(controls) else start
  timeline[r['frame']:end+1]=[tuple(r['buttons'])]*(end-r['frame']+1)
 world=World(3);world.goal=dict(room=0x41,x=104,y=80,target=0x41)
 state={};path=[];cursor=0;last_progress=start;done=None;failure=None;observed=0;before=None;expected=None;expected_work=None;rows=[];activated=None;events=[];captures=set();all_controls=[];cached=-1;buttons=[];previous=None
 tag='sms' if a.sms else 'md';out=ROOT/f'validation/natural-rope-route/{tag}-{a.trial}';assert not out.exists();out.mkdir(parents=True);driver=Path(__file__).read_bytes();(out/'route_driver.py').write_bytes(driver)
 def observe(f,r):
  nonlocal before,expected,expected_work,activated,done,failure,observed,previous
  observed=f
  if a.sms:
   cells=bytes(r[0x1c00:0x1d00]);work=bytes(r[0x98:0x9c]);tilemap=bytes(r[0x1600:0x1b00]);meta=bytes(r[0x900:0x1100]);owned=r[0xed]
   state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],x=r[0x313],y=r[0x311],health=r[0x318],maze=r[0x6c])
  else:
   data=lambda n,k:bytes(r[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
   cells=data('scratch',4096)[0x800:0x900];work=data('magic_rope_work',4);tilemap=data('sms_vram',16384)[0x3800:0x3d00];meta=data('scratch',2048);owned=data('hero_items',17)[13]
   state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),x=word('hero_x')>>8,y=word('hero_y')>>8,health=word('hero_health'),maze=data('forest_maze_progress',1)[0])
  if f<start:return
  if f==start:assert r==prefix_ram,('prefix replay RAM mismatch',f,dict(state))
  if not state['health'] or state['game']==20:failure='hero_died'
  key=(state['room'],state['game'],state['health'])
  if key!=previous:events.append(dict(frame=f,**state));previous=key;captures.add(f+1)
  assert owned,('The acquired rope must be present; no inventory fixture is injected',f,dict(state))
  if before is None and state['room']==0x41 and state['x']==104 and state['y']==88 and not state['counter']:
   before=dict(frame=f,cells=cells.hex(),map=tilemap.hex(),position=dict(state));changed=bytearray(cells);index=0x46;count=1
   assert changed[index]==2
   changed[index]=0x6d
   while index>=16 and changed[index-16]==12:index-=16;changed[index]=0x6c;count+=1
   expected=bytes(changed);expected_work=bytearray([3,count*2,72,96]);captures.add(f+1)
  if expected is not None and cells[0x46]==0x6d:
   indices=[i for i,(a,b) in enumerate(zip(bytes.fromhex(before['cells']),expected)) if a!=b]
   assert all(cells[i]==expected[i] for i in indices),('rope column',f)
   if activated is None:(out/'activation_differences.json').write_text(json.dumps(dict(frame=f,work=work.hex(),other_cell_differences=[i for i,(a,b) in enumerate(zip(cells,expected)) if a!=b]),indent=2)+'\n')
   if activated is None:activated=f
   if expected_work[0]:
    y,x=expected_work[2:4];offset=y*8+x//4;cell=expected[(y&240)|(x>>4)];data=meta[cell*8+((y&8)>>1):cell*8+((y&8)>>1)+4]
    assert tilemap[offset:offset+4]==data,('progressive map',f)
    rows.append(dict(frame=f,offset=offset,data_hex=data.hex()))
    expected_work[2]=(y-8)&255;expected_work[1]-=1
    if not expected_work[1]:expected_work[0]=0
   assert work==expected_work,('animation work',f,work.hex(),expected_work.hex())
   if work[0]==0 and state['y']<=72 and done is None:done=f;captures.add(f+100)
 def choose(f):
  nonlocal path,cursor,last_progress,failure
  buttons=[]
  if f<=start:return list(timeline[f])
  if failure or done is not None:return buttons
  if state['game']!=12 or state['hero']!=1:return buttons
  point=(state['room'],state['x'],state['y'])
  if before is not None:return [4]
  if not path:
   path,visited=world.route((*point,state['maze']));assert path is not None
  while cursor<len(path) and point==tuple(path[cursor][2][:3]):cursor+=1;last_progress=f
  if cursor==len(path):return [4]
  previous,d,nxt=path[cursor]
  if not state['counter'] and point!=tuple(previous[:3]):
   path,visited=world.route((*point,state['maze']));cursor=0;last_progress=f
   if not path:failure='route_lost';return []
   previous,d,nxt=path[0]
  if f-last_progress>600:failure='route_stalled';return []
  return [4+d]
 def controller(f):
  nonlocal cached,buttons
  if f==cached:return buttons
  cached=f;buttons=choose(f)
  if not all_controls or all_controls[-1]['buttons']!=buttons:all_controls.append(dict(frame=f,buttons=buttons))
  return buttons
 with contextlib.redirect_stdout(io.StringIO()):run(rom,a.frames,out,captures,capture['presses'],ram_writes=writes,skip_intro=False,ram_observer=observe,input_provider=controller,stop_when=lambda:bool(failure) or done is not None and observed>=done+100,core_options=capture['core_options'])
 if writes:(out/'assistance.json').write_bytes((base/'assistance.json').read_bytes())
 (out/'controls.json').write_text(json.dumps(all_controls,indent=2)+'\n');(out/'events.json').write_text(json.dumps(events,indent=2)+'\n')
 report=dict(passed=done is not None and failure is None,rom_sha256=sha(rom.read_bytes()),prefix=a.prefix,frames=observed,done_frame=done,failure=failure,rope_activation_frame=activated,source_room=0x41,source_position=[104,88],before=before,rows=rows,last_state=state,expected_cells=None if expected is None else expected.hex(),ram_injections=bool(writes),new_assistance_writes=0,extension_unassisted=True,driver_sha256=sha(driver),prefix_capture_sha256=sha((base/'capture.json').read_bytes()),natural_unassisted_campaign_proof=not writes,limits=['Ordinary outdoor traversal and rope deployment after a cold replay; inherited approach assistance is explicit and ends before this extension.','No inventory, position, cell, map, save or state transplant.'])
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k not in ['before','expected_cells']})
 assert report['passed']
if __name__=='__main__':main()
