"""Audit D7 preparation and ordinary-damage intermediate combat checkpoints."""
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
 prior=load('analysis/d7_supplies_v0306_report.json');assert prior['passed'] and prior['six_crystals_preserved']
 digest=sha(read('versions/v0306-3a12380b/gaw-megadrive-v0306.bin'));assert digest==prior['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');read('megadrive/out/release/symbol.txt')
 index=load('validation/v0306-d7-progress-sources/source_index.json')
 for name,h in index.items():
  assert sha(read('validation/v0306-d7-progress-sources/'+name.split('/')[-1]))==h
  if name!='tools/unassisted_dungeon_continuation.py':assert sha((ROOT/name).read_bytes())==h
 variants=load('validation/v0306-d7-progress-sources/unassisted_source_variants.json')
 for h,name in variants.items():assert sha(read(name))==h
 assert sha((ROOT/'tools/unassisted_dungeon_continuation.py').read_bytes()) in variants
 original=read('input/original.sms');assert sha(original)=='852e068e331dbfb01b9c38a62eecf81ce5b9f0f1bd10fff497117bd885c716c9'
 assert original[0x3234e+0x1b8*8]==0x78 and original[0x320ea+(0x78-0x20)*4:0x320ee+(0x78-0x20)*4]==bytes([30,12,4,32])
 selection=load('analysis/d7_midboss_v0306_selection.json');assert selection['combat_traces']
 specs=[('md-auto-v0306-d7-'+n,k) for n,k in [('key03','key'),('earth1b9-01','earth'),('earth1b9-02','earth'),('guard-release01','close'),('contact1b9-01','contact')]]+[(n,'combat') for n in selection['combat_traces']]
 prev=prior['current_campaign_trace'];pc=load(prev+'/capture.json');_,previous_writes=recording(ROOT/prev,pc)
 stages=[];closed_writes=None;release=None;contact=None;first_damage=None;predictions=0;final_raw=None;final_report=None;magic=[]
 for name,kind in specs:
  root='validation/natural-dungeon-combat/'+name;c=load(root+'/capture.json');r=load(root+'/report.json');frame=c['frames'];proof=root+f'-assisted-fixed-replay-{frame}';p=load(proof+'/replay_report.json')
  assert c['rom_sha256']==r['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None
  assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
  assert r['prefix_end']==pc['frames'] and r['recorded_new_game_prefix']==prev.split('/')[-1] and frame>pc['frames']
  assert not r.get('deaths',0) and not r.get('rom_modifications',False) and not r.get('sram_checkpoint_injection',False)
  assert r['failure'] is None or kind=='combat' and r['failure']=='frame_limit'
  for filename,h in p['evidence'].items():assert sha(read(root+'/'+filename))==h
  for stem,ext in [('ram','bin'),('frame','png')]:assert read(root+f'/{stem}_{frame:05d}.{ext}')==read(proof+f'/{stem}_{frame:05d}.{ext}')
  raw=read(root+f'/ram_{frame:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  a,writes=recording(ROOT/root,c);read(root+'/assistance.json');assert all(addr==sy['hero_hurt'] for _,addr,_ in writes)
  assert word('game_state')==12 and word('hero_health')>0 and word('hero_max_health')==80
  assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*6+[0]*3)
  items=data('hero_items',17);assert items[4:6]==bytes([1,1]) and items[10] and items[12:15]==bytes([1,1,1]) and not items[16]
  if kind=='key':assert r['new_key_verified'] and word('hero_keys')==2 and word('hero_health')==80
  if kind=='earth':
   assert r['earth_route_passed'] and r['earth_cell_cleared'] and r['earth_action_only_requested'] and r['earth_state_writes']==0
   cost=r['earth_before']['magic']-r['earth_opened']['magic'];assert cost==8;magic.append(cost)
  if kind=='close':
   release=r['guard_release_frame'];assert r['passed'] and a['approach_closed_early'] and a['closed_before_room']==0x1b8
   assert writes==previous_writes+[(release,sy['hero_hurt'],b'\x00\x00')] and word('hero_hurt')==0 and word('room_id')==0x1b9
   assert release==frame and word('hero_health')==80 and word('hero_magic')==56;closed_writes=writes
  elif closed_writes is not None:
   assert writes==closed_writes and not any(f>release for f,_,_ in writes)
   assert r['unassisted_extension'] and r['new_assistance_writes']==0 and r['extension_guard_checks_through_frame']==frame
   assert r['unassisted_controller_sha256'] in variants and word('hero_hurt')<=128
   if first_damage is None and r.get('first_extension_damage'):first_damage=r['first_extension_damage']
   if kind=='contact':
    contact=r['first_intermediate_combat'];assert r['contact_route_passed'] and contact['room']==0x1b8 and contact['health']==80 and contact['hurt']==0
    assert contact['actors']==[dict(slot=0,kind=0x78,hp=30)] and release<contact['frame']
   if kind=='combat':
    if r.get('terminal_recapture'):
     original_root=r['terminal_recapture_source'];assert sha(read(original_root+'/report.json'))==r['terminal_recapture_source_report_sha256']
     assert load(original_root+'/controls.json')==load(root+'/controls.json')
     for name,h in r['terminal_recapture_original_evidence'].items():
      assert sha(read(original_root+'/'+name))==h and read(root+'/'+name)==read(original_root+'/'+name)
     assert r['terminal_recapture_original_checkpoint_count']==18
     assert sha(read('validation/v0306-d7-progress-sources/terminal_recapture.py'))==r['terminal_recapture_driver_sha256']
    assert r['primary_state_imports']==0 and r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows'] and r['stack_only_difference_windows']==0
    assert r['full_ram_prediction_matches']>0;predictions+=r['full_ram_prediction_matches']
  stages.append(dict(trace=root,kind=kind,frames=frame,room=word('room_id'),health=word('hero_health'),keys=word('hero_keys'),magic=word('hero_magic'),whole_ram_png_exact=True))
  prev,pc,previous_writes=root,c,writes;final_raw,final_report=raw,r
 assert magic==[8,8] and contact is not None
 actors=bytes(final_raw[(sy['world_actor_state']+i)^1] for i in range(768));remaining=[actors[i*48+24] for i in range(8) if actors[i*48]==0x78 and actors[i*48+24]]
 won=bool(final_report['room_cleared']);assert not won or not remaining
 read('tools/summarize_d7_midboss_v0306.py')
 result=dict(passed=True,version=306,md_sha256=digest,production_rom_unchanged=True,stages=stages,current_campaign_trace=prev,campaign_frames=pc['frames'],intermediate_defeated=won,remaining_intermediate_hp=remaining,intermediate_assistance=False,guard_release_frame=release,first_intermediate_combat=contact,first_extension_damage=first_damage,full_ram_prediction_windows=predictions,earth_magic_spent=sum(magic),six_crystals_preserved=True,ship_acquired=False,seventh_crystal_obtained=False,full_game_validated=False,evidence=refs,limits=['Approach assistance is declared; all subsequent stages retain exactly its final write list. The intermediate fight has ordinary damage. No game state or SRAM is imported.','Cold RAM/PNG equality proves checkpoint reproducibility, not whole-source RNG, audiovisual fidelity, ending, saves or hardware behavior.','The every-instruction stack measurement remains the previous D6 checkpoint at162574 frames; no extended stack claim.'])
 (ROOT/'analysis/d7_midboss_v0306_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('D7 intermediate checkpoints verified; defeated=',won,'predictions=',predictions)
if __name__=='__main__':main()
