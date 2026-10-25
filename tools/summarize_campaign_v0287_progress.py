"""Bind v287 D2 victory/exit and the original cartridge's real rope deployment."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols

def main():
 refs={}
 def read(name):
  b=evidence(ROOT/name);refs[name]=sha(b);return b
 def load(name):return json.loads(read(name))
 digest=sha((ROOT/'gaw-megadrive.bin').read_bytes());stages=[]
 for name in ['key01','escape01','escape02','exit01']:
  suffix='assisted-key01' if name=='key01' else name;base='validation/natural-dungeon-combat/md-auto-v0287-d2-'+suffix
  r=load(base+'/report.json');c=load(base+'/capture.json');a=load(base+'/assistance.json');proof=load(base+f"-assisted-fixed-replay-{c['frames']}/replay_report.json")
  assert r['rom_sha256']==c['rom_sha256']==proof['rom_sha256']==digest and proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact']
  assert not r['deaths'] and r['failure'] in [None,'frame_limit'] and a['boss_assistance'] is False
  assert c['sram_input'] is None and not a['health_refills']
  if a['release_write_frame']:
   assert max(w['frame'] for w in a['writes'])==a['release_write_frame']<a['first_boss_combat']['frame'] and a['first_boss_combat']['hurt']==0 and a['first_boss_damage'] is None
  if name in ['escape01','escape02']:assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows'] and not r['primary_state_imports']
  if name in ['escape02','exit01']:assert r['room_cleared'] and r['failure'] is None
  stages.append(dict(trace=base,frames=c['frames'],state=r['last_state'],failure=r['failure'],release_frame=a['release_write_frame'],first_boss_combat=a['first_boss_combat'],boss_damage=a['first_boss_damage'],full_ram_png_cold_replay=True))
 boss=load('validation/natural-dungeon-combat/md-auto-v0287-d2-escape02/report.json');assert boss['last_state']['progress']==128 and boss['last_state']['max_health']==48
 final=stages[-1];assert final['state']['room']==0xd6 and final['state']['dungeon']==0 and final['state']['health']==final['state']['max_health']==48 and final['state']['completed_dungeon_progress']==128
 folder=final['trace'];raw=read(folder+f"/ram_{final['frames']:05d}.bin");sy=symbols(ROOT/'megadrive/out/release/symbol.txt');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
 source=read('validation/natural-dungeon-combat/sms-auto-v0286-d2-assisted-exit01/ram_53907.bin')
 assert data('game_save_state',592)[0x50:0x150]==source[0x100:0x200]
 assert data('sms_vram',16384)[0x3800:0x3d00]==source[0x1600:0x1b00] and data('hero_items',17)==source[0xe0:0xf1]
 stack=load('validation/stack-v0287-d2-all/stack_report.json');assert stack['md_sha256']==digest and stack['all_instructions'] and not stack['invalid_heap_examples']
 assert read('validation/stack-v0287-d2-all/'+f"ram_{final['frames']:05d}.bin")==raw
 assert read('validation/stack-v0287-d2-all/'+f"frame_{final['frames']:05d}.png")==read(folder+f"/frame_{final['frames']:05d}.png")
 minimum=min(v['sp'] for v in stack['instruction_minima']);heap=stack['heap_changes'][-1]['end']+2;assert minimum>=heap
 source_exit='validation/natural-dungeon-combat/sms-auto-v0287-source-d3-exit02';r=load(source_exit+'/report.json');c=load(source_exit+'/capture.json');proof=load(source_exit+f"-assisted-fixed-replay-{c['frames']}/replay_report.json")
 assert r['full_dungeon_cleared'] and r['last_state']['completed_dungeon_progress']==128 and r['last_state']['max_health']==56 and not r['deaths'] and proof['passed'] and proof['whole_ram_bytes']==8192
 rope='validation/natural-rope-route/sms-v0287-rope41-04';r=load(rope+'/report.json');proof=load(rope+'-assisted-fixed-replay-69953/replay_report.json');a=load(rope+'/assistance.json')
 assert r['passed'] and r['failure'] is None and not r['new_assistance_writes'] and proof['passed'] and proof['whole_ram_bytes']==8192 and proof['final_png_exact']
 assert max(w['frame'] for w in a['writes'])==a['release_write_frame']<r['rope_activation_frame']
 assert len(r['rows'])==10 and [v['offset'] for v in r['rows']]==list(range(600,23,-64)) and r['last_state']['y']==72
 newer='validation/natural-rope-route/sms-v0287-rope41-05';new=load(newer+'/report.json');assert new['passed'] and new['driver_sha256']==sha(read('tools/natural_rope_route.py'))
 for filename in ['controls.json','ram_69953.bin','frame_69953.png']:assert read(newer+'/'+filename)==read(rope+'/'+filename),filename
 assert read(newer+'/route_driver.py')==read('tools/natural_rope_route.py')
 diagnostic=load(rope+'/activation_differences.json');assert all(i>=160 for i in diagnostic['other_cell_differences'])
 failures=[]
 for name in ['cautious01','nav01']:
  base='validation/natural-dungeon-combat/md-auto-v0287-d2-'+name;rfailed=load(base+'/report.json');assert rfailed['deaths']==1 and not rfailed['room_cleared'];failures.append(dict(trace=base,state=rfailed['last_state'],failure=rfailed['failure']))
 result=dict(passed=True,md_sha256=digest,version=287,new_rom_build=False,native_d2_stages=stages,source_d2_exit_comparison=dict(flags_exact_bytes=256,map_exact_bytes=1280,inventory_exact_bytes=17),stack=dict(minimum_sp=minimum,heap_boundary=heap,observed_margin_bytes=minimum-heap,heap_valid=True,frames=final['frames']),source_d3_exit=dict(trace=source_exit,max_health=56,full_ram_png_cold_replay=True),source_rope=dict(trace=rope,rows=10,activation_frame=69833,completed_frame=69853,final_frame=69953,full_ram_png_cold_replay=True,current_tool_same_controls_ram_png=True,extension_unassisted=True),retained_native_d2_defeats=failures,full_game_validated=False,evidence=refs,limits=['Approach uses only the authorized hurt-counter guard. Exact release frames are in each manifest. No boss or exit invulnerability, HP refill, SRAM or primary state import.','Escape01 stopped at its diagnostic budget while alive; escape02 cold-replays it before continuing. Their 375+70 eight-frame prediction windows match all RAM; separate official replay gates are authoritative.','The real source rope route includes earlier approach assistance, so the complete campaign is not labelled unassisted. The outdoor extension receives no new writes.','Source natural rope validation covers the changed terrain column, work bytes and ten successive map rows. Three bytes beyond visible160 cells are live source scratch aliases; an earlier overly broad comparison was retained as a diagnostic failure.','Cross-system comparison covers flags, item inventory and map, not remaining keys/gold, encounters or the entire save record.',
 'No new native D3 boss victory, v287 natural rope use, full PAL campaign, exact RNG/R/IRQ stream, global timing, waveform or hardware parity is claimed.'])
 (ROOT/'analysis/campaign_v0287_progress_report.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k in ['passed','md_sha256','stack','source_d2_exit_comparison']})
if __name__=='__main__':main()
