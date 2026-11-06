"""Recover the eight-crystal campaign by normal Continue, free healing."""
import json,shutil
import continue_d8_entry_v0317 as helper
from continue_d8_entry_v0317 import ROOT,ROUTE,SERVICE,COMBAT,load,budget,run,assert_canonical
from cold_replay_stream import ReplayStream
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from rebase_natural_campaign import evidence
helper.EVIDENCE=ROOT/'validation/v0317-d9-recovery-sources'

def main():
 prior=json.loads((ROOT/'analysis/d8_campaign_v0317_report.json').read_bytes())
 digest=sha((ROOT/'gaw-megadrive.bin').read_bytes());assert prior['passed']and prior['md_sha256']==digest
 helper.EVIDENCE.mkdir(exist_ok=False);snapshot=helper.EVIDENCE/'sources';snapshot.mkdir()
 names=['continue_d9_recovery_v0317.py','natural_death_continue.py','natural_dungeon_route.py','natural_free_healer.py','natural_house_service.py','assisted_boss_route.py','assisted_prefix.py','cold_replay_stream.py','run_core.py']
 index={}
 for name in names:
  target=snapshot/name;shutil.copyfile(ROOT/'tools'/name,target);index[name]=sha(target.read_bytes())
 (snapshot/'source_index.json').write_text(json.dumps(index,indent=2)+'\n')
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');points=[];stream=ReplayStream(helper.EVIDENCE/'cold-stream')
 original=ROOT/prior['current_campaign_trace'];oc=json.loads((original/'capture.json').read_bytes());ow=recording(original,oc)[1]
 original_raw=(original/f'ram_{oc["frames"]:05d}.bin').read_bytes();base=lambda n,k:bytes(original_raw[(sy[n]+i)^1]for i in range(k))
 def canonical(family,name,gate,unchanged=False):
  root=ROOT/'validation'/family/name;c=load(family,name,'capture.json');r=load(family,name,'route_report.json'if family==ROUTE else'report.json');a,w=recording(root,c)
  assert r['failure']is None and gate(r),r
  assert c['rom_sha256']==digest and c['sram_input']is None and not a['primary_state_imports']and not a['health_refills']and not a['boss_assistance']
  if unchanged:assert w==ow
  assert w[:len(ow)]==ow and all(addr==sy['hero_hurt']and data in(b'\0\0',b'\0\x81')for _,addr,data in w)
  stream.prove(family+'/'+name);assert_canonical(family,name)
  raw=(root/f'ram_{c["frames"]:05d}.bin').read_bytes();data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  assert data('hero_items',17)==base('hero_items',17) and data('game_save_state',592)[0x1f:0x28]==bytes([128]*8+[0])
  assert word('hero_max_health')==96 and word('hero_keys')==1 and word('hero_health')>0 and not word('sound_unhandled_command')
  point=dict(trace=root.relative_to(ROOT).as_posix(),frames=c['frames'],room=word('room_id'),health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),gold=word('hero_gold'),keys=word('hero_keys'),whole_ram_png_exact=True)
  points.append(point);(helper.EVIDENCE/'verified_endpoints.json').write_text(json.dumps(points,indent=2)+'\n');return r,point
 try:
  death='md-v0317-d9-death-continue01'
  r,p=canonical(SERVICE,death,lambda r:r['passed']and r['normal_deaths']==r['normal_continues']==1,True)
  assert p['room']==0x95 and p['health']==p['magic']==24 and p['gold']==3
  assert r['death']['frame']<r['death_menu']['frame']<r['resumed']['frame']and r['resumed']['items']==r['first_state']['items']
  route='v0317-d9-healer94-route01'
  run('natural_dungeon_route.py',['--prefix-service',death,'--assisted-prefix','--house-outside','0x94','--house-target','0','--trial',route,'--frames',budget(SERVICE,death,6000),'--axe-terrain','--live-prefix-terrain','--live-room-replan'])
  canonical(ROUTE,'md-'+route,lambda r:r['reached_entrance']and r['directional_probe_succeeded'],True)
  heal='v0317-d9-healer94-service01'
  run('natural_free_healer.py',['--prefix','md-'+route,'--assisted-prefix','--trial',heal])
  r,p=canonical(SERVICE,'md-'+heal,lambda r:r['passed']and r['normal_health_refill'],True)
  assert p['health']==96 and p['gold']==3 and p['magic']==24
  result=dict(passed=True,version=317,md_sha256=digest,production_rom_unchanged=True,normal_death_continue=True,normal_free_healing=True,currency_or_inventory_fixtures=False,primary_state_imports=0,eight_crystals_preserved=True,stages=points,current_campaign_trace=points[-1]['trace'],campaign_frames=p['frames'],full_game_validated=False,source_index=index,scope='Current eight-crystal branch uses ordinary death/Continue and free healer. No resources,actors,progression or SRAM imported. Approach protection resumes only after real recovery; all checkpoints cold-replayed in whole RAM and PNG.')
 finally:stream.close()
 done=json.loads((helper.EVIDENCE/'cold-stream/completed.json').read_bytes())
 assert done['passed'] and done['cold_boot_count']==1 and not done['primary_state_imports']
 assert [(x['trace'],x['frames'])for x in done['checkpoints']]==[(x['trace'].removeprefix('validation/'),x['frames'])for x in points]
 refs={}
 def bind(path):refs[path.relative_to(ROOT).as_posix()]=sha(evidence(path))
 for name in ('analysis/d8_campaign_v0317_report.json','gaw-megadrive.bin','input/original.sms','megadrive/out/release/symbol.txt'):bind(ROOT/name)
 for path in snapshot.rglob('*'):
  if path.is_file():bind(path)
 for name in index:bind(ROOT/'tools'/name)
 for point in points:
  root=ROOT/point['trace'];f=point['frames'];proof=root.with_name(root.name+f'-assisted-fixed-replay-{f}')
  for name in ('capture.json','report.json','controls.json','assistance.json',f'ram_{f:05d}.bin',f'frame_{f:05d}.png'):bind(root/name)
  for name in ('replay_report.json',f'ram_{f:05d}.bin',f'frame_{f:05d}.png'):bind(proof/name)
  if (root/'route_report.json').exists():bind(root/'route_report.json')
 for name in ('completed.json','checkpoints.json'):bind(helper.EVIDENCE/'cold-stream'/name)
 result['evidence']=refs
 (ROOT/'analysis/d9_recovery_v0317_report.json').write_text(json.dumps(result,indent=2)+'\n')
 print('D9 ordinary Continue and free healing verified',flush=True)
if __name__=='__main__':main()
