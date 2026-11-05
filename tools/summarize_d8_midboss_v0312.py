import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'tools');from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
p=Path.cwd();validation=p/'validation';refs={};h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def read(f):
 refs[f.relative_to(p).as_posix()]=h(f);return json.loads(f.read_bytes())
prior=read(p/'analysis/d7_campaign_v0312_report.json');rom=h(p/'gaw-megadrive.bin');assert prior['passed'] and prior['md_sha256']==rom
folder=p/prior['stages'][-1]['trace'];cap=read(folder/'capture.json');_,writes=recording(folder,cap);stages=[]
sy=symbols(p/'megadrive/out/release/symbol.txt')
cases=[('natural-dungeon-route','md-v0312-d8-paid3c-route01'),('natural-service-route','md-v0312-d8-paid3c-service01'),('natural-dungeon-route','md-v0312-d8-entry01'),*[('natural-dungeon-combat','md-auto-v0312-d8-'+s) for s in ('mini-ready01','guard-release01','midboss01')]]
for family,name in cases:
 previous,old=folder,writes;folder=validation/family/name;cap=read(folder/'capture.json');r=read(folder/('route_report.json' if family=='natural-dungeon-route' else 'report.json'));a,writes=recording(folder,cap)
 assert cap['rom_sha256']==rom and cap['sram_input'] is None and r['failure'] is None and not r.get('deaths',0) and not a['boss_assistance'] and writes[:len(old)]==old
 assert not a['primary_state_imports'] and not a['health_refills'] and all(addr==sy['hero_hurt'] and data in (b'\0\0',b'\0\x81') for _,addr,data in writes)
 f=cap['frames'];proof=folder.with_name(f'{name}-assisted-fixed-replay-{f}');q=read(proof/'replay_report.json');assert q['passed'] and q['whole_ram_bytes']==65536 and q['final_png_exact'] and not q['feedback_reads']
 for n,digest in q['evidence'].items(): assert h(folder/n)==digest;refs[(folder/n).relative_to(p).as_posix()]=digest
 for n in [f'ram_{f:05d}.bin',f'frame_{f:05d}.png']:
  assert (folder/n).read_bytes()==(proof/n).read_bytes();refs[(folder/n).relative_to(p).as_posix()]=h(folder/n)
 if family=='natural-dungeon-route':assert r['reached_entrance'] and r['directional_probe_succeeded'] and previous.name in (r['recorded_combat_prefix'],r['recorded_service_prefix'])
 if family=='natural-service-route':assert r['passed'] and r['source_prefix']==previous.name and r['price']==10 and r['first_state']['gold']-r['last_state']['gold']==10 and r['last_state']['room']==0x1a and writes==old
 if name.endswith('guard-release01'):assert r['last_state']['hurt']==0 and r['closed_before_room']==0x1c9 and writes[-1][0]==f
 if name.endswith('midboss01'):
  first=r['first_intermediate_combat'];assert first['hurt']==0 and first['actors']==[{'slot':0,'kind':0x7a,'hp':50}]
  assert r['room_cleared'] and not r['last_actors'] and not r['new_assistance_writes'] and writes==old and r['guard_release_frame']<first['frame'] and r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0 and not r['stack_only_difference_windows'] and r['secondary_video_suppressed'] and not r['primary_video_suppressed']
 raw=(folder/f'ram_{f:05d}.bin').read_bytes();data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
 assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*7+[0]*2) and data('hero_items',17)[16]==1
 stages.append(dict(trace=folder.relative_to(p).as_posix(),frame=f,room=r['last_state']['room'],health=r['last_state']['health'],whole_ram_png_exact=True))
report=dict(passed=True,version=312,md_sha256=rom,stages=stages,paid_horns=10,intermediate_defeated=True,first_combat=first,first_damage=r['first_extension_damage'],final_health=r['last_state']['health'],prediction_windows=r['full_ram_prediction_matches'],intermediate_assistance=False,full_game_validated=False,eighth_crystal_validated=False,production_rom_unchanged=True,primary_state_imports=0,evidence=refs)
(p/'analysis/d8_midboss_v0312_report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
print('v312 D8 payment, entry and unassisted intermediate verified with six cold RAM/PNG replays')
