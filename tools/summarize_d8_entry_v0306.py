"""Audit current-ROM paid coastal passage and eighth-dungeon entry."""
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
 prior=load('analysis/d7_campaign_v0306_report.json');assert prior['passed'] and prior['seventh_crystal_and_exterior_exit']
 digest=sha(read('versions/v0306-3a12380b/gaw-megadrive-v0306.bin'));assert digest==prior['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');read('megadrive/out/release/symbol.txt');index=load('validation/v0306-d8-entry-sources/source_index.json')
 for name,h in index.items():assert sha(read('validation/v0306-d8-entry-sources/'+name.split('/')[-1]))==h and sha((ROOT/name).read_bytes())==h
 original=read('input/original.sms');paid=load('analysis/paid_passage_reference.json');assert paid['source_sha256']==sha(original) and [0x3c,0x1a,32,232] in paid['routes'] and paid['prices'][paid['towns'].index(0x3c)]==10
 assert original[0x3234e+0x196*8:0x32356+0x196*8]==bytes([0x6b]+[0]*7)
 previous=prior['current_campaign_trace'];pc=load(previous+'/capture.json');pa,pw=recording(ROOT/previous,pc);stages=[]
 for family,name,kind,room in [('natural-dungeon-route','md-v0306-d8-paid3c-route01','route',0x9f),('natural-service-route','md-v0306-d8-paid3c-service01','payment',0x1a),('natural-dungeon-route','md-v0306-d8-entry03','entry',0x1ea)]:
  root='validation/'+family+'/'+name;c=load(root+'/capture.json');r=load(root+('/report.json' if kind=='payment' else '/route_report.json'));f=c['frames'];proof=root+f'-assisted-fixed-replay-{f}';p=load(proof+'/replay_report.json')
  assert c['rom_sha256']==r['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None and r['failure'] is None
  assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
  assert f>pc['frames']
  if kind=='payment':assert r['source_prefix']==previous.split('/')[-1]
  else:assert r['prefix_end']==pc['frames'] and previous.split('/')[-1] in [r['recorded_combat_prefix'],r['recorded_service_prefix']]
  for filename,h in p['evidence'].items():assert sha(read(root+'/'+filename))==h
  for stem,ext in [('ram','bin'),('frame','png')]:assert read(root+f'/{stem}_{f:05d}.{ext}')==read(proof+f'/{stem}_{f:05d}.{ext}')
  a,w=recording(ROOT/root,c);read(root+'/assistance.json');assert a['preserve_floor_hurt_requested'] and len(a['episodes'])==9 and a['boss_room']==0x196 and all(a[k] is None for k in ['first_boss_entry','release_write_frame','first_boss_combat','first_boss_damage'])
  assert w[:len(pw)]==pw and all(addr==sy['hero_hurt'] for _,addr,_ in w) and not a['boss_assistance'] and not a['health_refills'] and not a['primary_state_imports']
  if kind=='route':
   for before,after in zip(pa['episodes'],a['episodes'][:-1]):assert all(before[k]==after[k] for k in EPISODE_KEYS)
   assert a['activation_after_frame']==pc['frames'] and r['door_entry_direction']==1 and r['house_outside']==0x3c and r['house_target']==0x9f
  else:assert a['episodes'][:-1]==pa['episodes'][:-1]
  raw=read(root+f'/ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  assert word('room_id')==room and word('game_state')==12 and word('hero_health')>0 and word('hero_max_health')==88
  assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*7+[0]*2) and data('hero_items',17)[16]==1 and word('hero_keys')==1
  if kind=='payment':assert r['passed'] and r['price']==10 and r['outside']==0x3c and r['target']==0x1a and r['first_state']['gold']-r['last_state']['gold']==10 and r['new_assistance_writes']==0 and w==pw and not r['currency_or_inventory_fixtures']
  else:assert r['reached_entrance'] and r['directional_probe_succeeded']
  stages.append(dict(trace=root,kind=kind,frames=f,room=room,health=word('hero_health'),keys=word('hero_keys'),gold=word('hero_gold'),magic=word('hero_magic'),whole_ram_png_exact=True));previous,pc,pa,pw=root,c,a,w
 read('tools/summarize_d8_entry_v0306.py')
 result=dict(passed=True,version=306,md_sha256=digest,production_rom_unchanged=True,coastal_passage_paid=True,passage_origin=0x3c,passage_destination=0x1a,passage_price=10,stages=stages,current_campaign_trace=previous,campaign_frames=pc['frames'],seventh_crystal_preserved=True,eighth_boss_entered=False,approach_assisted=True,full_game_validated=False,evidence=refs,limits=['Cold ordinary-input checkpoints with explicit hero_hurt approach assistance. No resources,actors,progression or SRAM state are imported.','The eight-dungeon intermediate7A must be approached with the guard removed before its fight; the main196/6B remains unentered.','No complete source campaign,RNG,audiovisual,ending,save or hardware claim; stack coverage remains the prior D7 checkpoint.'])
 (ROOT/'analysis/d8_entry_v0306_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('D8 coastal fare and entry: three independent cold RAM/PNG gates exact')
if __name__=='__main__':main()
