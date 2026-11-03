"""Audit real NPC save,full replay including SRAM,and ordinary Continue."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols

def main():
 refs={}
 def read(p):
  raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
 def load(p):return json.loads(read(p))
 r=load(ROOT/'analysis/game_written_save_v0309_report.json');assert r['passed'] and r['game_written_save'] and not r['synthetic_sram_fixture']
 digest=sha((ROOT/'gaw-megadrive.bin').read_bytes());assert r['rom_sha256']==digest
 indexes={}
 for label in ['04','04b']:
  p=ROOT/('validation/v0309-game-written-save'+label+'-sources');index=load(p/'source_index.json');indexes[label]=index
  for name,h in index.items():assert sha(read(p/name.split('/')[-1]))==h
 assert r['driver_sha256']==indexes['04b']['tools/validate_game_written_save.py']
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
 def reader(raw):
  data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k))
  return data,lambda n:int.from_bytes(data(n,2),'big')
 source=ROOT/'validation'/r['source_trace'];sc=load(source/'capture.json');sr=load(source/'report.json');sa,sw=recording(source,sc)
 assert sr['passed'] and sr['payload_source_ram_exact'] and sr['game_written_save'] and not sr['new_assistance_writes'] and not sr['primary_state_imports'] and sc['sram_input'] is None and sc['rom_sha256']==digest
 assert sr['driver_sha256']==indexes['04']['tools/natural_save_service.py'] and sr['save_written_frame']<sr['complete_frame']<sc['frames']
 parent=ROOT/'validation'/sr['source_prefix'];pc=load(parent/'capture.json');pr=load(parent/'route_report.json');pa,pw=recording(parent,pc)
 assert sr['prefix_end']==pc['frames'] and pr['reached_entrance'] and pr['failure'] is None and pr['required_chop_verified'] and pr['house_outside']==0xfa and pr['house_target']==0x6f and pc['sram_input'] is None
 assert sw==pw and sa==pa and all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81')for _,addr,value in sw)
 pp=parent.with_name(parent.name+'-assisted-fixed-replay-'+str(pc['frames']));proof=load(pp/'replay_report.json');assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads']
 for n,h in proof['evidence'].items():assert sha(read(parent/n))==h
 for stem,ext in [('ram','bin'),('frame','png')]:assert read(parent/f'{stem}_{pc["frames"]:05d}.{ext}')==read(pp/f'{stem}_{pc["frames"]:05d}.{ext}')
 controls=load(source/'controls.json');previous=load(parent/'controls.json');assert controls[:len(previous)]==previous and all(v['frame']>pc['frames']for v in controls[len(previous):])
 events=load(source/'events.json');assert sum(e['phase']==3 for e in events)==1 and any(e['phase']==0 and e['frame']>sr['save_written_frame']for e in events)
 payload=read(source/'serialized-payload.bin');sram=ROOT/sr['sram_file'];raw_sram=read(sram);logical=raw_sram[1::2].ljust(8192,b'\xff')
 assert len(payload)==592 and sha(payload)==sr['serialized_payload_sha256'] and sha(raw_sram)==sr['sram_sha256']==r['source_sram_sha256'] and logical[0x400:0x650]==payload and logical[0x30]==1
 sf=sc['frames'];sd,word=reader(read(source/f'ram_{sf:05d}.bin'));assert word('room_id')==0x6f and word('game_state')==12 and word('save_service_phase')==0 and not word('house_dialogue_active')
 assert word('hero_health')==payload[0x29]==82 and word('hero_magic')==payload[0x2b]==64 and sd('game_save_state',592)[0x1f:0x28]==bytes([128]*9)
 read(source/f'frame_{sf:05d}.png')
 fixed=ROOT/r['fixed_replay_trace'];fc=load(fixed/'capture.json');fr=load(fixed/'replay_report.json')
 assert fr['passed'] and fr['feedback_reads'] is False and fr['whole_ram_bytes']==65536 and fr['final_png_exact'] and fr['raw_sram_exact'] and fc['sram_input'] is None and fc['frames']==sf and fc['test_ram_writes']==sc['test_ram_writes']
 assert read(fixed/'replayed.srm')==raw_sram
 for stem,ext in [('ram','bin'),('frame','png')]:assert read(source/f'{stem}_{sf:05d}.{ext}')==read(fixed/f'{stem}_{sf:05d}.{ext}')
 reload=ROOT/r['reload_trace'];rc=load(reload/'capture.json');rr=load(reload/'report.json');assert rr==r and rc['sram_input']==str(sram) and rc['test_ram_writes']==[] and rc['rom_sha256']==digest
 assert r['reload_primary_sram_imports']==1 and not r['reload_ram_writes'] and not r['reload_actor_records_cleared'] and r['checkpoint_room']==0xfa and r['reload_ready_frame']<r['movement_verified_frame']<rc['frames']
 initial=read(reload/f'ram_{r["reload_ready_frame"]+1:05d}.bin');id,iw=reader(initial)
 for name,offset in r['restored_source_fields'].items():assert iw(name)==payload[offset]
 assert id('hero_items',17)==payload[0x30:0x41] and id('game_save_state',592)[0x1f:0x28]==payload[0x1f:0x28]==bytes([128]*9)
 final=read(reload/f'ram_{rc["frames"]:05d}.bin');fd,fw=reader(final);assert fw('room_id')==0xfa and fw('game_state')==12 and fw('hero_health')==82 and fw('hero_hurt')<=128
 pe=load(parent/'events.json');cut=next(e for e in pe if e.get('reason')=='required_chop_verified');cf=cut['frame']+1;cd,cw=reader(read(parent/f'ram_{cf:05d}.bin'))
 assert cw('room_id')==0xfa and cd('scratch',4096)[0x85d]==fd('scratch',4096)[0x85d]==4 and payload[0x14a]&1 and fd('game_save_state',592)[0x14a]&1
 for name in ['controls.json','events.json',f'frame_{rc["frames"]:05d}.png',f'vram_{rc["frames"]:05d}.bin',f'vdp_regs_{rc["frames"]:05d}.bin']:read(reload/name)
 result=dict(passed=True,version=309,md_sha256=digest,game_written_save=True,primary_save_trace=r['source_trace'],saved_frame=sr['save_written_frame'],service_closed_frame=sr['complete_frame'],save_checkpoint_frame=sf,serialized_payload_bytes=592,raw_sram_bytes=len(raw_sram),source_sram_sha256=sha(raw_sram),source_no_initial_sram=True,new_test_resource_actor_progression_writes=0,save_full_ram_png_sram_exact=True,reload_trace=r['reload_trace'],reload_ready_frame=r['reload_ready_frame'],movement_verified_frame=r['movement_verified_frame'],reload_checkpoint=0xfa,reload_health=fw('hero_health'),reload_magic=fw('hero_magic'),saved_stats={name:payload[offset]for name,offset in r['restored_source_fields'].items()},restored_stats={name:iw(name)for name in r['restored_source_fields']},reload_primary_game_written_sram_imports=1,reload_ram_writes=0,tree_cut_persists=True,tree_room=0xfa,tree_cell=0x5d,tree_saved_and_restored_metatile=4,physical_hud_words_exact=r['physical_hud_words_exact'],source_crystal_markers_exact=r['source_crystal_markers_exact'],full_game_validated=False,evidence=refs,limits=['Separate actual nine-crystal New Game branch through FA/6F;ordinary owned axe cuts the tree and normal Save writes slot0. No initial fixture and no new RAM injections.','Reload uses the exact game-written SRAM as intended by Continue;it is explicitly not a cold New Game campaign. Source-layout payload,items,stats,nine gems,persistent cut,actual movement and HUD are checked without clearing actors.','Slot refusal/cancel/other-slot combinations,global SMS RNG/phase and hardware remain separate requirements.'])
 (ROOT/'analysis/game_written_save_audit_v0309_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('Real game-written save,Continue and persistent tree independently audited')
if __name__=='__main__':main()
