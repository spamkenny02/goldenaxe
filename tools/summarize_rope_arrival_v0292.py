"""Bind rope arrival checks and explicitly scoped campaign progress to builds."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha

def main():
 refs={}
 def read(name):
  raw=evidence(ROOT/name);refs[name]=sha(raw);return raw
 def load(name):return json.loads(read(name))
 rom=read('gaw-megadrive.bin');digest=sha(rom);unit=load('analysis/rope_arrival_v0292_unit_report.json');game=load('analysis/rope_arrival_game_v0292-01_report.json');base=load('analysis/rope_arrival_game_v0291-baseline01_report.json');pub=load('analysis/rope_arrival_v0292_publication_report.json')
 assert unit['passed'] and unit['cases']==5456 and unit['native_c_sha256']==sha(read('megadrive/src/source_magic_rope.c'))
 assert game['passed'] and pub['passed'] and game['md_sha256']==pub['md_sha256']==digest
 assert not game['missing_arrival_reproduced'] and len(game['results'])==4 and all(c['arrival_fields_exact'] for c in game['results'])
 assert base['passed'] and base['missing_arrival_reproduced'] and base['md_sha256']==sha(read('versions/v0291-e6d968e1/gaw-megadrive-v0291.bin'))
 assert len(pub['cases'])==4 and sum(c['hardware_map_words'] for c in pub['cases'])==160
 root='validation/natural-dungeon-route/md-v0292-d1-exit02';d1=load(root+'/rebase_report.json');proof=load(root+'-fixed-replay/replay_report.json');capture=load(root+'/capture.json')
 assert d1['passed'] and proof['passed'] and d1['rom_sha256']==proof['rom_sha256']==digest and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not capture['test_ram_writes']
 final=d1['states'][-1];assert final['room_id']==0xb9 and final['hero_health']==final['hero_max_health']==32 and final['first_crystal']==128
 stackroot='validation/stack-v0292-d1-all';stack=load(stackroot+'/stack_report.json');assert stack['md_sha256']==digest and stack['all_instructions'] and not stack['ram_injections'] and not stack['invalid_heap_examples']
 low=min(c['sp'] for c in stack['instruction_minima']);boundary=stack['heap_changes'][-1]['end']+2;assert low>=boundary
 for stem,ext in [('ram','bin'),('frame','png')]:assert read(f'{stackroot}/{stem}_{capture["frames"]:05d}.{ext}')==read(f'{root}/{stem}_{capture["frames"]:05d}.{ext}')
 source_stages=[]
 for family,name,reportname in [('natural-dungeon-route','sms-v0292-source-earth-entry01','route_report'),('natural-service-route','sms-v0292-source-earth-learn01','report')]:
  root=f'validation/{family}/{name}';r=load(root+'/'+reportname+'.json');c=load(root+'/capture.json');p=load(root+f'-assisted-fixed-replay-{c["frames"]}/replay_report.json');assist=load(root+'/assistance.json')
  assert c['rom_sha256']==p['rom_sha256']==sha(read('input/original.sms')) and p['passed'] and p['whole_ram_bytes']==8192 and p['final_png_exact'] and not p['boss_assistance']
  assert not r['failure'];assert r['reached_entrance'] if reportname=='route_report' else r['passed']
  if reportname=='report':assert r['last_state']['level']==1 and r['last_state']['gold']==r['first_state']['gold']-50 and r['last_state']['max_magic']==r['first_state']['max_magic']+24 and r['new_assistance_writes']==0
  source_stages.append(dict(trace=root,frames=c['frames'],last_state=r['last_state'],last_injection_frame=p['last_injection_frame'],whole_ram_png_replay=True,assisted_history=True))
 historical=[]
 for name in ['md-v0291-d2-rebase-boss01','md-auto-v0291-d2-live-boss01','md-auto-v0291-d2-crystal01','md-auto-v0291-d2-exit01']:
  root='validation/natural-dungeon-combat/'+name;r=load(root+'/report.json');c=load(root+'/capture.json');p=load(root+f'-assisted-fixed-replay-{c["frames"]}/replay_report.json');assert p['passed'] and p['rom_sha256']==base['md_sha256'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['boss_assistance']
  historical.append(dict(trace=root,rom_sha256=c['rom_sha256'],frames=c['frames'],whole_ram_png_replay=True))
 for name in ['megadrive/src/main.c','megadrive/src/source_magic_rope.h','tools/natural_dungeon_route.py','tools/natural_house_service.py','tools/rebase_assisted_campaign.py','tools/natural_dungeon_combat.py']:read(name)
 checksum=sum(int.from_bytes(rom[i:i+2],'big') for i in range(0x200,len(rom),2))&65535;assert checksum==int.from_bytes(rom[0x18e:0x190],'big')
 report=dict(passed=True,version=292,md_sha256=digest,bytes=len(rom),checksum=f'{checksum:04X}',original_cell_cases=5456,game_cases=4,hardware_map_words=160,natural_d1=dict(frames=capture['frames'],final_state=final,whole_ram_png_replay=True),stack=dict(minimum_sp=low,heap_boundary=boundary,observed_margin_bytes=low-boundary,heap_valid=True),source_earth_stages=source_stages,historical_v0291_d2_stages=historical,full_game_validated=False,evidence=refs,limits=['Original19AB guards and19C6..1A01 execute in5456 isolated cases, compared over256 map alias bytes. Unusual source accesses outside that alias and DD00 queue timing are not asserted.','Four controlled real-loop cases deploy rope and cross B2/A2 up/down in PAL/NTSC. Arrival cells,map,integer position andterrain match. Final actual VDP climbing columns and referenced tile color indices match; intermediate transfer phase,audio,sprites and full framebuffer are not asserted.','Current v292 D1 is cold-replayed without assistance. Current native natural acquired-rope,Earth acquisition,D4/canoe and complete campaign remain unproven.','Source Earth acquisition follows an assisted historical D3 approach, with no new assistance after the prefix and no boss help. It is source-reference evidence, not v292 native campaign proof.','The v291 D2 boss/crystal/exit proofs are historical and not promoted to v292. A first D1 diagnostic used the wrong expected exterior95; actualB9 and32HP matched the prior recording. Corrected exit02 is canonical.'])
 (ROOT/'analysis/rope_arrival_v0292_report.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k in ['passed','md_sha256','checksum','stack']})
if __name__=='__main__':main()
