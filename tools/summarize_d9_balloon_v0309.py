"""Audit the optional D9 giant and real Balloon acquisition on cold v309."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

SPECS=[('approach-resume01','resume',0x1be),('switch1ad-01','contact',0x1ad),
       ('portal19e-ready01','portal',0x19e),('giant-ready02','reach',0x19d),
       ('giant-release01','release',0x19d),('giant01','giant',0x19c),
       ('post-giant-resume01','resume2',0x19c),('balloon01','item',0x19b)]

def main():
 refs={}
 def read(p):
  raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
 def load(p):return json.loads(read(p))
 digest='7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049'
 assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==digest
 prior=load(ROOT/'analysis/d9_midboss_v0309_report.json')
 assert prior['passed'] and prior['first_intermediate_defeated'] and not prior['intermediate_assistance']
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
 source=ROOT/'validation/v0309-d9-balloon-sources';index=load(source/'source_index.json')
 for n,h in index.items():
  assert sha(read(source/n))==h
  current=ROOT/('megadrive/src'if n.endswith('.c')else'tools')/n
  assert sha(current.read_bytes())==h
 original=read(ROOT/'input/original.sms')
 assert original[0x3234e+0x19c*8:0x32356+0x19c*8]==bytes([0x7b]+[0]*7)
 assert original[0x320ea+(0x7b-0x20)*4:0x320ee+(0x7b-0x20)*4]==bytes([60,20,6,32])
 rewards=load(ROOT/'analysis/item_rewards_reference.json');assert rewards['source_sha256']==sha(original)
 assert any(x['room']==0x19b and x.get('inventory_offset')==11 and x['value']==1 for x in rewards['records'])
 previous=ROOT/prior['current_campaign_trace'];pc=load(previous/'capture.json');pa,pw=recording(previous,pc)
 stages=[];release=None;giant_report=None;fixed=None
 for suffix,kind,room in SPECS:
  folder=ROOT/'validation/natural-dungeon-combat'/('md-auto-v0309-d9-'+suffix)
  cap=load(folder/'capture.json');r=load(folder/'report.json');a,w=recording(folder,cap);f=cap['frames']
  assert cap['rom_sha256']==r['rom_sha256']==digest and cap['sram_input'] is None
  assert r['failure'] is None and not r['deaths'] and r['prefix_end']==pc['frames'] and r['recorded_new_game_prefix']==previous.name and f>pc['frames']
  proof_folder=folder.with_name(folder.name+'-assisted-fixed-replay-'+str(f));proof=load(proof_folder/'replay_report.json')
  assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads'] and proof['rom_sha256']==digest
  for n,h in proof['evidence'].items():assert sha(read(folder/n))==h
  for stem,ext in [('ram','bin'),('frame','png')]:assert read(folder/f'{stem}_{f:05d}.{ext}')==read(proof_folder/f'{stem}_{f:05d}.{ext}')
  assert not a['boss_assistance'] and not a['health_refills'] and not a['primary_state_imports']
  assert len(a['episodes'])==(13 if kind in ('resume2','item')else 12) and a['boss_room']==0x1ac and a['first_boss_entry'] is None
  assert all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in w)
  raw=read(folder/f'ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  items=data('hero_items',17);save=data('game_save_state',592);actors=data('world_actor_state',768)
  assert word('room_id')==room and word('game_state')==12 and 0<word('hero_health')<=96 and word('hero_max_health')==96 and not word('sound_unhandled_command')
  assert save[0x1f:0x28]==bytes([128]*8+[0]) and items[10]==items[15]==items[16]==1
  assert items[11]==int(kind=='item')
  if kind in ('resume','resume2'):
   assert r['resumed_after_verified_intermediate'] and r['new_guard_frame']==f and w==pw+[(f,sy['hero_hurt'],b'\0\x81')]
   assert a['intermediate_entry_cold_verified'] and a['main_boss_never_entered_in_prefix'] and a['episodes'][:-2]==pa['episodes'][:-1]
   oldraw=read(previous/f'ram_{pc["frames"]:05d}.bin')
   for n,k in [('hero_health',2),('hero_magic',2),('hero_gold',2),('hero_keys',2),('hero_items',17)]:assert data(n,k)==bytes(oldraw[(sy[n]+i)^1]for i in range(k))
   ep=a['episodes'][-2];assert ep['boss_room']==(0x1be if kind=='resume' else 0x19c)
   assert ep['release_write_frame']==(prior['guard_release_frame']if kind=='resume'else release)
  elif kind=='release':
   release=f;fixed=w;assert w==pw+[(f,sy['hero_hurt'],b'\0\0')] and word('hero_hurt')==0 and a['closed_before_room']==0x19c
  elif kind=='giant':
   assert w==fixed and all(t<=release for t,_,_ in w) and r['unassisted_extension'] and not r['new_assistance_writes'] and not r['primary_state_imports']
   assert r['guard_release_frame']==release and r['extension_guard_checks_through_frame']==f and r['room_cleared']
   first=r['first_intermediate_combat'];assert first['room']==0x19c and first['frame']>release and first['health']>0 and first['hurt']<=128 and first['actors']==[dict(slot=0,kind=0x7b,hp=60)]
   assert not any(actors[i*48]==0x7b and actors[i*48+24]for i in range(8))
   assert word('hero_selected_item')==0 and word('hero_basic_level')==2 and word('hero_attack')==6
   assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0 and not r['stack_only_difference_windows']
   giant_report=r
  else:
   assert w[:len(pw)]==pw and a['episodes'][:-1]==pa['episodes'][:-1]
   if kind=='contact':assert r['contact_route_passed'] and not r['contact_state_writes'] and r['contact_opened']['flags']&4
   elif kind=='portal':assert r['room_cleared'] and r['avoided_portal_rooms']==[0x19e]
   elif kind=='reach':
    assert r['target_room_reached'] and r['reach_room_requested'] and not r['room_cleared'] and (word('hero_x')>>8,word('hero_y')>>8)==(24,88)
    assert [actors[i*48]for i in range(4)]==[0x62]*4 and all(actors[i*48+24]==0 for i in range(4))
   elif kind=='item':
    assert r['item_acquisition_passed'] and r['collect_item_requested']==11 and not r['item_acquisition_state_writes']
    assert not r['item_acquisition_first']['owned'] and r['item_acquisition_last']['owned']==1 and not word('item_reward_active')
    assert not save[0x150+0x9c] and word('hero_selected_item')==1
  stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),kind=kind,frames=f,room=room,health=word('hero_health'),magic=word('hero_magic'),gold=word('hero_gold'),keys=word('hero_keys'),balloon_owned=bool(items[11]),whole_ram_png_exact=True))
  read(folder/'controls.json');read(folder/'assistance.json');previous,pc,pa,pw=folder,cap,a,w
 sms=data('sms_vram',16384);vram=read(previous/f'vram_{pc["frames"]:05d}.bin');regs=read(previous/f'vdp_regs_{pc["frames"]:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
 for n in range(128):
  at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
 for n in range(8):
  tile,off=original[0x1edc+n*2:0x1ede+n*2];assert sms[0x3d00+off:0x3d02+off]==bytes([tile,0x59])
 result=dict(passed=True,version=309,md_sha256=digest,production_rom_unchanged=True,stages=stages,current_campaign_trace=stages[-1]['trace'],campaign_frames=pc['frames'],optional_giant_defeated=True,balloon_acquired=True,giant_guard_release_frame=release,first_giant_combat=giant_report['first_intermediate_combat'],giant_first_damage=giant_report['first_extension_damage'],giant_prediction_windows=giant_report['full_ram_prediction_matches'],persistent_62_hazards_retained=True,final_hud_words_exact=128,source_crystal_markers_exact=8,ninth_crystal_obtained=False,full_game_validated=False,evidence=refs,limits=['The giant fight has no new test writes after release; approach assistance resumes only after canonical victories. No resources,actors,progression or SRAM are imported.','Actual Balloon acquisition is covered,not actual Balloon overview activation/return or global SMS RNG,audiovisual,save or hardware fidelity.'])
 (ROOT/'analysis/d9_balloon_v0309_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
 print('D9 optional giant and real Balloon: eight canonical checkpoints verified')
if __name__=='__main__':main()
