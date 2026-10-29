"""Replay recorded buttons on the current ROM; promote only observed progression."""
import argparse,contextlib,gzip,io,json
from run_core import ROOT,run
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols

def evidence(path):
 if path.exists():return path.read_bytes()
 name=path.relative_to(ROOT).as_posix()
 for folder in ['fairy-campaign-v0280','natural-campaign-v0280','natural-axe-campaign-v0274','stack-release-v0285','d2-progress-v0285','hero-pattern-v0286','d2-campaign-v0286','magic-rope-v0287','campaign-v0287-progress','terrain-walk-v0288','floor-damage-v0289','spell-teacher-v0290','axe-terrain-v0291','rope-arrival-v0292','campaign-v0292-progress','canoe-campaign-v0292','d5-progress-v0292','d5-campaign-v0292','crystal-bridge-v0293','d6-progress-v0293','d6-campaign-v0293','first-boss-variants-v0294','d2-campaign-v0294','variant-7c-v0295','sprite-cache-v0296','burst-cadence-v0304','d2-campaign-v0304','d3-campaign-v0304','d4-earth-v0304','d4-canoe-v0304','d4-campaign-v0304','d5-progress-v0304','d5-supplies-v0304']:
  archive=ROOT/'analysis'/folder
  if not (archive/'manifest.json').exists():continue
  manifest=json.loads((archive/'manifest.json').read_bytes())
  if name in manifest['files']:
   raw=(archive/name).read_bytes();assert sha(raw)==manifest['files'][name];return raw
  if name in manifest['compressed']:
   item=manifest['compressed'][name];encoded=(archive/item['stored']).read_bytes();assert sha(encoded)==item['stored_sha256'];raw=gzip.decompress(encoded);assert sha(raw)==item['raw_sha256'];return raw
 raise FileNotFoundError(path)

def main():
 p=argparse.ArgumentParser();p.add_argument('--trace',required=True);p.add_argument('--trial',required=True);p.add_argument('--expected-room',type=lambda s:int(s,0),required=True);p.add_argument('--end-frame',type=int);p.add_argument('--expected-capacity',type=int,default=32);p.add_argument('--stage',choices=['first-dungeon','second-dungeon'],default='second-dungeon');a=p.parse_args()
 source=(ROOT/'validation'/a.trace).resolve();assert source.is_relative_to(ROOT/'validation')
 capture=json.loads(evidence(source/'capture.json'));recorded_controls=evidence(source/'controls.json');controls=json.loads(recorded_controls)
 assert not capture['test_ram_writes'] and capture['sram_input'] is None
 rom=ROOT/'gaw-megadrive.bin';digest=sha(rom.read_bytes());sy=symbols(ROOT/'megadrive/out/release/symbol.txt');end=a.end_frame or capture['frames'];assert 0<end<=capture['frames'];controls=[row for row in controls if row['frame']<=end]
 folder=ROOT/'validation/natural-dungeon-route'/a.trial;assert not folder.exists()
 presses=[(start,min(stop,end),button) for start,stop,button in capture['presses'] if start<=end]
 for n,row in enumerate(controls):
  stop=controls[n+1]['frame']-1 if n+1<len(controls) else end
  presses.extend((row['frame'],min(stop,end),b) for b in row['buttons'] if row['frame']<=end)
 states=[]
 def observe(f,r):
  if f%10000 and f!=end:return
  data=lambda n,k:bytes(r[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  row=dict(frame=f,**{n:word(n) for n in ['room_id','game_state','hero_state','hero_health','hero_max_health','hero_weapon_level','hero_selected_item','world_dungeon_number','hero_keys','hero_x','hero_y','sound_unhandled_command']},first_crystal=data('game_save_state',592)[0x1f])
  states.append(row);print(row,flush=True)
 with contextlib.redirect_stdout(io.StringIO()):run(rom,end,folder,{end},presses,skip_intro=False,ram_observer=observe,core_options=capture['core_options'])
 final=states[-1]
 stage_ok=(final['first_crystal']==0 and final['hero_max_health']==24 and final['hero_weapon_level']==0 and final['hero_selected_item']==0) if a.stage=='first-dungeon' else (final['first_crystal']==128 and final['hero_max_health']==a.expected_capacity and final['hero_weapon_level']==1 and final['hero_selected_item']==1)
 passed=stage_ok and final['room_id']==a.expected_room and final['game_state']==12 and final['hero_health']>0 and not final['sound_unhandled_command']
 # No source capture or state is transplanted: these controls were all executed.
 (folder/'controls.json').write_bytes((json.dumps(controls,indent=2)+'\n').encode())
 result=dict(passed=passed,rom_sha256=digest,recording_rom_sha256=capture['rom_sha256'],recording=source.relative_to(ROOT).as_posix(),recording_controls_sha256=sha(recorded_controls),frames=end,expected_capacity=a.expected_capacity,states=states,expected_room=a.expected_room,stage=a.stage,ram_injections=False,sram_checkpoint_injection=False,limits=['Cold replay of recorded ordinary buttons on a newer ROM. Successful promotion requires live stage-specific progression/equipment/HP capacity,correct room,alive state12 and no native audio error. First-dungeon stage has no crystal/axe and24HP capacity; second-dungeon stage requires first crystal,axe equipped and the explicitly requested capacity (default32).','Does not assert identical encounters,whole RAM,HP remaining,global clock or complete campaign.'])
 (folder/'rebase_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(result,flush=True)
 assert passed,'Recorded route does not reach the required progression on this ROM'

if __name__=='__main__':main()
