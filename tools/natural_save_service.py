"""Write a real save by ordinary NPC interaction after a verified cold house route."""
import argparse,contextlib,io,json
from pathlib import Path
from run_core import ROOT,run,FrameWrites
from assisted_prefix import prefix_writes,recording
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols
from natural_dungeon_combat import walk

def main():
 p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--trial',required=True);p.add_argument('--assisted-prefix',action='store_true');p.add_argument('--frames-after',type=int,default=6000);p.add_argument('--rom');p.add_argument('--slot',type=int,choices=range(3),default=0);a=p.parse_args()
 source=ROOT/'validation/natural-dungeon-route'/a.prefix;c=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes())
 assert c['sram_input'] is None and prior['reached_entrance'] and not prior['failure']
 rom=ROOT/(a.rom or 'gaw-megadrive.bin');digest=sha(rom.read_bytes());assert c['rom_sha256']==digest
 writes=prefix_writes(source,c,a.assisted_prefix);start=c['frames'];expected=evidence(source/f'ram_{start:05d}.bin');assert len(expected)==65536
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');recorded=json.loads((source/'controls.json').read_bytes());controls=list(recorded);timeline=[()]*(start+1)
 for i,row in enumerate(recorded):
  end=recorded[i+1]['frame']-1 if i+1<len(recorded)else start;timeline[row['frame']:end+1]=[tuple(row['buttons'])]*(end-row['frame']+1)
 folder=ROOT/'validation/natural-service-route'/('md-'+a.trial);assert not folder.exists();sram=folder/'game-written.srm'
 nodes={r:(x,y)for r,x,y in json.loads((ROOT/'analysis/save_assets.json').read_bytes())['nodes']}
 state={};events=[];captures={start};first=None;house=None;point=None;written=None;payload=None;complete=None;failure=None;observed=0;last_key=None;last_direction=0;selection_since=None
 def observe(f,raw):
  nonlocal first,house,point,written,payload,complete,failure,observed,last_key
  observed=f
  if f<start:return
  if f==start:assert raw==expected
  data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),x=word('hero_x')>>8,y=word('hero_y')>>8,health=word('hero_health'),magic=word('hero_magic'),gold=word('hero_gold'),keys=word('hero_keys'),selected=word('hero_selected_item'),phase=word('save_service_phase'),slot=word('save_slot_selection'),last_slot=word('save_last_slot'),modal=word('house_dialogue_active'),audio_error=word('sound_unhandled_command'),tilemap=data('sms_vram',16384)[0x3800:0x3e00])
  if first is None:
   first={k:v for k,v in state.items()if k!='tilemap'};house=state['room'];assert house in nodes and state['game']==12 and state['health'];point=nodes[house];assert state['last_slot']==0,'This test requires a genuinely fresh save list'
  if not state['health'] or state['game']==20:failure='hero_died'
  if state['audio_error']:failure='native_audio_error'
  if state['room']!=house:failure='unexpected_house_exit'
  if state['phase']==3 and written is None:
   written=f;payload=data('game_save_state',592);captures.add(f+1)
   assert state['last_slot']==a.slot+1 and state['slot']==a.slot and payload[0] not in (0,255)
  key=tuple(state[k]for k in ['room','game','phase','slot','last_slot','modal','health','magic','gold','keys'])
  if key!=last_key:
   events.append(dict(frame=f,**{k:v for k,v in state.items()if k!='tilemap'}));captures.add(f+1);last_key=key
  if written is not None and complete is None and state['phase']==0 and state['game']==12 and state['hero']==1 and not state['modal']:
   complete=f;captures.add(f+150)
 def choose(f):
  nonlocal last_direction,selection_since
  if f<=start:return list(timeline[f])
  if failure or complete is not None:return []
  if state.get('phase')==2:
   if selection_since is None:selection_since=f
   if f-selection_since<100 or f%20:return []
   return [5 if state['slot']<a.slot else 4] if state['slot']!=a.slot else [8]
  if state.get('game')==22 or state.get('modal'):return [8]if f%40<4 else []
  # The restored room first publishes hero0. Do not press UP again
  # while waiting for hero1,or the NPC service immediately reopens.
  if written is not None and state.get('game')==12 and state.get('phase')==0:return []
  if state.get('game')!=12 or state.get('hero')not in (0,1):return []
  if state['counter']:return [4+last_direction]
  at=state['x'],state['y']
  if at==point:last_direction=0;return [4]
  route=walk(state['tilemap'],at,lambda q:q==point)
  if route:last_direction=route[0];return [4+last_direction]
  return []
 def controller(f):
  value=choose(f)
  if f>start and(not controls or controls[-1]['buttons']!=value):controls.append(dict(frame=f,buttons=list(value)))
  return value
 with contextlib.redirect_stdout(io.StringIO()):
  run(rom,start+a.frames_after,folder,captures,c['presses'],skip_intro=False,ram_writes=FrameWrites(writes),ram_observer=observe,input_provider=controller,stop_when=lambda:bool(failure)or complete is not None and observed>=complete+150,sram_out=sram,core_options=c['core_options'])
 raw_sram=sram.read_bytes();logical=raw_sram[1::2].ljust(8192,b'\xff');valid=written is not None and payload is not None and logical[0x400+a.slot*0x400:0x650+a.slot*0x400]==payload and logical[0x30]==a.slot+1
 passed=complete is not None and not failure and valid
 if payload is not None:(folder/'serialized-payload.bin').write_bytes(payload)
 report=dict(passed=passed,failure=failure or(None if passed else 'save_service_or_payload_incomplete'),rom_sha256=digest,source_prefix='natural-dungeon-route/'+a.prefix,prefix_end=start,first_state=first,last_state={k:v for k,v in state.items()if k!='tilemap'},save_written_frame=written,complete_frame=complete,game_written_save=True,initial_sram=False,primary_state_imports=0,sram_checkpoint_injection=False,new_assistance_writes=0,ram_injections=bool(writes),assisted_route=bool(writes),natural_campaign_proof=False,sram_file=sram.relative_to(ROOT).as_posix(),sram_sha256=sha(raw_sram),sram_bytes=len(raw_sram),slot=a.slot,logical_payload_offset=0x400+a.slot*0x400,logical_payload_bytes=592,serialized_payload_sha256=sha(payload)if payload is not None else None,payload_source_ram_exact=valid,rom_modifications=False,driver_sha256=sha(Path(__file__).read_bytes()),scope='Actual normal NPC Yes/selected-slot transaction after a canonical cold house route. Exported SRAM matches the592-byte serialized live RAM. No resource,actor,progression or SRAM fixture. Separate fixed-input SRAM replay and fresh Continue load remain required.')
 for name,value in [('report',report),('events',events),('controls',controls)]:(folder/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())
 if writes:
  assist=json.loads((source/'assistance.json').read_bytes());assist['writes']=[dict(frame=f,address=addr,data_hex=data.hex())for f,addr,data in writes];(folder/'assistance.json').write_bytes((json.dumps(assist,indent=2)+'\n').encode());recording(folder,json.loads((folder/'capture.json').read_bytes()))
 print('Actual game-written save:',passed,written,complete)
 assert passed,report
if __name__=='__main__':main()
