"""Bind axe terrain translation and natural first-teacher/gold progress to v291."""
import json,re,subprocess
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha

def main():
 refs={}
 def read(n):
  raw=evidence(ROOT/n);refs[n]=sha(raw);return raw
 def load(n):return json.loads(read(n))
 rom=read('gaw-megadrive.bin');digest=sha(rom);source=read('input/original.sms');unit=load('analysis/axe_terrain_probes_v0291_report.json');game=load('analysis/axe_terrain_game_v0291-02_report.json');base=load('analysis/axe_terrain_game_v0290-baseline_report.json');publication=load('analysis/axe_terrain_publication_v0291_report.json')
 assert unit['passed'] and unit['cases']==4356 and unit['native_c_sha256']==sha(read('megadrive/src/source_axe_terrain.c'))
 assert game['passed'] and publication['passed'] and game['md_sha256']==publication['md_sha256']==digest and not game['missing_cut_reproduced'];assert base['passed'] and base['missing_cut_reproduced'] and base['md_sha256']==sha(read('versions/v0290-63cb9dcc/gaw-megadrive-v0290.bin'))
 for region in ['auto','pal']:
  prefix='validation/axe-terrain-game-v0291-02/'+region;sa=load(prefix+'-sms/observations.json');md=load(prefix+'-md/observations.json');assert sa==md and len(sa)==2560
 assert len(game['cases'])==64 and len(publication['cases'])==122
 stages=[]
 names=[('natural-dungeon-route','md-v0291-d1-exit01','rebase_report'),('natural-dungeon-route','md-v0291-thunder-entry04','route_report'),('natural-service-route','md-v0291-thunder-intro01','report'),('natural-dungeon-route','md-v0291-gold-entry03','route_report'),('natural-service-route','md-v0291-gold50-01','report'),('natural-dungeon-route','sms-v0291-source-thunder-entry03','route_report'),('natural-service-route','sms-v0291-source-thunder-intro01','report')]
 for family,name,report_name in names:
  root='validation/'+family+'/'+name;r=load(root+'/'+report_name+'.json');c=load(root+'/capture.json');proof=load(root+'-fixed-replay/replay_report.json');expected=sha(source) if name.startswith('sms') else digest
  assert c['rom_sha256']==proof['rom_sha256']==expected and proof['passed'] and proof['whole_ram_bytes']==(8192 if name.startswith('sms') else 65536) and proof['final_png_exact'] and not c['test_ram_writes'] and c['sram_input'] is None
  if report_name=='route_report':assert r['reached_entrance'] and not r['failure'] and not r['normal_continues'] and r['directional_probe_succeeded']
  else:assert r['passed'] and not r.get('failure')
  final=r.get('last_state',r.get('states',[None])[-1]);stages.append(dict(trace=root,frames=c['frames'],final_state=final,whole_ram_png_cold_replay=True))
 for stage in [stages[2],stages[6]]:assert stage['final_state']['room']==0xe6 and stage['final_state']['intro']==1 and stage['final_state']['level']==0
 assert stages[4]['final_state']['gold']==57 and stages[4]['final_state']['outside_flags']==3 and stages[4]['final_state']['room']==0xf4
 sy={m[2].split('.lto_priv.')[0]:int(m[1],16) for line in read('megadrive/out/release/symbol.txt').decode().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))};offset=sy['world_axe_terrain'];assert rom[offset:offset+21]==source[0x3620:0x3635]
 a=read(stages[2]['trace']+f"/ram_{stages[2]['frames']:05d}.bin");b=read(stages[6]['trace']+f"/ram_{stages[6]['frames']:05d}.bin");data=lambda n,k:bytes(a[((sy[n]+i)&65535)^1] for i in range(k));assert data('sms_vram',16384)[0x3800:0x3d00]==b[0x1600:0x1b00] and data('scratch',4096)[0x800:0x8a0]==b[0x1c00:0x1ca0] and data('hero_items',17)==b[0xe0:0xf1] and data('game_save_state',592)[0x136]==b[0x1e6]==1
 stack=load('validation/stack-v0291-axe-gold-all/stack_report.json');assert stack['md_sha256']==digest and stack['all_instructions'] and not stack['invalid_heap_examples'] and not stack['ram_injections'];minimum=min(v['sp'] for v in stack['instruction_minima']);boundary=stack['heap_changes'][-1]['end']+2;assert minimum>=boundary
 final=stages[4]
 for stem,ext in [('ram','bin'),('frame','png')]:assert read(f"validation/stack-v0291-axe-gold-all/{stem}_{final['frames']:05d}.{ext}")==read(final['trace']+f"/{stem}_{final['frames']:05d}.{ext}")
 read('megadrive/src/main.c');read('megadrive/src/source_axe_terrain.h');read('megadrive/src/axe_terrain_data.c');read('tools/natural_dungeon_route.py');read('tools/natural_house_service.py')
 checksum=sum(int.from_bytes(rom[i:i+2],'big') for i in range(0x200,len(rom),2))&65535;assert checksum==int.from_bytes(rom[0x18e:0x190],'big')
 result=dict(passed=True,version=291,md_sha256=digest,bytes=len(rom),checksum=f'{checksum:04X}',original_probe_cases=4356,controlled_game_cases=128,controlled_frames=5120,hardware_publication_cases=122,natural_stages=stages,cross_source_native_e6=dict(map_bytes=1280,cells_bytes=160,inventory_bytes=17,room_flag=1),stack=dict(frames=final['frames'],minimum_sp=minimum,heap_boundary=boundary,observed_margin_bytes=minimum-boundary,heap_valid=True),compiled_terrain_records_original=True,full_game_validated=False,evidence=refs,limits=['Original34D3/34F0 dispatch,guards and232F arithmetic execute in4356 isolated probe cases. Side effects are separately checked in128 real-loop cases with explicit RAM fixtures.','All128 cases match software cells,map,phase andflags for40 frames.122 positive cases also match final VDP map words and referenced tile color indices; intermediate transfer timing and audio waveform are not asserted.','The current native natural route completes D1,cuts real trees,opens E6,visits the first teacher and exits,then opens F4 and receives50 gold,without aid/death. The first visit only records the introduction; the Foudre spell is not yet acquired.','Source and native have separate whole-RAM/PNG cold replays and identical E6 map/cells/inventory/flag after the visit. HP,gold,encounters,RNG/IRQ and global timing are not asserted equal.','An A3 walking proposal still has no route; cliff/rope/travel prerequisites remain to model and execute. Earth acquisition,D4 passage/canoe/boss and the complete current-build campaign remain incomplete.','Natural controller diagnostics are retained: remote passage assumed early,tree blocking final house mouth,live map not expanded for proposed chopping,and one source budget below its recorded prefix. Canonical successful entry04 and gold-entry03 replace these failures.'])
 (ROOT/'analysis/axe_terrain_v0291_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print({k:v for k,v in result.items() if k in ['passed','md_sha256','checksum','stack','controlled_game_cases','hardware_publication_cases']})
if __name__=='__main__':main()
