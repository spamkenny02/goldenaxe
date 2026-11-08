"""Freeze computed native sprite status, temporal reference comparisons and68000 proofs."""
import difflib,json,struct,subprocess,sys
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
work=root/'validation/v319-chip-events02';r=json.loads((work/'report.json').read_bytes());assert r['passed']
assert sha((root/'megadrive/src/source_intro_sprite_status.c').read_bytes())==r['native_source_sha256']
assert sum(row['read_events'] for row in r['results'])==33707 and sum(row['irq_samples'] for row in r['results'])==27986
assert all(row['read_errors']==row['irq_errors']==row['unsupported']==0 and row['psg_exact_frames']==14000 for row in r['results'])
raw=(work/'native-transitions.bin').read_bytes();assert sha(raw)==r['transition_sha256'] and len(raw)==33179*472
kinds=Counter();boundary=Counter()
for offset in range(0,len(raw),472):
 case=raw[offset:offset+472];kind=case[146];kinds[kind]+=1
 if kind==2:
  assert case[151]==1 and case[148]==case[150]
  if case[66]&32:
   boundary['read_vectors_with_collision']+=1
   if struct.unpack_from('<h',case,144)[0]==struct.unpack_from('<h',case,68)[0]:boundary['same_collision_line_vectors']+=1
assert kinds=={0:26749,1:4000,2:2430}
cr=json.loads((work/'compiled-all-report.json').read_bytes());assert cr['passed'] and cr['source_transition_vectors']==33179 and cr['compiled_executions']==66358
covered=[]
for partition in cr['partitions']:
 p=partition['report'];assert p['passed'] and all(row['chip_case_errors']==0 and row['chip_cases_done']==p['count'] for row in p['results'])
 covered.extend(range(p['start'],p['start']+p['count']))
assert covered==list(range(33179))
rebuild=root/'validation/v319-chip-status-rebuild01'
assert (rebuild/'project/out/release/rom.bin').read_bytes()==(root/'gaw-megadrive.bin').read_bytes()
for p in (root/'megadrive/src').rglob('*'):
 if p.is_file():assert p.read_bytes()==(rebuild/'project/src'/p.relative_to(root/'megadrive/src')).read_bytes()
core=root.parents[1]/'work/genesis-plus-gx'
observers=[root/'validation/v319-chip-status-observer01',root/'validation/v319-chip-events-observer01']
for folder in observers:
 meta=json.loads((folder/'report.json').read_bytes())
 if 'original_sources_restored' in meta:
  assert meta['original_sources_restored']
  for name,digest in meta['original_source_sha256'].items():assert sha((core/name).read_bytes())==digest
 else:assert meta['original_source_restored'] and sha((core/'core/z80/z80.c').read_bytes())==meta['original_source_sha256']
 # Publish the instrumentation insertions and build recipe, not full emulator source files or DLLs.
 patches=[]
 for before in folder.glob('*-before.c'):
  after=folder/(before.name.replace('-before.c','-observer.c'));assert after.exists()
  patches.extend(difflib.unified_diff(before.read_text().splitlines(True),after.read_text().splitlines(True),fromfile=before.name,tofile=after.name,n=0))
 (folder/'instrumentation.patch').write_text(''.join(patches))
 (folder/'reference-license.txt').write_bytes((core/'LICENSE.txt').read_bytes())
 meta['reference_git_revision']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=core,text=True).strip()
 meta['reference_source_url']='https://github.com/ekeeke/Genesis-Plus-GX'
 (folder/'reproducibility.json').write_text(json.dumps(meta,indent=2)+'\n')
