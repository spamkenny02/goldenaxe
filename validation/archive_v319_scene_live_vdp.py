"""Freeze native scene/IRQ ports and live status driving canonical work."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
work=root/'validation/v319-scene-live-vdp02';r=json.loads((work/'report.json').read_bytes());cr=json.loads((work/'compiled-report.json').read_bytes())
assert r['passed'] and r['live_status_drives_canonical_irq'] and len(r['live_checks'])==10
assert sum(row['live_status_reads'] for row in r['live_checks'])==244 and sum(row['live_irq_packets'] for row in r['live_checks'])==40
assert all(row['accepted'] and not row['live_status_differences'] for row in r['live_checks'])
assert cr['passed'] and cr['source_vector_cases']==10 and all(row['intro_poll_done'] and not row['intro_poll_errors'] and row['intro_poll_cases']==10 for row in cr['results'])
for name,digest in r['native_sources'].items():assert sha((root/'megadrive/src'/(name+'.c')).read_bytes())==digest
wrapper=(work/'wrapper.c').read_text();assert 'irq->ram[0x1b]=irq_status_values' not in wrapper and 'context.status_read=source_intro_vdp_irq_status' in wrapper
rebuild=root/'validation/v319-scene-live-vdp-rebuild01';rr=json.loads((rebuild/'report.json').read_bytes());assert rr['passed'] and rr['byte_identical_v319']
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for name,digest in rr['source_sha256'].items():
 assert sha((root/'megadrive/src'/name).read_bytes())==digest
 assert (rebuild/'project/src'/name).read_bytes()==(root/'megadrive/src'/name).read_bytes()
for name in ('source_intro_vdp.c','source_intro_vdp.h'):(work/('before-'+name)).write_bytes(subprocess.check_output(['git','show','HEAD:megadrive/src/'+name],cwd=root))
result=dict(passed=True,public_version=319,production_rom_changed=False,production_rebuild_byte_identical=True,production_rom_sha256=rr['sha256'],
 implementation='source_intro_scene_vdp adapters deliver native foreground pattern11T/clear11T/mapOUTI16T outputs to independent logical VDP. Timed compact IRQ callback publishes original register OUTD16T/OUT(C)12T,192SAT OUTI16T,palette OUTI/DJNZ29T spacing with canonical PAL/NTSC polling. Live source_intro_vdp_irq_status drives C01B before actual native IRQ/audio work. Original statuses only compared after canonical work.',
 host=r,compiled68000=cr,compiled_cases=20,compiled_live_status_reads=488,compiled_timed_full_irq_packets=80,
 verification='All10 original E50 vectors retain15081trackedRAM/mirror bytes,400audio andclock/R/output. Live status equals all244originalIRQ bytes onhost and488compiled reads. Additional IRQ register/SAT/palette publication feeds owned memory chronologically; tracked9216pattern+768map VRAM exact.',
 limits=['Initial scene inputs are captured snapshots with explicit initial register/SAT/VRAM/palette values. Native sprite caches/latches start cold; these ten cases match,but uninterrupted complete boot/title history remains unproven.',
 'IRQ delivery covers observed intro path only: no queuedtile/HUD/map requests. Other requests reject before publication; general game video still uses its existing adapter.',
 'IRQ port offsets are implemented from original instruction sequence and canonical stage work; independent original full IRQ OUT timestamp capture remains to add.',
 'Compiled19188NTSC/16054PAL kernel frames include full diagnostic comparison/setup. They are not game FPS or helper-only budget. Composite CPU cost,physical MD video/PSG,PCM and hardware proof remain open.'],
 next_action='Independently audit IRQ OUT dates and profile the live scene helper without oracle overhead; preserve complete boot/history and validate physical video/PSG before ROM activation. Begin requested full publishedV319 gameplay recording, clearly labeled development build, for user review and later YouTube upload.',
 video_request=dict(channel='@KennYMcCormick-m2b',user_reports_authenticated_session=True,visibility='unspecified',full_gameplay_pending=True),
 oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-scene-live-vdp/manifest.json')
target=root/'analysis/v319_scene_live_vdp_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve(),root/'validation/validate_v319_scene_live_vdp.py',root/'validation/compile_v319_intro_poll_68k.py'}
folders=[root/'validation/v319-scene-live-vdp01',work,rebuild]
for folder in folders:paths.update(p for p in folder.rglob('*') if p.is_file())
for name in ('source_intro_vdp.c','source_intro_vdp.h','source_intro_scene_vdp.c','source_intro_scene_vdp.h'):paths.add(root/'megadrive/src'/name)
freeze(root,root/'analysis/v319-scene-live-vdp',paths,result,[*folders[:-1],rebuild/'project/out'],cleanup=True)
