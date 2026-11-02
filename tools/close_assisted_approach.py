"""End a test guard before an intermediate fight; never import game state."""
import argparse,contextlib,io,json
from pathlib import Path
from run_core import ROOT,run,FrameWrites
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import prefix_writes,recording,controlled_sram_input
from validate_playable_sprite_limit import symbols

def main():
 p=argparse.ArgumentParser();p.add_argument('--trace',required=True);p.add_argument('--before-room',type=lambda s:int(s,0),required=True);p.add_argument('--trial',required=True);p.add_argument('--controlled-sram-prefix',action='store_true');a=p.parse_args()
 source=(ROOT/'validation'/a.trace).resolve();assert source.is_relative_to(ROOT/'validation')
 c=json.loads((source/'capture.json').read_bytes());old=json.loads((source/'report.json').read_bytes());assert old['failure'] is None
 initial_sram=controlled_sram_input(source,c,a.controlled_sram_prefix);inherited=prefix_writes(source,c,True,controlled=a.controlled_sram_prefix);assist,_=recording(source,c)
 assert all(assist[k] is None for k in ['first_boss_entry','release_write_frame','first_boss_combat','first_boss_damage'])
 rom=ROOT/'gaw-megadrive.bin';assert sha(rom.read_bytes())==c['rom_sha256']
 original=(ROOT/'input/original.sms').read_bytes();kinds=[k for k in original[0x3234e+a.before_room*8:0x32356+a.before_room*8] if k in (0x78,0x79,0x7a,0x7b,0x7c)]
 assert kinds and all(original[0x320ea+(k-0x20)*4+3]&0x20 for k in kinds)
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');start=c['frames'];end=start+1
 expected=evidence(source/f'ram_{start:05d}.bin')
 controls=json.loads((source/'controls.json').read_bytes());timeline=[()]*(start+1)
 for i,row in enumerate(controls):
  stop=controls[i+1]['frame']-1 if i+1<len(controls) else start;timeline[row['frame']:stop+1]=[tuple(row['buttons'])]*(stop-row['frame']+1)
 writes=FrameWrites(inherited+[(end,sy['hero_hurt'],b'\x00\x00')]);folder=ROOT/'validation/natural-dungeon-combat'/('md-auto-'+a.trial);assert not folder.exists()
 states=[]
 def observe(f,raw):
  if f<start:return
  if f==start:assert raw==expected
  data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  actors=data('world_actor_state',768)
  state=dict(frame=f,room=word('room_id'),game=word('game_state'),health=word('hero_health'),hurt=word('hero_hurt'),gold=word('hero_gold'),keys=word('hero_keys'),magic=word('hero_magic'),items=list(data('hero_items',17)),crystals=list(data('game_save_state',592)[0x1f:0x28]))
  assert state['game']==12 and state['health'] and state['room']!=a.before_room
  assert not any(actors[i*48]>=0x20 and actors[i*48+24] for i in range(8)), 'Release before entering a live fight'
  states.append(state)
 with contextlib.redirect_stdout(io.StringIO()):run(rom,end,folder,{start,end},c['presses'],ram_writes=writes,ram_observer=observe,input_provider=lambda f:timeline[f] if f<=start else [],core_options=c['core_options'],sram_in=initial_sram)
 assert len(states)==2 and states[-1]['hurt']==0
 assert all(states[0][k]==states[-1][k] for k in ['room','health','gold','keys','magic','items','crystals'])
 controls.append(dict(frame=end,buttons=[]))
 assist.update(approach_closed_early=True,closed_before_room=a.before_room,source_intermediate_kinds=kinds,release_write_frame=end,closure_prefix=a.trace,closure_prefix_capture_sha256=sha((source/'capture.json').read_bytes()))
 assist['episodes'][-1].update(release_write_frame=end,end_frame=end+1)
 assist['writes']=[dict(frame=f,address=address,data_hex=value.hex()) for f,address,value in writes]
 report=dict(passed=True,failure=None,rom_sha256=c['rom_sha256'],recorded_new_game_prefix=source.name,prefix_end=start,last_state=states[-1],room_cleared=True,deaths=0,rom_modifications=False,sram_checkpoint_injection=False,primary_state_imports=0,approach_closed_early=True,guard_release_frame=end,closed_before_room=a.before_room,driver_sha256=sha(Path(__file__).read_bytes()),scope='One neutral frame and one final zero to release the test guard in a cleared room. Subsequent continuations must never add assistance.')
 if initial_sram:report.update(sram_checkpoint_injection=True,controlled_sram_fixture=True,natural_campaign_proof=False,game_written_save=False,sram_sha256=sha(initial_sram.read_bytes()),primary_state_imports=1)
 for name,value in [('assistance',assist),('report',report),('controls',controls),('events',states)]: (folder/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())
 recording(folder,json.loads((folder/'capture.json').read_bytes()))
 print('CLOSED APPROACH',folder.name,end,'before',hex(a.before_room),flush=True)
if __name__=='__main__':main()
