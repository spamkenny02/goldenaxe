"""Audit the current-ROM cold D4 campaign, including physical reward HUDs."""
import json
from pathlib import Path
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording, prefix_writes
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

CASES = [
 ('natural-dungeon-route/md-v0310-gold-entry01', 'route'),
 ('natural-service-route/md-v0310-gold50-01', 'gold'),
 ('natural-dungeon-route/md-v0310-earth-entry02', 'route'),
 ('natural-service-route/md-v0310-earth-learn01', 'teacher'),
 ('natural-dungeon-route/md-v0310-d4-entry01', 'route'),
 ('natural-dungeon-combat/md-auto-v0310-d4-key01', 'key'),
 ('natural-dungeon-combat/md-auto-v0310-d4-earth01', 'earth'),
 ('natural-dungeon-combat/md-auto-v0310-d4-a1-key01', 'key'),
 ('natural-dungeon-combat/md-auto-v0310-d4-canoe01', 'canoe'),
 ('natural-dungeon-combat/md-auto-v0310-d4-warp01', 'warp'),
 ('natural-dungeon-combat/md-auto-v0310-d4-boss-key01', 'key'),
 ('natural-dungeon-combat/md-auto-v0310-d4-approach01', 'approach'),
 ('natural-dungeon-combat/md-auto-v0310-d4-release01', 'release'),
 ('natural-dungeon-combat/md-auto-v0310-d4-boss01', 'boss'),
 ('natural-dungeon-combat/md-auto-v0310-d4-exit02', 'exit'),
]


