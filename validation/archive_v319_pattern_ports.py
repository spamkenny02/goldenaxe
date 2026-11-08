"""Freeze native decoder output timing,68000 and owned-VDP integration evidence."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
work=root/'validation/v319-pattern-ports02';r=json.loads((work/'report.json').read_bytes());cr=json.loads((work/'compiled-report.json').read_bytes())
binding=root/'validation/v319-pattern-vdp-binding01';br=json.loads((binding/'report.json').read_bytes())
rebuild=root/'validation/v319-pattern-ports-rebuild01';rr=json.loads((rebuild/'report.json').read_bytes())
assert r['passed'] and r['host_cases']==1054 and r['native_sha256']==sha((root/'megadrive/src/source_pattern_clock.c').read_bytes())
assert cr['passed'] and cr['compiled_cases']==48 and cr['compiled_outputs']==785664
assert br['passed'] and br['cases']==24 and br['outputs']==392832
for part in cr['partitions']:
 assert part['passed'] and part['cases']==6
 for row in part['results']:assert row['pattern_done'] and row['pattern_cases']==6 and row['pattern_errors']==0
for name,digest in br['native_sources'].items():assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
assert rr['passed'] and rr['byte_identical_v319'] and (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for name,digest in rr['source_sha256'].items():
 assert sha((root/'megadrive/src'/name).read_bytes())==digest
 assert (root/'megadrive/src'/name).read_bytes()==(rebuild/'project/src'/name).read_bytes()
for name in ('source_pattern_clock.c','source_pattern_clock.h'):
 (work/('before-'+name)).write_bytes(subprocess.check_output(['git','show','HEAD:megadrive/src/'+name],cwd=root))
result=dict(passed=True,public_version=319,production_rom_changed=False,production_rebuild_byte_identical=True,production_rom_sha256=rr['sha256'],
 implementation='source_pattern_decode_ports retains the native032A instruction/IRQ clock and decoded mirror while publishing every BF/BF/BE write at completed OUT time. Planned ROM windows,whole commands and repeated-byte batches expand exact dates; scalar fallback emits after each actual native instruction. Sink failure is fatal.',
 host=r,compiled68000=cr,native_owned_vdp_binding=br,
 output_dates='Per decoded byte,BF low at30T,BF high45T,BE value77T after RST28 call entry; literal135T or repeat134T byte stride,minus1T on page carry,minus5T terminal DJNZ. Command prefix44T and suffix16T literal/29T repeat. All calculations preserve15master ticks/T.',
 limits=['Independent original SMS trace checks18528port/value outputs for the first intro asset in each source region. Exact absolute original032A output timestamps remain to capture; scalar-expanded timing checks share the semantic instruction plan.',
 'Synthetic82T/8M1 interrupt callback in these decoder tests, not full native IRQ audio/SAT work. Complete scene boot history,foreground status reads and physical outputs are not yet composed.',
 'Owned VDP binding is host-tested24cases; decoder outputs alone are compiled48cases. Do not claim compiled complete decoder+VDP binding yet. No composite throughput/PCM/hardware certificate.',
 'PublishedV319 remains byte-identical. No numbered release for the unselected output sink.'],
 next_action='Compile/profile the decoder+ownedVDP sink, capture original032A OUT timestamps independently, then compose scene map/reveal sinks and timed IRQ SAT/status with complete boot history. Measure combined budget before activation and requested full gameplay video.',
 video_request=dict(channel='@KennYMcCormick-m2b',user_reports_authenticated_session=True,deliverable='Full gameplay video through credits after current step is validated, then YouTube upload.',visibility='not specified',publication_pending=True),
 oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-pattern-ports/manifest.json')
target=root/'analysis/v319_pattern_ports_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve()}
for name in ('validate_v319_pattern_ports.py','compile_v319_pattern_ports.py','validate_v319_pattern_vdp_binding.py'):paths.add(root/'validation'/name)
for name in ('source_pattern_clock.c','source_pattern_clock.h'):paths.add(root/'megadrive/src'/name)
folders=[root/'validation/v319-pattern-ports01',work,binding,rebuild]
for folder in folders:paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root,root/'analysis/v319-pattern-ports',paths,result,[*folders[:-1],rebuild/'project/out'],cleanup=True)
