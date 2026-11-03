"""Load genuine v309 game-written SRAM in the newly built v310 ROM. Load pilot derived from validate_game_written_save."""
import argparse,contextlib,io,json
from pathlib import Path
from run_core import ROOT,run,FrameWrites
from assisted_prefix import recording,prefix_writes
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated
from natural_dungeon_combat import walk

def main():
 source=ROOT/'validation/natural-service-route/md-v0309-game-written-save04'
 save_report=json.loads((source/'report.json').read_bytes());assert save_report['passed'] and save_report['game_written_save']
 rom=ROOT/'gaw-megadrive.bin';digest=sha(rom.read_bytes());assert digest!=save_report['rom_sha256']
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
 sram=source/'game-written.srm';raw_sram=sram.read_bytes();assert sha(raw_sram)==save_report['sram_sha256']
 payload=(source/'serialized-payload.bin').read_bytes();assert len(payload)==592 and sha(payload)==save_report['serialized_payload_sha256'] and raw_sram[1::2].ljust(8192,b'\xff')[0x400:0x650]==payload
 c=json.loads((source/'capture.json').read_bytes())
 reload=ROOT/'validation/game-written-save-load/v0310-compat02';assert not reload.exists();state={};events=[];inputs=[];captures=set();ready=None;moved=None;before=None;failure=None;observed=0;previous=None;direction=None
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
 assert data('scratch',4096)[0x85d]==4 and data('game_save_state',592)[0x14a]&1 and payload[0x14a]&1
 result=dict(passed=True,md_sha256=digest,source_rom_sha256=save_report['rom_sha256'],source_sram_sha256=sha(raw_sram),source_save_trace=source.relative_to(ROOT).as_posix(),reload_trace=reload.relative_to(ROOT).as_posix(),reload_ready_frame=ready,movement_verified_frame=moved,final_frame=f,restored_stats=fields,restored_items=17,restored_gems=markers,physical_hud_words_exact=128,persistent_tree_restored=True,sram_imports=1,ram_writes=0,actors_cleared=False,last_state={k:v for k,v in state.items()if k!='tilemap'},driver_sha256=sha(Path(__file__).read_bytes()),limits=['Compatibility load of exact game-written v309 SRAM in v310. Not a new v310 write test or cold campaign.','Stats/items/nine gems checked at first controllable frame; persistent tree, HUD and normal movement checked after load. Global source RNG timing and whole-game fidelity are not proved.'])
 (reload/'report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());(ROOT/'analysis/save_compat_v0310_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('v310 Continue: genuine v309 save,stats,items,gems,tree,HUD and movement passed')
if __name__=='__main__':main()
