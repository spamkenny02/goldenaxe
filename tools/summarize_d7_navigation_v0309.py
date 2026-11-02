"""Audit current-ROM boat return, Earth passage and main-boss approach."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols

def main():
 refs={}
 def read(name):
  raw=evidence(ROOT/name);refs[name]=sha(raw);return raw
 def load(name):return json.loads(read(name))
 prior=load('analysis/d7_ship_v0309_report.json');assert prior['passed'] and prior['ship_acquired'] and prior['intermediate_victory_without_assistance']
 digest=sha(read('versions/v0309-7270576d/gaw-megadrive-v0309.bin'));assert digest==prior['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');read('megadrive/out/release/symbol.txt');index={'tools/'+n:h for n,h in load('validation/v0309-d7-navigation-sources/source_index.json').items()}
 for name,h in index.items():assert sha(read('validation/v0309-d7-navigation-sources/'+name.split('/')[-1]))==h and sha((ROOT/name).read_bytes())==h
 recipes=load('validation/v0309-d7-navigation-sources/navigation_recipes.json');assert len(recipes)==3
 for recipe in recipes:assert sha(read(recipe['historical']))==recipe['sha256']
 previous=prior['current_campaign_trace'];pc=load(previous+'/capture.json');pa,pw=recording(ROOT/previous,pc);stages=[]
 for suffix,expected_room in [('north-return02',0x1b8),('warp1a8-01',0x198),('approach03',0x189)]:
  root='validation/natural-dungeon-combat/md-auto-v0309-d7-'+suffix;c=load(root+'/capture.json');r=load(root+'/report.json');f=c['frames'];proof=root+f'-assisted-fixed-replay-{f}';p=load(proof+'/replay_report.json')
  assert c['rom_sha256']==r['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None
  assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads'] and r['failure'] is None and not r['deaths']
  assert r['recorded_new_game_prefix']==previous.split('/')[-1] and r['prefix_end']==pc['frames'] and f>pc['frames']
  for name,h in p['evidence'].items():assert sha(read(root+'/'+name))==h
  for stem,ext in [('ram','bin'),('frame','png')]:assert read(root+f'/{stem}_{f:05d}.{ext}')==read(proof+f'/{stem}_{f:05d}.{ext}')
  a,w=recording(ROOT/root,c);read(root+'/assistance.json');assert a['episodes'][:-1]==pa['episodes'][:-1] and w[:len(pw)]==pw and len(a['episodes'])==8
  assert a['boss_room']==0x179 and a['preserve_floor_hurt_requested'] and all(a[k] is None for k in ['first_boss_entry','release_write_frame','first_boss_combat','first_boss_damage'])
  assert all(addr==sy['hero_hurt'] for _,addr,_ in w) and not a['boss_assistance'] and not a['health_refills'] and not a['primary_state_imports']
  raw=read(root+f'/ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  assert word('room_id')==expected_room and word('game_state')==12 and word('hero_health')>0 and word('hero_max_health')==80
  assert data('hero_items',17)[16]==1 and data('game_save_state',592)[0x1f:0x28]==bytes([128]*6+[0]*3)
  if suffix=='warp1a8-01':assert r['earth_route_passed'] and r['earth_cell_cleared'] and r['earth_passage_traversed'] and r['earth_before']['magic']-r['earth_opened']['magic']==8
  if suffix=='approach03':assert r['wake_sentinels_requested'] and word('hero_keys')==prior['stages'][-1]['keys']-1
  stages.append(dict(trace=root,frames=f,room=word('room_id'),health=word('hero_health'),keys=word('hero_keys'),magic=word('hero_magic'),whole_ram_png_exact=True));previous,pc,pa,pw=root,c,a,w
 read('tools/summarize_d7_navigation_v0309.py')
 result=dict(passed=True,version=309,md_sha256=digest,production_rom_unchanged=True,stages=stages,ready_trace=previous,current_campaign_trace=previous,campaign_frames=pc['frames'],ship_owned=True,six_crystals_preserved=True,seventh_boss_entered=False,seventh_crystal_obtained=False,full_game_validated=False,evidence=refs,limits=['Only current-ROM ordinary inputs and declared approach hero_hurt writes are used. No HP,magic,currency,ownership,actor,progression or SRAM fixture.','Historical routes supply parameters only. Cold RAM/PNG equality is not whole-source RNG,full audiovisual fidelity,ending,saves or hardware proof.'])
 (ROOT/'analysis/d7_navigation_v0309_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('D7 navigation three cold gates exact; ready before main boss179')
if __name__=='__main__':main()
