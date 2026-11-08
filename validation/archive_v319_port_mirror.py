"""Freeze independently owned video-port memory proof and native68000 replay."""
import gzip,json,struct,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
work=root/'validation/v319-port-mirror02';r=json.loads((work/'report.json').read_bytes());assert r['passed'] and r['frames']==14000
assert sum(row['writes'] for row in r['results'])==8494239
assert sum(row['status_reads'] for row in r['results'])==33707
assert sum(row['data_reads'] for row in r['results'])==5616
for row in r['results']:
 assert not any(row[k] for k in ('read_errors','rejected','vram_errors','protocol_errors','register_errors','palette_errors','capture_overflow','errors'))
for name,digest in r['native_sources'].items():assert sha((root/'megadrive/src'/name).read_bytes())==digest
origin=root/'validation/v319-port-origin01';pr=json.loads((origin/'report.json').read_bytes());assert pr['passed']
parts=[];events=reads=irq_reads=0
for region in ('ntsc','pal'):
 row=next(x for x in r['results'] if x['region']==region);phase=next(x for x in pr['results'] if x['region']==region)
 assert row['event_sha256']==phase['event_sha256'] and row['capture_final_hash']==phase['capture_final_hash']
 assert phase['initial_raster']==(159 if region=='ntsc' else 132)*3420+990
 raw=(work/(region+'-ports.bin')).read_bytes();assert sha(raw)==row['event_sha256'] and len(raw)==row['captured_port_events']*8
 last=0;original_reads=0
 for off in range(0,len(raw),8):
  elapsed,kind,port,value,tstates=struct.unpack_from('<IBBBB',raw,off)
  assert last<=elapsed and tstates and kind in (0,1,2);last=elapsed;original_reads+=kind!=0
 c=json.loads((work/('compiled-'+region+'-report.json')).read_bytes());assert c['passed'] and c['source_events']==len(raw)//8 and c['source_reads']==original_reads
 for result in c['results']:
  assert result['port_done'] and not result['port_errors'] and result['port_events_done']==c['source_events'] and result['port_reads']==original_reads and result['port_final_hash']==row['capture_final_hash']
  events+=result['port_events_done'];reads+=result['port_reads'];irq_reads+=result['port_irq_reads']
 parts.append(c)
assert (events,reads,irq_reads)==(535716,9856,3056)
rebuild=root/'validation/v319-port-mirror-rebuild01';rr=json.loads((rebuild/'report.json').read_bytes());assert rr['passed'] and rr['byte_identical_v319']
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for name,digest in rr['source_sha256'].items():
 assert sha((root/'megadrive/src'/name).read_bytes())==digest
 assert (rebuild/'project/src'/name).read_bytes()==(root/'megadrive/src'/name).read_bytes()
observer=root/'validation/v319-port-mirror-observer01';br=json.loads((observer/'report.json').read_bytes());core=root.parents[1]/'work/genesis-plus-gx'
assert br['original_sources_restored'] and br['core_sha256']==r['core_sha256']
for name,digest in br['original_source_sha256'].items():assert sha((core/name).read_bytes())==digest
prior=json.loads((root/'analysis/v319-psg-write-spacing/manifest.json').read_bytes())
for region in ('ntsc','pal'):
 item=prior['compressed'][f'validation/v319-psg-writes01/{region}-sms/exposed-psg-states.bin'];encoded=(root/'analysis/v319-psg-write-spacing'/item['stored']).read_bytes();assert sha(encoded)==item['stored_sha256']
 data=gzip.decompress(encoded);assert sha(data)==item['raw_sha256'] and data==(work/(region+'-psg.bin')).read_bytes()
# These are byte-identical diagnostic DLL duplicates created for separate
# cold static FIFO histories. All their runs have exited; retain the baseline
# observer DLL and reproducible instrumentation, remove only named copies.
removed=[]
baseline=Path(br['core']).resolve();assert baseline.parent==core.resolve() and sha(baseline.read_bytes())==br['core_sha256']
for name in ('v319-port-mirror01','v319-port-mirror02','v319-port-origin01'):
 duplicate=baseline.with_name(baseline.stem+'_'+name.replace('-','_')+'_pal.dll').resolve()
 assert duplicate.parent==core.resolve() and duplicate!=baseline
 if duplicate.exists():
  assert sha(duplicate.read_bytes())==br['core_sha256'];removed.append(dict(path=str(duplicate),bytes=duplicate.stat().st_size,sha256=br['core_sha256']));duplicate.unlink()
