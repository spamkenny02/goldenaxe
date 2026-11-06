import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'tools');from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from rebase_natural_campaign import evidence
p=Path.cwd();validation=p/'validation';refs={};h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def read(f):
 raw=evidence(f.resolve());refs[f.relative_to(p).as_posix()]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
original=(p/'input/original.sms').read_bytes();assert original[0x3234e+0x1c9*8]==0x7a and original[0x320ea+(0x7a-0x20)*4]==50
for name in ('input/original.sms','gaw-megadrive.bin','megadrive/out/release/symbol.txt'):refs[name]=h(p/name)
prior=read(p/'analysis/d7_campaign_v0317_report.json');rom=h(p/'gaw-megadrive.bin');assert prior['passed'] and prior['md_sha256']==rom
folder=p/prior['stages'][-1]['trace'];cap=read(folder/'capture.json');_,writes=recording(folder,cap);stages=[]
sy=symbols(p/'megadrive/out/release/symbol.txt')
cases=[('natural-dungeon-route','md-v0317-d8-paid3c-route01'),('natural-service-route','md-v0317-d8-paid3c-service01'),('natural-dungeon-route','md-v0317-d8-entry01'),*[('natural-dungeon-combat','md-auto-v0317-d8-'+s) for s in ('mini-ready01','guard-release01','midboss01')]]
if prior['stages'][-1]['health'] < prior['stages'][-1]['max_health']:
 cases[:0]=[('natural-dungeon-route','md-v0317-d8-healer-route01'),('natural-service-route','md-v0317-d8-heal01')]
source_folder=p/'validation/v0317-d8-sources/d8-entry-and-intermediate'
source_index=read(source_folder/'source_index.json')
for name,digest in source_index.items():
 for f in (p/'tools'/name,source_folder/name):
  assert h(f)==digest;refs[f.relative_to(p).as_posix()]=digest
for family,name in cases:
 previous,old=folder,writes;folder=validation/family/name;cap=read(folder/'capture.json');r=read(folder/('route_report.json' if family=='natural-dungeon-route' else 'report.json'));a,writes=recording(folder,cap)
 assert cap['rom_sha256']==rom and cap['sram_input'] is None and r['failure'] is None and not r.get('deaths',0) and not a['boss_assistance'] and writes[:len(old)]==old
 assert not a['primary_state_imports'] and not a['health_refills'] and all(addr==sy['hero_hurt'] and data in (b'\0\0',b'\0\x81') for _,addr,data in writes)
 f=cap['frames'];proof=folder.with_name(f'{name}-assisted-fixed-replay-{f}');q=read(proof/'replay_report.json');assert q['passed'] and q['whole_ram_bytes']==65536 and q['final_png_exact'] and not q['feedback_reads']
 for n,digest in q['evidence'].items(): assert h(folder/n)==digest;refs[(folder/n).relative_to(p).as_posix()]=digest
 for n in [f'ram_{f:05d}.bin',f'frame_{f:05d}.png']:
  assert (folder/n).read_bytes()==(proof/n).read_bytes();refs[(folder/n).relative_to(p).as_posix()]=h(folder/n)
 if family=='natural-dungeon-route':
  assert r['reached_entrance'] and r['directional_probe_succeeded'] and previous.name in (r['recorded_combat_prefix'],r['recorded_service_prefix'])
  assert not r['normal_continues'] and not r['retry_deaths']
 if family=='natural-service-route':
  assert r['passed'] and r['source_prefix']==previous.name and writes==old and not r['new_assistance_writes']
  if name.endswith('heal01'):
   assert r['normal_health_refill'] and r['first_state']['health']<r['last_state']['health']==r['last_state']['max_health']==88
   assert r['last_state']['room']==0x94 and not r['currency_or_inventory_fixtures'] and {1,2,3}.issubset(r['observed_healer_phases'])
   for key in ('gold','magic','keys','items','crystals'):assert r['first_state'][key]==r['last_state'][key]
  else:
   assert r['price']==10 and r['first_state']['gold']-r['last_state']['gold']==10 and r['last_state']['room']==0x1a
   assert not r['currency_or_inventory_fixtures']
   for key in ('health','magic','keys','inventory_hex','crystals_hex'):assert r['first_state'][key]==r['last_state'][key]
 if name.endswith('guard-release01'):assert r['last_state']['hurt']==0 and r['closed_before_room']==0x1c9 and writes[-1][0]==f
 if name.endswith('midboss01'):
  first=r['first_intermediate_combat'];assert first['hurt']==0 and first['actors']==[{'slot':0,'kind':0x7a,'hp':50}]
  assert r['room_cleared'] and not r['last_actors'] and not r['new_assistance_writes'] and writes==old and r['guard_release_frame']<first['frame'] and r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0 and not r['stack_only_difference_windows'] and r['secondary_video_suppressed'] and not r['primary_video_suppressed']
 raw=(folder/f'ram_{f:05d}.bin').read_bytes();data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
 assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*7+[0]*2) and data('hero_items',17)[16]==1
 stages.append(dict(trace=folder.relative_to(p).as_posix(),frame=f,room=r['last_state']['room'],health=r['last_state']['health'],whole_ram_png_exact=True))
cold=read(p/'validation/v0317-d8-sources/cold-stream/completed.json');assert cold['passed'] and cold['rom_sha256']==rom and not cold['primary_state_imports'] and cold['cold_boot_count']==1
assert [(x['trace'],x['frames']) for x in cold['checkpoints']]==[(x['trace'].removeprefix('validation/'),x['frame']) for x in stages]
report=dict(passed=True,version=317,md_sha256=rom,stages=stages,paid_horns=10,intermediate_defeated=True,first_combat=first,first_damage=r['first_extension_damage'],final_health=r['last_state']['health'],prediction_windows=r['full_ram_prediction_matches'],intermediate_assistance=False,full_game_validated=False,eighth_crystal_validated=False,production_rom_unchanged=True,primary_state_imports=0,evidence=refs)
(p/'analysis/d8_midboss_v0317_report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
print('v317 D8 payment, entry and unassisted intermediate verified:',len(stages),'cold RAM/PNG replays')
