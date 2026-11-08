"""Freeze the native calendar proof, independent event generation and rebuild."""
import gzip,json,re,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
work=root/'validation/v319-sprite-clock03';r=json.loads((work/'report.json').read_bytes())
assert r['passed'] and r['frames']==14000 and r['capture_overflow']==0 and r['transition_vectors']==58730
assert sum(row['mode4_reads'] for row in r['results'])==33707
assert sum(row['cpu_checkpoints'] for row in r['results'])==186498983
for row in r['results']:assert not (row['mismatch'] or row['unsupported'] or row['non_11t_reads'] or row['errors'])
for name,digest in r['native_sources'].items():assert sha((root/'megadrive/src'/name).read_bytes())==digest
raw=(work/'transitions.bin').read_bytes();assert len(raw)==58730*512 and sha(raw)==r['transition_sha256']
kinds={0:0,1:0};source_reads=0
for base in range(0,len(raw),512):
 kind=raw[base+188];kinds[kind]+=1
 if kind==1:assert raw[base+191]==1;source_reads+=1
assert source_reads==3163
cr=json.loads((work/'compiled-all-report.json').read_bytes());assert cr['passed'] and cr['source_transition_vectors']==58730 and cr['compiled_executions']==117460 and cr['irq_provider_checks']==6326
covered=[]
for part in cr['partitions']:
 p=part['report'];assert p['passed']
 for row in p['results']:assert row['clock_done']==1 and not row['clock_errors'] and row['clock_cases_done']==p['count']
 covered.extend(range(p['start'],p['start']+p['count']))
assert covered==list(range(58730))
bound=root/'validation/v319-sprite-clock-boundaries01';br=json.loads((bound/'report.json').read_bytes());assert br['passed'] and all(not row['boundary_errors'] for row in br['results'])
rebuild=root/'validation/v319-sprite-clock-rebuild01';rr=json.loads((rebuild/'report.json').read_bytes());assert rr['passed'] and rr['byte_identical_v319']
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for name,digest in rr['source_sha256'].items():
 assert sha((root/'megadrive/src'/name).read_bytes())==digest
 assert (root/'megadrive/src'/name).read_bytes()==(rebuild/'project/src'/name).read_bytes()
observer=root/'validation/v319-sprite-clock-observer01';build=json.loads((observer/'report.json').read_bytes());core=root.parents[1]/'work/genesis-plus-gx'
for name,digest in build['original_source_sha256'].items():assert sha((core/name).read_bytes())==digest
assert build['original_sources_restored'] and build['core_sha256']==r['core_sha256']
manifest=json.loads((root/'analysis/v319-psg-write-spacing/manifest.json').read_bytes())
for region in ('ntsc','pal'):
 item=manifest['compressed'][f'validation/v319-psg-writes01/{region}-sms/exposed-psg-states.bin'];encoded=(root/'analysis/v319-psg-write-spacing'/item['stored']).read_bytes();assert sha(encoded)==item['stored_sha256']
 data=gzip.decompress(encoded);assert sha(data)==item['raw_sha256'] and data==(work/(region+'-psg.bin')).read_bytes()
table=(core/'core/hvc.h').read_text().split('static const uint8 cycle2hc32[3420] =')[1].split('};')[0]
table=re.sub(r'/\*.*?\*/','',table,flags=re.S);values=[int(x,16) for x in re.findall(r'0x[0-9a-fA-F]+',table)];assert len(values)==3420
for phase,expected in enumerate(values):
 h=phase//20;assert ((h+0x85 if h<15 else h+0xda)&255)==expected
result=dict(passed=True,public_version=319,production_rom_changed=False,production_rebuild_byte_identical=True,production_rom_sha256=rr['sha256'],
 implementation='source_intro_sprite_clock.c/.h schedules native sprite parse/render and latched VINT directly from elapsed master ticks and live logical VRAM/register inputs. No reference parse/render callbacks or expected status queues feed the product calendar. IRQ provider samples IN37T before0137 and checks elapsed/raster origins.',
 native_calendar=r,compiled68000=cr,boundary_contracts=br,transition_kinds=dict(line_boundary=kinds[0],source_checked_read=kinds[1]),
 psg_exact_frames_per_region=14000,hcounter_phases_exact=3420,reference_observer=build,
 rejection='Initial vector storage kept empty fractional-line tails and exceeded its fixed capacity. Final capture normalizes those tails only in advance-only vector copies, preserving exact read phases and all live calendar state;58730 complete vectors, no overflows. Prior capture inputs and diagnostics retained.',
 limits=['VRAM/register values still come from the reference in this corpus; this is not yet a port-written native mirror connected to the foreground/IRQ writers.',
 'Advance-only compiled vectors normalize empty fractional-line tails to one exact line; read vectors preserve original phases. Full unnormalized host timeline independently compares all33707 source status bytes.',
 'Mode4/192/SMS2,unzoomed8px,no overscan processing,no-input intro/title. The early horizontal-read branch has synthetic contract coverage, not a new original-source observation.',
 'Calendar throughput and composite MD video/PSG deadlines have not been measured. The previous19..22-frame loader CPU measurement excludes this new calendar; no combined budget or hardware/PCM certificate.'],
 next_action='Drive the calendar from the native VRAM/register port mirror, foreground status reads and timed IRQ SAT writes. Provide instruction boundaries around observable writes, preserve boot history, supply032A output dates, then validate combined video/PSG output and throughput before activating a numbered ROM.',
 oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-sprite-clock/manifest.json')
target=root/'analysis/v319_sprite_clock_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve()}
for name in ('build_v319_sprite_clock_observer.py','validate_v319_sprite_clock.py','compile_v319_sprite_clock_68k.py','compile_v319_sprite_clock_all.py','validate_v319_sprite_clock_boundaries.py'):paths.add(root/'validation'/name)
for name in ('source_intro_sprite_clock.c','source_intro_sprite_clock.h','source_intro_sprite_status.c','source_intro_sprite_status.h'):paths.add(root/'megadrive/src'/name)
folders=[root/'validation'/name for name in ('v319-sprite-clock-smoke01','v319-sprite-clock01','v319-sprite-clock02','v319-sprite-clock03','v319-sprite-clock-boundaries01','v319-sprite-clock-rebuild01')]
for folder in folders:paths.update(p for p in folder.rglob('*') if p.is_file())
paths.update(p for p in observer.iterdir() if p.is_file() and not p.name.endswith(('-before.c','-observer.c')))
freeze(root,root/'analysis/v319-sprite-clock',paths,result,[*folders[:-1],rebuild/'project/out'],cleanup=True)
