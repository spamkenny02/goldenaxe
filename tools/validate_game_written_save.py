"""Independently replay a real save including SRAM,then cold-load it normally."""
import argparse,contextlib,io,json
from pathlib import Path
from run_core import ROOT,run,FrameWrites
from assisted_prefix import recording,prefix_writes
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated
from natural_dungeon_combat import walk

def main():
 p=argparse.ArgumentParser();p.add_argument('--trace',required=True);p.add_argument('--trial',required=True);a=p.parse_args()
 source=(ROOT/'validation'/a.trace).resolve();assert source.is_relative_to(ROOT/'validation')
 c=json.loads((source/'capture.json').read_bytes());r=json.loads((source/'report.json').read_bytes());assert r['passed'] and r['game_written_save'] and r['payload_source_ram_exact'] and not r['primary_state_imports'] and not r['new_assistance_writes'] and c['sram_input'] is None
 rom=ROOT/'gaw-megadrive.bin';digest=sha(rom.read_bytes());assert c['rom_sha256']==r['rom_sha256']==digest
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');assist,writes=recording(source,c)
 # This tool creates the service replay,so require the canonical parent
 # rather than circularly requiring the not-yet-created service proof.
 parent=(ROOT/'validation'/r['source_prefix']).resolve();assert parent.is_relative_to(ROOT/'validation')
 pc=json.loads((parent/'capture.json').read_bytes());pa,pw=recording(parent,pc)
 assert prefix_writes(parent,pc,True)==pw==writes and assist==pa and r['prefix_end']==pc['frames']
 parent_controls=json.loads((parent/'controls.json').read_bytes());service_controls=json.loads((source/'controls.json').read_bytes())
 assert service_controls[:len(parent_controls)]==parent_controls and all(row['frame']>pc['frames']for row in service_controls[len(parent_controls):])
 assert all(address==sy['hero_hurt']for _,address,_ in writes)
 sram=(ROOT/r['sram_file']).resolve();assert sram.is_relative_to(source);raw_sram=sram.read_bytes();assert sha(raw_sram)==r['sram_sha256']
 payload=(source/'serialized-payload.bin').read_bytes();assert len(payload)==592 and raw_sram[1::2].ljust(8192,b'\xff')[0x400:0x650]==payload and sha(payload)==r['serialized_payload_sha256']
 fixed=ROOT/'validation/game-written-save-replay'/a.trial;assert not fixed.exists();fixed_sram=fixed/'replayed.srm';end=c['frames'];presses=[tuple(v)for v in c['presses']];controls=json.loads((source/'controls.json').read_bytes())
 for i,row in enumerate(controls):
  stop=controls[i+1]['frame']-1 if i+1<len(controls)else end
  presses.extend((row['frame'],min(stop,end),key)for key in row['buttons']if row['frame']<=end)
 with contextlib.redirect_stdout(io.StringIO()):run(rom,end,fixed,{end},presses,skip_intro=False,ram_writes=FrameWrites(writes),sram_out=fixed_sram,core_options=c['core_options'])
 assert fixed_sram.read_bytes()==raw_sram
 for stem,ext in [('ram','bin'),('frame','png')]:assert(fixed/f'{stem}_{end:05d}.{ext}').read_bytes()==(source/f'{stem}_{end:05d}.{ext}').read_bytes()
 proof=dict(passed=True,rom_sha256=digest,feedback_reads=False,whole_ram_bytes=65536,final_png_exact=True,raw_sram_exact=True,sram_sha256=sha(raw_sram),initial_sram=False,source_trace=a.trace,frames=end,driver_sha256=sha(Path(__file__).read_bytes()))
 (fixed/'replay_report.json').write_bytes((json.dumps(proof,indent=2)+'\n').encode())
 reload=ROOT/'validation/game-written-save-load'/a.trial;assert not reload.exists();state={};events=[];inputs=[];captures=set();ready=None;moved=None;before=None;failure=None;observed=0;previous=None;direction=None
 target=int.from_bytes(payload[0x12:0x14],'little')
 fields={'hero_health':0x29,'hero_max_health':0x2a,'hero_magic':0x2b,'hero_max_magic':0x2c,'hero_gold':0x2d,'hero_keys':0x2e,'hero_selected_item':0x2f,'hero_basic_level':0x30,'hero_weapon_level':0x31,'hero_armor_level':0x41,'hero_shield_level':0x42}
 def reader(raw):
  data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k))
  return data,lambda n:int.from_bytes(data(n,2),'big')
 def observe(f,raw):
  nonlocal ready,moved,before,failure,observed,previous
  observed=f;data,word=reader(raw)
  state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),x=word('hero_x')>>8,y=word('hero_y')>>8,health=word('hero_health'),hurt=word('hero_hurt'),phase=word('save_service_phase'),slot=word('save_slot_selection'),audio_error=word('sound_unhandled_command'),tilemap=data('sms_vram',16384)[0x3800:0x3e00])
  key=tuple(state[n]for n in ['room','game','hero','health','phase','slot'])
  if key!=previous:events.append(dict(frame=f,**{k:v for k,v in state.items()if k!='tilemap'}));captures.add(f+1);previous=key
  if state['audio_error']:failure='native_audio_error'
  if state['game']==12 and ready is None and state['hero']==1 and state['room']==target:
   assert state['health'] and state['hurt']<=128
   for name,offset in fields.items():assert word(name)==payload[offset],(name,word(name),payload[offset])
   assert data('hero_items',17)==payload[0x30:0x41] and data('game_save_state',592)[0x1f:0x28]==payload[0x1f:0x28]
   ready=f;before=dict(frame=f,**{k:v for k,v in state.items()if k!='tilemap'});captures.add(f+1)
  if ready is not None:
   if not state['health'] or state['game']==20:failure='hero_died_after_load'
   assert state['hurt']<=128
   if moved is None and state['game']==12 and state['hero']==1 and not state['counter'] and state['room']==target and abs(state['x']-before['x'])+abs(state['y']-before['y'])>=8:moved=f;captures.add(f+100)
 def choose(f):
  nonlocal direction
  if failure:return []
  if ready is None:
   if 200<=f<=220 or 920<=f<=935:return [0]
   if 1050<=f<=1065 or 1300<=f<=1310:return [8]
   return []
  if moved is not None or state['room']!=target or state['game']!=12:return []
  if state['hero']not in (0,1):return []
  if state['counter']:return[4+direction]if direction is not None else []
  at=state['x'],state['y']
  if at!=(before['x'],before['y']):return []
  if direction is None:
   for d,(dx,dy)in enumerate([(0,-8),(0,8),(-8,0),(8,0)]):
    point=(at[0]+dx,at[1]+dy)
    if 16<=point[0]<=240 and 16<=point[1]<=160:
     route=walk(state['tilemap'],at,lambda q:q==point)
     if route and len(route)==1:direction=route[0];break
  return[4+direction]if direction is not None else []
 def controller(f):
  value=choose(f)
  if not inputs or inputs[-1]['buttons']!=value:inputs.append(dict(frame=f,buttons=list(value)))
  return value
 with contextlib.redirect_stdout(io.StringIO()):run(rom,6000,reload,captures,[],skip_intro=False,sram_in=sram,ram_observer=observe,input_provider=controller,stop_when=lambda:bool(failure)or moved is not None and observed>=moved+100,core_options=c['core_options'])
 assert ready is not None and moved is not None and not failure,(state,ready,moved,failure)
 cap=json.loads((reload/'capture.json').read_bytes());assert cap['test_ram_writes']==[] and cap['sram_input']==str(sram);f=cap['frames'];data,word=reader((reload/f'ram_{f:05d}.bin').read_bytes())
 sms=data('sms_vram',16384);vram=(reload/f'vram_{f:05d}.bin').read_bytes();regs=(reload/f'vdp_regs_{f:05d}.bin').read_bytes();base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
 for n in range(128):
  at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
 original=(ROOT/'input/original.sms').read_bytes();markers=0
 for n in range(9):
  if payload[0x1f+n]&128:
   tile,off=original[0x1edc+n*2:0x1ede+n*2];assert sms[0x3d00+off:0x3d02+off]==bytes([tile,0x59]);markers+=1
 for name,value in [('controls',inputs),('events',events)]:(reload/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())
 result=dict(passed=True,rom_sha256=digest,game_written_save=True,synthetic_sram_fixture=False,source_trace=a.trace,source_sram_sha256=sha(raw_sram),serialized_payload_bytes=592,raw_sram_fixed_replay_exact=True,save_whole_ram_png_exact=True,fixed_replay_trace=fixed.relative_to(ROOT).as_posix(),reload_trace=reload.relative_to(ROOT).as_posix(),reload_primary_sram_imports=1,reload_ram_writes=0,reload_actor_records_cleared=False,reload_ready_frame=ready,restored_source_fields=fields,checkpoint_room=target,movement_verified_frame=moved,physical_hud_words_exact=128,source_crystal_markers_exact=markers,last_state={k:v for k,v in state.items()if k!='tilemap'},full_game_validated=False,driver_sha256=sha(Path(__file__).read_bytes()),limits=['Real game-written SRAM from a separate canonical New Game branch;no initial save fixture or test resource writes. Reload necessarily imports that exact game-written SRAM and is not labelled a cold New Game campaign.','This checks slot0 write/reload and actual control/HUD,not all slot/refusal combinations,global source timing or console hardware.'])
 (reload/'report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());(ROOT/'analysis/game_written_save_v0309_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('Real save fixed replay,SRAM and normal Continue verified')
if __name__=='__main__':main()
