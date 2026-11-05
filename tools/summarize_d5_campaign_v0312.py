"""Audit fifth crystal and actual exterior return on the current cold campaign."""
import argparse,json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

CASES = [('approach01','approach'), ('release01','release'), ('boss01','boss'),
         ('return-contact01','contact'), ('exit01','exit')]


def main():
 global CASES
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--attempt',type=int,choices=[1,2],default=1);args=parser.parse_args()
 CASES=[('approach01','approach'),('release01','release'),(f'boss{args.attempt:02d}','boss'),(f'return-contact{args.attempt:02d}','contact'),(f'exit{args.attempt:02d}','exit')]
 refs = {}
 def read(p):
  raw = evidence(p); refs[p.relative_to(ROOT).as_posix()] = sha(raw); return raw
 def load(p): return json.loads(read(p))
 digest = sha((ROOT/'gaw-megadrive.bin').read_bytes())
 assert digest == '0b9aecb48fc9bb82cfcebc9547684742134d60e0f82e60b1a070ab3be50b4d64'
 prior = load(ROOT/'analysis/d5_supplies_v0312_report.json')
 assert prior['passed'] and prior['md_sha256'] == digest and not prior['fifth_boss_entered']
 index = {n:sha(read(ROOT/'tools'/n)) for n in ['natural_dungeon_combat.py','close_assisted_approach.py','unassisted_dungeon_continuation.py']}
 if args.attempt==2:index['unassisted_satellite_boss.py']=sha(read(ROOT/'tools/unassisted_satellite_boss.py'))
 sy = symbols(ROOT/'megadrive/out/release/symbol.txt')
 previous = ROOT/prior['ready_trace']; previous_cap = load(previous/'capture.json')
 initial_assist, previous_writes = recording(previous,previous_cap)
 stages = []; reports = {}; assists = {}; release = None; final_writes = None
 original = (ROOT/'input/original.sms').read_bytes()
 for suffix,kind in CASES:
  folder = ROOT/'validation/natural-dungeon-combat'/('md-auto-v0312-d5-'+suffix)
  cap = load(folder/'capture.json'); r = load(folder/'report.json'); a,writes = recording(folder,cap)
  assert cap['rom_sha256'] == r['rom_sha256'] == digest and cap['sram_input'] is None
  assert r['prefix_end'] == previous_cap['frames'] and r['recorded_new_game_prefix'] == previous.name
  assert cap['frames'] > previous_cap['frames'] and r['failure'] is None and not r.get('deaths',0)
  assert not r['sram_checkpoint_injection'] and not r['rom_modifications']
  assert len(a['episodes']) == 5 and a['boss_room'] == 0x163 and a['activation_after_frame'] == initial_assist['activation_after_frame']
  assert not a['primary_state_imports'] and not a['boss_assistance'] and not a['health_refills']
  assert writes[:len(previous_writes)] == previous_writes
  assert all(addr == sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in writes)
  assert r['driver_sha256'] == index['close_assisted_approach.py' if kind == 'release' else 'natural_dungeon_combat.py']
  proof_folder = folder.with_name(folder.name+'-assisted-fixed-replay-'+str(cap['frames']))
  proof = load(proof_folder/'replay_report.json')
  assert proof['passed'] and proof['rom_sha256'] == digest and proof['whole_ram_bytes'] == 65536
  assert proof['final_png_exact'] and not proof['feedback_reads']
  for name,h in proof['evidence'].items(): assert sha(read(folder/name)) == h
  for stem,ext in [('ram','bin'),('frame','png')]:
   n = f'{stem}_{cap["frames"]:05d}.{ext}'; assert read(folder/n) == read(proof_folder/n)
  raw = read(folder/f'ram_{cap["frames"]:05d}.bin')
  data = lambda n,k: bytes(raw[(sy[n]+i)^1] for i in range(k))
  word = lambda n: int.from_bytes(data(n,2),'big')
  items = data('hero_items',17); save = data('game_save_state',592)
  assert items[0] == 2 and items[4] == items[5] == items[12] == items[13] == items[14] == 1 and not items[8]
  assert word('hero_basic_level') == 2 and word('hero_selected_item') == 0
  assert word('hero_health') > 0 and not word('sound_unhandled_command')
  if kind == 'approach':
   assert r['room_cleared'] and word('room_id') == 0x173
   assert a['first_boss_entry'] is None and a['first_boss_combat'] is None
  if kind == 'release':
   release = cap['frames']; assert word('hero_hurt') == 0 and word('room_id') == 0x173
  if kind in ('boss','contact','exit'):
   assert r['unassisted_extension'] and not r['new_assistance_writes'] and not r['primary_state_imports']
   assert r['guard_release_frame'] == release == writes[-1][0] and writes[-1][2] == b'\0\0'
   assert r['unassisted_controller_sha256'] == index['unassisted_dungeon_continuation.py']
   assert r['extension_guard_checks_through_frame'] == cap['frames']
   if final_writes is None: final_writes = writes
   else: assert writes == final_writes
   assert save[0x1f:0x28] == bytes([128]*5+[0]*4) and word('hero_max_health') == 72
  else: assert save[0x1f:0x28] == bytes([128]*4+[0]*5)
  if kind in ('boss','exit'):
   assert r['verified_persistent_prediction_windows'] == r['full_ram_prediction_matches'] > 0
   assert not r['stack_only_difference_windows']
   sms = data('sms_vram',16384); vram = read(folder/f'vram_{cap["frames"]:05d}.bin')
   regs = read(folder/f'vdp_regs_{cap["frames"]:05d}.bin'); base = (regs[2]&56)<<10; width = [32,64,32,128][regs[16]&3]
   for n in range(128):
    at = base+((n//32+22)*width+n%32)*2
    assert int.from_bytes(vram[at:at+2],'little') == translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
   for n in range(5):
    tile,off = original[0x1edc+n*2:0x1ede+n*2]; assert sms[0x3d00+off:0x3d02+off] == bytes([tile,0x59])
  if kind == 'boss': assert r['room_cleared'] and word('hero_health') == 72 and not word('item_reward_active')
  if kind == 'contact':
   assert r['contact_route_passed'] and not r['contact_state_writes']
   assert r['contact_room'] == 0x173 and r['contact_destination'] == 0x174
  if kind == 'exit':
   assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and word('room_id') == 0x49 and not word('world_dungeon_number')
  stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),kind=kind,frames=cap['frames'],room=word('room_id'),
                     health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),keys=word('hero_keys'),
                     crystals=sum(x==128 for x in save[0x1f:0x28]),whole_ram_png_exact=True))
  read(folder/'controls.json'); read(folder/'assistance.json')
  reports[kind],assists[kind] = r,a; previous,previous_cap,previous_writes = folder,cap,writes
 first = reports['boss']['first_intermediate_combat']
 if args.attempt==2:assert reports['boss']['satellites_in_input_search'] and reports['boss']['satellite_controller_sha256']==index['unassisted_satellite_boss.py']
 assert first['health'] > 0 and first['hurt'] == 0 and any(e['kind'] == 0x65 and e['hp'] for e in first['actors'])
 rows = load(ROOT/stages[2]['trace']/'events.json')
 combat = [row for row in rows if row['room'] == 0x163 and row['game'] == 12]
 assert max(sum(e['type'] == 0x66 and e['hp'] > 0 for e in row['actors']) for row in combat) == 8
 spawned = min(row['frame'] for row in combat if sum(e['type'] == 0x66 and e['hp'] > 0 for e in row['actors']) == 8)
 vulnerable = next(row['frame'] for row in combat if row['frame'] > spawned and any(e['type'] == 0x65 and 0 < e['hp'] < 72 for e in row['actors']) and not any(e['type'] == 0x66 and e['hp'] for e in row['actors']))
 comparison=None
 if args.attempt==2:
  old_root=ROOT/'validation/natural-dungeon-combat/md-auto-v0312-d5-boss01'
  old_capture=load(old_root/'capture.json');old_report=load(old_root/'report.json')
  old_proof=load(old_root.with_name(old_root.name+f"-assisted-fixed-replay-{old_capture['frames']}")/'replay_report.json')
  _,old_writes=recording(old_root,old_capture);read(old_root/'assistance.json')
  assert old_capture['rom_sha256']==old_proof['rom_sha256']==digest and old_capture['sram_input'] is None
  assert old_proof['passed'] and old_proof['whole_ram_bytes']==65536 and old_proof['final_png_exact'] and not old_proof['feedback_reads']
  assert old_writes==final_writes and old_report['room_cleared'] and old_report['failure'] is None
  assert old_report['last_state']['progress']==128 and old_report['primary_state_imports']==0
  for n,h in old_proof['evidence'].items():assert sha(read(old_root/n))==h
  for stem,ext in [('ram','bin'),('frame','png')]:
   name=f"{stem}_{old_capture['frames']:05d}.{ext}"
   assert read(old_root/name)==read(old_root.with_name(old_root.name+f"-assisted-fixed-replay-{old_capture['frames']}")/name)
  comparison=dict(original_decisions=old_report['planning_decisions'],satellite_target_decisions=reports['boss']['planning_decisions'],
                  original_secondary_frames=old_report['secondary_frames'],satellite_target_secondary_frames=reports['boss']['secondary_frames'],
                  original_boss_capture_frame=old_capture['frames'],selected_boss_capture_frame=stages[2]['frames'],
                  both_combat_replays_whole_ram_png_exact=True,same_approach_write_list=True,
                  scope='Controller search efficiency on the same ROM and released prefix; game rules unchanged. Trial01 return was superseded; selected campaign continues from trial02.')
 result = dict(passed=True,version=312,md_sha256=digest,production_rom_unchanged=True,primary_state_imports=0,boss_attempt=args.attempt,
               stages=stages,fifth_crystal_and_exterior_return=True,guard_release_frame=release,first_boss_combat=first,planner_comparison=comparison,
               first_boss_damage=assists['boss']['first_boss_damage'],satellites_observed=8,first_observed_core_damage=vulnerable,boss_prediction_windows=reports['boss']['full_ram_prediction_matches'],
               return_prediction_windows=reports['exit']['full_ram_prediction_matches'],physical_huds_checked=2,owned_crystal_markers=5,
               full_game_validated=False,evidence=refs,
               limits=['Current-ROM cold campaign. Declared approach protection ends in the antechamber; no later writes during the boss or return.',
                       'Five crystals and their returns are covered. Remaining campaign, source RNG/global phase, optional content and global audio/video/hardware fidelity remain open.'])
 (ROOT/'analysis/d5_campaign_v0312_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
 print('v312: fifth crystal and exterior49 return verified, without boss/return assistance')


if __name__ == '__main__': main()
