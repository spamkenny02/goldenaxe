"""Audit sixth crystal and actual exterior return on the current cold campaign."""
import json
from pathlib import Path
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

CASES = [('release03','release'), ('boss01','boss'), ('exit02','exit')]


def main():
 refs = {}
 def read(p):
  raw = evidence(p); refs[p.relative_to(ROOT).as_posix()] = sha(raw); return raw
 def load(p): return json.loads(read(p))
 digest = sha((ROOT/'gaw-megadrive.bin').read_bytes())
 assert digest == '0b9aecb48fc9bb82cfcebc9547684742134d60e0f82e60b1a070ab3be50b4d64'
 prior = load(ROOT/'analysis/d6_progress_v0312_report.json')
 assert prior['passed'] and prior['md_sha256'] == digest and prior['ice_bell_acquired'] and not prior['sixth_boss_entered']
 names = load(ROOT/'validation/v0310-d6-boss-sources/source_index.json')
 index = {name:sha(read(ROOT/'tools'/name)) for name in names if (ROOT/'tools'/name).is_file()}
 for name in ('unassisted_fast_prediction.py','prediction_video_skip.py'):
  index[name] = sha(read(ROOT/'tools'/name))
 selection = dict(suffix='boss01', planning_step=8)
 cases = [('release03','release'),('boss01','boss'),('exit02','exit')]
 sy = symbols(ROOT/'megadrive/out/release/symbol.txt')
 previous = ROOT/prior['ready_trace']; previous_cap = load(previous/'capture.json')
 ready_assist, previous_writes = recording(previous,previous_cap)
 activation = ready_assist['activation_after_frame']
 stages = []; reports = {}; assists = {}; release = None; final_writes = None
 original = (ROOT/'input/original.sms').read_bytes()
 for suffix,kind in cases:
  folder = ROOT/'validation/natural-dungeon-combat'/('md-auto-v0312-d6-'+suffix)
  cap = load(folder/'capture.json'); r = load(folder/'report.json'); a,writes = recording(folder,cap)
  assert cap['rom_sha256'] == r['rom_sha256'] == digest and cap['sram_input'] is None
  assert r['prefix_end'] == previous_cap['frames'] and r['recorded_new_game_prefix'] == previous.name
  assert cap['frames'] > previous_cap['frames'] and r['failure'] is None and not r.get('deaths',0)
  assert not r['sram_checkpoint_injection'] and not r['rom_modifications']
  assert len(a['episodes']) == 6 and a['boss_room'] == 0x115 and a['activation_after_frame'] == activation
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
  assert items[10] == 1
  assert items[0] == 2 and items[4] == items[5] == items[12] == items[13] == items[14] == 1 and not items[8]
  assert word('hero_basic_level') == 2 and word('hero_selected_item') == 1
  assert word('hero_health') > 0 and not word('sound_unhandled_command')
  if kind == 'release':
   release = cap['frames']; assert word('hero_hurt') == 0 and word('room_id') == 0x125
  if kind in ('boss','exit'):
   assert r['unassisted_extension'] and not r['new_assistance_writes'] and not r['primary_state_imports']
   assert r['guard_release_frame'] == release == writes[-1][0] and writes[-1][2] == b'\0\0'
   assert r['unassisted_controller_sha256'] == index['unassisted_dungeon_continuation.py']
   assert r['extension_guard_checks_through_frame'] == cap['frames']
   if final_writes is None: final_writes = writes
   else: assert writes == final_writes
   assert save[0x1f:0x28] == bytes([128]*6+[0]*3) and word('hero_max_health') == 80
  else: assert save[0x1f:0x28] == bytes([128]*5+[0]*4)
  if kind in ('boss','exit'):
   assert r['verified_persistent_prediction_windows'] == r['full_ram_prediction_matches'] > 0
   assert not r['stack_only_difference_windows']
   sms = data('sms_vram',16384); vram = read(folder/f'vram_{cap["frames"]:05d}.bin')
   regs = read(folder/f'vdp_regs_{cap["frames"]:05d}.bin'); base = (regs[2]&56)<<10; width = [32,64,32,128][regs[16]&3]
   for n in range(128):
    at = base+((n//32+22)*width+n%32)*2
    assert int.from_bytes(vram[at:at+2],'little') == translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
   for n in range(6):
    tile,off = original[0x1edc+n*2:0x1ede+n*2]; assert sms[0x3d00+off:0x3d02+off] == bytes([tile,0x59])
  if kind == 'boss':
   assert r['room_cleared'] and word('hero_health') == 80 and not word('item_reward_active')
   assert r['planning_step'] == selection['planning_step']
   selection['report_sha256'] = sha(read(folder/'report.json'))
  if kind == 'exit':
   assert r['planning_step'] == 8 and r['secondary_video_suppressed'] and not r['primary_video_suppressed']
   assert r['prediction_video_wrapper_sha256'] == index['unassisted_fast_prediction.py']
   assert r['prediction_video_adapter_sha256'] == index['prediction_video_skip.py']
   assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and word('room_id') == 0x8b and not word('world_dungeon_number')
  stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),kind=kind,frames=cap['frames'],room=word('room_id'),
                     health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),keys=word('hero_keys'),
                     crystals=sum(x==128 for x in save[0x1f:0x28]),whole_ram_png_exact=True))
  read(folder/'controls.json'); read(folder/'assistance.json')
  reports[kind],assists[kind] = r,a; previous,previous_cap,previous_writes = folder,cap,writes
 first = reports['boss']['first_intermediate_combat']
 assert first['health'] > 0 and first['hurt'] == 0 and any(e['kind'] == 0x64 and e['hp'] == 60 for e in first['actors'])
 failed_return = load(ROOT/'validation/natural-dungeon-combat/md-auto-v0312-d6-exit01/report.json')
 assert failed_return['failure'] == 'frame_limit' and not failed_return['deaths']
 assert failed_return['last_state']['room'] == 0x178 and failed_return['last_state']['health'] == 80
 result = dict(passed=True,version=312,md_sha256=digest,production_rom_unchanged=True,primary_state_imports=0,
               stages=stages,selected_boss_trial=selection,sixth_crystal_and_exterior_return=True,guard_release_frame=release,first_boss_combat=first,
               first_boss_damage=assists['boss']['first_boss_damage'],boss_prediction_windows=reports['boss']['full_ram_prediction_matches'],
               return_prediction_windows=reports['exit']['full_ram_prediction_matches'],return_planning_step=8,secondary_video_suppressed_on_return=True,
               earlier_return_frame_limit_preserved=True,physical_huds_checked=2,owned_crystal_markers=6,
               full_game_validated=False,test_controller_sha256=index,evidence=refs,
               limits=['Current-ROM cold campaign. Declared approach protection ends in the antechamber; no later writes during the boss or return.',
                       'Six crystals and their returns are covered. Remaining campaign, source RNG/global phase, optional content and global audio/video/hardware fidelity remain open.'])
 (ROOT/'analysis/d6_campaign_v0312_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
 print('v312: sixth crystal and exterior8B return verified, without boss/return assistance')


if __name__ == '__main__': main()
