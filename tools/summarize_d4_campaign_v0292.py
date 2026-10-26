"""Current native D4 completion, acquired canoe/warp, and scoped source evidence."""
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
 digest=sha(read('gaw-megadrive.bin'));assert digest==sha(read('versions/v0292-6eeb5608/gaw-megadrive-v0292.bin'));sy=symbols(ROOT/'megadrive/out/release/symbol.txt');canoe=load('analysis/canoe_campaign_v0292_report.json');assert canoe['passed'] and canoe['md_sha256']==digest and len(canoe['stages'])==6
 stages=[];reports={};assists={}
 names=[('sms-auto-v0292-source-d4-boss-key02','key'),('md-auto-v0292-d4-boss-key02','key'),('md-auto-v0292-d4-boss02','fight_partial_heal'),('md-auto-v0292-d4-crystal01','crystal'),('md-auto-v0292-d4-exit02','exit')]
 for name,kind in names:
  root='validation/natural-dungeon-combat/'+name;r=load(root+'/report.json');c=load(root+'/capture.json');p=load(root+f'-assisted-fixed-replay-{c["frames"]}/replay_report.json');sms=name.startswith('sms');expected=sha(read('input/original.sms')) if sms else digest
  assert c['rom_sha256']==p['rom_sha256']==expected and c['sram_input'] is None and p['passed'] and p['whole_ram_bytes']==(8192 if sms else 65536) and p['final_png_exact'] and not p['boss_assistance']
  assist,writes=recording(ROOT/root,c);read(root+'/assistance.json');read(root+'/controls.json');assert all(address==(0x305 if sms else sy['hero_hurt']) for _,address,_ in writes)
  assert all(p['evidence'][n]==sha(read(root+'/'+n)) for n in ['capture.json','controls.json','assistance.json'])
  assert not r['deaths'] and r['last_state']['health']>0 and not r['last_state']['audio_error']
  if kind=='key':assert r['room_cleared'] and r['new_key_verified'] and r['last_state']['keys']==1 and r['last_state']['room']==0x182 and not r['failure']
  else:
   assert assist['boss_room']==0x180 and assist['release_write_frame']==79684 and assist['first_boss_combat']==dict(frame=79729,health=56,hurt=0)
   assert writes[-1][0]==79684 and writes[-1][2]==b'\0\0' and r['last_state']['max_health']==64
  if kind=='fight_partial_heal':assert r['failure']=='frame_limit' and r['last_state']['progress']==128 and r['last_state']['health']==62 and r['planning_decisions']==r['verified_persistent_prediction_windows']==r['full_ram_prediction_matches']==261
  if kind=='crystal':assert r['room_cleared'] and not r['failure'] and r['last_state']['health']==64 and r['last_state']['progress']==128 and not r['last_state']['reward_active'] and r['last_state']['hero']==1
  if kind=='exit':
   assert not r['failure'] and r['full_dungeon_cleared'] and r['last_state']['room']==16 and r['last_state']['dungeon']==0 and r['last_state']['completed_dungeon_progress']==128 and r['last_state']['health']==62
   assert assist['new_assistance_writes']==0 and assist['unassisted_extension'] and r['planning_decisions']==r['verified_persistent_prediction_windows']==r['full_ram_prediction_matches']==110
   raw=read(root+f'/ram_{c["frames"]:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));assert data('game_save_state',592)[0x1f:0x23]==bytes([128]*4) and data('hero_items',17)[12:14]==b'\1\1'
  stages.append(dict(trace=root,role=kind,frames=c['frames'],rom_sha256=expected,last_state=r['last_state'],whole_ram_png_cold_replay=True,assisted_history=True));reports[kind]=r;assists[kind]=assist
 grabs=[]
 for tag,name in [('sms','sms-auto-v0292-source-d4-a1-key03'),('md','md-auto-v0292-d4-a1-key03')]:
  root='validation/natural-dungeon-combat/'+name;c=load(root+'/capture.json');prefix=root+f'-assisted-fixed-replay-{c["frames"]}-grab01';g=load(prefix+'/replay_report.json');samples=load(prefix+'/grab_samples.json');releases=load(prefix+'/grab_releases.json')
  assert g['passed'] and g['final_png_exact'] and g['grab_observer'] and g['grab_alive_release_events']==2 and g['grab_frames']==len(samples) and len(releases)==2 and all(v['health']>0 for v in releases)
  grabs.append(dict(system=tag,grab_frames=g['grab_frames'],live_releases=2,rooms=g['grab_rooms']))
 stackroot='validation/stack-v0292-d4-crystal-all';stack=load(stackroot+'/stack_report.json');assert stack['md_sha256']==digest and stack['all_instructions'] and stack['frames']==82483 and not stack['invalid_heap_examples']
 low=min(r['sp'] for r in stack['instruction_minima']);boundary=stack['heap_changes'][-1]['end']+2;assert low>=boundary
 for stem,ext in [('ram','bin'),('frame','png')]:assert read(stackroot+f'/{stem}_82483.{ext}')==read('validation/natural-dungeon-combat/md-auto-v0292-d4-crystal01'+f'/{stem}_82483.{ext}')
 diagnostics=[]
 for name in ['sms-auto-v0292-source-d4-boss02','sms-auto-v0292-source-d4-boss03','sms-auto-v0292-source-d4-boss04','sms-auto-v0292-source-d4-boss05']:
  r=load('validation/natural-dungeon-combat/'+name+'/report.json');assert not r['room_cleared'];diagnostics.append(dict(trace=name,failure=r['failure'],health=r['last_state']['health'],remaining_boss_hp=next((a['hp'] for a in r['last_actors'] if a['type']==0x6a),None)))
 for name in ['movement_reference.py','natural_dungeon_combat.py','natural_earth_passage.py','natural_combat_navigation.py','natural_boss_evasive_planner.py','natural_boss_escape_planner.py','natural_boss_side_planner.py','assisted_boss_route.py','replay_assisted_prefix.py','validate_canoe_campaign_v0292.py']:read('tools/'+name)
 rom=read('gaw-megadrive.bin');checksum=sum(int.from_bytes(rom[i:i+2],'big') for i in range(0x200,len(rom),2))&65535;assert checksum==int.from_bytes(rom[0x18e:0x190],'big')
 report=dict(passed=True,version=292,md_sha256=digest,checksum=f'{checksum:04X}',production_rom_unchanged=True,native_dungeon4_completed=True,source_boss_victory_validated=False,canoe_report='analysis/canoe_campaign_v0292_report.json',new_stages=stages,total_canoe_and_d4_stages=11,grab_observers=grabs,boss_guard=dict(release_frame=79684,first_combat_frame=79729,lead_frames=45,first_damage=assists['fight_partial_heal']['first_boss_damage'],new_post_boss_writes=0),stack=dict(frames=82483,all_instructions=True,minimum_sp=low,heap_boundary=boundary,observed_margin_bytes=low-boundary,heap_valid=True,final_whole_ram_png_exact=True),source_fight_diagnostics=diagnostics,evidence=refs,full_game_validated=False,limits=['The current native cold campaign acquires canoe/warp,obtains the boss key,defeats boss4,collects its crystal and exits at62/64HP with all four crystals and canoe/rope present.','Logged hurt-counter assistance is restricted to approaches. The last D4 write is zero45frames before combat; no new assistance after the boss. Native lookahead has261 fight and110 exit windows matching the entire RAM; only the secondary core imports search states.','The initial fight budget stops inside normal healing at62/64HP; a separate ordinary continuation finishes64/64HP before the unassisted return. This is a stopped test,not a failed healing routine.','The source canoe/warp/key/grab/water stages pass independent fixed replays,but the original boss fight has no victory proof: one ordinary attempt dies and adaptive attempts hit their budgets with boss alive. These diagnostics are not promoted to source completion or cross-system combat timing equivalence.','Stack/heap observations cover cold boot through native crystal82483,not every later route. Hardware/global timing,RNG,complete sound/framebuffer equivalence,remaining six dungeons and ending remain unproven.','Only controller/navigation/reporting code changes in this milestone; no new ROM number is created for the unchanged v0292 binary.'])
 (ROOT/'analysis/d4_campaign_v0292_report.json').write_text(json.dumps(report,indent=2)+'\n');print('Native D4 complete;',len(stages),'additional replayed stages;stack margin',low-boundary)
if __name__=='__main__':main()
