"""Audit already completed Continue/healer checkpoints without replaying gameplay."""
import json
from pathlib import Path
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols

def main():
 refs={}
 def read(p):
  raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
 def load(p):return json.loads(read(p))
 prior=load(ROOT/'analysis/d8_campaign_v0317_report.json');digest=sha(read(ROOT/'gaw-megadrive.bin'))
 assert prior['passed'] and prior['md_sha256']==digest
 base=ROOT/'validation/v0317-d9-recovery-sources'
 done=load(base/'cold-stream/completed.json');points=load(base/'verified_endpoints.json')
 assert done['passed'] and done['rom_sha256']==digest and done['cold_boot_count']==1 and not done['primary_state_imports']
 assert [(x['trace'],x['frames'])for x in done['checkpoints']]==[(x['trace'].removeprefix('validation/'),x['frames'])for x in points]
 assert len(points)==3
 index=load(base/'sources/source_index.json')
 for name,h in index.items():assert sha(read(base/'sources'/name))==h
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');read(ROOT/'megadrive/out/release/symbol.txt')
 original=ROOT/prior['current_campaign_trace'];oc=load(original/'capture.json');ow=recording(original,oc)[1]
 before=read(original/f'ram_{oc["frames"]:05d}.bin')
 results=[]
 for row in points:
  root=ROOT/row['trace'];c=load(root/'capture.json');r=load(root/('route_report.json' if root.parent.name=='natural-dungeon-route' else 'report.json'));a,w=recording(root,c)
  assert r['failure']is None and c['rom_sha256']==digest and c['sram_input']is None and w==ow
  assert not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance']
  f=c['frames'];proof=root.with_name(root.name+f'-assisted-fixed-replay-{f}');p=load(proof/'replay_report.json')
  assert p['passed'] and p['rom_sha256']==digest and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
  for name,h in p['evidence'].items():assert sha(read(root/name))==h
  for name in (f'ram_{f:05d}.bin',f'frame_{f:05d}.png'):assert read(root/name)==read(proof/name)
  raw=read(root/f'ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  assert data('hero_items',17)==bytes(before[(sy['hero_items']+i)^1]for i in range(17))
  assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*8+[0])
  assert word('hero_max_health')==96 and word('hero_keys')==1 and word('hero_magic')==24 and word('hero_gold')==3 and word('hero_health')>0 and not word('sound_unhandled_command')
  results.append(r)
 death,route,heal=results
 assert death['passed'] and death['normal_deaths']==death['normal_continues']==1 and not death['new_assistance_writes']
 assert death['death']['frame']<death['death_menu']['frame']<death['resumed']['frame'] and death['resumed']['room']==0x95
 assert death['resumed']['health']==death['resumed']['magic']==24
 assert route['reached_entrance'] and route['directional_probe_succeeded'] and not route['normal_continues']
 assert heal['passed'] and heal['normal_health_refill'] and not heal['new_assistance_writes'] and not heal['currency_or_inventory_fixtures']
 assert heal['first_state']['health']==24 and heal['last_state']['health']==96 and heal['last_state']['room']==0x94
 for key in ('gold','magic','keys','items','crystals'):assert heal['first_state'][key]==heal['last_state'][key]
 read(Path(__file__).resolve())
 report=dict(passed=True,version=317,md_sha256=digest,production_rom_unchanged=True,normal_death_continue=True,normal_free_healing=True,currency_or_inventory_fixtures=False,primary_state_imports=0,eight_crystals_preserved=True,stages=points,current_campaign_trace=points[-1]['trace'],campaign_frames=points[-1]['frames'],full_game_validated=False,evidence=refs,export_recovered_after_missing_import=True)
 (ROOT/'analysis/d9_recovery_v0317_report.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Continue and free healer verified from three completed cold checkpoints')

if __name__=='__main__':main()
