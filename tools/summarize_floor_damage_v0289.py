"""Bind source-like dangerous-floor damage, collision interaction and v289 D1 proof."""
import json,re,subprocess
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha

def main():
 refs={}
 def read(n):
  b=evidence(ROOT/n);refs[n]=sha(b);return b
 def load(n):return json.loads(read(n))
 rom=read('gaw-megadrive.bin');digest=sha(rom);original=read('input/original.sms');game=load('analysis/floor_damage_v0289_game_report.json');assert game['passed'] and game['md_sha256']==digest and len(game['cases'])==70
 for region in ['auto','pal']:
  prefix=f'validation/floor-damage-v0289-05/{region}-';sms=load(prefix+'sms/observations.json');md=load(prefix+'md/observations.json');assert sms==md and len(sms)==6446
  rows={(r['case'],r['offset']):r['values'] for r in sms}
  for i,case in enumerate(game['cases']):
   if case['contact'] and not case.get('reflect') and not case['hurt']:
    assert rows[i,0][0]==24-max(2,9-(case['armor']-1)*4)-(4 if case['terrain']==4 else 0)
    assert rows[i,0][7]==104<<8
   if not case['contact'] and case['hurt']==0:
    assert rows[i,0][0]==max(0,case['hp']-4) and rows[i,0][1]==47 and rows[i,0][7]==96<<8
    if case['hp']==24:
     assert [rows[i,f][0] for f in [0,48,96]]==[20,16,12]
   if not case['contact'] and case['hurt']==129:
    assert all(rows[i,f][0]==case['hp'] and rows[i,f][1]==129 for f in range(case['span']))
  reflected=load(prefix+'sms/reflections.json');assert reflected==load(prefix+'md/reflections.json') and len(reflected)==2
  assert [r['hero_health'] for r in reflected]==[24,20] and all(r['velocity']==65152 and not r['flags']&2 for r in reflected)
 terrain=load('analysis/terrain_walk_v0289_game_report.json');rope=load('analysis/rope_motion_v0289_game_report.json');assert terrain['passed'] and rope['passed'] and terrain['md_sha256']==rope['md_sha256']==digest
 stages=[]
 for name in ['md-v0289-d1-entry01','md-auto-v0289-axe01','md-auto-v0289-d1-boss01','md-auto-v0289-d1-exit01']:
  route='entry' in name;base='validation/'+('natural-dungeon-route/' if route else 'natural-dungeon-combat/')+name;r=load(base+('/route_report.json' if route else '/report.json'));c=load(base+'/capture.json');proof=load(base+'-fixed-replay/replay_report.json')
  assert r['rom_sha256']==c['rom_sha256']==proof['rom_sha256']==digest and proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not c['test_ram_writes'] and c['sram_input'] is None
  assert r['failure'] is None and not r.get('deaths',0)
  stages.append(dict(trace=base,frames=c['frames'],state=r['last_state'],full_ram_png_cold_replay=True))
 end=stages[-1];assert end['state']['first_gem']==end['state']['completed_dungeon_progress']==128 and end['state']['health']==end['state']['max_health']==32 and end['state']['room']==0xb9 and end['state']['selected']==end['state']['weapon']==1
 stack=load('validation/stack-v0289-d1-all/stack_report.json');assert stack['md_sha256']==digest and stack['all_instructions'] and not stack['invalid_heap_examples'] and not stack['ram_injections'];minimum=min(v['sp'] for v in stack['instruction_minima']);heap=stack['heap_changes'][-1]['end']+2;assert minimum>=heap
 for stem,ext in [('ram','bin'),('frame','png')]:assert read(f"validation/stack-v0289-d1-all/{stem}_{end['frames']:05d}.{ext}")==read(end['trace']+f"/{stem}_{end['frames']:05d}.{ext}")
 sy={m[2].split('.lto_priv.')[0]:int(m[1],16) for line in read('megadrive/out/release/symbol.txt').decode().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))};address=sy['world_walk_tables'];assert rom[address:address+204]==original[0x33db:0x34a7]
 template=read('validation/sms-shield-detail/ram_03740.bin')[0x780:0x7b0];assert len(template)==48
 checksum=sum(int.from_bytes(rom[p:p+2],'big') for p in range(0x200,len(rom),2))&65535;assert checksum==int.from_bytes(rom[0x18e:0x190],'big')
 baseline=subprocess.check_output(['git','show','91033eb9e4994882f799c5e83d65f1daede3f2ff:megadrive/src/main.c'],cwd=ROOT).decode();new=read('megadrive/src/main.c').decode()
 expected=baseline.replace('    bool bell_action=FALSE;','    bool bell_action=FALSE;\r\n    u16 terrain_damage=0;')
 needle='    if(contact>=0 && damage && !(hero_state==1 && reflect_world_actor(contact,hero_direction,hero_shield_level)))'
 expected=expected.replace(needle,'    /* 2EB6: floor damage is added after reflection, before the common tail.\r\n     * Unlike contact damage it causes no knockback and ignores armor. */\r\n    if(hero_terrain_context==4 && !hero_hurt && hero_state!=9 && hero_health) terrain_damage=4;\r\n'+needle)
 expected=expected.replace('        hurt_hero(contact,cache,damage);','        hurt_hero(contact,cache,damage+terrain_damage);terrain_damage=0;').replace('    integrate_hero();\r\n    if(hero_hurt','    if(terrain_damage) { hero_hurt=48;sound_effect_main(0x91); }\r\n    integrate_hero();\r\n    if(hero_hurt',1)
 expected=expected.replace('    tick_world_spell(sms_vram+0x3800,','    /* 2753/27CF applies the pending damage after movement/flash counters. */\r\n    if(terrain_damage) hero_health=terrain_damage>=hero_health?0:hero_health-terrain_damage;\r\n    tick_world_spell(sms_vram+0x3800,',1);assert expected==new
 result=dict(passed=True,md_sha256=digest,version=289,bytes=len(rom),checksum=f'{checksum:04X}',damage_cases=140,damage_frames=12892,fields=game['fields'],protection_interval_frames=48,terrain_damage=4,body_contact_and_reflection_active=True,contact_template_sha256=sha(template),contact_template_hex=template.hex(),movement_regression_cases=96,rope_motion_regression_frames=64,natural_d1=stages,stack=dict(frames=end['frames'],minimum_sp=minimum,heap_boundary=heap,observed_margin_bytes=minimum-heap,heap_valid=True),main_change_scoped_to_terrain_damage=True,full_game_validated=False,evidence=refs,limits=['Damage cases are explicit RAM fixtures with shared terrain, hero/equipment/derived defense, actor and collision-clock initial conditions. They compare the real original and native loops, not a natural hazardous-terrain route.','Earlier templates froze actors and suppressed contact; final trial05 asserts that body impact and shield reflection really occur. Derived defense is synchronized before collision, rather than inherited from the previous fixture. Earlier failed trials are retained.','Movement, protection, HP and death-phase states match in the tested cases; entire framebuffer, HUD timing, SFX waveform and hardware parity are not claimed.','D1 is completed naturally on v289; later dungeons and natural hazardous terrain remain to extend on this build. Historical v287 D2/D3 proofs, original RNG/R/IRQ stream and global timing do not become v289 full-campaign proofs.'])
 (ROOT/'analysis/floor_damage_v0289_report.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k in ['passed','md_sha256','checksum','stack','damage_cases','damage_frames']})
if __name__=='__main__':main()
