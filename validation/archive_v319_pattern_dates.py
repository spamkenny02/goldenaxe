"""Freeze source-executed pattern dates and compiled decoder/ownedVDP binding."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
work=root/'validation/v319-pattern-dates01';r=json.loads((work/'report.json').read_bytes());assert r['passed']
assert r['source_sha256']==sha((root/'input/original.sms').read_bytes()) and r['native_sha256']==sha((root/'megadrive/src/source_pattern_clock.c').read_bytes())
assert len(r['results'])==2
for region in r['results']:
 assert region['psg_exact_frames']==14000 and len(region['checks'])==2
 for check in region['checks']:assert check['foreground_dates_and_values_exact'] and check['source_end_and_destination_exact'] and check['actual_irq_master']>0
outputs=sum(c['outputs'] for region in r['results'] for c in region['checks']);assert outputs==65472
prior=root/'validation/v319-pattern-ports02';cr=json.loads((prior/'compiled-vdp-report.json').read_bytes());assert cr['passed'] and cr['compiled_cases']==48 and cr['compiled_outputs']==785664
for part in cr['partitions']:
 assert part['passed'] and part['owned_vdp_bound'] and part['cases']==6
 for row in part['results']:assert row['pattern_cases']==6 and not row['pattern_errors'] and row['pattern_done']
observer=root/'validation/v319-pattern-dates-observer01';br=json.loads((observer/'report.json').read_bytes());core=root.parents[1]/'work/genesis-plus-gx'
assert br['original_sources_restored'] and br['core_sha256']==r['core_sha256']
for name,digest in br['original_source_sha256'].items():assert sha((core/name).read_bytes())==digest
result=dict(passed=True,public_version=319,production_rom_changed=False,
 source_executed_dates=r,compiled_native_decoder_and_owned_vdp=cr,source_outputs_exact=outputs,
 native_sources={name:sha((root/'megadrive/src'/(name+'.c')).read_bytes()) for name in ('source_pattern_clock','source_clock','source_rng','source_intro_vdp','source_intro_sprite_clock','source_intro_sprite_status')},
 progress='Both intro032A streams now have independent original execution evidence for every foreground OUT completion date and value, total foreground time and HL/DE return. Native decoder feeding its independently owned VDP memory is additionally compiled and checked in both MD regions at six IRQ edges for each source region/asset.',
 limits=['Foreground dates are original-execution exact after subtracting actual original IRQ work. Native test IRQ callback remains synthetic82T/8M1, so original absolute dates and full audio/SAT IRQ composition are still unproven.',
 'All16KiB final mirror bytes and all dated outputs are checked in the compiled binding, but source scene boot/status history and physical video/PSG are not yet composed.',
 'Compiled diagnostic frame counts include expected-event comparisons. They are not a helper CPU profile or game FPS. Large diagnostic runtimes justify profiling and optimization before activation; no combined performance gate claimed.'],
 next_action='Compose dated pattern outputs with the native scene clear/map/reveal ports and real timed IRQ status/SAT history, then profile helper-only execution and physical video/PSG delivery before activating a numbered ROM and recording full gameplay.',
 oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-pattern-dates/manifest.json')
target=root/'analysis/v319_pattern_dates_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve()}
for name in ('build_v319_pattern_dates_observer.py','validate_v319_pattern_dates.py','compile_v319_pattern_ports.py'):paths.add(root/'validation'/name)
for p in (root/'megadrive/src').glob('source_*'):
 if p.name.startswith(('source_pattern_clock','source_intro_vdp','source_intro_sprite_clock','source_intro_sprite_status','source_clock','source_rng')):paths.add(p)
paths.update(p for p in work.rglob('*') if p.is_file())
for folder in prior.glob('kernel-*-vdp*'):
 if folder.is_dir():paths.update(p for p in folder.rglob('*') if p.is_file())
paths.update(prior.glob('kernel-*-vdp-report.json'));paths.add(prior/'compiled-vdp-report.json')
paths.update(p for p in observer.iterdir() if p.is_file() and not p.name.endswith(('-before.c','-observer.c')))
cleanup=[work,*[p for p in prior.glob('kernel-*-vdp*') if p.is_dir()]]
freeze(root,root/'analysis/v319-pattern-dates',paths,result,cleanup,cleanup=True)
