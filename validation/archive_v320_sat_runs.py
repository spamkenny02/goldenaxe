"""Freeze native IRQ SAT batching equivalence,profile and unchanged publicV320."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path('tools').resolve()))
from archive_lossless_evidence import freeze,sha
root=Path('.').resolve();test=root/'validation/v320-sat-runs02';tr=json.loads((test/'report.json').read_bytes());assert tr['passed'] and tr['host_cases']==48300
assert all(r['sat_done'] and r['sat_cases']==48300 and not r['sat_errors'] for r in tr['results'])
for name,digest in tr['native_sources'].items():assert sha((root/'megadrive/src'/name).read_bytes())==digest
work=root/'validation/v320-live-scene-sat01';pr=json.loads((work/'report.json').read_bytes());cr=json.loads((work/'compiled-report.json').read_bytes());assert pr['passed'] and cr['passed']
before=json.loads((root/'analysis/v319_empty_sprite_clock_report.json').read_bytes())['compiled_scene'];timing=[]
for a,b in zip(before['results'],cr['results']):
 assert a['region']==b['region'] and b['intro_poll_cases']==10 and not b['intro_poll_errors'] and b['intro_poll_reads']==84520
 assert all(x<y for x,y in zip(b['native_call_frames'],a['native_call_frames']))
 timing.append(dict(region=b['region'],before=a['native_call_frames'],after=b['native_call_frames'],stage_frames=b['native_stage_frames'],mean_reduction_percent=100*(1-sum(b['native_call_frames'])/sum(a['native_call_frames']))))
# Profile used current C text with CRLF; formatting was restored to repositoryLF.
for name,digest in pr['native_sources'].items():
 p=root/'megadrive/src'/(name+'.c');raw=p.read_bytes()
 assert digest in (sha(raw),sha(raw.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))),name
rebuild=root/'validation/v320-sat-production-rebuild01';rr=json.loads((rebuild/'report.json').read_bytes());assert rr['passed'] and rr['base_v319_byte_identical']
for name,digest in rr['native_sources'].items():assert sha((root/'megadrive/src'/name).read_bytes())==digest
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin').read_bytes()
overlay=root/'validation/v320-sat-overlay-rebuild01';o=json.loads((overlay/'build-report.json').read_bytes());assert o['passed'] and o['md_sha256']=='9e5b0abed80678ce864a0bb796c17e97047d1d34e5227a5275bf9336129ceaff'
assert (overlay/'gaw-megadrive-candidate.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
report=dict(passed=True,public_version=320,public_rom_changed=False,public_rom_sha256=o['md_sha256'],native_module_selected_in_public_rom=False,implementation='The192IRQ SAT OUTIs are supplied as64Y and128XY byte runs. Advance to each sprite-line boundary before its first following VRAM mutation;group only byte dates strictly within a line. Preserve final command/buffer/address/checkpoint,cache and latch state. BF control and palette writes remain individually dated.',full_state_equivalence=tr,compiled_cases=96600,compiled_scene=cr,helper_profile=timing,budget_gate_passed=False,production_base_rebuild=rr,production_overlay_rebuild=o,profile_line_endings_normalized_after_build=True,limits=['Native helper profile70..78MDframesNTSC/58..65PAL remains above original source scene budget. Do not select this composition in the publicROM. These are helper diagnostic runtimes,not gameplayFPS.','48300host and96600compiled cases check fullVDP/cache/state and256SAT bytes after each run/read;full16KiBVRAM canaries after each source-line block. The earlier test01 stopped at its180000frame cap with11404cases/no mismatch;not counted as a completed68000 test.','Live source-scene states/status/clock/audio match20compiled vectors. Physical MD video/PSG publication and independent original IRQ OUT-date capture remain open. No uninterrupted native source-clock coldboot or global PCM/hardware fidelity certificate.'],next_action='Patterns now dominate25..34NTSC frames;reduce their native overhead and IRQ preview/rollback copies without replacing source work or observable dates. Recheck composed CPU gate before activation.',archive_manifest='analysis/v320-sat-runs/manifest.json')
target=root/'analysis/v320_sat_runs_report.json';assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n')
paths={target,Path(__file__).resolve(),root/'validation/validate_v320_sat_runs.py',root/'validation/profile_v319_live_scene.py'}
for name in ('source_intro_vdp.c','source_intro_vdp.h','source_intro_scene_vdp.c'):paths.add(root/'megadrive/src'/name)
folders=[root/'validation'/n for n in ('v320-sat-runs01','v320-sat-runs02','v320-live-scene-sat01','v320-sat-production-rebuild01','v320-sat-overlay-rebuild01')]
for folder in folders:
 paths.update(p for p in folder.rglob('*') if p.is_file());log=folder.with_suffix('.log')
 if log.exists():paths.add(log)
freeze(root,root/'analysis/v320-sat-runs',paths,report,[folders[0],folders[1],folders[2],rebuild/'project/out',overlay],cleanup=True)
