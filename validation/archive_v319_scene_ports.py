"""Freeze composed full native scene port publication against original vectors."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
work=root/'validation/v319-scene-ports01';r=json.loads((work/'report.json').read_bytes());cr=json.loads((work/'compiled-report.json').read_bytes())
assert r['passed'] and len(r['host_scene_ports'])==10 and all(row['state_and_io_exact'] for row in r['host_scene_ports'])
assert sum(row['all_foreground_outputs'] for row in r['host_scene_ports'])==252520 and sum(row['real_native_irqs'] for row in r['host_scene_ports'])==244
assert cr['passed'] and cr['source_vector_cases']==10 and all(row['intro_poll_done'] and row['intro_poll_cases']==10 and not row['intro_poll_errors'] for row in cr['results'])
for name,digest in r['native_sources'].items():assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
rebuild=root/'validation/v319-scene-ports-rebuild01';rr=json.loads((rebuild/'report.json').read_bytes());assert rr['passed'] and rr['byte_identical_v319']
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for name,digest in rr['source_sha256'].items():
 assert sha((root/'megadrive/src'/name).read_bytes())==digest
 assert (rebuild/'project/src'/name).read_bytes()==(root/'megadrive/src'/name).read_bytes()
for name in ('source_intro_scene.c','source_intro_scene.h'):(work/('before-'+name)).write_bytes(subprocess.check_output(['git','show','HEAD:megadrive/src/'+name],cwd=root))
result=dict(passed=True,public_version=319,production_rom_changed=False,production_rebuild_byte_identical=True,production_rom_sha256=rr['sha256'],
 implementation='source_intro_scene_load_ports composes E50 scene preparation/map copy,dated native032A outputs,plane clear,map decode/place/transfer with unchanged real native IRQ/audio work and callbacks. Separate pattern sink preserves11T immediateOUT versus16T mapOUTI distinction. Legacy API retains prior behavior.',
 host=r,compiled68000=cr,compiled_cases=20,compiled_foreground_outputs=505040,compiled_real_native_irqs=488,
 verification='Ten original full-scene state vectors,15081trackedRAM/mirror bytes plus400audio and18clock/R/output fields. All old8452clear/map OUT dates percase remain original full-elapsed exact; additional pattern OUT dates/values match the independent actual original foreground execution after separating IRQ work. Chronological ordering across all foreground sinks checked.',
 limits=['Original per-IRQ status values still come from captured diagnostic inputs. Live ownedVDP status,IRQ video packets/register writes,complete coldboot history and physical MD video/audio are not yet composed.',
 'Pattern dates are foreground-time exact; source captures constrain real native IRQ timing and full final clock/R state but do not independently sample every pattern wall-clock timestamp.',
 'Compiled diagnostic frames include expected-output checks; no helper-only composite budget or hardware/PCM claim. PublishedV319 unchanged.'],
 next_action='Bind separate pattern/map/clear ports into ownedVDP with exact instruction durations,deliver real IRQ SAT/status and initial history,then profile/optimize the complete scene and physical video/PSG. Prepare requested full gameplay recording after the current integration step is validated.',
 oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-scene-ports/manifest.json')
target=root/'analysis/v319_scene_ports_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve(),root/'validation/validate_v319_scene_ports.py',root/'validation/compile_v319_intro_poll_68k.py'}
for folder in (work,rebuild):paths.update(p for p in folder.rglob('*') if p.is_file())
for name in ('source_intro_scene.c','source_intro_scene.h'):paths.add(root/'megadrive/src'/name)
freeze(root,root/'analysis/v319-scene-ports',paths,result,[work,rebuild/'project/out'],cleanup=True)
