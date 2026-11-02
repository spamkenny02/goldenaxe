"""Resume an authorized approach guard only after a cold-verified intermediate win."""
import argparse,contextlib,io,json
from pathlib import Path
from run_core import ROOT,run,FrameWrites
from assisted_prefix import prefix_writes,recording,EPISODE_KEYS,controlled_sram_input
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols

def main():
 p=argparse.ArgumentParser();p.add_argument('--trace',required=True);p.add_argument('--boss-room',type=lambda s:int(s,0),required=True);p.add_argument('--next-boss-room',type=lambda s:int(s,0));p.add_argument('--trial',required=True);p.add_argument('--controlled-sram-prefix',action='store_true');a=p.parse_args()
 source=(ROOT/'validation'/a.trace).resolve();assert source.is_relative_to(ROOT/'validation')
 c=json.loads((source/'capture.json').read_bytes());r=json.loads((source/'report.json').read_bytes());old,writes=recording(source,c)
 initial_sram=controlled_sram_input(source,c,a.controlled_sram_prefix)
 assert prefix_writes(source,c,True,controlled=a.controlled_sram_prefix)==writes and old.get('approach_closed_early') and r['room_cleared'] and r['failure'] is None and not r['deaths']
 assert old['boss_room']==a.boss_room and all(old[k] is None for k in ['first_boss_entry','first_boss_combat','first_boss_damage'])
 intermediate=old['closed_before_room'];original=(ROOT/'input/original.sms').read_bytes();kinds=[k for k in original[0x3234e+intermediate*8:0x32356+intermediate*8] if k in (0x78,0x79,0x7a,0x7b,0x7c)];assert kinds
 next_boss=a.next_boss_room if a.next_boss_room is not None else a.boss_room
 assert next_boss!=intermediate,'The next approach must target a different fight'
 assert any(k>=0x20 and original[0x320ea+(k-0x20)*4+3]&0x60 for k in original[0x3234e+next_boss*8:0x32356+next_boss*8])
 rom=ROOT/'gaw-megadrive.bin';assert sha(rom.read_bytes())==c['rom_sha256']
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');start=c['frames'];end=start+1;expected=evidence(source/f'ram_{start:05d}.bin');controls=json.loads((source/'controls.json').read_bytes());timeline=[()]*(start+1)
 for i,row in enumerate(controls):
  stop=controls[i+1]['frame']-1 if i+1<len(controls) else start;timeline[row['frame']:stop+1]=[tuple(row['buttons'])]*(stop-row['frame']+1)
 folder=ROOT/'validation/natural-dungeon-combat'/('md-auto-'+a.trial);assert not folder.exists()
 new_writes=FrameWrites(writes+[(end,sy['hero_hurt'],b'\x00\x81')]);entry=combat=damage=None;previous=None;states=[]
 def observe(f,raw):
  nonlocal entry,combat,damage,previous
  data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  state=dict(frame=f,room=word('room_id'),game=word('game_state'),health=word('hero_health'),hurt=word('hero_hurt'))
  if f<=start:assert state['room']!=next_boss,'No prior next-boss entry may be hidden'
  if f>old['activation_after_frame'] and f<=start:
   if a.boss_room!=intermediate:assert state['room']!=a.boss_room,'No prior pending-boss entry may be hidden'
   if f>old['release_write_frame']:assert state['hurt']<=128,'No held test guard after the declared release'
   if state['room']==intermediate:
    assert f>old['release_write_frame']
    if entry is None:
     assert state['game']!=12;entry=dict(state)
    if state['game']==12:
     if combat is None:
      actors=data('world_actor_state',768);assert state['hurt']<=128 and any(actors[i*48] in kinds and actors[i*48+24] for i in range(8));combat=dict(state)
     if previous is not None and state['health']<previous['health'] and damage is None:damage=dict(**state,before=previous['health'])
   previous=state
  if f==start:
   assert raw==expected and state['room']==intermediate and state['game']==12 and state['health']>0 and state['hurt']<=128
   actors=data('world_actor_state',768);assert not any(actors[i*48] in kinds and actors[i*48+24] for i in range(8))
  if f>=start:
   state.update(gold=word('hero_gold'),keys=word('hero_keys'),magic=word('hero_magic'),items=list(data('hero_items',17)),crystals=list(data('game_save_state',592)[0x1f:0x28]));states.append(state)
 with contextlib.redirect_stdout(io.StringIO()):run(rom,end,folder,{start,end},c['presses'],ram_writes=new_writes,ram_observer=observe,input_provider=lambda f:timeline[f] if f<=start else [],core_options=c['core_options'],sram_in=initial_sram)
 assert entry and combat and entry['frame']<combat['frame'] and old['release_write_frame']<entry['frame']
 assert states[-1]['hurt']==129 and all(states[0][k]==states[-1][k] for k in ['room','health','gold','keys','magic','items','crystals'])
 assist=json.loads(json.dumps(old));closed=assist['episodes'];closed[-1].update(boss_room=intermediate,first_boss_entry=entry,first_boss_combat=combat,first_boss_damage=damage,end_frame=start,natural_cooldown_observed=bool(combat['hurt']))
 fresh=dict(activation_after_frame=start,boss_room=next_boss,first_boss_entry=None,release_write_frame=None,first_boss_combat=None,first_boss_damage=None,end_frame=end+1);assist.update({k:fresh[k] for k in EPISODE_KEYS});assist['episodes']=closed+[fresh];assist['approach_closed_early']=False
 assist.update(resumed_after_verified_intermediate=True,intermediate_victory_trace=a.trace,intermediate_victory_capture_sha256=sha((source/'capture.json').read_bytes()),retargeted_closed_episode_from_room=old['boss_room'],retargeted_closed_episode_to_room=intermediate,intermediate_entry_cold_verified=True,main_boss_never_entered_in_prefix=True,preserve_floor_hurt_requested=True)
 assist['writes']=[dict(frame=f,address=addr,data_hex=value.hex()) for f,addr,value in new_writes];controls.append(dict(frame=end,buttons=[]))
 report=dict(passed=True,failure=None,rom_sha256=c['rom_sha256'],recorded_new_game_prefix=source.name,prefix_end=start,last_state=states[-1],room_cleared=True,deaths=0,rom_modifications=False,sram_checkpoint_injection=False,primary_state_imports=0,resumed_after_verified_intermediate=True,first_intermediate_entry=entry,first_intermediate_combat=combat,first_intermediate_damage=damage,new_approach_boss_room=next_boss,new_guard_frame=end,new_assistance_writes=1,driver_sha256=sha(Path(__file__).read_bytes()),scope='Cold-verified ordinary intermediate victory followed by one new approach guard. No health, resources, actors or progression are imported; next main boss has never been entered.')
 if initial_sram:report.update(controlled_sram_fixture=True,natural_campaign_proof=False,game_written_save=False,sram_sha256=sha(initial_sram.read_bytes()),primary_state_imports=1,sram_checkpoint_injection=True,scope='Controlled synthetic-SRAM prefix retained. One new approach guard after the verified intermediate fight; no further resource,actor or progression writes.')
 for name,value in [('assistance',assist),('report',report),('controls',controls),('events',states)]: (folder/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())
 recording(folder,json.loads((folder/'capture.json').read_bytes()));print('RESUMED APPROACH',end,'after verified intermediate',hex(intermediate),'before main',hex(next_boss))
if __name__=='__main__':main()
