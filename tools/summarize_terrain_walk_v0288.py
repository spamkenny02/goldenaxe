"""Bind the v288 terrain-selection fix to its compiled bytes and game tests."""
import json,re
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha

def main():
 refs={}
 def read(n):
  b=evidence(ROOT/n);refs[n]=sha(b);return b
 def load(n):return json.loads(read(n))
 rom=read('gaw-megadrive.bin');digest=sha(rom);original=read('input/original.sms');sy={m[2].split('.lto_priv.')[0]:int(m[1],16) for line in read('megadrive/out/release/symbol.txt').decode().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
 address=sy['world_walk_tables'];assert rom[address:address+204]==original[0x33db:0x34a7]
 terrain=load('analysis/terrain_walk_v0288_game_report.json');rope=load('analysis/rope_motion_v0288_game_report.json');assert terrain['passed'] and rope['passed'] and terrain['md_sha256']==rope['md_sha256']==digest
 assert len(terrain['results'])==2 and all(r['cases']==48 and not r['differences'] for r in terrain['results'])
 assert len(rope['cases'])==2 and all(r['frames']==32 and r['rope_step_ticks']==12 for r in rope['cases'])
 stages=[]
 for name in ['md-v0288-d1-entry01','md-auto-v0288-axe01','md-auto-v0288-d1-boss01','md-auto-v0288-d1-exit01']:
  route='entry' in name;base='validation/'+('natural-dungeon-route/' if route else 'natural-dungeon-combat/')+name;r=load(base+('/route_report.json' if route else '/report.json'));c=load(base+'/capture.json');proof=load(base+'-fixed-replay/replay_report.json')
  assert r['rom_sha256']==c['rom_sha256']==proof['rom_sha256']==digest and proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact']
  assert r['failure'] is None and not r.get('deaths',0) and not c['test_ram_writes'] and c['sram_input'] is None
  stages.append(dict(trace=base,frames=c['frames'],state=r['last_state'],full_ram_png_cold_replay=True))
 end=stages[-1];assert end['state']['first_gem']==end['state']['completed_dungeon_progress']==128 and end['state']['max_health']==32 and end['state']['health']>0 and end['state']['room']==0xb9 and end['state']['selected']==1 and end['state']['weapon']==1
 stack=load('validation/stack-v0288-d1-all/stack_report.json');assert stack['md_sha256']==digest and stack['all_instructions'] and not stack['invalid_heap_examples'] and not stack['ram_injections'];minimum=min(r['sp'] for r in stack['instruction_minima']);heap=stack['heap_changes'][-1]['end']+2;assert minimum>=heap
 for stem,ext in [('ram','bin'),('frame','png')]:assert read(f"validation/stack-v0288-d1-all/{stem}_{end['frames']:05d}.{ext}")==read(end['trace']+f"/{stem}_{end['frames']:05d}.{ext}")
 old=read('validation/v0287-d3-build/main.c').decode();new=read('megadrive/src/main.c').decode();decl='extern const u8 world_hero_bitmaps[],world_hero_frames[],world_walk_table[],world_fast_ground_walk[];';old=old.replace(decl,decl+'\r\nextern const u8 world_walk_tables[204];')
 old_selector='    const u8 *walk=hero_terrain_context==3?world_water_walk+(hero_attack_speed?17:0):\r\n        hero_terrain_context==0 && hero_attack_speed?world_fast_ground_walk:world_walk_table;'
 new_selector='    /* 32DE..32F6 selects every terrain row, including the slower rope. */\r\n    const u8 *walk=world_walk_tables+(hero_attack_speed?102:0)+hero_terrain_context*17;'
 assert old.replace(old_selector,new_selector)==new
 checksum=sum(int.from_bytes(rom[p:p+2],'big') for p in range(0x200,len(rom),2))&65535;assert int.from_bytes(rom[0x18e:0x190],'big')==checksum
 result=dict(passed=True,md_sha256=digest,version=288,bytes=len(rom),checksum=f'{checksum:04X}',compiled_table_bytes_exact=204,terrain_rows=12,terrain_movement_cases=96,terrain_movement_frames=3072,rope_motion_frames_exact=64,rope_motion_step_ticks=12,natural_d1=stages,stack=dict(frames=end['frames'],minimum_sp=minimum,heap_boundary=heap,observed_margin_bytes=minimum-heap,heap_valid=True),main_change_scoped_to_table_selection=True,historical_v287_d3_report_sha256=sha(read('analysis/d3_rope_v0287_report.json')),full_game_validated=False,evidence=refs,limits=['Terrain and rope comparisons use explicit map/equipment/hero fixtures, while both real gameplay loops perform classification, selection, movement and rope work. HP is reset for each movement case; hazard-damage parity is not tested.','The first dungeon is completed naturally on v288. D2/D3 and real acquired-rope campaign evidence belong to historical v287 and need extension on the corrected build.','Exact RNG/R/IRQ stream, global title/enemy/transition speed, audio waveform, remaining campaign and hardware parity are not claimed.','An earlier synthetic terrain test accumulated source damage across cases. Environment-damage handling, including original2EB6..2EDA on context4, remains an explicit follow-up; table-selection checks do not prove it.'])
 (ROOT/'analysis/terrain_walk_v0288_report.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k in ['passed','md_sha256','checksum','stack']})
if __name__=='__main__':main()
