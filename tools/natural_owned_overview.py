"""Use a genuinely owned Balloon and return to gameplay, with no new state writes."""
import argparse,contextlib,io,json
from pathlib import Path
from run_core import ROOT,run,FrameWrites
from archive_lossless_evidence import sha
from assisted_prefix import prefix_writes,recording
from validate_playable_sprite_limit import symbols

def main():
 p=argparse.ArgumentParser();p.add_argument('--trace',required=True);p.add_argument('--trial',required=True);p.add_argument('--assisted-prefix',action='store_true');a=p.parse_args()
 source=(ROOT/'validation'/a.trace).resolve();assert source.is_relative_to(ROOT/'validation')
 cap=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'report.json').read_bytes())
 assert prior['failure'] is None and not prior['deaths'] and cap['sram_input'] is None
 rom=ROOT/'gaw-megadrive.bin';assert sha(rom.read_bytes())==cap['rom_sha256']
 writes=prefix_writes(source,cap,a.assisted_prefix);start=cap['frames'];sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
 controls=json.loads((source/'controls.json').read_bytes());timeline=[()]*(start+1)
 for i,row in enumerate(controls):
  end=controls[i+1]['frame']-1 if i+1<len(controls)else start;timeline[row['frame']:end+1]=[tuple(row['buttons'])]*(end-row['frame']+1)
 folder=ROOT/'validation/natural-dungeon-combat'/('md-auto-'+a.trial);assert not folder.exists()
 state={};events=[];captures={start};first=None;modal_entry=None;baseline=None;restored=None;ready=None;activated=None;returned=None;done=None;failure=None;observed=0;phase='select';rooms=[];previous_key=None;cached={}
 driver=Path(__file__).read_bytes()
 def observe(f,raw):
  nonlocal first,modal_entry,restored,ready,activated,returned,done,failure,observed,phase,previous_key
  observed=f
  if f<start:return
  data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),x=word('hero_x'),y=word('hero_y'),health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),gold=word('hero_gold'),keys=word('hero_keys'),selected=word('hero_selected_item'),slot=word('inventory_slot'),graphics=word('world_graphics_class'),terrain=word('hero_terrain_context'),overview=word('world_overview_active'),pacing_error=word('overview_pacing_error'),audio_error=word('sound_unhandled_command'),items=list(data('hero_items',17)),crystals=list(data('game_save_state',592)[0x1f:0x28]))
  state['background']=data('sms_vram',5120);state['map']=data('sms_vram',0x3d00)[0x3800:];state['cells']=data('scratch',4096)[0x800:0x8a0];state['metadata']=data('room_metadata',3)
  public={k:v for k,v in state.items()if k not in ('background','map','cells','metadata')}
  if first is None:
   first=dict(public);assert first['health'] and first['game']==12 and first['hero']==1 and not first['graphics'] and first['terrain']not in (3,5)
   assert first['items'][11]==1 and first['items'][1] and first['crystals']==[128]*9
  if not state['health']or state['game']==20:failure='hero_died'
  if state['audio_error']or state['pacing_error']:failure='native_error'
  if state['overview']==1:
   if modal_entry is None:modal_entry=dict(public);activated=f;captures.add(f+1)
   if not rooms or rooms[-1]['room']!=state['room']:rooms.append(dict(frame=f,room=state['room']))
  if state['overview']==2 and ready is None:ready=f;captures.update([f+1,f+32])
  if ready is not None and returned is None and not state['overview']:
   returned=f;restored=dict(state);phase='restore';captures.add(f+1)
   assert state['selected']==0 and state['room']==first['room'] and (state['x'],state['y'])==(first['x'],first['y'])
   assert all(state[n]==modal_entry[n]for n in ['health','max_health','magic','gold','keys','items','crystals'])
   assert baseline is not None and all(state[n]==baseline[n]for n in ['background','map','cells','metadata'])
  if returned is not None and state['game']==12 and state['hero']==1 and not state['counter'] and state['selected']==1 and done is None:
   done=f;captures.add(f+100)
  key=(state['game'],state['selected'],state['slot'],state['overview'],state['health'])
  if key!=previous_key:events.append(dict(frame=f,**public));previous_key=key
 def choose(f):
  nonlocal baseline,phase
  if f<=start:return list(timeline[f])
  if cached.get('frame')==f:return cached['buttons']
  buttons=[]
  if not failure and done is None:
   if state['overview']==2:
    if f==ready+64:buttons=[8]
   elif state['overview']in (1,3):pass
   elif phase=='select' and state['selected']==11 and state['game']==12 and state['hero']==1 and not state['counter']:
    baseline={n:state[n]for n in ['background','map','cells','metadata']};buttons=[8];phase='activating'
   elif phase=='activating' and modal_entry is None and f%20==0 and state['game']==12 and state['hero']==1 and not state['counter']:
    baseline={n:state[n]for n in ['background','map','cells','metadata']};buttons=[8]
   elif phase in ('select','restore') and f%20==0:
    wanted=11 if phase=='select'else 1
    if state['game']==12 and state['hero']==1:buttons=[0]
    elif state['game']==16:
     if state['selected']==wanted:buttons=[0]
     elif state['slot']//4!=wanted//4:buttons=[5 if state['slot']//4<wanted//4 else 4]
     elif state['slot']%4!=wanted%4:buttons=[7 if state['slot']%4<wanted%4 else 6]
     else:buttons=[8]
  cached.update(frame=f,buttons=buttons)
  if not controls or controls[-1]['buttons']!=buttons:controls.append(dict(frame=f,buttons=buttons))
  return buttons
 with contextlib.redirect_stdout(io.StringIO()):run(rom,start+12000,folder,captures,cap['presses'],skip_intro=False,ram_writes=FrameWrites(writes),ram_observer=observe,input_provider=choose,core_options=cap['core_options'],stop_when=lambda:bool(failure)or done is not None and observed>=done+100)
 passed=done is not None and ready is not None and returned is not None and not failure
 result=dict(passed=passed,failure=failure or(None if passed else'overview_not_completed'),rom_sha256=cap['rom_sha256'],recorded_new_game_prefix=source.name,prefix_end=start,source_trace=a.trace,deaths=int(failure=='hero_died'),room_cleared=False,rom_modifications=False,sram_checkpoint_injection=False,primary_state_imports=0,new_assistance_writes=0,first_state=first,last_state={k:v for k,v in state.items()if k not in ('background','map','cells','metadata')},overview_start=activated,overview_ready=ready,overview_return=returned,complete_frame=done,background_5120_map_1280_cells_160_metadata_restored=passed,modal_resources_unchanged=passed,actual_owned_balloon=True,selected_zero_on_return=passed,ordinary_axe_reselection=passed,ram_injections=bool(writes),assisted_route=bool(writes),natural_campaign_proof=False,driver_sha256=sha(driver),full_game_validated=False,limits=['Nine-crystal cold recording and genuinely owned Balloon. Only inherited approach writes;no new guard,resource,actor,progression or SRAM writes.','This checks natural use and restoration,not complete source RNG or timing parity.'])
 for n,v in [('report',result),('controls',controls),('events',events),('overview_rooms',rooms)]: (folder/(n+'.json')).write_bytes((json.dumps(v,indent=2)+'\n').encode())
 (folder/'overview_driver.py').write_bytes(driver)
 if writes:
  assist=json.loads((source/'assistance.json').read_bytes());(folder/'assistance.json').write_bytes((json.dumps(assist,indent=2)+'\n').encode());recording(folder,json.loads((folder/'capture.json').read_bytes()))
 print(json.dumps(result,indent=2));assert passed
if __name__=='__main__':main()
