"""Verify real coin collection and cold replay before using its state as a campaign prefix."""
import argparse,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
p=argparse.ArgumentParser();p.add_argument('--trial',default='08');a=p.parse_args();assert a.trial.isdigit()
work=Path(__file__).resolve().parent;project=work/'isolated/project';folder=project/f'validation/natural-dungeon-combat/md-pal-palc0046-d9-funds{a.trial}'
source=project/'validation/natural-dungeon-combat/md-pal-palc0046-d8-exit01'
paths={Path(__file__).resolve()}
def read(p):paths.add(p);return p.read_bytes()
def load(p):return json.loads(read(p))
r=load(folder/'report.json');c=load(folder/'capture.json');s=load(source/'capture.json');prior=load(ROOT/'analysis/palc0046_d8_report.json')
assert prior['passed'] and prior['actual_eighth_crystal_and_exterior'] and r['passed'] and r['ordinary_gold_goal_reached'] and r['failure'] is None and r['deaths']==0 and r['new_resource_writes']==0 and r['primary_state_imports']==0
assert c['rom_sha256']==s['rom_sha256']==prior['rom_sha256']=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5' and c['sram_input'] is None and c['frames']>s['frames'] and c['core_options']['genesis_plus_gx_region_detect']=='pal'
assist,w=recording(folder,c);old,previous=recording(source,s);sy=symbols(project/'megadrive/out/release/symbol.txt')
assert w[:len(previous)]==previous and all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in w)
assert not assist['primary_state_imports'] and not assist['boss_assistance'] and not assist['health_refills'] and assist['release_near_coins_requested'] and assist['boss_room']==0x1ac and assist['first_boss_entry'] is None
assert assist['episodes'][:-1][-1]['first_boss_combat']==old['first_boss_combat'] and assist['episodes'][-1]['activation_after_frame']==s['frames']
f=c['frames'];raw=read(folder/f'ram_{f:05d}.bin');before=read(source/f'ram_{s["frames"]:05d}.bin');data=lambda ram,n,k:bytes(ram[(sy[n]+i)^1] for i in range(k));word=lambda ram,n:int.from_bytes(data(ram,n,2),'big')
assert word(before,'hero_gold')==7 and word(raw,'hero_gold')>=10 and word(raw,'game_state')==12 and word(raw,'room_id')<256 and word(raw,'hero_health')>0 and word(raw,'hero_max_health')==96 and not word(raw,'sound_unhandled_command')
assert data(raw,'hero_items',17)==data(before,'hero_items',17) and word(raw,'hero_keys')==word(before,'hero_keys')==2 and data(raw,'game_save_state',592)[0x1f:0x28]==bytes([128]*8+[0])
assert r['gold_events'][0]['gold']==7 and r['gold_events'][-1]['gold']==word(raw,'hero_gold') and all(row['frame']>s['frames'] and row['health']>0 for row in r['gold_events'])
proof=folder.with_name(folder.name+f'-assisted-fixed-replay-{f}')
if not proof.exists():subprocess.run([sys.executable,'tools/replay_assisted_prefix.py','--trace','natural-dungeon-combat/'+folder.name],cwd=project,check=True)
pr=load(proof/'replay_report.json');assert pr['passed'] and pr['rom_sha256']==c['rom_sha256'] and pr['whole_ram_bytes']==65536 and pr['final_png_exact'] and not pr['feedback_reads']
for n,h in pr['evidence'].items():assert sha(read(folder/n))==h
for stem,ext in [('ram','bin'),('frame','png')]:assert read(folder/f'{stem}_{f:05d}.{ext}')==read(proof/f'{stem}_{f:05d}.{ext}')
for path in folder.iterdir():
 if path.is_file():read(path)
for path in project.glob('validation/palc0046-d9-guarded-funding*/funding_controller.py'):
 if sha(path.read_bytes())==r['driver_sha256']:
  for p in path.parent.glob('*.py'):read(p)
out=ROOT/f'analysis/palc0046-d9-funding-success{a.trial}'
result=dict(passed=True,candidate='c0046',region='pal',rom_sha256=c['rom_sha256'],current_campaign_trace=folder.relative_to(ROOT).as_posix(),campaign_frames=f,gold_before=7,gold_after=word(raw,'hero_gold'),final_health=word(raw,'hero_health'),ordinary_coin_collection=True,approach_protection=True,protection_released_near_actual_coins=True,primary_state_imports=0,resource_or_actor_writes=0,whole_ram_bytes_exact=65536,final_png_exact=True,full_game_validated=False,archive_manifest=(out/'manifest.json').relative_to(ROOT).as_posix(),scope='Real exterior kills and coin pickups after eight crystals, with declared approach-only hurt protection and ordinary coin contact. No currency/ownership/actor/progression/SRAM imports. Exact cold whole-RAM/PNG endpoint; does not validate D9 entry or any boss.')
freeze(ROOT,out,paths,result,[work]);(ROOT/'analysis/palc0046_d9_funding_success_report.json').write_text(json.dumps(result,indent=2)+'\n');print('PAL real funding verified, replayed and archived',flush=True)
