"""Freeze private IRQ workspace semantics and source-frame regression evidence."""
from pathlib import Path
import sys,json,subprocess
sys.path.insert(0,str(Path('tools').resolve()))
from archive_lossless_evidence import freeze,sha
root=Path('.').resolve();unit=root/'validation/v320-irq-workspace02';u=json.loads((unit/'report.json').read_bytes());assert u['passed'] and u['canonical_preprocessed_tokens_identical'] and u['host']['workspace_cases']==23000 and not u['host']['workspace_errors']
assert all(r['workspace_done'] and r['workspace_cases']==23000 and not r['workspace_errors'] for r in u['results'])
reference='95935a2db8331394f3b0889b4630258f412a5f31';assert (unit/'canonical-before.c').read_bytes()==subprocess.check_output(['git','show',reference+':megadrive/src/source_irq.c'])
for name,digest in u['native_sources'].items():assert sha((root/'megadrive/src'/name).read_bytes())==digest
work=root/'validation/v320-live-scene-workspace02';pr=json.loads((work/'report.json').read_bytes());cr=json.loads((work/'compiled-report.json').read_bytes());assert pr['passed'] and cr['passed']
old=json.loads((root/'analysis/v320_sat_runs_report.json').read_bytes())['compiled_scene'];timing=[]
for a,b in zip(old['results'],cr['results']):
 assert a['region']==b['region'] and b['intro_poll_cases']==10 and not b['intro_poll_errors'] and b['intro_poll_reads']==84520
 assert sum(b['native_call_frames'])<sum(a['native_call_frames'])
 timing.append(dict(region=b['region'],before=a['native_call_frames'],after=b['native_call_frames'],stage_frames=b['native_stage_frames'],mean_reduction_percent=100*(1-sum(b['native_call_frames'])/sum(a['native_call_frames']))))
for name,digest in pr['native_sources'].items():assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest,name
frame_path=root/'analysis/v320_workspace_game_frame_report.json';fr=json.loads(frame_path.read_bytes());assert len(fr['results'])==2 and all(r['cases']==133 for r in fr['results']) and fr['trace_disabled_full_ram_clock_agree']
for name,digest in fr['sources'].items():assert sha((root/'megadrive/src'/name).read_bytes())==digest,name
rebuild=root/'validation/v320-workspace-production-rebuild01';rr=json.loads((rebuild/'report.json').read_bytes());assert rr['passed'] and rr['base_v319_byte_identical']
for name,digest in rr['native_sources'].items():assert sha((root/'megadrive/src'/name).read_bytes())==digest,name
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin').read_bytes()
overlay=root/'validation/v320-workspace-overlay-rebuild01';o=json.loads((overlay/'build-report.json').read_bytes());assert o['passed'] and (overlay/'gaw-megadrive-candidate.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
report=dict(passed=True,public_version=320,public_rom_changed=False,public_rom_sha256=o['md_sha256'],reference_commit=reference,implementation='Shared canonical source_irq body compiled a second time for disposable private336-byte RAM. Only that variant omits its rollback buffer/copy;canonical transactional entry point keeps the identical preprocessed tokens. Full compact IRQ adapter and intro video preview already own/discard private snapshots,so use workspace entry. Intro private snapshot copy uses SGDK memcpy.',compiled_cases=46000,equivalence=u,source_frame_regression=dict(report='analysis/v320_workspace_game_frame_report.json',sha256=sha(frame_path.read_bytes()),cases_per_region=133,scope='Host native0938/frame/wait/fullIRQ/SAT/PSG composition compared against original133fixtures in each region,including exact port dates and930-byte state;five contracts each. Not compiled68000 physical renderer proof.'),compiled_scene=cr,helper_profile=timing,rollback_storage_removed_per_workspace_call_bytes=336,budget_gate_passed=False,production_base_rebuild=rr,production_overlay_rebuild=o,limits=['Small helper timing improvement near1percent,not a major performance breakthrough.69..77NTSC/58..64PAL helper frames still exceed original scene budget;not gameplayFPS.','Private workspace may be modified on rejection;never pass live RAM. Callers commit only after full success. Canonical source_irq retains rollback.','Independent original intro IRQ OUTdate audit,uninterrupted native source-clock boot,physical MDVDP/PSG and exactPCM/hardware remain open. PublicV320 remains byte-identical.'],next_action='Pattern decode/clock overhead remains dominant25..35NTSC helper frames. Profile and reduce that path before considering activation.',archive_manifest='analysis/v320-irq-workspace/manifest.json')
target=root/'analysis/v320_irq_workspace_report.json';assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n')
paths={target,frame_path,Path(__file__).resolve(),root/'validation/validate_v320_irq_workspace.py',root/'validation/validate_v320_workspace_game_frame.py',root/'validation/profile_v319_live_scene.py',root/'validation/compile_v319_intro_poll_68k.py'}
for n in ('source_irq.c','source_irq.h','source_irq_workspace.c','source_irq_context.c','source_intro_scene_vdp.c'):paths.add(root/'megadrive/src'/n)
for n in ('validate_native_source_wait.py','validate_game_sprite_frame.py','validate_queued_irq_faults.py'):paths.add(root/'tools'/n)
folders=[root/'validation'/n for n in ('v320-irq-workspace01','v320-irq-workspace02','v320-live-scene-workspace01','v320-live-scene-workspace02','v320-workspace-game-frame01','v320-workspace-production-rebuild01','v320-workspace-overlay-rebuild01')]
for folder in folders:
 paths.update(p for p in folder.rglob('*') if p.is_file());log=folder.with_suffix('.log')
 if log.exists():paths.add(log)
freeze(root,root/'analysis/v320-irq-workspace',paths,report,[*folders[:5],rebuild/'project/out',overlay],cleanup=True)
