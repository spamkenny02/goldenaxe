"""Audit actual cold-v317 palace portals,Earth casts and remote mechanism."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

SPECS=[('resume01','resume',0x15e),('portal14e05','portal',0x14e),('earth14e01','earth14e',0x119),('earth11a01','earth11a',0x12a),('switch12901','switch',0x12a)]
def main():
 refs={}
 def read(p):
  raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
 def load(p):return json.loads(read(p))
 prior=load(ROOT/'analysis/cold_palace_giant_v0317_report.json');assert prior['passed'] and prior['cold_palace_giant_defeated'] and not prior['primary_state_imports']
 digest=prior['md_sha256'];assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==digest
 source=ROOT/'validation/v0317-palace-sources/inner-tools02';index=load(source/'source_index.json')
 for n,h in index.items():assert sha(read(source/n.split('/')[-1]))==h
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');previous=ROOT/prior['current_campaign_trace'];pc=load(previous/'capture.json');pa,pw=recording(previous,pc)
 stages=[]
 for suffix,kind,room in SPECS:
  p=ROOT/'validation/natural-dungeon-combat'/('md-auto-v0317-cold-palace-'+suffix);c=load(p/'capture.json');r=load(p/'report.json');a,w=recording(p,c);f=c['frames']
  assert c['rom_sha256']==r['rom_sha256']==digest and c['sram_input'] is None and r['failure'] is None and not r['deaths'] and not r['primary_state_imports']
  assert r['prefix_end']==pc['frames'] and r['recorded_new_game_prefix']==previous.name and f>pc['frames']
  proofp=p.with_name(p.name+'-assisted-fixed-replay-'+str(f));proof=load(proofp/'replay_report.json')
  assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads'] and proof['rom_sha256']==digest
  for n,h in proof['evidence'].items():assert sha(read(p/n))==h
  for stem,ext in [('ram','bin'),('frame','png')]:assert read(p/f'{stem}_{f:05d}.{ext}')==read(proofp/f'{stem}_{f:05d}.{ext}')
  assert len(a['episodes'])==15 and a['boss_room']==0x14c and all(a[k] is None for k in ['first_boss_entry','first_boss_combat','first_boss_damage','release_write_frame'])
  assert not a['boss_assistance'] and not a['primary_state_imports'] and not a['health_refills']
  assert all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in w)
  assert w[:len(pw)]==pw
  raw=read(p/f'ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  items=data('hero_items',17);save=data('game_save_state',592);actors=data('world_actor_state',768)
  assert word('room_id')==room and word('game_state')==12 and word('world_dungeon_number')==10 and 0<word('hero_health')<=104 and word('hero_max_health')==104 and not word('sound_unhandled_command')
  assert save[0x1f:0x28]==bytes([128]*9) and items[1]==items[10]==items[11]==items[15]==items[16]==1 and word('hero_basic_level')==2 and word('hero_selected_item')==0
  if kind=='resume':
   assert r['passed'] and r['resumed_after_verified_intermediate'] and r['new_guard_frame']==f and w==pw+[(f,sy['hero_hurt'],b'\0\x81')]
   assert r['driver_sha256']==index['tools/resume_after_intermediate.py']
   old=read(previous/f"ram_{pc['frames']:05d}.bin")
   for symbol,length in [('hero_health',2),('hero_magic',2),('hero_gold',2),('hero_keys',2),('hero_items',17)]:
    assert data(symbol,length)==bytes(old[(sy[symbol]+i)^1] for i in range(length))
  else:
   assert r['driver_sha256']==index['tools/natural_dungeon_combat.py'] and a['episodes'][:-1]==pa['episodes'][:-1]
   if kind=='portal':
    assert r['room_cleared'] and not any(actors[i*48] and (i<8 or actors[i*48+24])for i in range(16))
    assert r['itinerary']==[0x15e,0x15d,0x16d,0x16c,0x14d,0x14e] and 0x14d in r['avoided_portal_rooms'] and 0x16c not in r['avoided_portal_rooms'] and 0x16c in r['deferred_puzzles'] and set(r['rush_rooms'])=={0x16c,0x16d}
   elif kind.startswith('earth'):
    source_room,cell=(0x14e,0x58) if kind=='earth14e' else (0x11a,0x35)
    assert r['earth_route_passed'] and r['earth_passage_traversed'] and r['earth_passage_opened'] and not r['earth_state_writes'] and r['earth_passage_room']==source_room and r['earth_cell']==cell and r['earth_restore_item']==0
    assert r['earth_controller_sha256']==index['tools/natural_earth_passage.py']
   else:
    assert r['contact_route_passed'] and not r['contact_state_writes'] and r['contact_room']==0x129 and r['contact_destination']==r['contact_remote_room']==0x12a and save[0x7a]&4
    assert r['contact_controller_sha256']==index['tools/natural_contact_passage.py']
  stages.append(dict(trace=p.relative_to(ROOT).as_posix(),kind=kind,frames=f,room=room,health=word('hero_health'),magic=word('hero_magic'),gold=word('hero_gold'),keys=word('hero_keys'),whole_ram_png_exact=True))
  read(p/'controls.json');read(p/'assistance.json');previous,pc,pa,pw=p,c,a,w
 sms=data('sms_vram',16384);vram=read(previous/f'vram_{f:05d}.bin');regs=read(previous/f'vdp_regs_{f:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
 for n in range(128):
  at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
 original=read(ROOT/'input/original.sms')
 for n in range(9):
  tile,off=original[0x1edc+n*2:0x1ede+n*2];assert sms[0x3d00+off:0x3d02+off]==bytes([tile,0x59])
 result=dict(passed=True,version=317,md_sha256=digest,production_rom_unchanged=True,current_campaign_trace=stages[-1]['trace'],campaign_frames=f,stages=stages,cold_palace_inner_mechanisms_verified=True,physical_hud_words_exact=128,source_crystal_markers_exact=9,primary_state_imports=0,full_game_validated=False,evidence=refs,limits=['Actual cold campaign after nine crystals and first palace giant. Approach-only hurt guard; no health,inventory,actors,progression or SRAM imports.','Guardian11E,GoldenAxe2 and final14C still pending here. Own-ROM replay does not prove source RNG,timing,saves,optional content or hardware.'])
 (ROOT/'analysis/cold_palace_inner_v0317_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('Cold palace inner mechanisms verified')
if __name__=='__main__':main()
