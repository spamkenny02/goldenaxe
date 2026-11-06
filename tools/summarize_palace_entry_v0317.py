"""Audit the real nine-crystal palace gate and cold entry after owned overview."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording,EPISODE_KEYS
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

def main():
 if not(ROOT/'analysis/owned_overview_v0317_report.json').exists():
  from summarize_owned_overview_v0317 import main as verify_owned_overview
  verify_owned_overview()
 refs={}
 def read(p):
  raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
 def load(p):return json.loads(read(p))
 prior=load(ROOT/'analysis/owned_overview_v0317_report.json');assert prior['passed'] and prior['natural_owned_overview_verified']
 digest=prior['md_sha256'];assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==digest
 source=ROOT/'validation/v0317-after-d9-sources/palace';index={'tools/'+k:v for k,v in load(source/'source_index.json').items()}
 for n,h in index.items():assert sha(read(source/n.split('/')[-1]))==h
 previous=ROOT/prior['current_campaign_trace'];pc=load(previous/'capture.json');pa,pw=recording(previous,pc)
 p=ROOT/'validation/natural-dungeon-route/md-v0317-cold-palace-entry02';c=load(p/'capture.json');r=load(p/'route_report.json');a,w=recording(p,c);f=c['frames']
 assert c['rom_sha256']==r['rom_sha256']==digest and c['sram_input'] is None and r['prefix_end']==pc['frames'] and r['recorded_combat_prefix']==previous.name
 assert r['failure'] is None and r['reached_entrance'] and r['directional_probe_succeeded'] and r['door_index']==10
 assert r['palace_gate_verified'] and not r['palace_new_map_or_resource_writes'] and r['palace_gate_opened']['cells']==[0x30,0x31,0x1f]
 assert r['route_driver_sha256']==index['tools/natural_dungeon_route.py']
 proofp=p.with_name(p.name+'-assisted-fixed-replay-'+str(f));proof=load(proofp/'replay_report.json')
 assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads'] and proof['rom_sha256']==digest
 for n,h in proof['evidence'].items():assert sha(read(p/n))==h
 for stem,ext in [('ram','bin'),('frame','png')]:assert read(p/f'{stem}_{f:05d}.{ext}')==read(proofp/f'{stem}_{f:05d}.{ext}')
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');raw=read(p/f'ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
 assert word('room_id')==0x18d and word('world_dungeon_number')==10 and word('game_state')==12 and word('hero_state')==1 and word('hero_health')>0 and word('hero_max_health')==104 and not word('sound_unhandled_command')
 items=data('hero_items',17);save=data('game_save_state',592);assert save[0x1f:0x28]==bytes([128]*9) and save[0x48] and items[1]==items[10]==items[11]==items[15]==items[16]==1
 assert len(a['episodes'])==14 and a['boss_room']==0x14c and a['activation_after_frame']==pc['frames'] and a['first_boss_entry'] is None
 assert not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance'] and w[:len(pw)]==pw
 assert all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81')for _,addr,value in w)
 for before,after in zip(pa['episodes'],a['episodes'][:-1]):assert all(before[k]==after[k]for k in EPISODE_KEYS)
 sms=data('sms_vram',16384);vram=read(p/f'vram_{f:05d}.bin');regs=read(p/f'vdp_regs_{f:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
 for n in range(128):
  at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
 original=read(ROOT/'input/original.sms')
 for n in range(9):
  tile,off=original[0x1edc+n*2:0x1ede+n*2];assert sms[0x3d00+off:0x3d02+off]==bytes([tile,0x59])
 read(p/'palace_gate_events.json');assert sha(read(p/'palace_world_driver.py'))==index['tools/natural_palace_world_route.py']
 result=dict(passed=True,version=317,md_sha256=digest,production_rom_unchanged=True,current_campaign_trace=p.relative_to(ROOT).as_posix(),campaign_frames=f,real_nine_crystal_gate=True,cold_palace_entered=True,room=word('room_id'),health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),gold=word('hero_gold'),keys=word('hero_keys'),new_approach_episode=14,pending_main_boss_room=0x14c,gate_first=r['palace_gate_first'],gate_opened=r['palace_gate_opened'],whole_ram_png_exact=True,physical_hud_words_exact=128,source_crystal_markers_exact=9,primary_state_imports=0,full_game_validated=False,evidence=refs,limits=['Cold current-ROM campaign follows actual Balloon use. Only declared approach protection resumes after the ninth audited exit;no resource,actor,progression or SRAM imports.','Entry is not palace completion. Guard must be released before15E/7B,11E/7C and14C/6D;real GoldenAxe2 is still needed.','The current route requires the verified ninth-dungeon exit before starting its palace approach.'])
 (ROOT/'analysis/cold_palace_entry_v0317_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('Cold palace18D after real gate verified; no synthetic SRAM')
if __name__=='__main__':main()
