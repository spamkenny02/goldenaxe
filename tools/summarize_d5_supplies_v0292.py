"""Verified supply trip and D5 route through the Earth warp/contact mechanism."""
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
 digest=sha(read('gaw-megadrive.bin'));assert digest==sha(read('versions/v0292-6eeb5608/gaw-megadrive-v0292.bin'));sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
 names=[('natural-dungeon-combat','md-auto-v0292-d5-supply-exit01','exit')]
 for suffix in ['54','a1','b5','b4']:
  names.extend([('natural-dungeon-route','md-v0292-d5-gold'+suffix+'-route01','route'),('natural-service-route','md-v0292-d5-gold'+suffix+'-service01','gold')])
 names.extend([('natural-dungeon-route','md-v0292-d5-merchant94-route01','route'),('natural-service-route','md-v0292-d5-keys94-service03','purchase'),('natural-dungeon-route','md-v0292-d5-return-route02','route'),('natural-dungeon-combat','md-auto-v0292-d5-warp04','earth'),('natural-dungeon-combat','md-auto-v0292-d5-contact01','contact')])
 stages=[];reports={};states={}
 for family,name,kind in names:
  root='validation/'+family+'/'+name;r=load(root+('/route_report.json' if kind=='route' else '/report.json'));c=load(root+'/capture.json');p=load(root+f'-assisted-fixed-replay-{c["frames"]}/replay_report.json')
  assert c['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None and p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
  assert r['failure'] is None and (r['reached_entrance'] if kind=='route' else r['room_cleared'] if kind=='exit' else r['passed'])
  a,w=recording(ROOT/root,c);read(root+'/assistance.json');assert a['boss_room']==0x163 and a['first_boss_entry'] is None and a['first_boss_combat'] is None and not a['health_refills'] and not a['primary_state_imports'] and all(address==sy['hero_hurt'] for _,address,_ in w)
  for fn,h in p['evidence'].items():assert sha(read(root+'/'+fn))==h
  raw=read(root+f'/ram_{c["frames"]:05d}.bin');read(root+f'/frame_{c["frames"]:05d}.png')
  data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
  assert data('hero_items',17)[12:15]==bytes([1,1,1]) and data('game_save_state',592)[0x1f:0x23]==bytes([128]*4) and data('game_save_state',592)[0x23]==0
  stages.append(dict(trace=root,kind=kind,frames=c['frames'],whole_ram_bytes=65536,final_png_exact=True));reports[name]=r;states[name]=r['last_state']
 exit=reports['md-auto-v0292-d5-supply-exit01'];assert exit['dungeon_exit_verified'] and not exit['full_dungeon_cleared'] and exit['last_state']['completed_dungeon_progress']==0
 gains=[]
 for suffix,amount in [('54',10),('a1',30),('b5',10),('b4',30)]:
  r=reports['md-v0292-d5-gold'+suffix+'-service01'];assert r['last_state']['gold']-r['first_state']['gold']==amount and not r['new_assistance_writes'];gains.append(amount)
 purchase=reports['md-v0292-d5-keys94-service03'];assert purchase['unit_price']==60 and purchase['keys_bought']==2 and purchase['first_state']['gold']==128 and purchase['last_state']['gold']==8 and purchase['first_state']['keys']==0 and purchase['last_state']['keys']==2 and purchase['free_healing_completed'] and purchase['last_state']['health']==64 and not purchase['currency_or_inventory_fixtures']
 earth=reports['md-auto-v0292-d5-warp04'];assert earth['earth_route_passed'] and earth['earth_passage_room']==0x153 and earth['earth_cell']==0x44 and earth['earth_opened']['cell']==0x0c and earth['earth_before']['magic']-earth['earth_opened']['magic']==8
 contact=reports['md-auto-v0292-d5-contact01'];assert contact['contact_route_passed'] and contact['contact_room']==0x162 and contact['contact_destination']==0x172 and contact['contact_opened']['flags']&4 and not contact['contact_state_writes'] and contact['last_state']['health']==64 and contact['last_state']['keys']==2
 for name in ['natural_dungeon_combat.py','natural_dungeon_route.py','natural_house_service.py','natural_merchant_purchase.py','natural_earth_passage.py','natural_contact_passage.py','assisted_boss_route.py','replay_assisted_prefix.py','run_core.py']:read('tools/'+name)
 boots=load('analysis/boots_timing_v0292_report.json');assert boots['passed'] and boots['md_sha256']==digest
 report=dict(passed=True,version=292,md_sha256=digest,production_rom_unchanged=True,stages=stages,scope_ends_before_boss=True,dungeon5_completed=False,full_game_validated=False,source_campaign_compared=False,boots_controlled_movement_cases=96,boots_controlled_movement_frame_comparisons=3072,gold_gifts=gains,keys_bought=2,key_price=60,actual_free_healing=True,post_supply_health=64,earth_warp_room=0x153,earth_warp_cell=0x44,earth_warp_destination=0x162,contact_room=0x162,contact_destination=0x172,last_state=contact['last_state'],evidence=refs,limits=['Fourteen official cold fixed replays compare entire RAM and final PNG,not every framebuffer or original SMS campaign.','All campaign fixtures are explicitly logged approach hurt-counter writes. Inventory,money,keys and healing are obtained by normal game input. The movement-table benchmark separately controls fixtures.','The incomplete exit is a supply trip,not a crystal or dungeon-completion claim. The checkpoint stops before the boss.'])
 (ROOT/'analysis/d5_supplies_v0292_report.json').write_text(json.dumps(report,indent=2)+'\n');print('D5 supplies/warp/contact:14 official RAM/PNG replays; checkpoint before boss')

if __name__=='__main__':main()