result=dict(passed=True,public_version=319,production_rom_changed=False,production_rebuild_byte_identical=True,production_rom_sha256=rr['sha256'],
 implementation='source_intro_vdp.c/.h owns zero-initialized16KiB VRAM,16registers,32palette bytes,address/command latch,read buffer and native sprite/VINT calendar. Raw port instructions are the only live inputs. Reference VRAM/register/palette arrays and expected reads are compared afterward, never copied into the product model.',
 native_mirror=r,compiled68000=parts,compiled_port_events=events,compiled_original_read_checks=reads,compiled_irq_provider_reads=irq_reads,
 native_header_sha256={name:sha((root/'megadrive/src'/name).read_bytes()) for name in ('source_intro_vdp.h','source_intro_sprite_clock.h','source_intro_sprite_status.h')},
 psg_reference_states_exact_frames_per_region=14000,initial_phase_probe=pr,
 recovery=['Initial same-process PAL comparison retained the reference static FIFO from the earlier NTSC run; vdp_reset does not initialize that FIFO. Final corpus uses separate byte-identical DLL images for genuinely cold per-region static state. No source state patched.',
 'Initial prefix recorder reopened its first200-period window after32-bit epoch wrap. Final recorder closes that window permanently; monotonic full prefixes and digest independently reproduced in201-frame origin probe.',
 'First compiled cold replays incorrectly assumed first CPU raster192*3420. gen_reset starts CPU at159*3420+990 NTSC and132*3420+990 PAL. Explicit first-checkpoint phase capture fixes test origin; original bytes and product algorithm unchanged. Rejected kernels retained.'],
 limits=['Raw IO is still produced by original Z80 instructions in this diagnostic. The native scene/IRQ/pattern writers are not yet connected to this same model, so no claim of a newly activated intro ROM.',
 'Compiled prefixes cover the first200 source periods,267858 source IO instructions total, replayed in both MD regions. Full14000-frame no-input loops per region are host native checks.',
 'The roughly4258..5500 MD kernel frames include diagnostic replay overhead and are NOT game FPS or a helper-only CPU measurement. Combined native loader/calendar/video/PSG budget is still unproven; optimize and profile before activation.',
 'SMS2/no-BIOS register defaults,Mode4/192,unzoomed8px,no overscan sprite processing. No general VDP/hardware/PCM certification. Exposed PSG checks verify unchanged reference observations, not physical output from this VDP-only module.'],
 next_action='Feed this owned port model from native foreground and IRQ video sinks, including dated032A pattern bytes and status reads. Preserve port instruction ordering and boot history, optimize/profile the composite, then validate actual MD video/PSG before a numbered ROM.',
 removed_verified_reference_duplicates=removed,oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-port-mirror/manifest.json')
target=root/'analysis/v319_port_mirror_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,Path(__file__).resolve()}
for name in ('build_v319_port_mirror_observer.py','validate_v319_port_mirror.py','compile_v319_port_mirror_68k.py'):paths.add(root/'validation'/name)
for name in ('source_intro_vdp.c','source_intro_vdp.h','source_intro_sprite_clock.c','source_intro_sprite_clock.h','source_intro_sprite_status.c','source_intro_sprite_status.h'):paths.add(root/'megadrive/src'/name)
folders=[root/'validation'/name for name in ('v319-port-mirror-smoke01','v319-port-mirror01','v319-port-mirror02','v319-port-origin01')]
for folder in [*folders,rebuild]:paths.update(p for p in folder.rglob('*') if p.is_file())
paths.update(p for p in observer.iterdir() if p.is_file() and not p.name.endswith(('-before.c','-observer.c')))
freeze(root,root/'analysis/v319-port-mirror',paths,result,[*folders,rebuild/'project/out'],cleanup=True)
