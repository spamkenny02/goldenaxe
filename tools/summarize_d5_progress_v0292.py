"""Record native D5 key, Earth opening and actual boots acquisition."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols

def main():
 refs={}
 def read(name):raw=evidence(ROOT/name);refs[name]=sha(raw);return raw
 def load(name):return json.loads(read(name))
 approach=load('analysis/d5_approach_v0292_report.json');assert approach['passed']
 digest=sha(read('gaw-megadrive.bin'));assert digest==approach['md_sha256']
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');stages=[];states={};reports={}
 for suffix,kind in [('key01','key'),('earth02','earth'),('boots03','boots')]:
  name='validation/natural-dungeon-combat/md-auto-v0292-d5-'+suffix;r=load(name+'/report.json');c=load(name+'/capture.json');p=load(name+f'-assisted-fixed-replay-{c["frames"]}/replay_report.json')
  assert r['failure'] is None and not r['deaths'] and r['last_state']['health']>0 and not r['last_state']['audio_error']
  assert p['passed'] and p['rom_sha256']==c['rom_sha256']==digest and c['sram_input'] is None and p['whole_ram_bytes']==65536 and p['final_png_exact']
  a,w=recording(ROOT/name,c);read(name+'/assistance.json');assert a['boss_room']==0x163 and a['first_boss_entry'] is None and a['first_boss_combat'] is None and not a['health_refills']
  assert all(address==sy['hero_hurt'] for _,address,_ in w)
  for fn,h in p['evidence'].items():assert sha(read(name+'/'+fn))==h
  raw=read(name+f'/ram_{c["frames"]:05d}.bin');read(name+f'/frame_{c["frames"]:05d}.png')
  data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
  assert data('game_save_state',592)[0x1f:0x23]==bytes([128]*4) and data('hero_items',17)[12]
  states[kind]=r['last_state'];reports[kind]=r
  stages.append(dict(trace=name,kind=kind,frames=c['frames'],room=r['last_state']['room'],health=r['last_state']['health'],keys=r['last_state']['keys'],magic=r['last_state']['magic'],whole_ram_bytes=65536,final_png_exact=True))
  if kind=='key':assert r['room_cleared'] and r['new_key_verified'] and r['last_state']['room']==0x176 and r['last_state']['keys']==1
  if kind=='earth':
   assert r['passed'] and r['earth_route_passed'] and r['earth_passage_opened'] and r['earth_state_writes']==0 and r['earth_cell']==0x4a and r['earth_passage_room']==0x176
   assert r['earth_before']['cell']==11 and r['earth_opened']['cell']==0 and r['earth_before']['magic']-r['earth_opened']['magic']==8 and r['earth_opened']['flags']&0x24==0x24 and r['last_state']['room']==0x166
  if kind=='boots':assert r['room_cleared'] and r['collect_item_requested']==14 and r['last_state']['item_value']==1 and data('hero_items',17)[14] and r['last_state']['room']==0x157
 for name in ['natural_dungeon_combat.py','natural_earth_passage.py','assisted_boss_route.py','replay_assisted_prefix.py']:read('tools/'+name)
 report=dict(passed=True,version=292,md_sha256=digest,production_rom_unchanged=True,stages=stages,canoe_and_first_four_crystals_retained=True,boots_acquired=True,boots_movement_timing_compared=False,earth_magic_spent=8,keys_consumed_between_earth_and_boots=states['earth']['keys']-states['boots']['keys'],last_state=states['boots'],assisted_approach=True,primary_state_imports=0,boss_reached=False,boss_victory_validated=False,dungeon5_completed=False,full_game_validated=False,source_campaign_comparison=False,evidence=refs)
 (ROOT/'analysis/d5_progress_v0292_report.json').write_text(json.dumps(report,indent=2)+'\n');print('D5 key,Earth andboots: three official whole-RAM/PNG replays; boss stillopen')

if __name__=='__main__':main()
