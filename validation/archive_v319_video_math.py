"""Freeze measured live-scene CPU reduction and exhaustive native arithmetic checks."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha,freeze
baseline=root/'validation/v319-live-scene-profile01';fast=root/'validation/v319-live-scene-profile02';math=root/'validation/v319-video-math01';ports=root/'validation/v319-port-mirror03';scene=root/'validation/v319-scene-live-vdp03';rebuild=root/'validation/v319-video-math-rebuild01'
b=json.loads((baseline/'compiled-report.json').read_bytes());f=json.loads((fast/'compiled-report.json').read_bytes());mr=json.loads((math/'report.json').read_bytes());pr=json.loads((ports/'report.json').read_bytes());sr=json.loads((scene/'report.json').read_bytes());rr=json.loads((rebuild/'report.json').read_bytes())
assert all(x['passed'] for x in (b,f,mr,pr,sr,rr)) and rr['byte_identical_v319']
assert sr['live_status_drives_canonical_irq'] and all(not row['live_status_differences'] for row in sr['live_checks'])
timing=[]
for before,after in zip(b['results'],f['results']):
 assert before['region']==after['region'] and not before['intro_poll_errors'] and not after['intro_poll_errors'] and after['intro_poll_cases']==10
 old=before['native_call_frames'];new=after['native_call_frames'];assert len(old)==len(new)==10 and all(x<y for x,y in zip(new,old))
 timing.append(dict(region=after['region'],before=old,after=new,mean_reduction_percent=100*(1-sum(new)/sum(old))))
for region in mr['results']:assert region['video_math_cases']==1966500 and region['video_math_wraps']==6325 and not region['video_math_errors']
for region in pr['results']:assert not any(region[k] for k in ('read_errors','rejected','vram_errors','protocol_errors','register_errors','palette_errors','capture_overflow'))
compiled=[]
for region in ('ntsc','pal'):
 c=json.loads((ports/('compiled-'+region+'-report.json')).read_bytes());assert c['passed'] and all(not row['port_errors'] and row['port_done'] for row in c['results']);compiled.append(c)
for name,digest in rr['source_sha256'].items():
 assert sha((root/'megadrive/src'/name).read_bytes())==digest
 assert (root/'megadrive/src'/name).read_bytes()==(rebuild/'project/src'/name).read_bytes()
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for name in ('source_intro_vdp.c','source_intro_sprite_clock.c','source_intro_scene_vdp.c'):(fast/('before-'+name)).write_bytes(subprocess.check_output(['git','show','HEAD:megadrive/src/'+name],cwd=root))
result=dict(passed=True,public_version=319,production_rom_changed=False,production_rebuild_byte_identical=True,production_rom_sha256=rr['sha256'],
 implementation='Common raster wrap replaces repeated32bit modulo with bounded subtraction; long stable gaps retain generic reduction. Native DIVU.W quotient/remainder handles every valid3420-master line coordinate. Line-boundary loop increments known line instead of dividing again. No state layout or scheduling changes.',
 helper_profile=timing,baseline_profile=b,optimized_profile=f,exhaustive_arithmetic=mr,source_port_regression=pr,compiled_port_regression=compiled,live_scene_host_regression=sr,
 native_headers={'source_video_clock_math.h':sha((root/'megadrive/src/source_video_clock_math.h').read_bytes())},
 budget_gate_passed=False,
 limits=['Same real native scene helper/status/IRQ and final original-state checks in both profiles. Setup,copies,final comparisons and per-OUT expected checks excluded; physical MD video/PSG publication still excluded.',
 'Optimized helper remains606..711 MD frames across these NTSC executions (507..595 PAL),far above source scene budget. This is a real unresolved CPU gate,not a playable speed increase. Do not activate this per-OUT composition in publishedROM.',
 'Initial scene snapshots,not uninterrupted coldboot. Independent IRQ OUT-date proof and complete physical video/PSG remain open. No hardware/PCM/fidelity completion claim.'],
 next_action='Profile hot call counts/stage costs and replace per-OUT overhead with exact source-timed runs and stable-line batching,without skipping observable status or IRQ boundaries. Recheck live states and measure against source before activation. YouTube video remains local pending browser access and visibility.',
 oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-video-math/manifest.json')
target=root/'analysis/v319_video_math_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve()}
for name in ('profile_v319_live_scene.py','validate_v319_video_math_68k.py','compile_v319_port_mirror_68k.py'):paths.add(root/'validation'/name)
for name in ('source_video_clock_math.h','source_intro_vdp.c','source_intro_sprite_clock.c','source_intro_scene_vdp.c'):paths.add(root/'megadrive/src'/name)
folders=[baseline,fast,math,ports,scene,rebuild]
for folder in folders:paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root,root/'analysis/v319-video-math',paths,result,[*folders[:-1],rebuild/'project/out'],cleanup=True)
