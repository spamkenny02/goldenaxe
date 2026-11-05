"""Audit D5 key, Earth, actual boots reward and ordinary supply-trip exit."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

CASES = [('key01','key'), ('earth01','earth'), ('boots01','boots'), ('supply-exit01','exit')]


def main():
 refs = {}
 def read(p):
  raw = evidence(p); refs[p.relative_to(ROOT).as_posix()] = sha(raw); return raw
 def load(p): return json.loads(read(p))
 digest = sha((ROOT/'gaw-megadrive.bin').read_bytes())
 prior = load(ROOT/'analysis/fire_sword_v0314_report.json')
 assert prior['passed'] and prior['md_sha256'] == digest and prior['d5_entrance_reached']
 index = {n:sha(read(ROOT/'tools'/n)) for n in ['natural_dungeon_combat.py','natural_earth_passage.py','natural_item_acquisition.py']}
 sy = symbols(ROOT/'megadrive/out/release/symbol.txt')
 previous = ROOT/'validation/natural-dungeon-route/md-v0314-d5-entry01'
 previous_cap = load(previous/'capture.json'); previous_assist, previous_writes = recording(previous, previous_cap)
 stages = []; first_guard = None
 for suffix,kind in CASES:
  folder = ROOT/'validation/natural-dungeon-combat'/('md-auto-v0314-d5-'+suffix)
  cap = load(folder/'capture.json'); r = load(folder/'report.json'); a,writes = recording(folder,cap)
  assert cap['rom_sha256'] == r['rom_sha256'] == digest and cap['sram_input'] is None
  assert r['prefix_end'] == previous_cap['frames'] and r['recorded_new_game_prefix'] == previous.name
  assert cap['frames'] > previous_cap['frames'] and r['failure'] is None and not r['deaths']
  assert r['driver_sha256'] == index['natural_dungeon_combat.py']
  assert not r['sram_checkpoint_injection'] and not r['rom_modifications']
  assert len(a['episodes']) == 5 and a['boss_room'] == 0x163 and a['activation_after_frame'] == previous_assist['activation_after_frame']
  assert a['first_boss_entry'] is None and a['first_boss_combat'] is None
  assert not a['primary_state_imports'] and not a['boss_assistance'] and not a['health_refills']
  assert writes[:len(previous_writes)] == previous_writes
  assert all(addr == sy['hero_hurt'] and value in (b'\0\0', b'\0\x81') for _,addr,value in writes)
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
  assert save[0x1f:0x28] == bytes([128]*4+[0]*5) and word('hero_max_health') == 64
  assert items[0] == 2 and items[4] == items[5] == items[12] == items[13] == 1 and items[8] == 0
  assert word('hero_selected_item') == word('hero_weapon_level') == 1
  assert word('hero_health') > 0 and not word('sound_unhandled_command')
  if kind == 'key': assert r['new_key_verified'] and word('hero_keys') == 1
  if kind == 'earth':
   assert r['earth_route_passed'] and r['earth_passage_traversed'] and not r['earth_state_writes']
   assert r['earth_passage_room'] == 0x176 and r['earth_cell'] == 0x4a
   assert r['earth_before']['magic']-r['earth_opened']['magic'] == 8
   assert r['earth_controller_sha256'] == index['natural_earth_passage.py']
  if kind == 'boots':
   assert r['item_acquisition_passed'] and not r['item_acquisition_state_writes']
   assert r['item_acquisition_first']['owned'] == 0 and r['item_acquisition_last']['owned'] == 1
   assert not r['item_acquisition_last']['reward_active']
   assert r['item_acquisition_driver_sha256'] == index['natural_item_acquisition.py']
  if kind in ('boots','exit'):
   assert items[14] == word('hero_attack_speed') == 1
   sms = data('sms_vram',16384); vram = read(folder/f'vram_{cap["frames"]:05d}.bin')
   regs = read(folder/f'vdp_regs_{cap["frames"]:05d}.bin'); base = (regs[2]&56)<<10; width = [32,64,32,128][regs[16]&3]
   for n in range(128):
    at = base+((n//32+22)*width+n%32)*2
    assert int.from_bytes(vram[at:at+2],'little') == translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
  if kind == 'exit':
   assert r['dungeon_exit_verified'] and r['exit_before_crystal_requested'] and not r['full_dungeon_cleared']
   assert r['last_state']['completed_dungeon_progress'] == 0 and word('room_id') == 0x49 and not word('world_dungeon_number')
  stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),kind=kind,frames=cap['frames'],room=word('room_id'),
                     health=word('hero_health'),max_health=64,magic=word('hero_magic'),gold=word('hero_gold'),keys=word('hero_keys'),
                     boots=items[14],attack_speed=word('hero_attack_speed'),whole_ram_png_exact=True))
  read(folder/'controls.json'); read(folder/'assistance.json')
  previous,previous_cap,previous_writes = folder,cap,writes
 result = dict(passed=True,version=314,md_sha256=digest,production_rom_unchanged=True,primary_state_imports=0,
               stages=stages,boots_acquired=True,supply_exit_verified=True,four_crystals_retained=True,
               fifth_boss_entered=False,fifth_crystal_verified=False,physical_huds_checked=2,full_game_validated=False,evidence=refs,
               limits=['Cold campaign with explicitly logged approach protection; no resources, actors, progression or SRAM imports.',
                       'This is a supply-trip exit before the fifth boss. The fifth crystal, subsequent campaign, global SMS fidelity, optional content and hardware remain open.'])
 (ROOT/'analysis/d5_progress_v0314_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
 print('v314: D5 key, Earth, actual boots and supply exit verified; fifth boss not yet entered')


if __name__ == '__main__': main()
