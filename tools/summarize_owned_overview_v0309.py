"""Audit natural owned-Balloon use, cold replay and physical map/HUD restoration."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

def main():
 refs={}
 def read(p):
  raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
 def load(p):return json.loads(read(p))
 prior=load(ROOT/'analysis/d9_campaign_v0309_report.json');assert prior['passed'] and prior['ninth_crystal_and_exterior_return']
 p=ROOT/'validation/natural-dungeon-combat/md-auto-v0309-owned-overview01';r=load(p/'report.json');c=load(p/'capture.json');f=c['frames']
 assert r['passed'] and r['failure'] is None and r['source_trace']==prior['current_campaign_trace'].removeprefix('validation/')
 assert r['rom_sha256']==c['rom_sha256']==prior['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
 assert c['sram_input'] is None and not r['new_assistance_writes'] and not r['primary_state_imports']
 assert r['modal_resources_unchanged'] and r['background_5120_map_1280_cells_160_metadata_restored'] and r['selected_zero_on_return'] and r['ordinary_axe_reselection']
 proofp=p.with_name(p.name+'-assisted-fixed-replay-'+str(f));proof=load(proofp/'replay_report.json')
 assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads']
 for n,h in proof['evidence'].items():assert sha(read(p/n))==h
 for stem,ext in [('ram','bin'),('frame','png')]:assert read(p/f'{stem}_{f:05d}.{ext}')==read(proofp/f'{stem}_{f:05d}.{ext}')
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');raw=read(p/f'ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
 assert word('game_state')==12 and word('hero_state')==1 and word('hero_health')>0 and not word('world_overview_active') and not word('overview_pacing_error') and not word('sound_unhandled_command')
 assert word('hero_selected_item')==1 and data('hero_items',17)[11]==1 and data('game_save_state',592)[0x1f:0x28]==bytes([128]*9)
 sms=data('sms_vram',16384);vram=read(p/f'vram_{f:05d}.bin');regs=read(p/f'vdp_regs_{f:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
 for n in range(768):
  at=base+((n//32+2)*width+n%32)*2;assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3800+n*2:0x3802+n*2],'little')),(n,at)
 original=read(ROOT/'input/original.sms')
 for n in range(9):
  tile,off=original[0x1edc+n*2:0x1ede+n*2];assert sms[0x3d00+off:0x3d02+off]==bytes([tile,0x59])
 assert sha(read(p/'overview_driver.py'))==r['driver_sha256'];read(p/'overview_rooms.json');read(p/'events.json')
 result=dict(passed=True,version=309,md_sha256=r['rom_sha256'],production_rom_unchanged=True,current_campaign_trace=p.relative_to(ROOT).as_posix(),campaign_frames=f,natural_owned_overview_verified=True,overview_start=r['overview_start'],overview_ready=r['overview_ready'],overview_return=r['overview_return'],physical_room_and_hud_words_exact=768,source_crystal_markers_exact=9,primary_state_imports=0,new_assistance_writes=0,whole_ram_png_exact=True,full_game_validated=False,evidence=refs,limits=['Actual owned Balloon is selected,activated and closed using ordinary input after the ninth exterior return. No new guard,resource,actor,progression or SRAM writes.','Modal shadow background/cells/metadata and physical room/HUD restoration are checked. This is not whole-source timing,RNG,ending,save or hardware proof.'])
 (ROOT/'analysis/owned_overview_v0309_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('Owned Balloon overview and physical room/HUD return verified')
if __name__=='__main__':main()
