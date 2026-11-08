import sys,json,contextlib,io,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('tools').resolve()))
from run_core import run,FrameWrites,ROOT
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
trace=ROOT/'validation/c0046-campaign01/isolated/project/validation/natural-dungeon-combat/md-auto-c0046-cold-palace-ending01'
cap=json.loads((trace/'capture.json').read_bytes());assist,writes=recording(trace,cap)
rom=ROOT/'validation/v320-credits-overlay01/gaw-megadrive-candidate.bin';sy=symbols(ROOT/'megadrive/out/release/symbol.txt');oldsy=symbols(ROOT/'megadrive/out/release/symbol.txt')
assert cap['sram_input'] is None and {a for _,a,_ in writes}=={oldsy['hero_hurt']}
writes=[(f,sy['hero_hurt'],b) for f,a,b in writes];controls=json.loads((trace/'controls.json').read_bytes());end=cap['frames'];presses=list(map(tuple,cap['presses']))
for i,row in enumerate(controls):
 stop=controls[i+1]['frame']-1 if i+1<len(controls) else end
 presses.extend((row['frame'],stop,b) for b in row['buttons'])
out=ROOT/'validation/v320-credits-campaign03';assert not out.exists();latest={};states={};events={};observed=0;final={}
def video(f,data,w,h,pitch,mode):
 if f<395000 or data is None or (w,h,mode)!=(256,224,2):return
 im=np.frombuffer(data,dtype='<u2').reshape(h,pitch//2)[:,:w];latest.update(bottom=int(np.count_nonzero(im[208:])),top=int(np.count_nonzero(im[:16])))
def observe(f,raw):
 global observed
 observed=f
 if f%50000==0:print('campaign frame',f,flush=True,file=sys.__stdout__)
 if f<390000:return
 data=lambda k,n:bytes(raw[(sy[k]+i)^1] for i in range(n))
 word=lambda k:int.from_bytes(data(k,2),'big')
 credit=data('ending_credits',9);game=word('game_state');descriptor=word('ending_hero_descriptor')
 if game==14 and descriptor==0x84e1 and int.from_bytes(credit[6:8],'big')>0:
  events.setdefault('credits_started',f);states.setdefault(credit.hex(),dict(frame=f,**latest))
  if credit[1]:events.setdefault('credits_finished',f)
 if 'credits_finished' in events and game==0:events.setdefault('returned_to_intro',f)
 if f==end:final.update(game=game,room=word('room_id'),audio_error=word('sound_unhandled_command'),crystals=list(data('game_save_state',592)[0x1f:0x28]))
with contextlib.redirect_stdout(io.StringIO()):run(rom,end,out,{395935,400000,end},presses,skip_intro=False,ram_writes=FrameWrites(writes),core_options=cap['core_options'],ram_observer=observe,video_observer=video)
assert observed==end and len(states)==7424 and events.get('returned_to_intro') and not final['audio_error'],(events,len(states),final)
assert final['game']==0 and final['crystals']==[128]*9,final
assert all(not r['bottom'] and not r['top'] for r in states.values())
report=dict(passed=True,md_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),frames=end,events=events,credit_states=len(states),borders_black_all_states=True,final=final,approach_guard_writes=len(writes),boss_assistance=False,sram_imports=0,progression_imports=0,recording=str(trace.relative_to(ROOT)),limits=['Recorded full campaign from cold boot; original authorized approach guard rebased to current hero_hurt address and removed before bosses. Not an unassisted campaign or physical hardware/PCM certificate.'])
(out/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
