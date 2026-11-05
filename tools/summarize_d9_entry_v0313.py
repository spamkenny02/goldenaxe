"""Audit current-ROM paid coastal passage and ninth-dungeon entry."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording,EPISODE_KEYS
from validate_playable_sprite_limit import symbols

def main():
 refs={}
 def read(name):
  raw=evidence(ROOT/name);refs[name]=sha(raw);return raw
 def load(name):return json.loads(read(name))
 prior=load('analysis/startup_v0313_report.json');assert prior['passed'] and prior['eighth_crystal_and_exterior_return']
 digest=sha(read('versions/v0313-48fb6e92/gaw-megadrive-v0313.bin'));assert digest==prior['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');read('megadrive/out/release/symbol.txt');index={'tools/'+k:v for k,v in load('validation/v0313-d9-sources02/entry-tools/source_index.json').items()}
 for name,h in index.items():assert sha(read('validation/v0313-d9-sources02/entry-tools/'+name.split('/')[-1]))==h and sha((ROOT/name).read_bytes())==h
 from extract_world import initial_room
 from extract_title import rle_planes
 original=read('input/original.sms');arrays=initial_room(original)[4];cells=bytearray(160);offset=int.from_bytes(arrays['world_room_index'][0xcb*2:0xcb*2+2],'little');rle_planes(arrays['world_room_streams'],offset,cells,0,1);assert cells[0x86]==0x2f
 paid=load('analysis/paid_passage_reference.json');assert paid['source_sha256']==sha(original) and [0x1a,0x3c,144,24] in paid['routes'] and paid['prices'][paid['towns'].index(0x1a)]==10
 assert original[0x3234e+0x1ac*8:0x32356+0x1ac*8]==bytes([0x6c]+[0]*7)
 previous=prior['current_campaign_trace'];pc=load(previous+'/capture.json');pa,pw=recording(ROOT/previous,pc);stages=[]
 for family,name,kind,room in [('natural-dungeon-route','md-v0313-d9-paid1a-route01','route',0x9f),('natural-service-route','md-v0313-d9-paid1a-service01','payment',0x3c),('natural-dungeon-route','md-v0313-d9-entry01','entry',0x1fc)]:
  root='validation/'+family+'/'+name;c=load(root+'/capture.json');r=load(root+('/report.json' if kind=='payment' else '/route_report.json'));f=c['frames'];proof=root+f'-assisted-fixed-replay-{f}';p=load(proof+'/replay_report.json')
  assert c['rom_sha256']==r['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None and r['failure'] is None
  assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
  assert f>pc['frames']
  if kind=='payment':assert r['source_prefix']==previous.split('/')[-1]
  else:assert r['prefix_end']==pc['frames'] and previous.split('/')[-1] in [r['recorded_combat_prefix'],r['recorded_service_prefix']]
  for filename,h in p['evidence'].items():assert sha(read(root+'/'+filename))==h
  for stem,ext in [('ram','bin'),('frame','png')]:assert read(root+f'/{stem}_{f:05d}.{ext}')==read(proof+f'/{stem}_{f:05d}.{ext}')
  a,w=recording(ROOT/root,c);read(root+'/assistance.json');assert a['preserve_floor_hurt_requested'] and len(a['episodes'])==11 and a['boss_room']==0x1ac and all(a[k] is None for k in ['first_boss_entry','release_write_frame','first_boss_combat','first_boss_damage'])
  assert w[:len(pw)]==pw and all(addr==sy['hero_hurt'] for _,addr,_ in w) and not a['boss_assistance'] and not a['health_refills'] and not a['primary_state_imports']
  if kind=='route':
   for before,after in zip(pa['episodes'],a['episodes'][:-1]):assert all(before[k]==after[k] for k in EPISODE_KEYS)
   assert a['activation_after_frame']==pc['frames'] and r['door_entry_direction']==0 and r['house_outside']==0x1a and r['house_target']==0x9f
  else:assert a['episodes'][:-1]==pa['episodes'][:-1]
  raw=read(root+f'/ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  assert word('room_id')==room and word('game_state')==12 and word('hero_health')>0 and word('hero_max_health')==96
  assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*8+[0]) and data('hero_items',17)[16]==1 and word('hero_keys')==prior['stages'][-1]['keys']
  if kind=='payment':assert r['passed'] and r['price']==10 and r['outside']==0x1a and r['target']==0x3c and r['first_state']['gold']-r['last_state']['gold']==10 and r['new_assistance_writes']==0 and w==pw and not r['currency_or_inventory_fixtures']
  else:assert r['reached_entrance'] and r['directional_probe_succeeded']
  if kind=='entry':
   assert r['bell_passage_verified'] and r['bell_new_resource_or_terrain_writes']==0
   assert sha(read(root+'/bell_world_driver.py'))==r['bell_world_driver_sha256']==index['tools/natural_bell_world_route.py']
   bell=load(root+'/bell_events.json');opened=r['bell_opened'];assert opened['room']==0xcb and opened['flag']&1 and opened['cell']==0x39 and opened['bell']==1
   assert any(e['game']==16 and e['selected']==10 for e in bell) and any(e['selected']==10 and not e['flag']&1 and e['cell']==0x2f for e in bell)
   assert data('game_save_state',592)[0x50+0xcb]&1 and word('hero_selected_item')==1 and word('hero_weapon_level')==1
   assert data('hero_items',17)[10]==data('hero_items',17)[15]==1

  stages.append(dict(trace=root,kind=kind,frames=f,room=room,health=word('hero_health'),keys=word('hero_keys'),gold=word('hero_gold'),magic=word('hero_magic'),whole_ram_png_exact=True));previous,pc,pa,pw=root,c,a,w
 read('tools/summarize_d9_entry_v0313.py')
 result=dict(passed=True,version=313,md_sha256=digest,production_rom_unchanged=True,coastal_passage_paid=True,passage_origin=0x1a,passage_destination=0x3c,passage_price=10,cb_gravestone_opened_with_owned_bell=True,stages=stages,current_campaign_trace=previous,campaign_frames=pc['frames'],eight_crystals_preserved=True,ninth_boss_entered=False,approach_assisted=True,full_game_validated=False,evidence=refs,limits=['Cold ordinary-input checkpoints with explicit hero_hurt approach assistance. No resources,actors,progression or SRAM state are imported.','The ninth-dungeon intermediate bosses1BE/79 and19C/7B must be fought with the guard removed before entry; the main1AC/6C remains unentered.','Current route pays the actual1A to3C transport and opensCB with ordinary Bell input. Historical paths are proposals only.','No complete source campaign,RNG,audiovisual,ending,save or hardware claim; stack coverage remains the prior D8 checkpoint.'])
 (ROOT/'analysis/d9_entry_v0313_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('D9 coastal fare, Bell gravestone and entry: three cold RAM/PNG gates exact')
if __name__=='__main__':main()