static=json.loads((root/'validation/v319-chip-status02/report.json').read_bytes());assert not static['passed'] and sum(row.get('mismatch',0) for row in static['results'])==2
prefix=(root/'megadrive/src/source_intro_sprite_status.c').read_text().split('\nvoid source_intro_sprite_status_reset')[0]
assert sha(prefix.encode())==static['native_source_sha256']
(root/'validation/v319-chip-status02/static-frame-source.c').write_bytes(prefix.encode())
erratum=dict(affected='Earlier intro actor notes and reports labeled the9F/BF change as sprite overflow.',correct='In the reference Mode4 status byte, bit20 is sprite collision and bit40 is sprite overflow.9F/BF differ by collision20. Original numeric captures/comparisons are unchanged.',evidence='Local reference vdp_render.c parse_satb_m4/render_obj_m4 and vdp_ctrl.c vdp_z80_ctrl_r, plus33707 direct native temporal read comparisons.',production_rom_changed=False)
erratum_path=root/'analysis/v319_sprite_status_erratum.json';assert not erratum_path.exists();erratum_path.write_text(json.dumps(erratum,indent=2)+'\n')
result=dict(passed=True,diagnostic_only=True,production_rom_changed=False,public_version=319,
 production_rom_sha256=sha((root/'gaw-megadrive.bin').read_bytes()),production_rebuild_byte_identical=True,
 temporal_reference=r,compiled68000_checks=cr,distinct_native_transition_vectors=33179,compiled_executions=66358,
 transition_kinds=dict(parse=kinds[0],render=kinds[1],status_read=kinds[2]),source_status_reads=33707,source_irq_status_samples=27986,
 implementation='New source_intro_sprite_status.c/.h computes native SMS2 Mode4/192 unzoomed8-pixel sprite flags. Two parsed sprite caches, pending overflow latch, ordered opaque-pixel collision detection, read-to-clear flags and horizontal collision timing. No expected status byte or frame lookup is used by the product algorithm.',
 verification='Read-only reference callbacks supply live VRAM/register and parse/render/read timing inputs. Native model independently caches/parses/draws/reads; bridge compares expected outputs only afterward. All reference status reads and IRQ-saved flags agree over14000 no-input frames per region; exposed PSG states also match prior immutable source captures.',
 static_snapshot_probe=static,
 recovery='Static-frame prediction first missed disabled-display overflow, then still failed two NTSC startup samples because current VRAM cannot reconstruct prior reads/writes/latches. Preserved rejected probes; temporal cache/latch model resolves them without frame-specific values.',
 boundary_coverage=dict(boundary,limit='Natural corpus has no same-collision-line early-HCounter read; that deferral branch is implemented from the reference logic but not source-oracle exercised here.'),
 erratum=erratum,
 limits=['Reference-driven event timeline is not yet a live producer connected to the MD native VRAM/SourceClock. No claim that source IRQ fixture queues have already been removed from the scene-loader diagnostic.',
         'Compiled vectors canonicalize only unused cached slots and unlatched collision coordinates; live model state is unchanged. Direct original read flags are checked for2430 unique read vectors.',
         'Mode4/192/SMS2,8-pixel unzoomed sprites and no-input intro/title loops only. No general VDP,hardware or PCM certification.'],
 next_action='Connect native logical VRAM/register writes and SourceClock raster/status reads to this temporal model; reuse source_game_irq status_read and timed SAT first_y/first_xy interfaces where applicable. Preserve boot latch history and handle foreground status reads, not just IRQ reads. Then validate native intro physical video/PSG delivery.',
 oracle_ram_writes=0,sram_imports=0,archive_manifest='analysis/v319-chip-temporal/manifest.json')
target=root/'analysis/v319_chip_temporal_report.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
paths={target,erratum_path,Path(__file__).resolve()}
for name in ('build_v319_chip_status_observer.py','validate_v319_chip_status.py','build_v319_chip_events_observer.py','validate_v319_chip_events.py','compile_v319_chip_events_68k.py','compile_v319_chip_events_all.py'):paths.add(root/'validation'/name)
for name in ('source_intro_sprite_status.c','source_intro_sprite_status.h'):paths.add(root/'megadrive/src'/name)
folders=[root/'validation'/name for name in ('v319-chip-status01','v319-chip-status02','v319-chip-events01','v319-chip-events02')]
for folder in [*folders,rebuild]:paths.update(p for p in folder.rglob('*') if p.is_file())
for folder in observers:
 paths.update(p for p in folder.iterdir() if p.is_file() and not p.name.endswith(('-before.c','-observer.c')))
freeze(root,root/'analysis/v319-chip-temporal',paths,result,[*folders,rebuild/'project/out'],cleanup=True)
print('Native temporal sprite status,33707 reads and66358 compiled transitions frozen; V319 unchanged.')
