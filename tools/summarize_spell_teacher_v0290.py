"""Bind original teacher policies, production UI, portraits and v290 D1 proof."""
import json,re,subprocess
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from audit_item_reward_visuals import sms_pixels,md_pixels
from validate_playable_sprite_limit import symbols

def main():
 refs={}
 def read(n):
  raw=evidence(ROOT/n);refs[n]=sha(raw);return raw
 def load(n):return json.loads(read(n))
 rom=read('gaw-megadrive.bin');digest=sha(rom);source=read('input/original.sms');policy=load('analysis/spell_teacher_policy_report.json');assert policy['passed'] and policy['cases']==3081 and policy['native_c_sha256']==sha(read('megadrive/src/source_spell_teacher.c'))
 standalone=load('analysis/spell_teacher_game_v0290-standalone01_report.json');assert standalone['passed'] and standalone['md_sha256']==digest
 baseline=load('analysis/spell_teacher_game_v0289-baseline_report.json');assert baseline['passed'] and baseline['missing_service_reproduced'] and len(baseline['cases'])==24
 games=[];portraits=[];stack_cases=[]
 for name in ['v0290-01','v0290-decline01','v0290-stack01']:
  game=load('analysis/spell_teacher_game_'+name+'_report.json');assert game['passed'] and not game['missing_service_reproduced'] and game['md_sha256']==digest
  for case in game['cases']:
   assert case['sms']['activation'] and case['md']['activation'] and case['sms']['rows'][-1]['fields']==case['md']['rows'][-1]['fields']
   region=case['region'];label=case['case']['name'];base=f'validation/spell-teacher-game-{name}/';captures={}
   for tag in ['sms','md']:
    folder=base+f'{region}-{label}-{tag}';capture=load(folder+'/capture.json');assert capture['rom_sha256']==(sha(source) if tag=='sms' else digest) and capture['sram_input'] is None;read(folder+'/observations.json');captures[tag]=folder
   if name=='v0290-01':
    a=read(captures['sms']+'/vram_03600.bin');b=read(captures['md']+'/vram_03600.bin');tiles=set()
    for y in range(2,10):
     for x in range(3,11):
      off=0x3800+y*64+x*2;w=int.from_bytes(a[off:off+2],'little');translated=((w>>11)&1)<<13|((w>>12)&1)<<15|((w>>10)&1)<<12|((w>>9)&1)<<11|16+(w&511);p=0xe000+(y+2)*128+x*2;assert int.from_bytes(b[p:p+2],'little')==translated;tiles.add(w&511)
    for tile in tiles:assert sms_pixels(a,tile)==md_pixels(b,tile+16)
    portraits.append(dict(region=region,case=label,words=64,tiles=len(tiles)))
   if name=='v0290-stack01':
    minima=case['md']['stack'];boundary=max(case['md']['heap_boundaries']);minimum=min(v['sp'] for v in minima);assert minimum>=boundary
    for stem,ext in [('ram','bin'),('frame','png')]:assert read(captures['md']+f'/{stem}_05800.{ext}')==read(f'validation/spell-teacher-game-v0290-standalone01/{region}-{label}-md/{stem}_05800.{ext}')
    stack_cases.append(dict(region=region,minimum_sp=minimum,heap_boundary=boundary,observed_margin_bytes=minimum-boundary,whole_ram_png_replay_exact=True))
  if name!='v0290-stack01':games.extend(game['cases'])
 assert len(games)==26 and len(portraits)==24
 d1='validation/natural-dungeon-route/md-v0290-d1-exit01';rebased=load(d1+'/rebase_report.json');capture=load(d1+'/capture.json');proof=load(d1+'-fixed-replay/replay_report.json');assert rebased['passed'] and proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and capture['rom_sha256']==proof['rom_sha256']==digest and not capture['test_ram_writes']
 final=rebased['states'][-1];assert final['room_id']==0xb9 and final['hero_health']==final['hero_max_health']==32 and final['first_crystal']==128 and final['hero_weapon_level']==final['hero_selected_item']==1
 stack=load('validation/stack-v0290-d1-all/stack_report.json');assert stack['md_sha256']==digest and stack['all_instructions'] and not stack['invalid_heap_examples'] and not stack['ram_injections'];minimum=min(v['sp'] for v in stack['instruction_minima']);boundary=stack['heap_changes'][-1]['end']+2;assert minimum>=boundary
 for stem,ext in [('ram','bin'),('frame','png')]:assert read(f"validation/stack-v0290-d1-all/{stem}_{capture['frames']:05d}.{ext}")==read(d1+f"/{stem}_{capture['frames']:05d}.{ext}")
 old=load('analysis/d2_campaign_v0289_report.json');assert old['passed'] and old['version']==289 and old['native_d2_stages'][-1]['last_state']['health']==48
 assets=load('analysis/spell_teacher_assets.json');sy={m[2].split('.lto_priv.')[0]:int(m[1],16) for line in read('megadrive/out/release/symbol.txt').decode().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
 for n,item in enumerate(assets['portraits']):
  data=source[item['start']:item['rle_end']];offset=sy[f'spell_teacher_portrait{n}_rle'];assert rom[offset:offset+len(data)]==data
 texts=b''
 for pc,offset in assets['text_index']:
  start=pc+0x4000;assert offset==len(texts);texts+=source[start:source.index(0,start)+1]
 address=sy['spell_teacher_text'];assert rom[address:address+len(texts)]==texts
 old_main=subprocess.check_output(['git','show','b6f6b05:megadrive/src/main.c'],cwd=ROOT);assert read('megadrive/src/main.c')==old_main.replace(b'#include "healer.inc"',b'#include "healer.inc"\r\n#include "spell_teacher.inc"')
 old_save=subprocess.check_output(['git','show','b6f6b05:megadrive/src/save.inc'],cwd=ROOT);e=b'\r\n' if b'\r\n' in old_save else b'\n';expected=old_save.replace(b'static void show_healer_service(void);',b'static void show_healer_service(void);'+e+b'static void show_spell_teacher_service(void);').replace(b'        for(n=0;n<healer_nodes_count;n++)',b'        if(room_id==0xbf && x==136 && y==56) { show_spell_teacher_service();return; }'+e+b'        for(n=0;n<healer_nodes_count;n++)');assert read('megadrive/src/save.inc')==expected
 for n in ['megadrive/src/source_spell_teacher.h','megadrive/src/spell_teacher.inc','megadrive/src/spell_teacher_data.c']:read(n)
 checksum=sum(int.from_bytes(rom[i:i+2],'big') for i in range(0x200,len(rom),2))&65535;assert checksum==int.from_bytes(rom[0x18e:0x190],'big')
 result=dict(passed=True,version=290,md_sha256=digest,bytes=len(rom),checksum=f'{checksum:04X}',original_policy_cases=3081,controlled_game_interactions=26,portrait_checks=portraits,teacher_stack=stack_cases,natural_d1=dict(frames=capture['frames'],final_state=final,whole_ram_png_cold_replay=True,minimum_sp=minimum,heap_boundary=boundary,observed_margin_bytes=minimum-boundary),historical_v0289_d2=dict(md_sha256=old['md_sha256'],final_state=old['native_d2_stages'][-1]['last_state'],boss_assistance=False),compiled_portraits_and_texts_original=True,existing_main_change_only_service_include=True,existing_save_change_only_service_registration=True,full_game_validated=False,evidence=refs,limits=['Teacher progression, currency, introductory flags and capacity semantics execute in3081 isolated original policy cases; UI is checked in26 controlled PAL/NTSC door interactions, not a natural teacher visit.','The matrix and isolated NTSC wind-upgrade runs differed in22 inactive stack bytes at FCE2 or above, with identical persistent RAM and PNG. Separate isolated official and stack-core runs reproduce all65536 RAM bytes and PNG in both regions.','Portrait map words and referenced color indices match in24 cases. Palette quantization, reveal timing, complete dialogue raster and audio waveform are not claimed.','A static walking proposal from D1 to E6 has no route; it omits transportation and quest transformations. This does not prove the teacher unreachable in normal play. Natural acquisition and use of the second spell to open D4 remain to establish.','D1 is re-executed on v290 and cold replayed exactly. D2 success belongs to v289; later current-build campaign, exact RNG/R/IRQ and hardware parity remain incomplete.'])
 (ROOT/'analysis/spell_teacher_v0290_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print({k:v for k,v in result.items() if k in ['passed','md_sha256','checksum','controlled_game_interactions','teacher_stack','natural_d1']})
if __name__=='__main__':main()
