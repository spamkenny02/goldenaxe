"""Scoped native D5 boss/crystal/exit proof, with logged approach assistance."""
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
 digest=sha(read('gaw-megadrive.bin'));assert digest==sha(read('versions/v0292-6eeb5608/gaw-megadrive-v0292.bin'));sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
 supplies=load('analysis/d5_supplies_v0292_report.json');assert supplies['passed'] and supplies['md_sha256']==digest
 stages=[];reports={}
 for name,kind in [('md-auto-v0292-d5-boss03','boss_crystal'),('md-auto-v0292-d5-return-contact01','return_contact'),('md-auto-v0292-d5-exit01','exit')]:
  root='validation/natural-dungeon-combat/'+name;r=load(root+'/report.json');c=load(root+'/capture.json');p=load(root+f'-assisted-fixed-replay-{c["frames"]}/replay_report.json');a,w=recording(ROOT/root,c)
  read(root+'/assistance.json');assert c['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None and p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads'] and not p['boss_assistance']
  for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
  assert a['boss_room']==0x163 and a['release_write_frame']==112509 and a['first_boss_combat']==dict(frame=112535,health=64,hurt=0) and a['first_boss_damage'] is None and not a['primary_state_imports'] and not a['health_refills']
  assert all(address==sy['hero_hurt'] for _,address,_ in w) and w[-1][0]==112509 and w[-1][2]==b'\0\0'
  assert not r['failure'] and not r['deaths'] and r['last_state']['health']>0 and not r['last_state']['audio_error'] and r['last_state']['max_health']==72 and not r['last_state']['reward_active']
  raw=read(root+f'/ram_{c["frames"]:05d}.bin');read(root+f'/frame_{c["frames"]:05d}.png');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));assert data('game_save_state',592)[0x1f:0x24]==bytes([128]*5) and data('hero_items',17)[12:15]==bytes([1]*3)
  if kind=='boss_crystal':
   assert r['room_cleared'] and r['clear_frame']==116065 and r['last_state']['health']==72 and r['last_state']['hero']==1 and r['last_state']['progress']==128 and not r['last_actors']
   assert r['planning_decisions']==r['verified_persistent_prediction_windows']==r['full_ram_prediction_matches']==381
   events=load(root+'/events.json');dead=next(e['frame'] for e in events if e['frame']>=112535 and any(x['slot']==0 and x['type']==7 for x in e['actors']));assert dead==115582
   assert min(e['health'] for e in events if 112535<=e['frame']<=dead)==64
  else:assert a['unassisted_extension'] and not a['new_assistance_writes']
  if kind=='return_contact':assert r['passed'] and r['contact_route_passed'] and r['contact_room']==0x173 and r['contact_destination']==0x174 and r['contact_opened']['marker']==0x4d and not r['contact_state_writes']
  if kind=='exit':assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and r['last_state']['room']==0x49 and r['last_state']['dungeon']==0 and r['last_state']['completed_dungeon_progress']==128
  stages.append(dict(trace=root,role=kind,frames=c['frames'],last_state=r['last_state'],whole_ram_bytes=65536,final_png_exact=True));reports[kind]=r
 stackroot='validation/stack-v0292-d5-crystal-all';s=load(stackroot+'/stack_report.json');assert s['md_sha256']==digest and s['all_instructions'] and s['frames']==116135 and not s['invalid_heap_examples'];low=min(r['sp'] for r in s['instruction_minima']);boundary=s['heap_changes'][-1]['end']+2;assert low>=boundary
 for stem,ext in [('ram','bin'),('frame','png')]:assert read(stackroot+f'/{stem}_116135.{ext}')==read('validation/natural-dungeon-combat/md-auto-v0292-d5-boss03'+f'/{stem}_116135.{ext}')
 for name in ['natural_dungeon_combat.py','natural_contact_passage.py','assisted_boss_route.py','replay_assisted_prefix.py','natural_boss_evasive_planner.py','natural_boss_escape_planner.py','natural_boss_side_planner.py','natural_combat_navigation.py','natural_exit_planner.py','profile_playable_stack.py','run_core.py']:read('tools/'+name)
 rom=read('gaw-megadrive.bin');checksum=sum(int.from_bytes(rom[i:i+2],'big') for i in range(0x200,len(rom),2))&65535;assert checksum==int.from_bytes(rom[0x18e:0x190],'big')
 report=dict(passed=True,version=292,md_sha256=digest,checksum=f'{checksum:04X}',production_rom_unchanged=True,native_dungeon5_completed=True,source_boss_victory_validated=False,new_stages=stages,prior_supply_replays=14,boss_guard=dict(release_frame=112509,first_combat_frame=112535,lead_frames=26,health_at_start=64,damage_during_boss=0,boss_death_frame=dead,crystal_full_heal_frame=116065),stack=dict(frames=116135,all_instructions=True,minimum_sp=low,heap_boundary=boundary,observed_margin_bytes=low-boundary,heap_valid=True,final_whole_ram_png_exact=True),evidence=refs,full_game_validated=False,limits=['Native campaign proof with logged approach hurt-counter assistance; no assistance during boss or return. Not an unassisted full campaign.','The adaptive combat predicts381 complete RAM windows; independent cold fixed replays compare final65536 RAM bytes and final PNG for each stage. They do not compare every framebuffer or the equivalent original SMS campaign.','The test boss budget ends after the full crystal/healing condition has already passed. No death or incomplete reward is promoted to completion.','Stack observation covers this cold route through D5 crystal,not every later route. Dungeons6-10,ending,full audio/visual/global timing fidelity remain unproven.','Only tools,proofs and documentation change; no new ROM number is assigned to unchanged v0292.'])
 (ROOT/'analysis/d5_campaign_v0292_report.json').write_text(json.dumps(report,indent=2)+'\n');print('Native D5 boss/crystal/exit:',len(stages),'new cold fixed replays; observed stack margin',low-boundary)

if __name__=='__main__':main()
