"""Audit first palace giant on the actual cold nine-crystal campaign."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

SPECS=[('panel16d01','panel'),('switch16d01','west'),('pre-giant02','north'),('giant-release02','release'),('giant02','giant')]
def main():
 refs={}
 def read(p):
  raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
 def load(p):return json.loads(read(p))
 prior=load(ROOT/'analysis/cold_palace_entry_v0309_report.json');assert prior['passed'] and prior['cold_palace_entered'] and not prior['primary_state_imports']
 digest=prior['md_sha256'];assert digest==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 source_indices={}
 for name in ['v0309-cold-palace-giant-sources','v0309-cold-palace-giant02-sources']:
  source=ROOT/'validation'/name;index=load(source/'source_index.json');source_indices[name]=index
  for n,h in index.items():assert sha(read(source/n.split('/')[-1]))==h
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');original=read(ROOT/'input/original.sms')
 assert original[0x3234e+0x15e*8:0x32356+0x15e*8]==bytes([0x7b]+[0]*7)
 assert original[0x320ea+(0x7b-0x20)*4:0x320ee+(0x7b-0x20)*4]==bytes([60,20,6,32])
 previous=ROOT/prior['current_campaign_trace'];pc=load(previous/'capture.json');pa,pw=recording(previous,pc)
 stages=[];release=None;fixed=None;combat=None;damage=None;giant_report=None
 for suffix,kind in SPECS:
  p=ROOT/'validation/natural-dungeon-combat'/('md-auto-v0309-cold-palace-'+suffix);c=load(p/'capture.json');r=load(p/'report.json');a,w=recording(p,c);f=c['frames']
  assert c['rom_sha256']==r['rom_sha256']==digest and c['sram_input'] is None and r['failure'] is None and not r['deaths']
  index=source_indices['v0309-cold-palace-giant-sources' if kind in ('panel','west') else 'v0309-cold-palace-giant02-sources']
  if kind in ('panel','west','north'):assert r['driver_sha256']==index['tools/natural_dungeon_combat.py']
  assert r['prefix_end']==pc['frames'] and r['recorded_new_game_prefix']==previous.name and f>pc['frames']
  proofp=p.with_name(p.name+'-assisted-fixed-replay-'+str(f));proof=load(proofp/'replay_report.json')
  assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads'] and proof['rom_sha256']==digest
  for n,h in proof['evidence'].items():assert sha(read(p/n))==h
  for stem,ext in [('ram','bin'),('frame','png')]:assert read(p/f'{stem}_{f:05d}.{ext}')==read(proofp/f'{stem}_{f:05d}.{ext}')
  assert len(a['episodes'])==14 and a['boss_room']==0x14c and a['first_boss_entry'] is None
  assert not a['boss_assistance'] and not a['primary_state_imports'] and not a['health_refills']
  assert all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81')for _,addr,value in w)
  raw=read(p/f'ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  items=data('hero_items',17);save=data('game_save_state',592);actors=data('world_actor_state',768)
  assert word('game_state')==12 and word('world_dungeon_number')==10 and 0<word('hero_health')<=104 and word('hero_max_health')==104 and not word('sound_unhandled_command')
  assert save[0x1f:0x28]==bytes([128]*9) and items[1]==items[10]==items[11]==items[15]==items[16]==1
  assert word('hero_selected_item')==0 and word('hero_basic_level')==2
  if kind in ('panel','west','north'):
   assert w[:len(pw)]==pw and a['episodes'][:-1]==pa['episodes'][:-1] and a['release_write_frame'] is None
   assert word('room_id')==(0x16e if kind=='north'else 0x16d)
   if kind=='panel':assert r['room_cleared']
   else:
    room=0x16e if kind=='north'else 0x16d
    assert r['contact_route_passed'] and not r['contact_state_writes'] and r['contact_room']==r['contact_destination']==room
    assert save[0x50+(room&255)]&4 and save[0x50+(room&255)]&(0x20 if kind=='north'else 0x40)
  elif kind=='release':
   release=f;fixed=w;assert r['passed'] and a['closed_before_room']==0x15e and word('room_id')==0x16e and word('hero_hurt')==0
   assert w==pw+[(f,sy['hero_hurt'],b'\0\0')]
  else:
   assert word('room_id')==0x15e and r['room_cleared'] and w==fixed and all(t<=release for t,_,_ in w)
   assert r['unassisted_extension'] and not r['new_assistance_writes'] and not r['primary_state_imports'] and r['guard_release_frame']==release and r['extension_guard_checks_through_frame']==f
   combat=r['first_intermediate_combat'];assert combat['room']==0x15e and combat['frame']>release and combat['health']>0 and combat['hurt']<=128 and combat['actors']==[dict(slot=0,kind=0x7b,hp=60)]
   assert word('hero_hurt')<=128 and word('hero_attack')==6 and not any(actors[i*48]==0x7b and actors[i*48+24]for i in range(16))
   assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0 and not r['stack_only_difference_windows']
   events=load(p/'events.json');hp=[e for e in events if 'health'in e];damage=[dict(frame=b['frame'],room=b['room'],before=a['health'],after=b['health'])for a,b in zip(hp,hp[1:])if b['health']<a['health']]
   assert not any(e.get('room') in (0x11e,0x14c)for e in events);giant_report=r
  stages.append(dict(trace=p.relative_to(ROOT).as_posix(),kind=kind,frames=f,room=word('room_id'),health=word('hero_health'),magic=word('hero_magic'),gold=word('hero_gold'),keys=word('hero_keys'),whole_ram_png_exact=True))
  read(p/'controls.json');read(p/'assistance.json');previous,pc,pa,pw=p,c,a,w
 sms=data('sms_vram',16384);vram=read(previous/f'vram_{pc["frames"]:05d}.bin');regs=read(previous/f'vdp_regs_{pc["frames"]:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
 for n in range(128):
  at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
 for n in range(9):
  tile,off=original[0x1edc+n*2:0x1ede+n*2];assert sms[0x3d00+off:0x3d02+off]==bytes([tile,0x59])
 result=dict(passed=True,version=309,md_sha256=digest,production_rom_unchanged=True,current_campaign_trace=stages[-1]['trace'],campaign_frames=pc['frames'],stages=stages,cold_palace_giant_defeated=True,guard_release_frame=release,first_giant_combat=combat,observed_health_drops=damage,full_ram_prediction_windows=giant_report['full_ram_prediction_matches'],physical_hud_words_exact=128,source_crystal_markers_exact=9,primary_state_imports=0,full_game_validated=False,evidence=refs,limits=['Actual cold campaign with nine crystals and owned Balloon. Approach guard is removed before15E;no later writes during the giant fight or antechamber walk. Natural floor/projectile cooldowns below129 are allowed and recorded.','Guardian11E,real GoldenAxe2 and final14C remain pending. This does not prove whole-source RNG,timing,saves,optional content or hardware.'])
 (ROOT/'analysis/cold_palace_giant_v0309_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('Cold palace giant verified without boss assistance')
if __name__=='__main__':main()
