"""Bind current-ROM campaign milestones to independent cold replays."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols
from assisted_prefix import recording

def main():
 refs={}
 def read(name):raw=evidence(ROOT/name);refs[name]=sha(raw);return raw
 def load(name):return json.loads(read(name))
 digest=sha(read('gaw-megadrive.bin'));assert digest==sha(read('versions/v0292-6eeb5608/gaw-megadrive-v0292.bin'));sy=symbols(ROOT/'megadrive/out/release/symbol.txt');stages=[]
 names=[('natural-dungeon-combat','md-auto-v0292-d2-exit02','report'),('natural-dungeon-route','md-v0292-d3-entry01','route_report'),('natural-dungeon-combat','md-auto-v0292-d3-rope01','report'),('natural-dungeon-combat','md-auto-v0292-d3-boss01','report'),('natural-dungeon-combat','md-auto-v0292-d3-exit01','report'),('natural-dungeon-route','md-v0292-gold-entry01','route_report'),('natural-service-route','md-v0292-gold50-02','report'),('natural-dungeon-route','md-v0292-earth-entry01','route_report'),('natural-service-route','md-v0292-earth-learn01','report'),('natural-dungeon-route','md-v0292-d4-entry01','route_report'),('natural-dungeon-combat','md-auto-v0292-d4-key01','report'),('natural-dungeon-combat','md-auto-v0292-d4-earth01','report'),('natural-dungeon-route','sms-v0292-source-d4-entry03','route_report'),('natural-dungeon-combat','sms-auto-v0292-source-d4-key01','report'),('natural-dungeon-combat','sms-auto-v0292-source-d4-earth06','report')]
 for family,name,reportname in names:
  root=f'validation/{family}/{name}';r=load(root+'/'+reportname+'.json');c=load(root+'/capture.json');proof=load(root+f'-assisted-fixed-replay-{c["frames"]}/replay_report.json');sms=name.startswith('sms');expected=sha(read('input/original.sms')) if sms else digest
  assert c['rom_sha256']==proof['rom_sha256']==expected and c['sram_input'] is None and proof['passed'] and proof['whole_ram_bytes']==(8192 if sms else 65536) and proof['final_png_exact'] and not proof['boss_assistance']
  assist,writes=recording(ROOT/root,c);read(root+'/assistance.json');read(root+'/controls.json')
  assert all(addr==(0x305 if sms else sy['hero_hurt']) for _,addr,_ in writes)
  assert r['failure'] is None and not r.get('deaths',r.get('normal_continues',0))
  assert r['reached_entrance'] and r['directional_probe_succeeded'] if reportname=='route_report' else r.get('passed',r.get('room_cleared'))
  if 'd2-exit02' in name or 'd3-exit01' in name:assert r['full_dungeon_cleared'] and r['last_state']['completed_dungeon_progress']==128 and r['last_state']['dungeon']==0
  if 'd3-rope01' in name:assert r['last_state']['item_value']==1 and r['collect_item_requested']==13
  if 'd3-boss01' in name:assert r['last_state']['progress']==128 and r['last_state']['max_health']==56 and r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']==260
  if 'gold50-02' in name:assert r['last_state']['gold']==r['first_state']['gold']+50 and r['new_assistance_writes']==0
  if 'earth-learn01' in name:assert r['last_state']['level']==1 and r['last_state']['gold']==r['first_state']['gold']-50 and r['last_state']['max_magic']==48 and r['new_assistance_writes']==0
  if 'd4-earth' in name:assert r['earth_route_passed'] and r['earth_state_writes']==0 and r['last_state']['room']==0x1d1 and r['last_state']['magic']==40 and not r['destination_combat_cleared']
  stages.append(dict(trace=root,frames=c['frames'],rom_sha256=expected,final_state=r['last_state'],whole_ram_png_cold_replay=True,assisted_history=True,episodes=[{k:v for k,v in e.items() if k!='writes'} for e in assist['episodes']]))
 cross=load('analysis/campaign_earth_v0292_report.json');assert cross['passed'] and cross['md_sha256']==digest and cross['changed_cells']==[54,55,56,57,88] and cross['hardware_map_words']==20
 scheduler=load('analysis/campaign_v0292_input_scheduler_report.json');assert scheduler['passed'] and scheduler['cases']==2000 and scheduler['run_core_sha256']==sha(read('tools/run_core.py'))
 replay=load('validation/natural-dungeon-route/md-v0292-gold-entry01-assisted-fixed-replay-58752-compact02/replay_report.json');assert replay['passed'] and replay['indexed_writes'] and replay['whole_ram_bytes']==65536 and replay['final_png_exact'] and replay['rom_sha256']==digest
 for name in ['assisted_boss_route.py','assisted_prefix.py','natural_dungeon_combat.py','natural_dungeon_route.py','natural_house_service.py','natural_earth_passage.py','rebase_assisted_campaign.py','replay_assisted_prefix.py','validate_campaign_input_scheduler.py','validate_campaign_earth_v0292.py']:read('tools/'+name)
 report=dict(passed=True,version=292,md_sha256=digest,production_rom_unchanged=True,stages=stages,cross_source_native_earth=dict(cells=160,map_bytes=1280,inventory_bytes=17,flag=cross['persistent_flag'],changed_cells=cross['changed_cells'],hardware_map_words=20),input_scheduler=dict(interval_cases=2000,older_recording_whole_ram_png_replay=True,frames=58752),full_game_validated=False,evidence=refs,limits=['Approach-only hurt guards are logged; bosses D2/D3 fight with ordinary damage. No ROM patch,equipment/currency fixture,health refill,SRAM or primary state import. Later D4 approach assistance is a separate episode.','Current v292 completes D2 and D3,acquires rope,receives real50gold,buys Earth and crosses the real D4 Earth passage. D1 destination of that passage is entered,not cleared.','Two independent SMS/native E1 casts spend8magic and agree on5 changed cells,full software map/inventory/flag,and20 actual VDP map words plus referenced tile indices. HP,gold,actors,clock,full-framebuffer andaudio are not cross-system equivalence claims.','Latest canoe-route diagnostics reach D4 B2 on both systems,with no key left; they are not a canoe acquisition or boss4 proof. The intermediate key/trigger route still needs execution. Complete game,remaining dungeons,ending,hardware and global RNG/timing remain unproven.','Input scheduling and route-controller improvements do not change the production ROM; no new ROM version is created. Historical/failed diagnostics remain preserved separately.'])
 (ROOT/'analysis/campaign_v0292_progress_report.json').write_text(json.dumps(report,indent=2)+'\n');print('Validated campaign stages:',len(stages),'ROM:',digest)
if __name__=='__main__':main()