def main():
 files = {}
 def read(path):
  raw = evidence(path); files[path.relative_to(ROOT).as_posix()] = sha(raw); return raw
 def load(path): return json.loads(read(path))
 digest = sha((ROOT/'gaw-megadrive.bin').read_bytes())
 assert digest == '32fe75a653d7152f7cbf873a32f2ffef14234ea190885ae8a8235f2ccd10e071'
 prior = load(ROOT/'analysis/d3_campaign_v0310_report.json')
 assert prior['passed'] and prior['md_sha256'] == digest and prior['three_crystals_and_exterior_return']
 for name in ['gaw-title-megadrive.bin', 'versions/v0310-32fe75a6/gaw-megadrive-v0310.bin']:
  assert sha((ROOT/name).read_bytes()) == digest
 source_root = ROOT/'validation/v0310-d4-sources'
 source_index = load(source_root/'source_index.json')
 for name, h in source_index.items(): assert sha(read(source_root/name)) == h
 revision = load(source_root/'audit_revision2.json')
 assert revision['prior_auditor_sha256'] == source_index['summarize_d4_campaign_v0310.py']
 assert sha(read(source_root/'summarize_d4_campaign_v0310_revision2.py')) == revision['auditor_sha256'] == sha(Path(__file__).read_bytes())
 sy = symbols(ROOT/'megadrive/out/release/symbol.txt')
 original = (ROOT/'input/original.sms').read_bytes()
 previous = []; previous_frame = 66413; stages = []; reports = {}; assists = {}; water = None
 boss_writes = None; release_frame = None
 for relative, kind in CASES:
  folder = ROOT/'validation'/relative; cap = load(folder/'capture.json')
  r = load(folder/('route_report.json' if kind == 'route' else 'report.json'))
  a, writes = recording(folder, cap); read(folder/'assistance.json')
  assert cap['rom_sha256'] == r['rom_sha256'] == digest and cap['sram_input'] is None
  assert cap['frames'] > previous_frame
  if 'prefix_end' in r: assert r['prefix_end'] == previous_frame
  previous_frame = cap['frames']
  assert not a['primary_state_imports'] and not a['boss_assistance'] and not a['health_refills']
  assert not r.get('controlled_sram_fixture', False) and not r.get('sram_checkpoint_injection', False)
  assert r['failure'] is None and not r.get('deaths', 0)
  assert prefix_writes(folder, cap, True) == writes
  assert writes[:len(previous)] == previous; previous = writes
  assert all(addr == sy['hero_hurt'] and value in (b'\0\0', b'\0\x81') for _, addr, value in writes)
  for field, name in [('aim_sha256','natural_combat_aim.py'), ('earth_controller_sha256','natural_earth_passage.py'),
                      ('item_acquisition_driver_sha256','natural_item_acquisition.py'),
                      ('unassisted_controller_sha256','unassisted_dungeon_continuation.py')]:
   if r.get(field): assert r[field] == source_index[name]
  if 'driver_sha256' in r:
   candidates = ['close_assisted_approach.py'] if kind == 'release' else ['natural_dungeon_combat.py']
   assert r['driver_sha256'] in [source_index[n] for n in candidates]
  proof_folder = folder.with_name(folder.name+'-assisted-fixed-replay-'+str(cap['frames']))
  proof = load(proof_folder/'replay_report.json')
  assert proof['passed'] and proof['rom_sha256'] == digest and proof['whole_ram_bytes'] == 65536 and proof['final_png_exact']
  assert not proof['feedback_reads'] and not proof.get('controlled_sram_fixture', False)
  for stem, ext in [('ram','bin'), ('frame','png')]:
   name = f'{stem}_{cap["frames"]:05d}.{ext}'; assert read(folder/name) == read(proof_folder/name)
  read(folder/'controls.json')
  raw = read(folder/f'ram_{cap["frames"]:05d}.bin')
  data = lambda n,k: bytes(raw[(sy[n]+i)^1] for i in range(k))
  word = lambda n: int.from_bytes(data(n,2),'big')
  save = data('game_save_state',592); items = data('hero_items',17)
  assert save[0x1f:0x22] == bytes([128]*3) and items[8] == items[13] == 1
  assert word('hero_weapon_level') == word('hero_selected_item') == 1 and not word('sound_unhandled_command')
  if kind == 'route': assert r['reached_entrance'] and r['directional_probe_succeeded'] and not r['normal_continues']
  if kind == 'gold': assert r['passed'] and r['first_state']['gold'] == 2 and r['last_state']['gold'] == 52
  if kind == 'teacher':
   assert r['passed'] and r['first_state']['gold'] == 52 and r['last_state']['gold'] == 2
   assert r['first_state']['level'] == 0 and r['last_state']['level'] == 1
  if kind == 'key': assert r['new_key_verified']
  if relative.endswith('a1-key01'):
   assert r['deferred_puzzles'] == [0x1b0] and r['wake_sentinels_requested'] and not r['ignore_inactive_actors_requested']
   decisions = load(folder/'pilot_decisions.json'); assert any(x['reason'] == 'step_on_ambusher_floor' for x in decisions)
  if kind == 'approach': assert r['target_room_reached'] and not r['room_cleared'] and (word('hero_x')>>8,word('hero_y')>>8) == (128,40)
  if kind in ('earth','warp'):
   assert r['earth_route_passed'] and r['earth_passage_traversed'] and r['earth_cell_cleared'] and not r['earth_state_writes']
   assert r['earth_before']['cell'] == 11 and r['earth_before']['level'] == 1
   assert r['earth_before']['magic']-r['earth_opened']['magic'] == 8
  if kind == 'canoe':
   assert r['item_acquisition_passed'] and r['item_acquisition_first']['owned'] == 0
   assert r['item_acquisition_last']['owned'] == 1 and not r['item_acquisition_last']['reward_active']
   assert not r['item_acquisition_state_writes']
  if kind == 'warp':
   assert proof['water_observer'] and proof['water_moving_frames'] > 0 and proof['shallow_water_flag'] == 32
   water = proof['water_moving_frames']; samples = load(proof_folder/'water_samples.json')
   assert samples and all(x['owned'] for x in samples)
  if kind == 'release':
   release_frame = cap['frames']; assert word('hero_hurt') == 0 and word('room_id') == 0x190
  if kind in ('boss','exit'):
   assert r['unassisted_extension'] and not r['new_assistance_writes']
   assert writes[-1][0] == r['guard_release_frame'] == release_frame and writes[-1][2] == b'\0\0'
   assert r['full_ram_prediction_matches'] == r['verified_persistent_prediction_windows'] > 0
   assert not r['stack_only_difference_windows']
   if boss_writes is None: boss_writes = writes
   else: assert writes == boss_writes
   assert save[0x1f:0x28] == bytes([128]*4+[0]*5) and word('hero_max_health') == 64
  if kind in ('canoe','boss','exit'):
   sms = data('sms_vram',16384); vram = read(folder/f'vram_{cap["frames"]:05d}.bin'); regs = read(folder/f'vdp_regs_{cap["frames"]:05d}.bin')
   base = (regs[2]&56)<<10; width = [32,64,32,128][regs[16]&3]
   for n in range(128):
    at = base+((n//32+22)*width+n%32)*2
    assert int.from_bytes(vram[at:at+2],'little') == translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
   for n in range(4 if kind != 'canoe' else 3):
    tile, off = original[0x1edc+n*2:0x1ede+n*2]; assert sms[0x3d00+off:0x3d02+off] == bytes([tile,0x59])
  if kind == 'exit': assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and word('room_id') == 0x10 and not word('world_dungeon_number')
  stages.append(dict(trace=relative,kind=kind,frames=cap['frames'],room=word('room_id'),health=word('hero_health'),
                     max_health=word('hero_max_health'),magic=word('hero_magic'),keys=word('hero_keys'),
                     crystals=sum(x==128 for x in save[0x1f:0x28]),canoe_owned=bool(items[12]),whole_ram_png_exact=True))
  reports[kind] = r; assists[kind] = a
 first = reports['boss']['first_intermediate_combat']
 source_bosses = [k for k in original[0x3234e+0x180*8:0x32356+0x180*8] if k >= 0x20 and original[0x320ea+(k-0x20)*4+3]&0x40]
 assert source_bosses and first['health'] > 0 and first['hurt'] == 0 and any(e['kind'] in source_bosses and e['hp'] for e in first['actors'])
 assert first['health'] == 56 and any(e['kind'] == 0x6a and e['hp'] == 30 for e in first['actors'])
 assert assists['boss']['first_boss_damage'] is None
 assert reports['boss']['extension_guard_checks_through_frame'] == stages[-2]['frames']
 assert reports['exit']['extension_guard_checks_through_frame'] == stages[-1]['frames']
 result = dict(passed=True,version=310,md_sha256=digest,production_rom_unchanged=True,
               fourth_crystal_and_exterior_return=True,primary_state_imports=0,stages=stages,
               first_boss_combat=first,first_boss_damage=assists['boss']['first_boss_damage'],
               guard_release_frame=release_frame,canoe_water_moving_frames=water,physical_reward_huds_checked=3,
               full_game_validated=False,evidence=files,
               limits=['Cold boot and normal inventory/progression. Logged approach protection ends before boss entry; no new writes during fight or return.',
                       'Optional B0 mechanism deferred. One current NTSC path. Global SMS fidelity, optional content, hardware and remaining current-ROM campaign remain unproved.'])
 (ROOT/'analysis/d4_campaign_v0310_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
 print('v310: fourth crystal and exterior return verified; no SRAM imports; physical HUDs exact')


if __name__ == '__main__': main()
