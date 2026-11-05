"""Audit ordinary death/Continue and free healing on the eight-crystal v314 branch."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols

def main():
 refs={}
 def read(p):
  raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
 def load(p):return json.loads(read(p))
 prior=load(ROOT/'analysis/d8_campaign_v0314_report.json');digest=sha((ROOT/'gaw-megadrive.bin').read_bytes());assert prior['passed']and prior['md_sha256']==digest
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');source=ROOT/prior['current_campaign_trace'];pc=load(source/'capture.json');_,writes=recording(source,pc)
 base=read(source/f'ram_{pc["frames"]:05d}.bin');base_items=bytes(base[(sy['hero_items']+i)^1]for i in range(17));stages=[]
 for family,name,kind in [('natural-service-route','md-v0314-d9-death-continue01','continue'),('natural-dungeon-route','md-v0314-d9-healer94-route01','route'),('natural-service-route','md-v0314-d9-healer94-service01','heal')]:
  root=ROOT/'validation'/family/name;c=load(root/'capture.json');r=load(root/('route_report.json'if kind=='route'else'report.json'));a,w=recording(root,c);read(root/'assistance.json')
  assert c['rom_sha256']==r['rom_sha256']==digest and c['sram_input']is None and r['failure']is None and c['frames']>pc['frames']
  assert w==writes and not a['primary_state_imports']and not a['health_refills']and not a['boss_assistance']and len(a['episodes'])==10
  proof=root.with_name(name+'-assisted-fixed-replay-'+str(c['frames']));p=load(proof/'replay_report.json')
  assert p['passed']and p['rom_sha256']==digest and p['whole_ram_bytes']==65536 and p['final_png_exact']and not p['feedback_reads']
  for n,h in p['evidence'].items():assert sha(read(root/n))==h
  for stem,ext in [('ram','bin'),('frame','png')]:
   f=f'{stem}_{c["frames"]:05d}.{ext}';assert read(root/f)==read(proof/f)
  raw=read(root/f'ram_{c["frames"]:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  assert data('hero_items',17)==base_items and data('game_save_state',592)[0x1f:0x28]==bytes([128]*8+[0])
  assert word('hero_max_health')==96 and word('hero_max_magic')==72 and word('hero_keys')==1 and word('hero_gold')==6 and word('hero_magic')==24 and not word('sound_unhandled_command')
  if kind=='continue':
   assert r['passed']and r['source_trace']==source.relative_to(ROOT/'validation').as_posix()and r['normal_deaths']==r['normal_continues']==1
   assert r['death']['health']==0 and r['death']['frame']<r['death_menu']['frame']<r['resumed']['frame']
   assert r['first_state']['health']==80 and r['first_state']['gold']==8 and r['resumed']['health']==r['resumed']['magic']==24 and r['resumed']['gold']==(8>>2)*3
   assert word('room_id')==0x95 and word('hero_health')==24 and not r['new_assistance_writes']and not r['currency_or_inventory_fixtures']and not r['primary_state_imports']
  elif kind=='route':assert r['reached_entrance']and r['directional_probe_succeeded']and r['recorded_service_prefix']==source.name and r['prefix_end']==pc['frames']and word('room_id')==0
  else:
   assert r['passed']and r['source_prefix']==source.name and r['normal_health_refill']and not r['new_assistance_writes']and not r['currency_or_inventory_fixtures']and not r['primary_state_imports']
   assert r['first_state']['health']==24 and r['healed']['health']==96 and {1,2,3}.issubset(r['observed_healer_phases'])and word('room_id')==0x94 and word('hero_health')==96
  stages.append(dict(trace=root.relative_to(ROOT).as_posix(),kind=kind,frames=c['frames'],room=word('room_id'),health=word('hero_health'),max_health=96,magic=24,gold=6,keys=1,whole_ram_png_exact=True));source,pc=root,c
 result=dict(passed=True,md_sha256=digest,version=314,stages=stages,current_campaign_trace=stages[-1]['trace'],campaign_frames=stages[-1]['frames'],normal_death_continue=True,normal_free_healing=True,eight_crystals_preserved=True,all_owned_items_preserved=True,new_assistance_writes=0,currency_or_inventory_fixtures=False,primary_state_imports=0,full_game_validated=False,evidence=refs,limits=['Ordinary death and Continue, then actual free healer. The declared cold campaign now contains one normal death, not a deathless run. No resources,actors,progression or SRAM imported.','Continue returns to the source southern checkpoint95; D9 may be approached from this region without repeating the northern paid transport. Subsequent routes and D9 remain to validate.','The attempted A6 gift route after these three completed checkpoints had no static path and never ran gameplay; no gift or money gain is claimed.'])
 (ROOT/'analysis/d9_recovery_v0314_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('Normal Continue and free healer: three full-RAM/PNG gates verified')
if __name__=='__main__':main()
