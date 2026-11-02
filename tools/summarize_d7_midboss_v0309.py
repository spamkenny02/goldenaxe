"""Audit ordinary D7 intermediate combat, with the approach guard closed first."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols

CASES = [('key03','key'),('earth1b9-01','earth'),('earth1b9-02','earth'),
         ('guard-release01','release'),('contact1b9-01','contact'),('midboss01','combat')]


def main():
 refs = {}
 def read(p):
  raw = evidence(p); refs[p.relative_to(ROOT).as_posix()] = sha(raw); return raw
 def load(p): return json.loads(read(p))
 digest = sha((ROOT/'gaw-megadrive.bin').read_bytes())
 prior = load(ROOT/'analysis/d7_supplies_v0309_report.json')
 assert prior['passed'] and prior['md_sha256'] == digest and prior['six_crystals_preserved']
 source = ROOT/'validation/v0309-d7-midboss-sources'; index = load(source/'source_index.json')
 for name,h in index.items(): assert sha(read(source/name)) == h
 original = read(ROOT/'input/original.sms')
 assert original[0x3234e+0x1b8*8] == 0x78
 assert original[0x320ea+(0x78-0x20)*4:0x320ee+(0x78-0x20)*4] == bytes([30,12,4,32])
 sy = symbols(ROOT/'megadrive/out/release/symbol.txt')
 previous = ROOT/prior['current_campaign_trace']; pc = load(previous/'capture.json')
 _, previous_writes = recording(previous,pc); stages = []; closed = None; release = None; reports = {}
 for suffix,kind in CASES:
  folder = ROOT/'validation/natural-dungeon-combat'/('md-auto-v0309-d7-'+suffix)
  cap = load(folder/'capture.json'); r = load(folder/'report.json'); a,writes = recording(folder,cap)
  assert cap['rom_sha256'] == r['rom_sha256'] == digest and cap['sram_input'] is None
  assert r['prefix_end'] == pc['frames'] and r['recorded_new_game_prefix'] == previous.name and cap['frames'] > pc['frames']
  assert r['failure'] is None and not r.get('deaths',0) and not r.get('rom_modifications',False) and not r.get('sram_checkpoint_injection',False)
  assert len(a['episodes']) == 7 and a['boss_room'] == 0x179 and a['first_boss_entry'] is None
  assert not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance']
  assert writes[:len(previous_writes)] == previous_writes
  assert all(addr == sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in writes)
  assert r['driver_sha256'] == index['close_assisted_approach.py' if kind == 'release' else 'natural_dungeon_combat.py']
  proof_folder = folder.with_name(folder.name+'-assisted-fixed-replay-'+str(cap['frames']))
  proof = load(proof_folder/'replay_report.json')
  assert proof['passed'] and proof['rom_sha256'] == digest and proof['whole_ram_bytes'] == 65536 and proof['final_png_exact'] and not proof['feedback_reads']
  for name,h in proof['evidence'].items(): assert sha(read(folder/name)) == h
  for stem,ext in [('ram','bin'),('frame','png')]:
   name = f'{stem}_{cap["frames"]:05d}.{ext}'; assert read(folder/name) == read(proof_folder/name)
  raw = read(folder/f'ram_{cap["frames"]:05d}.bin')
  data = lambda n,k: bytes(raw[(sy[n]+i)^1] for i in range(k))
  word = lambda n: int.from_bytes(data(n,2),'big')
  items = data('hero_items',17); save = data('game_save_state',592)
  assert save[0x1f:0x28] == bytes([128]*6+[0]*3) and word('hero_max_health') == 80 and word('hero_health') > 0
  assert items[0] == 2 and items[1] == items[4] == items[5] == items[10] == items[12] == items[13] == items[14] == 1 and not items[16]
  assert word('hero_selected_item') == 1 and not word('sound_unhandled_command')
  if kind == 'key': assert r['new_key_verified'] and word('hero_keys') == 2
  if kind == 'earth':
   assert r['earth_route_passed'] and r['earth_cell_cleared'] and r['earth_action_only_requested'] and not r['earth_state_writes']
   assert r['earth_before']['magic']-r['earth_opened']['magic'] == 8
   assert r['earth_controller_sha256'] == index['natural_earth_passage.py']
  if kind == 'release':
   release = cap['frames']; assert word('hero_hurt') == 0 and word('room_id') == 0x1b9 and a['closed_before_room'] == 0x1b8
   assert writes == previous_writes+[(release,sy['hero_hurt'],b'\0\0')]; closed = writes
  if kind in ('contact','combat'):
   assert writes == closed and writes[-1][0] == r['guard_release_frame'] == release
   assert r['unassisted_extension'] and not r['new_assistance_writes'] and not r['primary_state_imports']
   assert r['unassisted_controller_sha256'] == index['unassisted_dungeon_continuation.py'] and r['extension_guard_checks_through_frame'] == cap['frames']
  if kind == 'contact': assert r['contact_route_passed'] and not r['contact_state_writes'] and r['contact_destination'] == 0x1b8
  if kind == 'combat':
   assert r['room_cleared'] and word('room_id') == 0x1b8
   assert r['full_ram_prediction_matches'] == r['verified_persistent_prediction_windows'] > 0 and not r['stack_only_difference_windows']
  read(folder/'controls.json'); read(folder/'assistance.json')
  stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),kind=kind,frames=cap['frames'],room=word('room_id'),health=word('hero_health'),magic=word('hero_magic'),keys=word('hero_keys'),whole_ram_png_exact=True))
  reports[kind] = r; previous,pc,previous_writes = folder,cap,writes
 first = reports['combat']['first_intermediate_combat']
 assert first['room'] == 0x1b8 and first['hurt'] == 0 and first['health'] == 66
 assert any(e['kind'] == 0x78 and e['hp'] == 30 for e in first['actors'])
 result = dict(passed=True,version=309,md_sha256=digest,stages=stages,production_rom_unchanged=True,primary_state_imports=0,
               intermediate_defeated=True,intermediate_assistance=False,guard_release_frame=release,first_intermediate_combat=first,
               first_intermediate_damage=reports['combat']['first_extension_damage'],full_ram_prediction_matches=reports['combat']['full_ram_prediction_matches'],
               main_boss_entered=False,seventh_crystal_validated=False,full_game_validated=False,
               current_campaign_trace=previous.relative_to(ROOT).as_posix(),campaign_frames=pc['frames'],evidence=refs,
               limits=['Cold prefix, actual two8MP Earth casts, guard released before1B8 and no later writes during intermediate combat.',
                       'Main179 and seventh crystal remain unvalidated by this report. Boat is not yet acquired.'])
 (ROOT/'analysis/d7_midboss_v0309_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
 print('v309: intermediate78 defeated without protection; six checkpoints replay fullRAM/PNG exactly')


if __name__ == '__main__': main()
