"""Audit normal D7 gifts, key purchase, healing and first dungeon key."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols

CASES = [
 ('natural-dungeon-route/md-v0309-d7-gold7d-route01','route'),
 ('natural-service-route/md-v0309-d7-gold7d-service01','gift'),
 ('natural-dungeon-route/md-v0309-d7-goldac-route01','route'),
 ('natural-service-route/md-v0309-d7-goldac-service01','gift'),
 ('natural-dungeon-route/md-v0309-d7-merchant2e-route01','route'),
 ('natural-service-route/md-v0309-d7-key2e-service01','purchase'),
 ('natural-dungeon-route/md-v0309-d7-entry01','route'),
 ('natural-dungeon-combat/md-auto-v0309-d7-key01','key'),
]


def main():
 refs = {}
 def read(p):
  raw = evidence(p); refs[p.relative_to(ROOT).as_posix()] = sha(raw); return raw
 def load(p): return json.loads(read(p))
 digest = sha((ROOT/'gaw-megadrive.bin').read_bytes())
 prior = load(ROOT/'analysis/d6_campaign_v0309_report.json')
 assert prior['passed'] and prior['md_sha256'] == digest and prior['sixth_crystal_and_exterior_return']
 source = ROOT/'validation/v0309-d7-sources'; index = load(source/'source_index.json')
 for name,h in index.items(): assert sha(read(source/name)) == h
 sy = symbols(ROOT/'megadrive/out/release/symbol.txt')
 previous = ROOT/prior['stages'][-1]['trace']; previous_cap = load(previous/'capture.json')
 _, previous_writes = recording(previous,previous_cap)
 stages = []; gifts = []; purchase = None
 for relative,kind in CASES:
  folder = ROOT/'validation'/relative; cap = load(folder/'capture.json')
  r = load(folder/('route_report.json' if kind == 'route' else 'report.json'))
  a,writes = recording(folder,cap)
  assert cap['rom_sha256'] == r['rom_sha256'] == digest and cap['sram_input'] is None
  assert r['failure'] is None and not r.get('deaths',0) and not r.get('sram_checkpoint_injection',False)
  assert cap['frames'] > previous_cap['frames'] and writes[:len(previous_writes)] == previous_writes
  assert all(addr == sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in writes)
  assert len(a['episodes']) == 7 and a['boss_room'] == 0x179 and a['activation_after_frame'] == 182351
  assert a['first_boss_entry'] is None and a['first_boss_combat'] is None
  assert not a['boss_assistance'] and not a['primary_state_imports'] and not a['health_refills']
  if kind == 'route':
   assert r['prefix_end'] == previous_cap['frames'] and r['reached_entrance'] and r['directional_probe_succeeded']
   assert (r['recorded_combat_prefix'] or r['recorded_service_prefix']) == previous.name and not r['normal_continues']
   assert r['route_driver_sha256'] == index['natural_dungeon_route.py']
   if 'goldac-route' in relative: assert r['required_chop_verified']
  elif kind == 'key':
   assert r['prefix_end'] == previous_cap['frames'] and r['recorded_new_game_prefix'] == previous.name
   assert r['new_key_verified'] and r['room_cleared']
   assert r['driver_sha256'] == index['natural_dungeon_combat.py']
  else:
   assert r['passed'] and r['source_prefix'] == previous.name and not r['new_assistance_writes']
   assert writes == previous_writes
   if kind == 'gift':
    assert r['last_state']['gold']-r['first_state']['gold'] == 30
    assert r['last_state']['outside_flags'] == r['first_state']['outside_flags']|2
    gifts.append(dict(room=r['last_state']['room'],before=r['first_state']['gold'],after=r['last_state']['gold']))
   else:
    assert r['keys_bought'] == 1 and r['unit_price'] == 60 and not r['currency_or_inventory_fixtures']
    assert r['first_state']['gold']-r['last_state']['gold'] == 60
    assert r['last_state']['keys']-r['first_state']['keys'] == 1
    assert not r['free_healing_completed'] and r['last_state']['health'] == r['first_state']['health']
    purchase = dict(room=0x2e,price=60,health_before=r['first_state']['health'],health_after=r['last_state']['health'],
                    healing_observed=False)
  proof_folder = folder.with_name(folder.name+'-assisted-fixed-replay-'+str(cap['frames']))
  proof = load(proof_folder/'replay_report.json')
  assert proof['passed'] and proof['rom_sha256'] == digest and proof['whole_ram_bytes'] == 65536
  assert proof['final_png_exact'] and not proof['feedback_reads']
  for name,h in proof['evidence'].items(): assert sha(read(folder/name)) == h
  for stem,ext in [('ram','bin'),('frame','png')]:
   name = f'{stem}_{cap["frames"]:05d}.{ext}'; assert read(folder/name) == read(proof_folder/name)
  raw = read(folder/f'ram_{cap["frames"]:05d}.bin')
  data = lambda n,k: bytes(raw[(sy[n]+i)^1] for i in range(k))
  word = lambda n: int.from_bytes(data(n,2),'big')
  items = data('hero_items',17); save = data('game_save_state',592)
  assert save[0x1f:0x28] == bytes([128]*6+[0]*3) and word('hero_max_health') == 80 and word('hero_health')>0
  assert items[0] == 2 and items[1] == items[4] == items[5] == items[10] == items[12] == items[13] == items[14] == 1
  assert not items[8] and not items[16] and word('hero_selected_item') == 1 and not word('sound_unhandled_command')
  stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),kind=kind,frames=cap['frames'],room=word('room_id'),
                     health=word('hero_health'),keys=word('hero_keys'),gold=word('hero_gold'),whole_ram_png_exact=True))
  read(folder/'controls.json'); read(folder/'assistance.json')
  previous,previous_cap,previous_writes = folder,cap,writes
 assert [v['room'] for v in gifts] == [0x7d,0xac] and stages[-1]['room'] == 0x1cb and stages[-1]['keys'] == 1
 result = dict(passed=True,version=309,md_sha256=digest,production_rom_unchanged=True,stages=stages,
               gold_gifts=gifts,purchase=purchase,six_crystals_preserved=True,primary_state_imports=0,
               intermediate_boss_entered=False,seventh_boss_entered=False,seventh_crystal_validated=False,
               current_campaign_trace=previous.relative_to(ROOT).as_posix(),campaign_frames=previous_cap['frames'],
               full_game_validated=False,evidence=refs,
               limits=['Current cold campaign with explicitly logged approach protection only. No money,items,health,actors,progression or SRAM imports.',
                       'The planner could not find a route to merchant94; the successful historical2E destination is used. No healing or intermediate1B8/type78/main179/type67 victory is claimed.'])
 (ROOT/'analysis/d7_supplies_v0309_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
 print('v309: eight D7 supply/entry/key checkpoints verified, intermediate boss not yet entered')


if __name__ == '__main__': main()
